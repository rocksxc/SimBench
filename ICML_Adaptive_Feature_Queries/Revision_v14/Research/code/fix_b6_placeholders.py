"""Remove placeholder round ratios from screening runs in which no r-round optimum was computed (b=6 batch run with
--max_round 1 before the fix in screening_v14.run): keep round values only where an r-round colgen ran (iterations
recorded) or where the fixed design already attains full information."""
import json, glob, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1] / 'results' / 'screening_v14'
for f in sorted(glob.glob(str(R / '*.json'))):
    r = json.load(open(f)); changed = False
    if r['fixed_ratio'] > 1 + 1e-7:
        for k in range(2, r['b'] + 1):
            if f'round{k}_ratio' in r and f'round{k}_iterations' not in r:
                # keep values implied by an earlier computed round that reached full information
                prev = [kk for kk in range(2, k) if f'round{kk}_iterations' in r]
                if prev and r.get(f'round{prev[-1]}_ratio', 2) <= 1 + 1e-6:
                    continue
                del r[f'round{k}_ratio']; changed = True
    if changed:
        Path(f).write_text(json.dumps(r, indent=1)); print('cleaned', Path(f).name)
