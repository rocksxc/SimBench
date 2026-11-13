"""Lower bounds on W^(k)_branch for the address contrast by level-weighted witnesses h = sum_i alpha_i * (order-i part of t), exact DP over trees."""
import math, sys
from functools import lru_cache
import numpy as np

def bound(b, alphas):
    kap = b - 1; D = 2 ** kap; m = kap + D
    abits = [[(1 if (j >> i) & 1 else -1) for i in range(kap)] for j in range(D)]
    def leaf_energy(fixed):
        fx = dict(fixed); A = [i for i in range(kap) if i in fx]; tot = 0.0
        for j in range(D):
            if kap + j not in fx: continue
            signs = [fx[i] * abits[j][i] for i in A]
            neg = sum(1 for s in signs if s < 0); pos = len(signs) - neg
            c = sum(alphas[u + w] * math.comb(pos, u) * math.comb(neg, w) * (-1) ** w
                    for u in range(pos + 1) for w in range(neg + 1) if u + w < len(alphas))
            tot += fx[kap + j] * c
        return 2.0 ** (-len(fixed)) * (tot * 2.0 ** -kap) ** 2
    @lru_cache(maxsize=None)
    def V(fixed, r):
        if r == 0: return leaf_energy(fixed)
        fx = dict(fixed)
        return max(V(tuple(sorted(fixed + ((j, 1),))), r - 1) + V(tuple(sorted(fixed + ((j, -1),))), r - 1) for j in range(m) if j not in fx)
    num = (sum(a * math.comb(kap, i) for i, a in enumerate(alphas)) / D) ** 2
    return num / V((), b)

b = int(sys.argv[1]); k = int(sys.argv[2])
best = (0, None)
if k == 3:
    for a1 in np.linspace(0, 2, 41):
        v = bound(b, [1.0, a1]); best = max(best, (v, a1))
    print(f'b={b} k=3: best level-weighted witness alpha1/alpha0={best[1]:.3f} gives W_branch^(3) >= {best[0]:.6f}')
