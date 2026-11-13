"""v15: centered upper end N_P (Theorem thm:bracket) for the 21-item screening trees of scale_v14 (same splits, trees
and 1% smoothing). Needs only the tree and the target records; no design program is solved."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capdesign as cd
from scale_v14 import load21
from screening_v14 import path_sets
from sklearn.tree import DecisionTreeClassifier

root, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
X, y, names = load21(root); m = X.shape[1]
for b in (3, 4):
    for s in range(3):
        seed = 20261108 + s; rng = np.random.default_rng(seed)
        perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
        src = rng.permutation(src); tr = src[:20000]
        clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
        lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
        dv = 2 * clf.predict(X[tgt]).astype(float) - 1; tt = (2 * y[tgt] - 1) * dv
        delta = 0.99 * float(tt.mean()); var = 1.0 - delta ** 2  # smoothed law: uniform part has mean zero, t^2 = 1
        sets = path_sets(clf, m, b); setid = {lf: k for k, (S, lfs) in enumerate(sets.items()) for lf in lfs}
        w = np.bincount([setid[l] for l in clf.apply(X[tgt])], weights=(tt - delta) ** 2, minlength=len(sets)) / len(tgt)
        depth = {node: len(lits) for node, lits, v in leaves}
        wu = np.array([sum(2.0 ** -depth[lf] * (1 + delta ** 2) for lf in lfs) for S, lfs in sets.items()])
        w = 0.99 * w + 0.01 * wu
        row = dict(b=b, seed=seed, delta=delta, full_var=var, path_sets=len(sets), centered_upper=float(np.sum(np.sqrt(w)) ** 2 / var), weight_sum=float(w.sum() / var))
        (out / f'BRFSS21_b{b}_{s}.json').write_text(json.dumps(row, indent=1)); print(row, flush=True)
