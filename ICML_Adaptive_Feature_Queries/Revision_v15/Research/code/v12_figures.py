"""Main-text figure: (a) exact vs restricted-menu ratios for binding forest tasks;
(b) screening-tree ratios against the question budget b (medians over runs)."""
import json, glob, statistics as st, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1] / 'results'
OUT = Path(__file__).resolve().parents[2] / 'Manuscript' / 'figures'
# Reference palette slots (validated light-mode categorical order): blue, orange, aqua, violet(4th for lines)
C = {'blue': '#2a78d6', 'orange': '#eb6834', 'aqua': '#1baf7a', 'violet': '#6250d6', 'ink': '#0b0b0b', 'ink2': '#52514e', 'grid': '#e4e3df'}
plt.rcParams.update({'font.size': 7.5, 'font.family': 'serif', 'axes.edgecolor': C['ink2'], 'axes.labelcolor': C['ink'],
                     'xtick.color': C['ink2'], 'ytick.color': C['ink2'], 'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
                     'legend.frameon': False, 'pdf.fonttype': 42})

fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.75, 2.25), gridspec_kw=dict(width_ratios=[1, 1.15], wspace=0.32))
rows = [json.load(open(f)) for f in glob.glob(str(R / 'forest_exact_tasks' / '*.json'))]
rows = [r for r in rows if r['m'] > 3]
markers = {6: 'o', 9: 's', 12: '^'}
for ds, col in [('WDBC', C['blue']), ('Spambase', C['orange']), ('Ionosphere', C['aqua'])]:
    rr = [r for r in rows if r['dataset'] == ds]
    ax.scatter([r['ratio_v11menu'] for r in rr], [r['ratio_exact_lower'] for r in rr], s=9, c=col, edgecolors='white', linewidths=0.4, label=ds, zorder=3)
lim = (0.95, 1.95)
ax.plot(lim, lim, color=C['ink2'], lw=0.8, ls='--', zorder=1)
ax.text(1.30, 1.22, 'equal ratios', color=C['ink2'], rotation=37, fontsize=6.5)
ax.set_xlim(*lim); ax.set_ylim(*lim)
ax.set_xlabel('ratio with restricted branching menu')
ax.set_ylabel('exact ratio, all depth-3 trees')
ax.grid(color=C['grid'], lw=0.5); ax.set_axisbelow(True)
ax.legend(loc='lower right', handletextpad=0.2, borderaxespad=0.3, markerscale=1.4)
ax.set_title('(a) 180 binding forest updates, $b=3$', fontsize=7.5, loc='left')

sr = [r for r in (json.load(open(f)) for f in glob.glob(str(R / 'budget_trees' / '*.json'))) if r['dataset'] == 'BRFSS']
bs = sorted({r['b'] for r in sr})
series = [('fixed_ht_ratio', 'path guessing', C['violet'], 'v'), ('fixed_fit_ratio', 'fitted fixed form', C['orange'], 's'),
          ('fixed_oracle_ratio', 'best fixed form', C['blue'], 'o'), ('round2_oracle_ratio', 'two rounds', C['aqua'], 'D')]
for key, lab, col, mk in series:
    xs, ys = [], []
    for b in bs:
        vals = [r[key] for r in sr if r['b'] == b and key in r]
        if vals: xs.append(b); ys.append(st.median(vals))
    bx.plot(xs, ys, color=col, lw=1.6, marker=mk, ms=4.2, mec='white', mew=0.5, label=lab, zorder=3)
    off = {'fitted fixed form': 1.07, 'best fixed form': 0.95, 'two rounds': 0.93, 'path guessing': 1.0}[lab]
    bx.text(xs[-1] + 0.12, ys[-1] * off, lab, color=C['ink'], va='center', fontsize=6.5)
bx.axhline(1, color=C['ink2'], lw=0.8, ls='--', zorder=1)
bx.set_yscale('log'); bx.set_yticks([1, 1.5, 2, 4, 8, 16]); bx.set_yticklabels(['1', '1.5', '2', '4', '8', '16'])
bx.set_xticks(bs); bx.set_xlim(bs[0] - 0.2, bs[-1] + 1.6)
bx.set_xlabel('question budget $b$ (tree depth)'); bx.set_ylabel('records needed / branching')
bx.grid(color=C['grid'], lw=0.5, which='major'); bx.set_axisbelow(True)
bx.set_title('(b) BRFSS screening trees (median over 6 runs)', fontsize=7.5, loc='left')
for s in ['top', 'right']:
    ax.spines[s].set_visible(False); bx.spines[s].set_visible(False)
fig.savefig(OUT / 'v12_main.pdf', bbox_inches='tight'); fig.savefig(OUT / 'v12_main.png', dpi=200, bbox_inches='tight')
print('saved', OUT / 'v12_main.pdf')
