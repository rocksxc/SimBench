"""v16 (round-5 R2/R3): at what audit size does the design-based ordering become the operative one?
For every BRFSS tree at b = 4, 5 (random-half and other-sex targets, seeds 0-2; trees and fitted fixed-form designs as
in screening_mi.setup), audits of n target respondents are simulated on the fitted fixed forms. Estimators on the same
records: the design-based form score, and maximum likelihood under log-linear working models for the label and the
items the rule depends on, with all two-way and with all three-way interactions (EM, one IPF sweep per M-step).
Branching (the mean of t over n respondents) is simulated on the same respondents. Reported per n: bias, SD and RMSE
over `reps` replications. No intervals are computed here (see audit_v15.py for coverage at n = 1000 and 16,000)."""
import argparse, json, sys, time
from itertools import combinations
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screening_mi as sm

NS = [500, 1000, 2000, 4000, 8000, 16000, 32000]


class LogLin:
    """Hierarchical log-linear model on K binary variables with all interactions of the given order, fitted by EM."""
    def __init__(self, K, order):
        self.K = K; n = 1 << K; bits = ((np.arange(n)[:, None] >> np.arange(K)) & 1).astype(np.int64)
        order = min(order, K)
        self.idx = [sum(bits[:, v] << p for p, v in enumerate(c)) for c in combinations(range(K), order)]; self.size = 1 << order

    def mstep(self, p, N):
        tot = N.sum(); targ = [np.bincount(ix, weights=N, minlength=self.size) / tot for ix in self.idx]
        for ix, tg in zip(self.idx, targ):
            cur = np.bincount(ix, weights=p, minlength=self.size)
            p = p * np.divide(tg, cur, out=np.zeros(self.size), where=cur > 0)[ix]
        return p / p.sum()

    def fit(self, cellidx, counts, tvec, max_iter=500, tol=1e-5):
        p = np.full(1 << self.K, 1.0 / (1 << self.K)); old = np.inf; calm = 0
        for it in range(max_iter):
            w = np.zeros_like(p)
            for ix, c in zip(cellidx, counts):
                marg = np.bincount(ix, weights=p, minlength=len(c)); w += np.divide(c, marg, out=np.zeros(len(c)), where=marg > 0)[ix]
            p = self.mstep(p, p * w); est = float(p @ tvec)
            calm = calm + 1 if abs(est - old) < tol else 0
            if calm >= 3: break
            old = est
        return est, it + 1


def em_inputs(used, forms, a, Xr, yv):
    k = len(used); upos = {j: i for i, j in enumerate(used)}; n = len(a)
    fmask = np.array([sum(1 << upos[j] for j in f if j in upos) for f in forms]); ua = fmask[a]
    full = np.arange(1 << (k + 1)); lab = full >> k; prof = full & ((1 << k) - 1)
    xr = Xr[:, used].astype(np.int64) @ (1 << np.arange(k))
    def compress(v, mk):
        out = np.zeros_like(v); j = 0
        for i in range(k):
            if mk >> i & 1: out |= ((v >> i) & 1) << j; j += 1
        return out, j
    cellidx = []; counts = []
    for mk in np.unique(ua):
        c, j = compress(prof, int(mk)); s = ua == mk; rc, _ = compress(xr[s], int(mk))
        cellidx.append(c + (lab << j)); counts.append(np.bincount(rc + (yv[s].astype(np.int64) << j), minlength=2 << j).astype(float))
    return cellidx, counts


def run(root, b, s, shift, reps):
    t0 = time.time(); S = sm.setup('BRFSS', root, b, 20261108 + s, shift)
    X, y, idx, d, menu, q, g, tgt = S['X'], S['y'], S['idx'], S['d'], S['menu'], S['q'], S['g'], S['tgt']
    m = menu.m; L = menu.L; C = menu.C; tY = (2 * y - 1) * d[idx]; truth = float(tY[tgt].mean())
    cube = np.arange(1 << m); used = [j for j in range(m) if np.any(d[cube] != d[cube ^ (1 << j)])]; k = len(used)
    rep_prof = np.zeros(1 << k, np.int64)
    for i, j in enumerate(used): rep_prof |= ((np.arange(1 << k) >> i) & 1) << j
    dk = d[rep_prof]; tvec = np.r_[-dk, dk]; models = {'em2': LogLin(k + 1, 2), 'em3': LogLin(k + 1, 3)}
    rng = np.random.default_rng(20261108 + s + 7919 * b + (1 if shift else 0)); res = {}
    for n in NS:
        est = {kk: [] for kk in ['branch', 'fixed', 'em2', 'em3']}; its = []
        for _ in range(reps):
            rows = tgt[rng.integers(0, len(tgt), n)]; est['branch'].append(tY[rows].mean())
            a = rng.choice(L, size=n, p=q); codes = menu.codes[a, idx[rows]]
            est['fixed'].append((g[y[rows], a * C + codes] / q[a]).mean())
            ci, cn = em_inputs(used, menu.forms, a, X[rows], y[rows])
            for kk, mod in models.items():
                e, it = mod.fit(ci, cn, tvec); est[kk].append(e); its.append(it)
        res[str(n)] = {kk: dict(bias=float(np.mean(v) - truth), sd=float(np.std(v, ddof=1)), rmse=float(np.sqrt(np.mean((np.array(v) - truth) ** 2)))) for kk, v in est.items()}
        res[str(n)]['em_iterations_max'] = int(max(its))
        print(b, s, shift, n, ' '.join('%s %.4f' % (kk, res[str(n)][kk]['rmse']) for kk in ['branch', 'fixed', 'em2', 'em3']), 'bias2 %.4f bias3 %.4f' % (res[str(n)]['em2']['bias'], res[str(n)]['em3']['bias']), '%.0fs' % (time.time() - t0), flush=True)
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
                dest.write_text(json.dumps(run(a.data, b, s, t == 'shift', a.reps), indent=1))
