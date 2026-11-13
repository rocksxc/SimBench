import sys, time, numpy as np
CODE='SCRATCH/v19/Research/code'
sys.path.insert(0, CODE)
import misspec_v19 as ms, model_v17 as mv
from curve_v16 import LogLin
import budget_trees as bt
from screening_v14 import splits
from baselines_v16 import dependent_items
from sklearn.tree import DecisionTreeClassifier
root='SCRATCH/inputs_v12'
b, s, shift = int(sys.argv[1]), int(sys.argv[2]), bool(int(sys.argv[3]))
seed = 20261108 + s; X, y, names, sex = bt.load('BRFSS', root); m = X.shape[1]
tr, cal, tgt = splits('BRFSS', X, y, names, sex, seed, shift)
clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
used = dependent_items(clf, m); K = len(used)
grid = mv.bits(K); Xc = np.zeros((1 << K, m), np.int8); Xc[:, used] = grid; d = 2.0 * clf.predict(Xc) - 1
code = X[tgt][:, used].astype(np.int64) @ (1 << np.arange(K)) + (y[tgt].astype(np.int64) << K)
P = 0.99 * np.bincount(code, minlength=2 << K) / len(tgt) + 0.01 / (2 << K); t = np.r_[-d, d]
delta = float(P @ t); var = float(P @ (t * t) - delta ** 2)
P2 = mv.loglin_fit(P, 2).reshape(2, 1 << K); E = mv.ModelEngine(K, b, P2, d, 2)
forms = [E.form_interview(f) for f in range(E.L)]; tree = mv.clf_interview(E, clf, used)
_, qd = mv.design_based_fixed(K, b, P.reshape(2, 1 << K), d)
def as_design(q, ints):
    return [(float(w), *ms.cell_ids(E, c)) for w, c in zip(q, ints) if w > 1e-8]
designs = dict(forms=as_design(qd, forms), tree=as_design([1.0], [tree]))
model = LogLin(K + 1, 2)
print('K', K, 'delta', delta, 'var', var, 'n params', (K+1) + (K+1)*K//2, 'tree cells x labels', 2*designs['tree'][0][2])
# check tree cells partition and that t is cell-measurable
cid, nc = designs['tree'][0][1], designs['tree'][0][2]
print('tree: d constant on cells:', all(len(set(d[cid == c])) == 1 for c in range(nc)), 'cells', nc)

def em(P, design, p0, iters, tol=1e-13):
    p = p0.copy(); idx = [np.r_[cid, cid + nc] for _, cid, nc in design]; tot = [2 * nc for _, _, nc in design]
    truec = [np.bincount(ix, weights=P, minlength=n) for ix, n in zip(idx, tot)]
    trace = []
    for it in range(iters):
        w = np.zeros_like(p)
        for (q, _, _), ix, n, tc in zip(design, idx, tot, truec):
            cur = np.bincount(ix, weights=p, minlength=n); w += q * np.divide(tc, cur, out=np.zeros(n), where=cur > 0)[ix]
        new = model.mstep(p, p * w); ch = np.max(np.abs(new - p)); p = new
        if it in (999, 4999, 19999, 49999, 99999, 199999): trace.append((it + 1, float(p @ t - delta), ch))
        if ch < tol: break
    L = sum(q * (tc @ np.log(np.bincount(ix, weights=p, minlength=n))) for (q, _, _), ix, n, tc in zip(design, idx, tot, truec))
    return p, it + 1, ch, L, trace

rng = np.random.default_rng(0)
for name, des in designs.items():
    tot = sum(w for w, _, _ in des); des = [(w / tot, c, n) for w, c, n in des]
    print('=====', name, 'interviews', len(des))
    pstar, its = ms.pseudo_true(model, K, P, des); v, vmodel, resid = ms.sandwich(K, P, pstar, des, t)
    print(' code: its %d bias %+.6f sand/var %.4f model/var %.4f resid %.1e' % (its, pstar @ t - delta, v / var, vmodel / var, resid))
    maxit = int(sys.argv[4]) if len(sys.argv) > 4 else 100000
    starts = [('uniform', np.full(2 << K, 1.0 / (2 << K))), ('pairwise fit of P', mv.loglin_fit(P, 2))]
    for j in range(3):
        th = rng.normal(size=(2 << K)) ; # random start INSIDE the pairwise model
        V = K + 1; sx = 1.0 - 2.0 * mv.bits(V); from itertools import combinations
        terms = [c for jj in (1, 2) for c in combinations(range(V), jj)]
        chi = np.stack([np.prod(sx[:, list(c)], axis=1) for c in terms], axis=1)
        a = chi @ rng.normal(scale=0.5, size=len(terms)); p0 = np.exp(a - a.max()); starts.append(('random pairwise %d' % j, p0 / p0.sum()))
    for sname, p0 in starts:
        t0 = time.time(); p, it, ch, L, trace = em(P, des, p0, maxit)
        v2, vm2, r2 = ms.sandwich(K, P, p, des, t)
        print('  start %-18s its %6d lastchange %.1e loglik %.12f bias %+.6f sand/var %.4f resid %.1e  trace %s (%.0fs)' % (sname, it, ch, L, p @ t - delta, v2 / var, r2, [(a_, round(b_, 6), float('%.1e' % c_)) for a_, b_, c_ in trace], time.time() - t0))
    # rank of A and null-space consistency of B
    V = K + 1; sx = 1.0 - 2.0 * mv.bits(V)
    chi = np.stack([np.prod(sx[:, list(c)], axis=1) for c in terms], axis=1)
    mu = pstar @ chi; A = (chi * pstar[:, None]).T @ chi - np.outer(mu, mu); Bm = np.zeros_like(A)
    for q, cid, nc in des:
        ix = np.r_[cid, cid + nc]
        for c in range(2 * nc):
            sel = ix == c; pc = P[sel].sum(); ps = pstar[sel]; msum = ps.sum(); e = (ps @ chi[sel]) / msum
            second = (chi[sel] * ps[:, None]).T @ chi[sel] / msum
            A -= q * pc * (second - np.outer(e, e)); sc = e - mu; Bm += q * pc * np.outer(sc, sc)
    ev, U = np.linalg.eigh(A); print('  eig(A): min %.2e, #<1e-8*max: %d, #<1e-5*max: %d of %d; five smallest %s' % (ev.min(), (ev < 1e-8 * ev.max()).sum(), (ev < 1e-5 * ev.max()).sum(), len(ev), np.array2string(ev[:5], precision=2)))
    nullv = U[:, ev < 1e-8 * ev.max()]
    if nullv.shape[1]:
        print('  max |B on null(A)| relative: %.2e ; score mean norm %.2e' % (np.abs(nullv.T @ Bm @ nullv).max() / np.abs(Bm).max(), 0))
    # first-order condition: expected score = 0?
    g = np.zeros(len(mu))
    for q, cid, nc in des:
        ix = np.r_[cid, cid + nc]
        for c in range(2 * nc):
            sel = ix == c; pc = P[sel].sum(); ps = pstar[sel]; g += q * pc * ((ps @ chi[sel]) / ps.sum() - mu)
    print('  expected score norm at code optimum: %.2e' % np.linalg.norm(g))
