"""What few annotators identify: identified sets, unbiased panel-size estimators, confidence intervals.

Model.  Item i has a latent share pi_i in [0,1] of the annotator population that endorses the label the
evaluated model predicts ("agreement share").  n annotators drawn at random give X_i ~ Binomial(n, pi_i).
G is the law of pi over items.  A metric is T_f(G) = E f(pi):
    f(x) = x                         agreement with one random annotator          (identified for n >= 1)
    f(x) = P(Bin(m, x) > m/2)        agreement with the majority of m annotators  (identified iff m <= n)
    f(x) = 1{x > 1/2}                agreement with the population majority       (never point identified)
Everything a data set of counts can reveal about G is the count law q_j = E[Bin(j; n, pi)], j = 0..n,
equivalently the first n moments of G.  Bounds on T_f over all laws with the same count law are linear programs.
"""
import numpy as np
from scipy.optimize import linprog
from scipy.stats import binom, hypergeom, beta as betadist, chi2

# ----------------------------------------------------------------------------------------------- grid
def make_grid(t=0.5, n_cheb=1601, n_local=400):
    """Support grid on [0,1]: Chebyshev points, points clustered at t, and two copies of t itself
    ('just below' and 'just above'), so that suprema and infima of threshold functionals are attained."""
    th = np.linspace(0.0, np.pi, n_cheb)
    ch = (1.0 - np.cos(th)) / 2.0
    d = np.logspace(-7, np.log10(0.3), n_local)
    x = np.unique(np.clip(np.concatenate([ch, t - d, t + d, [0.0, 1.0]]), 0.0, 1.0))
    x = x[np.abs(x - t) > 1e-13]
    xs = np.concatenate([x, [t, t]])
    above = np.concatenate([x > t, [False, True]])
    below = np.concatenate([x < t, [True, False]])
    return xs, above, below

def binom_matrix(n, xs):
    return binom.pmf(np.arange(n + 1)[:, None], n, xs[None, :])

def f_majority(m, xs):
    """P(strict majority of m votes agrees), m odd."""
    return binom.sf(m // 2, m, xs)

# ------------------------------------------------------------------------- population identified sets
def _lp(c, A_eq, b_eq, tol=0.0):
    if tol == 0.0:
        r = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
        if r.status == 0:
            return r.fun
        tol = 1e-10
    while tol <= 1e-6:
        A_ub = np.vstack([A_eq, -A_eq]); b_ub = np.concatenate([b_eq + tol, -b_eq + tol])
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(0, None), method="highs")
        if r.status == 0:
            return r.fun
        tol *= 10
    return np.nan

def idset(q, n, f, xs=None):
    """Sharp bounds on the integral of f against measures H >= 0 with count law q (q may sum to a weight < 1)."""
    A = binom_matrix(n, xs)
    return _lp(f, A, q), -_lp(-f, A, q)

def idset_threshold(q, n, t=0.5, grid=None):
    """Bounds on H((t,1]) and on H([0,t)) for measures with count law q."""
    xs, above, below = grid if grid is not None else make_grid(t)
    return idset(q, n, above.astype(float), xs), idset(q, n, below.astype(float), xs)

def count_law_of(pis, w, n):
    """Exact count law of a discrete law with atoms pis and weights w."""
    return binom_matrix(n, np.asarray(pis)) @ np.asarray(w)

# ----------------------------------------------------------------------------- unbiased finite-panel metrics
def panel_agreement(X, n, m):
    """Unbiased estimate of the agreement with the strict majority of m annotators (m odd, m <= n_i),
    from X_i votes agreeing with the model out of n_i: average hypergeometric tail (all sub-panels of size m)."""
    X = np.asarray(X); n = np.broadcast_to(np.asarray(n), X.shape)
    return hypergeom.sf(m // 2, n, X, m)

def soft_agreement(X, n):
    return np.asarray(X) / np.asarray(n)

# --------------------------------------------------------------------------------- confidence intervals
def clopper_pearson(k, M, a):
    lo = np.where(k > 0, betadist.ppf(a / 2, k, M - k + 1), 0.0)
    hi = np.where(k < M, betadist.ppf(1 - a / 2, k + 1, M - k), 1.0)
    return lo, hi

def ci_box(hist, f_list, n, alpha=0.05, xs=None):
    """Finite-sample confidence interval for sum_g int f_g dH_g, where hist[g, j] is the number of items in
    group g (e.g. g = model output) with j agreeing votes out of n.  A Bonferroni Clopper-Pearson box holds all
    cell probabilities simultaneously with probability >= 1 - alpha; the interval is the range of the target
    over all (H_g) whose count laws lie in the box."""
    hist = np.asarray(hist, float); G, J = hist.shape; M = hist.sum()
    lo, hi = clopper_pearson(hist.ravel(), M, alpha / hist.size)
    A = binom_matrix(n, xs); K = len(xs)
    A_ub, b_ub = [], []
    for g in range(G):
        blk = np.zeros((J, G * K)); blk[:, g * K:(g + 1) * K] = A
        A_ub += [blk, -blk]; b_ub += [hi[g * J:(g + 1) * J], -lo[g * J:(g + 1) * J]]
    A_ub = np.vstack(A_ub); b_ub = np.concatenate(b_ub)
    A_eq = np.ones((1, G * K)); b_eq = [1.0]
    c = np.concatenate(f_list)
    out = []
    for s in (1, -1):
        r = linprog(s * c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
        out.append(s * r.fun if r.status == 0 else np.nan)
    return out[0], out[1]

def ci_lr(hist, f_list, n, alpha=0.05, xs=None, dof=None, coarse=None):
    """Likelihood-ratio interval: range of the target over (H_g) with 2 M KL(observed || model) <= chi2 quantile.
    dof = number of free cells (default) gives a projection interval that is asymptotically valid whatever the
    identification status; dof = 1 is the usual profile calibration (not guaranteed here; reported for comparison)."""
    import cvxpy as cp
    hist = np.asarray(hist, float); G, J = hist.shape; M = hist.sum()
    if coarse is not None:                                   # thin the grid for speed
        keep = np.unique(np.concatenate([np.arange(0, len(xs) - 2, coarse), [len(xs) - 2, len(xs) - 1]]))
    else:
        keep = np.arange(len(xs))
    A = binom_matrix(n, xs[keep]); K = len(keep)
    H = cp.Variable((G, K), nonneg=True)
    R = H @ A.T                                               # G x J cell probabilities
    phat = hist / M
    mask = phat > 0
    d = (hist.size - 1) if dof is None else dof
    thr = chi2.ppf(1 - alpha, d) / (2 * M)
    kl = cp.sum(cp.multiply(phat[mask], -cp.log(R[mask]))) + float((phat[mask] * np.log(phat[mask])).sum())
    cons = [cp.sum(H) == 1, kl <= thr]
    c = np.vstack([f[keep] for f in f_list])
    out = []
    for s in (1, -1):
        prob = cp.Problem(cp.Minimize(s * cp.sum(cp.multiply(c, H))), cons)
        try:
            prob.solve(solver=cp.CLARABEL)
            out.append(s * prob.value if prob.status in ("optimal", "optimal_inaccurate") else np.nan)
        except Exception:
            out.append(np.nan)
    return out[0], out[1]

# ------------------------------------------------------------------------------------- helper for data
def hist_by_group(X, groups, n, n_groups):
    h = np.zeros((n_groups, n + 1))
    np.add.at(h, (np.asarray(groups), np.asarray(X)), 1)
    return h

def subsample_votes(X_full, n_full, n, rng):
    """Draw n of the n_full votes of each item without replacement; returns the number of agreeing votes."""
    return rng.hypergeometric(X_full, n_full - X_full, n)
