"""Is W^(3)_branch = 1 for the address contrast at every cap?  A branching design that beats the rule's own tree.

Design (s, r), s + r = b, r <= 2^(kappa-s):
  with prob 1-eps: draw s address bits S_a uniformly, read them (answers alpha), then read r of the 2^(kappa-s)
                   data bits whose index is consistent with alpha (uniform r-subset R); score c*Y*sum_{j in R} Z_j / (1-eps)
  with prob eps:   a fixed form of b data bits R' (uniform); score -delta*Y*sum_{j in R'} Z_j / eps
Claim: with c = kappa/(r s), delta = (kappa-s)/(s b) the mean score G satisfies Proj_{T_3} G = Proj_{T_3} t, so by weak duality
  W^(3)_branch <= second moment = (kappa/(s sqrt r) + (kappa-s)/(s sqrt b))^2  after optimising eps.

Checks: (1) exact Fourier coefficients of G of order <= 3 by enumeration over addresses (any b);
        (2) brute force at b = 4: exact v^T I_q^+ v of the mixture design over all of T_3 (298 dims) <= formula."""
import itertools, math, sys
import numpy as np


def ub(b, s):
    kap = b - 1; r = b - s
    if s < 1 or s > kap or r > 2 ** (kap - s): return None
    return (kap / (s * math.sqrt(r)) + (kap - s) / (s * math.sqrt(b))) ** 2


def fourier_check(b, s):
    """Level-0 and level-1 (and all |B|<=1) coefficients of the mean score on chi_{B+{j}+{Y}}, exactly."""
    kap = b - 1; D = 2 ** kap; r = b - s
    c = kap / (r * s); delta = (kap - s) / (s * b)
    abits = np.array([[(1 if (j >> i) & 1 else -1) for i in range(kap)] for j in range(D)])
    addrs = np.array(list(itertools.product((-1, 1), repeat=kap)))
    subsets = list(itertools.combinations(range(kap), s))
    # w[a, j] = P(j in R | address a) under the tree part
    w = np.zeros((len(addrs), D))
    for Sa in subsets:
        Sa = list(Sa)
        cons = (addrs[:, None, Sa] == abits[None, :, Sa]).all(axis=2)
        w += cons * (r / 2 ** (kap - s)) / len(subsets)
    # mean score G = Y * sum_j Z_j * (c*w[a,j] - delta*b/D); its coefficient on chi_B(a) Z_j Y is E_a[(...) chi_B(a)]
    coef = c * w - delta * b / D
    err = 0.0
    for B in [()] + [(i,) for i in range(kap)]:
        chiB = np.prod(addrs[:, list(B)], axis=1) if B else np.ones(len(addrs))
        got = (coef * chiB[:, None]).mean(axis=0)                       # per j
        target = 2.0 ** -kap * (np.prod(abits[:, list(B)], axis=1) if B else np.ones(D))   # hat t on B+{j}+{Y}
        err = max(err, np.abs(got - target).max())
    return err, (c * math.sqrt(r) + delta * math.sqrt(b)) ** 2


def brute_b4(s):
    sys.path.insert(0, '.')
    from core import states, chars, sets_upto, info_matrix, tree_keys, form_keys
    from t3_c import address_setup
    b = 4; kap, D, m, st, P, t = address_setup(b); r = b - s
    sets = sets_upto(m, 3); X = chars(st, m, sets); v = X.T @ (P * t)
    abits = [[(1 if (j >> i) & 1 else -1) for i in range(kap)] for j in range(D)]
    Itree = np.zeros((len(sets), len(sets))); ntree = 0
    for Sa in itertools.combinations(range(kap), s):
        # all assignments alpha -> r-subset of consistent data bits; average the information over them
        alphas = list(itertools.product((-1, 1), repeat=s))
        opts = []
        for al in alphas:
            cons = [j for j in range(D) if all(abits[j][i] == al[u] for u, i in enumerate(Sa))]
            opts.append(list(itertools.combinations(cons, r)))
        # information is additive over the cells {a_Sa = alpha}; average each cell's contribution separately
        for u, al in enumerate(alphas):
            for R in opts[u]:
                keys = []
                for x, y in st:
                    if tuple(x[i] for i in Sa) == al:
                        keys.append((al, tuple(x[kap + j] for j in R), y))
                    else:
                        keys.append(('other',))        # uninformative cell: contributes E[s|cell] -- must be excluded
                # compute contribution of the cell {a_Sa = alpha} only
                mask = np.array([k[0] != 'other' for k in keys])
                Xm = X[mask]; Pm = P[mask]
                km = [k for k in keys if k[0] != 'other']
                from core import cond_exp
                C = cond_exp(Pm, Xm, km)
                Itree += (C * Pm[:, None]).T @ C / len(opts[u]) / math.comb(kap, s)
    forms = list(itertools.combinations(range(kap, m), b))
    Iform = sum(info_matrix(P, X, form_keys(S, st)) for S in forms) / len(forms)
    best = np.inf
    for eps in np.linspace(0.01, 0.6, 60):
        I = (1 - eps) * Itree + eps * Iform
        u = np.linalg.pinv(I, rcond=1e-10) @ v
        assert np.abs(I @ u - v).max() < 1e-8        # v in range
        best = min(best, float(v @ u))
    return best


if __name__ == '__main__':
    print('b=4 brute force over all of T_3 (exact value of the mixture design, optimised over eps on a grid) vs formula:')
    for s in (2, 1):
        print(f'   s={s}, r={4 - s}: exact {brute_b4(s):.4f}   formula (upper bound) {ub(4, s):.4f}')
    print('exact Fourier check of the model-unbiasedness of the score, and resulting upper bound on W^(3)_branch:')
    N = lambda s_, j: sum(math.comb(s_, i) for i in range(j + 1))
    for b in range(3, 15):
        cands = [(ub(b, s), s) for s in range(1, b) if ub(b, s) is not None]
        val, s = min(cands)
        err, val2 = fourier_check(b, s) if b <= 13 else (float('nan'), val)
        L3 = b * b / ((b + 1) ** 2 // 4)
        print(f'   b={b:2d}: best (s,r)=({s},{b - s})  max coefficient error {err:.1e}  W^(3)_branch <= {min(val, 1):.4f}'
              f'   L_3(b)={L3:.4f}   => ratio W_fixed/W_branch >= {L3 / min(val, 1):.3f}')
    for b in (20, 50, 100, 400):
        val, s = min((ub(b, s), s) for s in range(1, b) if ub(b, s) is not None)
        print(f'   b={b}: upper bound {val:.4f} (s={s}), b*bound={b * val:.2f}')
