"""v14 (R2 Q3 / R3 Q1): does imputation from complete source records stay valid when the target population differs
from the source in the conditional law of the unasked items? Pre-specified BRFSS shifts (fixed before any result
was seen; all are defined by variables that are not among the twelve model items):
  sex       : female source, male target (as in v12/v13)
  education : source = college graduates (Education == 6), target = no education beyond high school (Education <= 4)
  costbar   : source = no cost barrier to a doctor visit (NoDocbcCost == 0), target = cost barrier (NoDocbcCost == 1)
  physhlth  : source = no poor physical-health days in the past month (PhysHlth == 0), target = 14 or more days
Everything else as screening_mi / screening_mi_v13: the tree is trained on up to 20,000 source records, the fitted
fixed-form design on up to 20,000 further source records (10% smoothing, 5% floor), and n=1000 target respondents
per simulated audit, 400 replications; estimators: branching, fitted fixed form, regression imputation, proper MI."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import screening_mi_v13 as smv
from sklearn.tree import DecisionTreeClassifier

SHIFTS = ['sex', 'education', 'costbar', 'physhlth']


def setup(root, b, seed, shift):
    X, y, names, sex = bt.load('BRFSS', root); m = X.shape[1]; rng = np.random.default_rng(seed)
    df = pd.read_csv(Path(root) / 'cdc_diabetes.csv')
    if shift == 'sex':
        src = np.flatnonzero(sex == 0); tgt = np.flatnonzero(sex == 1)
    elif shift == 'education':
        src = np.flatnonzero(df.Education.to_numpy() == 6); tgt = np.flatnonzero(df.Education.to_numpy() <= 4)
    elif shift == 'costbar':
        src = np.flatnonzero(df.NoDocbcCost.to_numpy() == 0); tgt = np.flatnonzero(df.NoDocbcCost.to_numpy() == 1)
    elif shift == 'physhlth':
        src = np.flatnonzero(df.PhysHlth.to_numpy() == 0); tgt = np.flatnonzero(df.PhysHlth.to_numpy() >= 14)
    else:
        raise ValueError(shift)
    src = rng.permutation(src); n_source = 20000
    tr = src[:min(n_source, len(src) // 2)]; cal = src[len(tr):len(tr) + min(n_source, len(src) - len(tr))]
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    grid = bt.allbits(m); idx = X @ (1 << np.arange(m)); d = 2 * clf.predict(grid).astype(float) - 1
    def law(rows, a):
        P = np.zeros((2, 1 << m))
        for z in range(2): P[z] = np.bincount(idx[rows][y[rows] == z], minlength=1 << m) / len(rows)
        return (1 - a) * P + a / (2 * (1 << m))
    menu = bt.FormMenu(m, b); Pc = law(cal, 0.1)
    _, qf, gf = menu.solve(menu.cellmass(Pc), d, beta=0.05)
    # how different are source and target? total variation of the item profile law and of the label rate
    Ps = law(np.r_[tr, cal], 0.0); Pt = law(tgt, 0.0)
    tv = 0.5 * float(np.abs(Ps.sum(0) - Pt.sum(0)).sum())
    info = dict(n_source=int(len(src)), n_target=int(len(tgt)), tv_profiles=tv, prev_source=float(y[src].mean()), prev_target=float(y[tgt].mean()))
    return dict(X=X, y=y, idx=idx, d=d, m=m, b=b, menu=menu, q=qf, g=gf, src=np.r_[tr, cal], tgt=tgt), info


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--reps', type=int, default=400); p.add_argument('--bs', default='4,5'); p.add_argument('--shifts', default=','.join(SHIFTS))
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for sh in a.shifts.split(','):
        for b in [int(v) for v in a.bs.split(',')]:
            dest = out / f'BRFSS_b{b}_{sh}.json'
            if dest.exists(): continue
            t0 = time.time(); S, info = setup(a.data, b, 20261108, sh); r = smv.simulate(S, reps=a.reps)
            r.update(dataset='BRFSS', b=b, shift=sh, seconds=time.time() - t0, **info); dest.write_text(json.dumps(r, indent=1))
            print(sh, b, 'truth %.4f' % r['truth'], 'tv %.3f' % info['tv_profiles'], ' '.join('%s bias %.4f rmse %.4f cov %.3f' % (k, r[k]['bias'], r[k]['rmse'], r[k]['coverage']) for k in ['branch', 'fixed', 'regimp', 'mi']), '%.0fs' % r['seconds'], flush=True)
