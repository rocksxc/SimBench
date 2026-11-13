"""Stronger sanity check of Theorem (binary pointer tree): simulate greedy adaptive r-round strategies
with total budget b = L+1 that (i) read the currently most likely path nodes, (ii) in the last round read
the most likely leaves. Compare P(c* in Obs) with the proven bound r b (1+2b/(r-1))^(r-1) / 2^L and with the
trivial 2^-(b-r) (path guessing after r-1 single questions). Also check E[Psi_r] <= 1 along the way."""
import numpy as np
rng = np.random.default_rng(7)

def run(L, r, split, trials=4000):
    b = L + 1; n_int = 2**L - 1
    hits = 0; psi_sum = 0.0
    for _ in range(trials):
        bits = rng.integers(0, 2, n_int)
        u = 0
        for l in range(L): u = 2*u + 1 + bits[u]
        cstar = u - n_int
        read = {}; M_prev = 1.0; prod = 1.0
        obs = set()
        for t in range(r):
            a_t = split[t]
            # greedy: descend from the root following known bits; read the unknown node on the current most likely path,
            # then continue (within the round, choices cannot depend on this round's answers -> pick nodes along a guessed path)
            node = 0; lvl = 0; batch = []
            while lvl < L and len(batch) < a_t:
                if node in read:
                    node = 2*node + 1 + read[node]; lvl += 1
                else:
                    batch.append(node)  # unknown node on the path: read it; guess its bit 0 for continuing within the round
                    node = 2*node + 1; lvl += 1
            if t == r - 1:
                # last round: read the most likely leaves (uniform below the deepest known node) with the remaining budget
                node = 0; lvl = 0
                while lvl < L and node in read:
                    node = 2*node + 1 + read[node]; lvl += 1
                leaves = [node]
                for l in range(lvl, L): leaves = [c for x in leaves for c in (2*x+1, 2*x+2)]
                k = b - sum(split[:r-1])
                for v in leaves[:k]: obs.add(v - n_int)
                batch = []
            for node in batch: read[node] = bits[node]
            # potential check: M_t = max_v 1{C_t(v)} 2^{R_t(v)}
            best = 0
            for v in range(2**L):
                node = 0; ok = True; R = 0
                for l in range(L):
                    bit = (v >> (L-1-l)) & 1
                    if node in read:
                        R += 1
                        if read[node] != bit: ok = False; break
                    node = 2*node + 1 + bit
                if ok: best = max(best, 2**R)
            prod *= (1 + 2*len(batch))
            M_prev = best
        psi_sum += M_prev / prod
        if cstar in obs: hits += 1
    return hits / trials, psi_sum / trials

for L in [6, 8, 10]:
    b = L + 1
    for r, split in [(2, [3, b-3]), (2, [b//2, b - b//2]), (3, [2, 2, b-4]), (3, [b//3, b//3, b - 2*(b//3)])]:
        p, psi = run(L, r, split, trials=1500)
        bound = r * b * (1 + 2*b/(r-1))**(r-1) / 2**L
        print(f'L={L} b={b} r={r} split={split}: P(hit)={p:.4f}  E[Psi_r]={psi:.3f} (<=1)  proven bound={bound:.3f}  trivial 2^-(b-r)={2**-(b-r):.4f}')
