"""Figure (v16): records needed relative to branching as a function of the number of rounds r (r = 1 fixed forms,
r = b branching). (a) exact optimal r-round designs for the BRFSS screening trees (median over targets and seeds;
crosses: heuristic second round) and for the forest updates of forest_rounds_v15 (median over tasks);
(b) RMSE of log-linear working models and of branching relative to the design-based form score on the same\nfitted-form records, as a function of the audit size (median over BRFSS trees; bands: quartiles)."""
import json, glob, statistics as st
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R = Path(__file__).resolve().parents[1] / 'results'; M = Path(__file__).resolve().parents[2] / 'Manuscript'
plt.rcParams.update({'font.size': 7.5, 'axes.labelsize': 7.5, 'legend.fontsize': 6.2, 'xtick.labelsize': 7, 'ytick.labelsize': 7, 'pdf.fonttype': 42})
sc = [json.load(open(f)) for f in sorted(glob.glob(str(R / 'screening_v14' / 'BRFSS_*.json')))]
r6 = {(r['shift'], r['seed']): r for r in (json.load(open(f)) for f in glob.glob(str(R / 'screening_v14_b6r2' / '*.json')))}
for r in sc:
    k = (r['shift'], r['seed'])
    if r['b'] == 6 and k in r6:
        for kk in r6[k]:
            if kk.startswith('round'): r[kk] = r6[k][kk]
for f in glob.glob(str(R / 'two_round_b6_v15' / '*.json')):  # certified upper bounds from time-limited column generation
    q = json.load(open(f))
    for r in sc:
        if r['b'] == 6 and r['shift'] == q['shift'] and r['seed'] == q['seed'] and r.get('round2_ratio') is None: r['round2_ratio'] = q['round2_ratio_upper']
fo = [json.load(open(f)) for f in sorted(glob.glob(str(R / 'forest_rounds_v15' / '*.json')))]
pt = {json.load(open(f))['b']: json.load(open(f)) for f in sorted(glob.glob(str(R / 'pointer_v14' / '*.json')))}
fig, ax = plt.subplots(1, 2, figsize=(3.4, 1.95), layout='constrained', gridspec_kw={'width_ratios': [1.1, 1]})
cols = {4: '#1f6f8b', 5: '#c75c2a', 6: '#4c8c4a', 3: '#7a5195'}
for b in [4, 5, 6]:
    rr = [r for r in sc if r['b'] == b]
    if not rr: continue
    xs, ys = [1], [st.median([r['fixed_ratio'] for r in rr])]
    for k in range(2, b):
        vals = [(1.0 if r['fixed_ratio'] <= 1 + 1e-6 else r.get(f'round{k}_ratio')) for r in rr]
        if all(v is not None for v in vals): xs.append(k); ys.append(st.median(vals))
    xs.append(b); ys.append(1.0)  # branching asks the tree's own questions
    ax[0].plot(xs, ys, 'o', color=cols[b], ms=2.6, label=f'BRFSS, $b={b}$')
    for (x0, y0), (x1, y1) in zip(zip(xs[:-1], ys[:-1]), zip(xs[1:], ys[1:])):
        ax[0].plot([x0, x1], [y0, y1], '-' if x1 == x0 + 1 else ':', color=cols[b], lw=1.1 if x1 == x0 + 1 else 0.8)
    h = [r.get('heur2_ratio') for r in rr if r.get('heur2_ratio') is not None]
    if h: ax[0].plot([2], [st.median(h)], 'x', color=cols[b], ms=4)
for b, c in [(3, '#7a5195'), (4, '#8a8f98')]:
    rr = [r for r in fo if r['b'] == b]
    if not rr: continue
    xs = list(range(1, b + 1)); ys = [st.median([r['fixed_ratio'] for r in rr])] + [st.median([r[f'round{k}_ratio'] for r in rr]) for k in range(2, b)] + [1.0]
    ax[0].plot(xs, ys, 's--', color=c, ms=2.4, lw=0.9, label=f'forests, $b={b}$')
ax[0].set(xlabel='rounds $r$', ylabel='records vs. branching', xticks=[1, 2, 3, 4, 5, 6], ylim=(0.95, None), xlim=(0.8, 6.2))
ax[0].set_title('(a) trained models', fontsize=7.5)
ax[0].legend(frameon=False, loc='upper right', handlelength=1.4, labelspacing=0.2, borderaxespad=0.1, fontsize=5.8)
cv = [json.load(open(f)) for f in sorted(glob.glob(str(R / 'curve_v16' / '*.json')))]
if cv:
    import numpy as np
    ns = sorted(int(k) for k in cv[0]['curve'])
    for kk, lab, c, ls in [('em2', 'two-way model', '#c75c2a', '-'), ('em3', 'three-way model', '#1f6f8b', '-'), ('branch', 'branching', '#8a8f98', '--')]:
        v = np.array([[r['curve'][str(n)][kk]['rmse'] / r['curve'][str(n)]['fixed']['rmse'] for n in ns] for r in cv])
        ax[1].plot(ns, np.median(v, 0), ls, color=c, lw=1.1, marker='o' if ls == '-' else None, ms=2.4, label=lab)
        if kk != 'branch': ax[1].fill_between(ns, np.percentile(v, 25, 0), np.percentile(v, 75, 0), color=c, alpha=0.15, lw=0)
    ax[1].axhline(1.0, color='k', lw=0.7)
    ax[1].set(xscale='log', xlabel='audit size $n$', ylabel='RMSE / form score', xticks=[500, 2000, 8000, 32000])
    ax[1].set_xticklabels(['500', '2k', '8k', '32k']); ax[1].minorticks_off()
    ax[1].set_title('(b) working models', fontsize=7.5)
    ax[1].legend(frameon=False, loc='upper left', handlelength=1.4, labelspacing=0.2, borderaxespad=0.1, fontsize=5.8)
for a in ax:
    a.spines[['top', 'right']].set_visible(False); a.grid(axis='y', color='#d4d9df', lw=0.5); a.set_axisbelow(True)
fig.savefig(M / 'figures' / 'v16_rounds.pdf', metadata={'Author': None})
print('figure written', len(sc), 'screening runs', len(fo), 'forest tasks', sorted(pt))
