"""v14 (R1/R3 scale request): screening trees on all 21 CDC/BRFSS variables (m = 21, 2^21 profiles never enumerated).
Binarization (pre-specified): HighBP, HighChol, CholCheck, BMI>=30, Smoker, Stroke, HeartDiseaseorAttack, PhysActivity,
Fruits, Veggies, HvyAlcoholConsump, AnyHealthcare, NoDocbcCost, GenHlth>=4, MentHlth>=14, PhysHlth>=14, DiffWalk, Sex,
Age>=9 (60+), Education<=4 (no college), Income<=5. Random-half source/target as in the m = 12 study; class-balanced
CART tree of depth b (min leaf 50) on up to 20,000 source records; fitted designs on up to 20,000 further source records
(10% smoothing, 5% floor on generated forms). Target law: all target records + 1% uniform mass over profiles and labels.
Computed: Gamma_P, N_P, optimized path-set design, exact fixed design (column generation over all C(21,b) forms, certified),
its fitted version, and the exact two-round design (certified) for b <= 5. Branching computes d (full information)."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from screening_v14 import path_sets
from sklearn.tree import DecisionTreeClassifier


def load21(root):
    df = pd.read_csv(Path(root) / 'cdc_diabetes.csv')
    cols = {'HighBP': df.HighBP, 'HighChol': df.HighChol, 'CholCheck': df.CholCheck, 'Obese': (df.BMI >= 30), 'Smoker': df.Smoker,
            'Stroke': df.Stroke, 'HeartDis': df.HeartDiseaseorAttack, 'PhysAct': df.PhysActivity, 'Fruits': df.Fruits, 'Veggies': df.Veggies,
            'HvyAlc': df.HvyAlcoholConsump, 'AnyHealthcare': df.AnyHealthcare, 'NoDocCost': df.NoDocbcCost, 'FairPoorHlth': (df.GenHlth >= 4),
            'MentDistress': (df.MentHlth >= 14), 'PhysDistress': (df.PhysHlth >= 14), 'DiffWalk': df.DiffWalk, 'Sex': df.Sex,
            'Age60': (df.Age >= 9), 'NoCollege': (df.Education <= 4), 'LowInc': (df.Income <= 5)}
    X = pd.DataFrame({k: v.astype(int) for k, v in cols.items()})
    return X.to_numpy(np.int8), df.Diabetes_binary.to_numpy(int), list(X.columns)


def run(root, b, s, rounds=True, partial_dest=None):
    t0 = time.time(); seed = 20261108 + s
    X, y, names = load21(root); m = X.shape[1]; rng = np.random.default_rng(seed)
    perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
    src = rng.permutation(src); tr = src[:20000]; cal = src[20000:40000]
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
    t1 = time.time()
    E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
    Es = cd.Engine(m, b, X=X[cal], y=y[cal], alpha=0.1, dvals=2 * clf.predict(X[cal]).astype(float) - 1, dhat=dhat)
    second, delta = E.second, E.delta; d2 = delta ** 2; var = second - d2; ratio = lambda M: (M - d2) / var
    used = sorted({f for node, lits, v in leaves for f, _ in lits})
    row = dict(dataset='BRFSS21', b=b, seed=seed, m=m, forms=E.L, n_target=len(tgt), accuracy=(delta + 1) / 2, delta=delta, full_var=var,
               used_features=len(used), setup_seconds=time.time() - t1, engine='capdesign_v14')
    gam, _ = E.gamma(); row['Gamma_P'] = gam; row['bracket_lower'] = ratio(second / gam)
    sets = path_sets(clf, m, b); row['path_sets'] = len(sets)
    leaf_rec = clf.apply(X[tgt]); setid = {lf: k for k, (S, lfs) in enumerate(sets.items()) for lf in lfs}
    w = np.bincount([setid[l] for l in leaf_rec], minlength=len(sets)) / len(tgt)
    depth = {node: len(lits) for node, lits, v in leaves}
    wu = np.array([sum(2.0 ** -depth[lf] for lf in lfs) for S, lfs in sets.items()])
    w = 0.99 * w + 0.01 * wu; row['N_P'] = float(np.sum(np.sqrt(w)) ** 2); row['bracket_upper_completion'] = ratio(row['N_P'] * second)
    psf = [E.form_interview(int(E.lat.rank(b, np.array([sum(1 << j for j in S)]))[0])) for S in sets]
    ps = E.solve(psf); row['ps_ratio'] = ratio(ps['value'])
    psfit = E.solve(psf, beta=0.05, P=Es.P); row['ps_fit_ratio'] = ratio(E.second_moment(psfit))
    if b <= 4:
        start = [E.form_interview(f) for f in range(E.L)]  # all forms: one solve certifies the optimum
    else:
        top = np.argsort(-E.form_energy_t())[:1500]; start = psf + [E.form_interview(int(f)) for f in top]
    t2 = time.time(); fx = E.colgen(1, start, max_iter=100, k_add=12, gap=1e-4)
    row.update(fixed_ratio=ratio(fx['upper']), fixed_ratio_lower=ratio(fx['lower']), fixed_iterations=fx['iterations'], fixed_optimal=fx['optimal'],
               fixed_forms_used=int(np.sum(fx['sol']['q'] > 1e-7)), fixed_seconds=time.time() - t2)
    ff = E.colgen(1, start, beta=0.05, P=Es.P, max_iter=1); row['fixed_fit_ratio'] = ratio(E.second_moment(ff['sol']))
    row['fixed_consistent'] = bool(row['fixed_ratio'] <= min(row['ps_ratio'], row['fixed_fit_ratio']) + 1e-6)
    if partial_dest is not None:  # save the fixed-design results before the slower two-round stage
        partial_dest.write_text(json.dumps(dict(row, seconds=time.time() - t0), indent=1))
    if rounds and b <= 4 and row['fixed_ratio'] > 1 + 1e-6:
        sup = [fx['interviews'][i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
        t3 = time.time(); r2 = E.colgen(2, sup, max_iter=150, k_add=12, gap=1e-4)
        row.update(round2_ratio=ratio(r2['upper']), round2_ratio_lower=ratio(r2['lower']), round2_iterations=r2['iterations'], round2_optimal=r2['optimal'],
                   round2_seconds=time.time() - t3)
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--bs', default='3,4,5'); p.add_argument('--seeds', type=int, default=3); p.add_argument('--norounds', action='store_true'); p.add_argument('--seedlist', default='')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for b in [int(v) for v in a.bs.split(',')]:
        for s in ([int(v) for v in a.seedlist.split(',')] if a.seedlist else range(a.seeds)):
            dest = out / f'BRFSS21_b{b}_{s}.json'
            if dest.exists(): continue
            r = run(a.data, b, s, rounds=not a.norounds, partial_dest=dest); dest.write_text(json.dumps(r, indent=1))
            print(b, s, ' '.join(f'{k} {v:.4g}' if isinstance(v, float) else f'{k} {v}' for k, v in r.items() if k not in ('dataset', 'engine')), flush=True)
