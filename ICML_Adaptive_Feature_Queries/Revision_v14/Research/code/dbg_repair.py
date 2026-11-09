import sys, time
sys.path.insert(0, '.')
import numpy as np, budget_trees as bt, capdesign as cd, screening_v14 as sv
from sklearn.tree import DecisionTreeClassifier
root = '/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/inputs_v12'
X, y, names, sex = bt.load('BRFSS', root)
for b, seed in [(4, 20261110), (5, 20261110)]:
    tr, cal, tgt = sv.splits('BRFSS', X, y, names, sex, seed, False)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    lat = cd.Lattice(12, b); dhat, leaves = cd.tree_fourier(clf, lat, 12)
    E = cd.Engine(12, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
    allforms = [E.form_interview(f) for f in range(E.L)]; d2 = E.delta ** 2; var = E.second - d2
    t0 = time.time(); fx = E.colgen(1, allforms); print('b', b, 'fixed %.6f' % ((fx['upper'] - d2) / var), '%.1fs' % (time.time() - t0), flush=True)
    sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
    t0 = time.time(); r2 = E.colgen(2, sup, max_iter=200, gap=1e-4); print('b', b, 'r2 %.6f lower %.6f it %d' % ((r2['upper'] - d2) / var, (r2['lower'] - d2) / var, r2['iterations']), '%.1fs' % (time.time() - t0), flush=True)
