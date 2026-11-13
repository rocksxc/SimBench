# Offline feasibility check 2: finite number of tasks M.
# Estimators (1/M) sum_i g(X_i), X_i ~ Bin(n, pi_i).  Worst-case RMSE <= sup-bias + ||g||_inf / sqrt(M).
# For each bound C on ||g||_inf minimise the sup-bias (an LP); report the best trade-off.
import numpy as np
from scipy.optimize import linprog
from scipy.stats import binom

def best(n, k, Ms, Cs=(1, 2, 4, 8, 16, 32, 64, 128, 512, 2048, 1e4, 1e5, 1e6)):
    th = np.linspace(0, np.pi, 1200)
    g = np.unique(np.concatenate([[0], np.logspace(-8, 0, 1200), (1 - np.cos(th)) / 2]))
    B = binom.pmf(np.arange(n + 1)[None, :], n, g[:, None])      # grid x (n+1)
    f = (1 - g) ** k
    # variables: g_0..g_n, eps ; minimise eps s.t. |B g - f| <= eps
    A = np.block([[B, -np.ones((len(g), 1))], [-B, -np.ones((len(g), 1))]])
    b = np.concatenate([f, -f])
    c = np.zeros(n + 2); c[-1] = 1
    res = {}
    for C in Cs:
        r = linprog(c, A_ub=A, b_ub=b, bounds=[(-C, C)] * (n + 1) + [(0, None)], method="highs")
        res[C] = r.fun if r.status == 0 else np.nan
    out = {}
    for M in Ms:
        out[M] = min(res[C] + C / np.sqrt(M) for C in Cs if np.isfinite(res[C]))
    return out, res

for n in (20, 50):
    print(f"n={n}")
    for t in (1, 2, 3, 5, 10, 20, 50):
        k = t * n
        out, res = best(n, k, (300, 3000, 10**5, 10**7, 10**10))
        print(f"  k={k:5d} (k/n={t:3d}, k/n^2={k/n/n:5.2f})  worst-case RMSE bound: " +
              "  ".join(f"M={M:.0e}: {v:.4f}" for M, v in out.items()) + f"   bias with |g|<=1: {res[1]:.4f}, unconstrained-ish: {res[1e6]:.5f}")
