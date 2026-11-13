"""Numerical checks for Theorem thm:structuredfull (adaptivity in a model), by brute force on small cubes.
(a) information domination: for random laws P on {0,1}^m x {0,1}, random depth-b trees tau and random functions h,
    sum over the padded path sets S of J_S(h) >= J_tau(h);
(b) at random product laws, for random h in the order-k tangent space, sum_S P(S_tau = S) J_S(h) >= J_tau(h) / nu_k;
(c) closed forms for the address contrast: L_k(b) from its definition, L_3(b) = b^2 / floor((b+1)^2/4) < 4,
    L_{b+1}(b) = 2^(b-1), L_k(b) >= C(b-1, k-2) / b, and the value 1/b of uniform data-bit forms for k = 2."""
import itertools, math
import numpy as np

rng = np.random.default_rng(20261113)


def random_tree(m, b, used=(), depth=0):
    """Random decision tree of depth exactly b on distinct coordinates along each path (so paths are padded)."""
    if depth == b: return None
    j = int(rng.choice([c for c in range(m) if c not in used]))
    return (j, random_tree(m, b, used + (j,), depth + 1), random_tree(m, b, used + (j,), depth + 1))


def leaf_of(tree, x):
    path = []; node = tree
    while node is not None:
        j, lo, hi = node; path.append((j, x[j])); node = hi if x[j] else lo
    return tuple(path)


def cond_energy(P, h, keys):
    """E[E[h | key]^2] for a law P over states and a list of hashable keys per state."""
    num = {}; den = {}
    for p, hv, k in zip(P, h, keys):
        num[k] = num.get(k, 0.0) + p * hv; den[k] = den.get(k, 0.0) + p
    return sum(num[k] ** 2 / den[k] for k in num if den[k] > 0)


def run(m=5, b=3, trials=200):
    states = [(x, y) for y in (0, 1) for x in itertools.product((0, 1), repeat=m)]
    worst_a = np.inf; worst_b = np.inf
    for _ in range(trials):
        tree = random_tree(m, b)
        leaves = [leaf_of(tree, x) for x, y in states]; sets = [frozenset(j for j, _ in lf) for lf in leaves]
        # (a) arbitrary law, arbitrary h
        P = rng.dirichlet(np.ones(len(states))); h = rng.normal(size=len(states))
        Jt = cond_energy(P, h, [(lf, y) for lf, (x, y) in zip(leaves, states)])
        Js = sum(cond_energy(P, h, [(tuple(x[j] for j in sorted(S)), y) for x, y in states]) for S in set(sets))
        worst_a = min(worst_a, Js / Jt)
        # (b) product law, h of order k
        lam = 0.2; pi = rng.uniform(lam, 1 - lam, size=m + 1)
        Pp = np.array([np.prod([pi[j] if v else 1 - pi[j] for j, v in enumerate(x + (y,))]) for x, y in states])
        phi = np.array([[(v - pi[j]) / math.sqrt(pi[j] * (1 - pi[j])) for j, v in enumerate(x + (y,))] for x, y in states])
        for k in (2, 3):
            terms = [c for r in range(1, k + 1) for c in itertools.combinations(range(m + 1), r)]
            a = rng.normal(size=len(terms)); hk = sum(a_ * np.prod(phi[:, c], axis=1) for a_, c in zip(a, terms))
            Jt = cond_energy(Pp, hk, [(lf, y) for lf, (x, y) in zip(leaves, states)])
            qS = {}
            for p, S in zip(Pp, sets): qS[S] = qS.get(S, 0.0) + p
            Jf = sum(q * cond_energy(Pp, hk, [(tuple(x[j] for j in sorted(S)), y) for x, y in states]) for S, q in qS.items())
            nu = sum(math.comb(b + 1, j) * ((1 - lam) / lam) ** j for j in range(1, k + 1))
            worst_b = min(worst_b, Jf * nu / Jt)
    return worst_a, worst_b


def N(s, j): return sum(math.comb(s, i) for i in range(j + 1))
def L(b, k): return N(b - 1, k - 2) ** 2 / max((b - s) * N(s, k - 2) for s in range(b))


if __name__ == '__main__':
    wa, wb = run()
    print('(a) min over trials of sum_S J_S(h) / J_tau(h): %.4f (must be >= 1)' % wa); assert wa >= 1 - 1e-9
    print('(b) min over trials of nu_k * sum_S q_S J_S(h) / J_tau(h): %.4f (must be >= 1)' % wb); assert wb >= 1 - 1e-9
    for b in range(2, 13):
        assert abs(L(b, 2) - 1 / b) < 1e-12 and abs(L(b, b + 1) - 2 ** (b - 1)) < 1e-9
        if b >= 3: assert abs(L(b, 3) - b * b / ((b + 1) ** 2 // 4)) < 1e-12 and L(b, 3) < 4
        for k in range(2, b + 2): assert L(b, k) >= math.comb(b - 1, k - 2) / b - 1e-12
    print('(c) closed forms of L_k(b) verified for b = 2..12;', 'L_3:', [round(L(b, 3), 3) for b in range(3, 9)], 'L_4:', [round(L(b, 4), 3) for b in range(3, 9)])
