"""v17 (round-6 R1 Q3, R2 Q1, R3 Q2): the value of within-record adaptivity when the law of (X, Y) is restricted to a
hierarchical log-linear model with all interactions of order <= k (the working models of curve_v16.py).

For a law P in the model with scores s_A = chi_A - E chi_A (A a nonempty set of at most k of the K + 1 variables), an
interview iota has Fisher information I_iota = E[E[s | transcript] E[s | transcript]'] and the target has gradient
v = E[(t - Delta) s]. The local asymptotic minimax constant of a class of interviews is

    W^M_class(P) = min_q v' (sum_iota q_iota I_iota)^+ v,

a c-optimal design problem. It is the constant of Theorem 1 with the dual witness h restricted to the tangent space of
the model. ModelEngine computes it for fixed forms (all b-subsets of the K items) and, by column generation with the
exact tree pricing of capdesign.Engine, for branching interviews. Every reported value has a certified lower bound
(v'u)^2 / max_iota u' I_iota u, the maximum being exact over the class.

Weights of a restricted menu are optimised through the Elfving dual (a second-order cone program; the multipliers of
its cone constraints are the weights), with the multiplicative algorithm q <- q (d/f)^(1/2) as a fallback. Optimality
is certified by the bound above, not assumed."""
import argparse, json, sys, time
from itertools import combinations
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capdesign as cd


def bits(n):
    return ((np.arange(1 << n)[:, None] >> np.arange(n)) & 1).astype(np.int64)


def loglin_fit(emp, order, sweeps=2000, tol=1e-12):
    """Maximum-likelihood fit of the all-`order`-way hierarchical log-linear model to a positive law `emp` on
    {0,1}^V (flat index, bit v = variable v) by iterative proportional fitting."""
    V = int(np.log2(len(emp))); B = bits(V); order = min(order, V)
    idx = [sum(B[:, v] << p for p, v in enumerate(c)) for c in combinations(range(V), order)]; size = 1 << order
    targ = [np.bincount(ix, weights=emp, minlength=size) for ix in idx]
    p = np.full(len(emp), 1.0 / len(emp))
    for _ in range(sweeps):
        old = p.copy()
        for ix, tg in zip(idx, targ):
            cur = np.bincount(ix, weights=p, minlength=size); p = p * (tg / cur)[ix]
        if np.max(np.abs(p - old)) < tol: break
    return p / p.sum()


class ModelEngine(cd.Engine):
    """Engine on the K items a rule depends on, at a law `cube` (2, 2^K) over (label, profile), with the dual witness
    restricted to the tangent space of the order-k log-linear model on the K items and the label."""
    def __init__(self, K, b, cube, d, order):
        lat = cd.Lattice(K, b); dfull = cd.wht(d) / (1 << K)
        super().__init__(K, b, cube=cube, dvals=d, dhat=dfull[lat.allmasks], alpha=0.0)
        self.K = K; self.order = order; grid = bits(K); sx = 1 - 2 * grid  # chi of a profile bit: 0 -> +1, 1 -> -1
        t = np.stack([-d, d]); self.delta = float(np.sum(cube * t)); self.var = float(np.sum(cube * t * t) - self.delta ** 2)
        self.terms = [c for j in range(1, order + 1) for c in combinations(range(K + 1), j)]; self.p = len(self.terms)
        R = np.zeros((self.p, 2, lat.nterms)); v = np.zeros(self.p); full = np.zeros((self.p, 2, 1 << K))
        for a, c in enumerate(self.terms):
            chi = np.ones((2, 1 << K))
            for j in c:
                if j < K: chi = chi * sx[:, j][None, :]
                else: chi = chi * np.array([-1.0, 1.0])[:, None]
            s = chi - np.sum(cube * chi); mu = cube * s
            R[a] = cd.wht(mu)[:, lat.allmasks]; v[a] = float(np.sum(mu * (t - self.delta))); full[a] = s
        self.R = R; self.v = v
        Fm = (full * np.sqrt(cube)[None]).reshape(self.p, -1); self.I_full = Fm @ Fm.T  # complete records
        self.W_full = float(v @ np.linalg.lstsq(self.I_full, v, rcond=None)[0])

    def info(self, cells):
        """Square-root factor G (p x 2*cells) of the interview's Fisher information, I = G G'."""
        f, u = cells; G = np.einsum('pzcs,cs->pzc', self.R[:, :, self.sub[f]], self.sign[u], optimize=True) / self.C
        G = G / np.sqrt(self.P[:, f, u])[None]
        return G.reshape(self.p, -1)

    def eta_of(self, u):
        return np.einsum('p,pzt->zt', u, self.R)

    def value(self, Gs, q):
        """f(q) = v' I(q)^+ v with I(q) = sum_i q_i G_i G_i'; returns (f, u, d) with d_i = u' I_i u."""
        n, p, c = Gs.shape; Gst = Gs.transpose(1, 0, 2).reshape(p, n * c)
        I = (Gst * np.repeat(q, c)[None, :]) @ Gst.T; u = np.linalg.lstsq(I, self.v, rcond=1e-11)[0]
        if np.linalg.norm(I @ u - self.v) > 1e-7 * max(np.linalg.norm(self.v), 1e-300):
            return np.inf, u, None
        dvec = ((Gst.T @ u) ** 2).reshape(n, c).sum(1)
        return float(self.v @ u), u, dvec

    def master(self, Gs, q0=None):
        """c-optimal weights on a menu: min s s.t. v'u = 1, ||G_i'u|| <= s (the Elfving dual); the multipliers of the
        cone constraints are the weights. Falls back to the multiplicative algorithm if the solver fails."""
        import cvxpy as cp, warnings
        n, p, c = Gs.shape; vn = self.v / np.linalg.norm(self.v)
        try:
            u = cp.Variable(p); s = cp.Variable()
            A = Gs.transpose(0, 2, 1).reshape(n * c, p)
            con = cp.SOC(s * np.ones(n), cp.reshape(A @ u, (n, c), order='C'), axis=1)
            prob = cp.Problem(cp.Minimize(s), [vn @ u == 1, con])
            with warnings.catch_warnings():
                warnings.simplefilter('ignore'); prob.solve(solver='CLARABEL', tol_gap_abs=1e-11, tol_gap_rel=1e-11, tol_feas=1e-11, max_iter=300)
            lam = np.maximum(np.asarray(con.dual_value[0]).ravel(), 0); q = lam / lam.sum()
            f, uu, dvec = self.value(Gs, q)
            if np.isfinite(f): return q
        except Exception:
            pass
        q = np.full(n, 1.0 / n) if q0 is None else q0 / q0.sum()
        for it in range(20000):
            f, uu, dvec = self.value(Gs, q)
            if not np.isfinite(f): raise RuntimeError('target not estimable on the menu')
            if f - f * f / dvec.max() <= 1e-6 * f: break
            q = q * np.sqrt(np.maximum(dvec, 0) / f); q = q / q.sum()
        return q

    def design(self, r, start, gap=1e-6, max_iter=400, k_add=6, verbose=False, time_budget=None):
        """Optimal design over fixed forms (r = 1; `start` must be the whole menu) or branching interviews (r = b)."""
        ints = list(start); Gs = np.stack([self.info(c) for c in ints]); t0 = time.time(); best_lb = -np.inf; q = None
        if np.linalg.norm(self.v) < 1e-13:
            return dict(value=0.0, lower=0.0, q=np.full(len(ints), 1.0 / len(ints)), interviews=ints, Gs=Gs, u=np.zeros(self.p), iterations=0)
        for it in range(max_iter):
            q = self.master(Gs, None if q is None else np.r_[q, np.full(len(ints) - len(q), 1e-3)])
            f, u, dvec = self.value(Gs, q)
            if r == 1:
                best_lb = f * f / dvec.max(); break
            e = self.cell_energy(self.eta_of(u)); top, cands = self.price(r, e, k_add)
            best_lb = max(best_lb, f * f / top)
            if verbose: print(it, len(ints), f, best_lb, flush=True)
            new = [c for val, c in cands if val > f * (1 + gap / 4)]
            if f - best_lb <= gap * f or not new: break
            if time_budget is not None and time.time() - t0 > time_budget: break
            Gs = np.concatenate([Gs, np.stack([self.info(c) for c in new])]); ints += new
        return dict(value=f, lower=best_lb, q=q, interviews=ints, Gs=Gs, u=u, iterations=it + 1)


def rule_interview(E, d):
    """A depth-<=b tree for d on the K-cube found greedily (split on the coordinate that leaves the fewest
    non-constant halves), padded to exactly b coordinates per leaf; returns cells or None if depth b is not enough."""
    K, b = E.K, E.b; grid = bits(K); cells_f = []; cells_u = []
    def rec(mask, val, depth):
        sel = np.all(((grid >> 0) & 1)[:, [j for j in range(K) if mask >> j & 1]] == [val >> j & 1 for j in range(K) if mask >> j & 1], axis=1) if mask else np.ones(1 << K, bool)
        dv = d[sel]
        if np.all(dv == dv[0]):
            return [(mask, val)]
        if depth == b: return None
        best = None
        for j in range(K):
            if mask >> j & 1: continue
            out = []; ok = True
            for x in (0, 1):
                sub = rec(mask | (1 << j), val | (x << j), depth + 1)
                if sub is None: ok = False; break
                out += sub
            if ok and (best is None or len(out) < len(best)): best = out
        return best
    leaves = rec(0, 0, 0)
    if leaves is None: return None
    for mask, val in leaves:
        pad = mask; j = 0
        while bin(pad).count('1') < b:
            if not pad >> j & 1: pad |= 1 << j
            j += 1
        f = int(E.lat.rank(b, np.array([pad]))[0]); co = [j for j in range(K) if pad >> j & 1]
        for uu in range(1 << b):
            if all(((uu >> i) & 1) == (val >> c & 1) for i, c in enumerate(co) if mask >> c & 1):
                cells_f.append(f); cells_u.append(uu)
    return (np.array(cells_f, np.int64), np.array(cells_u, np.int64))


def clf_interview(E, clf, used):
    """The fitted tree itself as an interview on the used items: splits on items the decision does not depend on are
    skipped (left child), paths are padded to b coordinates with the smallest unused indices."""
    t = clf.tree_; K, b = E.K, E.b; pos = {j: i for i, j in enumerate(used)}; cf = []; cu = []
    def rec(node, mask, val):
        if t.children_left[node] == -1:
            pad = mask; j = 0
            while bin(pad).count('1') < b:
                if not pad >> j & 1: pad |= 1 << j
                j += 1
            f = int(E.lat.rank(b, np.array([pad]))[0]); co = [j for j in range(K) if pad >> j & 1]
            for uu in range(1 << b):
                if all(((uu >> i) & 1) == (val >> c & 1) for i, c in enumerate(co) if mask >> c & 1):
                    cf.append(f); cu.append(uu)
            return
        f = int(t.feature[node])
        if f not in pos: return rec(t.children_left[node], mask, val)
        i = pos[f]
        if mask >> i & 1:
            return rec(t.children_right[node] if val >> i & 1 else t.children_left[node], mask, val)
        rec(t.children_left[node], mask | (1 << i), val); rec(t.children_right[node], mask | (1 << i), val | (1 << i))
    rec(0, 0, 0)
    return (np.array(cf, np.int64), np.array(cu, np.int64))


def analyse(K, b, cube, d, order, tree_cells=None, verbose=False, time_budget=None):
    """Model-based constants at `cube` (which must lie in the order-k model), relative to the variance of t."""
    E = ModelEngine(K, b, cube, d, order); forms = [E.form_interview(f) for f in range(E.L)]
    fx = E.design(1, forms); br = E.design(b, forms + ([tree_cells] if tree_cells is not None else []), verbose=verbose, time_budget=time_budget)
    out = dict(order=order, p=E.p, var=E.var, delta=E.delta, full=E.W_full / E.var, fixed=fx['value'] / E.var, fixed_lower=fx['lower'] / E.var,
               branch=br['value'] / E.var, branch_lower=br['lower'] / E.var, branch_interviews=int(np.sum(br['q'] > 1e-6)), branch_iterations=br['iterations'])
    if tree_cells is not None:
        ft = E.value(np.stack([E.info(tree_cells)]), np.ones(1))[0] if np.linalg.norm(E.v) > 1e-13 else 0.0; out['rule_tree'] = ft / E.var if np.isfinite(ft) else None
    return out, E, fx, br


def selftest():
    """With all interactions the model is saturated and the constants are those of capdesign.Engine."""
    rng = np.random.default_rng(1); K, b = 5, 3
    cube = rng.dirichlet(np.ones(2 << K)).reshape(2, 1 << K); grid = bits(K)
    d = np.where(grid[:, 0] == 1, 2.0 * grid[:, 1] - 1, np.where(grid[:, 2] == 1, 2.0 * grid[:, 3] - 1, 2.0 * grid[:, 4] - 1))
    out, E, fx, br = analyse(K, b, cube, d, K + 1)
    E0 = cd.Engine(K, b, cube=cube, dvals=d, dhat=E.dhat, alpha=0.0); forms = [E0.form_interview(f) for f in range(E0.L)]
    Mf = E0.solve(forms)['value']; Mb = E0.colgen(b, forms)['value']
    a = (out['fixed'], out['branch'], (Mf - E0.delta ** 2) / E.var, (Mb - E0.delta ** 2) / E.var)
    print('saturated model: fixed %.6f branch %.6f | engine: fixed %.6f branch %.6f' % a)
    assert abs(a[0] - a[2]) < 1e-4 and abs(a[1] - a[3]) < 1e-4
    cells = rule_interview(E, d); assert E.check_interview(cells)


def design_based_fixed(K, b, cube, d):
    """Design-based (saturated) optimum over the same forms at the same law, relative to Var(t)."""
    lat = cd.Lattice(K, b); E0 = cd.Engine(K, b, cube=cube, dvals=d, dhat=(cd.wht(d) / (1 << K))[lat.allmasks], alpha=0.0)
    sol = E0.solve([E0.form_interview(f) for f in range(E0.L)]); var = E0.second - E0.delta ** 2
    return (sol['value'] - E0.delta ** 2) / var, sol['q']


def run_brfss(root, b, s, shift, orders=(2, 3), budget=1500):
    import budget_trees as bt
    from screening_v14 import splits
    from baselines_v16 import dependent_items
    from sklearn.tree import DecisionTreeClassifier
    t0 = time.time(); seed = 20261108 + s; X, y, names, sex = bt.load('BRFSS', root); m = X.shape[1]
    tr, cal, tgt = splits('BRFSS', X, y, names, sex, seed, shift)
    clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
    used = dependent_items(clf, m); K = len(used); grid = bits(K)
    Xc = np.zeros((1 << K, m), np.int8); Xc[:, used] = grid; d = 2.0 * clf.predict(Xc) - 1
    code = X[tgt][:, used].astype(np.int64) @ (1 << np.arange(K)) + (y[tgt].astype(np.int64) << K)
    emp = 0.99 * np.bincount(code, minlength=2 << K) / len(tgt) + 0.01 / (2 << K)
    row = dict(dataset='BRFSS', b=b, seed=seed, shift=shift, items=K, n_target=int(len(tgt)))
    t = np.r_[-d, d]; row['delta_emp'] = float(emp @ t)
    if K <= b:
        row['trivial'] = True; row['seconds'] = time.time() - t0; return row
    row['design_emp'], _ = design_based_fixed(K, b, emp.reshape(2, 1 << K), d)
    for k in orders:
        P = loglin_fit(emp, k); cube = P.reshape(2, 1 << K)
        E = ModelEngine(K, b, cube, d, k); cells = clf_interview(E, clf, used); assert E.check_interview(cells)
        o, E, fx, br = analyse(K, b, cube, d, k, tree_cells=cells, time_budget=budget)
        o['design_fixed_at_fit'], qd = design_based_fixed(K, b, cube, d)  # design-based ratio at the fitted law (branching = 1)
        o['model_on_design_forms'] = E.value(fx['Gs'], qd)[0] / E.var     # efficient model-based analysis of design-optimal forms
        o['kl_emp_fit'] = float(np.sum(emp * np.log(emp / P))); o['delta_fit'] = E.delta
        row[f'order{k}'] = o
    row['seconds'] = time.time() - t0
    return row


def address_cube(b):
    """Address contrast on a = b - 1 address bits and 2^a data bits; uniform profiles, independent fair label."""
    a = b - 1; K = a + (1 << a); grid = bits(K); addr = grid[:, :a] @ (1 << np.arange(a))
    d = 1.0 - 2.0 * grid[np.arange(1 << K), a + addr]; cube = np.full((2, 1 << K), 1.0 / (2 << K))
    return K, cube, d


def run_address(b, orders):
    K, cube, d = address_cube(b); out = dict(b=b, items=K, design_fixed=design_based_fixed(K, b, cube, d)[0])
    E = ModelEngine(K, b, cube, d, 1); cells = rule_interview(E, d)
    for k in orders:
        t0 = time.time(); o, *_ = analyse(K, b, cube, d, k, tree_cells=cells, time_budget=1500); o['seconds'] = time.time() - t0; out[f'order{k}'] = o
        print('address b=%d order %d: p %d full %.4f fixed %.4f branch %.4f [lower %.4f] ratio %.4f rule tree %s (%.0fs)' % (b, k, o['p'], o['full'], o['fixed'], o['branch'], o['branch_lower'], o['fixed'] / o['branch'], o.get('rule_tree'), o['seconds']), flush=True)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--selftest', action='store_true'); p.add_argument('--data'); p.add_argument('--out')
    p.add_argument('--bs', default='4,5,6'); p.add_argument('--workers', type=int, default=1); p.add_argument('--address', default=''); p.add_argument('--budget', type=float, default=1500)
    a = p.parse_args()
    if a.selftest: selftest(); sys.exit(0)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.address:
        for spec in a.address.split(';'):
            b, orders = spec.split(':'); dest = out / f'address_b{b}.json'
            if not dest.exists(): dest.write_text(json.dumps(run_address(int(b), [int(k) for k in orders.split(',')]), indent=1, default=float))
        sys.exit(0)
    tasks = [(int(b), s, sh) for b in a.bs.split(',') for sh in (False, True) for s in range(3)]
    tasks = [t for t in tasks if not (out / f'BRFSS_b{t[0]}_{"shift" if t[2] else "iid"}_{t[1]}.json').exists()]
    def go(t):
        r = run_brfss(a.data, *t, budget=a.budget); (out / f'BRFSS_b{t[0]}_{"shift" if t[2] else "iid"}_{t[1]}.json').write_text(json.dumps(r, indent=1, default=float)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                if r.get('trivial'): print(t, 'items', r['items'], 'trivial', flush=True); continue
                print(t, 'items %d design(emp) %.3f' % (r['items'], r['design_emp']), ' | '.join('k=%d: design@fit %.3f model fixed %.3f branch %.3f ratio %.3f full %.3f tree %.3f desforms %.3f' % (k, o['design_fixed_at_fit'], o['fixed'], o['branch'], o['fixed'] / o['branch'], o['full'], o['rule_tree'] or float('nan'), o['model_on_design_forms']) for k, o in ((2, r['order2']), (3, r['order3']))), '%.0fs' % r['seconds'], flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1500:], flush=True)
