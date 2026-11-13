import sys, numpy as np
sys.path.insert(0, 'SCRATCH/v21/Research/code')
import capcurve_v21 as cv, fill_v20 as fv, rules_v19 as rv, model_v17 as mv
from sklearn.tree import DecisionTreeClassifier
rng = np.random.default_rng(5); ok = 0
for trial in range(12):
    m = 14; b = int(rng.integers(3, 6)); N = 6000
    X = (rng.random((N, m)) < 0.5).astype(np.int8); w = rng.normal(size=m)
    y = ((X @ w + 1.5 * X[:, 0] * X[:, 1] - 2 * X[:, 2] * X[:, 3] * X[:, 4] + rng.normal(size=N)) > np.median(X @ w)).astype(int)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=20, random_state=trial).fit(X, y)
    used = rv.dependent(clf, m); K = len(used)
    if K <= b or K > 11: continue
    grid = mv.bits(K); Xc = np.zeros((1 << K, m), np.int8); Xc[:, used] = grid; d = 2.0 * clf.predict(Xc) - 1
    code = X[:, used].astype(np.int64) @ (1 << np.arange(K)) + (y.astype(np.int64) << K)
    emp = 0.99 * np.bincount(code, minlength=2 << K) / N + 0.01 / (2 << K)
    r0, E0 = cv.fixed_ratio(K, b, emp, d); idx = cv.path_set_forms(E0, clf, used, m, b); sets = [tuple(int(v) for v in E0.forms[i]) for i in idx]
    ids = fv.leaf_path_sets(clf, used, m, b)
    assert len(set(ids.tolist())) == len(sets), (len(set(ids.tolist())), len(sets))
    # each profile's realised path (features on the decision path, restricted to used) lies in exactly the set of its id class
    path = clf.decision_path(Xc); feat = clf.tree_.feature; pos = {f: i for i, f in enumerate(used)}
    for x in range(0, 1 << K, 7):
        nodes = path.indices[path.indptr[x]:path.indptr[x + 1]]; p_ = {pos[int(feat[n])] for n in nodes if feat[n] >= 0 and int(feat[n]) in pos}
        cands = [s for s in sets if p_ <= set(s)]; assert cands, 'path not covered'
    # all profiles with the same id have the same covering set of size b, and d is determined by x_S on that class
    for i in set(ids.tolist()):
        sel = np.flatnonzero(ids == i); S = None
        for s in sets:
            cd_ = grid[sel][:, list(s)] @ (1 << np.arange(len(s)))
            if all(len(set(d[sel][cd_ == c])) == 1 for c in np.unique(cd_)): S = s; break
        assert S is not None
    assert all(len(s) == b for s in sets)
    rps = cv.fixed_ratio(K, b, emp, d, forms=idx)[0]
    assert rps >= r0 * (1 - 1e-6) and r0 >= 1 - 1e-9
    r1 = cv.fixed_ratio(K, b + 1, emp, d)[0] if b + 1 < K else 1.0
    assert r1 <= r0 * (1 + 1e-6)
    print('trial %d b %d K %d: path sets %d, optimal forms %.4f, path-set design %.4f, size b+1: %.4f' % (trial, b, K, len(sets), r0, rps, r1)); ok += 1
print('checked', ok, 'synthetic trees')
