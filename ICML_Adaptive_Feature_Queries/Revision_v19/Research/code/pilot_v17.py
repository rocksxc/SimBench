"""v17 (round-6 R2 Q2): a pilot whose cell masses are smoothed by a low-order log-linear fit.
Protocol and accounting as in baselines_v16.py: n1 pilot respondents answer path-set forms drawn uniformly; the pilot
is split into halves, each scored with tables fitted on the other half; the main sample uses the path-set design
learned from the whole pilot (5% floor). The only change is how the pilot's records become cell masses:
  empirical : per form, 0.9 * observed frequencies + 0.1 * uniform (baselines_v16.py);
  loglin2   : the two-way log-linear model for the label and the items of the path-set forms is fitted to the pilot's
              incomplete records by EM, and every form's cell masses are the fitted model's margins (mixed with 1%
              uniform mass).
The fitted law is used only to choose form probabilities and score tables, which satisfy the unbiasedness constraints
exactly for any law, so the scores stay pointwise unbiased. Reported: exact per-record variances at the target law,
relative to branching, of the cross-fitted pilot scores and of the learned design, and the all-in price
[n1 * pilot + (N - n1) * learned] / N with N = 4 * n1."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from screening_v14 import splits, path_sets
from curve_v16 import LogLin
from sklearn.tree import DecisionTreeClassifier

N1 = [1000, 2000]


def em_law(model, cellidx, counts, max_iter=300, tol=1e-7):
    p = np.full(1 << model.K, 1.0 / (1 << model.K))
    for it in range(max_iter):
        w = np.zeros_like(p)
        for ix, c in zip(cellidx, counts):
            marg = np.bincount(ix, weights=p, minlength=len(c)); w += np.divide(c, marg, out=np.zeros(len(c)), where=marg > 0)[ix]
        new = model.mstep(p, p * w); done = np.max(np.abs(new - p)) < tol; p = new
        if done: break
    return p


def run(root, b, s, shift, draws=12, order=2):
    t0 = time.time(); seed = 20261108 + s; name = 'BRFSS'
    X, y, names, sex = bt.load(name, root); m = X.shape[1]
    tr, cal, tgt = splits(name, X, y, names, sex, seed, shift)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
    E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
    d2 = E.delta ** 2; var = E.second - d2; ratio = lambda M: (M - d2) / var
    sets = path_sets(clf, m, b); fids = [int(E.lat.rank(b, np.array([sum(1 << j for j in S)]))[0]) for S in sets]
    psf = [E.form_interview(f) for f in fids]; L = len(fids); C = E.C
    row = dict(dataset=name, shift=shift, b=b, seed=seed, path_sets=L, order=order); row['ps_oracle'] = ratio(E.solve(psf)['value'])
    if row['ps_oracle'] <= 1.01:
        row['seconds'] = time.time() - t0; return row
    items = sorted(set(int(j) for f in fids for j in E.forms[f])); k = len(items); pos = {j: i for i, j in enumerate(items)}
    row['items_in_forms'] = k; model = LogLin(k + 1, order)
    full = np.arange(1 << (k + 1)); lab = full >> k; prof = full & ((1 << k) - 1)
    # per path-set form: local positions of its b coordinates, and the cell index of every (profile, label) state
    loc = [np.array([pos[int(j)] for j in E.forms[f]]) for f in fids]
    cidx = [(((prof[:, None] >> lc[None, :]) & 1) @ (1 << np.arange(b))) + (lab << b) for lc in loc]
    rng = np.random.default_rng(seed + 177); pw = 1 << np.arange(b); Xt = X[tgt].astype(np.int64); yt = y[tgt]
    def counts(rec, assign):
        return [np.bincount((Xt[rec[assign == k_]][:, E.forms[f]] @ pw) + (yt[rec[assign == k_]].astype(np.int64) << b), minlength=2 * C).astype(float) for k_, f in enumerate(fids)]
    def masses(cn, smooth):
        Ph = np.full((2, E.L, C), 1.0 / (2 * C))
        if smooth:
            p = em_law(model, cidx, cn)
            for k_, f in enumerate(fids):
                Ph[:, f, :] = 0.99 * np.bincount(cidx[k_], weights=p, minlength=2 * C).reshape(2, C) + 0.01 / (2 * C)
        else:
            for k_, f in enumerate(fids):
                if cn[k_].sum() > 0: Ph[:, f, :] = 0.9 * cn[k_].reshape(2, C) / cn[k_].sum() + 0.1 / (2 * C)
        return Ph
    out = {}
    for n1 in N1:
        acc = {key: [] for key in ['cf_emp', 'ln_emp', 'cf_ll', 'ln_ll']}
        for _ in range(draws):
            rec = rng.integers(0, len(tgt), n1); assign = rng.integers(0, L, n1); half = rng.permutation(n1) < n1 // 2
            for tag, smooth in (('emp', False), ('ll', True)):
                r_half = [ratio(E.second_moment(E.solve(psf, beta=1.0, P=masses(counts(rec[h], assign[h]), smooth)))) for h in (half, ~half)]
                acc['cf_' + tag].append(float(np.mean(r_half)))
                acc['ln_' + tag].append(ratio(E.second_moment(E.solve(psf, beta=0.05, P=masses(counts(rec, assign), smooth)))))
        o = {}
        for tag in ('emp', 'll'):
            cf = np.array(acc['cf_' + tag]); ln = np.array(acc['ln_' + tag]); allin = 0.25 * cf + 0.75 * ln
            o[tag] = dict(pilot_cf=float(np.median(cf)), learned=float(np.median(ln)), allin=float(np.median(allin)), allin_q90=float(np.quantile(allin, .9)))
        out[str(n1)] = o
    row['pilot'] = out; row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--bs', default='4,5,6'); p.add_argument('--workers', type=int, default=1); p.add_argument('--draws', type=int, default=12); p.add_argument('--order', type=int, default=2)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tasks = [(int(b), s, sh) for b in a.bs.split(',') for sh in (False, True) for s in range(3)]
    tasks = [t for t in tasks if not (out / f'BRFSS_b{t[0]}_{"shift" if t[2] else "iid"}_{t[1]}.json').exists()]
    def go(t):
        r = run(a.data, *t, draws=a.draws, order=a.order); (out / f'BRFSS_b{t[0]}_{"shift" if t[2] else "iid"}_{t[1]}.json').write_text(json.dumps(r, indent=1)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t, 'PSopt %.3f' % r['ps_oracle'], ' '.join('n1=%s emp: cf %.2f learn %.2f all-in %.2f | loglin: cf %.2f learn %.2f all-in %.2f' % (k, v['emp']['pilot_cf'], v['emp']['learned'], v['emp']['allin'], v['ll']['pilot_cf'], v['ll']['learned'], v['ll']['allin']) for k, v in r.get('pilot', {}).items()), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1200:], flush=True)
