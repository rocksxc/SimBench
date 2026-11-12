"""Main-text illustration: (a) the address contrast and a fixed form, (b) path guessing, (c) the binary pointer tree.
Explanations are kept in the LaTeX caption; the figure carries only labels."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / 'Manuscript' / 'figures'
C = {'blue': '#2a78d6', 'orange': '#eb6834', 'ink': '#0b0b0b', 'ink2': '#52514e', 'grid': '#cfcdc7', 'pale': '#f3f2ee'}
plt.rcParams.update({'font.size': 7, 'font.family': 'serif', 'pdf.fonttype': 42, 'mathtext.fontset': 'dejavuserif'})
fig, axes = plt.subplots(1, 3, figsize=(6.75, 1.85), gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.25], wspace=0.14))
for ax in axes: ax.set_axis_off()

# (a) address contrast
ax = axes[0]; ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.text(0.2, 9.3, '(a) address contrast', fontsize=7.5, color=C['ink'])
for i, lab in enumerate(['$A_1$', '$A_2$']):
    ax.add_patch(FancyBboxPatch((1.4 + 2.2 * i, 6.2), 1.6, 1.4, boxstyle='round,pad=0.05', fc=C['blue'], ec='none'))
    ax.text(2.2 + 2.2 * i, 6.9, lab, ha='center', va='center', color='white', fontsize=7.5)
ax.text(3.3, 8.2, 'address bits ($\\kappa=b-1$)', ha='center', color=C['ink2'], fontsize=6.5)
for j in range(4):
    sel = (j == 2)
    ax.add_patch(FancyBboxPatch((0.5 + 2.35 * j, 2.4), 1.7, 1.4, boxstyle='round,pad=0.05', fc=C['orange'] if sel else C['pale'], ec=C['ink2'], lw=0.6))
    ax.text(1.35 + 2.35 * j, 3.1, '$Z_{%d}$' % (j + 1), ha='center', va='center', color='white' if sel else C['ink'], fontsize=7.5)
ax.text(5.0, 1.2, 'data bits ($D=2^{\\kappa}$), $d=Z_A$', ha='center', color=C['ink2'], fontsize=6.3)
ax.annotate('', xy=(5.6, 3.95), xytext=(3.3, 6.1), arrowprops=dict(arrowstyle='->', color=C['ink'], lw=0.9))
ax.text(5.6, 5.3, 'read $A$,\nthen $Z_A$', fontsize=6.3, color=C['ink'], va='center')

# (b) path guessing
ax = axes[1]; ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.text(0.2, 9.3, '(b) path guessing', fontsize=7.5, color=C['ink'])
pos = {0: (5, 7.4), 1: (3, 5.2), 2: (7, 5.2), 3: (2, 3.0), 4: (4, 3.0), 5: (6, 3.0), 6: (8, 3.0)}
labels = {0: '$X_1$', 1: '$X_2$', 2: '$X_3$', 3: '$X_4$', 4: '$X_5$', 5: '$X_2$', 6: '$X_6$'}
edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
chosen = {0, 2, 5}
for a_, b_ in edges:
    on = (a_ in chosen and b_ in chosen)
    ax.plot([pos[a_][0], pos[b_][0]], [pos[a_][1], pos[b_][1]], color=C['orange'] if on else C['grid'], lw=1.8 if on else 1.0, zorder=1)
for k, (x, y) in pos.items():
    fc = C['orange'] if k in chosen else 'white'
    ax.add_patch(Circle((x, y), 0.58, fc=fc, ec=C['ink2'], lw=0.6, zorder=2))
    ax.text(x, y, labels[k], ha='center', va='center', fontsize=6.5, color='white' if k in chosen else C['ink'], zorder=3)
ax.text(5, 1.1, 'draw $S=\\{1,3,2\\}$ w.p. $q_S$; return $t/q_S$\nif the path completes in $S$, else $0$', ha='center', va='center', fontsize=6.0, color=C['ink2'])

# (c) binary pointer tree
ax = axes[2]; ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.text(0.2, 9.3, '(c) binary pointer tree, $b=L+1$', fontsize=7.5, color=C['ink'])
levels = {0: [(5, 7.6)], 1: [(3, 6.1), (7, 6.1)], 2: [(2, 4.6), (4, 4.6), (6, 4.6), (8, 4.6)]}
leaves = [(1.25 + 1.07 * i, 3.0) for i in range(8)]
path_nodes = [(5, 7.6), (3, 6.1), (4, 4.6)]; path_leaf = leaves[3]
def kids(l, i): return levels[l + 1][2 * i], levels[l + 1][2 * i + 1]
for l in range(2):
    for i, p in enumerate(levels[l]):
        for c in kids(l, i):
            on = (p in path_nodes and c in path_nodes)
            ax.plot([p[0], c[0]], [p[1], c[1]], color=C['orange'] if on else C['grid'], lw=1.8 if on else 0.9, zorder=1)
for i, p in enumerate(levels[2]):
    for c in (leaves[2 * i], leaves[2 * i + 1]):
        on = (p in path_nodes and c == path_leaf)
        ax.plot([p[0], c[0]], [p[1], c[1]], color=C['orange'] if on else C['grid'], lw=1.8 if on else 0.9, zorder=1)
for l in levels:
    for p in levels[l]:
        ax.add_patch(Circle(p, 0.42, fc=C['orange'] if p in path_nodes else 'white', ec=C['ink2'], lw=0.6, zorder=2))
for i, p in enumerate(leaves):
    ax.add_patch(FancyBboxPatch((p[0] - 0.36, p[1] - 0.3), 0.72, 0.6, boxstyle='round,pad=0.03', fc=C['orange'] if p == path_leaf else C['pale'], ec=C['ink2'], lw=0.5, zorder=2))
ax.text(0.2, 6.6, 'pointer bits\n($L$ levels)', fontsize=6.0, color=C['ink2'], va='center')
ax.text(9.2, 3.0, '$Z_v$', fontsize=6.5, color=C['ink2'], va='center')
ax.text(5, 1.1, '$B_L=Z$ at the leaf reached\nby following the pointer bits', ha='center', va='center', fontsize=6.0, color=C['ink2'])
fig.savefig(OUT / 'v13_constructions.pdf', bbox_inches='tight'); fig.savefig(OUT / 'v13_constructions.png', dpi=220, bbox_inches='tight')
print('saved')
