"""v13 addition (R2 Q3): a model-assisted single regression-imputation estimator that uses the SAME complete
source records as MI (conditional mean of t given the asked items and the label, estimated from the donor pool),
with a naive standard error (ignores imputation uncertainty). Everything else as screening_mi.simulate (v12).
Also reports MI and the design-based fitted fixed-form score on the same simulated audits."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screening_mi as sm
from scipy.stats import t as student_t


def simulate(S, n=1000, reps=400, M=10, seed=0):
    rng = np.random.default_rng(seed + 99)
    X, y, idx, d, menu, q, g = S['X'], S['y'], S['idx'], S['d'], S['menu'], S['q'], S['g']
    tgt, src = S['tgt'], S['src']; tY = (2 * y - 1) * d[idx]
    truth = float(tY[tgt].mean())
    Xs = X[src]; ys = y[src]; L = menu.L; C = menu.C; forms = menu.forms; tS = (2 * ys - 1) * d[idx[src]]
    keys = ['branch', 'fixed', 'regimp', 'mi']
    out = {k: [] for k in keys}; cover = {k: 0 for k in keys}; width = {k: [] for k in keys}
    pools = {}; cmean = {}
    def pool_of(a_i, code_i, y_i):
        key = (a_i, code_i, y_i)
        if key not in pools:
            f = forms[a_i]; obs = (Xs[:, f] @ (1 << np.arange(len(f))))
            p = np.flatnonzero((obs == code_i) & (ys == y_i))
            if len(p) == 0: p = np.flatnonzero(obs == code_i)
            if len(p) == 0: p = np.arange(len(src))
            pools[key] = p; cmean[key] = float(tS[p].mean())
        return pools[key], cmean[key]
    for rep in range(reps):
        rows = tgt[rng.integers(0, len(tgt), n)]
        tb = tY[rows]; est = tb.mean(); se = tb.std(ddof=1) / np.sqrt(n)
        out['branch'].append(est); cover['branch'] += abs(est - truth) <= 1.96 * se; width['branch'].append(2 * 1.96 * se)
        a = rng.choice(L, size=n, p=q)
        codes = np.array([menu.codes[a[i]][idx[rows[i]]] for i in range(n)])
        H = g[y[rows], a * C + codes] / q[a]
        est = H.mean(); se = H.std(ddof=1) / np.sqrt(n)
        out['fixed'].append(est); cover['fixed'] += abs(est - truth) <= 1.96 * se; width['fixed'].append(2 * 1.96 * se)
        # model-assisted regression imputation: conditional mean of t from the source donor pool
        R = np.array([pool_of(a[i], codes[i], y[rows[i]])[1] for i in range(n)])
        est = R.mean(); se = R.std(ddof=1) / np.sqrt(n)
        out['regimp'].append(est); cover['regimp'] += abs(est - truth) <= 1.96 * se; width['regimp'].append(2 * 1.96 * se)
        # proper MI (as in v12)
        ests = []; wvars = []
        for mm in range(M):
            bw = rng.dirichlet(np.ones(len(src))); imp = np.empty(n)
            for i in range(n):
                pool, _ = pool_of(a[i], codes[i], y[rows[i]]); w = bw[pool]; w = w / w.sum()
                donor = pool[rng.choice(len(pool), p=w)]
                f = forms[a[i]]; xi = Xs[donor].copy(); xi[list(f)] = X[rows[i], list(f)]
                imp[i] = (2 * y[rows[i]] - 1) * d[xi @ (1 << np.arange(len(xi)))]
            ests.append(imp.mean()); wvars.append(imp.var(ddof=1) / n)
        qbar = np.mean(ests); Ubar = np.mean(wvars); Bv = np.var(ests, ddof=1); T = Ubar + (1 + 1 / M) * Bv
        dfree = (M - 1) * (1 + Ubar / ((1 + 1 / M) * Bv)) ** 2 if Bv > 0 else 1e6
        tq = student_t.ppf(0.975, dfree)
        out['mi'].append(qbar); cover['mi'] += abs(qbar - truth) <= tq * np.sqrt(T); width['mi'].append(2 * tq * np.sqrt(T))
    res = dict(truth=truth, n=n, reps=reps, M=M)
    for k in keys:
        v = np.array(out[k]); res[k] = dict(bias=float(v.mean() - truth), sd=float(v.std(ddof=1)), rmse=float(np.sqrt(np.mean((v - truth) ** 2))),
                                           coverage=cover[k] / reps, width=float(np.mean(width[k])), mc_se_cov=float(np.sqrt(0.95 * 0.05 / reps)))
    return res


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--reps', type=int, default=400); p.add_argument('--datasets', default='BRFSS'); p.add_argument('--bs', default='4,5')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for ds in a.datasets.split(','):
        for b in [int(v) for v in a.bs.split(',')]:
            for shift in [True, False]:
                dest = out / f'{ds}_b{b}_{"shift" if shift else "iid"}.json'
                if dest.exists(): continue
                t0 = time.time(); S = sm.setup(ds, a.data, b, 20261108, shift); r = simulate(S, reps=a.reps)
                r.update(dataset=ds, b=b, shift=shift, seconds=time.time() - t0); dest.write_text(json.dumps(r, indent=1))
                print(ds, b, 'shift' if shift else 'iid', 'truth %.4f' % r['truth'], ' '.join('%s rmse %.4f cov %.3f' % (k, r[k]['rmse'], r[k]['coverage']) for k in ['branch', 'fixed', 'regimp', 'mi']), '%.0fs' % r['seconds'], flush=True)
