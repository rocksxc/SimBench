import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, '.')
import budget_trees as bt, screening_v14 as sv
import importlib
mod = importlib.import_module(sys.argv[1])
from sklearn.tree import DecisionTreeClassifier
root = '/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/inputs_v12'
X, y, names, sex = bt.load('BRFSS', root); seed = 20261110; b = 4
tr, cal, tgt = sv.splits('BRFSS', X, y, names, sex, seed, False)
clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
lat = mod.Lattice(12, b); dhat, leaves = mod.tree_fourier(clf, lat, 12)
E = mod.Engine(12, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
allforms = [E.form_interview(f) for f in range(E.L)]
d2 = E.delta ** 2; var = E.second - d2
fx = E.colgen(1, allforms); sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
print('fixed ratio', (fx['upper'] - d2) / var, flush=True)
kw = eval(sys.argv[2]) if len(sys.argv) > 2 else {}
t0 = time.time(); res = E.colgen(2, sup, max_iter=int(kw.pop("max_iter", 150)), **kw)
print(sys.argv[1], kw, 'r2 ratio %.4f lower %.4f iters %d opt %s %.0fs' % ((res['upper'] - d2) / var, (res['lower'] - d2) / var, res['iterations'], res['optimal'], time.time() - t0), flush=True)
