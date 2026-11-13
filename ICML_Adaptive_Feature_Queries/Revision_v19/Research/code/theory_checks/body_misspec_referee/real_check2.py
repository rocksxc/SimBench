import sys, time, numpy as np
from itertools import combinations
CODE='SCRATCH/v19/Research/code'
sys.path.insert(0, CODE)
import misspec_v19 as ms, model_v17 as mv
from curve_v16 import LogLin
import budget_trees as bt
from screening_v14 import splits
from baselines_v16 import dependent_items
from sklearn.tree import DecisionTreeClassifier
root='SCRATCH/inputs_v12'
b, s, shift = int(sys.argv[1]), int(sys.argv[2]), bool(int(sys.argv[3])); maxit = int(sys.argv[4]); nstart = int(sys.argv[5])
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
fx = E.design(1, forms)
def as_design(q, ints):
    return [(float(w), *ms.cell_ids(E, c)) for w, c in zip(q, ints) if w > 1e-8]
br = E.design(b, forms + [tree], time_budget=600)
designs = dict(forms=as_design(qd, forms), mforms=as_design(fx['q'], forms), tree=as_design([1.0], [tree]), mbranch=as_design(br['q'], br['interviews']))
model = LogLin(K + 1, 2); V = K + 1; sx = 1.0 - 2.0 * mv.bits(V)
terms = [c for jj in (1, 2) for c in combinations(range(V), jj)]
chi = np.stack([np.prod(sx[:, list(c)], axis=1) for c in terms], axis=1)
def em(P, design, p0, iters, tol=1e-13):
    p = p0.copy(); idx = [np.r_[cid, cid + nc] for _, cid, nc in design]; tot = [2 * nc for _, _, nc in design]
    truec = [np.bincount(ix, weights=P, minlength=n) for ix, n in zip(idx, tot)]
    for it in range(iters):
        w = np.zeros_like(p)
        for (q, _, _), ix, n, tc in zip(design, idx, tot, truec):
            cur = np.bincount(ix, weights=p, minlength=n); w += q * np.divide(tc, cur, out=np.zeros(n), where=cur > 0)[ix]
        new = model.mstep(p, p * w); ch = np.max(np.abs(new - p)); p = new
        if ch < tol: break
    L = sum(q * (tc @ np.log(np.bincount(ix, weights=p, minlength=n))) for (q, _, _), ix, n, tc in zip(design, idx, tot, truec))
    return p, it + 1, ch, L
def Amat(pstar, des):
    mu = pstar @ chi; A = (chi * pstar[:, None]).T @ chi - np.outer(mu, mu)
    for q, cid, nc in des:
        ix = np.r_[cid, cid + nc]
        for c in range(2 * nc):
            sel = ix == c; pc = P[sel].sum(); ps = pstar[sel]; msum = ps.sum(); e = (ps @ chi[sel]) / msum
            A -= q * pc * ((chi[sel] * ps[:, None]).T @ chi[sel] / msum - np.outer(e, e))
    return A
rng = np.random.default_rng(int(sys.argv[6]) if len(sys.argv) > 6 else 0)
print('b', b, 'seed', s, 'shift', shift, 'K', K, 'delta %.4f var %.4f sd %.4f' % (delta, var, var ** .5))
import os
for name, des in [(k, v) for k, v in designs.items() if k in os.environ.get("DES", "forms,mforms,tree").split(",")]:
    tot = sum(w for w, _, _ in des); des = [(w / tot, c, n) for w, c, n in des]
    starts = [('uniform', np.full(2 << K, 1.0 / (2 << K))), ('pairwise fit of P', mv.loglin_fit(P, 2))]
    for j in range(nstart):
        a = chi @ rng.normal(scale=0.5, size=len(terms)); p0 = np.exp(a - a.max()); starts.append(('random %d' % j, p0 / p0.sum()))
    print('=====', name, 'interviews', len(des))
    for sname, p0 in starts:
        p, it, ch, L = em(P, des, p0, maxit); v2, vm2, r2 = ms.sandwich(K, P, p, des, t); ev = np.linalg.eigvalsh(Amat(p, des))
        print('  %-18s its %6d lastchg %.0e loglik %.10f bias %+.5f (%.2f%% sd) sand/var %.3f model/var %.3f resid %.0e mineigA %.1e minP* %.1e' % (sname, it, ch, L, p @ t - delta, 100 * (p @ t - delta) / var ** .5, v2 / var, vm2 / var, r2, ev.min(), p.min()))
