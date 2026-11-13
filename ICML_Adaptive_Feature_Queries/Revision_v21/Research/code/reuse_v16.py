"""v16 (round-5 R3): are records collected under a design optimized for one rule usable for another rule?
BRFSS, other-sex target (the same target population for every seed), caps b = 4, 5; the three trees of seeds 0-2 are
three different screening rules A, B, C. For every ordered pair (A, B):
  own      : W_fixed for B under B's own optimal fixed design (all forms), relative to branching for B;
  reuse    : the best pointwise-unbiased scores for B on records collected under A's optimal design, mixed with a
             5% uniform floor over all forms so that every contrast of degree <= b stays identifiable;
For every unordered pair: the fixed design that minimizes the sum of the two records ratios (one shared form
distribution, separate score tables), a second-order cone program over all forms.
Branching benchmark for two rules: administering rule A's tree to half of the respondents and rule B's tree to the
other half gives each rule a records ratio of 2 (sum 4)."""
import json, sys, time
from itertools import combinations
from pathlib import Path
import numpy as np
import scipy.sparse as sp
import cvxpy as cp
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
import capdesign as cd
from screening_v14 import splits
from screening_v15 import fixed_given_q
from sklearn.tree import DecisionTreeClassifier


def joint(Es, tol=1e-9):
    """min_q sum_j W_j(q)/sigma_j^2 over fixed-form designs on all forms; returns per-rule records ratios."""
    E0 = Es[0]; L, C = E0.L, E0.C; Mc = L * C
    F = sp.csc_matrix(((np.tile(E0.sign, (L, 1, 1)) / C).ravel(), (np.tile(E0.sub[:, None, :], (1, C, 1)).ravel(), np.repeat(np.arange(Mc), C))), shape=(E0.lat.nterms, Mc))
    q = cp.Variable(L, nonneg=True); Q = sp.csc_matrix((np.ones(Mc), (np.arange(Mc), np.repeat(np.arange(L), C))), shape=(Mc, L)) @ q
    cons = [cp.sum(q) == 1]; obj = 0; gs = []
    for E in Es:
        var = E.second - E.delta ** 2; g = cp.Variable((2, Mc)); u = cp.Variable((2, Mc), nonneg=True); gs.append(g)
        for z in range(2):
            cons += [F @ g[z] == (2 * z - 1) * E.dhat, cp.SOC(Q + u[z], cp.vstack([2 * g[z], Q - u[z]]), axis=0)]
        obj = obj + cp.sum(cp.multiply(E.P.reshape(2, Mc), u)) / var
    prob = cp.Problem(cp.Minimize(obj), cons); prob.solve(solver='CLARABEL', tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol, max_iter=500)
    qq = np.maximum(q.value, 1e-15); qq /= qq.sum()
    # exact per-rule values: best tables for the optimized q (closed form), so every reported ratio is that of an exactly unbiased design
    return [(fixed_given_q(E, qq)[0] - E.delta ** 2) / (E.second - E.delta ** 2) for E in Es], prob.status


if __name__ == '__main__':
    root, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    bs = [int(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else [4, 5]
    X, y, names, sex = bt.load('BRFSS', root); m = X.shape[1]
    for b in bs:
        dest = out / f'BRFSS_b{b}_shift.json'
        if dest.exists(): continue
        t0 = time.time(); Es = []; own = []; qs = []
        for s in range(3):
            seed = 20261108 + s; tr, cal, tgt = splits('BRFSS', X, y, names, sex, seed, True)
            clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=seed).fit(X[tr], y[tr])
            lat = cd.Lattice(m, b); dhat, _ = cd.tree_fourier(clf, lat, m)
            E = cd.Engine(m, b, X=X[tgt], y=y[tgt], alpha=0.01, dvals=2 * clf.predict(X[tgt]).astype(float) - 1, dhat=dhat)
            fx = E.colgen(1, [E.form_interview(f) for f in range(E.L)]); qf = np.zeros(E.L)
            for i, c in enumerate(fx['interviews']): qf[c[0][0]] += fx['sol']['q'][i]
            Es.append(E); qs.append(qf / qf.sum()); own.append((fx['upper'] - E.delta ** 2) / (E.second - E.delta ** 2))
            print(b, s, 'own %.4f' % own[-1], '%.0fs' % (time.time() - t0), flush=True)
        row = dict(b=b, own=own, reuse={}, joint={}, agreement={})
        for i in range(3):
            for j in range(3):
                if i == j: continue
                qmix = 0.95 * qs[i] + 0.05 / Es[i].L
                row['reuse'][f'{i}->{j}'] = (fixed_given_q(Es[j], qmix)[0] - Es[j].delta ** 2) / (Es[j].second - Es[j].delta ** 2)
        for i, j in combinations(range(3), 2):
            r, st = joint([Es[i], Es[j]]); row['joint'][f'{i},{j}'] = r
            print(b, (i, j), 'joint', ['%.4f' % v for v in r], st, '%.0fs' % (time.time() - t0), flush=True)
        r, st = joint(Es); row['joint']['0,1,2'] = r; row['seconds'] = time.time() - t0
        print(b, 'all three', ['%.4f' % v for v in r], st, flush=True)
        dest.write_text(json.dumps(row, indent=1)); print(json.dumps(row)[:600], flush=True)
