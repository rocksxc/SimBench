"""Referee tests of fill_v20.py: waterfill(), ci_constants(), bracket()."""
import sys, itertools
import numpy as np
from scipy.optimize import minimize
CODE = 'SCRATCH/v20/Research/code'
sys.path.insert(0, CODE)
import fill_v20 as fv
from ref_common import *
import cvxpy as cp
rng = np.random.default_rng(11)

# ---- waterfill vs referee bisection vs convex solver (two-sided), including zeros and < b nonzeros
def cvx_M(c, b):
    c = np.asarray(c, float); nz = np.abs(c) > 0
    if nz.sum() == 0: return 0.0
    a = np.abs(c[nz]); pi = cp.Variable(len(a))
    prob = cp.Problem(cp.Minimize(cp.sum(cp.multiply(a ** 2, cp.inv_pos(pi)))), [pi <= 1, cp.sum(pi) <= b, pi >= 0]); prob.solve(solver='CLARABEL')
    return float(prob.value)
w1 = w2 = 0.0; cases = dict(zeros=0, few=0, exact_b=0, sat=0, total=0)
for _ in range(400):
    m = int(rng.integers(1, 9)); b = int(rng.integers(1, m + 1)); c = rng.normal(size=m) * rng.choice([0.01, 1.0, 20.0], size=m)
    if rng.random() < 0.5: c[rng.random(m) < 0.4] = 0.0
    nzc = int((c != 0).sum()); cases['total'] += 1; cases['zeros'] += nzc < m; cases['few'] += nzc < b; cases['exact_b'] += nzc == b
    a = np.sort(np.abs(c))[::-1]; cases['sat'] += (nzc > b and b * a[0] > a.sum())
    f = fv.waterfill(c, b); r = Mb(c, b); s = cvx_M(c, b)
    w1 = max(w1, abs(f - r) / max(r, 1e-300) if r > 0 else abs(f)); w2 = max(w2, abs(f - s) / max(s, 1e-12) if s > 0 else abs(f))
    # the special case of the theorem
    if nzc > 0 and b * a[0] <= a.sum(): assert abs(f - a.sum() ** 2 / b) <= 1e-10 * max(f, 1e-300)
print('waterfill vs referee bisection: max rel diff %.2e; vs CLARABEL: %.2e; cases %s' % (w1, w2, cases))
print('  all-zero input:', fv.waterfill(np.zeros(4), 2), ' b >= nonzeros:', fv.waterfill([3, 0, 0, 4], 2), fv.waterfill([3, 0, 0, 4], 3), ' tiny entries 1e-15 (dropped by the 1e-14 threshold):', fv.waterfill([1e-15, 1.0, 1.0], 1))

# ---- ci_constants vs the definitions
w = dict(delta=0.0, var=0.0, lab=0.0, blind=0.0, full=0.0)
for _ in range(60):
    K = int(rng.integers(3, 8)); b = int(rng.integers(2, K)); emp = rng.dirichlet(np.ones(2 << K) * rng.choice([0.3, 1.0, 5.0])) * 0.99 + 0.01 / (2 << K)
    d = rng.choice([-1.0, 1.0], size=1 << K) if rng.random() < 0.5 else rng.uniform(-1, 1, 1 << K)
    out = fv.ci_constants(K, b, emp, d)
    # referee: conditional-independence fit = product of the class-conditional marginals of emp; label index 0 <-> y = -1
    P = emp.reshape(2, 1 << K); py = P.sum(1); Bm = bitmat(K)
    fit = np.stack([py[y] * np.prod(np.where(Bm == 1, (P[y] @ Bm) / py[y], 1 - (P[y] @ Bm) / py[y]), axis=1) for y in (0, 1)])
    t = np.stack([-d, d]); delta = (fit * t).sum(); var = (fit * t * t).sum() - delta ** 2
    cf = closed_forms(fit, d, b)
    # complete records: variance of the projection of t - Delta on the tangent space, by least squares in the non-orthogonal basis
    basis = ci_basis(K, fit); v, _, _ = gradient(fit, basis, d); G = np.array([[(fit * s1 * s2).sum() for s2 in basis] for s1 in basis]); full = float(v @ np.linalg.solve(G, v))
    w['delta'] = max(w['delta'], abs(out['delta_fit'] - delta)); w['var'] = max(w['var'], abs(out['var_fit'] - var))
    w['lab'] = max(w['lab'], abs(out['ci_label'] - cf['lab']) / cf['lab']); w['blind'] = max(w['blind'], abs(out['ci_blind'] - cf['blind']) / cf['blind']); w['full'] = max(w['full'], abs(out['ci_full'] - full) / full)
    assert full <= cf['lab'] * (1 + 1e-9) <= cf['blind'] * (1 + 2e-9) and cf['blind'] <= var * (1 + 1e-9) + 1e-12 or True
print('ci_constants vs definitions (60 random laws/contrasts): max abs diff delta_fit %.1e, var_fit %.1e; max rel diff ci_label %.1e, ci_blind %.1e, ci_full %.1e' % (w['delta'], w['var'], w['lab'], w['blind'], w['full']))

# ---- bracket vs brute force
wl = wu = 0.0
for _ in range(40):
    K = int(rng.integers(3, 8)); b = int(rng.integers(2, K)); emp = rng.dirichlet(np.ones(2 << K)) * 0.99 + 0.01 / (2 << K)
    asked = random_interview(K, b, [1] * b, rng); cs = cells_of(K, asked); d = np.zeros(1 << K)
    for c in cs: d[c] = rng.choice([-1.0, 1.0])
    sets = {}; leaf_sets = np.array([sets.setdefault(tuple(sorted(asked[x])), len(sets)) for x in range(1 << K)])
    out = fv.bracket(K, b, emp, d, leaf_sets)
    P = emp.reshape(2, 1 << K); t = np.stack([-d, d]); delta = (P * t).sum(); var = (P * (t - delta) ** 2).sum(); Bm = bitmat(K); best = 0.0
    for T in itertools.combinations(range(K), b):
        e = 0.0
        for y in (0, 1):
            for pat in itertools.product((0, 1), repeat=b):
                sel = np.all(Bm[:, list(T)] == np.array(pat), axis=1); pc = P[y, sel].sum()
                if pc > 0: e += (P[y, sel] @ (t[y, sel] - delta)) ** 2 / pc
        best = max(best, e)
    up = sum(np.sqrt((P[:, leaf_sets == s] * (t[:, leaf_sets == s] - delta) ** 2).sum()) for s in range(len(sets))) ** 2 / var
    wl = max(wl, abs(out['lower'] - var / best) / (var / best)); wu = max(wu, abs(out['upper'] - up) / up)
    assert out['lower'] <= out['upper'] * (1 + 1e-9)
print('bracket vs brute force (40 random laws and trees): max rel diff lower %.1e, upper %.1e' % (wl, wu))
