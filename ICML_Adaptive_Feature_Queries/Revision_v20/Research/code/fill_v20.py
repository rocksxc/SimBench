"""v20: quantities that are cheap for every rule, including the runs that rules_v19.py did not finish.
(1) Conditional-independence working model (features independent given the label; Theorem 4(b) of v20): closed-form
    constants at the conditional-independence fit of the target law,
        W(pi) = Var(E[t | Y]) + sum_y P(y) sum_j dhat_{y,j}^2 / pi_j(y),   dhat_{y,j} = E_y[d(X) phi^y_j(X_j)],
    minimised over inclusion vectors pi(y) in [0,1]^K with sum <= b: label-dependent forms (a separate vector per label;
    equal to the branching optimum when the label may be used, and a lower bound on it otherwise) and label-blind forms
    (one vector).
(2) The bracket of Theorem 3(c) over forms on the rule's items: 1/rho_P^2 and the centred N_P of the rule's tree.
(3) For unfinished runs with at most --kmax items: the optimal forms on the rule's items (no bootstrap, no model fit).
Rules: the further rules of rules_v19.py (five targets, caps 4-6, three seeds) and the BRFSS diabetes trees."""
import argparse, json, sys, time
from itertools import combinations
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_v17 as mv
import rules_v19 as rv


def waterfill(c, b):
    """min sum_j c_j^2 / pi_j over 0 <= pi_j <= 1, sum_j pi_j <= b (0/0 = 0)."""
    a = np.sort(np.abs(np.asarray(c, float)))[::-1]; a = a[a > 1e-14]
    if len(a) <= b: return float(np.sum(a ** 2))
    for n1 in range(0, b):
        lam = a[n1:].sum() / (b - n1)
        if a[n1] <= lam * (1 + 1e-12): return float(np.sum(a[:n1] ** 2) + a[n1:].sum() ** 2 / (b - n1))
    raise RuntimeError('waterfill')


def ci_constants(K, b, emp, d):
    grid = mv.bits(K).astype(float); P = emp.reshape(2, 1 << K); py = P.sum(1); out = {}
    dh = np.zeros((2, K)); mean = np.zeros(2); var_fit = 0.0
    for y in (0, 1):
        p1 = (P[y] @ grid) / py[y]; prod = np.prod(np.where(grid > 0.5, p1, 1 - p1), axis=1)  # product law given the label
        phi = (grid - p1) / np.sqrt(p1 * (1 - p1)); mean[y] = prod @ d; dh[y] = (prod * d) @ phi
    sgn = np.array([-1.0, 1.0]); delta = float(np.sum(py * sgn * mean)); vey = float(np.sum(py * (sgn * mean) ** 2) - delta ** 2)
    # t^2 = d^2 = 1 for a deterministic rule; keep general
    second = float(sum(py[y] * (np.prod(np.where(grid > 0.5, (P[y] @ grid) / py[y], 1 - (P[y] @ grid) / py[y]), axis=1) @ (d * d)) for y in (0, 1)))
    lab = vey + sum(py[y] * waterfill(dh[y], b) for y in (0, 1))
    blind = vey + waterfill(np.sqrt(py[0] * dh[0] ** 2 + py[1] * dh[1] ** 2), b)
    full = vey + float(np.sum(py[:, None] * dh ** 2))
    return dict(delta_fit=delta, var_fit=second - delta ** 2, ci_label=lab, ci_blind=blind, ci_full=full, ci_ratio_upper=blind / lab if lab > 0 else 1.0)


def bracket(K, b, emp, d, leaf_sets):
    """1/rho^2 over the b-subsets of the K items and the centred N_P of the rule's tree (leaf_sets: path set id per profile)."""
    t = np.r_[-d, d]; delta = float(emp @ t); var = float(emp @ (t * t) - delta ** 2); grid = mv.bits(K); best = 0.0
    st = emp * (t - delta)
    for T in combinations(range(K), b):
        code = grid[:, list(T)] @ (1 << np.arange(b)); idx = np.r_[code, code + (1 << b)]
        num = np.bincount(idx, weights=st, minlength=2 << b); den = np.bincount(idx, weights=emp, minlength=2 << b)
        e = float(np.sum(np.divide(num ** 2, den, out=np.zeros_like(num), where=den > 0)))
        best = max(best, e)
    w = np.bincount(np.r_[leaf_sets, leaf_sets], weights=emp * (t - delta) ** 2)
    return dict(lower=var / best, upper=float(np.sum(np.sqrt(w)) ** 2 / var), path_sets=int(len(w)))


def leaf_path_sets(clf, used, m, b):
    """Path-set id of every profile of the cube on the used items: the used items on the profile's path, padded by lowest index to min(b, K)."""
    K = len(used); grid = mv.bits(K); Xc = np.zeros((1 << K, m), np.int8); Xc[:, used] = grid
    tr = clf.tree_; node_of = clf.apply(Xc); pos = {f: i for i, f in enumerate(used)}; parent = {}
    for n in range(tr.node_count):
        for c in (tr.children_left[n], tr.children_right[n]):
            if c != -1: parent[c] = n
    def pset(leaf):
        s = []; n = leaf
        while n in parent:
            n = parent[n]; f = int(tr.feature[n])
            if f in pos and pos[f] not in s: s.append(pos[f])
        for j in range(K):
            if len(s) >= min(b, K): break
            if j not in s: s.append(j)
        return tuple(sorted(s))
    ids = {}; out = np.zeros(1 << K, np.int64)
    for leaf in np.unique(node_of):
        out[node_of == leaf] = ids.setdefault(pset(int(leaf)), len(ids))
    return out


def further(name, root, root_forest, b, s):
    from sklearn.tree import DecisionTreeClassifier
    seed = 20261108 + s; X, y, leaf = rv.load(name, root, root_forest); m = X.shape[1]
    rng = np.random.default_rng(seed); perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]; tr = src[:20000]
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=leaf, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    return X, y, tgt, clf, rv.dependent(clf, m), m


def diabetes(root, b, s, shift):
    import budget_trees as bt
    from screening_v14 import splits
    from baselines_v16 import dependent_items
    from sklearn.tree import DecisionTreeClassifier
    seed = 20261108 + s; X, y, names, sex = bt.load('BRFSS', root); m = X.shape[1]
    tr, cal, tgt = splits('BRFSS', X, y, names, sex, seed, shift)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    return X, y, tgt, clf, dependent_items(clf, m), m


def run(task, a):
    t0 = time.time(); kind, name, b, s, shift = task
    X, y, tgt, clf, used, m = further(name, a.data, a.forest, b, s) if kind == 'further' else diabetes(a.data, b, s, shift)
    K = len(used); row = dict(kind=kind, dataset=name, b=b, seed=20261108 + s, shift=shift, items=K)
    if K <= b: row['trivial'] = True; return row
    grid = mv.bits(K); Xc = np.zeros((1 << K, m), np.int8); Xc[:, used] = grid; d = 2.0 * clf.predict(Xc) - 1
    code = X[tgt][:, used].astype(np.int64) @ (1 << np.arange(K)) + (y[tgt].astype(np.int64) << K)
    emp = 0.99 * np.bincount(code, minlength=2 << K) / len(tgt) + 0.01 / (2 << K)
    row.update(ci_constants(K, b, emp, d))
    if K <= a.kbracket: row['bracket'] = bracket(K, b, emp, d, leaf_path_sets(clf, used, m, b))
    done = Path(a.rules) / f"{name.replace(':', '_')}_b{b}_{s}.json"
    prev = json.loads(done.read_text()) if (kind == 'further' and done.exists()) else None
    if kind == 'further': row['rules_v19_status'] = prev['status'] if prev else 'unfinished'
    if kind == 'further' and (prev is None or prev['status'] != 'ok') and K <= a.kmax:
        row['fixed'] = float(rv.ratios(K, b, emp, d, uniform=False)[0])
    elif prev and prev['status'] == 'ok': row['fixed'] = prev['fixed']
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--forest', required=True); p.add_argument('--rules', required=True); p.add_argument('--out', required=True)
    p.add_argument('--kmax', type=int, default=0); p.add_argument('--kbracket', type=int, default=16); p.add_argument('--workers', type=int, default=1); p.add_argument('--only', default='')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tasks = [('further', ds, b, s, False) for ds in ['BRFSS:heart', 'BRFSS:stroke', 'BRFSS:highbp', 'BRFSS:diffwalk', 'Spambase'] for b in (4, 5, 6) for s in range(3)]
    tasks += [('diabetes', 'BRFSS', b, s, sh) for b in (4, 5, 6) for sh in (False, True) for s in range(3)]
    if a.only: tasks = [t for t in tasks if t[0] == a.only]
    fn = lambda t: out / f"{t[0]}_{t[1].replace(':', '_')}_b{t[2]}_{'shift' if t[4] else 'iid'}_{t[3]}.json"
    tasks = [t for t in tasks if not fn(t).exists()]
    def go(t):
        r = run(t, a); fn(t).write_text(json.dumps(r, indent=1, default=float)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t, 'trivial' if r.get('trivial') else 'K %d ci blind/label %.4f  bracket %s fixed %s  %.0fs' % (r['items'], r['ci_ratio_upper'], ('[%.2f, %.2f]' % (r['bracket']['lower'], r['bracket']['upper'])) if 'bracket' in r else '-', ('%.3f' % r['fixed']) if 'fixed' in r else '-', r['seconds']), flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1200:], flush=True)
