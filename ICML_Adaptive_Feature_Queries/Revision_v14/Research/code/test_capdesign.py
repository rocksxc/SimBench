import sys, time, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from sklearn.tree import DecisionTreeClassifier

root = '/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/inputs_v12'
name, b, seed = sys.argv[1], int(sys.argv[2]), 20261108 + int(sys.argv[3])
X, y, names, sex = bt.load(name, root); m = X.shape[1]
rng = np.random.default_rng(seed)
perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
src = rng.permutation(src); n_source = 20000; tr = src[:min(n_source, len(src) // 2)]; cal = src[len(tr):len(tr) + min(n_source, len(src) - len(tr))]
clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50 if name == 'BRFSS' else 10, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
t0 = time.time()
lat = cd.Lattice(m, b)
dhat, leaves = cd.tree_fourier(clf, lat, m)
dv = 2 * clf.predict(X[tgt]).astype(float) - 1
E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=dv, dhat=dhat)
print('setup %.1fs' % (time.time() - t0), 'second', E.second, 'delta', E.delta, flush=True)
g, f = E.gamma(); print('Gamma_P', g, flush=True)
allforms = [E.form_interview(f) for f in range(E.L)]
t0 = time.time(); fx = E.colgen(1, allforms); print('fixed M', fx['value'], 'lower', fx['lower'], 'iters', fx['iterations'], '%.1fs' % (time.time() - t0), flush=True)
for r in range(2, b + 1):
    t0 = time.time(); res = E.colgen(r, allforms, verbose=False)
    bad = sum(not E.check_interview(c) for c in res['interviews'])
    print('r', r, 'M upper', res['upper'], 'lower', res['lower'], 'iters', res['iterations'], 'opt', res['optimal'], 'invalid', bad, '%.1fs' % (time.time() - t0), flush=True)
