"""v15: which screening trees are computed exactly by a two-round interview with at most b questions?
A two-round interview asks a first batch B1 and then, for each answer pattern a on B1, a second batch of at most
b - |B1| items. It computes the decision d exactly iff for every pattern a the restriction of d to {x_B1 = a}
depends on at most b - |B1| further items. If such a B1 exists, the interview observes t, so W_2 = W_branch
(ratio exactly 1); at a full-support law the converse also holds, because a design with variance Var(t) must return
t on every profile. The check enumerates all first batches inside the items the tree depends on; no design program
is solved. Trees, splits and seeds are those of screening_v14.run (12 items) and scale_v14.run (21 items)."""
import json, sys
from itertools import combinations
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
from screening_v14 import splits
from scale_v14 import load21
from sklearn.tree import DecisionTreeClassifier


def computable(clf, m, b):
    feats = sorted(set(int(f) for f in clf.tree_.feature if f >= 0)); k = len(feats)
    cube = np.arange(1 << k); Xc = np.zeros((1 << k, m), np.int8)
    for i, j in enumerate(feats): Xc[:, j] = (cube >> i) & 1
    d = clf.predict(Xc)
    diff = np.stack([d != d[cube ^ (1 << i)] for i in range(k)])  # diff[i, x]: flipping item i changes d at x
    dep = [i for i in range(k) if diff[i].any()]
    if len(dep) <= b: return dict(items=len(dep), computable=True, first_batch=[feats[i] for i in dep], rounds_needed=1)
    for size in range(1, b):
        for B in combinations(dep, size):
            code = np.zeros(1 << k, np.int64)
            for p, i in enumerate(B): code |= ((cube >> i) & 1) << p
            cnt = np.zeros(1 << size, np.int64)
            for i in dep:
                if i in B: continue
                cnt += (np.bincount(code, weights=diff[i], minlength=1 << size) > 0)
            if cnt.max() <= b - size:
                return dict(items=len(dep), computable=True, first_batch=[feats[i] for i in B], rounds_needed=2)
    return dict(items=len(dep), computable=False, first_batch=None, rounds_needed=None)


if __name__ == '__main__':
    root, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    for name in ['BRFSS', 'Thyroid']:
        X, y, names, sex = bt.load(name, root); m = X.shape[1]
        for b in [3, 4, 5, 6]:
            for shift in [False, True]:
                for s in range(3):
                    seed = 20261108 + s; tr, cal, tgt = splits(name, X, y, names, sex, seed, shift)
                    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50 if name == 'BRFSS' else 10, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
                    r = computable(clf, m, b); r.update(dataset=name, b=b, shift=shift, seed=seed)
                    (out / f'{name}_b{b}_{"shift" if shift else "iid"}_{s}.json').write_text(json.dumps(r)); print(r, flush=True)
    X, y, names = load21(root); m = X.shape[1]
    for b in [3, 4]:
        for s in range(3):
            seed = 20261108 + s; rng = np.random.default_rng(seed)
            perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; src = rng.permutation(src); tr = src[:20000]
            clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
            r = computable(clf, m, b); r.update(dataset='BRFSS21', b=b, shift=False, seed=seed)
            (out / f'BRFSS21_b{b}_iid_{s}.json').write_text(json.dumps(r)); print(r, flush=True)
