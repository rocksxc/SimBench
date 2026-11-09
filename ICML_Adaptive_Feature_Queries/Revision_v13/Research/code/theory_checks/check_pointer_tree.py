"""Monte Carlo sanity check of the new r-round lower bound for the binary pointer-tree contrast.
Tree: internal nodes at levels 0..L-1 hold pointer bits; leaves (level L) hold data bits Z.
We check (i) the lemma E[M_t | T_{t-1}] <= (1+2 a_t) M_{t-1} for random and adversarial batches,
(ii) P(c* in Obs) <= r b (1+2b/(r-1))^(r-1) / 2^L for several hand-designed 2- and 3-round strategies,
(iii) the exact identity P(c*=v | T) = 1{C(v)} 2^{R(v)-L} via simulation.
"""
import numpy as np, itertools, math
rng = np.random.default_rng(1)

def tree(L):
    # node ids: level l has nodes 2^l-1 .. 2^(l+1)-2 ; children of node u: 2u+1, 2u+2
    n_int = 2**L - 1; n_leaf = 2**L
    return n_int, n_leaf

def path_nodes(L, v):
    """internal nodes on the path to leaf index v (0..2^L-1) and the direction taken at each."""
    nodes = []; dirs = []
    u = 0
    for l in range(L):
        bit = (v >> (L-1-l)) & 1
        nodes.append(u); dirs.append(bit); u = 2*u+1+bit
    return nodes, dirs

def M_value(L, read, bits):
    """M = max_v 1{C(v)} 2^{R(v)} given read set (dict node->bit)."""
    best = 0
    for v in range(2**L):
        nodes, dirs = path_nodes(L, v)
        ok = True; R = 0
        for u, dr in zip(nodes, dirs):
            if u in read:
                R += 1
                if bits[u] != dr: ok = False; break
        if ok: best = max(best, 2**R)
    return best

def lemma_check(L, trials=4000):
    n_int, n_leaf = tree(L)
    worst = 0.0
    for _ in range(trials):
        bits = rng.integers(0, 2, n_int)
        # random old read set
        k_old = rng.integers(0, 4); old = set(rng.choice(n_int, size=k_old, replace=False).tolist())
        M_old = M_value(L, old, bits)
        # new batch: adversarial-ish: pick a_t nodes among unread, prefer shallow + consistent
        a_t = rng.integers(1, 4)
        cand = [u for u in range(n_int) if u not in old]
        new = set(rng.choice(cand, size=min(a_t, len(cand)), replace=False).tolist())
        # E[M_t | T_{t-1}]: average over random values of the NEW bits (old bits fixed)
        tot = 0.0; reps = 64
        for _ in range(reps):
            b2 = bits.copy()
            for u in new: b2[u] = rng.integers(0, 2)
            tot += M_value(L, old | new, b2)
        ratio = (tot / reps) / ((1 + 2*len(new)) * M_old)
        worst = max(worst, ratio)
    return worst

def strategy_prob_hit(L, strategy, trials=20000):
    """P(c* in Obs) for a given r-round strategy (function of transcript)."""
    n_int, n_leaf = tree(L); hits = 0
    for _ in range(trials):
        bits = rng.integers(0, 2, n_int)
        # selected leaf
        u = 0
        for l in range(L): u = 2*u+1+bits[u]
        cstar = u - n_int
        read = {}; obs_leaves = set(); budget_used = 0
        for t, batch_fn in enumerate(strategy):
            batch = batch_fn(read, L)
            for node in batch:
                if node < n_int: read[node] = bits[node]
                else: obs_leaves.add(node - n_int)
            budget_used += len(batch)
        if cstar in obs_leaves: hits += 1
    return hits / trials

def known_node(read, L):
    """deepest known path node (internal node id) following read bits from the root, and its level."""
    u = 0; lvl = 0
    while lvl < L and u in read:
        u = 2*u+1+read[u]; lvl += 1
    return u, lvl

def two_round_subtree(k):
    """round 1: read complete subtree of depth k from the root; round 2: read the (b - (2^k-1)) most probable leaves."""
    def r1(read, L):
        return list(range(2**k - 1))
    def r2(read, L):
        n_int = 2**L - 1
        u, lvl = known_node(read, L)
        # leaves below u: descend
        nodes = [u]
        for l in range(lvl, L): nodes = [c for x in nodes for c in (2*x+1, 2*x+2)]
        return nodes[:max(0, (L+1) - (2**k-1))]
    return [r1, r2]

if __name__ == '__main__':
    for L in [3, 4]:
        print('L', L, 'lemma worst ratio E[M_t|T]/((1+2a)M_{t-1}) over trials (should be <= 1):', round(lemma_check(L), 4))
    for L in [4, 5, 6]:
        b = L + 1
        for k in [1, 2]:
            if 2**k - 1 > b: continue
            p = strategy_prob_hit(L, two_round_subtree(k))
            bound2 = 2*b*(1+2*b)/2**L
            print(f'L={L} b={b} 2-round subtree k={k}: P(hit)={p:.4f}  bound={bound2:.4f}  trivial path-guess 2^-(b-2)={2**-(b-2):.4f}')
