"""Case study: validating a budgeted screening tree (depth b, at most b questions per person)
on a target population, with at most b answers per person in the validation sample.

Designs compared (all pointwise unbiased for every population on the declared cube):
  branch      : follow the tree itself (computes t exactly; full-information variance)
  fixed_oracle: best randomized fixed b-form design for the target population (all C(m,b) forms;
                the strongest admissible pre-committed unbiased design)
  fixed_fit   : same program fitted on SOURCE records (smoothed), evaluated on target
  fixed_ht    : completion-only path guessing, uniform over the tree's padded path sets
  round_r     : follow the first r-1 tree levels one question per round, then the best fixed form of
                the remaining size inside the reached subtree (an r-round design), oracle and fitted
Diagnostics: N_P (effective number of path sets, Renyi-1/2) and Gamma_P (best single-form energy).
Theorem: E[t^2]/Gamma_P <= M_fixed(P) <= N_P E[t^2], where M = second moment.
"""
import argparse, json, sys, time, warnings
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd
import scipy.sparse as sp
import cvxpy as cp
from sklearn.tree import DecisionTreeClassifier

V11 = Path("/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/handoff/ICML_Handoff_v12/Research/code")
sys.path.insert(0, str(V11))
from forest_audit import fwht, allbits  # noqa: E402


# ----------------------------------------------------------------------------- data
def load(name, root):
    root = Path(root)
    if name == 'BRFSS':
        df = pd.read_csv(root / 'cdc_diabetes.csv')
        X = pd.DataFrame({
            'HighBP': df.HighBP, 'HighChol': df.HighChol, 'Obese': (df.BMI >= 30).astype(int),
            'Smoker': df.Smoker, 'Stroke': df.Stroke, 'HeartDis': df.HeartDiseaseorAttack,
            'PhysAct': df.PhysActivity, 'HvyAlc': df.HvyAlcoholConsump, 'FairPoorHlth': (df.GenHlth >= 4).astype(int),
            'DiffWalk': df.DiffWalk, 'Age60': (df.Age >= 9).astype(int), 'LowInc': (df.Income <= 5).astype(int)})
        return X.to_numpy(np.int8), df.Diabetes_binary.to_numpy(int), list(X.columns), df.Sex.to_numpy(int)
    if name == 'Thyroid':
        cols = ['age', 'sex', 'on_thyroxine', 'query_on_thyroxine', 'on_antithyroid', 'sick', 'pregnant', 'thyroid_surgery',
                'I131', 'query_hypo', 'query_hyper', 'lithium', 'goitre', 'tumor', 'hypopituitary', 'psych',
                'TSH', 'T3', 'TT4', 'T4U', 'FTI', 'cls']
        tr = pd.read_csv(root / 'thyroid' / 'ann-train.data', sep=r'\s+', header=None, names=cols)
        te = pd.read_csv(root / 'thyroid' / 'ann-test.data', sep=r'\s+', header=None, names=cols)
        df = pd.concat([tr, te], ignore_index=True)
        # thresholds fixed a priori from pooled training-file quantiles of the lab values (no labels used)
        q = tr[['age', 'TSH', 'T3', 'TT4', 'T4U', 'FTI']].quantile([.25, .75])
        X = pd.DataFrame({
            'Age>Q3': (df.age > q.loc[.75, 'age']).astype(int), 'Sex': df.sex.astype(int), 'OnThyroxine': df.on_thyroxine,
            'Surgery': df.thyroid_surgery, 'QueryHypo': df.query_hypo, 'Goitre': df.goitre,
            'TSHhigh': (df.TSH > q.loc[.75, 'TSH']).astype(int), 'T3low': (df.T3 < q.loc[.25, 'T3']).astype(int),
            'TT4low': (df.TT4 < q.loc[.25, 'TT4']).astype(int), 'T4Uhigh': (df.T4U > q.loc[.75, 'T4U']).astype(int),
            'FTIlow': (df.FTI < q.loc[.25, 'FTI']).astype(int), 'Sick': df.sick})
        return X.to_numpy(np.int8), (df.cls != 3).to_numpy(int), list(X.columns), df.sex.to_numpy(int)
    raise ValueError(name)


# ----------------------------------------------------------------------------- menus on a subcube
class FormMenu:
    """All coordinate subsets of size k of the m' free coordinates, with Fourier constraints
    sum_T ghat_T(S) = that(S) for |S|<=k (equivalent to pointwise unbiasedness on the subcube)."""
    def __init__(self, mm, k):
        self.m = mm; self.k = k; self.grid = allbits(mm)
        self.terms = np.array([s for s in range(1 << mm) if s.bit_count() <= k])
        lookup = {s: i for i, s in enumerate(self.terms)}
        self.forms = list(combinations(range(mm), k)); self.codes = []; cols = []
        C = 1 << k
        H = fwht(np.eye(C)) / C  # H[s, u] = 2^-k chi_s(u)
        rr = []; cc = []; vv = []; off = 0
        for form in self.forms:
            self.codes.append(self.grid[:, form] @ (1 << np.arange(k)))
            for s in range(C):
                glob = sum(1 << form[j] for j in range(k) if s >> j & 1)
                rr.extend([lookup[glob]] * C); cc.extend(range(off, off + C)); vv.extend(H[s])
            off += C
        self.F = sp.csc_matrix((vv, (rr, cc)), shape=(len(self.terms), off))
        self.C = C; self.L = len(self.forms); self.group = np.repeat(np.arange(self.L), C)
        self.codes = np.array(self.codes)  # L x 2^m'

    def cellmass(self, Pz):
        """Pz: (2, 2^m') mass on subcube x label -> (2, L*C) cell masses."""
        out = np.zeros((2, self.L * self.C))
        for a in range(self.L):
            for z in range(2):
                out[z, a * self.C:(a + 1) * self.C] = np.bincount(self.codes[a], weights=Pz[z], minlength=self.C)
        return out

    def solve(self, mass, d, beta=0.0):
        """min sum mass * g^2/q s.t. unbiased for t=(2z-1)d on the whole subcube. Returns (value, q, tables)."""
        scale = max(np.max(np.abs(d)), 1e-12)
        coef = fwht(d) / (1 << self.m)
        offt = np.setdiff1d(np.arange(1 << self.m), self.terms)
        assert np.max(np.abs(coef[offt]), initial=0) < 1e-9, 'contrast degree exceeds form size'
        coef = coef[self.terms] / scale; L = self.L; M = L * self.C
        q = cp.Variable(L, nonneg=True); g = cp.Variable((2, M)); u = cp.Variable((2, M), nonneg=True)
        Q = sp.csc_matrix((np.ones(M), (np.arange(M), self.group)), shape=(M, L)) @ q
        cons = [cp.sum(q) == 1, q >= beta / L] + [self.F @ g[z] == (2 * z - 1) * coef for z in range(2)]
        for z in range(2):
            cons.append(cp.SOC(Q + u[z], cp.vstack([2 * g[z], Q - u[z]]), axis=0))
        prob = cp.Problem(cp.Minimize(cp.sum(cp.multiply(mass, u))), cons)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            prob.solve(solver='CLARABEL', tol_gap_abs=1e-9, tol_gap_rel=1e-9, tol_feas=1e-9, max_iter=400)
        if prob.status not in ['optimal', 'optimal_inaccurate']:
            raise RuntimeError(prob.status)
        qq = np.maximum(q.value, 1e-12); qq = qq / qq.sum(); gg = g.value * scale
        # exact repair of the linear constraints (least-norm correction)
        for z in range(2):
            r = (2 * z - 1) * coef * scale - self.F @ gg[z]
            gg[z] += self.F.T @ np.linalg.lstsq((self.F @ self.F.T).toarray(), r, rcond=None)[0]
        res = max(np.max(np.abs(self.F @ gg[z] - (2 * z - 1) * coef * scale)) for z in range(2))
        assert res < 1e-8, res
        return float(prob.value) * scale ** 2, qq, gg

    def second_moment(self, mass, q, gg):
        return float(np.sum(mass * gg ** 2 / q[self.group]))


# ----------------------------------------------------------------------------- tree helpers
def tree_paths(clf, m):
    """Return for every profile of the cube: leaf id, path feature list."""
    grid = allbits(m)
    leaves = clf.apply(grid)
    t = clf.tree_; paths = {}
    def rec(node, feats):
        if t.children_left[node] == -1:
            paths[node] = feats; return
        f = int(t.feature[node])
        rec(t.children_left[node], feats + [f]); rec(t.children_right[node], feats + [f])
    rec(0, [])
    return leaves, paths


def padded_set(feats, b, m):
    s = []
    for f in feats:
        if f not in s: s.append(f)
    for j in range(m):
        if len(s) >= b: break
        if j not in s: s.append(j)
    return tuple(sorted(s[:b]))


def run(name, root, b, seed, shift=False, alpha=0.01, n_source=20000):
    t0 = time.time()
    X, y, names, sex = load(name, root); m = X.shape[1]
    rng = np.random.default_rng(seed)
    if shift and name == 'BRFSS':
        # source: one sex; target: the other (Sex is not a model feature)
        src = np.flatnonzero(sex == 0); tgt = np.flatnonzero(sex == 1)
    elif shift and name == 'Thyroid':
        f = names.index('Sex'); src = np.flatnonzero(X[:, f] == 1); tgt = np.flatnonzero(X[:, f] == 0)
    else:
        perm = rng.permutation(len(y)); half = len(y) // 2; src = perm[:half]; tgt = perm[half:]
    src = rng.permutation(src); tr = src[:min(n_source, len(src) // 2)]; cal = src[len(tr):len(tr) + min(n_source, len(src) - len(tr))]
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50 if name == 'BRFSS' else 10, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    grid = allbits(m); idx = X @ (1 << np.arange(m))
    pred = clf.predict(grid).astype(float)
    d = 2 * pred - 1  # accuracy contrast vs coin flip: E[Y d] = 2 acc - 1 (deterministic screening decision)
    def law(rows, a):
        P = np.zeros((2, 1 << m))
        for z in range(2): P[z] = np.bincount(idx[rows][y[rows] == z], minlength=1 << m) / len(rows)
        return (1 - a) * P + a / (2 * (1 << m))
    P = law(tgt, alpha); Pc = law(cal, 0.1)  # target population; smoothed source calibration reference
    tt = np.array([-d, d]); second = float(np.sum(P * tt ** 2)); delta = float(np.sum(P * tt)); fullvar = second - delta ** 2
    leaves, paths = tree_paths(clf, m)
    used = sorted({f for p in paths.values() for f in p})
    sets = {}
    for lf, feats in paths.items():
        sets.setdefault(padded_set(feats, b, m), []).append(lf)
    leaf_of = leaves
    setid = np.array([list(sets).index(padded_set(paths[l], b, m)) for l in leaf_of])
    w = np.array([np.sum(P * tt ** 2 * (setid == s)[None, :]) for s in range(len(sets))])
    N_P = float(np.sum(np.sqrt(w)) ** 2 / second)
    row = dict(dataset=name, shift=shift, b=b, seed=seed, m=m, n_target=len(tgt), n_train=len(tr), n_cal=len(cal),
               accuracy=(delta + 1) / 2, delta=delta, full_var=fullvar, used_features=len(used), path_sets=len(sets), N_P=N_P)
    menu = FormMenu(m, b)
    mass = menu.cellmass(P); cmass = menu.cellmass(Pc)
    val, q, gg = menu.solve(mass, d)
    row['fixed_oracle_M'] = val
    # Gamma_P with witness t
    best = 0
    for a in range(menu.L):
        e = 0
        for z in range(2):
            num = np.bincount(menu.codes[a], weights=P[z] * tt[z], minlength=menu.C); den = np.bincount(menu.codes[a], weights=P[z], minlength=menu.C)
            e += np.sum(np.divide(num ** 2, den, out=np.zeros_like(num), where=den > 0))
        best = max(best, e)
    row['Gamma_P'] = best / second
    # fitted fixed design (source calibration), evaluated on target
    vfit, qf, gf = menu.solve(cmass, d, beta=0.05)
    row['fixed_fit_M'] = menu.second_moment(mass, qf, gf)
    # completion-only HT path guessing, uniform over path sets
    K = len(sets)
    row['fixed_ht_M'] = float(K * second)  # E[(K t 1{set})^2 averaged over uniform set] = K E[t^2]
    # r-round follow-then-fixed (oracle and fitted), r = 2..b-1
    t = clf.tree_
    for r in range(2, b):
        tot_or = 0.0; tot_fit = 0.0
        # enumerate nodes at depth r-1 along with their path constraints
        def nodes_at(node, depth, cons):
            if depth == r - 1 or t.children_left[node] == -1:
                yield node, cons; return
            f = int(t.feature[node])
            yield from nodes_at(t.children_left[node], depth + 1, cons + [(f, 0)])
            yield from nodes_at(t.children_right[node], depth + 1, cons + [(f, 1)])
        for node, cons in nodes_at(0, 0, []):
            fixedf = [f for f, _ in cons]; free = [j for j in range(m) if j not in fixedf]
            mask = np.ones(1 << m, bool)
            for f, v in cons: mask &= (grid[:, f] == v)
            sub = np.flatnonzero(mask)  # profiles in this node, ordered by free coordinates
            subgrid = grid[sub][:, free]; order = np.argsort(subgrid @ (1 << np.arange(len(free))))
            sub = sub[order]
            Ps = P[:, sub]; Pcs = Pc[:, sub]; ds = d[sub]
            k = b - len(cons)
            if Ps.sum() <= 0: continue
            if len(cons) < r - 1 or k <= 0 or np.ptp(ds) == 0:  # leaf reached early or constant: compute exactly
                tot_or += float(np.sum(Ps * np.array([-ds, ds]) ** 2)); tot_fit += float(np.sum(Ps * np.array([-ds, ds]) ** 2)); continue
            sm = FormMenu(len(free), k)
            v, qs, gs = sm.solve(sm.cellmass(Ps), ds); tot_or += v
            vf, qsf, gsf = sm.solve(sm.cellmass(Pcs / max(Pcs.sum(), 1e-12)), ds, beta=0.05)
            tot_fit += sm.second_moment(sm.cellmass(Ps), qsf, gsf)
        row[f'round{r}_oracle_M'] = tot_or; row[f'round{r}_fit_M'] = tot_fit
    d2 = delta ** 2
    for key in [k for k in list(row) if k.endswith('_M')]:
        row[key.replace('_M', '_ratio')] = (row[key] - d2) / fullvar
    row['bracket_lower'] = (second / row['Gamma_P'] - d2) / fullvar
    row['bracket_upper'] = (N_P * second - d2) / fullvar
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--datasets', default='BRFSS,Thyroid'); p.add_argument('--bs', default='3,4,5,6'); p.add_argument('--seeds', type=int, default=5)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for ds in a.datasets.split(','):
        for b in [int(v) for v in a.bs.split(',')]:
            for shift in [False, True]:
                for s in range(a.seeds):
                    dest = out / f'{ds}_b{b}_{"shift" if shift else "iid"}_{s}.json'
                    if dest.exists(): continue
                    r = run(ds, a.data, b, 20261108 + s, shift)
                    dest.write_text(json.dumps(r, indent=1))
                    print(ds, b, shift, s, 'acc %.3f' % r['accuracy'], 'oracle %.2f fit %.2f ht %.2f' % (r['fixed_oracle_ratio'], r['fixed_fit_ratio'], r['fixed_ht_ratio']),
                          'bracket [%.2f, %.2f]' % (r['bracket_lower'], r['bracket_upper']),
                          ' '.join('r%d %.2f' % (rr, r[f'round{rr}_oracle_ratio']) for rr in range(2, b)), '%.0fs' % r['seconds'], flush=True)
