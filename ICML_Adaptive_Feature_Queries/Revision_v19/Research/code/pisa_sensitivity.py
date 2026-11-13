"""PISA sensitivity to the two duplicated items whose endorsement differs across forms (p<0.05).
Models and score tables are refitted exactly as in the v11 pipeline (same seeds) and then frozen.
For each item, audit answers on the form with the higher weighted endorsement are flipped 1->0 at
random until the two forms' weighted rates match (or 0->1 on the lower form); the optimized-score
Brier estimate is recomputed. 200 random equalizations per scenario."""
import sys, json
from pathlib import Path
import numpy as np
V11 = Path(__file__).resolve().parents[3] / 'Research' / 'code'
sys.path.insert(0, str(V11))
import pisa_archive as pa
from sklearn.ensemble import RandomForestClassifier

root = Path(sys.argv[1])
raw = pa.load_data(root); valid = raw.ST07Q01.isin(['1', '2', '3']); df = raw[valid].copy().reset_index(drop=True)
form = df.QUESTID.to_numpy(int) - 1; y = df.ST07Q01.isin(['2', '3']).to_numpy(int); x = np.full((len(df), 9), np.nan)
for j, item in enumerate(pa.ITEMS):
    observed = np.array([j in pa.FORMS[f] for f in form]); codes = df[item].to_numpy(int)
    x[observed, j] = np.isin(codes[observed], [1, 2] if j < 6 else [1]).astype(int)
w = df.W_FSTUWT.to_numpy(float); reps = df[[f'W_FSTR{i}' for i in range(1, 81)]].to_numpy(float)
schools = np.array(sorted(raw.SCHOOLID.unique())); rng = np.random.default_rng(20261108); schools = rng.permutation(schools); k = len(schools) // 4
tr0 = df.SCHOOLID.isin(schools[:k]).to_numpy(); tr1 = df.SCHOOLID.isin(schools[k:2 * k]).to_numpy(); audit = ~(tr0 | tr1)
grid = pa.allbits(9); pred = np.empty((2, 3, 512))
for version, train in enumerate([tr0, tr1]):
    for block in range(3):
        columns = list(range(3 * block, 3 * block + 3)); ix = train & np.isfinite(x[:, columns[0]])
        model = RandomForestClassifier(n_estimators=50, max_depth=2 + version, min_samples_leaf=20, max_features=None, random_state=20261108 + 11 * version + 101 * block, n_jobs=1)
        model.fit(x[ix][:, columns], y[ix], sample_weight=w[ix] / w[ix].mean()); pred[version, block] = model.predict_proba(grid[:, columns])[:, 1]
p0 = pred[0].mean(axis=0); p1 = pred[1].mean(axis=0)
T = np.column_stack([(p0 - z) ** 2 - (p1 - z) ** 2 for z in [0, 1]])
score, code, res = pa.score_design(grid, T, x[tr0 | tr1], y[tr0 | tr1], form[tr0 | tr1], w[tr0 | tr1])

def estimate(xx):
    h = np.zeros(len(df))
    for f, cols in enumerate(pa.FORMS):
        ix = form == f; c = xx[ix][:, cols].astype(int) @ (1 << np.arange(6)); h[ix] = score[y[ix], 64 * f + c]
    e, _ = pa.estimate(h[audit], w[audit], reps[audit]); return e

base = estimate(x); print('baseline Brier estimate %.6f se %.6f' % (base['estimate'], base['se']))
out = dict(baseline=base, scenarios=[])
for item, fa, fb in [('ST29Q02', 0, 1), ('ST42Q03', 1, 2)]:
    j = pa.ITEMS.index(item)
    rate = {f: float(w[audit & (form == f)] @ x[audit & (form == f), j] / w[audit & (form == f)].sum()) for f in (fa, fb)}
    hi, lo = (fa, fb) if rate[fa] > rate[fb] else (fb, fa)
    for mode in ['lower the higher form', 'raise the lower form']:
        shifts = []
        for rep in range(200):
            g = np.random.default_rng(1000 + rep); xx = x.copy()
            if mode == 'lower the higher form':
                ix = np.flatnonzero(audit & (form == hi) & (x[:, j] == 1)); prob = 1 - rate[lo] / rate[hi]
                flip = ix[g.random(len(ix)) < prob]; xx[flip, j] = 0
            else:
                ix = np.flatnonzero(audit & (form == lo) & (x[:, j] == 0)); prob = (rate[hi] - rate[lo]) / (1 - rate[lo])
                flip = ix[g.random(len(ix)) < prob]; xx[flip, j] = 1
            shifts.append(estimate(xx)['estimate'] - base['estimate'])
        s = np.array(shifts)
        row = dict(item=item, forms=[fa + 1, fb + 1], rates={str(f + 1): rate[f] for f in rate}, mode=mode, mean_shift=float(s.mean()), max_abs_shift=float(np.abs(s).max()), shift_over_se=float(s.mean() / base['se']))
        out['scenarios'].append(row); print(row)
both = []
for rep in range(200):
    g = np.random.default_rng(5000 + rep); xx = x.copy()
    for item, fa, fb in [('ST29Q02', 0, 1), ('ST42Q03', 1, 2)]:
        j = pa.ITEMS.index(item)
        rate = {f: float(w[audit & (form == f)] @ x[audit & (form == f), j] / w[audit & (form == f)].sum()) for f in (fa, fb)}
        hi, lo = (fa, fb) if rate[fa] > rate[fb] else (fb, fa)
        ix = np.flatnonzero(audit & (form == hi) & (x[:, j] == 1)); flip = ix[g.random(len(ix)) < 1 - rate[lo] / rate[hi]]; xx[flip, j] = 0
    both.append(estimate(xx)['estimate'] - base['estimate'])
b = np.array(both); out['both_items_lowered'] = dict(mean_shift=float(b.mean()), max_abs_shift=float(np.abs(b).max()), shift_over_se=float(b.mean() / base['se']))
print('both', out['both_items_lowered'])
Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
