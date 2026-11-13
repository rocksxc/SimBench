import sys, itertools, numpy as np, scipy.sparse as sp, cvxpy as cp
sys.path.insert(0, 'SCRATCH/v21/Research/code')
from capcurve_v21 import fixed_ratio, engine
rng = np.random.default_rng(3)
b = 3; m = 7; n = 1 << m; X = ((np.arange(n)[:, None] >> np.arange(m)) & 1)
last = np.zeros(n, int)
for x in range(n):
    v = 0
    for lvl in range(b):
        a = X[x, v]; last[x] = a
        if lvl < b - 1: v = 2 * v + 1 + a
d = 2.0 * last - 1
P = rng.dirichlet(np.full(2 * n, 0.3)); P = 0.95 * P + 0.05 / (2 * n); P0, P1 = P[:n], P[n:]
Delta = float(P1 @ d - P0 @ d); var = 1 - Delta ** 2; B = 3
forms = list(itertools.combinations(range(m), B)); C = 1 << B; L = len(forms)
codes = np.stack([X[:, list(T)] @ (1 << np.arange(B)) for T in forms])
A = sp.csr_matrix((np.ones(L * n), (np.tile(np.arange(n), L), (np.arange(L)[:, None] * C + codes).ravel())), shape=(n, L * C))
q = cp.Variable(L, nonneg=True); Q = sp.kron(sp.eye(L), np.ones((C, 1))).tocsr() @ q; cons = [cp.sum(q) == 1]; obj = 0; gs = []; masses = []
for tv, Pz in ((d, P1), (-d, P0)):
    g = cp.Variable(L * C); u = cp.Variable(L * C, nonneg=True); gs.append(g)
    cons += [A @ g == tv, cp.SOC(Q + u, cp.vstack([2 * g, Q - u]), axis=0)]
    mass = np.concatenate([np.bincount(codes[l], weights=Pz, minlength=C) for l in range(L)]); masses.append(mass); obj = obj + mass @ u
prob = cp.Problem(cp.Minimize(obj), cons)
for tol in (1e-8, 1e-11):
    prob.solve(solver='CLARABEL', tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol, max_iter=1000)
    qq = np.repeat(np.maximum(q.value, 1e-300), C)
    rec = sum(float(np.sum(masses[z] * gs[z].value ** 2 / qq)) for z in range(2))
    print('tol %g: solver objective ratio %.7f ; recomputed sum mass g^2/q ratio %.7f ; status %s; max constraint violation %.1e' % (tol, (prob.value - Delta ** 2) / var, (rec - Delta ** 2) / var, prob.status, max(np.abs(A @ gs[0].value - d).max(), np.abs(A @ gs[1].value + d).max())))
r, E0 = fixed_ratio(m, B, P, d); print('authors fixed_ratio %.7f' % r)
sol = E0.solve([E0.form_interview(f) for f in range(E0.L)], repair=False); print('authors without repair %.7f' % ((sol['value'] - E0.delta ** 2) / var))
# prune forms with tiny probability, re-solve on the support, and evaluate the design exactly
keep = [l for l in range(L) if q.value[l] > 1e-6]; print('forms kept', len(keep), 'of', L)
Lk = len(keep); Ak = sp.csr_matrix((np.ones(Lk * n), (np.tile(np.arange(n), Lk), (np.arange(Lk)[:, None] * C + codes[keep]).ravel())), shape=(n, Lk * C))
q2 = cp.Variable(Lk, nonneg=True); Q2 = sp.kron(sp.eye(Lk), np.ones((C, 1))).tocsr() @ q2; cons = [cp.sum(q2) == 1]; obj = 0; gs = []; ms = []
for tv, Pz in ((d, P1), (-d, P0)):
    g = cp.Variable(Lk * C); u = cp.Variable(Lk * C, nonneg=True); gs.append(g)
    cons += [Ak @ g == tv, cp.SOC(Q2 + u, cp.vstack([2 * g, Q2 - u]), axis=0)]
    mass = np.concatenate([np.bincount(codes[l], weights=Pz, minlength=C) for l in keep]); ms.append(mass); obj = obj + mass @ u
pr = cp.Problem(cp.Minimize(obj), cons); pr.solve(solver='CLARABEL', tol_gap_abs=1e-10, tol_gap_rel=1e-10, tol_feas=1e-10)
qq = np.repeat(q2.value / q2.value.sum(), C); rec = sum(float(np.sum(ms[z] * gs[z].value ** 2 / qq)) for z in range(2))
print('restricted: objective ratio %.7f, exactly evaluated design ratio %.7f, min q %.2e, violation %.1e' % ((pr.value - Delta ** 2) / var, (rec - Delta ** 2) / var, q2.value.min(), max(np.abs(Ak @ gs[0].value - d).max(), np.abs(Ak @ gs[1].value + d).max())))
print('authors q: number of forms with q<1e-9:', int(np.sum(sol['q'] < 1e-9)), ' contribution of forms with q<1e-6 to their value (ratio units): %.2e' % (float(np.sum((E0.P[:, sol['fidx'], sol['u']] * sol['g'] ** 2 / sol['q'][sol['group']][None, :])[:, sol['q'][sol['group']] < 1e-6])) / var))
