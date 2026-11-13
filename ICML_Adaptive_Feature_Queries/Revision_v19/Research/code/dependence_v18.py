"""v18 (round-7 R1 Q3, R2 Q1): the model-based gap at laws with dependence.

(1) Gadget path. Address contrast with kappa = b - 1 address bits a and D = 2^kappa data bits z, plus auxiliary
    features: a one-hot copy s of the address (D bits) and products p_j = s_j AND z_j (D bits). The pairwise law
        P_beta(x) proportional to exp(beta * H(x)),  label uniform and independent,
        H = sum_j s_j <a, j> - (kappa + 1) (sum_j s_j - 1)^2 - sum_j (3 p_j + s_j z_j - 2 p_j s_j - 2 p_j z_j),
    lies in the pairwise log-linear model for every beta; at beta = 0 it is uniform, and as beta grows it concentrates
    on {s = one-hot(a), p_j = s_j z_j}, where t = Y z_a = Y (2 sum_j p_j - 1) is a polynomial of degree two.
    Theorem: liminf_beta W^(2)_fixed / W^(2)_branch >= 2^(b-1) / b. Here the constants are computed along the path.
(2) Fitted path. The address contrast with label Y = d(X) xi, P(xi = 1) = acc (not a pairwise law), projected on the
    pairwise and three-way models by maximum likelihood; constants at the fits."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model_v17 as mv


def gadget(b, beta):
    kap = b - 1; D = 1 << kap; K = kap + 3 * D; g = mv.bits(K)
    a = g[:, :kap]; s = g[:, kap:kap + D]; z = g[:, kap + D:kap + 2 * D]; p = g[:, kap + 2 * D:]
    idx = a @ (1 << np.arange(kap)); jb = mv.bits(kap)  # D x kap address bits of every data index
    agree = kap - 2 * (a[:, None, :] != jb[None, :, :]).sum(2)  # <a, j> in the +-1 encoding
    H = (s * agree).sum(1) - (kap + 1) * (s.sum(1) - 1) ** 2 - (3 * p + s * z - 2 * p * s - 2 * p * z).sum(1)
    w = np.exp(beta * (H - H.max())); w = w / w.sum(); cube = np.stack([w / 2, w / 2])
    d = 1.0 - 2.0 * z[np.arange(1 << K), idx]  # d = z_a in the +-1 encoding (bit 1 <-> -1), as in model_v17.address_cube
    return K, cube, d


def address_tree(E, kap, zoff):
    """Cells of the tree that reads the kap address bits (coordinates 0..kap-1) and then data bit zoff + address."""
    cf = []; cu = []
    for al in range(1 << kap):
        co = list(range(kap)) + [zoff + al]; f = int(E.lat.rank(E.b, np.array([sum(1 << c for c in co)]))[0])
        for zb in (0, 1):
            cf.append(f); cu.append(al + (zb << kap))  # pattern bit i <-> i-th smallest coordinate; the data bit is the largest
    return (np.array(cf, np.int64), np.array(cu, np.int64))


def run_gadget(b, betas, orders=(2,), budget=900):
    out = []
    for beta in betas:
        t0 = time.time(); K, cube, d = gadget(b, beta); row = dict(b=b, beta=beta, items=K, min_mass=float(cube.min()))
        kap = b - 1; E0 = mv.ModelEngine(K, b, cube, d, 1); cells = address_tree(E0, kap, kap + (1 << kap)); assert E0.check_interview(cells)
        for k in orders:
            o, E, fx, br = mv.analyse(K, b, cube, d, k, tree_cells=cells, time_budget=budget)
            row[f'order{k}'] = o
        row['seconds'] = time.time() - t0; out.append(row)
        print('gadget b=%d beta=%.2f' % (b, beta), ' | '.join('k=%d fixed %.4f branch %.4f [lower %.4f] ratio %.3f tree %s' % (k, row[f'order{k}']['fixed'], row[f'order{k}']['branch'], row[f'order{k}']['branch_lower'], row[f'order{k}']['fixed'] / row[f'order{k}']['branch'], row[f'order{k}'].get('rule_tree')) for k in orders), '%.0fs' % row['seconds'], flush=True)
    return out


def run_fitted(b, accs, orders=(2, 3)):
    K, U, d = mv.address_cube(b); out = []
    E0 = mv.ModelEngine(K, b, U, d, 1); cells = address_tree(E0, b - 1, b - 1); assert E0.check_interview(cells)
    for acc in accs:
        t0 = time.time(); row = dict(b=b, acc=acc, items=K)
        emp = np.r_[np.where(d < 0, acc, 1 - acc), np.where(d > 0, acc, 1 - acc)] / (1 << K)  # P(Y = d) = acc; label index 1 <-> Y = +1
        t = np.r_[-d, d]; row['delta'] = float(emp @ t)
        row['design'] = mv.design_based_fixed(K, b, emp.reshape(2, -1), d)[0]
        for k in orders:
            P = mv.loglin_fit(emp, k).reshape(2, -1); o, *_ = mv.analyse(K, b, P, d, k, tree_cells=cells, time_budget=900); row[f'order{k}'] = o
        row['seconds'] = time.time() - t0; out.append(row)
        print('fitted b=%d acc=%.2f design %.3f' % (b, acc, row['design']), ' | '.join('k=%d fixed %.4f branch %.4f ratio %.3f' % (k, row[f'order{k}']['fixed'], row[f'order{k}']['branch'], row[f'order{k}']['fixed'] / row[f'order{k}']['branch']) for k in orders), '%.0fs' % row['seconds'], flush=True)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); p.add_argument('--what', default='gadget3')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.what == 'gadget3': res = run_gadget(3, [0, 0.5, 1, 1.5, 2, 3, 4, 6], budget=400)
    elif a.what == 'fitted3': res = run_fitted(3, [0.5, 0.6, 0.7, 0.8, 0.9, 0.97])
    elif a.what == 'fitted4': res = run_fitted(4, [0.5, 0.7, 0.9, 0.97])
    (out / f'{a.what}.json').write_text(json.dumps(res, indent=1, default=float))
