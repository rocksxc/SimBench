"""Referee: explicit law in M_ci where label-blind forms need markedly more records than a label-blind branching design.
m = 1 + 2k. X_0 is a noisy copy of the label (error eps); the other coordinates are fair coins independent of Y.
d(x) = [(1+x_0)/2 * mean(x_A) + (1-x_0)/2 * mean(x_B)]   (degree 2, values in [-1,1])."""
import itertools, sys
import numpy as np
from ref_common import *
from test_b_theorem import copt

def run(k, b, eps):
    m = 1 + 2 * k; B = bitmat(m); X = 2.0 * B - 1; A = list(range(1, 1 + k)); Bc = list(range(1 + k, 1 + 2 * k))
    p = np.full((2, m), 0.5); p[0, 0] = eps; p[1, 0] = 1 - eps; py = np.array([0.5, 0.5])
    P = np.stack([py[y] * np.prod(np.where(B == 1, p[y], 1 - p[y]), axis=1) for y in (0, 1)])
    d = (1 + X[:, 0]) / 2 * X[:, A].mean(1) + (1 - X[:, 0]) / 2 * X[:, Bc].mean(1)
    basis = ci_basis(m, P); v, delta, t = gradient(P, basis, d); cf = closed_forms(P, d, b)
    forms = list(itertools.combinations(range(m), b))
    wforms, q = copt([info_matrix(P, basis, [c, c]) for c in [cells_of(m, [S] * (1 << m)) for S in forms]], v)
    # label-blind branching design: ask X_0, then a uniformly drawn (b-1)-subset of A if X_0=+1, of B if X_0=-1
    I = 0; n = 0
    for SA in itertools.combinations(A, b - 1):
        for SB in itertools.combinations(Bc, b - 1):
            asked = [((0,) + SA) if B[x, 0] == 1 else ((0,) + SB) for x in range(1 << m)]
            cl = cells_of(m, asked); I = I + info_matrix(P, basis, [cl, cl]); n += 1
    wtree = value(I / n, v)
    print('k=%d b=%d m=%d eps=%.3f: W_lab %.5f | label-blind forms: closed %.5f, SDP over all %d forms %.5f | label-blind branching design %.5f | forms/branching >= %.3f, forms/lab = %.3f'
          % (k, b, m, eps, cf['lab'], cf['blind'], len(forms), wforms, wtree, wforms / wtree, cf['blind'] / cf['lab']))

for k, b, eps in [(3, 3, 0.05), (3, 3, 0.01), (4, 4, 0.01), (4, 3, 0.01), (5, 5, 0.01)]:
    run(k, b, eps)
