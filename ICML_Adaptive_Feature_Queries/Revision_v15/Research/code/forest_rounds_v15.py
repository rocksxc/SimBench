"""v15: exact optimal two-round (and, at b = 4, three-round) designs for the forest updates of forest_engine_v14,
next to the fixed and branching optima, all certified by column generation with exact pricing (gap 1e-4).
Same data protocol, forests, evaluation law and 1% smoothing as forest_engine_v14.run_task."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
sys.path.insert(0, str(Path(__file__).resolve().parent))
from forest_exact_b import data, fwht, allbits  # noqa: E402
import capdesign as cd
from forest_engine_v14 import SPLITS, tree_interview


def run_task(name, seed, m, b, root, alpha=0.01):
    t0 = time.time()
    X, y = data(name, Path(root)); perm = np.random.default_rng(seed).permutation(len(y))
    n0, n1 = SPLITS[name]
    tr0 = perm[:n0]; tr1 = perm[n0:n0 + n1]; train = perm[:n0 + n1]; test = perm[n0 + n1:]
    median = np.median(X[train], axis=0); binary = (X > median).astype(np.int8)
    eligible = np.flatnonzero((binary[train].min(axis=0) == 0) & (binary[train].max(axis=0) == 1))
    chosen = eligible[np.linspace(0, len(eligible) - 1, 12).round().astype(int)][:m]; x = binary[:, chosen]
    pars = dict(n_estimators=20, max_depth=b, max_features='sqrt', min_samples_leaf=max(3, n0 // 30), n_jobs=1)
    old = RandomForestClassifier(random_state=seed + 101, **pars).fit(x[tr0], y[tr0])
    new = RandomForestClassifier(random_state=seed + 307, **pars).fit(x[tr1], y[tr1])
    grid = allbits(m); d = new.predict_proba(grid)[:, 1] - old.predict_proba(grid)[:, 1]; idx = x @ (1 << np.arange(m))
    P = np.zeros((2, 1 << m))
    for z in range(2): P[z] = np.bincount(idx[test][y[test] == z], minlength=1 << m) / len(test)
    full = fwht(d) / (1 << m); lat = cd.Lattice(m, b); dhat = full[lat.allmasks]
    E = cd.Engine(m, b, cube=P, dvals=d, dhat=dhat, alpha=alpha)
    second, delta = E.second, E.delta; d2 = delta ** 2
    row = dict(dataset=name, seed=seed, m=m, b=b, delta=delta, second=second, full_var=second - d2)
    allforms = [E.form_interview(f) for f in range(E.L)]
    fx = E.colgen(1, allforms); row['fixed_M'] = fx['upper']
    sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
    comps = [tree_interview(E, est, b) for est in list(old.estimators_) + list(new.estimators_)]
    prev = sup
    for r in range(2, b):
        res = E.colgen(r, prev, k_add=12, gap=1e-4, max_iter=300)
        row[f'round{r}_M_upper'] = res['upper']; row[f'round{r}_M_lower'] = res['lower']; row[f'round{r}_iterations'] = res['iterations']
        prev = [res['interviews'][i] for i in np.flatnonzero(res['sol']['q'] > 1e-7)]
    br = E.colgen(b, prev + comps, k_add=12, gap=1e-4, max_iter=400)
    row.update(branch_M_upper=br['upper'], branch_M_lower=br['lower'], branch_iterations=br['iterations'])
    wb = br['upper'] - d2
    row['fixed_ratio'] = (row['fixed_M'] - d2) / wb
    for r in range(2, b):
        row[f'round{r}_ratio'] = (row[f'round{r}_M_upper'] - d2) / wb
        row[f'round{r}_recovered'] = 1 - np.log(max(row[f'round{r}_ratio'], 1.0)) / np.log(row['fixed_ratio']) if row['fixed_ratio'] > 1.001 else float('nan')
    row['branch_gap'] = (br['upper'] - br['lower']) / br['upper']
    row['fixed_vs_full'] = (row['fixed_M'] - d2) / (second - d2); row['branch_vs_full'] = wb / (second - d2)
    row['seconds'] = time.time() - t0
    return row


def go(args):
    t, root, out = args
    r = run_task(t[0], t[1], t[2], t[3], root)
    (Path(out) / f'{t[0]}_{t[1]}_m{t[2]}_b{t[3]}.json').write_text(json.dumps(r, indent=1)); return r


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--grid', default='6:3,9:3,12:3,6:4'); p.add_argument('--seeds', type=int, default=5)
    p.add_argument('--datasets', default='WDBC,Spambase,Ionosphere'); p.add_argument('--workers', type=int, default=2)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tasks = [(ds, 20261108 + s, int(g.split(':')[0]), int(g.split(':')[1])) for g in a.grid.split(',') for ds in a.datasets.split(',') for s in range(a.seeds)]
    tasks = [t for t in tasks if not (out / f'{t[0]}_{t[1]}_m{t[2]}_b{t[3]}.json').exists()]
    print(len(tasks), 'tasks', flush=True)
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, (t, a.data, str(out))): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t, 'fixed %.3f' % r['fixed_ratio'], ' '.join('r%d %.3f (rec %.2f)' % (rr, r[f'round{rr}_ratio'], r[f'round{rr}_recovered']) for rr in range(2, t[3])),
                      'cap: fixed/full %.2f branch/full %.2f gap %.1e' % (r['fixed_vs_full'], r['branch_vs_full'], r['branch_gap']), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-800:], flush=True)
