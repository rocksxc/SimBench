import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from sklearn.tree import DecisionTreeClassifier
root = '/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/inputs_v12'
name, b, seed, r, mode = sys.argv[1], int(sys.argv[2]), 20261108 + int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
X, y, names, sex = bt.load(name, root); m = X.shape[1]
rng = np.random.default_rng(seed)
perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
src = rng.permutation(src); tr = src[:20000]
clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
dv = 2 * clf.predict(X[tgt]).astype(float) - 1
E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=dv, dhat=dhat)
allforms = [E.form_interview(f) for f in range(E.L)]
fx = E.colgen(1, allforms); sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
print('fixed', fx['value'], 'support', len(sup), flush=True)
start = allforms if mode == 'all' else sup
t0 = time.time()
import capdesign
orig_solve = E.solve
def timed_solve(*a, **k):
    t1 = time.time(); out = orig_solve(*a, **k); print('   solve %.2fs ints %d' % (time.time() - t1, len(a[0])), flush=True); return out
E.solve = timed_solve
res = E.colgen(r, start, verbose=True, smooth=float(sys.argv[6]) if len(sys.argv) > 6 else 0.5)
print('r', r, 'upper', res['upper'], 'lower', res['lower'], 'iters', res['iterations'], 'opt', res['optimal'], 'valid', all(E.check_interview(c) for c in res['interviews']), '%.1fs' % (time.time() - t0), flush=True)
