# Offline feasibility checks 3 and 4.
import numpy as np
from scipy.optimize import linprog, minimize
from scipy.special import betaln, gammaln
from scipy.stats import binom, chi2

rng = np.random.default_rng(7)

# ---- 3. a beta-binomial forecast under a non-Beta truth -------------------------------------
def sample_pi(M, kind):
    if kind == "beta":            # the parametric model is right
        return rng.beta(0.35, 1.6, M)
    if kind == "floor":           # same bulk, but 12% of tasks are effectively unsolvable
        p = rng.beta(0.5, 1.6, M); z = rng.random(M) < 0.12; p[z] = 1e-7; return p
    if kind == "lognormal":       # success rates log-normal, truncated to [0,1]
        return np.minimum(np.exp(rng.normal(-3.0, 2.2, M)), 1.0)

def bb_loglik(par, cnt, n):
    a, b = np.exp(par); j = np.arange(n + 1)
    lp = gammaln(n + 1) - gammaln(j + 1) - gammaln(n - j + 1) + betaln(a + j, b + n - j) - betaln(a, b)
    return -(cnt * lp).sum()

def fit_bb(cnt, n):
    best = None
    for s in [(-1, 0), (0, 0), (-2, 1), (-0.5, 1.5)]:
        r = minimize(bb_loglik, s, args=(cnt, n), method="Nelder-Mead", options={"xatol": 1e-7, "fatol": 1e-9, "maxiter": 4000})
        if best is None or r.fun < best.fun: best = r
    return np.exp(best.x)

print("3. beta-binomial forecast of the unsolved fraction U_k = E(1-pi)^k   (M = 2000 tasks, n = 30 attempts)")
n, M = 30, 2000
for kind in ("beta", "floor", "lognormal"):
    rows = []
    for rep in range(20):
        pi = sample_pi(M, kind)
        x = rng.binomial(n, pi); cnt = np.bincount(x, minlength=n + 1)
        a, b = fit_bb(cnt, n)
        j = np.arange(n + 1)
        pm = np.exp(gammaln(n + 1) - gammaln(j + 1) - gammaln(n - j + 1) + betaln(a + j, b + n - j) - betaln(a, b))
        # Pearson goodness of fit with pooled cells (expected >= 5)
        e = M * pm; order = np.argsort(e); pooled_o, pooled_e, so, se = [], [], 0, 0
        for i in order:
            so += cnt[i]; se += e[i]
            if se >= 5: pooled_o.append(so); pooled_e.append(se); so = se = 0
        if se > 0: pooled_o[-1] += so; pooled_e[-1] += se
        X2 = ((np.array(pooled_o) - np.array(pooled_e)) ** 2 / np.array(pooled_e)).sum()
        pval = chi2.sf(X2, len(pooled_e) - 3)
        r = [pval]
        for k in (30, 300, 3000, 30000):
            r += [np.exp(betaln(a, b + k) - betaln(a, b)), np.mean((1 - pi) ** k)]
        rows.append(r)
    R = np.array(rows)
    print(f"  truth = {kind:9s}  share of replications where the fit is not rejected at 5%: {np.mean(R[:,0] > 0.05):.2f}")
    for i, k in enumerate((30, 300, 3000, 30000)):
        print(f"     k={k:6d}  forecast {R[:,1+2*i].mean():.4f}   truth {R[:,2+2*i].mean():.4f}")

# ---- 4. majority vote: what n attempts identify about the infinite-vote accuracy ----------------
print("4. identification interval for G(pi > 1/2), the accuracy of an infinite majority vote (two answers)")
def fingerprint_beta(n, a, b):
    j = np.arange(n + 1)
    return np.exp(gammaln(n + 1) - gammaln(j + 1) - gammaln(n - j + 1) + betaln(a + j, b + n - j) - betaln(a, b))
from scipy.stats import beta as betad
for a, b in [(1.2, 0.9), (0.7, 0.5)]:
    for n in (5, 10, 20, 40, 80):
        th = np.linspace(0, np.pi, 4001); g = np.unique(np.concatenate([(1 - np.cos(th)) / 2, np.linspace(0.3, 0.7, 4001), [0.5, 0.5 + 1e-9]]))
        A = binom.pmf(np.arange(n + 1)[:, None], n, g[None, :]); c = fingerprint_beta(n, a, b)
        f = (g > 0.5).astype(float); r = []
        for s in (1, -1):
            res = linprog(s * f, A_eq=A, b_eq=c, bounds=(0, None), method="highs")
            r.append(s * res.fun if res.status == 0 else np.nan)
        tr = betad.sf(0.5, a, b)
        print(f"  Beta({a},{b}) n={n:3d}  [{r[0]:.4f}, {r[1]:.4f}]  truth {tr:.4f}  width {r[1]-r[0]:.4f}  width*n {n*(r[1]-r[0]):.3f}")
