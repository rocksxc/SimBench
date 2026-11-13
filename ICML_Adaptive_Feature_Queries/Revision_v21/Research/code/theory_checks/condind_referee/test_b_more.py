"""Referee tests: (A) explicit example where label-blind forms lose to a label-blind tree in M_ci;
(B) item (iii): pairwise model at product laws, balanced / unbalanced label, label-blind / label-dependent interviews."""
import itertools, sys
import numpy as np
from ref_common import *
from test_b_theorem import copt, compositions, incl, label_part

rng = np.random.default_rng(5)


def example_gap(eps=0.02, b=3, a=0.25, verbose=True):
    """m = 5. X_1 is a near-copy of the label; X_2,X_3 vary only in class +1, X_4,X_5 only in class -1; d linear."""
    m = 5; B = bitmat(m); X = 2.0 * B - 1
    p = np.array([[eps, eps, eps, 0.5, 0.5],      # P(X_j = +1 | Y = -1)
                  [1 - eps, 0.5, 0.5, eps, eps]])  # P(X_j = +1 | Y = +1)
    py = np.array([0.5, 0.5])
    P = np.stack([py[y] * np.prod(np.where(B == 1, p[y], 1 - p[y]), axis=1) for y in (0, 1)])
    d = a * (X[:, 1] + X[:, 2] + X[:, 3] + X[:, 4])
    basis = ci_basis(m, P); v, delta, t = gradient(P, basis, d); cf = closed_forms(P, d, b)
    # the tree: ask X_1; if +1 ask {2,3}, else ask {4,5}  (coordinates 0-based: 0; {1,2}; {3,4})
    asked = [((0, 1, 2) if B[x, 0] == 1 else (0, 3, 4)) for x in range(1 << m)]
    cl = cells_of(m, asked); Itree = info_matrix(P, basis, [cl, cl]); wtree = value(Itree, v)
    forms = list(itertools.combinations(range(m), b)); cs = [cells_of(m, [S] * (1 << m)) for S in forms]
    wforms, q = copt([info_matrix(P, basis, [c, c]) for c in cs], v)
    if verbose:
        print('  eps=%.3f b=%d: Var(E[t|Y])=%.4f  W_lab(closed)=%.4f  W_fixed blind: closed %.4f, SDP %.4f  | one label-blind tree: %.4f  -> forms/tree = %.3f (forms/lab = %.3f)'
              % (eps, b, cf['vey'], cf['lab'], cf['blind'], wforms, wtree, wforms / wtree, cf['blind'] / cf['lab']))
    return wforms / wtree


def pairwise_basis(m, P):
    """chi_A - E chi_A for 1 <= |A| <= 2 over the m features and the label."""
    X = 2.0 * bitmat(m) - 1; out = []
    var = [np.stack([X[:, j], X[:, j]]) for j in range(m)] + [np.stack([-np.ones(1 << m), np.ones(1 << m)])]
    for k in (1, 2):
        for A in itertools.combinations(range(m + 1), k):
            f = np.ones((2, 1 << m))
            for j in A: f = f * var[j]
            out.append(f - (P * f).sum())
    return np.array(out)


def test_iii(trials=30):
    res = {}
    for balanced in (True, False):
        for labdep in (False, True):
            worst = 0.0; lo = np.inf; hi = -np.inf
            for _ in range(trials):
                m = int(rng.integers(3, 6)); b = int(rng.integers(2, m)); B = bitmat(m); X = 2.0 * B - 1
                p1 = rng.uniform(0.15, 0.85, m); py1 = 0.5 if balanced else rng.uniform(0.15, 0.85) * rng.choice([1.0])
                if not balanced and abs(py1 - 0.5) < 0.1: py1 = 0.25
                px = np.prod(np.where(B == 1, p1, 1 - p1), axis=1); P = np.stack([(1 - py1) * px, py1 * px])
                d = random_contrast(m, b, rng, kind=rng.choice(['tree', 'poly']))
                basis = pairwise_basis(m, P); v, delta, t = gradient(P, basis, d)
                n = int(rng.integers(2, 8)); q = rng.dirichlet(np.ones(n)); I = 0; pi = np.zeros((2, m))
                for i in range(n):
                    r = int(rng.integers(1, b + 1)); sizes = list(compositions(b, r)[rng.integers(len(compositions(b, r)))])
                    a0 = random_interview(m, b, sizes, rng); a1 = random_interview(m, b, [1] * b, rng) if labdep else a0
                    I = I + q[i] * info_matrix(P, basis, [cells_of(m, a0), cells_of(m, a1)]); pi += q[i] * incl(m, P, [a0, a1])
                val = value(I, v)
                phi = (X - (px @ X)) / np.sqrt(px @ (X - (px @ X)) ** 2); dh = (px * d) @ phi
                sig2 = 4 * py1 * (1 - py1)       # Var(Y)
                form = (px @ d) ** 2 * sig2 + sig2 * np.sum(dh ** 2 / (0.5 * (pi[0] + pi[1]))) if not labdep else None
                if form is not None:
                    rel = (val - form) / form; worst = max(worst, abs(rel)); lo = min(lo, rel); hi = max(hi, rel)
                else:
                    # label-dependent: compare with the M_ci value for the realised inclusion vectors (a lower bound, T_ci subset of T_2)
                    lb = (px @ d) ** 2 * sig2 + sig2 * sum((1 - py1 if y == 0 else py1) * np.sum(dh ** 2 / pi[y]) for y in (0, 1))
                    rel = (val - lb) / lb; lo = min(lo, rel); hi = max(hi, rel)
            res[(balanced, labdep)] = (lo, hi)
            print('  balanced=%s label-dependent=%s: (v\'I^+v - formula)/formula over random mixtures: min %.2e max %.2e' % (balanced, labdep, lo, hi))


def test_iii_opt(trials=10):
    """Optimal label-blind forms in the pairwise model at balanced product laws vs (E d)^2 + M_b(dhat); and a menu with trees."""
    w = 0.0; wt = 0.0
    for _ in range(trials):
        m = int(rng.integers(4, 6)); b = int(rng.integers(2, m)); B = bitmat(m); X = 2.0 * B - 1
        p1 = rng.uniform(0.15, 0.85, m); px = np.prod(np.where(B == 1, p1, 1 - p1), axis=1); P = np.stack([0.5 * px, 0.5 * px])
        d = random_contrast(m, b, rng, kind=rng.choice(['tree', 'poly'])); basis = pairwise_basis(m, P); v, delta, t = gradient(P, basis, d)
        phi = (X - (px @ X)) / np.sqrt(px @ (X - (px @ X)) ** 2); dh = (px * d) @ phi; closed = (px @ d) ** 2 + Mb(dh, b)
        forms = [cells_of(m, [S] * (1 << m)) for S in itertools.combinations(range(m), b)]
        trees = [cells_of(m, random_interview(m, b, [1] * b, rng)) for _ in range(40)]
        vf, _ = copt([info_matrix(P, basis, [c, c]) for c in forms], v)
        vt, _ = copt([info_matrix(P, basis, [c, c]) for c in forms + trees], v)
        w = max(w, abs(vf - closed) / closed); wt = max(wt, abs(vt - closed) / closed)
    print('  pairwise model, balanced product laws: optimal forms vs (E d)^2 + M_b(dhat): max rel. diff %.2e; forms + 40 random trees: %.2e' % (w, wt))


if __name__ == '__main__':
    print('(A) label-blind forms vs one label-blind tree in M_ci (explicit example)')
    for eps in (0.1, 0.02, 0.002): example_gap(eps, 3)
    print('(B) item (iii)')
    test_iii(); test_iii_opt()
