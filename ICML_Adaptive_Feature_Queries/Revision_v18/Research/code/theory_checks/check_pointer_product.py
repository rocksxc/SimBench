"""Numerical check of the potential inequality behind the product pointer-tree bound (v15, Theorem `thm:productpointer`).

One block: complete binary tree with L pointer levels (nodes 1..2^L-1 in heap order, node u has children 2u, 2u+1)
and 2^L data leaves (heap indices 2^L..2^(L+1)-1). State after some rounds: every pointer is unread (-1) or read
with value 0/1 (0 = left child); Obs = set of leaves whose data bit was read. For a leaf v:
  C(v) = every read pointer on its path selects towards v;  R(v) = number of read pointers on its path.
  M = max_v 1{C(v)} 2^R(v);   2^L * pi = sum_{v in Obs} 1{C(v)} 2^R(v);   Q = M + 2^L pi.
Claim: for a batch reading a unread pointers and lam unread data leaves, E[Q_new | state] <= (1 + 2a + lam) Q_old,
the expectation being over the uniform values of the newly read pointers.
L = 2: exhaustive over all states and nonempty batches. L = 3: random states and batches."""
import itertools, sys
import numpy as np


def stats(L, ptr, obs):
    best = 0.0; tot = 0.0
    for v in range(1 << L, 1 << (L + 1)):
        u = v; ok = True; R = 0
        while u > 1:
            par = u >> 1
            if ptr[par] >= 0:
                R += 1
                if ptr[par] != (u & 1): ok = False; break
            u = par
        if ok:
            val = 2.0 ** R; best = max(best, val)
            if v in obs: tot += val
    return best, tot


def check(L, ptr, obs, newp, newd):
    M0, S0 = stats(L, ptr, obs); Q0 = M0 + S0
    a = len(newp); lam = len(newd); obs2 = obs | set(newd); EQ = 0.0
    for vals in itertools.product([0, 1], repeat=a):
        p2 = list(ptr)
        for u, x in zip(newp, vals): p2[u] = x
        M1, S1 = stats(L, p2, obs2); EQ += (M1 + S1) / (1 << a)
    return EQ / ((1 + 2 * a + lam) * Q0), EQ / ((1 + 2 * a) * M0 + lam * M0 + S0)


def exhaustive(L):
    nodes = list(range(1, 1 << L)); leaves = list(range(1 << L, 1 << (L + 1))); worst = (0.0, 0.0); n = 0
    for st in itertools.product([-1, 0, 1], repeat=len(nodes)):
        ptr = [-1] + list(st); unread = [u for u in nodes if ptr[u] < 0]
        for ob in range(1 << len(leaves)):
            obs = {leaves[i] for i in range(len(leaves)) if ob >> i & 1}; free = [v for v in leaves if v not in obs]
            for ka in range(len(unread) + 1):
                for newp in itertools.combinations(unread, ka):
                    for kd in range(len(free) + 1):
                        for newd in itertools.combinations(free, kd):
                            if ka + kd == 0: continue
                            r = check(L, ptr, obs, newp, newd); worst = (max(worst[0], r[0]), max(worst[1], r[1])); n += 1
    return worst, n


def random_checks(L, trials, rng):
    nodes = list(range(1, 1 << L)); leaves = list(range(1 << L, 1 << (L + 1))); worst = (0.0, 0.0)
    for _ in range(trials):
        ptr = [-1] + [int(x) for x in rng.choice([-1, 0, 1], size=len(nodes), p=[0.5, 0.25, 0.25])]
        obs = {v for v in leaves if rng.random() < 0.3}
        unread = [u for u in nodes if ptr[u] < 0]; free = [v for v in leaves if v not in obs]
        newp = [u for u in unread if rng.random() < 0.4][:8]; newd = [v for v in free if rng.random() < 0.3]
        if not newp and not newd: continue
        r = check(L, ptr, obs, newp, newd); worst = (max(worst[0], r[0]), max(worst[1], r[1]))
    return worst


if __name__ == '__main__':
    w, n = exhaustive(2)
    print('L=2 exhaustive: %d (state, batch) pairs; max E[Q_new]/((1+2a+lam) Q_old) = %.4f; max against the sharper sum = %.4f' % (n, w[0], w[1]))
    rng = np.random.default_rng(20261111)
    for L in (3, 4):
        w = random_checks(L, 20000 if L == 3 else 5000, rng)
        print('L=%d random: max ratio %.4f; sharper %.4f' % (L, w[0], w[1]))
    # numerical value of the bound 2^(b-1)/(1+2b/r)^r against the exact small-cap constants of Table (pointer)
    for b, r, exact in [(3, 2, 1.8), (4, 2, 3.3241), (4, 3, 1.8)]:
        print('b=%d r=%d: new bound %.3f, old bound %.3f, exact lower bound M_r(U) %.3f' % (b, r, 2 ** (b - 1) / (1 + 2 * b / r) ** r, 2 ** (b - 1) / (r * b * (1 + 2 * b / (r - 1)) ** (r - 1)), exact))
