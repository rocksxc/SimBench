import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import forest_engine_v14 as fe, capdesign as cd
from forest_exact_b import data, fwht, allbits
from sklearn.ensemble import RandomForestClassifier
name, seed, m, b = 'WDBC', 20261108, 9, 4
X, y = data(name, Path('/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/inputs_v11')); perm = np.random.default_rng(seed).permutation(len(y))
n0, n1 = 100, 200; tr0 = perm[:n0]; tr1 = perm[n0:n0 + n1]; train = perm[:n0 + n1]; test = perm[n0 + n1:]
median = np.median(X[train], axis=0); binary = (X > median).astype(np.int8)
eligible = np.flatnonzero((binary[train].min(axis=0) == 0) & (binary[train].max(axis=0) == 1))
chosen = eligible[np.linspace(0, len(eligible) - 1, 12).round().astype(int)][:m]; x = binary[:, chosen]
pars = dict(n_estimators=20, max_depth=b, max_features='sqrt', min_samples_leaf=max(3, n0 // 30), n_jobs=1)
old = RandomForestClassifier(random_state=seed + 101, **pars).fit(x[tr0], y[tr0]); new = RandomForestClassifier(random_state=seed + 307, **pars).fit(x[tr1], y[tr1])
grid = allbits(m); d = new.predict_proba(grid)[:, 1] - old.predict_proba(grid)[:, 1]; idx = x @ (1 << np.arange(m))
P = np.zeros((2, 1 << m))
for z in range(2): P[z] = np.bincount(idx[test][y[test] == z], minlength=1 << m) / len(test)
lat = cd.Lattice(m, b); dhat = (fwht(d) / (1 << m))[lat.allmasks]
E = cd.Engine(m, b, cube=P, dvals=d, dhat=dhat, alpha=0.01)
allforms = [E.form_interview(f) for f in range(E.L)]
fx = E.colgen(1, allforms); sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
comps = [fe.tree_interview(E, est, b) for est in list(old.estimators_) + list(new.estimators_)]
print('fixed', fx['upper'], 'support', len(sup), flush=True)
k = int(sys.argv[1]); sm = float(sys.argv[2])
orig = E.solve; ts = []
def ts_solve(*a, **kw):
    t = time.time(); o = orig(*a, **kw); ts.append(time.time() - t); return o
E.solve = ts_solve
t0 = time.time(); res = E.colgen(b, sup + comps, k_add=k, smooth=sm, verbose=True)
print('k', k, 'smooth', sm, 'iters', res['iterations'], 'ints', len(res['interviews']), 'upper %.7g lower %.7g' % (res['upper'], res['lower']), 'total %.1fs solve %.1fs' % (time.time() - t0, sum(ts)), flush=True)
