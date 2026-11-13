"""Items 1 and 2: definition/identity checks and part (a)."""
import itertools, math, sys
import numpy as np
from core import *

rng = np.random.default_rng(7)


def random_contrast(st, m, deg):
    sets = [A for r in range(0, deg + 1) for A in itertools.combinations(range(m), r)]
    X = chars(st, m, sets)
    return X @ rng.normal(size=len(sets))


def tangent_full(P, n):
    # basis of L^2_0(P): scores of the simplex parametrisation P + U theta  ->  U_i / P
    U = np.linalg.svd(np.ones((1, n)))[2][1:].T  # orthonormal, zero-sum columns
    return U / P[:, None]


def run_item1(m=3, b=2, reps=4):
    st = states(m); n = len(st)
    forms = [form_keys(S, st) for S in itertools.combinations(range(m), b)]
    trees = [tree_keys(t, st) for t in padded_trees(m, b)]
    for rep in range(reps):
        P = rng.dirichlet(np.ones(n) * 2)
        d = random_contrast(st, m, b)
        t = np.array([y for x, y in st]) * d
        Delta = P @ t
        S_full = tangent_full(P, n)
        for name, menu in (('fixed', forms), ('branch', trees)):
            v = S_full.T @ (P * (t - Delta))
            Wfull, _ = solve_W(v, [info_matrix(P, S_full, k) for k in menu])
            Wdes = solve_W_design(P, t, menu)
            # nested random subspaces of L^2_0
            Q = np.linalg.qr(rng.normal(size=(n - 1, n - 1)))[0]
            vals = []
            for p in (3, 7, n - 1):
                Sp = S_full @ Q[:, :p]
                vp = Sp.T @ (P * (t - Delta))
                vals.append(solve_W(vp, [info_matrix(P, Sp, k) for k in menu])[0])
            print(f'item1 rep{rep} {name}: W^(L20)={Wfull:.6f} design-based W={Wdes:.6f}  nested T (p=3,7,full): ' + ' '.join(f'{x:.5f}' for x in vals))
            assert abs(Wfull - Wdes) < 1e-4 * max(1, Wdes)
            assert vals[0] <= vals[1] + 1e-5 and vals[1] <= vals[2] + 1e-5


def run_item2_J(m=5, b=3, reps=300):
    st = states(m); n = len(st)
    worst = np.inf; worst_r = {}
    for rep in range(reps):
        tree = random_tree(rng, m, b)
        # make P possibly not full support
        P = rng.dirichlet(np.ones(n) * 0.3)
        if rep % 3 == 0:
            P[rng.random(n) < 0.3] = 0; P /= P.sum()
        h = rng.normal(size=n)
        kt = tree_keys(tree, st)
        Jt = J(P, h, kt)
        sets = sorted({frozenset(j for j, _ in k[0]) for k in kt}, key=sorted)
        # measurability claims
        for S in sets:
            fk = form_keys(S, st)
            ind = {}
            tr = {}
            for (lf, y), k in zip(kt, fk):
                g = frozenset(j for j, _ in lf) == S
                assert ind.setdefault(k[0], g) == g          # G_S determined by x_S
                if g:
                    assert tr.setdefault(k[0], lf) == lf      # transcript function of x_S on G_S
            # the two inequalities term by term
            g = np.array([frozenset(j for j, _ in lf) == S for lf, y in kt], float)
            cS = cond_exp(P, h, fk); ct = cond_exp(P, h, kt)
            a1 = float((P * cS ** 2).sum()); a2 = float((P * cS ** 2 * g).sum()); a3 = float((P * ct ** 2 * g).sum())
            assert a1 >= a2 - 1e-12 and a2 >= a3 - 1e-12
        Js = sum(J(P, h, form_keys(S, st)) for S in sets)
        if Jt > 1e-12:
            worst = min(worst, Js / Jt)
        # r-round version: follow tree r-1 questions, then guess the completion set below node v
        for r in range(1, b + 1):
            # nodes at depth r-1 identified by prefix of path
            def prefix(x): return leaf(tree, x)[:r - 1]
            compl = {}
            for x, y in st:
                lf = leaf(tree, x)
                compl.setdefault(prefix(x), set()).add(frozenset(j for j, _ in lf[r - 1:]))
            Kr = min(2 ** (b - r), math.comb(m - r, b - r))
            assert max(len(v) for v in compl.values()) <= Kr
            # expected information of the randomized r-round interview: enumerate product of choices is large, so
            # use linearity: J of design = E over independent uniform S_v.  Enumerate when small, else sample exactly per node.
            nodes = sorted(compl, key=str)
            choices = [sorted(compl[v], key=sorted) for v in nodes]
            total = 1
            for c in choices: total *= len(c)
            if total > 400: continue
            Jd = 0.0
            for pick in itertools.product(*choices):
                sel = dict(zip(nodes, pick))
                keys = []
                for x, y in st:
                    v = prefix(x); Sv = sorted(sel[v])
                    keys.append((v, tuple(Sv), tuple(x[j] for j in Sv), y))
                Jd += J(P, h, keys) / total
            if Jt > 1e-12:
                worst_r[r] = min(worst_r.get(r, np.inf), Jd * Kr / Jt)
    print('item2 J-level: min sum_S J_S / J_tau = %.4f (>=1 required)' % worst)
    print('item2 r-round: min K_r * J_design / J_tau by r:', {r: round(v, 4) for r, v in worst_r.items()})
    assert worst >= 1 - 1e-9 and all(v >= 1 - 1e-9 for v in worst_r.values())


def run_item2_W(m=4, b=2, reps=4):
    st = states(m); n = len(st)
    forms = [form_keys(S, st) for S in itertools.combinations(range(m), b)]
    trees = [tree_keys(t, st) for t in padded_trees(m, b)]
    K = min(2 ** (b - 1), math.comb(m - 1, b - 1))
    for rep in range(reps):
        P = rng.dirichlet(np.ones(n) * 2)
        d = random_contrast(st, m, b)
        t = np.array([y for x, y in st]) * d
        Delta = P @ t
        S_full = tangent_full(P, n)
        for p in (4, 10, n - 1):
            Sp = S_full @ np.linalg.qr(rng.normal(size=(n - 1, n - 1)))[0][:, :p]
            vp = Sp.T @ (P * (t - Delta))
            Wf = solve_W(vp, [info_matrix(P, Sp, k) for k in forms])[0]
            Wb = solve_W(vp, [info_matrix(P, Sp, k) for k in trees])[0]
            print(f'item2 W-level rep{rep} dimT={p}: W_fixed={Wf:.5f} W_branch={Wb:.5f} ratio={Wf / Wb:.4f} (K={K})')
            assert Wb <= Wf * (1 + 1e-4) and Wf <= K * Wb * (1 + 1e-4)


if __name__ == '__main__':
    run_item1()
    run_item2_J()
    run_item2_W()
