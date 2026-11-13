"""Independent check of thm:augment(b): address contrast, forms of size b+c.
(1) brute-force energy of every form under the uniform law; (2) exact programs (own cvxpy formulation, pointwise constraints)."""
import sys, itertools, time
import numpy as np, scipy.sparse as sp, cvxpy as cp

def address(kappa):
    D = 1 << kappa; m = kappa + D
    X = ((np.arange(1 << m)[:, None] >> np.arange(m)) & 1)
    a = X[:, :kappa] @ (1 << np.arange(kappa)) if kappa else np.zeros(1 << m, int)
    d = 2.0 * X[np.arange(1 << m), kappa + a] - 1
    return m, X, d

def jc(c, b):
    j = 0
    while j + 1 <= b - 1 and 2 ** (j + 2) - (j + 1) - 2 <= c: j += 1
    return j

def energies(m, X, d, B, mu=None):
    mu = np.full(1 << m, 1.0 / (1 << m)) if mu is None else mu
    out = {}
    for T in itertools.combinations(range(m), B):
        code = X[:, list(T)] @ (1 << np.arange(B))
        num = np.bincount(code, weights=mu * d, minlength=1 << B); den = np.bincount(code, weights=mu, minlength=1 << B)
        out[T] = float(np.sum(num ** 2 / np.maximum(den, 1e-300)))
    return out

def program(m, X, tvals, P, B, worst=False, forms=None):
    """min over designs on forms of size B of E_P[H^2] (worst=False) or max_x sum g^2/q (worst=True).
    tvals: list of target vectors (one per label value), P: list of masses per label value (each over 2^m profiles)."""
    forms = list(itertools.combinations(range(m), B)) if forms is None else forms
    n = 1 << m; C = 1 << B; L = len(forms); nl = len(tvals)
    codes = np.stack([X[:, list(T)] @ (1 << np.arange(B)) for T in forms])  # L x n
    rows = np.tile(np.arange(n), L); cols = (np.arange(L)[:, None] * C + codes).ravel()
    A = sp.csr_matrix((np.ones(L * n), (rows, cols)), shape=(n, L * C))
    q = cp.Variable(L, nonneg=True); cons = [cp.sum(q) == 1]
    Q = cp.reshape(cp.vstack([q] * C), (L * C,), order='F') if False else (sp.kron(sp.eye(L), np.ones((C, 1))).tocsr() @ q)
    obj = 0; us = []
    for z in range(nl):
        g = cp.Variable(L * C); u = cp.Variable(L * C, nonneg=True)
        cons += [A @ g == tvals[z], cp.SOC(Q + u, cp.vstack([2 * g, Q - u]), axis=0)]
        if worst: us.append(u)
        else:
            mass = np.concatenate([np.bincount(codes[l], weights=P[z], minlength=C) for l in range(L)])
            obj = obj + mass @ u
    if worst:
        tt = cp.Variable()
        for u in us: cons.append(A @ u <= tt)
        obj = tt
    prob = cp.Problem(cp.Minimize(obj), cons); prob.solve(solver='CLARABEL')
    return prob.value

if __name__ == '__main__':
    bmax = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for b in range(1, bmax + 1):
        kappa = b - 1; D = 1 << kappa; m, X, d = address(kappa); n = 1 << m
        for c in range(0, D):
            B = b + c; t0 = time.time()
            en = energies(m, X, d, B); emax = max(en.values())
            # check formula w 2^{s-2kappa} for every form
            dev = max(abs(e - sum(1 for i in T if i >= kappa) * 2.0 ** (sum(1 for i in T if i < kappa) - 2 * kappa)) for T, e in en.items())
            j = jc(c, b); Kp = 2 ** (b - 1 - j)
            line = 'b %d c %d B %d forms %d: max energy %.6f (claim (c+1)/D = %.6f), formula dev %.1e; lower D/(c+1) = %.4f, K+ = %d, K+/(lower) = %.3f, 2^{b+1}/(c+3) = %.3f' % (b, c, B, len(en), emax, (c + 1) / D, dev, D / (c + 1), Kp, Kp * (c + 1) / D, 2 ** (b + 1) / (c + 3))
            if B < m and len(en) * (1 << B) <= 60000:
                mu = np.full(n, 1.0 / n)
                W = program(m, X, [d], [mu], B)
                line += '; W_fixed(uniform, indep. label) = %.5f' % W
                if n <= 64 or (n <= 2048 and len(en) * (1 << B) <= 16000):
                    V = program(m, X, [d], None, B, worst=True); line += '; V_fixed = %.5f' % V
                if n <= 64:
                    # label noise: Y = d*xi, P(xi=1)=p ; t = xi ; label-dependent tables
                    for p in (0.8, 0.97):
                        P1 = np.where(d > 0, p, 1 - p) / n; P0 = np.where(d > 0, 1 - p, p) / n   # Y=+1, Y=-1
                        M = program(m, X, [d, -d], [P1, P0], B); Delta = 2 * p - 1; s2 = 1 - Delta ** 2
                        line += '; p=%.2f W/sigma^2 = %.5f' % (p, (M - Delta ** 2) / s2)
            elif B >= m: line += '; full form: ratio 1'
            print(line, '[%.0fs]' % (time.time() - t0), flush=True)
