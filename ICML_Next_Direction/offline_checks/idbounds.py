# Offline feasibility check: sharp identification bounds for the unsolved fraction
# U_k = E[(1-pi)^k] when only the law of Binomial(n, pi) is known (first n moments of G).
import numpy as np, sys
from scipy.optimize import linprog
from scipy.special import betaln, gammaln
from scipy.stats import binom

def grid(n, kmax):
    lo = np.concatenate([[0.0], np.logspace(-9, 0, 2400)])
    th = np.linspace(0, np.pi, 1500)
    ch = (1 - np.cos(th)) / 2
    g = np.unique(np.concatenate([lo, ch, 1 - np.logspace(-7, 0, 400)]))
    return g[(g >= 0) & (g <= 1)]

def fingerprint_beta(n, a, b):
    j = np.arange(n + 1)
    logc = gammaln(n + 1) - gammaln(j + 1) - gammaln(n - j + 1)
    return np.exp(logc + betaln(a + j, b + n - j) - betaln(a, b))

def bounds(n, ks, a, b):
    g = grid(n, max(ks))
    A = binom.pmf(np.arange(n + 1)[:, None], n, g[None, :])
    c = fingerprint_beta(n, a, b)
    out = []
    for k in ks:
        f = (1 - g) ** k
        r = []
        for s in (1, -1):
            res = linprog(s * f, A_eq=A, b_eq=c, bounds=(0, None), method="highs",
                          options={"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10})
            r.append(s * res.fun if res.status == 0 else np.nan)
        true = np.exp(betaln(a, b + k) - betaln(a, b))
        out.append((k, r[0], true, r[1]))
    return out

if __name__ == "__main__":
    for a, b in [(0.3, 1.5), (0.6, 2.0), (1.0, 3.0)]:
        for n in (10, 20, 40):
            ks = sorted(set([n, 2 * n, 4 * n, n * n // 4, n * n // 2, n * n, 2 * n * n, 4 * n * n, 16 * n * n, 10**7]))
            print(f"Beta({a},{b}) n={n}")
            for k, lo, tr, hi in bounds(n, ks, a, b):
                print(f"  k={k:>9d} k/n^2={k/n/n:8.3f}  lower={lo:.5f} true={tr:.5f} upper={hi:.5f}  rel.width={(hi-lo)/tr:.3f}")
