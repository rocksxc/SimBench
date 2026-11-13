import sys, warnings
import numpy as np, cvxpy as cp
from scipy.optimize import minimize
sys.path.insert(0, 'SCRATCH/v20/Research/code')
import fill_v20 as fv
from ref_common import Mb
warnings.simplefilter('ignore')
rng = np.random.default_rng(3)
def cvx_M(c, b):
    c = np.abs(np.asarray(c, float)); a = c[c > 0]
    if len(a) == 0: return 0.0, 'opt'
    s = a.max(); a = a / s; pi = cp.Variable(len(a)); u = cp.Variable(len(a))
    # SOCP form: a_j^2/pi_j <= u_j
    prob = cp.Problem(cp.Minimize(cp.sum(u)), [pi <= 1, cp.sum(pi) <= b, pi >= 0] + [cp.quad_over_lin(a[j], pi[j]) <= u[j] for j in range(len(a))])
    prob.solve(solver='CLARABEL'); return float(prob.value) * s * s, prob.status
def slsqp_M(c, b):
    c = np.abs(np.asarray(c, float)); a = c[c > 0]
    if len(a) == 0: return 0.0
    a = a / a.max(); best = np.inf
    for _ in range(6):
        z0 = rng.uniform(0.05, 1, len(a)); z0 = z0 * min(1, b / z0.sum())
        r = minimize(lambda z: np.sum(a ** 2 / z), z0, jac=lambda z: -a ** 2 / z ** 2, bounds=[(1e-9, 1)] * len(a), constraints=[dict(type='ineq', fun=lambda z: b - z.sum(), jac=lambda z: -np.ones(len(z)))], method='SLSQP', options=dict(maxiter=2000, ftol=1e-15))
        best = min(best, r.fun)
    return best * np.abs(c).max() ** 2
w = dict(cvx_opt=0.0, slsqp_lo=0.0, slsqp_hi=0.0); nbad = 0; n = 0
for _ in range(300):
    m = int(rng.integers(1, 9)); b = int(rng.integers(1, m + 1)); c = rng.normal(size=m) * rng.choice([0.05, 1.0, 5.0], size=m)
    if rng.random() < 0.5: c[rng.random(m) < 0.4] = 0.0
    f = fv.waterfill(c, b); s, st = cvx_M(c, b); q = slsqp_M(c, b); n += 1
    if st == 'optimal': w['cvx_opt'] = max(w['cvx_opt'], abs(f - s) / max(s, 1e-300) if s > 0 else abs(f))
    else: nbad += 1
    if q > 0: w['slsqp_lo'] = max(w['slsqp_lo'], (f - q) / q); w['slsqp_hi'] = max(w['slsqp_hi'], (q - f) / q)
print('waterfill vs CLARABEL (status optimal, %d of %d): max rel diff %.2e; vs best of 6 SLSQP starts: waterfill above by at most %.2e, below by at most %.2e' % (n - nbad, n, w['cvx_opt'], w['slsqp_lo'], w['slsqp_hi']))
