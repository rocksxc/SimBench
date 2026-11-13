"""v15: certified brackets for the optimal two-round design of one BRFSS screening run at b = 6, with a wall-clock
budget for column generation (the exact runs of screening_v14 with --max_round 2 need about an hour each without
competing jobs and were stopped by a time limit). Same data, split, tree, smoothing and engine as screening_v14.run.
Writes the certified lower and upper bounds on W_2/W_branch reached within the budget."""
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from screening_v14 import splits
from sklearn.tree import DecisionTreeClassifier

root, out, target, s, budget = sys.argv[1], Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]), float(sys.argv[5])
out.mkdir(parents=True, exist_ok=True); shift = target == 'shift'; b = 6; name = 'BRFSS'; t0 = time.time(); seed = 20261108 + s
X, y, names, sex = bt.load(name, root); m = X.shape[1]
tr, cal, tgt = splits(name, X, y, names, sex, seed, shift)
clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
d2 = E.delta ** 2; var = E.second - d2; ratio = lambda M: (M - d2) / var
allforms = [E.form_interview(f) for f in range(E.L)]
fx = E.colgen(1, allforms); t1 = time.time()
sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
res = E.colgen(2, sup, max_iter=400, gap=1e-4, k_add=12, time_budget=budget)
row = dict(dataset=name, shift=shift, b=b, seed=seed, fixed_ratio=ratio(fx['upper']), round2_ratio_upper=ratio(res['upper']), round2_ratio_lower=ratio(res['lower']),
           round2_iterations=res['iterations'], round2_optimal=res['optimal'], round2_timed_out=res['timed_out'], interviews=len(res['interviews']),
           valid=bool(all(E.check_interview(c) for c in res['interviews'][-6:])), fixed_seconds=t1 - t0, seconds=time.time() - t0, budget=budget)
(out / f'BRFSS_b6_{target}_{s}.json').write_text(json.dumps(row, indent=1)); print(row, flush=True)
