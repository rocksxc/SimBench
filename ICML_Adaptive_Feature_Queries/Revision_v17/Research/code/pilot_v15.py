"""v15: an empirical check of two-phase self-calibration (Proposition prop:selfcal) on the screening trees.
A pilot of n1 target respondents is interviewed with the uniform design on the tree's padded path sets (each
respondent answers one form of b items; the label is observed). The cell masses of every path-set form are
estimated from the respondents assigned to it, mixed with a uniform mass of 10%, and the path-set design is
re-optimized at the estimated masses with a 5% floor on the form probabilities. Every design is pointwise
unbiased, so learning costs variance only; we report the exact variance of each learned design at the target
law, relative to branching, next to the oracle path-set design, the design fitted on the source reference and
the uniform pilot design itself (scores fixed in advance at the source reference)."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from screening_v14 import splits, path_sets
from sklearn.tree import DecisionTreeClassifier

N1 = [250, 500, 1000, 2000, 4000]


def run(name, root, b, s, shift, draws=40):
    t0 = time.time(); seed = 20261108 + s
    X, y, names, sex = bt.load(name, root); m = X.shape[1]
    tr, cal, tgt = splits(name, X, y, names, sex, seed, shift)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50 if name == 'BRFSS' else 10, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
    E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
    Es = cd.Engine(m, b, X=X[cal], y=y[cal], alpha=0.1, dvals=2 * clf.predict(X[cal]).astype(float) - 1, dhat=dhat)
    d2 = E.delta ** 2; var = E.second - d2; ratio = lambda M: (M - d2) / var
    sets = path_sets(clf, m, b); fids = [int(E.lat.rank(b, np.array([sum(1 << j for j in S)]))[0]) for S in sets]
    psf = [E.form_interview(f) for f in fids]; L = len(fids); C = E.C
    row = dict(dataset=name, shift=shift, b=b, seed=seed, path_sets=L, cells=2 * L * C)
    row['ps_oracle'] = ratio(E.solve(psf)['value'])
    row['ps_reference'] = ratio(E.second_moment(E.solve(psf, beta=0.05, P=Es.P)))
    row['pilot_design'] = ratio(E.second_moment(E.solve(psf, beta=1.0, P=Es.P)))  # uniform q, scores fixed at the reference
    if row['ps_oracle'] <= 1 + 1e-6:
        row['seconds'] = time.time() - t0; return row
    rng = np.random.default_rng(seed + 77); pw = 1 << np.arange(b); Xt = X[tgt].astype(np.int64); yt = y[tgt]
    out = {}
    for n1 in N1:
        vals = []
        for _ in range(draws):
            rec = rng.integers(0, len(tgt), n1); assign = rng.integers(0, L, n1)
            Ph = np.full((2, E.L, C), 1.0 / (2 * C))
            for k, f in enumerate(fids):
                sel = rec[assign == k]
                if len(sel) == 0: continue
                codes = Xt[sel][:, E.forms[f]] @ pw
                emp = np.stack([np.bincount(codes[yt[sel] == z], minlength=C) for z in range(2)]) / len(sel)
                Ph[:, f, :] = 0.9 * emp + 0.1 / (2 * C)
            vals.append(ratio(E.second_moment(E.solve(psf, beta=0.05, P=Ph))))
        v = np.array(vals); out[str(n1)] = dict(median=float(np.median(v)), q10=float(np.quantile(v, .1)), q90=float(np.quantile(v, .9)), mean=float(v.mean()))
    row['learned'] = out; row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--bs', default='4,5'); p.add_argument('--workers', type=int, default=1); p.add_argument('--draws', type=int, default=40)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tasks = [('BRFSS', int(b), s, sh) for b in a.bs.split(',') for sh in (False, True) for s in range(3)]
    tasks = [t for t in tasks if not (out / f'{t[0]}_b{t[1]}_{"shift" if t[3] else "iid"}_{t[2]}.json').exists()]
    def go(t):
        r = run(t[0], a.data, t[1], t[2], t[3], draws=a.draws); (out / f'{t[0]}_b{t[1]}_{"shift" if t[3] else "iid"}_{t[2]}.json').write_text(json.dumps(r, indent=1)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t, 'L %d oracle %.3f ref %.3f pilot %.3f' % (r['path_sets'], r['ps_oracle'], r['ps_reference'], r['pilot_design']),
                      ' '.join('n1=%s: %.3f [%.3f,%.3f]' % (k, v['median'], v['q10'], v['q90']) for k, v in r.get('learned', {}).items()), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1500:], flush=True)
