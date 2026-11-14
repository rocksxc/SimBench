# Numerical checks of the statements used in the paper (population level, Beta laws with known formulas).
import numpy as np, sys
from scipy.special import eval_jacobi, roots_jacobi, betaln, gammaln
from scipy.stats import beta as betad, binom
sys.path.insert(0, ".")
import fewannot as fa

def beta_count_law(n, a, b):
    j = np.arange(n + 1)
    return np.exp(gammaln(n + 1) - gammaln(j + 1) - gammaln(n - j + 1) + betaln(a + j, b + n - j) - betaln(a, b))

def christoffel_beta(m, t, a, b):
    """1 / sum_{k<=m} p_k(t)^2 for the Beta(a,b) law: the largest mass at t compatible with moments up to 2m."""
    z, w = roots_jacobi(m + 40, b - 1, a - 1); w = w / w.sum()
    s = 0.0
    for k in range(m + 1):
        nk = (w * eval_jacobi(k, b - 1, a - 1, z) ** 2).sum()
        s += eval_jacobi(k, b - 1, a - 1, 2 * t - 1) ** 2 / nk
    return 1.0 / s

grid = fa.make_grid(0.5)
print("A. width of the identified set of G((1/2,1]) versus the Christoffel function and the law pi*g(1/2)/n")
for a, b in [(1.2, 0.9), (0.7, 0.5), (2.2, 2.2), (0.4, 0.4)]:
    g_half = betad.pdf(0.5, a, b)
    for n in (2, 4, 6, 10, 16, 24, 30):
        (lo, hi), _ = fa.idset_threshold(beta_count_law(n, a, b), n, grid=grid)
        lam = christoffel_beta(n // 2, 0.5, a, b)
        print(f"  Beta({a},{b}) n={n:2d}  LP width {hi-lo:.5f}  Christoffel {lam:.5f}  pi*g/n {np.pi*g_half/n:.5f}  ratio LP/law {(hi-lo)*n/(np.pi*g_half):.3f}  truth in set: {lo-1e-7 <= betad.sf(0.5,a,b) <= hi+1e-7}")
print("B. odd n")
for a, b in [(1.2, 0.9), (2.2, 2.2)]:
    g_half = betad.pdf(0.5, a, b)
    for n in (3, 5, 9, 15, 25):
        (lo, hi), _ = fa.idset_threshold(beta_count_law(n, a, b), n, grid=grid)
        print(f"  Beta({a},{b}) n={n:2d}  LP width {hi-lo:.5f}  pi*g/n {np.pi*g_half/n:.5f}  ratio {(hi-lo)*n/(np.pi*g_half):.3f}")
print("C. ceiling E max(pi,1-pi): identified width, plug-in bias and the bias law g(1/2)/(4n)")
xs = grid[0]
for a, b in [(1.2, 0.9), (2.2, 2.2), (0.4, 0.4)]:
    g_half = betad.pdf(0.5, a, b)
    z = np.linspace(0, 1, 400001); truth = np.trapezoid(np.maximum(z, 1 - z) * betad.pdf(np.clip(z, 1e-9, 1 - 1e-9), a, b), z)
    for n in (3, 5, 9, 15, 25):
        q = beta_count_law(n, a, b)
        lo, hi = fa.idset(q, n, np.maximum(xs, 1 - xs), xs)
        k = np.arange(n + 1); plug = (q * np.maximum(k, n - k) / n).sum()
        print(f"  Beta({a},{b}) n={n:2d}  set [{lo:.5f},{hi:.5f}] width {hi-lo:.5f} width*n^2 {(hi-lo)*n*n:.3f}  Jackson bound {np.pi/(2*(n+1)):.3f} | plug-in bias {plug-truth:.5f}  g/(4n) {g_half/(4*n):.5f}")
print("D. majority-of-n agreement minus consensus agreement: law 0.399*g(1/2)/sqrt(n) for the mislabel rate")
for a, b in [(1.2, 0.9), (2.2, 2.2)]:
    g_half = betad.pdf(0.5, a, b)
    z = np.linspace(1e-6, 1 - 1e-6, 400001); dens = betad.pdf(z, a, b)
    for n in (3, 5, 9, 21, 51, 101):
        mis = np.trapezoid(np.where(z > 0.5, binom.cdf(n // 2, n, z), binom.sf(n // 2, n, z)) * dens, z)
        print(f"  Beta({a},{b}) n={n:3d}  P(majority of n differs from population majority) {mis:.4f}   law {0.3989*g_half/np.sqrt(n):.4f}")
