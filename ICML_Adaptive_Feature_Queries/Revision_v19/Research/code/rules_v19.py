"""v19 (round-8 R2 Q3/weakness 7, R3 weakness 4): more rules, more targets and resampling intervals.
Screening trees of depth b are trained for further prediction targets, with all other variables as candidate items:
  BRFSS22 : the 21 binarized CDC/BRFSS variables of scale_v14.load21 plus the diabetes indicator; targets heart
            disease, stroke, high blood pressure and difficulty walking (the diabetes target is the main study);
  Spambase: 57 median-binarized features, target spam.
Random-half split, class-balanced CART (minimum leaf 50 for BRFSS, 10 for Spambase), three seeds, caps 4-6.
All designs live on the K items the rule depends on (forms: all b-subsets of these items), which is what a collector
who knows the rule would use and is an upper bound for the optimum over all forms. Per run, at the target law of the
rule's items and the label with 1% uniform mass:
  fixed       : optimal forms, records relative to branching (branching administers the rule and attains Var(t));
  uniform     : uniform over the forms with the best tables for that design;
  boot        : the fixed ratio recomputed on resamples of the target records (20 resamples; 5%, 95% quantiles);
  model2      : W^(2)_fixed / W^(2)_branch at the pairwise fit (model_v17), if K <= 10.
Runs with K <= b are trivial (one form asks everything); runs with K > 13 are skipped and counted."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capdesign as cd
import model_v17 as mv
from scale_v14 import load21
from sklearn.tree import DecisionTreeClassifier

TARGETS = {'heart': 'HeartDis', 'stroke': 'Stroke', 'highbp': 'HighBP', 'diffwalk': 'DiffWalk'}


def load(name, root, root_forest):
    if name.startswith('BRFSS:'):
        X, y, names = load21(root); tcol = TARGETS[name.split(':')[1]]; j = names.index(tcol)
        Xn = np.column_stack([np.delete(X, j, axis=1), y.astype(np.int8)]); return Xn, X[:, j].astype(int), 50
    from forest_exact_b import data
    X, y = data('Spambase', Path(root_forest)); med = np.median(X, axis=0); B = (X > med).astype(np.int8)
    keep = np.flatnonzero((B.min(0) == 0) & (B.max(0) == 1)); return B[:, keep], y.astype(int), 10


def dependent(clf, m):
    feats = sorted(set(int(f) for f in clf.tree_.feature if f >= 0)); k = len(feats)
    cube = np.arange(1 << k); Xc = np.zeros((1 << k, m), np.int8)
    for i, j in enumerate(feats): Xc[:, j] = (cube >> i) & 1
    d = clf.predict(Xc)
    return [feats[i] for i in range(k) if np.any(d != d[cube ^ (1 << i)])]


def ratios(K, b, emp, d, uniform=True):
    cube = emp.reshape(2, 1 << K); lat = cd.Lattice(K, b)
    E0 = cd.Engine(K, b, cube=cube, dvals=d, dhat=(cd.wht(d) / (1 << K))[lat.allmasks], alpha=0.0)
    forms = [E0.form_interview(f) for f in range(E0.L)]; var = E0.second - E0.delta ** 2
    fx = (E0.solve(forms)['value'] - E0.delta ** 2) / var
    un = (E0.solve(forms, beta=1.0)['value'] - E0.delta ** 2) / var if uniform else None
    return fx, un, E0.delta


def run(name, root, root_forest, b, s, boots=20):
    t0 = time.time(); seed = 20261108 + s; X, y, leaf = load(name, root, root_forest); m = X.shape[1]
    rng = np.random.default_rng(seed); perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
    tr = src[:20000]
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=leaf, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    used = dependent(clf, m); K = len(used)
    row = dict(dataset=name, b=b, seed=seed, items=K, n_target=int(len(tgt)), n_train=int(len(tr)), features=m)
    if K <= b or K > 13:
        row['status'] = 'trivial' if K <= b else 'skipped'; row['seconds'] = time.time() - t0; return row
    grid = mv.bits(K); Xc = np.zeros((1 << K, m), np.int8); Xc[:, used] = grid; d = 2.0 * clf.predict(Xc) - 1
    def law(rows):
        code = X[rows][:, used].astype(np.int64) @ (1 << np.arange(K)) + (y[rows].astype(np.int64) << K)
        return 0.99 * np.bincount(code, minlength=2 << K) / len(rows) + 0.01 / (2 << K)
    emp = law(tgt); fx, un, delta = ratios(K, b, emp, d)
    row.update(status='ok', accuracy=(delta + 1) / 2, fixed=fx, uniform=un)
    if K <= 11:
        bs = [ratios(K, b, law(tgt[rng.integers(0, len(tgt), len(tgt))]), d, uniform=False)[0] for _ in range(boots)]
        row['boot'] = dict(n=boots, q05=float(np.quantile(bs, .05)), q95=float(np.quantile(bs, .95)), sd=float(np.std(bs, ddof=1)))
    if K <= 10:
        P2 = mv.loglin_fit(emp, 2).reshape(2, 1 << K); o, *_ = mv.analyse(K, b, P2, d, 2, time_budget=600)
        row['model2'] = o['fixed'] / o['branch']; row['model2_gap'] = 1 - o['branch_lower'] / o['branch']
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--forest', required=True); p.add_argument('--out', required=True)
    p.add_argument('--datasets', default='BRFSS:heart,BRFSS:stroke,BRFSS:highbp,BRFSS:diffwalk,Spambase'); p.add_argument('--bs', default='4,5,6'); p.add_argument('--workers', type=int, default=1)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tasks = [(ds, int(b), s) for ds in a.datasets.split(',') for b in a.bs.split(',') for s in range(3)]
    fn = lambda t: out / f"{t[0].replace(':', '_')}_b{t[1]}_{t[2]}.json"
    tasks = [t for t in tasks if not fn(t).exists()]
    def go(t):
        r = run(t[0], a.data, a.forest, t[1], t[2]); fn(t).write_text(json.dumps(r, indent=1, default=float)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t, r['status'], 'K', r['items'], ('acc %.3f fixed %.3f uniform %.3f boot [%s] model2 %s' % (r['accuracy'], r['fixed'], r['uniform'], ('%.3f, %.3f' % (r['boot']['q05'], r['boot']['q95'])) if 'boot' in r else '-', ('%.3f' % r['model2']) if 'model2' in r else '-')) if r['status'] == 'ok' else '', '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1200:], flush=True)
