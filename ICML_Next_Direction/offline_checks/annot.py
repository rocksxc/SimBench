# Offline feasibility check for the second candidate: what n annotators per item identify.
# Item i has population positive rate pi_i; n annotators give X_i ~ Bin(n, pi_i); a model predicts yhat_i.
# Consensus accuracy  = P(yhat = 1{pi > 1/2});  ceiling = E max(pi, 1-pi)  (best agreement with a random annotator).
import numpy as np
from scipy.optimize import linprog
from scipy.stats import binom

rng = np.random.default_rng(3)
def grid():
    th = np.linspace(0, np.pi, 3001)
    return np.unique(np.concatenate([(1 - np.cos(th)) / 2, np.linspace(0.25, 0.75, 3001), [0.5 - 1e-9, 0.5 + 1e-9]]))
g = grid()

def idset(c, n, f):
    A = binom.pmf(np.arange(n + 1)[:, None], n, g[None, :])
    out = []
    for s in (1, -1):
        r = linprog(s * f, A_eq=A, b_eq=c, bounds=(0, None), method="highs")
        out.append(s * r.fun if r.status == 0 else np.nan)
    return out

def law(pis, w, n):          # exact count law of a discrete mixing distribution
    return (binom.pmf(np.arange(n + 1)[:, None], n, pis[None, :]) * w[None, :]).sum(1)

# population of items: mostly clear, a contested minority (shape loosely like re-annotated NLI / toxicity items)
N = 400000
pi = np.where(rng.random(N) < 0.7, rng.beta(0.5, 6, N), rng.beta(2.2, 2.2, N))
flip = rng.random(N) < 0.5; pi = np.where(flip, 1 - pi, pi)
for name, noise in [("model A (follows the crowd closely)", 0.10), ("model B (noisier on contested items)", 0.25)]:
    yhat = (pi + rng.normal(0, noise, N) > 0.5).astype(int)
    truth = np.mean(yhat == (pi > 0.5)); ceil = np.mean(np.maximum(pi, 1 - pi)); soft = np.mean(np.where(yhat == 1, pi, 1 - pi))
    print(f"{name}: consensus accuracy {truth:.4f}; agreement with a random annotator {soft:.4f}; ceiling of that agreement {ceil:.4f}")
    # histogram representation of G within each prediction group
    bins = np.linspace(0, 1, 2001); mid = (bins[:-1] + bins[1:]) / 2
    for n in (3, 5, 9, 21, 51):
        lo = hi = 0.0; plug = 0.0
        for y in (0, 1):
            m = yhat == y; w = np.histogram(pi[m], bins)[0] / N
            c = law(mid, w, n)
            f = (g > 0.5).astype(float) if y == 1 else (g < 0.5).astype(float)
            a, b = idset(c, n, f); lo += a; hi += b
            maj = binom.sf(n // 2, n, mid) if y == 1 else binom.cdf(n // 2, n, mid)   # n odd: no ties
            plug += (w * maj).sum()
        w = np.histogram(pi, bins)[0] / N; c = law(mid, w, n)
        a, b = idset(c, n, np.maximum(g, 1 - g))
        k = np.arange(n + 1); plugceil = (c * np.maximum(k, n - k) / n).sum()
        print(f"   n={n:2d}: accuracy vs majority-of-n {plug:.4f} | identified set for consensus accuracy [{lo:.4f}, {hi:.4f}] (width {hi-lo:.4f})"
              f" | ceiling: plug-in {plugceil:.4f}, identified set [{a:.4f}, {b:.4f}]")
