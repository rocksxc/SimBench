"""Numerical checks of Theorem 4(b) of v20 (features independent given the label).
(1) Brute force: for random laws with features independent given the label, random padded decision trees and random
    forms, the information of an interview about directions h = c(y) + sum_j g_j(x_j, y) of the model's tangent space
    equals E[c^2] + sum_y P(y) sum_j pi_j(y) E_y[g_j^2], with pi_j(y) the probability that j is queried given the label.
(2) Engine: at product laws with a balanced label, the pairwise-model constants of fixed forms and of branching
    interviews computed by model_v17.ModelEngine agree with the closed form (E d)^2 + M_b(dhat) for random contrasts.
(3) The closed form of M_b (water-filling) against a numerical minimisation."""
import sys
from itertools import combinations
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model_v17 as mv
from fill_v20 import waterfill

rng = np.random.default_rng(20261113)


def random_tree(m, b, rng):
    """A random depth-b tree with distinct questions on every path: returns for every profile its list of queried coordinates."""
    grid = mv.bits(m); paths = [None] * (1 << m)
    def rec(rows, asked):
        if len(asked) == b:
            for r in rows: paths[r] = tuple(asked)
            return
        j = int(rng.choice([i for i in range(m) if i not in asked]))
        for v in (0, 1): rec([r for r in rows if grid[r, j] == v], asked + [j])
    rec(list(range(1 << m)), [])
    return paths


def info_bruteforce(m, P, paths, H):
    """E[E[h | transcript, Y]^2] for each column h of H (functions on states, label-major), P of shape (2, 2^m)."""
    grid = mv.bits(m); out = np.zeros(H.shape[1]); cells = {}
    for x in range(1 << m):
        key = (paths[x], tuple(grid[x, list(paths[x])])); cells.setdefault(key, []).append(x)
    for y in (0, 1):
        for xs in cells.values():
            pc = P[y, xs].sum(); e = (P[y, xs] @ H[np.array(xs) + (y << m)]) / pc; out += pc * e ** 2
    return out


def check_information(trials=40):
    worst = 0.0
    for _ in range(trials):
        m = int(rng.integers(3, 6)); b = int(rng.integers(2, m)); grid = mv.bits(m).astype(float)
        py = np.array([1 - (pp := rng.uniform(0.2, 0.8)), pp]); p1 = rng.uniform(0.15, 0.85, (2, m))
        P = np.stack([py[y] * np.prod(np.where(grid > 0.5, p1[y], 1 - p1[y]), axis=1) for y in (0, 1)])
        phi = [(grid - p1[y]) / np.sqrt(p1[y] * (1 - p1[y])) for y in (0, 1)]
        ncol = 8; c = rng.normal(size=(ncol, 2)); c -= (c @ py)[:, None]; beta = rng.normal(size=(ncol, 2, m))
        H = np.zeros((2 << m, ncol))
        for y in (0, 1): H[(y << m):((y + 1) << m)] = c[:, y][None, :] + phi[y] @ beta[:, y, :].T
        for kind in ('tree', 'form'):
            paths = random_tree(m, b, rng) if kind == 'tree' else [tuple(sorted(rng.choice(m, b, replace=False)))] * (1 << m)
            J = info_bruteforce(m, P, paths, H)
            asked = np.zeros((1 << m, m)); [asked.__setitem__((x, list(paths[x])), 1.0) for x in range(1 << m)]
            pi = np.stack([(P[y] @ asked) / py[y] for y in (0, 1)])
            formula = (c ** 2) @ py + np.einsum('y,yj,nyj->n', py, pi, beta ** 2)
            worst = max(worst, float(np.max(np.abs(J - formula) / np.maximum(formula, 1e-12))))
    return worst


def check_engine(trials=12):
    worst = 0.0; rows = []
    for _ in range(trials):
        K = int(rng.integers(4, 7)); b = int(rng.integers(2, min(K, 4))); grid = mv.bits(K).astype(float)
        p1 = rng.uniform(0.2, 0.8, K); px = np.prod(np.where(grid > 0.5, p1, 1 - p1), axis=1); cube = np.stack([0.5 * px, 0.5 * px])
        # random contrast of degree <= b: a random depth-b tree with random +-1 leaves
        paths = random_tree(K, b, rng); leaf = {}; d = np.array([leaf.setdefault((paths[x], tuple(grid[x, list(paths[x])])), rng.choice([-1.0, 1.0])) for x in range(1 << K)])
        phi = (grid - p1) / np.sqrt(p1 * (1 - p1)); dh = (px * d) @ phi; closed = float((px @ d) ** 2 + waterfill(dh, b))
        o, E, fx, br = mv.analyse(K, b, cube, d, 2, time_budget=120)
        fixed, branch = o['fixed'] * o['var'], o['branch'] * o['var']
        rows.append((K, b, closed, fixed, branch, o['branch_lower'] * o['var']))
        worst = max(worst, abs(fixed - closed) / closed, abs(branch - closed) / closed)
    return worst, rows


def check_waterfill(trials=200):
    from scipy.optimize import minimize
    worst = 0.0
    for _ in range(trials):
        m = int(rng.integers(2, 8)); b = int(rng.integers(1, m + 1)); c = rng.normal(size=m) * rng.choice([0.05, 1.0, 5.0], size=m)
        f = lambda z: np.sum(c ** 2 / np.clip(z, 1e-9, 1.0))
        res = minimize(f, np.full(m, min(1.0, b / m) * 0.9), bounds=[(1e-9, 1.0)] * m, constraints=[dict(type='ineq', fun=lambda z: b - z.sum())], method='SLSQP', options=dict(maxiter=500, ftol=1e-14))
        worst = max(worst, (waterfill(c, b) - res.fun) / res.fun)  # closed form must not exceed the numerical value
    return worst


if __name__ == '__main__':
    print('information formula, max relative error over random trees and forms: %.2e' % check_information())
    w, rows = check_engine()
    for r in rows: print('K %d b %d  closed %.6f  fixed %.6f  branch %.6f  (branch lower %.6f)' % r)
    print('pairwise model at balanced product laws, max relative gap to the closed form: %.2e' % w)
    print('water-filling closed form minus numerical minimum, max relative: %.2e' % check_waterfill())
