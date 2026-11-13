"""v13: exact fixed vs all-depth-b-tree branching coefficients with (i) a variable uniform smoothing mass
alpha for the evaluation law, (ii) optional bootstrap resampling of the held-out records, (iii) optional
skipping of the fitted all-tree design. Everything else is identical to forest_exact_b.run_task (v12).
Sensitivity grid (R2 Q1 / R3 Q2 / R1 Q5): alpha in {0.001, 0.01, 0.05, 0.1}; bootstrap replicates 1..5.
"""
import argparse, json, sys, time
from pathlib import Path
from itertools import combinations
import numpy as np
from sklearn.ensemble import RandomForestClassifier
sys.path.insert(0, str(Path(__file__).resolve().parent))
from forest_exact_b import Menu, colgen, data, fwht, allbits  # noqa: E402
import forest_exact_b as _fb
_orig_best_trees = _fb.best_trees
_fb.best_trees = lambda m, b, H, P, k=12: _orig_best_trees(m, b, H, P, k)  # add up to 12 trees per iteration (same certified optimum, fewer master solves)


def run_task(name, seed, m, b, root, alpha=0.01, boot=0, fitted=True, max_iter=200):
    t0 = time.time()
    X, y = data(name, Path(root)); perm = np.random.default_rng(seed).permutation(len(y))
    n0, n1 = {'WDBC': (100, 200), 'Spambase': (500, 1000), 'Ionosphere': (60, 120)}[name]
    tr0 = perm[:n0]; tr1 = perm[n0:n0 + n1]; train = perm[:n0 + n1]; test = perm[n0 + n1:]
    if boot:  # bootstrap resample of the held-out evaluation records (same models, same training data)
        test = np.random.default_rng(seed * 1000 + boot).choice(test, size=len(test), replace=True)
    median = np.median(X[train], axis=0); binary = (X > median).astype(np.int8)
    eligible = np.flatnonzero((binary[train].min(axis=0) == 0) & (binary[train].max(axis=0) == 1))
    chosen = eligible[np.linspace(0, len(eligible) - 1, 12).round().astype(int)][:m]; x = binary[:, chosen]
    pars = dict(n_estimators=20, max_depth=b, max_features='sqrt', min_samples_leaf=max(3, n0 // 30), n_jobs=1)
    old = RandomForestClassifier(random_state=seed + 101, **pars).fit(x[tr0], y[tr0])
    new = RandomForestClassifier(random_state=seed + 307, **pars).fit(x[tr1], y[tr1])
    grid = allbits(m); d = new.predict_proba(grid)[:, 1] - old.predict_proba(grid)[:, 1]; idx = x @ (1 << np.arange(m))
    def law(rows, a):
        P = np.zeros((2, 1 << m))
        for z in range(2): P[z] = np.bincount(idx[rows][y[rows] == z], minlength=1 << m) / len(rows)
        return (1 - a) * P + a / (2 * (1 << m))
    P = law(test, alpha); Ptr = law(train, 0.1)
    tt = np.array([-d, d]); second = float(np.sum(P * tt ** 2)); delta = float(np.sum(P * tt)); d2 = delta ** 2
    scale = max(np.max(np.abs(d)), 1e-12)
    row = dict(dataset=name, seed=seed, m=m, b=b, alpha=alpha, boot=boot, n_eval=len(test), n_cells_occupied=int(np.sum(law(test, 0.0).sum(axis=0) > 0)),
               delta=delta, second=second, full_var=second - d2)
    active = sum(np.max(np.abs(d - d[np.arange(1 << m) ^ (1 << j)])) > 1e-9 for j in range(m)); row['active'] = int(active)
    if m <= b:
        row.update(fixed_M=second, branch_M_upper=second, branch_M_lower=second, ratio_exact_lower=1.0, ratio_exact_upper=1.0, iterations=0, seconds=time.time() - t0)
        return row
    fixed = Menu(m, b); coef = (fwht(d) / (1 << m))[fixed.terms] / scale
    fval, fq, fg, _ = fixed.solve(fixed.cellmass(P), coef); row['fixed_M'] = fval * scale ** 2
    # energy fractions with witness t (Gamma_fixed) on the evaluation law
    best = 0.0
    for a, codes in enumerate(fixed.codes):
        e = 0.0
        for z in range(2):
            num = np.bincount(codes, weights=P[z] * tt[z], minlength=fixed.sizes[a]); den = np.bincount(codes, weights=P[z], minlength=fixed.sizes[a])
            e += float(np.sum(num ** 2 / den))
        best = max(best, e)
    row['gamma_fixed'] = best / second
    fit_val, fq2, fg2, _ = fixed.solve(fixed.cellmass(Ptr), coef, beta=0.05)
    row['fixed_fit_M'] = float(np.sum(fixed.cellmass(P) * fg2 ** 2 / fq2[fixed.group])) * scale ** 2
    comps = list(old.estimators_) + list(new.estimators_)
    br = Menu(m, b, comps); v11 = br.solve(br.cellmass(P), coef)[0] * scale ** 2; row['compmenu_M'] = v11
    hist, bq, bg = colgen(br, P, coef, m, b, max_iter=max_iter)
    row['branch_M_upper'] = min(h[0] for h in hist) * scale ** 2; row['branch_M_lower'] = max(h[1] for h in hist) * scale ** 2
    row['iterations'] = len(hist); row['trees'] = len(br.sizes) - len(list(combinations(range(m), b)))
    if fitted:
        brf = Menu(m, b, comps); hf, qf, gf = colgen(brf, Ptr, coef, m, b, beta=0.05, max_iter=80)
        row['branch_fit_M'] = float(np.sum(brf.cellmass(P) * gf ** 2 / qf[brf.group])) * scale ** 2
        row['ratio_fitted'] = (row['fixed_fit_M'] - d2) / (row['branch_fit_M'] - d2)
    row['ratio_exact_lower'] = (row['fixed_M'] - d2) / (row['branch_M_upper'] - d2)
    row['ratio_exact_upper'] = (row['fixed_M'] - d2) / max(row['branch_M_lower'] - d2, 1e-15)
    row['ratio_compmenu'] = (row['fixed_M'] - d2) / (v11 - d2)
    row['ratio_fixed_vs_fullinfo'] = (row['fixed_M'] - d2) / (second - d2)
    row['bracket_lower_var'] = (second / row['gamma_fixed'] - d2) / (second - d2)
    row['seconds'] = time.time() - t0
    return row


def go(args):
    t, data_root, out, fitted = args
    name, seed, m, b, alpha, boot = t
    r = run_task(name, seed, m, b, data_root, alpha=alpha, boot=boot, fitted=fitted)
    (Path(out) / f'{name}_{seed}_m{m}_b{b}_a{alpha}_boot{boot}.json').write_text(json.dumps(r, indent=1))
    return r


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--bs', default='3'); p.add_argument('--ms', default='12'); p.add_argument('--seeds', type=int, default=5)
    p.add_argument('--alphas', default='0.01'); p.add_argument('--boots', default='0'); p.add_argument('--datasets', default='WDBC,Spambase,Ionosphere')
    p.add_argument('--workers', type=int, default=2); p.add_argument('--nofit', action='store_true'); p.add_argument('--one', default='')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.one:
        ds, s, m, b, al, bo = a.one.split(','); r = run_task(ds, int(s), int(m), int(b), a.data, alpha=float(al), boot=int(bo), fitted=not a.nofit)
        print(json.dumps({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()}, indent=0)); sys.exit()
    from concurrent.futures import ProcessPoolExecutor, as_completed
    tasks = [(ds, 20261108 + s, int(m), int(b), float(al), int(bo)) for b in a.bs.split(',') for m in a.ms.split(',') for ds in a.datasets.split(',')
             for s in range(a.seeds) for al in a.alphas.split(',') for bo in a.boots.split(',')]
    tasks = [t for t in tasks if not (out / f'{t[0]}_{t[1]}_m{t[2]}_b{t[3]}_a{t[4]}_boot{t[5]}.json').exists()]
    print(len(tasks), 'tasks', flush=True)
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, (t, a.data, str(out), not a.nofit)): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result(); print(t, 'exact [%.3f,%.3f] comp %.3f fitted %s' % (r['ratio_exact_lower'], r['ratio_exact_upper'], r.get('ratio_compmenu', 1), ('%.3f' % r['ratio_fitted']) if 'ratio_fitted' in r else '-'), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                print('ERROR', t, repr(e), flush=True)
