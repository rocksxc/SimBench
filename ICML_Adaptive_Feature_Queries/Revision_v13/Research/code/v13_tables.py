"""Generate v13 LaTeX tables/snippets from result files (robust to partial results). Prints the numbers quoted in the text."""
import json, glob, statistics as st, csv
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parents[1] / 'results'
R12 = Path('/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/handoff/ICML_Handoff_v12/Revision_v12/Research/results')
M = Path(__file__).resolve().parents[2] / 'Manuscript'
def med(v): return st.median(v) if v else float('nan')
def q(v, p): return float(np.percentile(v, p)) if v else float('nan')
def load(pattern): return [json.load(open(f)) for f in sorted(glob.glob(str(pattern)))]

# ---------------- cap grid table (main text) ----------------
cap = [r for r in load(R / 'forest_capgrid' / '*.json') if r.get('alpha', 0.01) == 0.01 and r.get('boot', 0) == 0]
b3 = [r for r in load(R12 / 'forest_exact_tasks' / '*.json') if r['m'] > 3]
for r in b3: r['b'] = 3; r['ratio_exact'] = r['ratio_exact_lower']
for r in cap: r['ratio_exact'] = r.get('ratio_exact_lower', float('nan'))
allrows = b3 + [r for r in cap if r['m'] > r['b']]
lines = [r'\begin{table}[t]', r'\centering',
         r'\caption{Exact fixed/branching variance ratio for independently retrained depth-$b$ forests with cap $b$ (median over five splits; $b=3$ is in Table~\ref{tab:forestexact}). Cells with $m\le b$ are not binding; cells marked -- were not computed within the compute budget (Appendix~\ref{app:capsens}). Right: number of binding tasks and the median fitted ratio (designs optimized on training records, evaluated held-out).}',
         r'\label{tab:capgrid}', r'\small', r'\setlength{\tabcolsep}{3.5pt}', r'\begin{tabular}{lrrrrrr}', r'\toprule',
         r'Data & $b$ & $m=6$ & $m=9$ & $m=12$ & tasks & fitted \\', r'\midrule']
summary = {}
for b in [2, 3, 4, 5, 6]:
    rows_b = [r for r in allrows if r['b'] == b]
    if not rows_b: continue
    for ds in (['WDBC', 'Spambase', 'Ionosphere'] if b != 3 else []):
        cells = []
        for m in [6, 9, 12]:
            v = [r['ratio_exact'] for r in rows_b if r['dataset'] == ds and r['m'] == m]
            cells.append(('%.2f' % med(v)) if v else '--')
        if ds == 'WDBC':
            fit = [r['ratio_fitted'] for r in rows_b if 'ratio_fitted' in r]
            lines.append(f"{ds} & {b} & {' & '.join(cells)} & {len(rows_b)} & {('%.2f' % med(fit)) if fit else '--'} \\\\")
        else:
            lines.append(f"{ds} & & {' & '.join(cells)} & & \\\\")
    summary[b] = dict(n=len(rows_b), median=med([r['ratio_exact'] for r in rows_b]), p90=q([r['ratio_exact'] for r in rows_b], 90), mx=max(r['ratio_exact'] for r in rows_b),
                      m12=med([r['ratio_exact'] for r in rows_b if r['m'] == 12]), m6=med([r['ratio_exact'] for r in rows_b if r['m'] == 6]))
    if b not in (3, 5) and rows_b: lines.append(r'\addlinespace[1pt]')
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v13_capgrid_table.tex').write_text('\n'.join(lines) + '\n')
print('CAP SUMMARY (b: n, median, p90, max, median m=6, median m=12):'); [print(b, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()}) for b, s in summary.items()]
conv = [r for r in cap if 'ratio_exact_upper' in r and r['m'] > r['b']]
gaps = [abs(r['ratio_exact_upper'] - r['ratio_exact_lower']) / r['ratio_exact_lower'] for r in conv]
print('cap grid max relative bracket width', max(gaps) if gaps else None, 'n', len(conv))
detail = [r'\begin{center}\small\begin{tabular}{lrrrrrr}\toprule', r'$b$ & tasks & median & 90th pct. & max & median $m=6$ & median $m=12$ \\', r'\midrule']
def fmt(x): return ('%.2f' % x) if np.isfinite(x) else '--'
for b, s in summary.items(): detail.append(f"{b} & {s['n']} & {fmt(s['median'])} & {fmt(s['p90'])} & {fmt(s['mx'])} & {fmt(s['m6'])} & {fmt(s['m12'])} \\\\")
detail += [r'\bottomrule\end{tabular}\end{center}']
(M / 'v13_capgrid_detail.tex').write_text('\n'.join(detail) + '\n')

# ---------------- sensitivity ----------------
sens = load(R / 'forest_sensitivity' / '*.json')
base = {(r['dataset'], r['seed']): r['ratio_exact_lower'] for r in sens if r['alpha'] == 0.01 and r['boot'] == 0}
if not base:  # fall back to stored v12 values at alpha 0.01
    base = {(r['dataset'], r['seed']): r['ratio_exact_lower'] for r in b3 if r['m'] == 12}
out = [r'\begin{center}\small\begin{tabular}{lrrrrr}\toprule', r'Variation & tasks & median ratio & median rel. change & max rel. change & median $|\log|$ change \\', r'\midrule']
sens_summary = {}
for al in [0.001, 0.01, 0.05, 0.1]:
    rows = [r for r in sens if r['alpha'] == al and r['boot'] == 0]
    if not rows: continue
    rel = [r['ratio_exact_lower'] / base[(r['dataset'], r['seed'])] - 1 for r in rows if (r['dataset'], r['seed']) in base]
    sens_summary[('alpha', al)] = (len(rows), med([r['ratio_exact_lower'] for r in rows]), med(rel), max((abs(x) for x in rel), default=float('nan')))
    out.append(f"$\\alpha={al*100:g}\\%$ & {len(rows)} & {med([r['ratio_exact_lower'] for r in rows]):.3f} & {100*med(rel):+.1f}\\% & {100*max((abs(x) for x in rel), default=float('nan')):.1f}\\% & {med([abs(np.log(1+x)) for x in rel]):.3f} \\\\")
boots = [r for r in sens if r['boot'] > 0]
if boots:
    rel = [r['ratio_exact_lower'] / base[(r['dataset'], r['seed'])] - 1 for r in boots if (r['dataset'], r['seed']) in base]
    sens_summary['boot'] = (len(boots), med([r['ratio_exact_lower'] for r in boots]), med(rel), max(abs(x) for x in rel), q([abs(x) for x in rel], 90))
    out.append(f"bootstrap of held-out records ($\\alpha=1\\%$) & {len(boots)} & {med([r['ratio_exact_lower'] for r in boots]):.3f} & {100*med(rel):+.1f}\\% & {100*max(abs(x) for x in rel):.1f}\\% & {med([abs(np.log(1+x)) for x in rel]):.3f} \\\\")
out += [r'\bottomrule\end{tabular}\end{center}']
(M / 'v13_sensitivity_detail.tex').write_text('\n'.join(out) + '\n')
print('SENS SUMMARY', {str(k): tuple(round(x, 4) if isinstance(x, float) else x for x in v) for k, v in sens_summary.items()})

# ---------------- predictor ----------------
pred_file = R / 'predictor_v13.csv'
ptxt = ['(predictor results pending)']
if pred_file.exists():
    rows = list(csv.DictReader(open(pred_file)))
    for r in rows:
        for k in ['ref_lower_var', 'realized', 'ref_gamma', 'target_gamma', 'fitted']:
            try: r[k] = float(r[k])
            except Exception: r[k] = float('nan')
    ptxt = [r'\begin{center}\small\begin{tabular}{lrrrrr}\toprule', r'Tasks & $n$ & Spearman($\widehat L$, realized) & median realized$/\widehat L$ & realized$<\widehat L$ & rule: $\widehat L\le1.05$ $\Rightarrow$ realized $\le1.25$ \\', r'\midrule']
    from scipy.stats import spearmanr
    allr = []
    for kind, name in [('forest', 'forests'), ('screening', 'screening trees')]:
        rr = [r for r in rows if r['kind'] == kind and np.isfinite(r['realized'])]
        if not rr: continue
        x = [r['ref_lower_var'] for r in rr]; y = [r['realized'] for r in rr]
        rho = spearmanr(x, y).correlation if len(rr) > 2 else float('nan')
        below = sum(1 for r in rr if r['realized'] < r['ref_lower_var'] - 1e-9)
        small = [r for r in rr if r['ref_lower_var'] <= 1.05]; rule = sum(1 for r in small if r['realized'] <= 1.25)
        ptxt.append(f"{name} & {len(rr)} & {rho:.2f} & {med([r['realized']/r['ref_lower_var'] for r in rr]):.2f} & {below} & {rule}/{len(small)} \\\\")
        allr += rr
        print('PRED', kind, len(rr), 'spearman', round(rho, 3), 'median realized/ref', round(med([r['realized']/r['ref_lower_var'] for r in rr]), 3), 'below', below, 'rule', rule, len(small))
    ptxt += [r'\bottomrule\end{tabular}\end{center}']
(M / 'v13_predictor_detail.tex').write_text('\n'.join(ptxt) + '\n')

# ---------------- MI / regimp table ----------------
mi = load(R / 'screening_mi_v13' / '*.json')
lines = [r'\begin{table}[h]', r'\centering',
         r'\caption{Audit simulations with $n=1000$ target respondents and 400 replications. Bias, standard deviation and RMSE are multiplied by 100; coverage of nominal 95\% intervals has Monte Carlo standard error about 0.011. Regression imputation: conditional mean of $t$ given the asked items and the label from the complete source records, naive standard error. MI: ten proper hot-deck imputations from the same source records with Rubin\textquotesingle s rules.}',
         r'\label{tab:regimp}', r'\small', r'\begin{tabular}{llrrrrr}', r'\toprule', r'Data, $b$, target & Design & Bias & SD & RMSE & Coverage & Width \\', r'\midrule']
mi_summary = []
for r in sorted(mi, key=lambda r: (r['dataset'], r['b'], r['shift'])):
    first = True
    for key, lab in [('branch', 'branching'), ('fixed', 'fitted fixed form'), ('regimp', 'fixed form + regression imputation'), ('mi', 'fixed form + MI')]:
        s = r[key]
        head = f"{r['dataset']}, {r['b']}, {'other sex' if r['shift'] else 'random half'}" if first else ''
        lines.append(f"{head} & {lab} & {100*s['bias']:.2f} & {100*s['sd']:.2f} & {100*s['rmse']:.2f} & {s['coverage']:.3f} & {100*s['width']:.2f} \\\\"); first = False
    mi_summary.append((r['dataset'], r['b'], r['shift'], round(r['regimp']['rmse'] / r['branch']['rmse'], 3), round(r['regimp']['coverage'], 3), round(r['mi']['rmse'] / r['branch']['rmse'], 3)))
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v13_mi_table.tex').write_text('\n'.join(lines) + '\n')
print('MI/REGIMP (dataset, b, shift, regimp/branch rmse, regimp coverage, mi/branch rmse):'); [print(x) for x in mi_summary]
print('done')
