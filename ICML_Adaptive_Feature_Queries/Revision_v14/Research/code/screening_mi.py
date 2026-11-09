"""Audit simulations for the screening-tree case study: branching, fitted fixed-form scores and
proper multiple imputation (hot-deck from complete SOURCE records conditional on the observed
items and the label, with a Bayesian bootstrap of the donor pool per imputation; Rubin's rules).
Truth = accuracy contrast on the full target sample. n audit respondents per replication."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
from sklearn.tree import DecisionTreeClassifier
from scipy.stats import t as student_t


def setup(name, root, b, seed, shift):
    X, y, names, sex = bt.load(name, root); m = X.shape[1]; rng = np.random.default_rng(seed)
    if shift and name == 'BRFSS':
        src = np.flatnonzero(sex == 0); tgt = np.flatnonzero(sex == 1)
    elif shift and name == 'Thyroid':
        f = names.index('Sex'); src = np.flatnonzero(X[:, f] == 1); tgt = np.flatnonzero(X[:, f] == 0)
    else:
        perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
    src = rng.permutation(src); n_source = 20000
    tr = src[:min(n_source, len(src) // 2)]; cal = src[len(tr):len(tr) + min(n_source, len(src) - len(tr))]
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50 if name == 'BRFSS' else 10, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    grid = bt.allbits(m); idx = X @ (1 << np.arange(m)); d = 2 * clf.predict(grid).astype(float) - 1
    def law(rows, a):
        P = np.zeros((2, 1 << m))
        for z in range(2): P[z] = np.bincount(idx[rows][y[rows] == z], minlength=1 << m) / len(rows)
        return (1 - a) * P + a / (2 * (1 << m))
    menu = bt.FormMenu(m, b); Pc = law(cal, 0.1)
    _, qf, gf = menu.solve(menu.cellmass(Pc), d, beta=0.05)
    return dict(X=X, y=y, idx=idx, d=d, m=m, b=b, menu=menu, q=qf, g=gf, src=np.r_[tr, cal], tgt=tgt)


def simulate(S, n=1000, reps=400, M=10, seed=0):
    rng = np.random.default_rng(seed + 99)
    X, y, idx, d, menu, q, g = S['X'], S['y'], S['idx'], S['d'], S['menu'], S['q'], S['g']
    tgt, src = S['tgt'], S['src']; tY = (2 * y - 1) * d[idx]
    truth = float(tY[tgt].mean())
    # donor pools keyed by (form, observed code, label)
    Xs = X[src]; ys = y[src]; L = menu.L; C = menu.C
    forms = menu.forms
    out = {k: [] for k in ['branch', 'fixed', 'mi']}; cover = {k: 0 for k in out}; width = {k: [] for k in out}
    pools = {}
    for rep in range(reps):
        rows = tgt[rng.integers(0, len(tgt), n)]
        # branching: exact t
        tb = tY[rows]; est = tb.mean(); se = tb.std(ddof=1) / np.sqrt(n)
        out['branch'].append(est); cover['branch'] += abs(est - truth) <= 1.96 * se; width['branch'].append(2 * 1.96 * se)
        # fixed forms drawn from fitted q; unbiased form score
        a = rng.choice(L, size=n, p=q)
        codes = np.array([menu.codes[a[i]][idx[rows[i]]] for i in range(n)])
        H = g[y[rows], a * C + codes] / q[a]
        est = H.mean(); se = H.std(ddof=1) / np.sqrt(n)
        out['fixed'].append(est); cover['fixed'] += abs(est - truth) <= 1.96 * se; width['fixed'].append(2 * 1.96 * se)
        # MI on the same observed data
        ests = []; wvars = []
        for mm in range(M):
            bw = rng.dirichlet(np.ones(len(src)))  # Bayesian bootstrap weights over donors
            imp = np.empty(n)
            for i in range(n):
                f = forms[a[i]]; key = (a[i], codes[i], y[rows[i]])
                if key not in pools:
                    obs = (Xs[:, f] @ (1 << np.arange(len(f))))
                    pools[key] = np.flatnonzero((obs == codes[i]) & (ys == y[rows[i]]))
                    if len(pools[key]) == 0:
                        pools[key] = np.flatnonzero(obs == codes[i])
                    if len(pools[key]) == 0:
                        pools[key] = np.arange(len(src))
                pool = pools[key]; w = bw[pool]; w = w / w.sum()
                donor = pool[rng.choice(len(pool), p=w)]
                xi = Xs[donor].copy(); xi[list(f)] = X[rows[i], list(f)]
                imp[i] = (2 * y[rows[i]] - 1) * d[xi @ (1 << np.arange(len(xi)))]
            ests.append(imp.mean()); wvars.append(imp.var(ddof=1) / n)
        qbar = np.mean(ests); Ubar = np.mean(wvars); Bv = np.var(ests, ddof=1); T = Ubar + (1 + 1 / M) * Bv
        dfree = (M - 1) * (1 + Ubar / ((1 + 1 / M) * Bv)) ** 2 if Bv > 0 else 1e6
        tq = student_t.ppf(0.975, dfree)
        out['mi'].append(qbar); cover['mi'] += abs(qbar - truth) <= tq * np.sqrt(T); width['mi'].append(2 * tq * np.sqrt(T))
    res = dict(truth=truth, n=n, reps=reps, M=M)
    for k in out:
        v = np.array(out[k]); res[k] = dict(bias=float(v.mean() - truth), sd=float(v.std(ddof=1)), rmse=float(np.sqrt(np.mean((v - truth) ** 2))),
                                           coverage=cover[k] / reps, width=float(np.mean(width[k])), mc_se_cov=float(np.sqrt(0.95 * 0.05 / reps)))
    return res


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--reps', type=int, default=400); a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for ds in ['BRFSS', 'Thyroid']:
        for b in [4, 5]:
            for shift in [True, False]:
                dest = out / f'{ds}_b{b}_{"shift" if shift else "iid"}.json'
                if dest.exists(): continue
                t0 = time.time(); S = setup(ds, a.data, b, 20261108, shift); r = simulate(S, reps=a.reps)
                r.update(dataset=ds, b=b, shift=shift, seconds=time.time() - t0); dest.write_text(json.dumps(r, indent=1))
                print(ds, b, 'shift' if shift else 'iid', 'truth %.4f' % r['truth'], ' '.join('%s bias %.4f rmse %.4f cov %.3f' % (k, r[k]['bias'], r[k]['rmse'], r[k]['coverage']) for k in ['branch', 'fixed', 'mi']), '%.0fs' % r['seconds'], flush=True)
