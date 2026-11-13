import sys, numpy as np
sys.path.insert(0,'SCRATCH/v19/Research/code')
import misspec_v19 as ms
from curve_v16 import LogLin
K = 3; V = K + 1; NST = 1 << V
x = ((np.arange(1 << K)[:, None] >> np.arange(K)) & 1)
def form_cid(items):
    cid = sum(x[:, j] << i for i, j in enumerate(items)); return cid.astype(np.int64), 1 << len(items)
def tree_cid():
    cid = np.where(x[:, 0] == 0, x[:, 1], 2 + x[:, 2]); return cid.astype(np.int64), 4
rng = np.random.default_rng(1)
def rand_law():
    P = rng.dirichlet(np.ones(NST) * 0.7); return 0.95 * P + 0.05 / NST
d = np.where(x[:, 0] == 0, 1 - 2 * x[:, 1], 1 - 2 * x[:, 2]).astype(float); t = np.r_[-d, d]
model = LogLin(V, 2)
laws = [rand_law() for _ in range(3)]
def em_counts(design_ix, counts, iters=3000, tol=1e-10):
    p = np.full(NST, 1.0 / NST); old = 9.
    for it in range(iters):
        w = np.zeros(NST)
        for ix, c in zip(design_ix, counts):
            cur = np.bincount(ix, weights=p, minlength=len(c)); w += np.divide(c, cur, out=np.zeros(len(c)), where=cur > 0)[ix]
        p = model.mstep(p, p * w); est = p @ t
        if abs(est - old) < tol: break
        old = est
    return est
cases = [('tree + form mix', [(0.7, *tree_cid()), (0.3, *form_cid([1, 2]))], 1),
         ('tree + form mix', [(0.7, *tree_cid()), (0.3, *form_cid([1, 2]))], 2),
         ('three forms', [(0.5, *form_cid([0, 1])), (0.3, *form_cid([1, 2])), (0.2, *form_cid([0, 2]))], 2),
         ('two forms (non-identified)', [(0.4, *form_cid([0, 1])), (0.6, *form_cid([1, 2]))], 2)]
n = 20000; reps = 800
for name, des, li in cases:
    P = laws[li]; pstar, its = ms.pseudo_true(model, K, P, des); v, vm, res = ms.sandwich(K, P, pstar, des, t)
    ixs = [np.r_[cid, cid + nc] for _, cid, nc in des]; qs = np.array([q for q, _, _ in des])
    est = []
    for r in range(reps):
        st = rng.choice(NST, size=n, p=P); a = rng.choice(len(des), size=n, p=qs)
        counts = [np.bincount(ix[st[a == j]], minlength=2 * des[j][2]).astype(float) for j, ix in enumerate(ixs)]
        est.append(em_counts(ixs, counts))
    est = np.array(est)
    se_var = n * est.var(ddof=1) * np.sqrt(2 / (reps - 1))
    print('%-28s law %d: D* %.5f (true %.5f) MC mean %.5f (se %.5f) | sandwich %.4f model-var %.4f | n*Var MC %.4f (se %.4f)' % (name, li, pstar @ t, P @ t, est.mean(), est.std() / np.sqrt(reps), v, vm, n * est.var(ddof=1), se_var))
