"""Referee tests of misspec_v20.pair_coverage() and of the identification claim for the pairwise model."""
import sys, itertools
import numpy as np
sys.path.insert(0, 'SCRATCH/v20/Research/code')
import misspec_v20 as ms
from ref_common import *
from test_b_more import pairwise_basis
rng = np.random.default_rng(21)

def as_design(K, qs, askeds):
    des = []
    for q, asked in zip(qs, askeds):
        keys = {}; cid = np.array([keys.setdefault((tuple(sorted(asked[x])), tuple(bitmat(K)[x, sorted(asked[x])])), len(keys)) for x in range(1 << K)])
        des.append((float(q), cid, len(keys)))
    return des

# ---- pair_coverage vs brute force
worst = 0.0
for _ in range(60):
    K = int(rng.integers(3, 8)); b = int(rng.integers(2, K)); n = int(rng.integers(1, 6)); q = rng.dirichlet(np.ones(n)); px = rng.dirichlet(np.ones(1 << K))
    askeds = [random_interview(K, b, [1] * b, rng) if rng.random() < 0.6 else [tuple(sorted(rng.choice(K, b, replace=False)))] * (1 << K) for _ in range(n)]
    cov = ms.pair_coverage(K, as_design(K, q, askeds), px); ref = np.zeros((K, K))
    for w, asked in zip(q, askeds):
        for x in range(1 << K):
            for i in asked[x]:
                for j in asked[x]: ref[i, j] += w * px[x]
    worst = max(worst, np.abs(cov - ref).max())
print('pair_coverage vs brute-force P(i and j both queried): max abs diff %.1e (60 random mixtures of forms and trees)' % worst)

# ---- identification of the pairwise model (K items + label) from incomplete records: rank of the information matrix
def pairwise_law(K, rng, scale=0.6):
    V = K + 1; S = 2.0 * bitmat(V) - 1; th1 = rng.normal(0, scale, V); th2 = np.triu(rng.normal(0, scale, (V, V)), 1)
    lp = S @ th1 + np.einsum('si,ij,sj->s', S, th2, S); p = np.exp(lp - lp.max()); p /= p.sum()
    return p.reshape(2, 1 << K)        # label is the top bit -> P[y, x]

def info(K, P, qs, askeds):
    basis = pairwise_basis(K, P); I = 0
    for q, a in zip(qs, askeds):
        cl = cells_of(K, a); I = I + q * info_matrix(P, basis, [cl, cl])
    return I

def rank_report(name, K, qs, askeds, laws=5):
    out = []
    for _ in range(laws):
        P = pairwise_law(K, rng); I = info(K, P, qs, askeds); ev = np.linalg.eigvalsh(I); out.append((int((ev > 1e-10 * ev.max()).sum()), ev.min() / ev.max()))
    px = np.full(1 << K, 1.0 / (1 << K)); cov = ms.pair_coverage(K, as_design(K, qs, askeds), px); unc = int((cov[~np.eye(K, dtype=bool)] < 1e-12).sum() // 2)
    p = (K + 1) + (K + 1) * K // 2
    print('  %-58s pairs uncovered (pair_coverage): %d; rank of information at 5 random pairwise laws: %s of %d (min/max eigenvalue %.1e..%.1e)' % (name, unc, sorted({r for r, _ in out}), p, min(e for _, e in out), max(e for _, e in out)))

form = lambda K, S: [tuple(S)] * (1 << K)
print('identification (rank of the observed-data information of the pairwise model at laws in the model):')
K = 4
rank_report('forms: all pairs of 4 items (b=2)', K, [1 / 6] * 6, [form(K, S) for S in itertools.combinations(range(K), 2)])
rank_report('forms {0,2,3},{1,2,3} (b=3): pair (0,1) never together', K, [0.5, 0.5], [form(K, (0, 2, 3)), form(K, (1, 2, 3))])
rank_report('forms {0,1},{1,2},{2,3} (b=2): three pairs uncovered', K, [1 / 3] * 3, [form(K, (0, 1)), form(K, (1, 2)), form(K, (2, 3))])
# product law for the uncovered-pair forms
Bm = bitmat(4); p1 = np.array([0.3, 0.6, 0.45, 0.7]); px = np.prod(np.where(Bm == 1, p1, 1 - p1), axis=1); Pprod = np.stack([0.4 * px, 0.6 * px])
ev = np.linalg.eigvalsh(info(4, Pprod, [0.5, 0.5], [form(4, (0, 2, 3)), form(4, (1, 2, 3))])); print('  same two forms at a PRODUCT law: rank %d of 15' % int((ev > 1e-10 * ev.max()).sum()))
# trees: all pairs "covered" in the sense of pair_coverage, yet a pair is only seen on a selected branch
K = 3; Bm = bitmat(K)
T1 = [((0, 1) if Bm[x, 0] == 1 else (0, 2)) for x in range(8)]          # ask 0; then 1 if x0=+1 else 2
T2 = [((1, 2) if Bm[x, 1] == 1 else (1, 0)) for x in range(8)]          # ask 1; then 2 if x1=+1 else 0
rank_report('two depth-2 trees on 3 items, every pair on some branch', K, [0.5, 0.5], [T1, T2])
rank_report('the single tree T1 (pair (1,2) never together)', K, [1.0], [T1])
K = 4; Bm = bitmat(K)
found = 0
for trial in range(300):
    b = 2 if trial % 2 else 3; n = int(rng.integers(1, 4)); askeds = [random_interview(K, b, [1] * b, rng) for _ in range(n)]; qs = [1.0 / n] * n
    cov = ms.pair_coverage(K, as_design(K, qs, askeds), np.full(16, 1 / 16)); unc = int((cov[~np.eye(K, dtype=bool)] < 1e-12).sum() // 2)
    P = pairwise_law(K, rng); ev = np.linalg.eigvalsh(info(K, P, qs, askeds)); rk = int((ev > 1e-10 * ev.max()).sum())
    if unc == 0 and rk < 15: found += 1; ex = (b, n, rk)
    if unc > 0 and rk == 15: found += 1000
print('  random mixtures of 1-3 trees on 4 items (300 trials): all pairs covered but information singular in %d trials; some pair uncovered but information nonsingular in %d trials' % (found % 1000, found // 1000), ('example (b, trees, rank): %s' % (ex,)) if found % 1000 else '')
