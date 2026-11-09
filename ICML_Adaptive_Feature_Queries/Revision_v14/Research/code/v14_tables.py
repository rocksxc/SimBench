"""Generate the v14 tables (LaTeX) and print the summary numbers quoted in the text. Robust to partial results."""
import json, glob, statistics as st
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; R = HERE.parent / 'results'; M = HERE.parents[1] / 'Manuscript'
R12 = Path('/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/handoff/ICML_Handoff_v12/Revision_v12/Research/results')
R13 = Path('/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/v13/Research/results')
def load(p): return [json.load(open(f)) for f in sorted(glob.glob(str(p)))]
def med(v): v = [x for x in v if x is not None and np.isfinite(x)]; return st.median(v) if v else float('nan')
def pct(v, q): v = [x for x in v if x is not None and np.isfinite(x)]; return float(np.percentile(v, q)) if v else float('nan')
def f2(x, d=2): return ('%.*f' % (d, x)) if (x is not None and np.isfinite(x)) else '--'
S = {}

# ------------------------------------------------------------------ forests: cap grid
b3 = [r for r in load(R12 / 'forest_exact_tasks' / '*.json') if r['m'] > 3]
for r in b3: r['b'] = 3; r['ratio'] = r['ratio_exact_lower']; r['own'] = r.get('ratio_v11menu')
b3fit = {(r['dataset'], r['seed'], r['m']): r for r in load(R12 / 'forest_exact_b3fit' / '*.json')}
for r in b3:
    k = (r['dataset'], r['seed'], r['m'])
    if k in b3fit and 'ratio_fitted' in b3fit[k]: r['fit'] = b3fit[k]['ratio_fitted']
b2 = [r for r in load(R / 'forest_capgrid' / '*_b2_a0.01_boot0.json') if r['m'] > r['b']]
for r in b2: r['ratio'] = r['ratio_exact_lower']; r['own'] = r.get('ratio_compmenu'); r['fit'] = r.get('ratio_fitted')
b45 = [r for r in load(R / 'forest_capgrid_v14' / '*.json') if r['m'] > r['b']]
for r in b45: r['ratio'] = r['ratio_exact_lower']; r['own'] = r.get('ratio_compmenu'); r['fit'] = r.get('ratio_fitted')
rows = {2: b2, 3: b3, 4: [r for r in b45 if r['b'] == 4], 5: [r for r in b45 if r['b'] == 5]}
lines = [r'\begin{table}[t]', r'\centering',
         r'\caption{Exact records ratio $W_{\rm fixed}/W_{\rm branch}$ for independently retrained forest updates of depth $b$ with cap $b$ on WDBC, Spambase and Ionosphere: median [10th, 90th percentile] over binding tasks, medians by number of candidate features $m$, median ratio realized by designs fitted on training records, and median share of the log-gain captured when branching may use only the forests\textquotesingle{} own trees; -- marks cells not computed.}',
         r'\label{tab:capgrid}', r'\footnotesize', r'\setlength{\tabcolsep}{2.4pt}', r'\begin{tabular}{rrlrrrrr}', r'\toprule',
         r'$b$ & tasks & median [p10, p90] & $m{=}6$ & $m{=}9$ & $m{=}12$ & fitted & own \\', r'\midrule']
for b, rr in rows.items():
    if not rr: continue
    v = [r['ratio'] for r in rr]
    share = [np.log(r['own']) / np.log(r['ratio']) if (r.get('own') and r['ratio'] > 1.001) else None for r in rr]
    S[f'cap{b}'] = dict(n=len(rr), med=med(v), p10=pct(v, 10), p90=pct(v, 90), mx=max(v), m6=med([r['ratio'] for r in rr if r['m'] == 6]),
                        m9=med([r['ratio'] for r in rr if r['m'] == 9]), m12=med([r['ratio'] for r in rr if r['m'] == 12]),
                        fit=med([r.get('fit') for r in rr]), share=med(share),
                        fitdev=med([abs(r['fit'] / r['ratio'] - 1) for r in rr if r.get('fit')]),
                        fitdev_max=max([abs(r['fit'] / r['ratio'] - 1) for r in rr if r.get('fit')] or [float('nan')]),
                        nfit=sum(1 for r in rr if r.get('fit')))
    s = S[f'cap{b}']
    lines.append(f"{b} & {s['n']} & {f2(s['med'])} [{f2(s['p10'])}, {f2(s['p90'])}] & {f2(s['m6'])} & {f2(s['m9'])} & {f2(s['m12'])} & {f2(s['fit'])} & {f2(100*s['share'],0)}\\% \\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v14_capgrid_table.tex').write_text('\n'.join(lines) + '\n')
det = [r'\begin{table}[h]', r'\centering', r'\caption{Exact records ratio by cap, dimension and dataset (median over five splits; $b=3$ uses twenty splits and is detailed in Table~\ref{tab:forestexact}). Width: largest relative gap between the certified bounds of the branching constant.}', r'\label{tab:capdetail}', r'\small',
       r'\begin{tabular}{rrrrrrr}', r'\toprule', r'$b$ & $m$ & WDBC & Spambase & Ionosphere & fitted & width \\', r'\midrule']
for b in [2, 4, 5]:
    for m in [6, 9, 12]:
        rr = [r for r in rows[b] if r['m'] == m]
        if not rr: continue
        cells = [f2(med([r['ratio'] for r in rr if r['dataset'] == ds])) for ds in ['WDBC', 'Spambase', 'Ionosphere']]
        wid = max(abs(r['ratio_exact_upper'] - r['ratio_exact_lower']) / r['ratio_exact_lower'] for r in rr)
        det.append(f"{b} & {m} & {' & '.join(cells)} & {f2(med([r.get('fit') for r in rr]))} & {wid:.0e} \\\\")
det += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v14_capgrid_detail.tex').write_text('\n'.join(det) + '\n')
if b45:
    S['forest_v14_seconds'] = dict(med=med([r['seconds'] for r in b45]), mx=max(r['seconds'] for r in b45),
                                   b4m9=med([r['seconds'] for r in b45 if r['b'] == 4 and r['m'] == 9]),
                                   iters=med([r['iterations'] for r in b45]), maxiter=max(r['iterations'] for r in b45),
                                   width=max(abs(r['ratio_exact_upper'] - r['ratio_exact_lower']) / r['ratio_exact_lower'] for r in b45),
                                   profiles={ds: (min(r['n_profiles_eval'] for r in b45 if r['dataset'] == ds and r['m'] == 12) if any(r['dataset'] == ds and r['m'] == 12 for r in b45) else None,
                                                  max(r['n_profiles_eval'] for r in b45 if r['dataset'] == ds and r['m'] == 12) if any(r['dataset'] == ds and r['m'] == 12 for r in b45) else None) for ds in ['WDBC', 'Spambase', 'Ionosphere']})

# ------------------------------------------------------------------ screening
sc = load(R / 'screening_v14' / '*.json')
s21 = load(R / 'scale_v14' / '*.json')
def frac(r, key):
    fx = r['fixed_ratio']; v = r.get(key)
    if v is None or fx <= 1.01: return None
    return float(np.log(fx / v) / np.log(fx))
dl = [r'\begin{table}[h]', r'\centering', r'\caption{All screening settings (medians over three seeds). Ratios are records needed relative to branching. Best/Fitted: optimal and fitted fixed designs; PS: optimized path-set design (oracle/fitted); Guess: uniform path guessing; H2: heuristic two-round design; $r$: exact optimal $r$-round design; Lower, $N_P$: ends of Theorem~\ref{thm:bracket}.}', r'\label{tab:screeningdetail}',
      r'\scriptsize', r'\setlength{\tabcolsep}{2.2pt}', r'\begin{tabular}{lllrrrrrrrrrrrr}', r'\toprule',
      r'Data & $b$ & Target & Acc. & Paths & Best & Fitted & PS & PS fit & Guess & H2 & $r{=}2$ & $r{=}3$ & Lower & $N_P$ \\', r'\midrule']
for ds in ['BRFSS', 'Thyroid']:
    for b in [3, 4, 5, 6]:
        for sh in [False, True]:
            rr = [r for r in sc if r['dataset'] == ds and r['b'] == b and r['shift'] == sh]
            if not rr: continue
            guess = med([(r['path_sets'] * r['second'] - r['delta'] ** 2) / r['full_var'] for r in rr])
            dl.append(f"{ds} & {b} & {'other sex' if sh else 'random half'} & {f2(med([r['accuracy'] for r in rr]),3)} & {f2(med([r['path_sets'] for r in rr]),0)} & {f2(med([r['fixed_ratio'] for r in rr]))} & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['ps_fit_ratio'] for r in rr]))} & {f2(guess,1)} & {f2(med([r.get('heur2_ratio') for r in rr]))} & {f2(med([(r.get('round2_ratio') if r['fixed_ratio'] > 1 + 1e-6 else 1.0) for r in rr]))} & {f2(med([r.get('round3_ratio') for r in rr]) if b > 3 else float('nan'))} & {f2(med([r['bracket_lower'] for r in rr]))} & {f2(med([r['bracket_upper_completion'] for r in rr]),1)} \\\\")
dl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v14_screening_detail.tex').write_text('\n'.join(dl) + '\n')
br = [r for r in sc if r['dataset'] == 'BRFSS']
if br:
    S['screen'] = {b: dict(best=med([r['fixed_ratio'] for r in br if r['b'] == b]), fit=med([r['fixed_fit_ratio'] for r in br if r['b'] == b]),
                          two=med([r.get('round2_ratio') for r in br if r['b'] == b]), heur=med([r.get('heur2_ratio') for r in br if r['b'] == b]),
                          ps=med([r['ps_ratio'] for r in br if r['b'] == b]), psfit=med([r['ps_fit_ratio'] for r in br if r['b'] == b]),
                          low=med([r['bracket_lower'] for r in br if r['b'] == b]), up=med([r['bracket_upper_completion'] for r in br if r['b'] == b]),
                          frac2=med([frac(r, 'round2_ratio') for r in br if r['b'] == b]), fracheur=med([frac(r, 'heur2_ratio') for r in br if r['b'] == b]),
                          n=len([r for r in br if r['b'] == b])) for b in [3, 4, 5, 6]}
    gaps = [(r['ps_ratio'] - r['fixed_ratio']) / r['fixed_ratio'] for r in sc]
    gain = [r for r in sc + s21 if r['fixed_ratio'] > 1.01]
    gaps = [max(0.0, (r['ps_ratio'] - r['fixed_ratio']) / r['fixed_ratio']) for r in gain]
    S['ps_gap'] = dict(med=med(gaps), mx=max(gaps) if gaps else float('nan'), n=len(gaps), equal=sum(g < 1e-3 for g in gaps),
                       np_over=med([r['bracket_upper_completion'] / r['fixed_ratio'] for r in gain]))
    S['thyroid'] = dict(maxfixed=max([r['fixed_ratio'] for r in sc if r['dataset'] == 'Thyroid'] or [float('nan')]), n=len([r for r in sc if r['dataset'] == 'Thyroid']))
    pos = [r for r in sc if 'position' in r]
    S['position'] = dict(n=len(pos), branch=med([r['position']['0.1']['bias_branch_se'] for r in pos if r['dataset'] == 'BRFSS']),
                         fit=med([r['position']['0.1']['bias_fit_se'] for r in pos if r['dataset'] == 'BRFSS']),
                         branch_max=max([r['position']['0.1']['bias_branch_se'] for r in pos] or [float('nan')]),
                         fit_max=max([r['position']['0.1']['bias_fit_se'] for r in pos] or [float('nan')]),
                         rmse_win=sum(r['position']['0.1']['rmse_branch'] < r['position']['0.1']['rmse_fit'] for r in pos if r['dataset'] == 'BRFSS'),
                         nb=len([r for r in pos if r['dataset'] == 'BRFSS']))
    pl = [r'\begin{table}[h]', r'\centering', r'\caption{Position effects on the screening trees: median absolute bias in units of the clean branching standard error at $n=1000$, and the share of runs in which branching keeps the smaller RMSE at $n=1000$ (the last answer flips with probability $\epsilon$).}', r'\label{tab:position}', r'\small',
          r'\begin{tabular}{llrrrr}', r'\toprule', r'Data & $\epsilon$ & branching & fitted form & oracle form & branching RMSE smaller \\', r'\midrule']
    for ds in ['BRFSS', 'Thyroid']:
        rr = [r for r in pos if r['dataset'] == ds]
        for e in ['0.01', '0.03', '0.05', '0.1']:
            if not rr: continue
            win = sum(r['position'][e]['rmse_branch'] < r['position'][e]['rmse_fit'] for r in rr)
            pl.append(f"{ds} & {e} & {f2(med([r['position'][e]['bias_branch_se'] for r in rr]))} & {f2(med([r['position'][e]['bias_fit_se'] for r in rr]))} & {f2(med([r['position'][e]['bias_oracle_se'] for r in rr]))} & {win}/{len(rr)} \\\\")
    pl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v14_position_table.tex').write_text('\n'.join(pl) + '\n')

# ------------------------------------------------------------------ scale m = 21
tl = [r'\begin{table}[h]', r'\centering', r'\caption{All 21 BRFSS variables (random-half target; medians over three seeds). Forms: $\binom{21}b$. Time: median minutes for the certified fixed design.}', r'\label{tab:scale}', r'\small',
      r'\begin{tabular}{rrrrrrrrrrr}', r'\toprule', r'$b$ & forms & Acc. & items used & Best & Fitted & $r{=}2$ & PS & Lower & $N_P$ & time \\', r'\midrule']
for b in [3, 4, 5, 6]:
    rr = [r for r in s21 if r['b'] == b]
    if not rr: continue
    tl.append(f"{b} & {rr[0]['forms']} & {f2(med([r['accuracy'] for r in rr]),3)} & {f2(med([r['used_features'] for r in rr]),0)} & {f2(med([r['fixed_ratio'] for r in rr]))} & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med([(r.get('round2_ratio') if r['fixed_ratio'] > 1 + 1e-6 else 1.0) for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['bracket_lower'] for r in rr]))} & {f2(med([r['bracket_upper_completion'] for r in rr]),1)} & {f2(med([r['fixed_seconds'] / 60 for r in rr]),1)} \\\\")
tl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v14_scale_table.tex').write_text('\n'.join(tl) + '\n')
if s21:
    S['scale'] = {b: dict(best=med([r['fixed_ratio'] for r in s21 if r['b'] == b]), mx=max([r['fixed_ratio'] for r in s21 if r['b'] == b] or [float('nan')]),
                         two=med([r.get('round2_ratio') for r in s21 if r['b'] == b]), ps=med([r['ps_ratio'] for r in s21 if r['b'] == b]),
                         fit=med([r['fixed_fit_ratio'] for r in s21 if r['b'] == b]), low=med([r['bracket_lower'] for r in s21 if r['b'] == b]),
                         mins=med([r['fixed_seconds'] / 60 for r in s21 if r['b'] == b]), frac2=med([frac(r, 'round2_ratio') for r in s21 if r['b'] == b]),
                         n=len([r for r in s21 if r['b'] == b])) for b in [3, 4, 5, 6]}

# ------------------------------------------------------------------ shifts
sh = load(R / 'shift_mi_v14' / '*.json')
names = {'sex': 'sex', 'education': 'education', 'costbar': 'cost barrier', 'physhlth': 'poor health'}
hl = [r'\begin{table}[h]', r'\centering', r'\caption{Pre-specified shifts on BRFSS: simulated audits with $n=1000$ target respondents and 400 replications. Bias, SD and RMSE are multiplied by 100; coverage of nominal 95\% intervals has Monte Carlo standard error about 0.011. TV: total variation distance between source and target item profiles.}', r'\label{tab:shift}', r'\scriptsize', r'\setlength{\tabcolsep}{2.6pt}',
      r'\begin{tabular}{lrrlrrrrr}', r'\toprule', r'Shift & $b$ & TV & Design & Bias & SD & RMSE & Coverage & Width \\', r'\midrule']
for key in ['sex', 'education', 'costbar', 'physhlth']:
    for b in [4, 5]:
        rr = [r for r in sh if r['shift'] == key and r['b'] == b]
        if not rr: continue
        r = rr[0]; first = True
        for k, lab in [('branch', 'branching'), ('fixed', 'fitted fixed form'), ('regimp', 'regression imputation'), ('mi', 'multiple imputation')]:
            s = r[k]; hl.append(f"{names[key] if first else ''} & {b if first else ''} & {f2(r['tv_profiles']) if first else ''} & {lab} & {100*s['bias']:.2f} & {100*s['sd']:.2f} & {100*s['rmse']:.2f} & {s['coverage']:.3f} & {100*s['width']:.2f} \\\\"); first = False
hl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v14_shift_table.tex').write_text('\n'.join(hl) + '\n')
if sh:
    S['shift'] = {f"{r['shift']}_b{r['b']}": dict(reg_bias_se=abs(r['regimp']['bias']) / r['branch']['sd'], mi_bias_se=abs(r['mi']['bias']) / r['branch']['sd'],
                                              reg_cov=r['regimp']['coverage'], mi_cov=r['mi']['coverage'], fix_cov=r['fixed']['coverage'], br_cov=r['branch']['coverage'],
                                              reg_rmse=r['regimp']['rmse'] / r['branch']['rmse'], mi_rmse=r['mi']['rmse'] / r['branch']['rmse'], fix_rmse=r['fixed']['rmse'] / r['branch']['rmse'],
                                              tv=r['tv_profiles']) for r in sh}

iidmi = load(R / 'screening_mi_v13' / 'BRFSS_b*_iid.json')
if iidmi:
    S['shift'].update({f"iid_b{r['b']}": dict(reg_bias_se=abs(r['regimp']['bias']) / r['branch']['sd'], mi_bias_se=abs(r['mi']['bias']) / r['branch']['sd'],
                                              reg_cov=r['regimp']['coverage'], mi_cov=r['mi']['coverage'], fix_cov=r['fixed']['coverage'], br_cov=r['branch']['coverage'],
                                              reg_rmse=r['regimp']['rmse'] / r['branch']['rmse'], mi_rmse=r['mi']['rmse'] / r['branch']['rmse'], fix_rmse=r['fixed']['rmse'] / r['branch']['rmse'], tv=0.0) for r in iidmi})

# ------------------------------------------------------------------ pointer tree
pt = load(R / 'pointer_v14' / '*.json')
if pt:
    ptl = [r'\begin{table}[h]', r'\centering', r'\caption{Round constants of the binary pointer tree $B_{b-1}$ ($m=2^b-1$). Entries are $M_r(\U)$, a lower bound on $V_r$; for $b\le4$ the brackets give the worst profile of the uniform-optimal design, an upper bound on $V_r$. The last column is the upper bound $2^{b-2}$ of Theorem~\ref{thm:rounds}(a) for $r=2$.}', r'\label{tab:pointer}', r'\small',
           r'\begin{tabular}{rrlllll}', r'\toprule', r'$b$ & $m$ & fixed & $r=2$ & $r=3$ & $r=4$ & $2^{b-2}$ \\', r'\midrule']
    for r in sorted(pt, key=lambda r: r['b']):
        cells = []
        for k in range(1, 5):
            if k > r['b'] - 1: cells.append(''); continue
            lo = r.get(f'M{k}'); up = r.get(f'V{k}_upper')
            cells.append((f"{lo:.3f}" + (f" [{up:.3f}]" if (up is not None and up - lo > 5e-4) else '')) if lo is not None else '--')
        ptl.append(f"{r['b']} & {r['m']} & {' & '.join(cells)} & {2 ** (r['b'] - 2)} \\\\")
    ptl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v14_pointer_table.tex').write_text('\n'.join(ptl) + '\n')
    S['pointer'] = {r['b']: {k: r.get(k) for k in ['M1', 'M2', 'M3', 'M4', 'V2_upper', 'V3_upper']} for r in pt}
json.dump(S, open(R / 'v14_summary.json', 'w'), indent=1, default=str)
print(json.dumps(S, indent=1, default=str)[:6000])

# ------------------------------------------------------------------ main-text screening table (twelve items and all 21 items)
n6 = sum(1 for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 6 and 'round2_iterations' in r)
fr_runs = [frac(r, 'round2_ratio') for r in sc if r['dataset'] == 'BRFSS' and r['fixed_ratio'] > 1.01 and r.get('round2_ratio') is not None]
S['frac2_min'] = min([x for x in fr_runs if x is not None] or [float('nan')]); S['frac2_n'] = len([x for x in fr_runs if x is not None])
S['n6_two'] = n6
ml = [r'\begin{table}[t]', r'\centering',
      r'\caption{Screening trees: records needed relative to branching, which asks the tree\textquotesingle s own questions (medians over targets and seeds). Best, Fitted: optimal fixed design at the target law and on source records. Two: exact optimal two-round design (at $b=6$ for ' + str(n6) + r' of six trees; not computed for 21 items, --); H2: following the root question, then the best fixed form. Lower, PS, $N_P$: the lower end of Theorem~\ref{thm:bracket}, the optimized path-set end of Proposition~\ref{prop:uppermain} and the completion-only end.}',
      r'\label{tab:screening}', r'\footnotesize', r'\setlength{\tabcolsep}{2.4pt}', r'\begin{tabular}{lrrrrrrr}', r'\toprule',
      r'Data, $b$ & Best & Fitted & Two & H2 & Lower & PS & $N_P$ \\', r'\midrule']
for b in [4, 5, 6]:
    rr = [r for r in sc if r['dataset'] == 'BRFSS' and r['b'] == b]
    if rr:
        ml.append(f"BRFSS, {b} & {f2(med([r['fixed_ratio'] for r in rr]))} & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med([(r.get('round2_ratio') if r['fixed_ratio'] > 1 + 1e-6 else 1.0) for r in rr]))} & {f2(med([r.get('heur2_ratio') for r in rr]))} & {f2(med([r['bracket_lower'] for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['bracket_upper_completion'] for r in rr]),1)} \\\\")
rr = [r for r in sc if r['dataset'] == 'Thyroid']
if rr:
    ml.append(f"Thyroid, 3--6 & {f2(med([r['fixed_ratio'] for r in rr]))} & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med([(r.get('round2_ratio') if r['fixed_ratio'] > 1 + 1e-6 else 1.0) for r in rr]))} & -- & {f2(med([r['bracket_lower'] for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['bracket_upper_completion'] for r in rr]),1)} \\\\")
if s21:
    ml.append(r'\addlinespace[2pt]')
    for b in [3, 4, 5, 6]:
        rr = [r for r in s21 if r['b'] == b]
        if rr:
            ml.append(f"BRFSS-21, {b} & {f2(med([r['fixed_ratio'] for r in rr]))} & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med([(r.get('round2_ratio') if r['fixed_ratio'] > 1 + 1e-6 else 1.0) for r in rr]))} & -- & {f2(med([r['bracket_lower'] for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['bracket_upper_completion'] for r in rr]),1)} \\\\")
ml += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v14_screening_table.tex').write_text('\n'.join(ml) + '\n')
print('main screening table rows', len(ml) - 13)

# ------------------------------------------------------------------ overall extremes and cost thresholds
allmax = [S[f'cap{b}']['mx'] for b in [2, 3, 4, 5] if f'cap{b}' in S]
allmax += [r['fixed_ratio'] for r in sc] + [r['fixed_ratio'] for r in s21]
S['max_ratio_all'] = max(allmax) if allmax else float('nan')
S['max_ratio_screen'] = max([r['fixed_ratio'] for r in sc] or [float('nan')])
S['cost'] = {}
for b in [4, 5, 6]:
    rr = [r for r in sc if r['dataset'] == 'BRFSS' and r['b'] == b]
    if rr:
        rho = med([r['fixed_ratio'] for r in rr]); S['cost'][b] = dict(rho=rho, cstar=(12 - rho * b) / (rho - 1) if rho > 1 else float('inf'))
if b45:
    S['forest_cert'] = dict(gap=max(abs(r['ratio_exact_upper'] - r['ratio_exact_lower']) / r['ratio_exact_lower'] for r in b45),
                            iters=med([r['iterations'] for r in b45]), secs=med([r['seconds'] for r in b45]), n=len(b45))
json.dump(S, open(R / 'v14_summary.json', 'w'), indent=1, default=str)
json.dump(S, open(R / 'v14_summary.json', 'w'), indent=1, default=str)
