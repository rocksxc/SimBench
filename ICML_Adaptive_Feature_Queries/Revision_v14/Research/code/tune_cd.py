import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt, capdesign as cd
from sklearn.tree import DecisionTreeClassifier
root = '/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/inputs_v12'
b, seed = int(sys.argv[1]), 20261108
X, y, names, sex = bt.load('BRFSS', root); m = X.shape[1]
rng = np.random.default_rng(seed); perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
src = rng.permutation(src); tr = src[:20000]
clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
allforms = [E.form_interview(f) for f in range(E.L)]
fx = E.colgen(1, allforms); sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
print('fixed', fx['upper'], flush=True)
for smooth, k in [(0.8, 12), (0.5, 12)]:
    t0 = time.time(); res = E.colgen(2, sup, smooth=smooth, k_add=k, max_iter=400)
    print('smooth', smooth, 'k', k, 'upper %.6f lower %.6f iters %d ints %d opt %s %.0fs' % (res['upper'], res['lower'], res['iterations'], len(res['interviews']), res['optimal'], time.time() - t0), flush=True)
