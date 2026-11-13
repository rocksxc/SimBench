"""Actual constants W^(2)_fixed(P_beta) (b=2,3) and W^(2)_branch(P_beta) (b=2, all padded trees) via
Elfving-type duality:  W = max_u (v'u)^2 / max_iota u' I_iota u  (lower bound for any u; upper bound from a design q)."""
import itertools, sys
import numpy as np, cvxpy as cp
from check_d import setup


def basis(m, k):
    """chi_A on (x,y) in {-1,1}^(m+1), 1<=|A|<=k; state index = x + (ybit << m)."""
    N = 1 << (m + 1)
    bits = 2.0 * ((np.arange(N)[:, None] >> np.arange(m + 1)) & 1) - 1
    cols = []; sets = []
    for r in range(1, k + 1):
        for A in itertools.combinations(range(m + 1), r):
            cols.append(np.prod(bits[:, A], axis=1)); sets.append(A)
    return np.array(cols).T, sets, bits


def B_of_cells(P, Sc, key, ncell):
    """rows E[s 1_c]/sqrt(P(c)) for cells c given by integer key."""
    den = np.bincount(key, weights=P, minlength=ncell)
    num = np.zeros((ncell, Sc.shape[1]))
    np.add.at(num, key, P[:, None] * Sc)
    ok = den > 1e-300
    return num[ok] / np.sqrt(den[ok])[:, None]


def solve(v, Bs, label):
    u = cp.Variable(len(v))
    cons = [cp.norm(B @ u, 2) <= 1 for B in Bs]
    prob = cp.Problem(cp.Maximize(v @ u), cons)
    prob.solve(solver=cp.CLARABEL)
    uu = u.value
    mx = max(float(np.sum((B @ uu) ** 2)) for B in Bs)
    lower = float(v @ uu) ** 2 / mx                     # rigorous lower bound (any u)
    lam = np.array([float(c.dual_value) for c in cons]); q = np.maximum(lam, 0); q = q / q.sum()
    M = sum(qi * (B.T @ B) for qi, B in zip(q, Bs) if qi > 1e-12)
    x = np.linalg.lstsq(M, v, rcond=1e-10)[0]
    resid = float(np.linalg.norm(M @ x - v))
    upper = float(v @ x)
    print(f"   {label}: dual lower bound {lower:.5f}; primal value from recovered design {upper:.5f} (range residual {resid:.1e}; support {int((q>1e-6).sum())})")
    return lower, upper, q


def run(b, betas, k=2, do_branch=False):
    G = setup(b); m, N, D, kap = G['m'], G['N'], G['D'], G['kap']
    S, sets, bits = basis(m, k)
    xidx = np.arange(1 << (m + 1)) & (N - 1); y = bits[:, m]
    t = y * G['d'][xidx]
    gx = G['g'][xidx].astype(np.int64); ybit = (np.arange(1 << (m + 1)) >> m).astype(np.int64)
    forms = list(itertools.combinations(range(m), b))
    fkeys = []
    for F in forms:
        key = ybit.copy()
        for i, c in enumerate(F): key |= gx[:, c] << (i + 1)
        fkeys.append(key)
    tkeys = []
    if do_branch:  # all padded depth-b trees for b=2
        assert b == 2
        for r in range(m):
            others = [c for c in range(m) if c != r]
            for c0 in others:
                for c1 in others:
                    child = np.where(gx[:, r] == 0, gx[:, c0], gx[:, c1])
                    tkeys.append(ybit | (gx[:, r] << 1) | (child << 2))
    for beta in betas:
        w = np.exp(beta * (G['H'] - G['H'].max())); Px = w / w.sum(); P = np.r_[Px, Px] / 2
        Delta = float(P @ t); Sc = S - P @ S
        v = (P * (t - Delta)) @ Sc
        print(f"b={b} k={k} beta={beta}: Delta={Delta:.2e} Var(t)={float(P@(t-Delta)**2):.5f}  D/b={D/b:.4f}  (2D-b)/b={(2*D-b)/b:.4f}")
        Bs = [B_of_cells(P, Sc, key, 1 << (b + 1)) for key in fkeys]
        lf, uf, q = solve(v, Bs, "fixed ")
        top = np.argsort(-q)[:4]
        names = [f"a{i}" for i in range(kap)] + [f"s{j}" for j in range(D)] + [f"z{j}" for j in range(D)] + [f"p{j}" for j in range(D)]
        print("      top forms:", [([names[c] for c in forms[i]], round(float(q[i]), 3)) for i in top])
        if do_branch:
            Bt = [B_of_cells(P, Sc, key, 1 << (b + 1)) for key in tkeys]
            lb, ub, _ = solve(v, Bt, "branch")
            print(f"      ratio fixed/branch in [{lf/ub:.4f}, {uf/lb:.4f}]")


if __name__ == '__main__':
    which = sys.argv[1]
    if which == '2': run(2, [0, 1, 2, 4, 8], do_branch=True)
    if which == '3': run(3, [0, 2, 4, 6, 8, 10])
    if which == '3k3': run(3, [6], k=3)
