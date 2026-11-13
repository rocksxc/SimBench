import numpy as np, time
from chk_address import *
b = 4; kappa = 3; D = 8; m, X, d = address(kappa); n = 1 << m
for c in range(0, D):
    B = b + c; t0 = time.time(); en = energies(m, X, d, B); emax = max(en.values())
    dev = max(abs(e - sum(1 for i in T if i >= kappa) * 2.0 ** (sum(1 for i in T if i < kappa) - 2 * kappa)) for T, e in en.items())
    j = jc(c, b); Kp = 2 ** (b - 1 - j)
    line = 'b 4 c %d B %d forms %d: max energy %.6f (claim %.6f) formula dev %.1e; lower %.4f K+ %d ratio %.3f bound2 %.3f' % (c, B, len(en), emax, (c + 1) / D, dev, D / (c + 1), Kp, Kp * (c + 1) / D, 2 ** (b + 1) / (c + 3))
    print(line, flush=True)
    if B < m:
        mu = np.full(n, 1.0 / n)
        try:
            W = program(m, X, [d], [mu], B); print('   W_fixed(uniform) = %.5f  [%.0fs]' % (W, time.time() - t0), flush=True)
        except Exception as e: print('   W failed', repr(e)[:200], flush=True)
