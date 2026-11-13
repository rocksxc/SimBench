"""v15 (round-4 R2): within-sample model-based comparators for the simulated BRFSS audits.

Same audits as screening_mi_v13.simulate / shift_mi_v14 (tree and fitted fixed-form design from source records,
n target respondents per audit). New estimators, which use the target's own capped records only (no source):
  em_fit : maximum likelihood under the log-linear model with all main effects and two-way interactions among
           the label and the items that the screening rule uses (items it ignores carry no information about the
           target), fitted by EM (one IPF sweep per M-step) to the records of the fitted fixed-form design;
           the estimate is sum_v p(v) t(v). Missingness is by design, so no transport assumption is needed; the
           model is the working assumption.
  em_unif: the same estimator on records of the uniform design over all C(12,b) forms (balanced random forms).
Intervals: delete-a-group jackknife with G groups (warm-started EM), Student-t quantile with G-1 degrees of freedom.
The branching and fitted-fixed design-based estimators are recomputed on the same audits for reference."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screening_mi as sm
import shift_mi_v14 as sh
from scipy.stats import t as student_t


class LogLin:
    """Two-way log-linear model on K binary variables, fitted by EM from partially observed records."""
    def __init__(self, K):
        self.K = K; n = 1 << K
        self.bits = ((np.arange(n)[:, None] >> np.arange(K)) & 1).astype(np.int64)
        self.pairs = [(j, k) for j in range(K) for k in range(j + 1, K)]
        self.pidx = [self.bits[:, j] + 2 * self.bits[:, k] for j, k in self.pairs]

    def mstep(self, p, N, sweeps=1):
        tot = N.sum()
        targ = [np.bincount(ix, weights=N, minlength=4) / tot for ix in self.pidx]
        for _ in range(sweeps):
            for ix, tg in zip(self.pidx, targ):
                cur = np.bincount(ix, weights=p, minlength=4)
                fac = np.divide(tg, cur, out=np.zeros(4), where=cur > 0)
                p = p * fac[ix]
        return p / p.sum()

    def fit(self, cellidx, counts, tvec, p0=None, max_iter=500, tol=1e-5):
        """cellidx: list of (n_cells,) int arrays mapping every full cell to an observed-cell code, one per form;
        counts: matching list of count vectors. Returns (p, estimate, iterations)."""
        p = np.full(1 << self.K, 1.0 / (1 << self.K)) if p0 is None else p0.copy()
        est_old = np.inf; calm = 0
        for it in range(max_iter):
            w = np.zeros_like(p)
            for ix, c in zip(cellidx, counts):
                marg = np.bincount(ix, weights=p, minlength=len(c))
                w += np.divide(c, marg, out=np.zeros(len(c)), where=marg > 0)[ix]
            p = self.mstep(p, p * w)
            est = float(p @ tvec)
            calm = calm + 1 if abs(est - est_old) < tol else 0
            if calm >= 3: break
            est_old = est
        return p, est, it + 1


def em_estimate(model, used, forms, a, Xr, yv, tvec, rng, G=8):
    """Log-linear EM on the items the rule uses. used: sorted item indices (k of them); forms: list of coordinate
    tuples; a: form index per record; Xr: (n, m) answers of the sampled respondents (only the coordinates of the
    assigned form are read); yv: labels. The model has k + 1 binary variables (items, then the label).
    Returns (estimate, half-width, iterations)."""
    k = len(used); upos = {j: i for i, j in enumerate(used)}; n = len(a)
    # the part of each form that the rule uses, as a bitmask over the used items
    fmask = np.array([sum(1 << upos[j] for j in f if j in upos) for f in forms])
    ua = fmask[a]; full = np.arange(1 << (k + 1)); lab = full >> k; prof = full & ((1 << k) - 1)
    xr = (Xr[:, used].astype(np.int64) @ (1 << np.arange(k)))
    masks = np.unique(ua)
    def compress(v, mk):  # keep the bits of v selected by mk, packed
        out = np.zeros_like(v); j = 0
        for i in range(k):
            if mk >> i & 1: out |= ((v >> i) & 1) << j; j += 1
        return out, j
    cellidx = []; rec_code = np.zeros(n, np.int64); sizes = []
    for mk in masks:
        c, j = compress(prof, int(mk)); cellidx.append(c + (lab << j)); sizes.append(2 << j)
        s = ua == mk; rc, _ = compress(xr[s], int(mk)); rec_code[s] = rc + (yv[s].astype(np.int64) << j)
    def cnt(sel):
        return [np.bincount(rec_code[sel & (ua == mk)], minlength=sz).astype(float) for mk, sz in zip(masks, sizes)]
    p, est, its = model.fit(cellidx, cnt(np.ones(n, bool)), tvec)
    grp = rng.permutation(n) % G; reps = []
    for gg in range(G):
        _, e, _ = model.fit(cellidx, cnt(grp != gg), tvec, p0=p, max_iter=80); reps.append(e)
    reps = np.array(reps); v = (G - 1) / G * np.sum((reps - reps.mean()) ** 2)
    return est, float(student_t.ppf(0.975, G - 1) * np.sqrt(v)), its


def simulate(S, n=1000, reps=200, seed=0, G=8):
    rng = np.random.default_rng(seed + 99); rng2 = np.random.default_rng(seed + 4242)
    X, y, idx, d, menu, q, g = S['X'], S['y'], S['idx'], S['d'], S['menu'], S['q'], S['g']
    tgt = S['tgt']; tY = (2 * y - 1) * d[idx]; truth = float(tY[tgt].mean()); L = menu.L; C = menu.C; m = menu.m
    # items the rule depends on: flipping the item changes d somewhere on the cube
    cube = np.arange(1 << m); used = [j for j in range(m) if np.any(d[cube] != d[cube ^ (1 << j)])]; k = len(used)
    # contrast as a function of the used items: any profile with those bits (others zero)
    rep_prof = np.zeros(1 << k, np.int64)
    for i, j in enumerate(used): rep_prof |= ((np.arange(1 << k) >> i) & 1) << j
    dk = d[rep_prof]; tvec = np.r_[-dk, dk]  # label 0 -> t = -d, label 1 -> t = d
    model = LogLin(k + 1)
    keys = ['branch', 'fixed', 'em_fit', 'em_unif']
    out = {kk: [] for kk in keys}; cover = {kk: 0 for kk in keys}; width = {kk: [] for kk in keys}; its = []
    for rep in range(reps):
        rows = tgt[rng.integers(0, len(tgt), n)]
        tb = tY[rows]; est = tb.mean(); se = tb.std(ddof=1) / np.sqrt(n)
        out['branch'].append(est); cover['branch'] += abs(est - truth) <= 1.96 * se; width['branch'].append(2 * 1.96 * se)
        a = rng.choice(L, size=n, p=q); codes = menu.codes[a, idx[rows]]
        H = g[y[rows], a * C + codes] / q[a]; est = H.mean(); se = H.std(ddof=1) / np.sqrt(n)
        out['fixed'].append(est); cover['fixed'] += abs(est - truth) <= 1.96 * se; width['fixed'].append(2 * 1.96 * se)
        est, hw, it = em_estimate(model, used, menu.forms, a, X[rows], y[rows], tvec, rng2, G)
        out['em_fit'].append(est); cover['em_fit'] += abs(est - truth) <= hw; width['em_fit'].append(2 * hw); its.append(it)
        au = rng2.integers(0, L, n)
        est, hw, it = em_estimate(model, used, menu.forms, au, X[rows], y[rows], tvec, rng2, G)
        out['em_unif'].append(est); cover['em_unif'] += abs(est - truth) <= hw; width['em_unif'].append(2 * hw)
    res = dict(truth=truth, n=n, reps=reps, G=G, items_used=k, em_iterations_median=float(np.median(its)), em_iterations_max=int(np.max(its)))
    for kk in keys:
        v = np.array(out[kk]); res[kk] = dict(bias=float(v.mean() - truth), sd=float(v.std(ddof=1)), rmse=float(np.sqrt(np.mean((v - truth) ** 2))),
                                             coverage=cover[kk] / reps, width=float(np.mean(width[kk])), mc_se_cov=float(np.sqrt(0.95 * 0.05 / reps)))
    return res


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--reps', type=int, default=200); p.add_argument('--bs', default='4,5'); p.add_argument('--shifts', default='iid,sex,education,costbar,physhlth')
    p.add_argument('--n', type=int, default=1000)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for shn in a.shifts.split(','):
        for b in [int(v) for v in a.bs.split(',')]:
            dest = out / f'BRFSS_b{b}_{shn}_n{a.n}.json'
            if dest.exists(): continue
            t0 = time.time()
            S = sm.setup('BRFSS', a.data, b, 20261108, False) if shn == 'iid' else sh.setup(a.data, b, 20261108, shn)[0]
            r = simulate(S, n=a.n, reps=a.reps); r.update(dataset='BRFSS', b=b, shift=shn, seconds=time.time() - t0)
            dest.write_text(json.dumps(r, indent=1))
            print(shn, b, 'truth %.4f' % r['truth'], ' '.join('%s bias %.4f sd %.4f rmse %.4f cov %.3f' % (k, r[k]['bias'], r[k]['sd'], r[k]['rmse'], r[k]['coverage']) for k in ['branch', 'fixed', 'em_fit', 'em_unif']),
                  'EM its %.0f/%d' % (r['em_iterations_median'], r['em_iterations_max']), '%.0fs' % r['seconds'], flush=True)
