"""Referee: pairwise model at product laws with an UNBALANCED label: optimal forms vs forms + random trees (SDP)."""
import itertools, warnings
import numpy as np
from ref_common import *
from test_b_theorem import copt
from test_b_more import pairwise_basis
warnings.simplefilter('ignore')
rng = np.random.default_rng(8); out = []
for _ in range(12):
    m = int(rng.integers(4, 6)); b = int(rng.integers(2, 4)); B = bitmat(m)
    p1 = rng.uniform(0.2, 0.8, m); py1 = rng.choice([0.2, 0.3, 0.75]); px = np.prod(np.where(B == 1, p1, 1 - p1), axis=1); P = np.stack([(1 - py1) * px, py1 * px])
    d = random_contrast(m, b, rng, kind='tree'); d = np.sign(d) ; basis = pairwise_basis(m, P); v, delta, t = gradient(P, basis, d)
    forms = [cells_of(m, [S] * (1 << m)) for S in itertools.combinations(range(m), b)]
    trees = [cells_of(m, random_interview(m, b, [1] * b, rng)) for _ in range(150)]
    vf, _ = copt([info_matrix(P, basis, [c, c]) for c in forms], v); vt, _ = copt([info_matrix(P, basis, [c, c]) for c in forms + trees], v)
    out.append(vf / vt); print('m %d b %d P(Y=1) %.2f: W2_fixed %.5f, forms + 150 random trees %.5f, ratio >= %.4f' % (m, b, py1, vf, vt, vf / vt))
print('max ratio', max(out))
