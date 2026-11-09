"""Merge exact two-round results computed separately for b=6 (results/screening_v14_b6r2) into the main b=6 run files.
Only the round keys are copied; the runs are identical otherwise (same data, split, tree and engine), which is checked."""
import json, glob
from pathlib import Path
R = Path(__file__).resolve().parents[1] / 'results'
for f in sorted(glob.glob(str(R / 'screening_v14_b6r2' / '*.json'))):
    r = json.load(open(f)); main = R / 'screening_v14' / Path(f).name
    m = json.load(open(main))
    assert abs(r['fixed_ratio'] - m['fixed_ratio']) < 1e-6 and r['seed'] == m['seed'] and r['shift'] == m['shift']
    for k in list(r):
        if k.startswith('round'): m[k] = r[k]
    main.write_text(json.dumps(m, indent=1)); print('merged', Path(f).name, 'r2 %.4f' % m['round2_ratio'])
