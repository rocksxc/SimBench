"""v14 (R1): exact round constants of the binary pointer tree B_L (L = b-1 levels, m = 2^b - 1 coordinates) at small b.
M_r(U), the optimal second moment of an r-round design at the uniform law, is a lower bound on the worst-case
constant V_r (V_r = sup_P M_r(P)). For b <= 4 the cube is enumerated and the U-optimal design's worst profile gives an
upper bound on V_r; when the two agree, V_r is exact. Coordinates: heap order (root = 0), pointer value 0 -> left."""
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capdesign as cd


def pointer_tree(b):
    L = b - 1; m = (1 << b) - 1
    leaves = list(range((1 << L) - 1, m))  # heap indices (0-based) of the data bits
    paths = []
    for leaf in leaves:
        h = leaf + 1; lits = []
        while h > 1:
            parent = h // 2; lits.append((parent - 1, h % 2)); h = parent
        paths.append((leaf, lits[::-1]))
    return m, L, paths


def run(b, verbose=False):
    t0 = time.time(); m, L, paths = pointer_tree(b)
    lat = cd.Lattice(m, b); dhat = np.zeros(lat.nterms)
    for leaf, lits in paths:
        for s in range(1 << L):
            mk = (1 << leaf) + sum(1 << lits[i][0] for i in range(L) if s >> i & 1)
            sg = (-1) ** sum(lits[i][1] for i in range(L) if s >> i & 1)
            dhat[lat.term(np.array([mk]))[0]] += sg / (1 << L)
    E = cd.Engine(m, b, X=np.zeros((1, m), np.int64), y=np.zeros(1, np.int64), alpha=1.0, dvals=np.zeros(1), dhat=dhat)
    row = dict(b=b, m=m, second=E.second, forms=E.L)
    row['Gamma_U'] = E.gamma()[0]
    ps = [E.form_interview(int(E.lat.rank(b, np.array([(1 << leaf) + sum(1 << p for p, _ in lits)]))[0])) for leaf, lits in paths]
    fx = E.colgen(1, ps, max_iter=500); row['M1'] = fx['upper']; row['M1_lower'] = fx['lower']
    prev = [fx['interviews'][i] for i in np.flatnonzero(fx['sol']['q'] > 1e-7)]
    designs = {1: fx}
    for r in range(2, b + 1):
        res = E.colgen(r, prev, max_iter=600, verbose=verbose)
        row[f'M{r}'] = res['upper']; row[f'M{r}_lower'] = res['lower']; row[f'M{r}_iters'] = res['iterations']; row[f'M{r}_optimal'] = res['optimal']
        designs[r] = res; prev = [res['interviews'][i] for i in np.flatnonzero(res['sol']['q'] > 1e-7)]
        print(b, r, res['upper'], res['lower'], res['iterations'], '%.0fs' % (time.time() - t0), flush=True)
    if m <= 15:  # worst profile of the U-optimal design: an upper bound on V_r
        grid = ((np.arange(1 << m)[:, None] >> np.arange(m)) & 1).astype(np.int64)
        for r, res in designs.items():
            sol = res['sol']; worst = np.zeros(1 << m); 
            for z in range(2):
                acc = np.zeros(1 << m)
                for c in range(len(sol['fidx'])):
                    T = E.forms[sol['fidx'][c]]; hit = (grid[:, T] @ (1 << np.arange(b))) == sol['u'][c]
                    acc[hit] += sol['g'][z, c] ** 2 / sol['q'][sol['group'][c]]
                worst = np.maximum(worst, acc)
            row[f'V{r}_upper'] = float(worst.max()); row[f'V{r}_spread'] = float(worst.max() - worst.min())
    row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for b in [int(v) for v in sys.argv[2].split(',')]:
        r = run(b); (out / f'pointer_b{b}.json').write_text(json.dumps(r, indent=1))
        print(json.dumps({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()}), flush=True)
