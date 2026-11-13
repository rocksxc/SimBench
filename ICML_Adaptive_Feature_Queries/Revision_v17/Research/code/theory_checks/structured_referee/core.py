"""Brute-force helpers on {-1,1}^m x {-1,1}. Independent of the paper's own check script."""
import itertools, math
import numpy as np


def states(m):
    return [(x, y) for x in itertools.product((-1, 1), repeat=m) for y in (-1, 1)]


def padded_trees(m, b):
    """All decision trees with exactly b distinct queries on every path (nested tuples (j, lo, hi))."""
    def rec(used, depth):
        if depth == b:
            yield None
            return
        for j in range(m):
            if j in used:
                continue
            subs = list(rec(used | {j}, depth + 1))
            for lo in subs:
                for hi in subs:
                    yield (j, lo, hi)
    return list(rec(frozenset(), 0))


def random_tree(rng, m, b, used=(), depth=0):
    if depth == b:
        return None
    j = int(rng.choice([c for c in range(m) if c not in used]))
    return (j, random_tree(rng, m, b, used + (j,), depth + 1), random_tree(rng, m, b, used + (j,), depth + 1))


def leaf(tree, x):
    path = []
    node = tree
    while node is not None:
        j, lo, hi = node
        path.append((j, x[j]))
        node = hi if x[j] == 1 else lo
    return tuple(path)


def tree_keys(tree, st):
    return [(leaf(tree, x), y) for x, y in st]


def form_keys(S, st):
    S = sorted(S)
    return [(tuple(x[j] for j in S), y) for x, y in st]


def cond_exp(P, H, keys):
    """E[H | key] as an array over states; H may be (n,) or (n,p)."""
    H = np.asarray(H, float)
    idx = {}
    for i, k in enumerate(keys):
        idx.setdefault(k, []).append(i)
    out = np.zeros_like(H)
    for k, ii in idx.items():
        w = P[ii]
        tot = w.sum()
        if tot > 0:
            out[ii] = (w[:, None] * H[ii].reshape(len(ii), -1)).sum(0).reshape(H[ii].shape[1:]) / tot
    return out


def info_matrix(P, Sc, keys):
    """E[E[s|key] E[s|key]^T] for score matrix Sc (n,p)."""
    C = cond_exp(P, Sc, keys)
    return (C * P[:, None]).T @ C


def J(P, h, keys):
    c = cond_exp(P, h, keys)
    return float((P * c * c).sum())


def chars(st, m, sets):
    """chi_A over coordinates 0..m (m = label)."""
    Z = np.array([list(x) + [y] for x, y in st], float)
    return np.stack([np.prod(Z[:, list(A)], axis=1) if len(A) else np.ones(len(st)) for A in sets], axis=1)


def sets_upto(m, k):
    return [A for r in range(1, k + 1) for A in itertools.combinations(range(m + 1), r)]


def solve_W(v, Is, solver='CLARABEL'):
    """min_q v^T (sum q I)^+ v via SDP epigraph (handles singular information; +inf if v not in range)."""
    import cvxpy as cp
    n = len(Is); p = len(v)
    q = cp.Variable(n, nonneg=True)
    tau = cp.Variable()
    M = sum(q[i] * Is[i] for i in range(n))
    vv = np.asarray(v, float).reshape(p, 1)
    blk = cp.bmat([[M, vv], [vv.T, cp.reshape(tau, (1, 1), order='C')]])
    prob = cp.Problem(cp.Minimize(tau), [cp.sum(q) == 1, blk >> 0])
    prob.solve(solver=solver)
    return prob.value, q.value


def solve_W_design(P, tvec, keys_list, solver='CLARABEL'):
    """Design-based W: min sum_iota sum_cells P(cell) g^2 / q_iota  s.t. sum_iota g_iota(cell(x,y)) = t(x,y); minus Delta^2."""
    import cvxpy as cp
    n = len(P)
    q = cp.Variable(len(keys_list), nonneg=True)
    cons = [cp.sum(q) == 1]
    tot = 0
    obj = 0
    for i, keys in enumerate(keys_list):
        cells = sorted(set(keys))
        pos = {c: k for k, c in enumerate(cells)}
        A = np.zeros((n, len(cells)))
        for s, c in enumerate(keys):
            A[s, pos[c]] = 1
        g = cp.Variable(len(cells))
        pc = A.T @ P
        obj = obj + cp.quad_over_lin(cp.multiply(np.sqrt(pc), g), q[i])
        tot = tot + A @ g
    cons.append(tot == tvec)
    prob = cp.Problem(cp.Minimize(obj), cons)
    prob.solve(solver=solver)
    return prob.value - float(P @ tvec) ** 2
