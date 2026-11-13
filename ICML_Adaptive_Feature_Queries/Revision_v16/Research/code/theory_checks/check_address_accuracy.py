"""v16 check of Proposition `prop:labelnoise`: the address contrast keeps its gap at accurate populations.
X uniform on the cube, Y = d(X) with probability p (independent flips). For b = 2 (m = 3) and b = 3 (m = 6) the
solver computes W_fixed, W_2 and W_branch exactly (no smoothing); the proposition predicts W_fixed/W_branch = 2^(b-1)
for every p in (0, 1), and rho_P^2 = 2^-(b-1)."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capdesign as cd

def address(kappa):
    D = 1 << kappa; m = kappa + D; grid = ((np.arange(1 << m)[:, None] >> np.arange(m)) & 1)
    a = grid[:, :kappa] @ (1 << np.arange(kappa)); z = grid[np.arange(1 << m), kappa + a]
    return m, 1.0 - 2.0 * z  # d = +1 if the addressed bit is 0

def wht_full(d, m):
    a = d.astype(float).copy(); h = 1; n = 1 << m
    while h < n:
        a = a.reshape(-1, 2, h); x = a[:, 0, :].copy(); y = a[:, 1, :].copy(); a[:, 0, :] = x + y; a[:, 1, :] = x - y; a = a.reshape(n); h *= 2
    return a / n

for kappa in (1, 2):
    b = kappa + 1; m, d = address(kappa); lat = cd.Lattice(m, b); dhat = wht_full(d, m)[lat.allmasks]
    for p in (0.5, 0.6, 0.75, 0.9, 0.97):
        cube = np.zeros((2, 1 << m)); u = 1.0 / (1 << m)
        cube[1] = u * np.where(d > 0, p, 1 - p); cube[0] = u * np.where(d > 0, 1 - p, p)  # label 1 <-> y = +1
        E = cd.Engine(m, b, cube=cube, dvals=d, dhat=dhat, alpha=0.0)
        d2 = E.delta ** 2; var = E.second - d2
        forms = [E.form_interview(f) for f in range(E.L)]
        fx = E.colgen(1, forms); sup = [forms[i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
        br = E.colgen(b, sup, gap=1e-9)
        gam, _ = E.gamma(); rho2 = (gam * E.second - d2) / var
        print('b=%d m=%d p=%.2f Delta=%.3f  W_fixed/W_branch = %.6f  W_branch/Var(t) = %.6f  1/rho^2 = %.6f' % (b, m, p, E.delta, (fx['upper'] - d2) / (br['upper'] - d2), (br['upper'] - d2) / var, 1 / rho2), flush=True)
