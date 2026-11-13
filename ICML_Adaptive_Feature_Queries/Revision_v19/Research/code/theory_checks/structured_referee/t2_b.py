"""Item 3: part (b) at product laws."""
import itertools, math
import numpy as np
import scipy.linalg as sla
from core import *

rng = np.random.default_rng(11)


def product_law(st, m, pi):
    return np.array([np.prod([pi[j] if v == 1 else 1 - pi[j] for j, v in enumerate(list(x) + [y])]) for x, y in st])


def phis(st, m, pi, sets):
    Z = np.array([list(x) + [y] for x, y in st], float)
    mu = 2 * pi - 1; sd = np.sqrt(1 - mu ** 2)
    F = (Z - mu) / sd
    return np.stack([np.prod(F[:, list(A)], axis=1) for A in sets], axis=1), F


def tangent_check(m=3, k=2):
    """Scores of the hierarchical log-linear model by finite differences at a random law of M_k."""
    st = states(m); n = len(st)
    sets = sets_upto(m, k)
    X = chars(st, m, sets)
    th = rng.normal(size=len(sets)) * 0.4
    def law(th):
        w = np.exp(X @ th); return w / w.sum()
    P = law(th)
    eps = 1e-6
    S = np.stack([(np.log(law(th + eps * e)) - np.log(law(th - eps * e))) / (2 * eps) for e in np.eye(len(sets))], axis=1)
    target = X - P @ X
    print('tangent: max |score - (chi_A - E chi_A)| = %.2e' % np.abs(S - target).max())
    assert np.abs(S - target).max() < 1e-6


def run(m=5, b=3, reps=150, lam=0.15):
    st = states(m); n = len(st)
    worst = {}
    for rep in range(reps):
        pi = rng.uniform(lam, 1 - lam, size=m + 1)
        if rep % 5 == 0: pi = np.where(rng.random(m + 1) < 0.5, lam, 1 - lam)   # extreme marginals
        if rep % 7 == 0: pi = np.full(m + 1, 0.5)
        lam_eff = float(min(pi.min(), (1 - pi).min()))
        P = product_law(st, m, pi)
        tree = random_tree(rng, m, b)
        kt = tree_keys(tree, st)
        path_sets = [frozenset(j for j, _ in k[0]) for k in kt]
        qS = {}
        for p, S in zip(P, path_sets): qS[S] = qS.get(S, 0) + p
        for k in (2, 3, 4):
            sets = sets_upto(m, k)
            Phi, F = phis(st, m, pi, sets)
            # orthonormality, and span equality with centred characters
            G = (Phi * P[:, None]).T @ Phi
            assert np.abs(G - np.eye(len(sets))).max() < 1e-9
            Xc = chars(st, m, sets); Xc = Xc - P @ Xc
            res = Xc - Phi @ ((Phi * P[:, None]).T @ Xc)
            assert np.abs(res).max() < 1e-9 and np.linalg.matrix_rank(Xc) == len(sets)
            assert (F ** 2).max() <= (1 - lam_eff) / lam_eff + 1e-9
            # conditional expectation formula for the tree
            C = cond_exp(P, Phi, kt)
            pred = np.stack([Phi[:, a] * np.array([set(A) <= (S | {m}) for S in path_sets]) for a, A in enumerate(sets)], axis=1)
            assert np.abs(C - pred).max() < 1e-9
            It = (C * P[:, None]).T @ C
            If = np.zeros_like(It)
            for S, q in qS.items():
                IS = info_matrix(P, Phi, form_keys(S, st))
                assert np.abs(IS - np.diag([float(set(A) <= (S | {m})) for A in sets])).max() < 1e-9
                If += q * IS
            diag = np.array([sum(q for S, q in qS.items() if set(A) - {m} <= S) for A in sets])
            assert np.abs(If - np.diag(diag)).max() < 1e-9
            # exact worst direction: max_h h'It h / h'If h over range of If (It vanishes off it)
            keep = diag > 1e-14
            assert np.abs(It[~keep][:, ~keep]).max() < 1e-12 if (~keep).any() else True
            w = sla.eigh(It[keep][:, keep], np.diag(diag[keep]), eigvals_only=True)[-1]
            nu = sum(math.comb(b + 1, j) * ((1 - lam_eff) / lam_eff) ** j for j in range(1, k + 1))
            key = (k, 'uniform' if rep % 7 == 0 else 'general')
            worst[key] = max(worst.get(key, 0), w / nu)
            assert w <= nu * (1 + 1e-9), (w, nu)
    print('part (b): max over trials of [max_h J_tau(h)/sum_S q_S J_S(h)] / nu_k  (must be <= 1):')
    for key in sorted(worst): print('   k=%d %-8s %.4f' % (key[0], key[1], worst[key]))
    for bb in range(1, 40):
        for k in range(1, bb + 2):
            assert sum(math.comb(bb + 1, j) for j in range(1, k + 1)) <= (bb + 1) ** k
    print('sum_{j<=k} C(b+1,j) <= (b+1)^k verified for b<40')


def run_W(m=4, b=2, reps=3, lam=0.2):
    st = states(m); n = len(st)
    forms = [form_keys(S, st) for S in itertools.combinations(range(m), b)]
    trees = [tree_keys(t, st) for t in padded_trees(m, b)]
    for rep in range(reps):
        pi = rng.uniform(lam, 1 - lam, size=m + 1)
        P = product_law(st, m, pi)
        dsets = [A for r in range(0, b + 1) for A in itertools.combinations(range(m), r)]
        d = chars(st, m, dsets) @ rng.normal(size=len(dsets))
        t = np.array([y for x, y in st]) * d; Delta = P @ t
        for k in (2, 3):
            sets = sets_upto(m, k)
            Phi, _ = phis(st, m, pi, sets)
            v = Phi.T @ (P * (t - Delta))
            Wf = solve_W(v, [info_matrix(P, Phi, kk) for kk in forms])[0]
            Wb = solve_W(v, [info_matrix(P, Phi, kk) for kk in trees])[0]
            nu = sum(math.comb(b + 1, j) * ((1 - lam) / lam) ** j for j in range(1, k + 1))
            print(f'part (b) W-level rep{rep} k={k}: fixed={Wf:.5f} branch={Wb:.5f} ratio={Wf / Wb:.4f}  (K=2, nu={nu:.1f})')
            assert Wb <= Wf * (1 + 1e-4) and Wf <= min(2, nu) * Wb * (1 + 1e-4)


if __name__ == '__main__':
    tangent_check(3, 2); tangent_check(4, 3)
    run()
    run_W()
