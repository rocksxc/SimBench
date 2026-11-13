"""Referee tests of Theorem (b): information formula, forms optimum (SDP) vs closed form, mixtures of trees vs lower bound."""
import itertools, sys
import numpy as np, cvxpy as cp
from ref_common import *

rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 1)


def compositions(b, r):
    return [c for c in itertools.product(range(1, b + 1), repeat=r) if sum(c) == b]


def incl(m, P, asked_by_label):
    py = P.sum(1); pi = np.zeros((2, m))
    for y in (0, 1):
        A = np.zeros((1 << m, m))
        for x in range(1 << m): A[x, list(asked_by_label[y][x])] = 1
        pi[y] = P[y] @ A / py[y]
    return pi


# ---------------------------------------------------------------- Test 1: information formula
def test1(trials=150):
    worst = 0.0; worst_off = 0.0; n = {}
    for _ in range(trials):
        m = int(rng.integers(3, 7)); b = int(rng.integers(2, m)); P, p, py = ci_law(m, rng, 0.08, 0.92)
        basis = ci_basis(m, P); X = 2.0 * bitmat(m) - 1
        r = int(rng.integers(1, b + 1)); sizes = list(compositions(b, r)[rng.integers(len(compositions(b, r)))])
        labdep = bool(rng.integers(2))
        a0 = random_interview(m, b, sizes, rng)
        if labdep:
            r2 = int(rng.integers(1, b + 1)); sizes2 = list(compositions(b, r2)[rng.integers(len(compositions(b, r2)))])
            a1 = random_interview(m, b, sizes2, rng)
        else: a1 = a0
        cl = [cells_of(m, a0), cells_of(m, a1)]
        for c in cl[0] + cl[1]: assert len(c) == 1 << (m - b)          # cylinder cells with exactly b asked coordinates
        I = info_matrix(P, basis, cl); pi = incl(m, P, [a0, a1])
        diag = [py[0] * py[1]]
        for y in (0, 1):
            for j in range(m):
                mu = (P[y] @ X[:, j]) / py[y]; var = (P[y] @ (X[:, j] - mu) ** 2) / py[y]
                diag.append(py[y] * pi[y, j] * var)
        D = np.diag(diag)
        worst = max(worst, np.abs(I - D).max()); worst_off = max(worst_off, np.abs(I - np.diag(np.diag(I))).max())
        assert abs(pi.sum(1) - b).max() < 1e-12
        key = ('label-dep' if labdep else 'blind', 'r=%d' % r, 'same-batch>1' if max(sizes) > 1 else 'singletons'); n[key] = n.get(key, 0) + 1
    print('TEST 1  information matrix = diag(P(y) pi_j(y) Var_y(x_j)) in the model basis: max abs error %.2e (max off-diagonal %.2e) over %d interviews' % (worst, worst_off, trials))
    print('        cases:', {' '.join(k): v for k, v in sorted(n.items())})


# ---------------------------------------------------------------- SDP for c-optimal design with possibly singular information
def copt(mats, v, groups=None):
    """min v' (sum_i q_i M_i)^+ v over q in the simplex (or a product of simplices given by `groups`)."""
    n = len(mats); p = len(v); q = cp.Variable(n, nonneg=True); tt = cp.Variable()
    I = sum(q[i] * mats[i] for i in range(n))
    Mx = cp.bmat([[I, v.reshape(-1, 1)], [v.reshape(1, -1), cp.reshape(tt, (1, 1), order='C')]])
    cons = [Mx >> 0]
    if groups is None: cons.append(cp.sum(q) == 1)
    else: cons += [cp.sum(q[g]) == 1 for g in groups]
    prob = cp.Problem(cp.Minimize(tt), cons); prob.solve(solver='CLARABEL')
    return float(tt.value), np.asarray(q.value)


def label_part(P, basis, cells, y):
    Pz = np.zeros_like(P); Pz[y] = P[y]
    p = basis.shape[0]; I = np.zeros((p, p))
    for c in cells:
        pc = P[y, c].sum(); e = basis[:, y, c] @ P[y, c] / pc; I += pc * np.outer(e, e)
    return I


def test2(trials=25):
    w_blind = 0.0; w_lab = 0.0; ratios = []
    for _ in range(trials):
        m = int(rng.integers(4, 7)); b = int(rng.integers(2, min(m, 5))); P, p, py = ci_law(m, rng, 0.05, 0.95)
        d = random_contrast(m, b, rng, kind=rng.choice(['tree', 'poly']))
        if rng.random() < 0.3:                         # make the contrast ignore some coordinates (zeros in dhat)
            k = int(rng.integers(1, m - 1)); X = 2.0 * bitmat(m) - 1
            d = np.tanh(X[:, :k] @ rng.normal(size=k)) * rng.uniform(0.3, 1)
        basis = ci_basis(m, P); v, delta, t = gradient(P, basis, d); cf = closed_forms(P, d, b)
        forms = list(itertools.combinations(range(m), b))
        cellsS = [cells_of(m, [S] * (1 << m)) for S in forms]
        mats = [info_matrix(P, basis, [c, c]) for c in cellsS]
        val, q = copt(mats, v)
        w_blind = max(w_blind, abs(val - cf['blind']) / cf['blind'])
        matsy = [label_part(P, basis, c, 0) for c in cellsS] + [label_part(P, basis, c, 1) for c in cellsS]
        vall, ql = copt(matsy, v, groups=[list(range(len(forms))), list(range(len(forms), 2 * len(forms)))])
        w_lab = max(w_lab, abs(vall - cf['lab']) / cf['lab'])
        ratios.append(cf['blind'] / cf['lab'])
        assert cf['blind'] <= 2 * cf['lab'] + 1e-12 and cf['lab'] <= cf['blind'] + 1e-12
    print('TEST 2  optimal label-blind forms (SDP over all forms, brute-force information) vs Var(E[t|Y]) + M_b(cbar): max rel. diff %.2e' % w_blind)
    print('        optimal label-dependent forms (SDP) vs Var(E[t|Y]) + sum_y P(y) M_b(dhat^y): max rel. diff %.2e' % w_lab)
    print('        closed-form ratio blind/label over the %d random laws: min %.4f max %.4f' % (trials, min(ratios), max(ratios)))


def test3(trials=40):
    worst = np.inf; worst_blind_forms = np.inf; below_forms = 0; minratio = np.inf
    for _ in range(trials):
        m = int(rng.integers(4, 7)); b = int(rng.integers(2, min(m, 5))); P, p, py = ci_law(m, rng, 0.05, 0.95)
        d = random_contrast(m, b, rng, kind=rng.choice(['tree', 'poly']))
        basis = ci_basis(m, P); v, delta, t = gradient(P, basis, d); cf = closed_forms(P, d, b)
        # random mixtures of random interviews (trees and r-round), label-blind and label-dependent
        for labdep in (False, True):
            n = int(rng.integers(3, 12)); q = rng.dirichlet(np.ones(n)); I = 0
            for i in range(n):
                r = int(rng.integers(1, b + 1)); sizes = list(compositions(b, r)[rng.integers(len(compositions(b, r)))])
                a0 = random_interview(m, b, sizes, rng); a1 = random_interview(m, b, [1] * b, rng) if labdep else a0
                I = I + q[i] * info_matrix(P, basis, [cells_of(m, a0), cells_of(m, a1)])
            val = value(I, v)
            worst = min(worst, val / cf['lab'])
        # optimise over a random menu of label-blind trees + all forms: can blind trees beat blind forms? never below `lab`?
        menu = [cells_of(m, random_interview(m, b, [1] * b, rng)) for _ in range(60)] + [cells_of(m, [S] * (1 << m)) for S in itertools.combinations(range(m), b)]
        mats = [info_matrix(P, basis, [c, c]) for c in menu]
        val, q = copt(mats, v)
        assert val >= cf['lab'] * (1 - 1e-6), (val, cf)
        assert val <= cf['blind'] * (1 + 1e-6)
        if val < cf['blind'] * (1 - 1e-5): below_forms += 1
        minratio = min(minratio, val / cf['blind'])
    print('TEST 3  random mixtures of trees / r-round interviews (blind and label-dependent): min value / W^{ci,lab} = %.6f (must be >= 1)' % worst)
    print('        optimum over 60 random label-blind trees + all forms: strictly below the label-blind forms optimum in %d of %d laws; smallest ratio to W_fixed %.4f; never below W^{ci,lab}' % (below_forms, trials, minratio))


if __name__ == '__main__':
    test1(); test2(); test3()
