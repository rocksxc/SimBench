"""Reproduce stored v12 forest_exact tasks from mirrored inputs; compare key numbers."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from forest_exact import run_task
root = sys.argv[1]; stored = Path(sys.argv[2])
for name, seed, m in [('Spambase', 20261108, 6), ('Ionosphere', 20261108, 6), ('WDBC', 20261108, 6)]:
    r = run_task(name, seed, m, root)
    s = json.load(open(stored / f'{name}_{seed}_{m}.json'))
    print(name, m, 'fixed_M new %.9f stored %.9f | branch_upper new %.9f stored %.9f | gamma_fixed new %.6f stored %.6f' % (
        r['fixed_M'], s['fixed_M'], r['branch_M_upper'], s['branch_M_upper'], r['gamma_fixed'], s['gamma_fixed']), flush=True)
