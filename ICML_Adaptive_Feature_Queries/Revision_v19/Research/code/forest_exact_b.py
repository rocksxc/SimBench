"""Exact fixed vs ALL-depth-b-tree branching coefficients for independent depth-b forest updates
(cap b), by column generation with a certified dual lower bound (generalizes forest_exact.py).
Also computes a FITTED all-tree design (column generation on the smoothed training law) and its
realized second moment on the held-out law, next to the fitted fixed design.
"""
import argparse, json, sys, time, warnings
from pathlib import Path
from itertools import combinations
from functools import lru_cache
import numpy as np
import scipy.sparse as sp
import cvxpy as cp
from sklearn.ensemble import RandomForestClassifier

V11 = Path("/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/handoff/ICML_Handoff_v12/Research/code")
sys.path.insert(0, str(V11))
from forest_audit import fwht, allbits, data  # noqa: E402


class SpecTree:
    """spec = (feature, child0_spec, child1_spec) or None for a leaf; leaf ids = binary path code."""
    def __init__(self, spec, depth):
        self.spec = spec; self.depth = depth
    def apply(self, grid):
        n = len(grid); code = np.zeros(n, int)
        def rec(spec, rows, prefix, lvl):
            if spec is None or lvl == self.depth:
                code[rows] = prefix; return
            f, c0, c1 = spec; v = grid[rows, f]
            rec(c0, rows[v == 0], prefix * 2, lvl + 1); rec(c1, rows[v == 1], prefix * 2 + 1, lvl + 1)
        rec(self.spec, np.arange(n), 0, 0)
        return code


class Menu:
    def __init__(self, m, b, trees=()):
        self.m = m; self.b = b; self.grid = allbits(m)
        self.terms = np.array([s for s in range(1 << m) if s.bit_count() <= b])
        self.codes = []; self.sizes = []; self.cols = []
        for form in combinations(range(m), min(b, m)):
            self._add(self.grid[:, form] @ (1 << np.arange(len(form))), 1 << len(form))
        self.add_trees(trees)

    def _add(self, codes, C):
        h = fwht(np.eye(C)[codes]) / (1 << self.m)
        self.codes.append(codes); self.sizes.append(C); self.cols.append(sp.csc_matrix(h[self.terms]))

    def add_trees(self, trees):
        for t in trees:
            leaf = t.apply(self.grid); _, codes = np.unique(leaf, return_inverse=True)
            self._add(codes, codes.max() + 1)
        self.F = sp.hstack(self.cols).tocsc(); self.offset = np.r_[0, np.cumsum(self.sizes)]
        self.group = np.repeat(np.arange(len(self.sizes)), self.sizes)

    def cellmass(self, P):
        out = np.zeros((2, self.offset[-1]))
        for a, codes in enumerate(self.codes):
            for z in range(2):
                out[z, self.offset[a]:self.offset[a + 1]] = np.bincount(codes, weights=P[z], minlength=self.sizes[a])
        return out

    def solve(self, mass, coef, beta=0.0):
        L = len(self.sizes); M = self.offset[-1]
        q = cp.Variable(L, nonneg=True); g = cp.Variable((2, M)); u = cp.Variable((2, M), nonneg=True)
        Q = sp.csc_matrix((np.ones(M), (np.arange(M), self.group)), shape=(M, L)) @ q
        eq = [self.F @ g[z] == (2 * z - 1) * coef for z in range(2)]
        cons = [cp.sum(q) == 1, q >= beta / L, *eq]
        for z in range(2):
            cons.append(cp.SOC(Q + u[z], cp.vstack([2 * g[z], Q - u[z]]), axis=0))
        prob = cp.Problem(cp.Minimize(cp.sum(cp.multiply(mass, u))), cons)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            prob.solve(solver='CLARABEL', tol_gap_abs=1e-9, tol_gap_rel=1e-9, tol_feas=1e-9, max_iter=400)
        if prob.status not in ['optimal', 'optimal_inaccurate']:
            raise RuntimeError(prob.status)
        eta = np.array([-e.dual_value / 2 for e in eq])
        qq = np.maximum(q.value, 1e-12); qq = qq / qq.sum(); gg = g.value.copy()
        FF = (self.F @ self.F.T).toarray()
        for z in range(2):
            gg[z] += self.F.T @ np.linalg.solve(FF, (2 * z - 1) * coef - self.F @ gg[z])
        return float(prob.value), qq, gg, eta

    def info_max(self, H, P):
        cur = 0
        for a, codes in enumerate(self.codes):
            v = 0
            for z in range(2):
                num = np.bincount(codes, weights=H[z], minlength=self.sizes[a]) / (1 << self.m)
                ms = np.bincount(codes, weights=P[z], minlength=self.sizes[a])
                v += np.sum(num ** 2 / ms)
            cur = max(cur, v)
        return cur


def best_trees(m, b, H, P, k=6):
    """DP over all depth-b trees: maximize sum_leaves sum_z (2^-m sum_{x in leaf} H_z)^2 / P(leaf,z).
    Returns up to k best trees (best per root feature)."""
    grid = allbits(m)
    w = [H[z] / (1 << m) for z in range(2)]

    @lru_cache(maxsize=None)
    def val(assign):  # assign: frozenset of (feature, value)
        mask = np.ones(1 << m, bool)
        for f, v in assign: mask &= grid[:, f] == v
        if len(assign) == b:
            return float(sum((w[z][mask].sum()) ** 2 / P[z][mask].sum() for z in range(2))), None
        used = {f for f, _ in assign}; best = (-1.0, None)
        for f in range(m):
            if f in used: continue
            v0, s0 = val(assign | {(f, 0)}); v1, s1 = val(assign | {(f, 1)})
            if v0 + v1 > best[0]: best = (v0 + v1, (f, s0, s1))
        return best
    out = []
    for f in range(m):
        v0, s0 = val(frozenset({(f, 0)})); v1, s1 = val(frozenset({(f, 1)}))
        out.append((v0 + v1, (f, s0, s1)))
    out.sort(key=lambda r: -r[0])
    return out[:k], out[0][0]


def colgen(menu, P, coef, m, b, beta=0.0, max_iter=200, tol=1e-7):
    hist = []
    for it in range(max_iter):
        mass = menu.cellmass(P)
        val, q, gg, eta = menu.solve(mass, coef, beta)
        H = np.zeros((2, 1 << m))
        for z in range(2):
            full = np.zeros(1 << m); full[menu.terms] = eta[z]; H[z] = fwht(full)
        cand, top = best_trees(m, b, H, P)
        cur = menu.info_max(H, P)
        numer = float(np.sum(eta * np.array([-coef, coef])))
        lower = numer ** 2 / max(top, cur) if beta == 0 else float('nan')
        hist.append((val, lower))
        if top <= cur * (1 + tol) or (beta == 0 and val - lower <= 1e-6 * val):
            break
        menu.add_trees([SpecTree(s, b) for v, s in cand if v > cur * (1 + tol)])
    if len(gg[0]) != menu.offset[-1]:  # columns were added after the last solve: re-solve once
        val, q, gg, eta = menu.solve(menu.cellmass(P), coef, beta)
        hist.append((val, float('nan')))
    return hist, q, gg


def run_task(name, seed, m, b, root, alpha=0.01):
    t0 = time.time()
    X, y = data(name, Path(root)); perm = np.random.default_rng(seed).permutation(len(y))
    n0, n1 = {'WDBC': (100, 200), 'Spambase': (500, 1000), 'Ionosphere': (60, 120)}[name]
    tr0 = perm[:n0]; tr1 = perm[n0:n0 + n1]; train = perm[:n0 + n1]; test = perm[n0 + n1:]
    median = np.median(X[train], axis=0); binary = (X > median).astype(np.int8)
    eligible = np.flatnonzero((binary[train].min(axis=0) == 0) & (binary[train].max(axis=0) == 1))
    chosen = eligible[np.linspace(0, len(eligible) - 1, 12).round().astype(int)][:m]; x = binary[:, chosen]
    pars = dict(n_estimators=20, max_depth=b, max_features='sqrt', min_samples_leaf=max(3, n0 // 30), n_jobs=1)
    old = RandomForestClassifier(random_state=seed + 101, **pars).fit(x[tr0], y[tr0])
    new = RandomForestClassifier(random_state=seed + 307, **pars).fit(x[tr1], y[tr1])
    grid = allbits(m); d = new.predict_proba(grid)[:, 1] - old.predict_proba(grid)[:, 1]; idx = x @ (1 << np.arange(m))
    def law(rows, a):
        P = np.zeros((2, 1 << m))
        for z in range(2): P[z] = np.bincount(idx[rows][y[rows] == z], minlength=1 << m) / len(rows)
        return (1 - a) * P + a / (2 * (1 << m))
    P = law(test, alpha); Ptr = law(train, 0.1)
    tt = np.array([-d, d]); second = float(np.sum(P * tt ** 2)); delta = float(np.sum(P * tt)); d2 = delta ** 2
    scale = max(np.max(np.abs(d)), 1e-12)
    row = dict(dataset=name, seed=seed, m=m, b=b, alpha=alpha, delta=delta, second=second, full_var=second - d2)
    active = sum(np.max(np.abs(d - d[np.arange(1 << m) ^ (1 << j)])) > 1e-9 for j in range(m)); row['active'] = int(active)
    if m <= b:
        row.update(fixed_M=second, branch_M_upper=second, branch_M_lower=second, ratio_exact_lower=1.0, ratio_exact_upper=1.0,
                   fixed_fit_M=second, branch_fit_M=second, ratio_fitted=1.0, iterations=0, seconds=time.time() - t0)
        return row
    fixed = Menu(m, b); coef = (fwht(d) / (1 << m))[fixed.terms] / scale
    fval, fq, fg, _ = fixed.solve(fixed.cellmass(P), coef); row['fixed_M'] = fval * scale ** 2
    fit_val, fq2, fg2, _ = fixed.solve(fixed.cellmass(Ptr), coef, beta=0.05)
    row['fixed_fit_M'] = float(np.sum(fixed.cellmass(P) * fg2 ** 2 / fq2[fixed.group])) * scale ** 2
    comps = list(old.estimators_) + list(new.estimators_)
    br = Menu(m, b, comps); v11 = br.solve(br.cellmass(P), coef)[0] * scale ** 2; row['compmenu_M'] = v11
    hist, bq, bg = colgen(br, P, coef, m, b)
    row['branch_M_upper'] = min(h[0] for h in hist) * scale ** 2; row['branch_M_lower'] = max(h[1] for h in hist) * scale ** 2
    row['iterations'] = len(hist); row['trees'] = len(br.sizes) - len(list(combinations(range(m), b)))
    # fitted all-tree design: column generation on the smoothed TRAINING law, evaluated on the held-out law
    brf = Menu(m, b, comps); hf, qf, gf = colgen(brf, Ptr, coef, m, b, beta=0.05, max_iter=80)
    row['branch_fit_M'] = float(np.sum(brf.cellmass(P) * gf ** 2 / qf[brf.group])) * scale ** 2
    row['ratio_exact_lower'] = (row['fixed_M'] - d2) / (row['branch_M_upper'] - d2)
    row['ratio_exact_upper'] = (row['fixed_M'] - d2) / max(row['branch_M_lower'] - d2, 1e-15)
    row['ratio_compmenu'] = (row['fixed_M'] - d2) / (v11 - d2)
    row['ratio_fitted'] = (row['fixed_fit_M'] - d2) / (row['branch_fit_M'] - d2)
    row['ratio_fixed_vs_fullinfo'] = (row['fixed_M'] - d2) / (second - d2)
    row['seconds'] = time.time() - t0
    return row


def go(args):
    t, data_root, out = args
    r = run_task(t[0], t[1], t[2], t[3], data_root)
    (Path(out) / f'{t[0]}_{t[1]}_m{t[2]}_b{t[3]}.json').write_text(json.dumps(r, indent=1))
    return r


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--bs', default='2,3,4'); p.add_argument('--ms', default='12'); p.add_argument('--seeds', type=int, default=5)
    p.add_argument('--workers', type=int, default=6); p.add_argument('--one', default='')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.one:
        ds, s, m, b = a.one.split(','); r = run_task(ds, int(s), int(m), int(b), a.data)
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, indent=0)); sys.exit()
    from concurrent.futures import ProcessPoolExecutor, as_completed
    tasks = [(ds, 20261108 + s, int(m), int(b)) for b in a.bs.split(',') for m in a.ms.split(',') for ds in ['WDBC', 'Spambase', 'Ionosphere'] for s in range(a.seeds)]
    tasks = [t for t in tasks if not (out / f'{t[0]}_{t[1]}_m{t[2]}_b{t[3]}.json').exists()]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, (t, a.data, str(out))): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result(); print(t, 'exact [%.3f,%.3f] comp %.3f fitted %.3f' % (r['ratio_exact_lower'], r['ratio_exact_upper'], r.get('ratio_compmenu', 1), r['ratio_fitted']), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                print('ERROR', t, repr(e), flush=True)
