"""v17 (round-6 R3): forest updates on more features than the exact study (m = 20 median-binarized Spambase features).
Same protocol as forest_rounds_v15.run_task (twenty-tree forests of depth b trained on disjoint records, 1% smoothing,
held-out law), but the feature subset has m = 20 and the adaptive classes are solved with a wall-clock budget: the
optimal fixed design is certified over all C(20, b) forms, and column generation over two-round and branching
interviews is stopped after the budget and reports the certified bracket [lower, upper] reached. Ratios to branching
are therefore reported as intervals: fixed / branch_upper <= W_fixed / W_branch <= fixed / branch_lower."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
sys.path.insert(0, str(Path(__file__).resolve().parent))
from forest_exact_b import data, fwht, allbits  # noqa: E402
import capdesign as cd
from forest_engine_v14 import SPLITS, tree_interview


def run_task(name, seed, m, b, root, budget_branch, budget_two, alpha=0.01):
    t0 = time.time()
    X, y = data(name, Path(root)); perm = np.random.default_rng(seed).permutation(len(y))
    n0, n1 = SPLITS[name]
    tr0 = perm[:n0]; tr1 = perm[n0:n0 + n1]; train = perm[:n0 + n1]; test = perm[n0 + n1:]
    median = np.median(X[train], axis=0); binary = (X > median).astype(np.int8)
    eligible = np.flatnonzero((binary[train].min(axis=0) == 0) & (binary[train].max(axis=0) == 1))
    chosen = eligible[np.linspace(0, len(eligible) - 1, m).round().astype(int)]; x = binary[:, chosen]
    pars = dict(n_estimators=20, max_depth=b, max_features='sqrt', min_samples_leaf=max(3, n0 // 30), n_jobs=1)
    old = RandomForestClassifier(random_state=seed + 101, **pars).fit(x[tr0], y[tr0])
    new = RandomForestClassifier(random_state=seed + 307, **pars).fit(x[tr1], y[tr1])
    grid = allbits(m); d = new.predict_proba(grid)[:, 1] - old.predict_proba(grid)[:, 1]
    lat = cd.Lattice(m, b); dhat = (fwht(d) / (1 << m))[lat.allmasks]; idx = x @ (1 << np.arange(m))
    E = cd.Engine(m, b, X=x[test], y=y[test], alpha=alpha, dvals=d[idx[test]], dhat=dhat)
    second, delta = E.second, E.delta; d2 = delta ** 2
    used = sorted(set(int(f) for est in list(old.estimators_) + list(new.estimators_) for f in est.tree_.feature if f >= 0))
    row = dict(dataset=name, seed=seed, m=m, b=b, forms=int(E.L), n_test=int(len(test)), features_used=len(used), delta=delta, full_var=second - d2)
    allforms = [E.form_interview(f) for f in range(E.L)]
    fx = E.colgen(1, allforms); row['fixed_M'] = fx['upper']; row['fixed_seconds'] = time.time() - t0
    print(name, seed, m, b, 'fixed/full %.3f' % ((fx['upper'] - d2) / (second - d2)), '%.0fs' % row['fixed_seconds'], flush=True)
    sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
    comps = [tree_interview(E, est, b) for est in list(old.estimators_) + list(new.estimators_)]
    if budget_two > 0:
        r2 = E.colgen(2, sup, k_add=12, gap=1e-4, max_iter=2000, time_budget=budget_two)
        row.update(round2_M_upper=r2['upper'], round2_M_lower=r2['lower'], round2_iterations=r2['iterations'], round2_timed_out=bool(r2['timed_out']))
        start = [r2['interviews'][i] for i in np.flatnonzero(r2['sol']['q'] > 1e-7)]
        print('  two rounds [%.4f, %.4f] / full' % ((r2['lower'] - d2) / (second - d2), (r2['upper'] - d2) / (second - d2)), r2['iterations'], 'iterations', '%.0fs' % (time.time() - t0), flush=True)
    else:
        start = sup
    br = E.colgen(b, start + comps, k_add=12, gap=1e-4, max_iter=4000, time_budget=budget_branch)
    row.update(branch_M_upper=br['upper'], branch_M_lower=br['lower'], branch_iterations=br['iterations'], branch_timed_out=bool(br['timed_out']))
    wu = br['upper'] - d2; wl = br['lower'] - d2; wf = row['fixed_M'] - d2
    row['fixed_ratio_lower'] = wf / wu; row['fixed_ratio_upper'] = wf / wl
    if budget_two > 0:
        row['round2_ratio_lower'] = max((row['round2_M_lower'] - d2) / wu, 1.0); row['round2_ratio_upper'] = (row['round2_M_upper'] - d2) / wl
    row['fixed_vs_full'] = wf / (second - d2); row['branch_vs_full_lower'] = wl / (second - d2); row['branch_vs_full_upper'] = wu / (second - d2)
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--dataset', default='Spambase'); p.add_argument('--seed', type=int, default=0); p.add_argument('--m', type=int, default=20); p.add_argument('--b', type=int, default=3)
    p.add_argument('--budget_branch', type=float, default=1200); p.add_argument('--budget_two', type=float, default=900)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    dest = out / f'{a.dataset}_{20261108 + a.seed}_m{a.m}_b{a.b}.json'
    if not dest.exists():
        r = run_task(a.dataset, 20261108 + a.seed, a.m, a.b, a.data, a.budget_branch, a.budget_two); dest.write_text(json.dumps(r, indent=1, default=float))
        print(a.dataset, a.seed, a.m, a.b, 'fixed/branch in [%.3f, %.3f]' % (r['fixed_ratio_lower'], r['fixed_ratio_upper']),
              ('two/branch in [%.3f, %.3f]' % (r['round2_ratio_lower'], r['round2_ratio_upper'])) if 'round2_ratio_upper' in r else '', 'branch iterations', r['branch_iterations'], '%.0fs' % r['seconds'], flush=True)
