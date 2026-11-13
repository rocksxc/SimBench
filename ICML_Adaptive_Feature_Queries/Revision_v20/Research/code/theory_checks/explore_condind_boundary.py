"""Exploration outside the hypotheses of Theorem 4(b) of v20: the PAIRWISE model (not the conditional-independence model)
at laws where the features are independent given the label. Case A: product law, unbalanced label. Case B: label
associated with every feature (balanced or not). Reports W^(2)_fixed / W^(2)_branch from model_v17.ModelEngine."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model_v17 as mv
from check_condind import random_tree

rng = np.random.default_rng(7)
for case in ('A', 'B'):
    out = []
    for _ in range(10):
        K = int(rng.integers(4, 7)); b = int(rng.integers(2, min(K, 4))); grid = mv.bits(K).astype(float)
        py1 = rng.uniform(0.15, 0.85); p0 = rng.uniform(0.2, 0.8, K); p1 = p0 if case == 'A' else np.clip(p0 + rng.uniform(-0.3, 0.3, K), 0.1, 0.9)
        cube = np.stack([(1 - py1) * np.prod(np.where(grid > 0.5, p0, 1 - p0), axis=1), py1 * np.prod(np.where(grid > 0.5, p1, 1 - p1), axis=1)])
        paths = random_tree(K, b, rng); leaf = {}; d = np.array([leaf.setdefault((paths[x], tuple(grid[x, list(paths[x])])), rng.choice([-1.0, 1.0])) for x in range(1 << K)])
        o, *_ = mv.analyse(K, b, cube, d, 2, time_budget=120)
        out.append(o['fixed'] / o['branch']); print(case, 'K %d b %d P(Y=1) %.2f  fixed/branch %.4f (branch gap %.1e)' % (K, b, py1, out[-1], 1 - o['branch_lower'] / o['branch']), flush=True)
    print('case', case, 'range %.4f - %.4f' % (min(out), max(out)))
