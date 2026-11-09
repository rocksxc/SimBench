"""Numbers quoted in the v12 text (screening study and MI simulations)."""
import json, glob, statistics as st, math
from pathlib import Path
R = Path(__file__).resolve().parents[1] / 'results'
sr = [json.load(open(f)) for f in sorted(glob.glob(str(R / 'budget_trees' / '*.json')))]
print('screening runs', len(sr))
for ds in ['BRFSS', 'Thyroid']:
    for b in [3, 4, 5, 6]:
        rr = [r for r in sr if r['dataset'] == ds and r['b'] == b]
        if not rr: continue
        o = [r['fixed_oracle_ratio'] for r in rr]
        print(f"{ds} b={b} n={len(rr)} oracle med {st.median(o):.2f} [{min(o):.2f},{max(o):.2f}] fitted med {st.median([r['fixed_fit_ratio'] for r in rr]):.2f} HT [{min(r['fixed_ht_ratio'] for r in rr):.1f},{max(r['fixed_ht_ratio'] for r in rr):.1f}] Gamma=1 count {sum(r['Gamma_P']>0.9999 for r in rr)}")
loss = [r['fixed_fit_ratio'] / r['fixed_oracle_ratio'] - 1 for r in sr]
print('fitted vs oracle loss: min %.3f median %.3f max %.3f' % (min(loss), st.median(loss), max(loss)))
print('HT overall range [%.1f, %.1f]' % (min(r['fixed_ht_ratio'] for r in sr), max(r['fixed_ht_ratio'] for r in sr)))
print('bracket violations', sum(not (r['bracket_lower'] - 1e-6 <= r['fixed_oracle_ratio'] <= r['bracket_upper'] + 1e-6) for r in sr))
for b in [4, 5, 6]:
    rr = [r for r in sr if r['b'] == b and r['fixed_oracle_ratio'] > 1.01]
    if rr:
        rec2 = [math.log(r['fixed_oracle_ratio'] / r['round2_oracle_ratio']) / math.log(r['fixed_oracle_ratio']) for r in rr]
        rec3 = [math.log(r['fixed_oracle_ratio'] / r['round3_oracle_ratio']) / math.log(r['fixed_oracle_ratio']) for r in rr if 'round3_oracle_ratio' in r]
        print(f"b={b}: runs with gap {len(rr)}; two rounds recover median {st.median(rec2):.2f} of log-gap; three rounds {st.median(rec3) if rec3 else float('nan'):.2f}")
lowgap = [r['fixed_oracle_ratio'] / r['bracket_lower'] for r in sr if r['fixed_oracle_ratio'] > 1.01]
upgap = [r['bracket_upper'] / r['fixed_oracle_ratio'] for r in sr if r['fixed_oracle_ratio'] > 1.01]
print('realized/lower median %.2f; upper/realized median %.2f' % (st.median(lowgap), st.median(upgap)))
mi = [json.load(open(f)) for f in sorted(glob.glob(str(R / 'screening_mi' / '*.json')))]
print('MI settings', len(mi))
for r in mi:
    br = r['branch']['rmse']
    print(f"{r['dataset']} b={r['b']} {'shift' if r['shift'] else 'iid'}: RMSE/branch fixed {r['fixed']['rmse']/br:.2f} MI {r['mi']['rmse']/br:.2f}; bias x100 branch {100*r['branch']['bias']:.2f} fixed {100*r['fixed']['bias']:.2f} MI {100*r['mi']['bias']:.2f}; cov {r['branch']['coverage']:.3f}/{r['fixed']['coverage']:.3f}/{r['mi']['coverage']:.3f}")
