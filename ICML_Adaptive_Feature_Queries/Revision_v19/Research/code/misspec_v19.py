"""v19 (round-8 R2 Q1): the pairwise working model is misspecified for the accuracy of a depth-b tree, and under
planned missingness the limit of its maximum-likelihood estimate depends on the design. For each BRFSS tree and each
of four collection designs under the same cap, this script computes at the TARGET law P (not at a fitted law)
  - the pseudo-true law P*_q, the maximiser of the expected observed-data log-likelihood of the pairwise model for
    the label and the rule's items (EM on expected counts), and the pseudo-true target Delta(P*_q);
  - the sandwich variance of the estimate of Delta, grad' A^+ B A^+ grad, with
        A = Cov*(chi) - sum_i q_i sum_c P(c) Cov*(chi | c)   (observed information at P*_q, averaged over the true law),
        B = sum_i q_i sum_c P(c) s_c s_c',  s_c = E*[chi | c] - E*[chi],   grad = Cov*(t, chi),
    following the theory of maximum likelihood under misspecification with missing data;
  - the asymptotic mean squared error bias^2 + variance / n at audit sizes n.
Designs: (forms) forms optimal for the design-based score at P; (mforms) forms optimal for the pairwise model at the
pairwise fit; (tree) the rule's own tree, padded; (mbranch) the branching design optimal for the pairwise model at
the pairwise fit. All on the K items the rule depends on."""
import argparse, json, sys, time
from itertools import combinations
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_v17 as mv

NS = [1000, 4000, 16000]


def cell_ids(E, cells):
    """Cell index of every profile of the K-cube under an interview given as (form index, pattern) cells."""
    K = E.K; grid = mv.bits(K); out = np.full(1 << K, -1, np.int64)
    for c, (f, u) in enumerate(zip(cells[0], cells[1])):
        code = grid[:, E.forms[f]] @ (1 << np.arange(E.b)); out[code == u] = c
    assert out.min() >= 0
    return out, len(cells[0])


def chi_matrix(K):
    V = K + 1; sx = 1.0 - 2.0 * mv.bits(V)
    terms = [c for j in (1, 2) for c in combinations(range(V), j)]
    return np.stack([np.prod(sx[:, list(c)], axis=1) for c in terms], axis=1)


def loglik(theta, chi, idx, tot, truec, qs):
    """Expected observed-data log-likelihood of the pairwise model at the true law and its gradient."""
    lp = chi @ theta; lp -= lp.max(); p = np.exp(lp); p /= p.sum(); F = 0.0; w = np.zeros_like(p)
    for q, ix, n, tc in zip(qs, idx, tot, truec):
        cur = np.maximum(np.bincount(ix, weights=p, minlength=n), 1e-300); F += q * float(tc @ np.log(cur)); w += q * (tc / cur)[ix]
    return F, (p * w) @ chi - p @ chi, p


def pseudo_true(K, P, design, starts=6, seed=0, gtol=1e-9):
    """Maximise the expected log-likelihood from several starts (L-BFGS, then Newton steps with the pseudo-inverse).
    Returns one record per start: objective, gradient norm, the law, and a flag for maximisers at the boundary."""
    from scipy.optimize import minimize
    chi = chi_matrix(K); idx = [np.r_[cid, cid + nc] for _, cid, nc in design]; tot = [2 * nc for _, _, nc in design]; qs = [q for q, _, _ in design]
    truec = [np.bincount(ix, weights=P, minlength=n) for ix, n in zip(idx, tot)]
    f = lambda th: loglik(th, chi, idx, tot, truec, qs)
    rng = np.random.default_rng(seed); p2 = mv.loglin_fit(P, 2).ravel()
    th_fit = np.linalg.lstsq(chi, np.log(p2) - np.log(p2).mean(), rcond=None)[0]
    inits = [np.zeros(chi.shape[1]), th_fit] + [rng.normal(0, 0.5, chi.shape[1]) for _ in range(max(0, starts - 2))]
    out = []
    for th0 in inits:
        r = minimize(lambda th: (lambda F, g, _: (-F, -g))(*f(th)), th0, jac=True, method='L-BFGS-B', options=dict(maxiter=20000, maxfun=40000, gtol=1e-11, ftol=1e-16, maxcor=30))
        th = r.x; F, g, p = f(th)
        for _ in range(30):  # Newton polish
            if np.linalg.norm(g) < gtol or np.abs(th).max() > 40: break
            mu = p @ chi; A = (chi * p[:, None]).T @ chi - np.outer(mu, mu)
            for q, ix, n, tc in zip(qs, idx, tot, truec):
                cur = np.maximum(np.bincount(ix, weights=p, minlength=n), 1e-300)
                E1 = np.stack([np.bincount(ix, weights=p * chi[:, k], minlength=n) for k in range(chi.shape[1])], axis=1) / cur[:, None]
                A -= q * ((chi * (p * (tc / cur)[ix])[:, None]).T @ chi - (E1 * tc[:, None]).T @ E1)
            step = np.linalg.lstsq(A, g, rcond=1e-10)[0]; ok = False
            for sc in (1.0, 0.5, 0.25, 0.1):
                F2, g2, p2_ = f(th + sc * step)
                if F2 >= F - 1e-14 and np.linalg.norm(g2) < np.linalg.norm(g): th, F, g, p = th + sc * step, F2, g2, p2_; ok = True; break
            if not ok: break
        gn = float(np.linalg.norm(g))
        out.append(dict(F=float(F), gnorm=gn, p=p, boundary=bool(np.abs(th).max() > 25 or p.min() < 1e-10 or gn > 1e-6), theta_max=float(np.abs(th).max()), pmin=float(p.min())))
    return out


def sandwich(K, P, pstar, design, t):
    V = K + 1; B_ = mv.bits(V); sx = 1.0 - 2.0 * B_
    terms = [c for j in (1, 2) for c in combinations(range(V), j)]
    chi = np.stack([np.prod(sx[:, list(c)], axis=1) for c in terms], axis=1)  # states x p
    mu = pstar @ chi; cov_full = (chi * pstar[:, None]).T @ chi - np.outer(mu, mu)
    grad = (pstar * t) @ chi - (pstar @ t) * mu
    A = cov_full.copy(); Bm = np.zeros_like(A)
    for q, cid, nc in design:
        ix = np.r_[cid, cid + nc]
        for c in range(2 * nc):
            sel = ix == c; pc = P[sel].sum()
            if pc <= 0: continue
            ps = pstar[sel]; ms = ps.sum()
            if ms <= 0: continue
            e = (ps @ chi[sel]) / ms; second = (chi[sel] * ps[:, None]).T @ chi[sel] / ms
            A -= q * pc * (second - np.outer(e, e)); s = e - mu; Bm += q * pc * np.outer(s, s)
    x = np.linalg.lstsq(A, grad, rcond=1e-10)[0]; resid = float(np.linalg.norm(A @ x - grad) / max(np.linalg.norm(grad), 1e-300))
    return float(x @ Bm @ x), float(x @ A @ x), resid


def run(root, b, s, shift):
    import budget_trees as bt
    from screening_v14 import splits
    from baselines_v16 import dependent_items
    from sklearn.tree import DecisionTreeClassifier
    t0 = time.time(); seed = 20261108 + s; X, y, names, sex = bt.load('BRFSS', root); m = X.shape[1]
    tr, cal, tgt = splits('BRFSS', X, y, names, sex, seed, shift)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    used = dependent_items(clf, m); K = len(used); row = dict(dataset='BRFSS', b=b, seed=seed, shift=shift, items=K)
    if K <= b:
        row['trivial'] = True; return row
    grid = mv.bits(K); Xc = np.zeros((1 << K, m), np.int8); Xc[:, used] = grid; d = 2.0 * clf.predict(Xc) - 1
    code = X[tgt][:, used].astype(np.int64) @ (1 << np.arange(K)) + (y[tgt].astype(np.int64) << K)
    P = 0.99 * np.bincount(code, minlength=2 << K) / len(tgt) + 0.01 / (2 << K); t = np.r_[-d, d]
    delta = float(P @ t); var = float(P @ (t * t) - delta ** 2); row.update(delta=delta, var=var)
    P2 = mv.loglin_fit(P, 2).reshape(2, 1 << K); E = mv.ModelEngine(K, b, P2, d, 2)
    forms = [E.form_interview(f) for f in range(E.L)]; tree = mv.clf_interview(E, clf, used)
    fx = E.design(1, forms); br = E.design(b, forms + [tree], time_budget=600)
    _, qd = mv.design_based_fixed(K, b, P.reshape(2, 1 << K), d)
    def as_design(q, ints):
        return [(float(w), *cell_ids(E, c)) for w, c in zip(q, ints) if w > 1e-8]
    designs = dict(forms=as_design(qd, forms), mforms=as_design(fx['q'], forms), tree=as_design([1.0], [tree]), mbranch=as_design(br['q'], br['interviews']))
    row['designs'] = {}
    for name, des in designs.items():
        tot = sum(w for w, _, _ in des); des = [(w / tot, c, n) for w, c, n in des]
        fits = pseudo_true(K, P, des, seed=seed); recs = []
        for ft in fits:
            rec = dict(F=ft['F'], gnorm=ft['gnorm'], boundary=ft['boundary'], theta_max=ft['theta_max'], pmin=ft['pmin'], delta_star=float(ft['p'] @ t), bias=float(ft['p'] @ t - delta))
            if not ft['boundary']:
                v, vmodel, resid = sandwich(K, P, ft['p'], des, t); rec.update(sandwich=v / var, model_variance=vmodel / var, resid=resid)
            recs.append(rec)
        best = max(recs, key=lambda r_: r_['F']); interior = [r_ for r_ in recs if not r_['boundary']]
        d_ = dict(interviews=len(des), starts=recs, best_boundary=best['boundary'], n_interior=len(interior), F_best=best['F'])
        if interior:
            bi = max(interior, key=lambda r_: r_['F'])
            d_.update(delta_star=bi['delta_star'], bias=bi['bias'], sandwich=bi['sandwich'], model_variance=bi['model_variance'], resid=bi['resid'], F=bi['F'],
                      bias_range=[min(r_['bias'] for r_ in interior), max(r_['bias'] for r_ in interior)], sandwich_range=[min(r_['sandwich'] for r_ in interior), max(r_['sandwich'] for r_ in interior)],
                      n_limits=len({round(r_['delta_star'], 6) for r_ in interior}), mse={str(n): float(bi['bias'] ** 2 + bi['sandwich'] * var / n) for n in NS})
        row['designs'][name] = d_
    row['design_based'] = dict(branch=1.0, forms=float(mv.design_based_fixed(K, b, P.reshape(2, 1 << K), d)[0]))
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True); p.add_argument('--bs', default='4,5,6'); p.add_argument('--workers', type=int, default=1)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tasks = [(int(b), s, sh) for b in a.bs.split(',') for sh in (False, True) for s in range(3)]
    fn = lambda t: out / f'BRFSS_b{t[0]}_{"shift" if t[2] else "iid"}_{t[1]}.json'
    tasks = [t for t in tasks if not fn(t).exists()]
    def go(t):
        r = run(a.data, *t); fn(t).write_text(json.dumps(r, indent=1, default=float)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                if r.get('trivial'): print(t, 'trivial', flush=True); continue
                print(t, 'K', r['items'], ' | '.join(('%s: bias%% %.2f var %.3f [%.3f, %.3f] limits %d interior %d/%d%s' % (k, 100 * v['bias'] / np.sqrt(r['var']), v['sandwich'], v['sandwich_range'][0], v['sandwich_range'][1], v['n_limits'], v['n_interior'], len(v['starts']), ' BEST-BOUNDARY' if v['best_boundary'] else '')) if v['n_interior'] else ('%s: all starts at boundary' % k) for k, v in r['designs'].items()), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1500:], flush=True)
