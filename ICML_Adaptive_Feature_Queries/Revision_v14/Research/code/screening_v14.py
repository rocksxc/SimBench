"""v14 screening-tree study on the Fourier-restricted engine (capdesign.py). Same data, splits and trees as
budget_trees.run (v12). Per run: exact fixed design (all forms) and its fitted version; the optimized
path-set design M_PS (Proposition prop:upper) and its fitted version; exact optimal r-round designs for
r = 2..b-1 (certified); the bracket ends 1/Gamma_P and N_P; and an exact position-effect calculation:
the answer at query position j (0-based) flips with probability eps*j/(b-1); branching routes on recorded
answers, fixed forms ask their coordinates in increasing index order."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from sklearn.tree import DecisionTreeClassifier

R12 = Path('/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/handoff/ICML_Handoff_v12/Revision_v12/Research/results/budget_trees')
EPS = [0.01, 0.03, 0.05, 0.1]


def splits(name, X, y, names, sex, seed, shift):
    rng = np.random.default_rng(seed)
    if shift and name == 'BRFSS':
        src = np.flatnonzero(sex == 0); tgt = np.flatnonzero(sex == 1)
    elif shift and name == 'Thyroid':
        f = names.index('Sex'); src = np.flatnonzero(X[:, f] == 1); tgt = np.flatnonzero(X[:, f] == 0)
    else:
        perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
    src = rng.permutation(src); n_source = 20000
    tr = src[:min(n_source, len(src) // 2)]; cal = src[len(tr):len(tr) + min(n_source, len(src) - len(tr))]
    return tr, cal, tgt


def path_sets(clf, m, b):
    t = clf.tree_; sets = {}
    def rec(node, feats):
        if t.children_left[node] == -1:
            sets.setdefault(bt.padded_set(feats, b, m), []).append(node); return
        f = int(t.feature[node]); rec(t.children_left[node], feats + [f]); rec(t.children_right[node], feats + [f])
    rec(0, [])
    return sets


def flip_kernel(b, eps):
    pr = np.array([eps * j / (b - 1) if b > 1 else 0.0 for j in range(b)])
    K = np.ones((1 << b, 1 << b))
    for u in range(1 << b):
        for v in range(1 << b):
            for j in range(b):
                K[u, v] *= pr[j] if ((u ^ v) >> j) & 1 else 1 - pr[j]
    return K  # K[u, v] = P(record v | latent u)


def branch_noisy_mean(clf, cubeP, m, b, eps):
    """Exact E[(2z-1) d(leaf reached on recorded answers)] under the smoothed target cube law."""
    t = clf.tree_; grid = bt.allbits(m)
    pr = [eps * j / (b - 1) if b > 1 else 0.0 for j in range(b)]
    acc = np.zeros(1 << m)
    def rec(node, depth, p):
        if t.children_left[node] == -1:
            acc[:] += p * (2.0 * float(np.argmax(t.value[node][0])) - 1.0); return
        f = int(t.feature[node]); e = pr[depth]; xf = grid[:, f]
        pl = np.where(xf == 0, 1 - e, e); rec(t.children_left[node], depth + 1, p * pl); rec(t.children_right[node], depth + 1, p * (1 - pl))
    rec(0, 0, np.ones(1 << m))
    return float(np.sum(cubeP[1] * acc) - np.sum(cubeP[0] * acc))


def fixed_noisy(E, sol, K):
    """Mean and second moment of a fixed-form design (cells ordered by pattern within each form) under kernel K."""
    fidx, u, g, q, grp = sol['fidx'], sol['u'], sol['g'], sol['q'], sol['group']
    mean = 0.0; sec = 0.0
    for i in np.unique(grp):
        sel = grp == i; f = fidx[sel][0]; uu = u[sel]; order = np.argsort(uu)
        for z in range(2):
            gz = np.zeros(E.C); gz[uu[order]] = g[z, sel][order]
            Pm = E.P[z, f]
            mean += float(Pm @ (K @ gz)); sec += float(Pm @ (K @ gz ** 2)) / q[i]
    return mean, sec


def run(name, root, b, s, shift, rounds=True, max_round=None, maxit=400, gap=1e-7):
    t0 = time.time(); seed = 20261108 + s
    X, y, names, sex = bt.load(name, root); m = X.shape[1]
    tr, cal, tgt = splits(name, X, y, names, sex, seed, shift)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50 if name == 'BRFSS' else 10, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    lat = cd.Lattice(m, b); dhat, leaves = cd.tree_fourier(clf, lat, m)
    E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
    Es = cd.Engine(m, b, X=X[cal], y=y[cal], alpha=0.1, dvals=2 * clf.predict(X[cal]).astype(float) - 1, dhat=dhat)
    second, delta = E.second, E.delta; d2 = delta ** 2; var = second - d2
    ratio = lambda M: (M - d2) / var
    row = dict(dataset=name, shift=shift, b=b, seed=seed, m=m, n_target=len(tgt), n_train=len(tr), n_cal=len(cal),
               accuracy=(delta + 1) / 2, delta=delta, second=second, full_var=var, engine='capdesign_v14')
    gam, _ = E.gamma(); row['Gamma_P'] = gam; row['bracket_lower'] = ratio(second / gam)
    sets = path_sets(clf, m, b); row['path_sets'] = len(sets)
    # N_P: path-set weights under the smoothed target law (t^2 = 1)
    leaf_rec = clf.apply(X[tgt]); setid = {lf: k for k, (S, lfs) in enumerate(sets.items()) for lf in lfs}
    w = np.bincount([setid[l] for l in leaf_rec], minlength=len(sets)) / len(tgt)
    depth = {node: len(lits) for node, lits, v in leaves}
    wu = np.zeros(len(sets))
    for k, (S, lfs) in enumerate(sets.items()):
        wu[k] = sum(2.0 ** -depth[lf] for lf in lfs)
    w = 0.99 * w + 0.01 * wu; row['N_P'] = float(np.sum(np.sqrt(w)) ** 2); row['bracket_upper_completion'] = ratio(row['N_P'] * second)
    allforms = [E.form_interview(f) for f in range(E.L)]
    fx = E.colgen(1, allforms); row['fixed_M'] = fx['upper']; row['fixed_ratio'] = ratio(fx['upper'])
    ff = E.colgen(1, allforms, beta=0.05, P=Es.P); row['fixed_fit_M'] = E.second_moment(ff['sol']); row['fixed_fit_ratio'] = ratio(row['fixed_fit_M'])
    psf = [E.form_interview(int(E.lat.rank(b, np.array([sum(1 << j for j in S)]))[0])) for S in sets]
    ps = E.solve(psf); row['ps_M'] = ps['value']; row['ps_ratio'] = ratio(ps['value'])
    psfit = E.solve(psf, beta=0.05, P=Es.P); row['ps_fit_M'] = E.second_moment(psfit); row['ps_fit_ratio'] = ratio(row['ps_fit_M'])
    row['fixed_consistent'] = bool(row['fixed_M'] <= min(row['ps_M'], row['fixed_fit_M']) * (1 + 1e-6))
    if not row['fixed_consistent']: print('WARNING inconsistent fixed optimum', name, b, s, shift, flush=True)
    sup = [allforms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
    if rounds and row['fixed_ratio'] > 1 + 1e-7:
        prev = sup
        for r in range(2, (b if max_round is None else min(b, max_round)) + 1):
            res = E.colgen(r, prev, max_iter=maxit, gap=gap)
            row[f'round{r}_M_upper'] = res['upper']; row[f'round{r}_M_lower'] = res['lower']; row[f'round{r}_ratio'] = ratio(res['upper'])
            row[f'round{r}_iterations'] = res['iterations']; row[f'round{r}_optimal'] = res['optimal']
            row[f'round{r}_gap'] = (res['upper'] - res['lower']) / res['upper']
            row[f'round{r}_valid'] = bool(all(E.check_interview(c) for c in res['interviews'][-6:]))
            prev = [res['interviews'][i] for i in np.flatnonzero(res['sol']['q'] > 1e-7)]
            if row[f'round{r}_ratio'] <= 1 + 1e-6:
                for rr in range(r + 1, b + 1):
                    row[f'round{rr}_ratio'] = 1.0
                break
    elif row['fixed_ratio'] <= 1 + 1e-7:  # the fixed design already attains full information
        for r in range(2, b + 1): row[f'round{r}_ratio'] = 1.0
    # stored v12 heuristic (follow the tree r-1 levels, then best fixed form inside the node)
    f12 = R12 / f'{name}_b{b}_{"shift" if shift else "iid"}_{s}.json'
    if f12.exists():
        old = json.loads(f12.read_text())
        for r in range(2, b): row[f'heur{r}_ratio'] = old.get(f'round{r}_oracle_ratio')
        row['v12_fixed_ratio'] = old['fixed_oracle_ratio']; row['v12_fit_ratio'] = old['fixed_fit_ratio']
    # position effects
    grid = bt.allbits(m); idx = X @ (1 << np.arange(m))
    cubeP = np.zeros((2, 1 << m))
    for z in range(2): cubeP[z] = np.bincount(idx[tgt][y[tgt] == z], minlength=1 << m) / len(tgt)
    cubeP = 0.99 * cubeP + 0.01 / (2 * (1 << m))
    se = np.sqrt(var / 1000.0); pe = {}
    for eps in EPS:
        K = flip_kernel(b, eps)
        mb = branch_noisy_mean(clf, cubeP, m, b, eps); vb = 1.0 - mb ** 2
        mf, sf = fixed_noisy(E, ff['sol'], K); vf = sf - mf ** 2
        mo, so = fixed_noisy(E, fx['sol'], K); vo = so - mo ** 2
        pe[str(eps)] = dict(bias_branch=mb - delta, bias_fit=mf - delta, bias_oracle=mo - delta,
                            bias_branch_se=abs(mb - delta) / se, bias_fit_se=abs(mf - delta) / se, bias_oracle_se=abs(mo - delta) / se,
                            rmse_branch=float(np.sqrt((mb - delta) ** 2 + vb / 1000)), rmse_fit=float(np.sqrt((mf - delta) ** 2 + vf / 1000)),
                            rmse_oracle=float(np.sqrt((mo - delta) ** 2 + vo / 1000)))
    row['position'] = pe
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--datasets', default='BRFSS,Thyroid'); p.add_argument('--bs', default='3,4,5,6'); p.add_argument('--seeds', type=int, default=3)
    p.add_argument('--workers', type=int, default=1); p.add_argument('--max_round', type=int, default=0); p.add_argument('--maxit', type=int, default=400)
    p.add_argument('--gap', type=float, default=1e-7); p.add_argument('--seedlist', default=''); p.add_argument('--targets', default='iid,shift')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    seeds = [int(v) for v in a.seedlist.split(',')] if a.seedlist else list(range(a.seeds))
    shifts = [t == 'shift' for t in a.targets.split(',')]
    tasks = [(ds, b, s, sh) for ds in a.datasets.split(',') for b in [int(v) for v in a.bs.split(',')] for sh in shifts for s in seeds]
    tasks = [t for t in tasks if not (out / f'{t[0]}_b{t[1]}_{"shift" if t[3] else "iid"}_{t[2]}.json').exists()]
    def go(t):
        r = run(t[0], a.data, t[1], t[2], t[3], rounds=(a.max_round != 1), max_round=(a.max_round or None), maxit=a.maxit, gap=a.gap); (out / f'{t[0]}_b{t[1]}_{"shift" if t[3] else "iid"}_{t[2]}.json').write_text(json.dumps(r, indent=1)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t, 'fixed %.3f (v12 %.3f) fit %.3f PS %.3f PSfit %.3f lower %.3f upperNP %.3f' % (r['fixed_ratio'], r.get('v12_fixed_ratio', float('nan')), r['fixed_fit_ratio'], r['ps_ratio'], r['ps_fit_ratio'], r['bracket_lower'], r['bracket_upper_completion']),
                      ' '.join('r%d %.3f' % (rr, r.get(f'round{rr}_ratio', float('nan'))) for rr in range(2, t[1] + 1)),
                      'heur ' + ' '.join('%.3f' % (r.get(f'heur{rr}_ratio') or float('nan')) for rr in range(2, t[1])),
                      'pos0.1 b %.2f f %.2f' % (r['position']['0.1']['bias_branch_se'], r['position']['0.1']['bias_fit_se']), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1500:], flush=True)
