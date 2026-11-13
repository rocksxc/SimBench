"""v21: what extra pre-committed questions buy on trained rules (round-10 R1 Q4, R2 Q2, R3 Q2).
For every rule (the BRFSS diabetes trees and the further rules of rules_v19.py) that depends on K > b items, with b the
depth of the rule: the optimal fixed forms of size B = b + c on the rule's items, c = 0, 1, 2, ..., relative to
Var_P(t), the constant of the branching interview that administers the rule with b questions. At B = K the form asks
every item of the rule and the ratio is one. Also the optimised path-set design at cap b (forms = the padded path
sets of the rule's tree, Proposition E.6), a certified upper bound on the fixed optimum that needs no enumeration of
forms beyond the path sets; it is computed for every rule, including those whose optimum over all forms is not."""
import argparse, json, sys, time
from math import comb
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import capdesign as cd
import model_v17 as mv
import fill_v20 as fv


def engine(K, B, emp, d):
    cube = emp.reshape(2, 1 << K); lat = cd.Lattice(K, B)
    return cd.Engine(K, B, cube=cube, dvals=d, dhat=(cd.wht(d) / (1 << K))[lat.allmasks], alpha=0.0)


def fixed_ratio(K, B, emp, d, forms=None):
    E0 = engine(K, B, emp, d); var = E0.second - E0.delta ** 2
    ints = [E0.form_interview(f) for f in (range(E0.L) if forms is None else forms)]
    return float((E0.solve(ints)['value'] - E0.delta ** 2) / var), E0


def path_set_forms(E0, clf, used, m, b):
    K = len(used); grid = mv.bits(K); ids = fv.leaf_path_sets(clf, used, m, b); sets = set()
    tr = clf.tree_; pos = {f: i for i, f in enumerate(used)}; parent = {}
    for n in range(tr.node_count):
        for c in (tr.children_left[n], tr.children_right[n]):
            if c != -1: parent[c] = n
    Xc = np.zeros((1 << K, m), np.int8); Xc[:, used] = grid
    for leaf in np.unique(clf.apply(Xc)):
        s = []; n = int(leaf)
        while n in parent:
            n = parent[n]; f = int(tr.feature[n])
            if f in pos and pos[f] not in s: s.append(pos[f])
        for j in range(K):
            if len(s) >= min(b, K): break
            if j not in s: s.append(j)
        sets.add(tuple(sorted(s)))
    index = {tuple(sorted(int(x) for x in f)): i for i, f in enumerate(E0.forms)}
    return [index[s] for s in sorted(sets)]


def run(task, a):
    t0 = time.time(); kind, name, b, s, shift = task
    X, y, tgt, clf, used, m = fv.further(name, a.data, a.forest, b, s) if kind == 'further' else fv.diabetes(a.data, b, s, shift)
    K = len(used); row = dict(kind=kind, dataset=name, b=b, seed=20261108 + s, shift=shift, items=K)
    if K <= b: row['trivial'] = True; return row
    grid = mv.bits(K); Xc = np.zeros((1 << K, m), np.int8); Xc[:, used] = grid; d = 2.0 * clf.predict(Xc) - 1
    code = X[tgt][:, used].astype(np.int64) @ (1 << np.arange(K)) + (y[tgt].astype(np.int64) << K)
    emp = 0.99 * np.bincount(code, minlength=2 << K) / len(tgt) + 0.01 / (2 << K)
    row['curve'] = {}; row['skipped'] = []
    if comb(K, b) <= a.maxforms:  # the path-set design first: it is cheap and must not be lost if a larger program fails
        E0 = engine(K, b, emp, d); var = E0.second - E0.delta ** 2
        ints = [E0.form_interview(f) for f in path_set_forms(E0, clf, used, m, b)]
        row['path_set'] = float((E0.solve(ints)['value'] - E0.delta ** 2) / var); row['path_sets'] = len(ints); del E0
    for c in range(0, a.cmax + 1):
        B = b + c
        if B >= K: row['curve'][str(c)] = 1.0; break
        if comb(K, B) * (2 << B) > a.maxsize: row['skipped'].append(c); continue
        row['curve'][str(c)] = fixed_ratio(K, B, emp, d)[0]
    row['close'] = K - b; row['seconds'] = time.time() - t0
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--forest', required=True); p.add_argument('--out', required=True)
    p.add_argument('--cmax', type=int, default=4); p.add_argument('--maxsize', type=int, default=450000); p.add_argument('--maxforms', type=int, default=9000); p.add_argument('--workers', type=int, default=1); p.add_argument('--light', action='store_true')
    a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tasks = [('diabetes', 'BRFSS', b, s, sh) for b in (4, 5, 6) for sh in (False, True) for s in range(3)]
    tasks += [('further', ds, b, s, False) for b in (4, 5, 6) for ds in ['BRFSS:heart', 'BRFSS:stroke', 'BRFSS:highbp', 'BRFSS:diffwalk', 'Spambase'] for s in range(3)]
    fn = lambda t: out / f"{t[0]}_{t[1].replace(':', '_')}_b{t[2]}_{'shift' if t[4] else 'iid'}_{t[3]}.json"
    tasks = [t for t in tasks if not fn(t).exists()]
    if a.light:  # lightest rules first (number of items from fill_v20), so that a failure of a large program does not block the rest
        import glob as _g
        ksz = {(r['kind'], r['dataset'], r['b'], r['seed'] - 20261108): r.get('items', 0) for r in (json.load(open(f)) for f in _g.glob(str(out.parent / 'fill_v20' / '*.json')))}
        tasks.sort(key=lambda t: ksz.get((t[0], t[1], t[2], t[3]), 99))
    def go(t):
        r = run(t, a); fn(t).write_text(json.dumps(r, indent=1, default=float)); return r
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(go, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t, 'trivial' if r.get('trivial') else 'K %d curve %s PS %s skipped %s %.0fs' % (r['items'], ' '.join('%s:%.3f' % kv for kv in r['curve'].items()), ('%.3f' % r['path_set']) if 'path_set' in r else '-', r['skipped'], r['seconds']), flush=True)
            except Exception as e:
                import traceback; print('ERROR', t, repr(e), traceback.format_exc()[-1500:], flush=True)
