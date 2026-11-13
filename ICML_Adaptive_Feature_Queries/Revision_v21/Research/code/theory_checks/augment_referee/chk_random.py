"""thm:augment(a) consequence W_fixed^{b+c}(P) <= K+ W_branch(P): own solver, complete depth-3 trees on 7 distinct
coordinates (heap order), (i) pointer-tree contrast d = last answer, uniform law; (ii) random leaf values, random
full-support laws of (X,Y) (label-dependent tables, design blind to label)."""
import numpy as np
from chk_address import program
from chk_sim import jc
rng = np.random.default_rng(11)
b = 3; m = 7; n = 1 << m; X = ((np.arange(n)[:, None] >> np.arange(m)) & 1)
node = np.zeros(n, int); leafid = np.zeros(n, int); last = np.zeros(n, int)
for x in range(n):
    v = 0
    for lvl in range(b):
        a = X[x, v]; last[x] = a
        if lvl < b - 1: v = 2 * v + 1 + a
    leafid[x] = 2 * (v - 3) + a
d = 2.0 * last - 1; mu = np.full(n, 1.0 / n)
for c in range(0, 4):
    Kp = 2 ** (b - 1 - jc(c, b))
    print('pointer tree b=3 m=7, forms of size %d: W_fixed(uniform)/W_branch = %.4f, V_fixed/V_branch = %.4f, K+ = %d' % (b + c, program(m, X, [d], [mu], b + c), program(m, X, [d], None, b + c, worst=True), Kp), flush=True)
worst = {c: 0.0 for c in range(4)}
for trial in range(12):
    vals = rng.choice([-1.0, 1.0], size=8); dd = vals[leafid]
    P = rng.dirichlet(np.full(2 * n, 0.3)); P = 0.95 * P + 0.05 / (2 * n); P0, P1 = P[:n], P[n:]   # Y=-1, Y=+1
    Delta = float(P1 @ dd - P0 @ dd); var = float((P0 + P1) @ dd ** 2 - Delta ** 2)
    for c in range(0, 4):
        Kp = 2 ** (b - 1 - jc(c, b)); M = program(m, X, [dd, -dd], [P1, P0], b + c); r = (M - Delta ** 2) / var
        worst[c] = max(worst[c], r / Kp); assert r <= Kp * (1 + 1e-6), (trial, c, r, Kp)
print('random leaf values and random laws, 12 trials: max of [W_fixed^{b+c}/Var(t)] / K+ by c:', {c: round(v, 4) for c, v in worst.items()})
