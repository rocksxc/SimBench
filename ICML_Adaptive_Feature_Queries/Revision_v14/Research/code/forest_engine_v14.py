"""v14: exact fixed vs all-depth-b-tree branching constants for independent depth-b forest updates, computed with
the Fourier-restricted engine (capdesign.py): restricted master + exact DP pricing over all depth-b trees + Wentges
dual smoothing, certified by the dual witness. Same data protocol as forest_exact_b / forest_exact_v13 (v12/v13):
n0 records train the old forest, n1 the new forest, the remaining records form the held-out evaluation law,
mixed with a uniform mass alpha. Component trees are padded to depth b (a refinement within the cap)."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
sys.path.insert(0, str(Path(__file__).resolve().parent))
from forest_exact_b import data, fwht, allbits  # noqa: E402
import capdesign as cd

SPLITS = {'WDBC': (100, 200), 'Spambase': (500, 1000), 'Ionosphere': (60, 120)}


def tree_interview(E, est, b):
    """Cells of a fitted sklearn tree on 0/1 features, every leaf padded to exactly b coordinates."""
    t = est.tree_; cells_f = []; cells_u = []
    def rec(node, lits):
        if t.children_left[node] == -1:
            feats = [f for f, _ in lits]; pad = [j for j in range(E.m) if j not in feats][:b - len(feats)]
            T = sorted(feats + pad); f = int(E.lat.rank(b, np.array([sum(1 << j for j in T)]))[0])
            fixed = {f_: v for f_, v in lits}
            for extra in range(1 << len(pad)):
                val = dict(fixed); val.update({pj: (extra >> i) & 1 for i, pj in enumerate(pad)})
                cells_f.append(f); cells_u.append(sum(val[j] << i for i, j in enumerate(T)))
            return
        f = int(t.feature[node]); rec(t.children_left[node], lits + [(f, 0)]); rec(t.children_right[node], lits + [(f, 1)])
    rec(0, [])
    return (np.array(cells_f, np.int64), np.array(cells_u, np.int64))


def run_task(name, seed, m, b, root, alpha=0.01, fitted=True):
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
    def law(rows):
        P = np.zeros((2, 1 << m))
        for z in range(2): P[z] = np.bincount(idx[rows][y[rows] == z], minlength=1 << m) / len(rows)
        return P
    row = dict(dataset=name, seed=seed, m=m, b=b, alpha=alpha, n_old=n0, n_new=n1, n_eval=len(test),
               n_profiles_eval=int(np.sum(law(test).sum(0) > 0)), engine='capdesign_v14')
    if m <= b:
        row.update(ratio_exact_lower=1.0, ratio_exact_upper=1.0, seconds=time.time() - t0); return row
    full = fwht(d) / (1 << m)
    lat = cd.Lattice(m, b); dhat = full[lat.allmasks]
    deg = np.array([bin(s).count('1') for s in range(1 << m)])
    assert np.max(np.abs(full[deg > b]), initial=0) < 1e-10
    E = cd.Engine(m, b, cube=law(test), dvals=d, dhat=dhat, alpha=alpha)
    Etr = cd.Engine(m, b, cube=law(train), dvals=d, dhat=dhat, alpha=0.1)
    second, delta = E.second, E.delta; d2 = delta ** 2
    row.update(delta=delta, second=second, full_var=second - d2)
    allforms = [E.form_interview(f) for f in range(E.L)]
    fx = E.colgen(1, allforms); row['fixed_M'] = fx['upper']; row['fixed_M_lower'] = fx['lower']
    row['gamma_fixed'] = E.gamma()[0]
    sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
    comps = [tree_interview(E, est, b) for est in list(old.estimators_) + list(new.estimators_)]
    cm = E.solve(allforms + comps); row['compmenu_M'] = cm['value']
    br = E.colgen(b, sup + comps, k_add=12, gap=1e-4)
    row.update(branch_M_upper=br['upper'], branch_M_lower=br['lower'], iterations=br['iterations'], branch_optimal=br['optimal'],
               interviews=len(br['interviews']))
    if fitted:
        ff = E.colgen(1, allforms, beta=0.05, P=Etr.P); row['fixed_fit_M'] = E.second_moment(ff['sol'])
        warm = [br['interviews'][i] for i in np.flatnonzero(br['sol']['q'] > 1e-7)]
        bf = E.colgen(b, warm + comps, beta=0.05, P=Etr.P, max_iter=30, k_add=12); row['branch_fit_M'] = E.second_moment(bf['sol'])
        row['ratio_fitted'] = (row['fixed_fit_M'] - d2) / (row['branch_fit_M'] - d2)
    row['ratio_exact_lower'] = (row['fixed_M'] - d2) / (row['branch_M_upper'] - d2)
    row['ratio_exact_upper'] = (row['fixed_M'] - d2) / max(row['branch_M_lower'] - d2, 1e-15)
    row['ratio_compmenu'] = (row['fixed_M'] - d2) / (row['compmenu_M'] - d2)
    row['ratio_fixed_vs_fullinfo'] = (row['fixed_M'] - d2) / (second - d2)
    row['bracket_lower_var'] = (second / row['gamma_fixed'] - d2) / (second - d2)
    row['seconds'] = time.time() - t0
    return row


def go(args):
    t, data_root, out, fitted = args
    name, seed, m, b = t
    r = run_task(name, seed, m, b, data_root, fitted=fitted)
    (Path(out) / f'{name}_{seed}_m{m}_b{b}.json').write_text(json.dumps(r, indent=1))
    return r


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--bs', default='4'); p.add_argument('--ms', default='12'); p.add_argument('--seeds', type=int, default=5)
    p.add_argument('--datasets', default='WDBC,Spambase,Ionosphere'); p.add_argument('--workers', type=int, default=3)
    p.add_argument('--nofit', action='store_true'); p.add_argument('--one', default='')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.one:
        ds, s, m, b = a.one.split(','); r = run_task(ds, int(s), int(m), int(b), a.data, fitted=not a.nofit)
        print(json.dumps({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()}, indent=0)); sys.exit()
    from concurrent.futures import ProcessPoolExecutor, as_completed
    tasks = [(ds, 20261108 + s, int(m), int(b)) for b in a.bs.split(',') for m in a.ms.split(',') for ds in a.datasets.split(',') for s in range(a.seeds)]
    tasks = [t for t in tasks if not (out / f'{t[0]}_{t[1]}_m{t[2]}_b{t[3]}.json').exists()]
    print(len(tasks), 'tasks', flush=True)
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, (t, a.data, str(out), not a.nofit)): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result(); print(t, 'exact [%.4f,%.4f] comp %.3f fitted %s it %s' % (r['ratio_exact_lower'], r['ratio_exact_upper'], r.get('ratio_compmenu', 1), ('%.3f' % r['ratio_fitted']) if 'ratio_fitted' in r else '-', r.get('iterations')), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-800:], flush=True)
