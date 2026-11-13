"""R3 Q3: can the bracket's lower end computed from REFERENCE data alone predict the realized exact ratio?
Forests: reference = smoothed training law (alpha 0.1, as used for fitted designs); realized = exact ratio stored in
forest_exact_tasks (b=3) and forest_capgrid (b=2,4,5). Screening: reference = source calibration law (alpha 0.1);
realized = fixed_oracle_ratio stored in budget_trees runs. Outputs a CSV with reference and target quantities."""
import json, sys, glob, csv
from pathlib import Path
from itertools import combinations
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
sys.path.insert(0, str(Path(__file__).resolve().parent))
from forest_exact_b import Menu, data, fwht, allbits
import budget_trees as bt

def gamma_fixed(m, b, P, tt, second):
    best = 0.0
    for T in combinations(range(m), b):
        codes = allbits(m)[:, T] @ (1 << np.arange(b)); e = 0.0
        for z in range(2):
            num = np.bincount(codes, weights=P[z] * tt[z], minlength=1 << b); den = np.bincount(codes, weights=P[z], minlength=1 << b)
            e += float(np.sum(np.divide(num ** 2, den, out=np.zeros_like(num), where=den > 0)))
        best = max(best, e)
    return best / second

def forest_rows(root, result_dirs):
    rows = []
    for rd in result_dirs:
        for f in sorted(glob.glob(str(rd / '*.json'))):
            r = json.load(open(f))
            if r['m'] <= r.get('b', 3) or 'ratio_exact_lower' not in r: continue
            if r.get('alpha', 0.01) != 0.01 or r.get('boot', 0) != 0: continue
            name, seed, m, b = r['dataset'], r['seed'], r['m'], r.get('b', 3)
            X, y = data(name, Path(root)); perm = np.random.default_rng(seed).permutation(len(y))
            n0, n1 = {'WDBC': (100, 200), 'Spambase': (500, 1000), 'Ionosphere': (60, 120)}[name]
            tr0 = perm[:n0]; tr1 = perm[n0:n0 + n1]; train = perm[:n0 + n1]
            median = np.median(X[train], axis=0); binary = (X > median).astype(np.int8)
            eligible = np.flatnonzero((binary[train].min(axis=0) == 0) & (binary[train].max(axis=0) == 1))
            chosen = eligible[np.linspace(0, len(eligible) - 1, 12).round().astype(int)][:m]; x = binary[:, chosen]
            pars = dict(n_estimators=20, max_depth=b, max_features='sqrt', min_samples_leaf=max(3, n0 // 30), n_jobs=1)
            old = RandomForestClassifier(random_state=seed + 101, **pars).fit(x[tr0], y[tr0])
            new = RandomForestClassifier(random_state=seed + 307, **pars).fit(x[tr1], y[tr1])
            grid = allbits(m); d = new.predict_proba(grid)[:, 1] - old.predict_proba(grid)[:, 1]; idx = x @ (1 << np.arange(m))
            Ptr = np.zeros((2, 1 << m))
            for z in range(2): Ptr[z] = np.bincount(idx[train][y[train] == z], minlength=1 << m) / len(train)
            Ptr = 0.9 * Ptr + 0.1 / (2 * (1 << m))
            tt = np.array([-d, d]); second = float(np.sum(Ptr * tt ** 2)); delta = float(np.sum(Ptr * tt))
            g = gamma_fixed(m, b, Ptr, tt, second)
            ref_lower_var = (second / g - delta ** 2) / (second - delta ** 2)
            rows.append(dict(kind='forest', dataset=name, seed=seed, m=m, b=b, ref_gamma=g, ref_lower_var=ref_lower_var,
                             target_gamma=r.get('gamma_fixed', float('nan')), realized=r['ratio_exact_lower'], fitted=r.get('ratio_fitted', float('nan'))))
            print(rows[-1], flush=True)
    return rows

def screening_rows(root, result_dir):
    rows = []
    for f in sorted(glob.glob(str(result_dir / '*.json'))):
        r = json.load(open(f)); name, b, shift, seed = r['dataset'], r['b'], r['shift'], r['seed']
        X, y, names, sex = bt.load(name, root); m = X.shape[1]; rng = np.random.default_rng(seed)
        if shift and name == 'BRFSS': src = np.flatnonzero(sex == 0); tgt = np.flatnonzero(sex == 1)
        elif shift and name == 'Thyroid':
            fi = names.index('Sex'); src = np.flatnonzero(X[:, fi] == 1); tgt = np.flatnonzero(X[:, fi] == 0)
        else:
            perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
        src = rng.permutation(src); tr = src[:min(20000, len(src) // 2)]; cal = src[len(tr):len(tr) + min(20000, len(src) - len(tr))]
        clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50 if name == 'BRFSS' else 10, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
        grid = allbits(m); idx = X @ (1 << np.arange(m)); d = 2 * clf.predict(grid).astype(float) - 1
        Pc = np.zeros((2, 1 << m))
        for z in range(2): Pc[z] = np.bincount(idx[cal][y[cal] == z], minlength=1 << m) / len(cal)
        Pc = 0.9 * Pc + 0.1 / (2 * (1 << m))
        tt = np.array([-d, d]); second = float(np.sum(Pc * tt ** 2)); delta = float(np.sum(Pc * tt))
        g = gamma_fixed(m, b, Pc, tt, second)
        ref_lower_var = (second / g - delta ** 2) / (second - delta ** 2)
        rows.append(dict(kind='screening', dataset=name, seed=seed, m=m, b=b, shift=shift, ref_gamma=g, ref_lower_var=ref_lower_var,
                         target_gamma=r['Gamma_P'], realized=r['fixed_oracle_ratio'], fitted=r['fixed_fit_ratio']))
        print(rows[-1], flush=True)
    return rows

if __name__ == '__main__':
    v11root, v12root, out = sys.argv[1], sys.argv[2], Path(sys.argv[3]); out.parent.mkdir(parents=True, exist_ok=True)
    R12 = Path('/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/handoff/ICML_Handoff_v12/Revision_v12/Research/results')
    R13 = Path(__file__).resolve().parents[1] / 'results'
    rows = screening_rows(v12root, R12 / 'budget_trees') + forest_rows(v11root, [R12 / 'forest_exact_tasks', R13 / 'forest_capgrid'])
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=sorted({k for r in rows for k in r})); w.writeheader(); [w.writerow(r) for r in rows]
    print('wrote', out, len(rows))
