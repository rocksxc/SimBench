"""Numerical check of the '(b), stability' inequality chain on small product laws.
For each padded tree tau and nearby P in M_k: lambda_max(I^P_tau, I^P_{q^{tau,eta}}) <= nu_k/(1-eta) * (1+4 omega/(eta c0)),
with omega = max_iota || I^P_iota - I^{P0}_iota ||_op (a-coordinates, basis centred at the respective law), c0 = lambda_min(I^{P0}_u)."""
import itertools, math
import numpy as np
import scipy.linalg as sla

rng = np.random.default_rng(3)


def setup(m, b, k):
    N = 1 << (m + 1)
    bits01 = (np.arange(N)[:, None] >> np.arange(m + 1)) & 1
    pm = 2.0 * bits01 - 1
    sets = [A for r in range(1, k + 1) for A in itertools.combinations(range(m + 1), r)]
    S = np.array([np.prod(pm[:, A], axis=1) for A in sets]).T
    ybit = bits01[:, m]
    forms = list(itertools.combinations(range(m), b))
    fkeys = [];
    for Fm in forms:
        key = ybit.copy()
        for i, c in enumerate(Fm): key = key | (bits01[:, c] << (i + 1))
        fkeys.append(key)
    # all padded depth-b trees: recursive enumeration, returns list of (leafkey array, pathset-index array)
    form_index = {frozenset(Fm): i for i, Fm in enumerate(forms)}

    def trees(mask, used):
        """all padded subtrees on the profiles in mask (bool array); yields (key array (local leaf id), nleaves, formidx array)"""
        if len(used) == b:
            fi = np.full(N, form_index[frozenset(used)]); yield np.zeros(N, dtype=np.int64), 1, fi; return
        for c in range(m):
            if c in used: continue
            L = list(trees(mask, used + (c,)))
            for (k0, n0, f0) in L:
                for (k1, n1, f1) in L:
                    key = np.where(bits01[:, c] == 0, k0, n0 + k1); fi = np.where(bits01[:, c] == 0, f0, f1)
                    yield key, n0 + n1, fi
    T = [(key * 2 + ybit, 2 * n, fi) for key, n, fi in trees(None, ())]
    return dict(N=N, pm=pm, S=S, sets=sets, forms=forms, fkeys=fkeys, trees=T, m=m, b=b, k=k, bits01=bits01)


def info(P, Sc, key, ncell):
    den = np.bincount(key, weights=P, minlength=ncell)
    num = np.zeros((ncell, Sc.shape[1])); np.add.at(num, key, P[:, None] * Sc)
    ok = den > 0; B = num[ok] / np.sqrt(den[ok])[:, None]
    return B.T @ B


def all_info(G, P):
    Sc = G['S'] - P @ G['S']
    IF = [info(P, Sc, key, 1 << (G['b'] + 1)) for key in G['fkeys']]
    IT = [info(P, Sc, key, n) for key, n, _ in G['trees']]
    return IF, IT


def run(m, b, k, lam, eta=0.2):
    G = setup(m, b, k); N = G['N']
    marg = rng.uniform(lam, 1 - lam, size=m + 1); marg[0] = lam  # one coordinate exactly at lambda
    P0 = np.ones(N)
    for j in range(m + 1): P0 *= np.where(G['bits01'][:, j] == 1, marg[j], 1 - marg[j])
    rho = (1 - lam) / lam
    nu = sum(math.comb(b + 1, j) * rho ** j for j in range(1, k + 1))
    IF0, IT0 = all_info(G, P0)
    Iu0 = sum(IF0) / len(IF0); c0 = np.linalg.eigvalsh(Iu0).min()
    # (b) at P0: I_tau <= nu * sum_S q^tau_S I_S  (PSD order)
    worst_b = 0
    qtaus = []
    for (key, n, fi), It in zip(G['trees'], IT0):
        q = np.bincount(fi, weights=P0, minlength=len(G['forms'])); qtaus.append(q)
        Iq = sum(qi * I for qi, I in zip(q, IF0))
        ev = np.linalg.eigvalsh(nu * Iq - It).min(); assert ev > -1e-9, ev
        # actual best constant
        Iqe = Iq + 1e-12 * np.eye(len(Iq))
        worst_b = max(worst_b, sla.eigh(It, Iqe, eigvals_only=True).max())
    print(f"m={m} b={b} k={k} lam={lam}: {len(G['trees'])} padded trees, {len(G['forms'])} forms, dim T_k={len(G['sets'])}; nu_k={nu:.3f}; at P0 max_tau lambda_max(I_tau, I_q^tau)={worst_b:.3f} (<= nu_k OK); c0={c0:.4f}")
    # nearby laws in M_k: log p = log p0 + sum_A theta_A chi_A
    for scale in (0.1, 0.01, 0.003, 0.001, 0.0003):
        worst = 0; bound_worst = 0; ok = True; maxom = 0
        for rep in range(5):
            th = rng.normal(size=len(G['sets'])) * scale
            P = P0 * np.exp(G['S'] @ th); P /= P.sum()
            IF, IT = all_info(G, P)
            om = max(max(np.abs(np.linalg.eigvalsh(a - a0)).max() for a, a0 in zip(IF, IF0)),
                     max(np.abs(np.linalg.eigvalsh(a - a0)).max() for a, a0 in zip(IT, IT0)))
            maxom = max(maxom, om)
            Iu = sum(IF) / len(IF)
            for q, It in zip(qtaus, IT):
                Iq = (1 - eta) * sum(qi * I for qi, I in zip(q, IF)) + eta * Iu
                lmax = sla.eigh(It, Iq, eigvals_only=True).max()
                worst = max(worst, lmax)
                if om <= eta * c0 / 2:
                    bd = nu / (1 - eta) * (1 + 4 * om / (eta * c0)); bound_worst = max(bound_worst, bd)
                    assert np.linalg.eigvalsh(Iq).min() >= eta * c0 / 2 - 1e-12
                    if lmax > bd + 1e-9: ok = False
        cond = maxom <= eta * c0 / 2
        print(f"   |theta|~{scale}: omega={maxom:.4f} (need <= eta*c0/2={eta*c0/2:.4f}: {cond}); max_tau lambda_max(I^P_tau, I^P_q(tau,eta))={worst:.3f}; proof bound={bound_worst:.3f}; chain holds: {ok if cond else 'n/a'}")


run(3, 2, 2, 0.5)
run(3, 2, 2, 0.3)
run(4, 2, 2, 0.4)
run(4, 3, 2, 0.5)
run(4, 3, 3, 0.4)
