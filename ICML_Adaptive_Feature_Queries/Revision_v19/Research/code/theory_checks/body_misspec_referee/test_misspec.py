import sys, numpy as np
sys.path.insert(0,'SCRATCH/v19/Research/code')
import misspec_v19 as ms, model_v17 as mv
from curve_v16 import LogLin
from itertools import combinations
from scipy.optimize import minimize

K = 3; V = K + 1; NST = 1 << V
bitsV = ((np.arange(NST)[:, None] >> np.arange(V)) & 1)
sx = 1.0 - 2.0 * bitsV
terms = [c for j in (1, 2) for c in combinations(range(V), j)]
chi = np.stack([np.prod(sx[:, list(c)], axis=1) for c in terms], axis=1)
prof = np.arange(NST) & ((1 << K) - 1); lab = np.arange(NST) >> K
x = ((np.arange(1 << K)[:, None] >> np.arange(K)) & 1)

def form_cid(items):
    cid = sum(x[:, j] << i for i, j in enumerate(items)); return cid.astype(np.int64), 1 << len(items)
def tree_cid():  # ask item 0; if 0 ask item 1 else ask item 2
    cid = np.where(x[:, 0] == 0, x[:, 1], 2 + x[:, 2]); return cid.astype(np.int64), 4

rng = np.random.default_rng(1)
def rand_law():
    P = rng.dirichlet(np.ones(NST) * 0.7); return 0.95 * P + 0.05 / NST
# target: accuracy of the tree's rule: d = +-1 from item1 if x0==0 else item2
d = np.where(x[:, 0] == 0, 1 - 2 * x[:, 1], 1 - 2 * x[:, 2]).astype(float)
t = np.r_[-d, d]

def pth(th):
    a = chi @ th; a -= a.max(); p = np.exp(a); return p / p.sum()
def cells_full(design):
    return [(q, np.r_[cid, cid + nc], 2 * nc) for q, cid, nc in design]
def exp_loglik(th, P, design):
    p = pth(th); L = 0.0
    for q, ix, n in cells_full(design):
        Pc = np.bincount(ix, weights=P, minlength=n); pc = np.bincount(ix, weights=p, minlength=n); L += q * (Pc @ np.log(pc))
    return L
def num_grad(f, th, h=1e-5):
    g = np.zeros(len(th))
    for i in range(len(th)):
        e = np.zeros(len(th)); e[i] = h; g[i] = (f(th + e) - f(th - e)) / (2 * h)
    return g
def num_hess(f, th, h=1e-4):
    n = len(th); H = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            ei = np.zeros(n); ei[i] = h; ej = np.zeros(n); ej[j] = h
            H[i, j] = H[j, i] = (f(th + ei + ej) - f(th + ei - ej) - f(th - ei + ej) + f(th - ei - ej)) / (4 * h * h)
    return H
def independent(P, design, th0=None):
    f = lambda th: -exp_loglik(th, P, design)
    th0 = np.zeros(len(terms)) if th0 is None else th0
    r = minimize(f, th0, method='BFGS', options=dict(gtol=1e-11, maxiter=20000))
    r = minimize(f, r.x, method='Nelder-Mead', options=dict(xatol=1e-12, fatol=1e-16, maxiter=200000, maxfev=200000)) if False else r
    th = r.x; p = pth(th); dstar = p @ t
    A = num_hess(f, th)                      # expected negative Hessian by finite differences
    grad = num_grad(lambda u: pth(u) @ t, th)  # gradient of Delta(theta)
    B = np.zeros_like(A)
    for q, ix, n in cells_full(design):
        Pc = np.bincount(ix, weights=P, minlength=n)
        for c in range(n):
            s = num_grad(lambda u: np.log(pth(u)[ix == c].sum()), th); B += q * Pc[c] * np.outer(s, s)
    xs = np.linalg.lstsq(A, grad, rcond=1e-7)[0]
    resid = np.linalg.norm(A @ xs - grad) / np.linalg.norm(grad)
    return dstar, xs @ B @ xs, xs @ A @ xs, resid, th, np.linalg.eigvalsh(A)

designs = {
 'three forms (identified)': [(0.5, *form_cid([0, 1])), (0.3, *form_cid([1, 2])), (0.2, *form_cid([0, 2]))],
 'two forms (pair 0-2 never jointly)': [(0.4, *form_cid([0, 1])), (0.6, *form_cid([1, 2]))],
 'one tree (pair 1-2 never jointly)': [(1.0, *tree_cid())],
 'tree + form mix': [(0.7, *tree_cid()), (0.3, *form_cid([1, 2]))],
}
model = LogLin(V, 2)
for trial in range(3):
    P = rand_law(); print('--- law', trial, 'Delta true', P @ t)
    for name, des in designs.items():
        pstar, its = ms.pseudo_true(model, K, P, des)
        v, vm, res = ms.sandwich(K, P, pstar, des, t)
        dstar, v2, vm2, res2, th, ev = independent(P, des)
        print('%-36s code: D* %.8f sand %.6f model %.6f resid %.1e its %d | indep: D* %.8f sand %.6f model %.6f resid %.1e mineig %.1e' % (name, pstar @ t, v, vm, res, its, dstar, v2, vm2, res2, ev.min()))
