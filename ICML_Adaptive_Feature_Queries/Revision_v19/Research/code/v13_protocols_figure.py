"""Figure 1 redrawn at legible size: a two-query branching interview versus a fixed form, and the scores a fixed form can use."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / 'Manuscript' / 'figures'
C = {'blue': '#2a78d6', 'orange': '#eb6834', 'ink': '#0b0b0b', 'ink2': '#52514e', 'grid': '#cfcdc7', 'pale': '#f3f2ee'}
plt.rcParams.update({'font.size': 7.5, 'font.family': 'serif', 'pdf.fonttype': 42, 'mathtext.fontset': 'dejavuserif'})
fig, (ax, bx) = plt.subplots(1, 2, figsize=(3.4, 1.6), gridspec_kw=dict(width_ratios=[1, 1.2], wspace=0.3))
for a in (ax, bx): a.set_axis_off(); a.set_xlim(0, 10); a.set_ylim(0, 10)
# branching
ax.text(0.2, 9.4, 'branching interview', fontsize=7.5, color=C['ink'])
pos = {0: (5, 7.2), 1: (2.6, 3.8), 2: (7.4, 3.8)}; lab = {0: '$X_1$', 1: '$X_2$', 2: '$X_3$'}
for a_, b_ in [(0, 1), (0, 2)]:
    ax.plot([pos[a_][0], pos[b_][0]], [pos[a_][1], pos[b_][1]], color=C['grid'], lw=1.2, zorder=1)
ax.text(3.0, 6.0, '$X_1=+1$', fontsize=6.5, color=C['ink2'], ha='right'); ax.text(7.0, 6.0, '$X_1=-1$', fontsize=6.5, color=C['ink2'])
for k, p in pos.items():
    ax.add_patch(Circle(p, 0.85, fc=C['orange'], ec='none', zorder=2)); ax.text(p[0], p[1], lab[k], ha='center', va='center', color='white', fontsize=7.5, zorder=3)
ax.text(5, 1.2, 'next question depends\non the first answer', ha='center', va='center', fontsize=6.3, color=C['ink2'])
# fixed form
bx.text(0.2, 9.4, 'fixed form', fontsize=7.5, color=C['ink'])
for i, (lbl, y0) in enumerate([('$\\{X_1,X_2\\}$ with prob. $q_{12}$', 6.6), ('$\\{X_1,X_3\\}$ with prob. $q_{13}$', 4.4)]):
    bx.add_patch(FancyBboxPatch((0.2, y0 - 0.7), 9.6, 1.5, boxstyle='round,pad=0.05', fc=C['blue'] if i == 0 else C['pale'], ec=C['ink2'], lw=0.6))
    bx.text(5.0, y0 + 0.05, lbl, ha='center', va='center', color='white' if i == 0 else C['ink'], fontsize=7)
bx.text(5, 1.2, 'set drawn before the record;\nthe score uses every answer', ha='center', va='center', fontsize=6.3, color=C['ink2'])
fig.savefig(OUT / 'v13_protocols.pdf', bbox_inches='tight'); fig.savefig(OUT / 'v13_protocols.png', dpi=220, bbox_inches='tight'); print('saved')
