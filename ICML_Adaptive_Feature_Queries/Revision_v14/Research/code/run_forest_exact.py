"""Driver: all 240 v11 forest tasks with the exact all-tree branching arm."""
import argparse, json, os, sys, time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
sys.path.insert(0, str(Path(__file__).resolve().parent))
import forest_exact as fe

def one(args):
    name, seed, m, root, out = args
    dest = Path(out) / f'{name}_{seed}_{m}.json'
    if dest.exists():
        return json.loads(dest.read_text())
    r = fe.run_task(name, seed, m, root)
    d2 = r['delta'] ** 2
    r['ratio_exact_lower'] = (r['fixed_M'] - d2) / max(r['branch_M_upper'] - d2, 1e-15)
    r['ratio_exact_upper'] = (r['fixed_M'] - d2) / max(r['branch_M_lower'] - d2, 1e-15)
    r['ratio_v11menu'] = (r['fixed_M'] - d2) / max(r['v11menu_M'] - d2, 1e-15)
    r['ratio_vs_fullinfo'] = (r['fixed_M'] - d2) / max(r['second'] - d2, 1e-15)
    dest.write_text(json.dumps(r, indent=1))
    return r

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True); p.add_argument('--workers', type=int, default=10)
    a = p.parse_args(); Path(a.out).mkdir(parents=True, exist_ok=True)
    tasks = [(ds, s, m, a.data, a.out) for ds in ['WDBC', 'Spambase', 'Ionosphere'] for s in range(20261108, 20261128) for m in [3, 6, 9, 12]]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs = {pool.submit(one, t): t for t in tasks}
        for f in as_completed(jobs):
            t = jobs[f]
            try:
                r = f.result()
                print(t[0], t[1], t[2], 'iters', r['iterations'], 'ratio [%.3f, %.3f] v11menu %.3f' % (r.get('ratio_exact_lower', 1), r.get('ratio_exact_upper', 1), r.get('ratio_v11menu', 1)), '%.0fs' % (time.time() - t0), flush=True)
            except Exception as e:
                print('ERROR', t, repr(e), flush=True)
