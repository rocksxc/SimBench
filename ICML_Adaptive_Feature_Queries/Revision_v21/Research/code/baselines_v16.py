"""v16 (round-5 R2/R3): naive pre-committed baselines that a collector auditing one known rule could use, and an
all-in accounting of a design learned from a pilot. Same data, splits, trees and 1% smoothing as screening_v14.run.
  uniform_ps   : uniform over the tree's padded path sets, with the best scores for that design (at the target law);
  uniform_items: uniform over all b-subsets of the items the decision depends on (one form if it depends on <= b items),
                 with the best scores for that design.
Pilot accounting (BRFSS runs with a gain): n1 pilot respondents answer path-set forms drawn uniformly. The pilot is
split into two halves; the records of each half are scored with tables fitted on the other half (uniform design, so the
scores are pointwise unbiased and independent of the records they score). The main sample uses the path-set design
learned from the whole pilot (10% smoothing, 5% floor). We report the exact per-record variances, relative to
branching, of the cross-fitted pilot scores and of the learned design; the all-in price for a total of N records with
weights proportional to sample sizes is [n1 * pilot + (N - n1) * learned] / N."""
import argparse, json, sys, time
from itertools import combinations
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from screening_v14 import splits, path_sets
from sklearn.tree import DecisionTreeClassifier

N1 = [250, 500, 1000, 2000]


def dependent_items(clf, m):
    feats = sorted(set(int(f) for f in clf.tree_.feature if f >= 0)); k = len(feats)
    cube = np.arange(1 << k); Xc = np.zeros((1 << k, m), np.int8)
    for i, j in enumerate(feats): Xc[:, j] = (cube >> i) & 1
    d = clf.predict(Xc)
    return [feats[i] for i in range(k) if np.any(d != d[cube ^ (1 << i)])]


def run(name, root, b, s, shift, draws=30):
    t0 = time.time(); seed = 20261108 + s
    X, y, names, sex = bt.load(name, root); m = X.shape[1]
    tr, cal, tgt = splits(name, X, y, names, sex, seed, shift)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50 if name == 'BRFSS' else 10, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
    E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
    d2 = E.delta ** 2; var = E.second - d2; ratio = lambda M: (M - d2) / var
    sets = path_sets(clf, m, b); fids = [int(E.lat.rank(b, np.array([sum(1 << j for j in S)]))[0]) for S in sets]
    psf = [E.form_interview(f) for f in fids]; L = len(fids); C = E.C
    items = dependent_items(clf, m)
    row = dict(dataset=name, shift=shift, b=b, seed=seed, delta=E.delta, path_sets=L, items=len(items))
    row['ps_oracle'] = ratio(E.solve(psf)['value'])
    row['uniform_ps'] = ratio(E.solve(psf, beta=1.0)['value'])
    if len(items) <= b:
        row['uniform_items'] = 1.0; row['item_forms'] = 1
    else:
        ff = [int(E.lat.rank(b, np.array([sum(1 << j for j in T)]))[0]) for T in combinations(items, b)]
        row['uniform_items'] = ratio(E.solve([E.form_interview(f) for f in ff], beta=1.0)['value']); row['item_forms'] = len(ff)
    if name == 'BRFSS' and row['ps_oracle'] > 1.01:
        rng = np.random.default_rng(seed + 177); pw = 1 << np.arange(b); Xt = X[tgt].astype(np.int64); yt = y[tgt]
        def masses(rec, assign):
            Ph = np.full((2, E.L, C), 1.0 / (2 * C))
            for k_, f in enumerate(fids):
                sel = rec[assign == k_]
                if len(sel) == 0: continue
                codes = Xt[sel][:, E.forms[f]] @ pw
                emp = np.stack([np.bincount(codes[yt[sel] == z], minlength=C) for z in range(2)]) / len(sel)
                Ph[:, f, :] = 0.9 * emp + 0.1 / (2 * C)
            return Ph
        out = {}
        for n1 in N1:
            cf = []; ln = []
            for _ in range(draws):
                rec = rng.integers(0, len(tgt), n1); assign = rng.integers(0, L, n1); half = rng.permutation(n1) < n1 // 2
                r_half = [ratio(E.second_moment(E.solve(psf, beta=1.0, P=masses(rec[h], assign[h])))) for h in (half, ~half)]
                cf.append(float(np.mean(r_half)))  # each half is scored with tables fitted on the other half
                ln.append(ratio(E.second_moment(E.solve(psf, beta=0.05, P=masses(rec, assign)))))
            out[str(n1)] = dict(pilot_cf=float(np.median(cf)), pilot_cf_q90=float(np.quantile(cf, .9)), learned=float(np.median(ln)), learned_q90=float(np.quantile(ln, .9)))
        row['pilot'] = out
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--datasets', default='BRFSS,Thyroid'); p.add_argument('--bs', default='3,4,5,6'); p.add_argument('--workers', type=int, default=1)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tasks = [(ds, int(b), s, sh) for ds in a.datasets.split(',') for b in a.bs.split(',') for sh in (False, True) for s in range(3)]
    tasks = [t for t in tasks if not (out / f'{t[0]}_b{t[1]}_{"shift" if t[3] else "iid"}_{t[2]}.json').exists()]
    def go(t):
        r = run(*t[:1], a.data, *t[1:]); (out / f'{t[0]}_b{t[1]}_{"shift" if t[3] else "iid"}_{t[2]}.json').write_text(json.dumps(r, indent=1)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t, 'items %d forms %d PSopt %.3f unifPS %.3f unifItems %.3f' % (r['items'], r['item_forms'], r['ps_oracle'], r['uniform_ps'], r['uniform_items']),
                      ' '.join('n1=%s cf %.2f learn %.2f' % (k, v['pilot_cf'], v['learned']) for k, v in r.get('pilot', {}).items()), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1200:], flush=True)
