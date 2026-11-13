"""Independent check of thm:augment(c): product of k address blocks, kappa address bits each. Forms of size b+c.
(1) brute-force energies over all forms (uniform law) vs prod r_j 2^{s_j-2kappa} and vs the bound (1+c/k)^k 2^{-k kappa};
(2) integer maximisation of prod phi(u_j); (3) exact program at the uniform law for the small case."""
import itertools, math, sys, numpy as np
from chk_address import program

def product(k, kappa):
    D = 1 << kappa; blk = kappa + D; m = k * blk
    X = ((np.arange(1 << m)[:, None] >> np.arange(m)) & 1); d = np.ones(1 << m)
    for j in range(k):
        o = j * blk; a = X[:, o:o + kappa] @ (1 << np.arange(kappa)) if kappa else np.zeros(1 << m, int)
        d *= 2.0 * X[np.arange(1 << m), o + kappa + a] - 1
    return m, X, d

def phi(u): return float(u) if u >= 1 else 2.0 ** (u - 1)

# (2) integer maximisation: max prod phi(u_j), sum u_j <= k + c, u_j in [-4, k+c+4]
for k in (1, 2, 3, 4):
    for c in range(0, 9):
        best = max(np.prod([phi(u) for u in us]) for us in itertools.product(range(-3, k + c + 4), repeat=k) if sum(us) <= k + c)
        q, r = divmod(k + c, k); bal = (q + 1) ** r * q ** (k - r)
        assert abs(best - bal) < 1e-9 and best <= (1 + c / k) ** k + 1e-12, (k, c, best, bal)
print('integer maximum of prod phi(u_j) equals the balanced allocation and is <= (1+c/k)^k for k<=4, c<=8')
# per-block bound r 2^s <= 2^kappa phi(u), u = s + r - kappa
for kappa in range(0, 6):
    for s in range(0, kappa + 1):
        for r in range(1, 2 ** kappa + 1):
            assert r * 2 ** s <= 2 ** kappa * phi(s + r - kappa) + 1e-12
print('per-block bound r 2^s <= 2^kappa phi(s+r-kappa) holds for kappa<=5')

for (k, kappa) in ((2, 1), (3, 1), (2, 2)):
    m, X, d = product(k, kappa); b = k * (kappa + 1); n = 1 << m; mu = np.full(n, 1.0 / n); blk = kappa + (1 << kappa)
    for c in range(0, k * (2 ** kappa - 1) + 1):
        B = b + c; emax = 0; dev = 0
        for T in itertools.combinations(range(m), B):
            code = X[:, list(T)] @ (1 << np.arange(B)); num = np.bincount(code, weights=mu * d, minlength=1 << B); den = np.bincount(code, weights=mu, minlength=1 << B)
            e = float(np.sum(num ** 2 / den)); emax = max(emax, e)
            f = 1.0
            for j in range(k):
                s = sum(1 for i in T if j * blk <= i < j * blk + kappa); r = sum(1 for i in T if j * blk + kappa <= i < (j + 1) * blk); f *= r * 2.0 ** (s - 2 * kappa)
            dev = max(dev, abs(e - f))
        bound = (1 + c / k) ** k * 2.0 ** (-k * kappa)
        line = 'k %d kappa %d b %d m %d c %d: max energy %.6f, bound (1+c/k)^k 2^{-k kappa} = %.6f, %s; energy formula dev %.1e; V lower bound claimed %.4f, from true max energy %.4f' % (k, kappa, b, m, c, emax, bound, 'EQUAL' if abs(emax - bound) < 1e-12 else ('strict' if emax < bound else 'VIOLATED'), dev, 1 / bound, 1 / emax)
        if B < m and math.comb(m, B) * (1 << B) <= 40000 and n <= 4096:
            line += '; W_fixed(uniform) = %.5f' % program(m, X, [d], [mu], B)
            if n <= 512: line += '; V_fixed = %.5f' % program(m, X, [d], None, B, worst=True)
        print(line, flush=True)
