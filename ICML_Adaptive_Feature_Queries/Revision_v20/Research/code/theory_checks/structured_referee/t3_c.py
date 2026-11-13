"""Item 4: part (c), address contrast at the uniform law with independent uniform label."""
import itertools, math, sys
from functools import lru_cache
import numpy as np
from core import *

rng = np.random.default_rng(3)


def N(s, j): return sum(math.comb(s, i) for i in range(j + 1))
def L(b, k): return N(b - 1, k - 2) ** 2 / max((b - s) * N(s, k - 2) for s in range(b))


def address_setup(b):
    kap = b - 1; D = 2 ** kap; m = kap + D
    st = states(m)
    addr = lambda x: sum((1 if x[i] == 1 else 0) << i for i in range(kap))
    d = np.array([x[kap + addr(x)] for x, y in st], float)
    t = d * np.array([y for x, y in st])
    P = np.full(len(st), 1 / len(st))
    return kap, D, m, st, P, t


def fourier_check(b):
    kap, D, m, st, P, t = address_setup(b)
    allsets = [A for r in range(0, m + 2) for A in itertools.combinations(range(m + 1), r)]
    X = chars(st, m, allsets)
    v = X.T @ (P * t)
    nz = [(A, c) for A, c in zip(allsets, v) if abs(c) > 1e-12]
    ok = all(m in A and sum(1 for j in A if kap <= j < m) == 1 and abs(abs(c) - 2 ** -kap) < 1e-12 for A, c in nz)
    by_k = {k: sum(1 for A, c in nz if len(A) <= k) for k in range(2, b + 2)}
    print(f'b={b}: nonzero coefficients all of form B+{{j}}+{{label}} with |v|=2^-kappa: {ok}; counts by k: {by_k};'
          f' formula D*N(kappa,k-2): {[D * N(kap, k - 2) for k in range(2, b + 2)]}; Delta={P @ t:.1f}, var={P @ (t * t):.1f}')
    assert ok and all(by_k[k] == D * N(kap, k - 2) for k in by_k)


def W_fixed_sym(b, k):
    """Exact fixed-form constant by symmetrisation: min_w sum_i C(kappa,i)^2 / sum_s w_s (b-s) C(s,i)."""
    import cvxpy as cp
    kap = b - 1; D = 2 ** kap
    ss = [s for s in range(0, kap + 1) if b - s <= D]
    w = cp.Variable(len(ss), nonneg=True)
    obj = 0
    for i in range(0, k - 1):
        den = sum(w[a] * (b - s) * math.comb(s, i) for a, s in enumerate(ss))
        obj = obj + math.comb(kap, i) ** 2 * cp.inv_pos(den)
    prob = cp.Problem(cp.Minimize(obj), [cp.sum(w) == 1]); prob.solve(solver='CLARABEL')
    return prob.value, dict(zip(ss, np.round(w.value, 4)))


def W_menu(b, k, menu):
    kap, D, m, st, P, t = address_setup(b)
    sets = sets_upto(m, k)
    X = chars(st, m, sets)
    v = X.T @ (P * t)
    if menu == 'fixed':
        keys = [form_keys(S, st) for S in itertools.combinations(range(m), b)]
    else:
        keys = [tree_keys(tr, st) for tr in padded_trees(m, b)]
    Is = [info_matrix(P, X, kk) for kk in keys]
    if menu == 'fixed':
        assert all(np.abs(I - np.diag(np.diag(I))).max() < 1e-12 for I in Is)   # diagonal information
    return solve_W(v, Is)[0]


def tree_block_check(b, reps=200):
    """Off-diagonal entries of the (data bit x label) block vanish for trees; trace <= b."""
    kap, D, m, st, P, t = address_setup(b)
    sets = [(j, m) for j in range(kap, m)]
    X = chars(st, m, sets)
    worst_off = 0; max_tr = 0
    trees = padded_trees(m, b) if b == 2 else [random_tree(rng, m, b) for _ in range(reps)]
    for tr in trees:
        I = info_matrix(P, X, tree_keys(tr, st))
        worst_off = max(worst_off, np.abs(I - np.diag(np.diag(I))).max()); max_tr = max(max_tr, np.trace(I))
    print(f'b={b}: {len(trees)} trees, max |off-diagonal| of I_vv = {worst_off:.1e}, max trace = {max_tr:.4f} (<= b={b})')
    assert worst_off < 1e-12 and max_tr <= b + 1e-9
    # full T_2 information of a tree is NOT diagonal in general (so the Schur step is needed)
    X2 = chars(st, m, sets_upto(m, 2))
    I2 = info_matrix(P, X2, tree_keys(trees[0], st))
    print('    full T_2 information of a tree diagonal?', bool(np.abs(I2 - np.diag(np.diag(I2))).max() < 1e-12))


def max_tree_energy(b, k):
    """max over depth-b trees of J_tau(t_k), t_k = projection of t on T_k, by DP over subcubes (exact).
    Returns (max energy, <t,t_k>^2 / max energy) = certified lower bound on W^(k)_branch."""
    kap = b - 1; D = 2 ** kap; m = kap + D
    abits = [[(1 if (j >> i) & 1 else -1) for i in range(kap)] for j in range(D)]

    def leaf_energy(fixed):
        fx = dict(fixed)
        A = [i for i in range(kap) if i in fx]
        tot = 0.0
        for j in range(D):
            if kap + j not in fx: continue
            # sum over B subset of A, |B|<=k-2 of prod_{i in B} a_i a_{j,i}
            signs = [fx[i] * abits[j][i] for i in A]
            neg = sum(1 for s in signs if s < 0); pos = len(signs) - neg
            c = sum(math.comb(pos, u) * math.comb(neg, w) * (-1) ** w for u in range(pos + 1) for w in range(neg + 1) if u + w <= k - 2)
            tot += fx[kap + j] * c
        return 2.0 ** (-len(fixed)) * (tot * 2.0 ** -kap) ** 2

    @lru_cache(maxsize=None)
    def V(fixed, r):
        if r == 0: return leaf_energy(fixed)
        fx = dict(fixed); best = -1
        for j in range(m):
            if j in fx: continue
            val = V(tuple(sorted(fixed + ((j, 1),))), r - 1) + V(tuple(sorted(fixed + ((j, -1),))), r - 1)
            best = max(best, val)
        return best
    Jmax = V((), b)
    num = (N(kap, k - 2) / D) ** 2
    return Jmax, num / Jmax


if __name__ == '__main__':
    for b in (2, 3): fourier_check(b)
    print('--- closed forms of L_k(b)')
    for b in range(2, 60):
        assert abs(L(b, 2) - 1 / b) < 1e-12 and abs(L(b, b + 1) - 2 ** (b - 1)) < 1e-6 * 2 ** (b - 1)
        assert max((b - s) * (1 + s) for s in range(b)) == (b + 1) ** 2 // 4
        assert abs(L(b, 3) - b * b / ((b + 1) ** 2 // 4)) < 1e-12 and L(b, 3) < 4
        assert max((b - s) * 2 ** s for s in range(b)) == 2 ** (b - 1)
        for k in range(2, b + 2):
            assert L(b, k) >= N(b - 1, k - 2) / b - 1e-9 >= math.comb(b - 1, k - 2) / b - 1e-9
        s = b // 2; ub = 1 / (b - s) + (b - 1) ** 2 / (s * (b - s))
        assert ub <= 2 / b + 4 - 8 / (b + 1) + 1e-12 < 4 and ub >= L(b, 3) - 1e-12
    print('L_2=1/b, L_3=b^2/floor((b+1)^2/4)<4, L_{b+1}=2^(b-1), L_k>=C(b-1,k-2)/b, k=3 upper bound algebra: OK for b=2..59')
    print('L_3(b), b=2..8:', [round(L(b, 3), 4) for b in range(2, 9)], ' upper bound:', [round(1 / (b - b // 2) + (b - 1) ** 2 / ((b // 2) * (b - b // 2)), 4) for b in range(2, 9)])
    print('--- exact fixed constants by symmetrisation vs L_k(b)')
    for b in range(2, 9):
        row = []
        for k in range(2, b + 2):
            val, w = W_fixed_sym(b, k)
            assert val >= L(b, k) * (1 - 1e-6)
            row.append(f'k={k}: {val:.4f} (L={L(b, k):.4f})')
        print(f'b={b}: ' + '; '.join(row))
    print('--- brute force SDP, all forms / all padded trees')
    for k in (2, 3):
        print(f'b=2 k={k}: fixed={W_menu(2, k, "fixed"):.5f} branch={W_menu(2, k, "branch"):.5f}')
    for k in (2, 3, 4):
        print(f'b=3 k={k}: fixed (all 20 forms, SDP)={W_menu(3, k, "fixed"):.5f}  symmetrised formula={W_fixed_sym(3, k)[0]:.5f}')
    tree_block_check(2); tree_block_check(3)
    print('--- DP: max_tau J_tau(t_k) and certified lower bound <t,t_k>^2/max on W^(k)_branch')
    for b in ([2, 3, 4] + ([5] if '--b5' in sys.argv else [])):
        for k in range(2, b + 2):
            Jm, lb = max_tree_energy(b, k)
            print(f'b={b} k={k}: max_tau J = {Jm:.6f}; lower bound on W_branch^(k) = {lb:.6f}')
