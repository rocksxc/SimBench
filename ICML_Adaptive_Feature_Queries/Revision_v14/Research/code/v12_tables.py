"""Generate the v12 main-text tables from result JSON files."""
import json, glob, statistics as st, math
from pathlib import Path
R = Path(__file__).resolve().parents[1] / 'results'
M = Path(__file__).resolve().parents[2] / 'Manuscript'

def q(v, p):
    v = sorted(v); k = (len(v) - 1) * p; lo = math.floor(k); hi = math.ceil(k)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)

rows = [json.load(open(f)) for f in glob.glob(str(R / 'forest_exact_tasks' / '*.json'))]
fit = {(r['dataset'], r['seed']): r for r in [json.load(open(f)) for f in glob.glob(str(R / 'forest_exact_b3fit' / '*.json'))]}
lines = [r'\begin{table}[t]', r'\centering',
         r'\caption{Independent forest updates, cap $b=3$, 20 splits per cell. Exact fixed/branching variance ratio over all forms and all depth-3 trees (median and 10th--90th percentiles), the ratio when branching is restricted to the 40 component trees and all triples, and the fixed-form variance relative to the unattainable full-information variance. Fitted: designs optimized on training records and evaluated on held-out records ($m=12$, five splits).}',
         r'\label{tab:forestexact}', r'\footnotesize', r'\setlength{\tabcolsep}{2.6pt}', r'\begin{tabular}{llrrrr}', r'\toprule',
         r'Data & $m$ & Exact ratio & Restr. & Fix/full & Fitted \\', r'\midrule']
for ds in ['WDBC', 'Spambase', 'Ionosphere']:
    for m in [6, 9, 12]:
        rr = [r for r in rows if r['dataset'] == ds and r['m'] == m]
        ex = [r['ratio_exact_lower'] for r in rr]
        fv = [v['ratio_fitted'] for (d, s), v in fit.items() if d == ds and v['m'] == m] if m == 12 else []
        fcell = f"{st.median(fv):.2f}" if fv else ''
        lines.append(f"{ds if m == 6 else ''} & {m} & {st.median(ex):.2f} [{q(ex,.1):.2f}, {q(ex,.9):.2f}] & {st.median([r['ratio_v11menu'] for r in rr]):.2f} & {st.median([r['ratio_vs_fullinfo'] for r in rr]):.2f} & {fcell} \\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v12_forest_table.tex').write_text('\n'.join(lines) + '\n')

sr = [json.load(open(f)) for f in glob.glob(str(R / 'budget_trees' / '*.json'))]
lines = [r'\begin{table}[t]', r'\centering',
         r"\caption{Budgeted screening trees: records needed relative to branching (which asks the tree's own questions), median over two targets (random half, other sex) and three seeds. Best: optimal fixed-form design for the target law; Fitted: designed on source records; Guess: uniform path guessing; Two: follow the root question, then the best fixed form. $[1/\Gamma_P,N_P]$: medians of the bracket of Theorem~\ref{thm:bracket}.}",
         r'\label{tab:screening}', r'\small', r'\setlength{\tabcolsep}{3.2pt}', r'\begin{tabular}{lrrrrrr}', r'\toprule',
         r'Data, $b$ & Best & Fitted & Guess & Two & $1/\Gamma_P$ & $N_P$ \\', r'\midrule']
for ds in ['BRFSS', 'Thyroid']:
    for b in [3, 4, 5, 6]:
        rr = [r for r in sr if r['dataset'] == ds and r['b'] == b]
        if not rr: continue
        f = lambda k: st.median([r[k] for r in rr if k in r]) if any(k in r for r in rr) else float('nan')
        two = f('round2_oracle_ratio') if b > 2 else float('nan')
        lines.append(f"{ds}, {b} & {f('fixed_oracle_ratio'):.2f} & {f('fixed_fit_ratio'):.2f} & {f('fixed_ht_ratio'):.1f} & {two:.2f} & {f('bracket_lower'):.2f} & {f('bracket_upper'):.1f} \\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v12_screening_table.tex').write_text('\n'.join(lines) + '\n')
print(open(M / 'v12_forest_table.tex').read()); print(open(M / 'v12_screening_table.tex').read())

# ---- detailed screening table (appendix)
lines = [r'\begin{table}[h]', r'\centering',
         r"\caption{All screening settings: medians over three seeds of records needed relative to branching. Columns $r=2,\ldots$ follow the tree for $r-1$ questions and then use the best fixed form. Acc.: target accuracy of the screening decision. Paths: distinct padded path sets of the trained tree.}",
         r'\label{tab:screeningdetail}', r'\small', r'\begin{tabular}{lllrrrrrrrrrr}', r'\toprule',
         r'Data & $b$ & Target & Acc. & Paths & Best & Fitted & Guess & $r=2$ & $r=3$ & $r=4$ & $r=5$ & $[1/\Gamma_P,N_P]$ \\', r'\midrule']
for ds in ['BRFSS', 'Thyroid']:
    for b in [3, 4, 5, 6]:
        for shift in [False, True]:
            rr = [r for r in sr if r['dataset'] == ds and r['b'] == b and r['shift'] == shift]
            if not rr: continue
            med = lambda k: st.median([r[k] for r in rr])
            rounds = ' & '.join((f"{med(f'round{k}_oracle_ratio'):.2f}" if f'round{k}_oracle_ratio' in rr[0] else '') for k in range(2, 6))
            lines.append(f"{ds} & {b} & {'other sex' if shift else 'random half'} & {med('accuracy'):.3f} & {med('path_sets'):.0f} & {med('fixed_oracle_ratio'):.2f} & {med('fixed_fit_ratio'):.2f} & {med('fixed_ht_ratio'):.1f} & {rounds} & [{med('bracket_lower'):.2f}, {med('bracket_upper'):.1f}] \\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v12_screening_detail.tex').write_text('\n'.join(lines) + '\n')

# ---- MI table (appendix)
mi = [json.load(open(f)) for f in sorted(glob.glob(str(R / 'screening_mi' / '*.json')))]
lines = [r'\begin{table}[h]', r'\centering',
         r'\caption{Audit simulations with $n=1000$ target respondents and 400 replications (seed 0). Bias, standard deviation and RMSE are multiplied by 100; coverage of nominal 95\% intervals has Monte Carlo standard error about 0.011. MI: ten proper hot-deck imputations from complete source records.}',
         r'\label{tab:mi}', r'\small', r'\begin{tabular}{lllrrrrrr}', r'\toprule',
         r'Data, $b$ & Target & Design & Bias & SD & RMSE & Coverage & Width \\', r'\midrule']
for r in mi:
    for k, lab in [('branch', 'branching'), ('fixed', 'fitted fixed form'), ('mi', 'fixed form + MI')]:
        v = r[k]
        lines.append(f"{r['dataset'] + ', ' + str(r['b']) if k == 'branch' else ''} & {('other sex' if r['shift'] else 'random half') if k == 'branch' else ''} & {lab} & {100*v['bias']:.2f} & {100*v['sd']:.2f} & {100*v['rmse']:.2f} & {v['coverage']:.3f} & {100*v['width']:.2f} \\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v12_mi_table.tex').write_text('\n'.join(lines) + '\n')
print('detail and MI tables written;', len(mi), 'MI settings')
