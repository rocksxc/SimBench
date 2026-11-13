"""v18 (round-7 R2 Q3, R3 Q4): a cross-fitted model-assisted estimator on fixed forms that uses only the audit's own
records. Same trees, fitted form probabilities q and targets as curve_v17.py. The n records are split into two folds.
On each fold the pairwise log-linear model for the label and the rule's items is fitted by EM; the fitted law (items
the rule ignores are taken independent and uniform, 1% uniform mass added) gives cell masses for every form, and the
tables that minimise the variance for the given q at these masses are computed in closed form,
    g_z = W_z F' (F W_z F')^{-1} (+-coef),   W_z = diag(q / mass_z).
The tables of one fold score the records of the other fold. Tables satisfy the unbiasedness identities exactly, and
are independent of the records they score, so the estimator is unbiased at every population whatever the model.
Reported: bias, SD, RMSE and coverage of the normal interval from the pooled sample variance of the scores, next to
the design-based score with reference tables ('fixed'), the mean of t under branching, and pairwise ML on the forms."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screening_mi as sm
from budget_trees import fwht
from curve_v16 import LogLin
from curve_v17 import em_inputs_mask
from pilot_v17 import em_law

NS = [1000, 4000, 16000]


def tables_for(menu, q, mass, coef):
    """Variance-optimal tables for form probabilities q at cell masses `mass` (2, L*C)."""
    F = menu.F; g = np.zeros_like(mass)
    for z in range(2):
        W = q[menu.group] / mass[z]; A = (F.multiply(W[None, :]) @ F.T).toarray()
        lam = np.linalg.solve(A, (2 * z - 1) * coef); g[z] = W * (F.T @ lam)
    return g


def run(root, b, s, shift, reps):
    t0 = time.time(); S = sm.setup('BRFSS', root, b, 20261108 + s, shift)
    X, y, idx, d, menu, q, g, tgt = S['X'], S['y'], S['idx'], S['d'], S['menu'], S['q'], S['g'], S['tgt']
    m = menu.m; L = menu.L; C = menu.C; tY = (2 * y - 1) * d[idx]; truth = float(tY[tgt].mean())
    cube = np.arange(1 << m); used = [j for j in range(m) if np.any(d[cube] != d[cube ^ (1 << j)])]; k = len(used)
    coef = (fwht(d) / (1 << m))[menu.terms]; model = LogLin(k + 1, 2)
    upos = {j: i for i, j in enumerate(used)}; fmask = np.array([sum(1 << upos[j] for j in f if j in upos) for f in menu.forms])
    xk = X[:, used].astype(np.int64) @ (1 << np.arange(k)); proj = menu.grid[:, used] @ (1 << np.arange(k))  # used-item code of every profile
    rep_prof = np.zeros(1 << k, np.int64)
    for i, j in enumerate(used): rep_prof |= ((np.arange(1 << k) >> i) & 1) << j
    dk = d[rep_prof]; tvec = np.r_[-dk, dk]
    def masses(rows, a):
        ci, cn = em_inputs_mask(k, fmask[a], xk[rows], y[rows]); p = em_law(model, ci, cn, max_iter=200, tol=1e-6)
        Pfull = np.stack([p[:1 << k][proj], p[1 << k:][proj]]) / (1 << (m - k)); Pfull = 0.99 * Pfull + 0.01 / (2 << m)
        return menu.cellmass(Pfull), float(p @ tvec)
    rng = np.random.default_rng(20261108 + s + 7919 * b + (1 if shift else 0) + 77); res = {}
    for n in NS:
        est = {kk: [] for kk in ['branch', 'fixed', 'cf', 'em2']}; cov = {'fixed': 0, 'cf': 0, 'branch': 0}
        for _ in range(reps):
            rows = tgt[rng.integers(0, len(tgt), n)]; yr = y[rows]
            tb = tY[rows]; est['branch'].append(tb.mean()); cov['branch'] += abs(tb.mean() - truth) <= 1.96 * tb.std(ddof=1) / np.sqrt(n)
            a = rng.choice(L, size=n, p=q); codes = menu.codes[a, idx[rows]]; cell = a * C + codes
            H = g[yr, cell] / q[a]; est['fixed'].append(H.mean()); cov['fixed'] += abs(H.mean() - truth) <= 1.96 * H.std(ddof=1) / np.sqrt(n)
            fold = rng.permutation(n) < n // 2; Hc = np.empty(n); em = []
            for f0 in (fold, ~fold):
                ms, e2 = masses(rows[f0], a[f0]); em.append(e2); gt = tables_for(menu, q, ms, coef)
                Hc[~f0] = gt[yr[~f0], cell[~f0]] / q[a[~f0]]
            est['cf'].append(Hc.mean()); cov['cf'] += abs(Hc.mean() - truth) <= 1.96 * Hc.std(ddof=1) / np.sqrt(n)
            est['em2'].append(float(np.mean(em)))  # average of the two half-sample pairwise fits (for reference only)
        res[str(n)] = {kk: dict(bias=float(np.mean(v) - truth), sd=float(np.std(v, ddof=1)), rmse=float(np.sqrt(np.mean((np.array(v) - truth) ** 2)))) for kk, v in est.items()}
        for kk in cov: res[str(n)][kk]['coverage'] = cov[kk] / reps
        print(b, s, shift, n, ' '.join('%s rmse %.4f bias %.4f' % (kk, res[str(n)][kk]['rmse'], res[str(n)][kk]['bias']) for kk in est), 'cov fixed %.3f cf %.3f' % (res[str(n)]['fixed']['coverage'], res[str(n)]['cf']['coverage']), '%.0fs' % (time.time() - t0), flush=True)
    return dict(dataset='BRFSS', b=b, seed=20261108 + s, shift=shift, truth=truth, items=k, reps=reps, curve=res, seconds=time.time() - t0)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--bs', default='4,5'); p.add_argument('--seedlist', default='0,1,2'); p.add_argument('--targets', default='iid,shift'); p.add_argument('--reps', type=int, default=200)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for b in [int(v) for v in a.bs.split(',')]:
        for t in a.targets.split(','):
            for s in [int(v) for v in a.seedlist.split(',')]:
                dest = out / f'BRFSS_b{b}_{t}_{s}.json'
                if dest.exists(): continue
                dest.write_text(json.dumps(run(a.data, b, s, t == 'shift', a.reps), indent=1, default=float))
