"""v15 additions to the screening-tree study (same data, splits, trees and smoothing as screening_v14.run):
  * label-dependent fixed designs: form probabilities may depend on the always-observed label. The program
    decouples over labels, M_lab = M_0 + M_1 with M_z = min_{q,g_z} sum_cells P(cell, z) g_z^2 / q; each M_z is
    computed by the engine on the law with both label slices set to P(., z) (value = 2 M_z, certified).
  * label- and sex-stratified fixed designs on the iid BRFSS targets (strata = sex x label).
  * naive pre-committed baselines: the uniform design over all C(m,b) forms with (i) monomial Horvitz-Thompson
    scores and (ii) the optimal scores for that design (closed-form weighted least norm).
  * fitted two-round designs: optimized on the source reference (10% smoothing, 5% floor), evaluated at the target.
  * the centered path-guessing bound N_P (Theorem thm:bracket).
--light computes only the closed-form quantities (uniform designs and N_P) and solves no design program."""
import argparse, json, sys, time
from math import comb
from pathlib import Path
import numpy as np
import scipy.sparse as sp
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from screening_v14 import splits, path_sets
from sklearn.tree import DecisionTreeClassifier


def label_engine(m, b, X, y, dv, dhat, z, alpha, share=1.0):
    """Engine whose two label slices both equal the joint law restricted to label z (times `share`)."""
    E = cd.Engine(m, b, X=X, y=y, alpha=alpha, dvals=dv, dhat=dhat)
    E.P = share * np.stack([E.P[z], E.P[z]]); E.Sd = share * np.stack([E.Sd[z], E.Sd[z]])
    sel = (y == z)
    sec_z = (1 - alpha) * float(np.sum(dv[sel] ** 2)) / len(y) + alpha * float(np.sum(dhat ** 2)) / 2
    E.second = 2 * share * sec_z  # Jensen bound of the duplicated problem
    return E, share * sec_z


def fixed_given_q(E, q, P=None):
    """Optimal pointwise-unbiased scores for a given form distribution q (all forms): per label a weighted
    least-norm problem. Returns the second moment and the tables g (2, L, C)."""
    P = E.P if P is None else P; L, C = E.L, E.C
    rows = E.sub  # L x C term index of (form, local subset)
    F = sp.csc_matrix(((np.tile(E.sign, (L, 1, 1)) / C).ravel(),
                       (np.tile(rows[:, None, :], (1, C, 1)).ravel(), np.repeat(np.arange(L * C), C))), shape=(E.lat.nterms, L * C))
    # column (f, u): entries sign[u, s] / C at row rows[f, s]
    val = 0.0; G = np.zeros((2, L, C))
    for z in range(2):
        D = (np.repeat(q, C) / P[z].ravel())
        A = (F @ sp.diags(D) @ F.T).toarray(); rhs = (2 * z - 1) * E.dhat
        lam = np.linalg.lstsq(A, rhs, rcond=None)[0]
        g = D * (F.T @ lam); assert np.max(np.abs(F @ g - rhs)) < 1e-7
        G[z] = g.reshape(L, C); val += float(np.sum(P[z].ravel() * g ** 2 / np.repeat(q, C)))
    return val, G


def monomial_ht(E):
    """Second moment of the uniform design with monomial Horvitz-Thompson tables g_T = sum_{S in T} that(S) chi_S / N(S)."""
    L, C, m, b = E.L, E.C, E.m, E.b
    size = np.array([bin(s).count('1') for s in range(C)])
    N = np.array([comb(m - k, b - k) for k in size], float)
    gh = E.dhat[E.sub] / N[None, :]  # L x C Fourier coefficients of the form tables
    g = gh @ E.sign.T                # L x C tables at patterns u
    return float(sum(np.sum(E.P[z] * g ** 2) for z in range(2)) * L)


def run(name, root, b, s, shift, two_fit=True, maxit=150, gap=1e-4, light=False):
    t0 = time.time(); seed = 20261108 + s
    X, y, names, sex = bt.load(name, root); m = X.shape[1]
    tr, cal, tgt = splits(name, X, y, names, sex, seed, shift)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50 if name == 'BRFSS' else 10, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
    dv = 2 * clf.predict(X[tgt]).astype(float) - 1
    E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=dv, dhat=dhat)
    second, delta = E.second, E.delta; d2 = delta ** 2; var = second - d2
    ratio = lambda M: (M - d2) / var
    row = dict(dataset=name, shift=shift, b=b, seed=seed, m=m, delta=delta, second=second, full_var=var, prevalence=float(y[tgt].mean()))
    allforms = [E.form_interview(f) for f in range(E.L)]
    if not light:
        fx = E.colgen(1, allforms); row['fixed_ratio'] = ratio(fx['upper'])
    # centered path-guessing bound: w'_S = E[(t - Delta)^2 1{S_tau = S}] under the smoothed law
    sets = path_sets(clf, m, b); setid = {lf: k for k, (S, lfs) in enumerate(sets.items()) for lf in lfs}
    leaf_rec = clf.apply(X[tgt]); tt = (2 * y[tgt] - 1) * dv
    w = np.bincount([setid[l] for l in leaf_rec], weights=(tt - delta) ** 2, minlength=len(sets)) / len(tgt)
    depth = {node: len(lits) for node, lits, v in leaves}; wu = np.zeros(len(sets))
    for k, (S, lfs) in enumerate(sets.items()):
        wu[k] = sum(2.0 ** -depth[lf] * (1 + delta ** 2) for lf in lfs)  # uniform part: E[(t-Delta)^2] = 1 + Delta^2 per unit mass
    w = 0.99 * w + 0.01 * wu
    row['centered_upper'] = float(np.sum(np.sqrt(w)) ** 2 / var); row['path_sets'] = len(sets)
    # naive uniform designs
    qu = np.full(E.L, 1.0 / E.L)
    row['uniform_ht_ratio'] = ratio(monomial_ht(E)); row['uniform_opt_ratio'] = ratio(fixed_given_q(E, qu)[0])
    if light:  # closed-form quantities only: no design program is solved
        row['light'] = True; row['seconds'] = time.time() - t0; return row
    # label-dependent fixed designs
    Ml = 0.0; Mlow = 0.0
    for z in range(2):
        Ez, sec_z = label_engine(m, b, X[tgt], y[tgt], dv, dhat, z, 0.01)
        res = Ez.colgen(1, [Ez.form_interview(f) for f in range(Ez.L)]); Ml += res['upper'] / 2; Mlow += res['lower'] / 2
    row['label_fixed_M'] = Ml; row['label_fixed_ratio'] = ratio(Ml); row['label_fixed_ratio_lower'] = ratio(Mlow)
    # sex x label strata (iid BRFSS targets only: both sexes present)
    if name == 'BRFSS' and not shift:
        Ms = 0.0
        for sx in range(2):
            rows = tgt[sex[tgt] == sx]; share = len(rows) / len(tgt); dvs = 2 * clf.predict(X[rows]).astype(float) - 1
            for z in range(2):
                Ez, _ = label_engine(m, b, X[rows], y[rows], dvs, dhat, z, 0.01, share=share)
                Ms += Ez.colgen(1, [Ez.form_interview(f) for f in range(Ez.L)])['upper'] / 2
        row['strat_fixed_M'] = Ms; row['strat_fixed_ratio'] = ratio(Ms)
    # fitted two-round design (source reference with 10% smoothing and a 5% floor), evaluated at the target
    if two_fit and row['fixed_ratio'] > 1 + 1e-7:
        Es = cd.Engine(m, b, X=X[cal], y=y[cal], alpha=0.1, dvals=2 * clf.predict(X[cal]).astype(float) - 1, dhat=dhat)
        sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
        r2 = E.colgen(2, sup, max_iter=maxit, gap=gap)
        warm = [r2['interviews'][i] for i in np.flatnonzero(r2['sol']['q'] > 1e-7)]
        r2f = E.colgen(2, warm + sup, beta=0.05, P=Es.P, max_iter=40)
        row['round2_ratio'] = ratio(r2['upper']); row['round2_fit_ratio'] = ratio(E.second_moment(r2f['sol']))
        row['round2_fit_interviews'] = len(r2f['interviews'])
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--datasets', default='BRFSS,Thyroid'); p.add_argument('--bs', default='3,4,5'); p.add_argument('--seedlist', default='0,1,2')
    p.add_argument('--targets', default='iid,shift'); p.add_argument('--workers', type=int, default=1); p.add_argument('--notwo', action='store_true'); p.add_argument('--light', action='store_true')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tasks = [(ds, int(b), int(s), t == 'shift') for ds in a.datasets.split(',') for b in a.bs.split(',') for t in a.targets.split(',') for s in a.seedlist.split(',')]
    tasks = [t for t in tasks if not (out / f'{t[0]}_b{t[1]}_{"shift" if t[3] else "iid"}_{t[2]}.json').exists()]
    def go(t):
        r = run(t[0], a.data, t[1], t[2], t[3], two_fit=not a.notwo, light=a.light); (out / f'{t[0]}_b{t[1]}_{"shift" if t[3] else "iid"}_{t[2]}.json').write_text(json.dumps(r, indent=1)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t, ' '.join(f'{k} {r[k]:.3f}' for k in ['fixed_ratio', 'label_fixed_ratio', 'label_fixed_ratio_lower', 'strat_fixed_ratio', 'uniform_ht_ratio', 'uniform_opt_ratio', 'centered_upper', 'round2_ratio', 'round2_fit_ratio'] if k in r), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1500:], flush=True)
