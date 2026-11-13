"""v17 (round-6 R2 Q1, R3 Q2): does within-record adaptivity help the estimator an analyst would use?
For every BRFSS tree at b = 4, 5 (random-half and other-sex targets, seeds 0-2; trees and fitted forms as in
screening_mi.setup) audits of n target respondents are simulated under three collection designs with the same cap:
  forms   : the fitted fixed forms optimised for the design-based score (as in curve_v16.py);
  mforms  : fixed forms optimised for the two-way working model (model_v17.ModelEngine at the two-way fit of the
            calibration records, 5% uniform floor over the b-subsets of the rule's items);
  branch  : the rule is administered; the path is padded to b questions with the rule's lowest-index unasked items.
Estimators: the design-based score (forms: fitted tables; branch: the mean of t), and maximum likelihood under the
two- and three-way log-linear working models for the label and the rule's items (EM), on each design's records.
Reported per n: bias, SD and RMSE over `reps` replications."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screening_mi as sm
import model_v17 as mv
from curve_v16 import LogLin

NS = [500, 1000, 2000, 4000, 8000, 16000, 32000]


def em_inputs_mask(k, ua, xr, yv):
    """Group records by observed item mask `ua` (over the k rule items); cells are (observed pattern, label)."""
    full = np.arange(1 << (k + 1)); lab = full >> k; prof = full & ((1 << k) - 1)
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


def path_masks(d, k, b):
    """Observed mask per profile of the k-cube when a minimum-depth decision tree for d on its k items (found by
    exhaustive recursion over subcubes) is administered and every path is padded to min(b, k) questions with the
    lowest-index unasked items. Raises AssertionError if d needs depth > b on these items."""
    from functools import lru_cache
    grid = mv.bits(k); code = np.arange(1 << k)
    def members(mask, val): return code[(code & mask) == val]
    @lru_cache(maxsize=None)
    def depth(mask, val):
        dv = d[members(mask, val)]
        if np.all(dv == dv[0]): return 0, -1
        best = (99, -1)
        for j in range(k):
            if mask >> j & 1: continue
            dj = 1 + max(depth(mask | (1 << j), val)[0], depth(mask | (1 << j), val | (1 << j))[0])
            if dj < best[0]: best = (dj, j)
        return best
    assert depth(0, 0)[0] <= b, 'rule not computable at depth b on its items'
    mask_of = np.zeros(1 << k, np.int64)
    def rec(mask, val):
        dep, j = depth(mask, val)
        if dep == 0:
            pad = mask; i = 0
            while bin(pad).count('1') < min(b, k):
                if not pad >> i & 1: pad |= 1 << i
                i += 1
            mask_of[members(mask, val)] = pad; return
        rec(mask | (1 << j), val); rec(mask | (1 << j), val | (1 << j))
    rec(0, 0)
    return mask_of


def run(root, b, s, shift, reps):
    t0 = time.time(); S = sm.setup('BRFSS', root, b, 20261108 + s, shift)
    X, y, idx, d, menu, q, g, tgt = S['X'], S['y'], S['idx'], S['d'], S['menu'], S['q'], S['g'], S['tgt']
    m = menu.m; L = menu.L; C = menu.C; tY = (2 * y - 1) * d[idx]; truth = float(tY[tgt].mean())
    cube = np.arange(1 << m); used = [j for j in range(m) if np.any(d[cube] != d[cube ^ (1 << j)])]; k = len(used)
    rep_prof = np.zeros(1 << k, np.int64)
    for i, j in enumerate(used): rep_prof |= ((np.arange(1 << k) >> i) & 1) << j
    dk = d[rep_prof]; tvec = np.r_[-dk, dk]; models = {'em2': LogLin(k + 1, 2), 'em3': LogLin(k + 1, 3)}
    upos = {j: i for i, j in enumerate(used)}; fmask = np.array([sum(1 << upos[j] for j in f if j in upos) for f in menu.forms])
    xk = X[:, used].astype(np.int64) @ (1 << np.arange(k))
    # branching: administer the rule (a depth-b tree on its items), padded to b questions
    try:
        pm = path_masks(dk, k, b); branch_ok = True
    except AssertionError:
        pm = None; branch_ok = False
    # forms optimised for the two-way working model at the calibration law
    cal = S['src'][20000:]; code = xk[cal] + (y[cal].astype(np.int64) << k)
    emp = 0.9 * np.bincount(code, minlength=2 << k) / len(cal) + 0.1 / (2 << k)
    if k > b:
        P2 = mv.loglin_fit(emp, 2).reshape(2, 1 << k); E = mv.ModelEngine(k, b, P2, dk, 2)
        fx = E.design(1, [E.form_interview(f) for f in range(E.L)]); qm = 0.95 * fx['q'] + 0.05 / E.L
        mmask = np.array([int(v) for v in E.fmask]); model_ratio_cal = fx['value'] / E.var
    else:
        qm = np.ones(1); mmask = np.array([(1 << k) - 1]); model_ratio_cal = None
    rng = np.random.default_rng(20261108 + s + 7919 * b + (1 if shift else 0) + 31); res = {}
    keys = ['branch', 'fixed', 'forms_em2', 'forms_em3', 'mforms_em2', 'mforms_em3'] + (['branch_em2', 'branch_em3'] if branch_ok else [])
    for n in NS:
        est = {kk: [] for kk in keys}
        for _ in range(reps):
            rows = tgt[rng.integers(0, len(tgt), n)]; yr = y[rows]; xr = xk[rows]; est['branch'].append(tY[rows].mean())
            a = rng.choice(L, size=n, p=q); codes = menu.codes[a, idx[rows]]
            est['fixed'].append((g[yr, a * C + codes] / q[a]).mean())
            data = {'forms': em_inputs_mask(k, fmask[a], xr, yr), 'mforms': em_inputs_mask(k, mmask[rng.choice(len(qm), size=n, p=qm)], xr, yr)}
            if branch_ok: data['branch'] = em_inputs_mask(k, pm[xr], xr, yr)
            for src, (ci, cn) in data.items():
                for kk, mod in models.items():
                    est[f'{src}_{kk}'].append(mod.fit(ci, cn, tvec)[0])
        res[str(n)] = {kk: dict(bias=float(np.mean(v) - truth), sd=float(np.std(v, ddof=1)), rmse=float(np.sqrt(np.mean((np.array(v) - truth) ** 2)))) for kk, v in est.items()}
        print(b, s, shift, n, ' '.join('%s %.4f' % (kk, res[str(n)][kk]['rmse']) for kk in keys), '%.0fs' % (time.time() - t0), flush=True)
    return dict(dataset='BRFSS', b=b, seed=20261108 + s, shift=shift, truth=truth, items=k, reps=reps, branch_ok=branch_ok,
                model_forms=int(np.sum(qm > 0.05 / len(qm) + 1e-9)), model_ratio_cal=model_ratio_cal, curve=res, seconds=time.time() - t0)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
    p.add_argument('--bs', default='4,5'); p.add_argument('--seedlist', default='0,1,2'); p.add_argument('--targets', default='iid,shift'); p.add_argument('--reps', type=int, default=400)
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for b in [int(v) for v in a.bs.split(',')]:
        for t in a.targets.split(','):
            for s in [int(v) for v in a.seedlist.split(',')]:
                dest = out / f'BRFSS_b{b}_{t}_{s}.json'
                if dest.exists(): continue
                dest.write_text(json.dumps(run(a.data, b, s, t == 'shift', a.reps), indent=1, default=float))
