import sys, numpy as np
sys.path.insert(0, 'SCRATCH/v21/Research/code')
from capcurve_v21 import fixed_ratio
from chk_address import program
rng = np.random.default_rng(3)
b = 3; m = 7; n = 1 << m; X = ((np.arange(n)[:, None] >> np.arange(m)) & 1)
last = np.zeros(n, int)
for x in range(n):
    v = 0
    for lvl in range(b):
        a = X[x, v]; last[x] = a
        if lvl < b - 1: v = 2 * v + 1 + a
d = 2.0 * last - 1
emp = np.full(2 * n, 0.5 / n)
for B in (3, 4, 5, 6):
    print('pointer tree, uniform, size %d: authors fixed_ratio %.6f  own %.6f' % (B, fixed_ratio(m, B, emp, d)[0], program(m, X, [d], [np.full(n, 1.0 / n)], B)))
for trial in range(3):
    P = rng.dirichlet(np.full(2 * n, 0.3)); P = 0.95 * P + 0.05 / (2 * n); P0, P1 = P[:n], P[n:]
    Delta = float(P1 @ d - P0 @ d); var = 1 - Delta ** 2
    for B in (3, 5):
        own = (program(m, X, [d, -d], [P1, P0], B) - Delta ** 2) / var
        print('random law %d size %d: authors %.6f own %.6f' % (trial, B, fixed_ratio(m, B, P, d)[0], own))
