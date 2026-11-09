"""Figure: records needed relative to branching as a function of the number of rounds r (r = 1 is the fixed form,
r = b branching). (a) BRFSS screening trees (median over targets and seeds) with the heuristic second round;
(b) binary pointer tree at the uniform law (lower bounds on V_r) with the upper bound 2^(b-r) of Theorem 3(a)."""
import json, glob, statistics as st
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R = Path(__file__).resolve().parents[1] / 'results'; M = Path(__file__).resolve().parents[2] / 'Manuscript'
plt.rcParams.update({'font.size': 7.5, 'axes.labelsize': 7.5, 'legend.fontsize': 6.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7, 'pdf.fonttype': 42})
sc = [json.load(open(f)) for f in sorted(glob.glob(str(R / 'screening_v14' / 'BRFSS_*.json')))]
pt = {json.load(open(f))['b']: json.load(open(f)) for f in sorted(glob.glob(str(R / 'pointer_v14' / '*.json')))}
fig, ax = plt.subplots(1, 2, figsize=(3.4, 1.75), layout='constrained')
cols = {4: '#1f6f8b', 5: '#c75c2a', 6: '#4c8c4a', 3: '#7a5195'}
for b in [4, 5, 6]:
    rr = [r for r in sc if r['b'] == b]
    if not rr: continue
    xs, ys = [1], [st.median([r['fixed_ratio'] for r in rr])]
    for k in range(2, b):
        vals = [r.get(f'round{k}_ratio') for r in rr]
        if all(v is not None for v in vals): xs.append(k); ys.append(st.median(vals))
    xs.append(b); ys.append(1.0)  # branching asks the tree's own questions
    ax[0].plot(xs, ys, 'o', color=cols[b], ms=2.6, label=f'$b={b}$')
    for (x0, y0), (x1, y1) in zip(zip(xs[:-1], ys[:-1]), zip(xs[1:], ys[1:])):
        ax[0].plot([x0, x1], [y0, y1], '-' if x1 == x0 + 1 else ':', color=cols[b], lw=1.1 if x1 == x0 + 1 else 0.8)
    h = [r.get('heur2_ratio') for r in rr if r.get('heur2_ratio') is not None]
    if h: ax[0].plot([2], [st.median(h)], 'x', color=cols[b], ms=4)
ax[0].set(xlabel='rounds $r$', ylabel='records vs. branching', xticks=[1, 2, 3, 4, 5, 6], ylim=(0.95, None))
ax[0].set_title('(a) BRFSS screening trees', fontsize=7.5)
ax[0].legend(frameon=False, loc='upper right', handlelength=1.2)
for b in sorted(pt):
    r = pt[b]; ys = [r.get(f'M{k}') for k in range(1, b + 1)]
    ax[1].plot(range(1, b + 1), ys, 'o-', color=cols.get(b, 'k'), ms=2.6, lw=1.1, label=f'$b={b}$')
    ax[1].plot(range(1, b + 1), [2.0 ** (b - k) for k in range(1, b + 1)], ':', color=cols.get(b, 'k'), lw=0.9)
ax[1].set(xlabel='rounds $r$', yscale='log', xticks=[1, 2, 3, 4, 5])
ax[1].set_yticks([1, 2, 4, 8, 16]); ax[1].set_yticklabels(['1', '2', '4', '8', '16']); ax[1].minorticks_off()
ax[1].set_title('(b) binary pointer tree', fontsize=7.5)
ax[1].legend(frameon=False, loc='upper right', handlelength=1.2)
for a in ax:
    a.spines[['top', 'right']].set_visible(False); a.grid(axis='y', color='#d4d9df', lw=0.5); a.set_axisbelow(True)
fig.savefig(M / 'figures' / 'v14_rounds.pdf', metadata={'Author': None})
print('figure written', len(sc), 'screening runs', sorted(pt))
