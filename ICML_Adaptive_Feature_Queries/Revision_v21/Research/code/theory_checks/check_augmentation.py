"""Numerical checks of the extra-questions theorem of v21 (forms of size b + c against depth-b trees).
(1) Address contrast, uniform profiles, independent uniform label: the optimal forms of size b + c have constant
    2^{b-1} / (c + 1) for 0 <= c <= 2^{b-1} - 1 (solver against the closed form).
(2) Random depth-b trees at random full-support laws: the optimal forms of size b + c need at most 2^{b-1-j} times
    Var(t), where j = j(c) is the largest j with 2^{j+1} - j - 2 <= c (the simulation bound), and the bound of the
    explicit path-prefix design is checked constructively: the design 'guess the first b-1-j answers and ask the
    whole subtree below' is built and its acceptance probability is verified to be 2^{-(b-1-j)} for every profile.
(3) Product of two address blocks: forms of size b + c against the product formula prod_j D / (B_j - kappa)."""
import sys
from itertools import product
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capdesign as cd
import model_v17 as mv
from capcurve_v21 import engine

rng = np.random.default_rng(20261114)


def jc(c):
    j = 0
    while 2 ** (j + 2) - (j + 1) - 2 <= c: j += 1
    return j


def address(kappa):
    D = 1 << kappa; m = kappa + D; grid = mv.bits(m)
    a = grid[:, :kappa] @ (1 << np.arange(kappa)); z = grid[np.arange(1 << m), kappa + a]
    return m, 2.0 * z - 1


def wfixed(m, B, cube, d):
    E0 = engine(m, B, cube.ravel(), d); var = E0.second - E0.delta ** 2
    return float((E0.solve([E0.form_interview(f) for f in range(E0.L)])['value'] - E0.delta ** 2) / var)


def check_address():
    out = []
    for kappa in (1, 2):
        m, d = address(kappa); b = kappa + 1; D = 1 << kappa; cube = np.full((2, 1 << m), 0.5 / (1 << m))
        for c in range(0, D):
            if b + c >= m: val = 1.0
            else: val = wfixed(m, b + c, cube, d)
            out.append((b, c, val, D / (c + 1)))
    return out


def random_tree(m, b):
    """Complete depth-b tree with distinct questions on every path: node -> coordinate, nodes indexed by answer prefixes."""
    q = {}
    def rec(prefix, asked):
        if len(prefix) == b: return
        j = int(rng.choice([i for i in range(m) if i not in asked])); q[prefix] = j
        for v in (0, 1): rec(prefix + (v,), asked + [j])
    rec((), [])
    return q


def check_simulation(trials=30):
    worst = 0.0; rows = []
    for _ in range(trials):
        b = int(rng.integers(2, 4)); m = int(rng.integers(b + 2, 8)); q = random_tree(m, b); grid = mv.bits(m)
        leafval = {}; d = np.zeros(1 << m)
        for x in range(1 << m):
            pre = ()
            for _lvl in range(b): pre = pre + (int(grid[x, q[pre]]),)
            d[x] = leafval.setdefault(pre, float(rng.choice([-1.0, 1.0])))
        P = rng.dirichlet(np.ones(2 << m)); P = 0.9 * P + 0.1 / (2 << m); cube = P.reshape(2, 1 << m)
        for c in range(0, min(m - b, 5) + 0):
            j = min(jc(c), b - 1)
            # constructive check: prefix design
            for guess in product((0, 1), repeat=b - 1 - j):
                form = set(); pre = ()
                for g in guess: form.add(q[pre]); pre = pre + (g,)
                stack = [pre]
                while stack:
                    p_ = stack.pop()
                    if len(p_) == b: continue
                    form.add(q[p_]); stack += [p_ + (0,), p_ + (1,)]
                assert len(form) <= b + c, (b, c, j, len(form))
            if b + c >= m: continue
            val = wfixed(m, b + c, cube, d); bound = 2.0 ** (b - 1 - j)
            rows.append((b, m, c, j, val, bound)); worst = max(worst, val / bound)
    return worst, rows


def check_product():
    # two address blocks with kappa = 1: m = 6, b = 4, D = 4; forms of size 4 + c
    k1, d1 = address(1); m = 2 * k1; g = mv.bits(m); d = d1[g[:, :k1] @ (1 << np.arange(k1))] * d1[g[:, k1:] @ (1 << np.arange(k1))]
    cube = np.full((2, 1 << m), 0.5 / (1 << m)); out = []
    for c in (0, 1):
        B = 4 + c; best = max(np.prod([(Bj - 1) / 2.0 if Bj >= 2 else 0.0 for Bj in (B1, B - B1)]) for B1 in range(0, B + 1) if B1 <= 3 and B - B1 <= 3)
        out.append((c, wfixed(m, B, cube, d), 1.0 / best))
    return out


if __name__ == '__main__':
    for b, c, val, closed in check_address(): print('address b %d c %d  solver %.6f  closed form %.6f' % (b, c, val, closed))
    w, rows = check_simulation()
    print('random trees: max of W_fixed(b+c)/Var(t) over the simulation bound: %.4f over %d cases' % (w, len(rows)))
    for r in rows[:8]: print('  b %d m %d c %d j %d  W_fixed/Var %.4f  bound %.1f' % r)
    for c, val, lower in check_product(): print('product of two blocks, c %d: solver %.6f  lower bound from the product energy %.6f' % (c, val, lower))
