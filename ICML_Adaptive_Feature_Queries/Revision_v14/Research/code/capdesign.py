"""Fourier-restricted engine for capped acquisition designs (v14).

An interview is a partition of the profile cube {0,1}^m into cells (T, u): T is a set of exactly b
coordinates (an element of the form table) and u a pattern on T (bit i <-> i-th smallest coordinate).
Pointwise unbiasedness sum_cells g = t is imposed on the Fourier coefficients of degree <= b, which is
exact because every cell indicator has degree <= b. Cell masses come from records (a target law) mixed
with a uniform mass alpha over profiles and labels, so the 2^m cube is never enumerated.

Classes: r = 1 fixed forms; 1 < r < b r-round interviews (batches, each chosen from earlier answers);
r = b branching (depth-b trees). Pricing is exact over the whole class by dynamic programming over the
subset lattice; the dual witness of a restricted master gives a certified lower bound (Theorem 4, last
display), the master value an upper bound.
"""
import warnings
from functools import lru_cache
from itertools import combinations
from math import comb
import numpy as np
import scipy.sparse as sp
import cvxpy as cp


def wht(a):
    """Unnormalized Walsh-Hadamard transform along the last axis: out[..., u] = sum_s a[..., s] (-1)^{|u&s|}."""
    a = np.array(a, dtype=float, copy=True); n = a.shape[-1]; h = 1
    lead = a.shape[:-1]
    while h < n:
        a = a.reshape(lead + (n // (2 * h), 2, h))
        x = a[..., 0, :].copy(); y = a[..., 1, :].copy()
        a[..., 0, :] = x + y; a[..., 1, :] = x - y
        a = a.reshape(lead + (n,)); h *= 2
    return a


@lru_cache(maxsize=None)
def pext_table(k, s):
    """For local subset s of [k], map each pattern u in [2^k) to its compressed restriction to s."""
    pos = [i for i in range(k) if s >> i & 1]
    out = np.zeros(1 << k, dtype=np.int64)
    for u in range(1 << k):
        out[u] = sum(((u >> p) & 1) << j for j, p in enumerate(pos))
    return out


class Lattice:
    """All subsets of [m] with at most b elements, grouped by size and sorted by bitmask."""
    def __init__(self, m, b):
        self.m, self.b = m, b
        self.sets, self.masks = [], []
        for j in range(b + 1):
            S = np.zeros((1, 0), np.int64) if j == 0 else np.array(list(combinations(range(m), j)), dtype=np.int64)
            mk = (np.left_shift(1, S)).sum(1) if j else np.zeros(1, np.int64)
            o = np.argsort(mk, kind='stable'); self.sets.append(S[o]); self.masks.append(mk[o])
        self.allmasks = np.concatenate(self.masks)
        self.order = np.argsort(self.allmasks, kind='stable'); self.sorted_all = self.allmasks[self.order]
        self.offsets = np.r_[0, np.cumsum([len(x) for x in self.masks])]
        self.nterms = int(self.offsets[-1])

    def rank(self, j, masks):
        return np.searchsorted(self.masks[j], masks)

    def term(self, masks):
        """Global term index (size-major) of arbitrary masks of size <= b."""
        return self.order[np.searchsorted(self.sorted_all, masks)]


class Engine:
    def __init__(self, m, b, X=None, y=None, w=None, alpha=0.01, cube=None, dvals=None, dhat=None):
        """X: (N, m) 0/1 records, y: (N,) 0/1 labels, w: record weights (default 1). Alternatively cube:
        (2, 2^m) law over (label, profile) for small m (then X, y unused). dvals: contrast at the records
        (or on the cube); dhat: Fourier coefficients of d on all terms of size <= b (size-major order)."""
        self.m, self.b, self.alpha = m, b, alpha
        self.lat = Lattice(m, b); lat = self.lat
        self.forms = lat.sets[b]; self.fmask = lat.masks[b]; self.L = len(self.forms); C = 1 << b; self.C = C
        sbits = np.array([[(s >> i) & 1 for i in range(b)] for s in range(C)], dtype=np.int64)  # C x b
        submask = (sbits[None, :, :] * np.left_shift(1, self.forms)[:, None, :]).sum(2)  # L x C global masks
        self.sub = lat.term(submask)  # L x C term indices
        self.sign = np.array([[(-1) ** bin(u & s).count('1') for s in range(C)] for u in range(C)], float)  # [u, s]
        # cell masses and contrast sums
        P = np.zeros((2, self.L, C)); Sd = np.zeros((2, self.L, C))
        if cube is not None:
            grid = ((np.arange(1 << m)[:, None] >> np.arange(m)) & 1).astype(np.int64)
            dv = np.asarray(dvals, float)
            for f in range(self.L):
                codes = grid[:, self.forms[f]] @ (1 << np.arange(b))
                for z in range(2):
                    P[z, f] = np.bincount(codes, weights=cube[z], minlength=C)
                    Sd[z, f] = np.bincount(codes, weights=cube[z] * dv, minlength=C)
            self.emp_second = float(np.sum(cube * dv[None, :] ** 2)); self.emp_delta = float(np.sum(cube[1] * dv) - np.sum(cube[0] * dv))
        else:
            X = np.asarray(X, np.int64); y = np.asarray(y, np.int64); N = len(y)
            w = np.ones(N) if w is None else np.asarray(w, float); w = w / w.sum(); dv = np.asarray(dvals, float)
            key = X @ (1 << np.arange(m)) * 2 + y  # aggregate identical records
            uk, inv = np.unique(key, return_inverse=True)
            ww = np.bincount(inv, weights=w); wd = np.bincount(inv, weights=w * dv)
            ux = ((uk[:, None] >> 1) >> np.arange(m)) & 1; uy = uk & 1
            pw = 1 << np.arange(b)
            for f in range(self.L):
                codes = ux[:, self.forms[f]] @ pw
                for z in range(2):
                    sel = uy == z
                    P[z, f] = np.bincount(codes[sel], weights=ww[sel], minlength=C)
                    Sd[z, f] = np.bincount(codes[sel], weights=wd[sel], minlength=C)
            self.emp_second = float(np.sum(w * dv ** 2)); self.emp_delta = float(np.sum(w * (2 * y - 1) * dv))
        self.dhat = np.asarray(dhat, float)
        unif = 1.0 / (2 * C)
        # uniform part of sum_{x in cell} d(x) U(x)/2: 2^-b sum_{s} dhat(S(T,s)) (-1)^{|u&s|} / 2
        Ud = (self.dhat[self.sub] @ self.sign.T) / C / 2  # L x C  (sign is symmetric)
        self.P = (1 - alpha) * P + alpha * unif
        self.Sd = (1 - alpha) * Sd + alpha * np.stack([Ud, Ud])
        self.second = (1 - alpha) * self.emp_second + alpha * float(np.sum(self.dhat ** 2))
        self.delta = (1 - alpha) * self.emp_delta
        self.that = np.stack([-self.dhat, self.dhat])  # Fourier coefficients of t_z = (2z-1) d
        self._lev = None

    # ------------------------------------------------------------------ diagnostics
    def form_energy_t(self):
        """Energy of every form under the witness h = t (unnormalized), used to seed large masters."""
        return np.sum(np.divide(self.Sd ** 2, self.P), axis=(0, 2))

    def gamma(self):
        """Gamma_P = max_T E[E[t|X_T,Y]^2] / E[t^2] (energy of the witness h = t)."""
        e = np.sum(np.divide(self.Sd ** 2, self.P), axis=(0, 2))
        f = int(np.argmax(e)); return float(e[f] / self.second), f

    # ------------------------------------------------------------------ interviews
    def form_interview(self, f):
        return (np.full(self.C, f, np.int64), np.arange(self.C, dtype=np.int64))

    def interview_energy(self, cells, e):
        return float(e[cells[0], cells[1]].sum())

    # ------------------------------------------------------------------ master problem
    def solve(self, interviews, beta=0.0, P=None, tol=1e-10, repair=True):
        P = self.P if P is None else P
        fidx = np.concatenate([c[0] for c in interviews]); uu = np.concatenate([c[1] for c in interviews])
        sizes = np.array([len(c[0]) for c in interviews]); group = np.repeat(np.arange(len(interviews)), sizes)
        Mc = len(fidx); C = self.C
        rows_all = self.sub[fidx]  # Mc x C
        covered, rloc = np.unique(rows_all, return_inverse=True); rloc = rloc.reshape(rows_all.shape)
        unc = np.setdiff1d(np.arange(self.lat.nterms), covered)
        assert np.max(np.abs(self.dhat[unc]), initial=0) < 1e-10, 'contrast not representable by these interviews'
        vals = self.sign[uu] / C  # Mc x C: column entries 2^-b (-1)^{|u&s|}
        F = sp.csc_matrix((vals.ravel(), (rloc.ravel(), np.repeat(np.arange(Mc), C))), shape=(len(covered), Mc))
        scale = max(np.max(np.abs(self.dhat)), 1e-12)
        coef = self.dhat[covered] / scale
        mass = P[:, fidx, uu]
        L = len(interviews)
        q = cp.Variable(L, nonneg=True); g = cp.Variable((2, Mc)); uvar = cp.Variable((2, Mc), nonneg=True)
        Q = sp.csc_matrix((np.ones(Mc), (np.arange(Mc), group)), shape=(Mc, L)) @ q
        eq = [F @ g[z] == (2 * z - 1) * coef for z in range(2)]
        cons = [cp.sum(q) == 1, q >= beta / L, *eq]
        for z in range(2):
            cons.append(cp.SOC(Q + uvar[z], cp.vstack([2 * g[z], Q - uvar[z]]), axis=0))
        prob = cp.Problem(cp.Minimize(cp.sum(cp.multiply(mass, uvar))), cons)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            prob.solve(solver='CLARABEL', tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol, max_iter=500)
        if prob.status not in ['optimal', 'optimal_inaccurate']:
            raise RuntimeError(prob.status)
        eta = np.zeros((2, self.lat.nterms))
        for z in range(2):
            eta[z, covered] = -eq[z].dual_value / 2 * scale
        qq = np.maximum(q.value, 1e-15); qq = qq / qq.sum(); gg = g.value.copy()
        if not repair:  # inside column generation: the solver's feasibility (about 1e-10) is enough to steer
            gg = gg * scale
            value = float(np.sum(mass * gg ** 2 / qq[group][None, :]))
            return dict(value=value, q=qq, g=gg, eta=eta, group=group, fidx=fidx, u=uu, status=prob.status, repaired=False)
        # exact repair of the linear constraints, weighted by the interview probabilities so that the correction
        # minimizes the added second moment sum delta^2/q (cells of unused interviews receive no correction)
        Dq = sp.diags(qq[group])
        if len(covered) <= 400:
            FD = (F @ Dq).tocsc(); FF = (FD @ F.T).toarray()
            for z in range(2):
                gg[z] += Dq @ (F.T @ np.linalg.lstsq(FF, (2 * z - 1) * coef - F @ gg[z], rcond=None)[0])
        else:  # large problems: weighted least-norm correction by LSQR on F D^{1/2}
            from scipy.sparse.linalg import lsqr
            Dh = sp.diags(np.sqrt(qq[group])); FDh = (F @ Dh).tocsr()
            for z in range(2):
                yv = lsqr(FDh, (2 * z - 1) * coef - F @ gg[z], atol=1e-14, btol=1e-14, iter_lim=20000)[0]
                gg[z] += Dh @ yv
        res = max(np.max(np.abs(F @ gg[z] - (2 * z - 1) * coef)) for z in range(2))
        assert res < 1e-7, res
        gg = gg * scale
        value = float(np.sum(mass * gg ** 2 / qq[group][None, :]))
        return dict(value=value, q=qq, g=gg, eta=eta, group=group, fidx=fidx, u=uu, status=prob.status, repaired=True)

    def second_moment(self, sol, P=None):
        P = self.P if P is None else P
        return float(np.sum(P[:, sol['fidx'], sol['u']] * sol['g'] ** 2 / sol['q'][sol['group']][None, :]))

    # ------------------------------------------------------------------ pricing
    def cell_energy(self, eta):
        psi = np.stack([wht(eta[z][self.sub]) for z in range(2)]) / self.C  # 2 x L x C
        return np.sum(psi ** 2 / self.P, axis=0)

    def levels(self):
        """Per subset size j: subset masks, and for every (B of size k, local subset s) the ranks of B|s."""
        if self._lev is None:
            lat = self.lat; lev = {}
            for k in range(1, self.b + 1):
                Bs = lat.sets[k]
                for s in range(1 << k):
                    j = bin(s).count('1')
                    if j == k: continue
                    sub = (np.left_shift(1, Bs) * np.array([(s >> i) & 1 for i in range(k)])[None, :]).sum(1)
                    lev[(k, s)] = (j, lat.rank(j, sub), pext_table(k, s))
            self._lev = lev
        return self._lev

    def dp_values(self, e, r):
        """V[r'][j]: (C(m,j), 2^j) best energy from a partial assignment with r' rounds left, r' = 1..r.
        Leaves are full b-sets (V_b = e). With r = b and singleton batches this is the tree DP."""
        lat = self.lat; b = self.b; lev = self.levels()
        V = {}
        for rr in range(1, r + 1):
            cur = {b: e}
            for j in range(b - 1, -1, -1):
                cur[j] = np.full((len(lat.masks[j]), 1 << j), -np.inf)
            for k in range(b, 0, -1):
                src = e if k == b else (V[rr - 1][k] if rr > 1 else None)
                if src is None: continue
                for s in range(1 << k):
                    if (k, s) not in lev: continue
                    j, rA, tab = lev[(k, s)]
                    Mmat = np.zeros((1 << k, 1 << j)); Mmat[np.arange(1 << k), tab] = 1.0
                    cand = src @ Mmat
                    np.maximum.at(cur[j], rA, cand)
            V[rr] = cur
        return V

    def tree_values(self, e):
        """Exact DP over all depth-b trees (one question per round)."""
        lat = self.lat; b = self.b; lev = self.levels()
        cur = {b: e}
        for j in range(b - 1, -1, -1):
            k = j + 1; acc = np.full((len(lat.masks[j]), 1 << j), -np.inf)
            for s in range(1 << k):
                if bin(s).count('1') != j: continue
                jj, rA, tab = lev[(k, s)]
                Mmat = np.zeros((1 << k, 1 << j)); Mmat[np.arange(1 << k), tab] = 1.0
                np.maximum.at(acc, rA, cur[k] @ Mmat)
            cur[j] = acc
        return cur

    # ------------------------------------------------------------------ reconstruction
    def _supersets(self, Amask, j, ks):
        """All supersets B of A with |B| in ks, as (k, ranks, masks)."""
        lat = self.lat; out = []
        free = [i for i in range(self.m) if not (Amask >> i) & 1]
        for k in ks:
            if k - j < 0 or k - j > len(free): continue
            add = np.zeros((1, 0), np.int64) if k == j else np.array(list(combinations(free, k - j)), dtype=np.int64)
            mk = Amask + (np.left_shift(1, add)).sum(1) if k > j else np.array([Amask])
            out.append((k, lat.rank(k, mk), mk))
        return out

    def _ext(self, Amask, a, Bmask):
        """Patterns u on B (local order) whose restriction to A equals a (A's local order)."""
        Bco = [i for i in range(self.m) if (Bmask >> i) & 1]
        s = sum(1 << p for p, c in enumerate(Bco) if (Amask >> c) & 1)
        tab = pext_table(len(Bco), s)
        return np.flatnonzero(tab == a), s

    def build(self, Amask, a, rleft, V, e, tree=False):
        """Reconstruct an optimal interview from partial assignment (A, a) with rleft rounds left.
        Returns cells (form index array, pattern array)."""
        lat = self.lat; b = self.b; j = bin(Amask).count('1')
        if j == b:
            return (np.array([lat.rank(b, np.array([Amask]))[0]]), np.array([a]))
        best = (-np.inf, None)
        if tree:
            ks = [j + 1]
        elif rleft == 1:
            ks = [b]
        else:
            ks = list(range(j + 1, b + 1))
        Acoords = np.array([c for c in range(self.m) if (Amask >> c) & 1], dtype=np.int64)
        free = [c for c in range(self.m) if not (Amask >> c) & 1]
        for k in ks:
            if k - j < 0 or k - j > len(free): continue
            Vk = V[k] if tree else (e if k == b else V[rleft - 1][k])
            add = np.zeros((1, 0), np.int64) if k == j else np.array(list(combinations(free, k - j)), dtype=np.int64)
            mks = Amask + np.left_shift(1, add).sum(1); ranks = lat.rank(k, mks)
            # local positions of A's coordinates inside each candidate B (B sorted)
            pos = np.arange(j)[None, :] + (add[:, :, None] < Acoords[None, None, :]).sum(1) if j else np.zeros((len(add), 0), np.int64)
            svec = np.left_shift(1, pos).sum(1) if j else np.zeros(len(add), np.int64)
            for sv in np.unique(svec):
                sel = np.flatnonzero(svec == sv); us = np.flatnonzero(pext_table(k, int(sv)) == a)
                vals = Vk[ranks[sel]][:, us].sum(1); i = int(np.argmax(vals))
                if vals[i] > best[0]: best = (float(vals[i]), int(mks[sel[i]]))
        Bmask = best[1]; k = bin(Bmask).count('1')
        us, _ = self._ext(Amask, a, Bmask)
        if k == b:
            rk = lat.rank(b, np.array([Bmask]))[0]
            return (np.full(len(us), rk, np.int64), us.astype(np.int64))
        parts = [self.build(Bmask, int(u), None if tree else rleft - 1, V, e, tree) for u in us]
        return (np.concatenate([p[0] for p in parts]), np.concatenate([p[1] for p in parts]))

    # ------------------------------------------------------------------ column generation
    def price(self, r, e, k_add):
        """Exact pricing over the r-round class: (top energy, candidate interviews)."""
        b = self.b
        if r == 1:
            E = e.sum(1); return float(E.max()), [(float(E[f]), self.form_interview(int(f))) for f in np.argsort(-E)[:k_add]]
        if r >= b:
            V = self.tree_values(e); return float(V[0][0, 0]), self._roots(V, e, tree=True, k=k_add)
        V = self.dp_values(e, r); return float(V[r][0][0, 0]), self._roots(V, e, tree=False, k=k_add, r=r)

    def colgen(self, r, start, beta=0.0, P=None, max_iter=400, tol=1e-7, k_add=6, verbose=False, smooth=0.5, gap=1e-7, prune=0, solver_tol=1e-10):
        """Optimal design over the r-round class (r=1 fixed, r=b branching) at law P (default: target),
        by column generation with Wentges dual smoothing. The witness eta is normalized so that
        <eta, t> = 1; then 1/max_class energy(eta) is a certified lower bound on M for every eta
        (only reported for beta = 0 at the target law)."""
        Pl = self.P if P is None else P
        ints = list(start); hist = []; eta_best = None; lb_best = -np.inf; saveP = self.P
        certify = (beta == 0) and (P is None)
        jensen = self.second if certify else -np.inf  # every pointwise-unbiased design has M >= E_P[t^2]
        n0 = len(ints); idle = [0] * len(ints); best_ub = (np.inf, None, None)
        for it in range(max_iter):
            sol = self.solve(ints, beta, Pl, tol=solver_tol, repair=False); ub = sol['value']
            if ub < best_ub[0]: best_ub = (ub, sol, list(ints))
            if prune and beta == 0:
                idle = [0 if sol['q'][i] > 1e-6 else idle[i] + 1 for i in range(len(ints))]
            nk = float(np.sum(sol['eta'] * self.that)); eta_k = sol['eta'] / nk
            self.P = Pl
            e_k = self.cell_energy(eta_k); cur_k = max(self.interview_energy(c, e_k) for c in ints)
            if eta_best is None or smooth <= 0:
                eta_s = eta_k; e_s = e_k
            else:
                eta_s = smooth * eta_best + (1 - smooth) * eta_k; e_s = self.cell_energy(eta_s)
            top_s, cands = self.price(r, e_s, k_add)
            if 1.0 / top_s > lb_best: lb_best, eta_best = 1.0 / top_s, eta_s
            improving = [(v, c) for v, c in cands if self.interview_energy(c, e_k) > cur_k * (1 + tol)]
            if not improving and eta_s is not eta_k:  # mispricing: price at the master dual itself
                top_k, cands = self.price(r, e_k, k_add)
                if 1.0 / top_k > lb_best: lb_best, eta_best = 1.0 / top_k, eta_k
                improving = [(v, c) for v, c in cands if self.interview_energy(c, e_k) > cur_k * (1 + tol)]
            self.P = saveP
            lower = max(lb_best, jensen) if certify else float('nan')
            hist.append((ub, lower, cur_k))
            if verbose: print(it, len(ints), ub, lower, flush=True)
            if not improving or (certify and ub - lower <= gap * ub):
                break
            if prune and beta == 0 and it % 3 == 2:
                keep = [i for i in range(len(ints)) if idle[i] < prune]
                ints = [ints[i] for i in keep]; idle = [idle[i] for i in keep]
            for v, c in improving:
                ints.append(c); idle.append(0)
        if best_ub[1] is not None and best_ub[0] < sol['value']:
            ints = best_ub[2]
        sol = self.solve(ints, beta, Pl, tol=solver_tol, repair=True)  # exact feasibility for the reported design
        upper = sol['value']
        return dict(value=sol['value'], upper=upper, lower=(max(lb_best, jensen) if certify else float('nan')), interviews=ints, sol=sol,
                    hist=hist, iterations=len(hist), optimal=not improving)

    def check_interview(self, cells):
        """Small m only: every profile lies in exactly one cell (cells partition the cube)."""
        m, b = self.m, self.b
        grid = ((np.arange(1 << m)[:, None] >> np.arange(m)) & 1).astype(np.int64)
        hit = np.zeros(1 << m, int)
        for f, u in zip(cells[0], cells[1]):
            T = self.forms[f]; code = grid[:, T] @ (1 << np.arange(b)); hit += (code == u)
        return bool(np.all(hit == 1))

    def _roots(self, V, e, tree, k=6, r=None):
        """Best interviews by first batch: evaluate every first batch B (size-limited) and reconstruct the top k."""
        b = self.b; lat = self.lat; out = []
        if tree:
            ks = [1]
        else:
            ks = list(range(1, b + 1))
        scored = []
        for kk in ks:
            Vk = e if kk == b else (V[kk] if tree else V[r - 1][kk])
            tot = Vk.sum(1)
            for rk in np.argsort(-tot)[:k]:
                scored.append((float(tot[rk]), kk, int(lat.masks[kk][rk])))
        scored.sort(key=lambda t: -t[0])
        for val, kk, mk in scored[:k]:
            if kk == b:
                f = int(self.lat.rank(b, np.array([mk]))[0]); out.append((val, self.form_interview(f)))
                continue
            parts = [self.build(mk, u, (r - 1) if not tree else None, V, e, tree) for u in range(1 << kk)]
            out.append((val, (np.concatenate([p[0] for p in parts]), np.concatenate([p[1] for p in parts]))))
        return out


def tree_fourier(clf, lat, m, values=None):
    """Fourier coefficients (size-major term order of lat) and leaf structure of a fitted sklearn tree on 0/1
    features (thresholds at 0.5). values: per-leaf contrast value (default: 2*class-1 decision in {-1,1})."""
    t = clf.tree_; dhat = np.zeros(lat.nterms); leaves = []
    def rec(node, lits):
        if t.children_left[node] == -1:
            if values is None:
                v = 2.0 * float(np.argmax(t.value[node][0])) - 1.0
            else:
                v = values[node]
            leaves.append((node, list(lits), v))
            return
        f = int(t.feature[node])
        rec(t.children_left[node], lits + [(f, 0)]); rec(t.children_right[node], lits + [(f, 1)])
    rec(0, [])
    for node, lits, v in leaves:
        k = len(lits); fs = [f for f, _ in lits]; vs = [x for _, x in lits]
        for s in range(1 << k):
            mk = sum(1 << fs[i] for i in range(k) if s >> i & 1)
            sg = (-1) ** sum(vs[i] for i in range(k) if s >> i & 1)
            dhat[lat.term(np.array([mk]))[0]] += v * sg / (1 << k)
    return dhat, leaves
