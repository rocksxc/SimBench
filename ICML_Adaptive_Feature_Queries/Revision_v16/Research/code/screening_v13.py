"""v13: smoothing-mass sensitivity of the screening-tree constants (BRFSS, b in {4,6}, both targets, 3 seeds)."""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import budget_trees as bt
p = argparse.ArgumentParser(); p.add_argument('--data', required=True); p.add_argument('--out', required=True)
p.add_argument('--alphas', default='0.001,0.05,0.1'); p.add_argument('--bs', default='4,6'); p.add_argument('--seeds', type=int, default=3); p.add_argument('--datasets', default='BRFSS')
a = p.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
for ds in a.datasets.split(','):
    for b in [int(v) for v in a.bs.split(',')]:
        for al in [float(v) for v in a.alphas.split(',')]:
            for shift in [False, True]:
                for s in range(a.seeds):
                    dest = out / f'{ds}_b{b}_{"shift" if shift else "iid"}_{s}_a{al}.json'
                    if dest.exists(): continue
                    r = bt.run(ds, a.data, b, 20261108 + s, shift, alpha=al); r['alpha'] = al
                    dest.write_text(json.dumps(r, indent=1))
                    print(ds, b, al, shift, s, 'oracle %.3f fit %.3f bracket [%.2f, %.2f]' % (r['fixed_oracle_ratio'], r['fixed_fit_ratio'], r['bracket_lower'], r['bracket_upper']), '%.0fs' % r['seconds'], flush=True)
