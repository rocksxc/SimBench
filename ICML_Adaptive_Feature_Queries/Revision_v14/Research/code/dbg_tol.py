import sys, time, warnings
from pathlib import Path
import numpy as np
sys.path.insert(0, '.')
import budget_trees as bt, capdesign as cd, screening_v14 as sv
from sklearn.tree import DecisionTreeClassifier
import cvxpy as cp
root = '/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/inputs_v12'
X, y, names, sex = bt.load('BRFSS', root); seed = 20261110; b = 4
tr, cal, tgt = sv.splits('BRFSS', X, y, names, sex, seed, False)
clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
lat = cd.Lattice(12, b); dhat, leaves = cd.tree_fourier(clf, lat, 12)
E = cd.Engine(12, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
allforms = [E.form_interview(f) for f in range(E.L)]
d2 = E.delta ** 2; var = E.second - d2
for tol in [1e-8, 1e-9, 1e-10]:
    t0 = time.time(); s = E.solve(allforms, tol=tol)
    print('tol', tol, 'status', s['status'], 'M', s['value'], 'ratio', (s['value'] - d2) / var, '%.1fs' % (time.time() - t0), flush=True)
