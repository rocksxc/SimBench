"""Exact population-specific fixed vs ALL-depth-3-tree branching coefficients for the
v11 independent-forest tasks, by column generation with a certified dual lower bound.

Population: P_alpha = (1-alpha) * empirical held-out law + alpha * uniform(cube x labels),
alpha=0.01 (full support, so every dual information value is finite).
Fixed menu: all coordinate triples (exact fixed class for b=3).
Branch menu: all deterministic depth-3 trees (exact branching class), generated lazily.
At each iteration: master value = upper bound on M_branch; num^2 / max_{all trees} info(eta)
= certified lower bound (dual witness evaluated over every depth-3 tree by dynamic programming).
"""
import argparse, json, sys, time, warnings
from pathlib import Path
from itertools import combinations
import numpy as np
import scipy.sparse as sp
from scipy.linalg import cho_factor, cho_solve
import cvxpy as cp
from sklearn.ensemble import RandomForestClassifier

V11 = Path("/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/handoff/ICML_Handoff_v12/Research/code")
sys.path.insert(0, str(V11))
from forest_audit import fwht, allbits, data  # noqa: E402  (v11 released code)


class FixedTree:
    """A depth-<=3 tree given by root feature and child features; apply() returns leaf ids."""
    def __init__(self, spec):
        self.spec = spec  # (j1, (j2_0, j2_1), ((j3_00, j3_01), (j3_10, j3_11)))
    def apply(self, grid):
        j1, (a, b_), ((c00, c01), (c10, c11)) = self.spec
        v1 = grid[:, j1].astype(int)
        j2 = np.where(v1 == 0, a, b_)
        v2 = grid[np.arange(len(grid)), j2].astype(int)
        j3 = np.select([(v1 == 0) & (v2 == 0), (v1 == 0) & (v2 == 1), (v1 == 1) & (v2 == 0)], [c00, c01, c10], c11)
        v3 = grid[np.arange(len(grid)), j3].astype(int)
        return 4 * v1 + 2 * v2 + v3


class Menu:
    """Same Fourier-constrained menu as v11 forest_audit.Menu, but trees can be appended."""
    def __init__(self, m, b, trees=()):
        self.m = m; self.b = b; self.grid = allbits(m)
        self.terms = np.array([s for s in range(1 << m) if s.bit_count() <= b])
        self.lookup = {s: i for i, s in enumerate(self.terms)}
        self.codes = []; self.sizes = []; self.cols = []; self.names = []
        for form in combinations(range(m), min(b, m)):
            C = 1 << len(form); codes = self.grid[:, form] @ (1 << np.arange(len(form)))
            self._add(codes, C, ('form', form))
        for t in trees:
            leaf = t.apply(self.grid); _, codes = np.unique(leaf, return_inverse=True)
            self._add(codes, codes.max() + 1, ('tree', getattr(t, 'spec', None)))
        self._finish()

    def _add(self, codes, C, name):
        h = fwht(np.eye(C)[codes]) / (1 << self.m)
        off = np.setdiff1d(np.arange(1 << self.m), self.terms)
        assert np.max(np.abs(h[off]), initial=0) < 1e-12
        self.codes.append(codes); self.sizes.append(C); self.cols.append(sp.csc_matrix(h[self.terms])); self.names.append(name)

    def _finish(self):
        self.F = sp.hstack(self.cols).tocsc()
        self.offset = np.r_[0, np.cumsum(self.sizes)]
        self.group = np.repeat(np.arange(len(self.sizes)), self.sizes)

    def add_trees(self, trees):
        for t in trees:
            leaf = t.apply(self.grid); _, codes = np.unique(leaf, return_inverse=True)
            self._add(codes, codes.max() + 1, ('tree', t.spec))
        self._finish()

    def masses(self, index, y, alpha):
        out = np.zeros((2, self.offset[-1]))
        for a, codes in enumerate(self.codes):
            c = codes[index]; C = self.sizes[a]; sl = slice(self.offset[a], self.offset[a + 1])
            for z in range(2):
                out[z, sl] = (1 - alpha) * np.bincount(c[y == z], minlength=C) / len(y) + alpha / (2 * C)
        return out

    def solve(self, mass, coef):
        L = len(self.sizes); M = self.offset[-1]
        q = cp.Variable(L, nonneg=True); g = cp.Variable((2, M)); u = cp.Variable((2, M), nonneg=True)
        Q = sp.csc_matrix((np.ones(M), (np.arange(M), self.group)), shape=(M, L)) @ q
        eq = [self.F @ g[z] == (2 * z - 1) * coef for z in range(2)]
        cons = [cp.sum(q) == 1, *eq]
        for z in range(2):
            cons.append(cp.SOC(Q + u[z], cp.vstack([2 * g[z], Q - u[z]]), axis=0))
        prob = cp.Problem(cp.Minimize(cp.sum(cp.multiply(mass, u))), cons)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            prob.solve(solver='CLARABEL', tol_gap_abs=1e-9, tol_gap_rel=1e-9, tol_feas=1e-9, max_iter=400)
        if prob.status not in ['optimal', 'optimal_inaccurate']:
            raise RuntimeError(prob.status)
        eta = np.array([-e.dual_value / 2 for e in eq])
        return float(prob.value), q.value, eta


def cell_info_triples(m, eta, terms, grid, mass_cube):
    """For every triple T and cell u, return per-label numerators and masses:
    num_z(T,u)=2^-m sum_{x:x_T=u} H_z(x), mass_z(T,u)=sum_{x:x_T=u} P(x,z)."""
    H = np.zeros((2, 1 << m))
    for z in range(2):
        full = np.zeros(1 << m); full[terms] = eta[z]
        H[z] = fwht(full)  # sum_S eta(S) chi_S(x)
    triples = list(combinations(range(m), 3))
    info = {}
    for T in triples:
        codes = grid[:, T] @ (1 << np.arange(3))
        val = np.zeros(8)
        for z in range(2):
            num = np.bincount(codes, weights=H[z], minlength=8) / (1 << m)
            ms = np.bincount(codes, weights=mass_cube[z], minlength=8)
            val += num ** 2 / ms
        info[T] = val  # indexed by code = x_T0 + 2 x_T1 + 4 x_T2 (T sorted)
    return info


def best_tree(m, info):
    """DP over all depth-3 trees with distinct features on each path; leaf value from triple cells."""
    def leafval(f1, v1, f2, v2, f3, v3):
        T = tuple(sorted((f1, f2, f3))); vals = {f1: v1, f2: v2, f3: v3}
        code = sum(vals[T[k]] << k for k in range(3))
        return info[T][code]
    per_root = []
    for j1 in range(m):
        tot = 0; spec2 = []; spec3 = []
        for v1 in range(2):
            b2 = (-1, None, None)
            for j2 in range(m):
                if j2 == j1: continue
                s = 0; ch = []
                for v2 in range(2):
                    b3 = max((leafval(j1, v1, j2, v2, j3, 0) + leafval(j1, v1, j2, v2, j3, 1), j3) for j3 in range(m) if j3 not in (j1, j2))
                    s += b3[0]; ch.append(b3[1])
                if s > b2[0]: b2 = (s, j2, tuple(ch))
            tot += b2[0]; spec2.append(b2[1]); spec3.append(b2[2])
        per_root.append((tot, (j1, tuple(spec2), tuple(spec3))))
    per_root.sort(key=lambda r: -r[0])
    return per_root


def run_task(name, seed, m, root, alpha=0.01, max_iter=150, tol=1e-7):
    t0 = time.time()
    X, y = data(name, Path(root)); perm = np.random.default_rng(seed).permutation(len(y))
    n0, n1 = {'WDBC': (100, 200), 'Spambase': (500, 1000), 'Ionosphere': (60, 120)}[name]
    tr0 = perm[:n0]; tr1 = perm[n0:n0 + n1]; train = perm[:n0 + n1]; test = perm[n0 + n1:]
    median = np.median(X[train], axis=0); binary = (X > median).astype(np.int8)
    eligible = np.flatnonzero((binary[train].min(axis=0) == 0) & (binary[train].max(axis=0) == 1))
    chosen = eligible[np.linspace(0, len(eligible) - 1, 12).round().astype(int)][:m]; x = binary[:, chosen]
    pars = dict(n_estimators=20, max_depth=3, max_features='sqrt', min_samples_leaf=max(3, n0 // 30), n_jobs=1)
    old = RandomForestClassifier(random_state=seed + 101, **pars).fit(x[tr0], y[tr0])
    new = RandomForestClassifier(random_state=seed + 307, **pars).fit(x[tr1], y[tr1])
    grid = allbits(m)
    d = new.predict_proba(grid)[:, 1] - old.predict_proba(grid)[:, 1]; idx = x @ (1 << np.arange(m))
    # population P_alpha on cube x labels
    Pemp = np.zeros((2, 1 << m))
    for z in range(2): Pemp[z] = np.bincount(idx[test][y[test] == z], minlength=1 << m) / len(test)
    P = (1 - alpha) * Pemp + alpha / (2 * (1 << m))
    tt = np.array([-d, d])  # t(x,z) = (2z-1) d(x)
    second = float(np.sum(P * tt ** 2)); delta = float(np.sum(P * tt))
    scale = max(np.max(np.abs(d)), 1e-12)
    coef_full = fwht(d) / (1 << m)
    row = dict(dataset=name, seed=seed, m=m, alpha=alpha, delta=delta, second=second, full_var=second - delta ** 2)
    if m == 3:
        # one triple = whole cube: both classes compute t exactly.
        row.update(fixed_M=second, branch_M_upper=second, branch_M_lower=second, branch_M_lower_best=second, v11menu_M=second, iterations=0, trees_added=0,
                   gamma_fixed=1.0, gamma_branch=1.0, seconds=time.time() - t0)
        return row
    fixed = Menu(m, 3)
    coef = coef_full[fixed.terms] / scale
    fmass = fixed.masses(idx[test], y[test], alpha)
    fval, fq, feta = fixed.solve(fmass, coef)
    row['fixed_M'] = fval * scale ** 2
    # energy fractions for witness h = t (diagnostic): Gamma = max_iota E[(E[t|cell])^2]/E[t^2]
    def explained(menu, mass_of):
        best = 0
        for a, codes in enumerate(menu.codes):
            e = 0
            for z in range(2):
                num = np.bincount(codes, weights=P[z] * tt[z], minlength=menu.sizes[a])
                den = np.bincount(codes, weights=P[z], minlength=menu.sizes[a])
                e += np.sum(num ** 2 / den)
            best = max(best, e)
        return best / second
    row['gamma_fixed'] = explained(fixed, None)
    comps = list(old.estimators_) + list(new.estimators_)
    branch = Menu(m, 3, comps)
    hist = []; added = 0
    for it in range(max_iter):
        bmass = branch.masses(idx[test], y[test], alpha)
        bval, bq, beta_ = branch.solve(bmass, coef)
        info = cell_info_triples(m, beta_, branch.terms, grid, P)
        cand = best_tree(m, info); tot = cand[0][0]
        # current max info over menu items under same witness
        H = np.zeros((2, 1 << m))
        for z in range(2):
            full = np.zeros(1 << m); full[branch.terms] = beta_[z]; H[z] = fwht(full)
        cur = 0
        for a, codes in enumerate(branch.codes):
            v = 0
            for z in range(2):
                num = np.bincount(codes, weights=H[z], minlength=branch.sizes[a]) / (1 << m)
                ms = np.bincount(codes, weights=P[z], minlength=branch.sizes[a])
                v += np.sum(num ** 2 / ms)
            cur = max(cur, v)
        numer = float(np.sum(beta_ * np.array([-coef, coef])))
        lower = numer ** 2 / max(tot, cur)
        hist.append((bval, lower, tot, cur))
        if bval - lower <= 1e-6 * max(bval, 1e-12) or tot <= cur * (1 + tol):
            break
        new = [FixedTree(sp_) for v, sp_ in cand if v > cur * (1 + tol)][:6]
        branch.add_trees(new); added += len(new)
    row['v11menu_M'] = hist[0][0] * scale ** 2
    row['branch_M_upper'] = min(h[0] for h in hist) * scale ** 2
    row['branch_M_lower_best'] = max(h[1] for h in hist) * scale ** 2
    row['branch_M_lower'] = row['branch_M_lower_best']
    row['iterations'] = len(hist); row['trees_added'] = added
    # Gamma for all trees with witness t: DP with eta replaced by t's per-cell values
    # (compute directly: max over trees of sum_leaf sum_z (sum P t)^2 / sum P)
    infot = {}
    for T in combinations(range(m), 3):
        codes = grid[:, T] @ (1 << np.arange(3)); val = np.zeros(8)
        for z in range(2):
            num = np.bincount(codes, weights=P[z] * tt[z], minlength=8); den = np.bincount(codes, weights=P[z], minlength=8)
            val += num ** 2 / den
        infot[T] = val
    row['gamma_branch'] = best_tree(m, infot)[0][0] / second
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', type=Path, required=True)
    p.add_argument('--dataset', default='WDBC'); p.add_argument('--seed', type=int, default=20261108); p.add_argument('--m', type=int, default=6)
    a = p.parse_args()
    r = run_task(a.dataset, a.seed, a.m, a.data)
    r['ratio_upper'] = (r['fixed_M'] - r['delta'] ** 2) / max(r['branch_M_lower'] - r['delta'] ** 2, 1e-15)
    r['ratio_lower'] = (r['fixed_M'] - r['delta'] ** 2) / max(r['branch_M_upper'] - r['delta'] ** 2, 1e-15)
    print(json.dumps(r, indent=1))
