"""Referee's independent helpers (no code shared with the authors' scripts).
Profiles x in {0,1}^m are integers (bit j = coordinate j); x_j = +1 iff bit j is 1. Label index 0 <-> y=-1, 1 <-> y=+1."""
import itertools
import numpy as np


def bitmat(m):
    return ((np.arange(1 << m)[:, None] >> np.arange(m)) & 1).astype(int)


def random_interview(m, b, sizes, rng):
    """A random deterministic interview with batch sizes `sizes` (sum = b, distinct coordinates).
    The batch asked in round k is a random function of the answers to earlier batches.
    Returns asked[x] = tuple of coordinates asked on profile x (in order)."""
    B = bitmat(m)
    asked = [None] * (1 << m)

    def rec(rows, done, k):
        if k == len(sizes):
            for r in rows: asked[r] = tuple(done)
            return
        free = [j for j in range(m) if j not in done]
        batch = [int(j) for j in rng.choice(free, sizes[k], replace=False)]
        for vals in itertools.product((0, 1), repeat=len(batch)):
            sub = [r for r in rows if all(B[r, j] == v for j, v in zip(batch, vals))]
            if sub: rec(sub, done + batch, k + 1)
    rec(list(range(1 << m)), [], 0)
    return asked


def cells_of(m, asked):
    """Transcript cells of an interview: list of arrays of profiles sharing (set asked, answers)."""
    B = bitmat(m); d = {}
    for x in range(1 << m):
        key = (asked[x], tuple(B[x, list(asked[x])]))
        d.setdefault(key, []).append(x)
    return [np.array(v) for v in d.values()]


def ci_law(m, rng, lo=0.15, hi=0.85, py1=None):
    """Random law with features independent given the label: P[y, x]."""
    B = bitmat(m)
    py1 = rng.uniform(0.2, 0.8) if py1 is None else py1
    p = rng.uniform(lo, hi, (2, m))
    P = np.stack([(1 - py1 if y == 0 else py1) * np.prod(np.where(B == 1, p[y], 1 - p[y]), axis=1) for y in (0, 1)])
    return P, p, np.array([1 - py1, py1])


def ci_basis(m, P):
    """A basis of the tangent space of M_ci at P built from the parametrisation (NOT standardised, not orthogonal):
    s_0 = 1{y=+1} - P(y=+1);  s_{y,j} = 1{Y=y} (x_j - E[x_j | Y=y]).  Returns array (1+2m, 2, 2^m)."""
    B = bitmat(m); X = 2.0 * B - 1; py = P.sum(1)
    out = [np.stack([np.full(1 << m, -py[1]), np.full(1 << m, 1 - py[1])])]
    for y in (0, 1):
        for j in range(m):
            mu = (P[y] @ X[:, j]) / py[y]
            f = np.zeros((2, 1 << m)); f[y] = X[:, j] - mu; out.append(f)
    return np.array(out)


def info_matrix(P, basis, cells_by_label):
    """Fisher information of one record of an interview in the given basis, by brute force:
    I = sum over label y and transcript cells c of P(c,y) E[s | c,y] E[s | c,y]'.
    cells_by_label[y] = cells of the interview used for label y (label-blind: the same list twice)."""
    p = basis.shape[0]; I = np.zeros((p, p))
    for y in (0, 1):
        for c in cells_by_label[y]:
            pc = P[y, c].sum()
            if pc <= 0: continue
            e = basis[:, y, c] @ P[y, c] / pc
            I += pc * np.outer(e, e)
    return I


def gradient(P, basis, d):
    t = np.stack([-d, d]); delta = float((P * t).sum())
    return np.array([float((P * (t - delta) * s).sum()) for s in basis]), delta, t


def value(I, v, tol=1e-9):
    """v' I^+ v, +inf if v is not in the range of I."""
    u = np.linalg.lstsq(I, v, rcond=1e-12)[0]
    if np.linalg.norm(I @ u - v) > tol * max(1.0, np.linalg.norm(v)): return np.inf
    return float(v @ u)


def Mb(c, b):
    """Referee's own solver for min sum c_j^2/pi_j, 0<=pi<=1, sum pi <= b (0/0=0): bisection on the multiplier."""
    a = np.abs(np.asarray(c, float)); a = a[a > 0]
    if len(a) <= b: return float(np.sum(a ** 2))
    lo, hi = 0.0, a.sum()            # sum_j min(1, a_j/lam) is decreasing in lam; want it equal to b
    for _ in range(200):
        lam = 0.5 * (lo + hi)
        if np.minimum(1.0, a / lam).sum() > b: lo = lam
        else: hi = lam
    pi = np.minimum(1.0, a / hi)
    return float(np.sum(a ** 2 / pi))


def closed_forms(P, d, b):
    """Closed forms of Theorem (b) computed directly from the definitions (ci law P[y,x], contrast d on the cube)."""
    m = int(np.log2(P.shape[1])); B = bitmat(m); X = 2.0 * B - 1; py = P.sum(1)
    t = np.stack([-d, d]); delta = float((P * t).sum())
    cond = np.array([(P[y] * t[y]).sum() / py[y] for y in (0, 1)])
    vey = float(py @ (cond - delta) ** 2)
    dh = np.zeros((2, m))
    for y in (0, 1):
        for j in range(m):
            mu = (P[y] @ X[:, j]) / py[y]; sd = np.sqrt((P[y] @ (X[:, j] - mu) ** 2) / py[y])
            dh[y, j] = (P[y] * d) @ ((X[:, j] - mu) / sd) / py[y]
    lab = vey + sum(py[y] * Mb(dh[y], b) for y in (0, 1))
    blind = vey + Mb(np.sqrt(py[0] * dh[0] ** 2 + py[1] * dh[1] ** 2), b)
    return dict(vey=vey, dh=dh, lab=lab, blind=blind, delta=delta, py=py)


def random_contrast(m, b, rng, kind='tree'):
    """A contrast of degree <= b with values in [-1, 1]."""
    if kind == 'tree':
        asked = random_interview(m, b, [1] * b, rng); cs = cells_of(m, asked); d = np.zeros(1 << m)
        for c in cs: d[c] = rng.uniform(-1, 1)
        return d
    X = 2.0 * bitmat(m) - 1; d = np.zeros(1 << m)
    for k in range(0, b + 1):
        for S in itertools.combinations(range(m), k):
            d += rng.normal() * np.prod(X[:, list(S)], axis=1)
    return d / np.abs(d).max()
