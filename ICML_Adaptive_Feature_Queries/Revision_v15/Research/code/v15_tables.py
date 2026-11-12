"""Generate the v15 tables (LaTeX), the summary results/v15_summary.json and the number macros Manuscript/v15_numbers.tex.
Every number quoted in the v15 text is one of these macros or sits in one of these tables. Robust to partial results."""
import json, glob, statistics as st
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; R = HERE.parent / 'results'; M = HERE.parents[1] / 'Manuscript'
R12 = Path('/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/handoff/ICML_Handoff_v12/Revision_v12/Research/results')
def load(p): return [json.load(open(f)) for f in sorted(glob.glob(str(p)))]
def fin(v): return [x for x in v if x is not None and np.isfinite(x)]
def med(v): v = fin(v); return st.median(v) if v else float('nan')
def mn(v): v = fin(v); return min(v) if v else float('nan')
def mx(v): v = fin(v); return max(v) if v else float('nan')
def f2(x, d=2): return ('%.*f' % (d, x)) if (x is not None and np.isfinite(x)) else '--'
S = {}; N = {}  # summary; number macros (name -> string)

# ================================================================== forests
b3 = [r for r in load(R12 / 'forest_exact_tasks' / '*.json') if r['m'] > 3]
for r in b3: r['b'] = 3; r['ratio'] = r['ratio_exact_lower']; r['own'] = r.get('ratio_v11menu'); r['capfix'] = r['ratio_vs_fullinfo']
b3fit = {(r['dataset'], r['seed'], r['m']): r for r in load(R12 / 'forest_exact_b3fit' / '*.json')}
for r in b3:
    k = (r['dataset'], r['seed'], r['m'])
    if k in b3fit and 'ratio_fitted' in b3fit[k]: r['fit'] = b3fit[k]['ratio_fitted']
b2 = [r for r in load(R / 'forest_capgrid' / '*_b2_a0.01_boot0.json') if r['m'] > r['b']]
for r in b2: r['ratio'] = r['ratio_exact_lower']; r['own'] = r.get('ratio_compmenu'); r['fit'] = r.get('ratio_fitted'); r['capfix'] = r['ratio_fixed_vs_fullinfo']
b4 = [r for r in load(R / 'forest_capgrid_v14' / '*.json') if r['m'] > r['b'] and r['b'] == 4]
for r in b4: r['ratio'] = r['ratio_exact_lower']; r['own'] = r.get('ratio_compmenu'); r['fit'] = r.get('ratio_fitted'); r['capfix'] = r['ratio_fixed_vs_fullinfo']
rows = {2: b2, 3: b3, 4: b4}
fr = load(R / 'forest_rounds_v15' / '*.json')
frb = {b: [r for r in fr if r['b'] == b] for b in (3, 4)}
# consistency of the two engines on the overlapping b = 3 tasks
ov = []
key3 = {(r['dataset'], r['seed'], r['m']): r for r in b3}
for r in frb[3]:
    k = (r['dataset'], r['seed'], r['m'])
    if k in key3: ov.append(abs(r['fixed_ratio'] / key3[k]['ratio'] - 1))
S['forest_engine_overlap'] = dict(n=len(ov), max_rel=mx(ov), agree=sum(1 for x in ov if x <= 2e-4), max_rel_agree=mx([x for x in ov if x <= 2e-4]))
lines = [r'\begin{table}[t]', r'\centering',
         r'\caption{Forest updates of depth $b$ under cap $b$ (WDBC, Spambase, Ionosphere; binding tasks). Fixed/branch: exact $W_{\rm fixed}/W_{\rm branch}$, median [minimum, maximum]. Fit: median excess of the ratio realized by designs optimized on training records over the exact ratio of the same task ($^\dagger$the 15 tasks with $m=12$). Own: share of the log-gap captured when branching may use only the forests\textquotesingle{} own trees. Two: exact optimal two-round design, $W_2/W_{\rm branch}$ ($^\ddagger$five splits per cell: NFRTHREE and NFRFOUR tasks; at $b=2$ two rounds are branching). Cap: $W_{\rm fixed}$ and $W_{\rm branch}$ relative to the full-information variance.}',
         r'\label{tab:capgrid}', r'\footnotesize', r'\setlength{\tabcolsep}{2.6pt}', r'\begin{tabular}{rrlrrrrr}', r'\toprule',
         r' & & & & & & \multicolumn{2}{c}{Cap: /full} \\', r'$b$ & tasks & Fixed/branch & Fit & Own & Two & fixed & branch \\', r'\midrule']
S['cap'] = {}
for b, rr in rows.items():
    if not rr: continue
    v = [r['ratio'] for r in rr]
    share = [np.log(r['own']) / np.log(r['ratio']) if (r.get('own') and r['ratio'] > 1.001) else None for r in rr]
    two = [r['round2_ratio'] for r in frb.get(b, [])]; rec = [r['round2_recovered'] for r in frb.get(b, [])]
    s = dict(n=len(rr), med=med(v), min=min(v), max=max(v), m6=med([r['ratio'] for r in rr if r['m'] == 6]), m9=med([r['ratio'] for r in rr if r['m'] == 9]),
             m12=med([r['ratio'] for r in rr if r['m'] == 12]), fit=med([r.get('fit') for r in rr]), nfit=sum(1 for r in rr if r.get('fit')),
             fitdev=med([abs(r['fit'] / r['ratio'] - 1) for r in rr if r.get('fit')]), share=med(share),
             two=med(two), two_max=mx(two), ntwo=len(two), rec_med=med(rec), rec_min=mn(rec), rec_max=mx(rec),
             capfix=med([r['capfix'] for r in rr]), capfix_min=min(r['capfix'] for r in rr), capfix_max=max(r['capfix'] for r in rr),
             capbr=med([r['capfix'] / r['ratio'] for r in rr]))
    S['cap'][b] = s
    twocell = '1' if b == 2 else (f2(s['two']) + r'$^\ddagger$' if s['ntwo'] else '--')
    lines.append(f"{b} & {s['n']} & {f2(s['med'])} [{f2(s['min'])}, {f2(s['max'])}] & +{f2(100*s['fitdev'],0)}\\%{'$^\\dagger$' if b == 3 else ''} & {f2(100*s['share'],0)}\\% & {twocell} & {f2(s['capfix'],1)} & {f2(s['capbr'],1)} \\\\")
lines += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
txt = '\n'.join(lines).replace('NFRTHREE', str(len(frb[3]))).replace('NFRFOUR', str(len(frb[4])))
(M / 'v15_capgrid_table.tex').write_text(txt + '\n')
# appendix: forest detail by cap, dimension, dataset, with two-round results
det = [r'\begin{table}[h]', r'\centering', r'\caption{Forest updates by cap and dimension (medians over splits). Fixed/branch at $b=3$ uses twenty splits per dataset (Table~\ref{tab:forestexact}); the two-round columns use five splits per dataset and the solver of Appendix~\ref{app:engine}: $W_2/W_{\rm branch}$, the share of the log-gap that the second round recovers (median and minimum over tasks), and the largest relative gap between the certified bounds of the branching constant.}',
       r'\label{tab:capdetail}', r'\small', r'\begin{tabular}{rrrrrrrrrr}', r'\toprule',
       r'$b$ & $m$ & WDBC & Spambase & Ionosphere & fitted & $W_2/W_{\rm branch}$ & recovered & min & width \\', r'\midrule']
for b in [2, 3, 4]:
    for m in [6, 9, 12]:
        rr = [r for r in rows[b] if r['m'] == m]
        if not rr: continue
        cells = [f2(med([r['ratio'] for r in rr if r['dataset'] == ds])) for ds in ['WDBC', 'Spambase', 'Ionosphere']]
        f5 = [r for r in frb.get(b, []) if r['m'] == m]
        det.append(f"{b} & {m} & {' & '.join(cells)} & {f2(med([r.get('fit') for r in rr]))} & {f2(med([r['round2_ratio'] for r in f5]),3) if f5 else '--'} & {(f2(100*med([r['round2_recovered'] for r in f5]),0)+chr(92)+'%') if f5 else '--'} & {(f2(100*mn([r['round2_recovered'] for r in f5]),0)+chr(92)+'%') if f5 else '--'} & {('%.0e' % max(r['branch_gap'] for r in f5)) if f5 else '--'} \\\\")
det += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v15_capgrid_detail.tex').write_text('\n'.join(det) + '\n')
if frb[4]:
    S['forest_round3_b4'] = dict(med=med([r.get('round3_ratio') for r in frb[4]]), rec=med([r.get('round3_recovered') for r in frb[4]]))
allrec = [r['round2_recovered'] for r in fr if np.isfinite(r['round2_recovered'])]
S['forest_two'] = dict(n=len(allrec), rec_min=mn(allrec), rec_max=mx(allrec), rec_med=med(allrec), ratio_max=mx([r['round2_ratio'] for r in fr]), ratio_med=med([r['round2_ratio'] for r in fr]),
                       seconds_med=med([r['seconds'] for r in fr]), gap_max=mx([r['branch_gap'] for r in fr]))

# ================================================================== screening (12 items), with the v15 additions
sc = load(R / 'screening_v14' / '*.json')
r6 = {(r['shift'], r['seed']): r for r in load(R / 'screening_v14_b6r2' / '*.json')}
for r in sc:  # exact two-round results at b = 6 are computed separately; copy the round keys after checking the run
    k = (r['shift'], r['seed'])
    if r['dataset'] == 'BRFSS' and r['b'] == 6 and k in r6:
        assert abs(r6[k]['fixed_ratio'] - r['fixed_ratio']) < 1e-6
        for kk in r6[k]:
            if kk.startswith('round'): r[kk] = r6[k][kk]
s15 = {(r['dataset'], r['b'], r['shift'], r['seed']): r for r in load(R / 'screening_v15' / '*.json')}
s15l = {(r['dataset'], r['b'], r['shift'], r['seed']): r for r in load(R / 'screening_v15_light' / '*.json')}
comp = {(r['dataset'], r['b'], r['shift'], r['seed']): r for r in load(R / 'two_round_computable_v15' / '*.json')}
b6b = {(r['shift'], r['seed']): r for r in load(R / 'two_round_b6_v15' / '*.json')}
comp_agree = 0
for r in sc:
    a = s15.get((r['dataset'], r['b'], r['shift'], r['seed']))
    sec = r['second']; d2 = r['delta'] ** 2; var = r['full_var']
    r['lower_c'] = var / (r['Gamma_P'] * sec - d2)  # 1 / rho_P^2
    if a:
        assert abs(a['fixed_ratio'] - r['fixed_ratio']) < 1e-5, (r['dataset'], r['b'], r['shift'], r['seed'])
        for kk in ['label_fixed_ratio', 'label_fixed_ratio_lower', 'strat_fixed_ratio', 'uniform_ht_ratio', 'uniform_opt_ratio', 'centered_upper', 'round2_fit_ratio']:
            r[kk] = a.get(kk)
        if r['fixed_ratio'] <= 1 + 1e-7: r['round2_fit_ratio'] = r['fixed_fit_ratio']
    al = s15l.get((r['dataset'], r['b'], r['shift'], r['seed']))
    if al:  # closed-form quantities computed separately (uniform designs, centered N_P)
        assert abs(al['delta'] - r['delta']) < 1e-9
        for kk in ['uniform_ht_ratio', 'uniform_opt_ratio', 'centered_upper']:
            if r.get(kk) is None: r[kk] = al[kk]
            else: assert abs(r[kk] - al[kk]) < 1e-6 * max(1, abs(al[kk])), (kk, r[kk], al[kk])
    r['two'] = (r.get('round2_ratio') if r['fixed_ratio'] > 1 + 1e-6 else 1.0); r['two_lower'] = r['two']
    r['two_computed'] = ('round2_iterations' in r) or r['fixed_ratio'] <= 1 + 1e-6
    c = comp.get((r['dataset'], r['b'], r['shift'], r['seed']))
    if c:
        r['computable'] = c['computable']; r['items'] = c['items']
        if r['two_computed']:  # the enumeration and the solver must agree on every run that has both
            assert c['computable'] == (r['two'] <= 1 + 1e-6), (r['dataset'], r['b'], r['shift'], r['seed']); comp_agree += 1
        elif c['computable']:
            r['two'] = 1.0; r['two_lower'] = 1.0; r['two_computed'] = True; r['two_by_enumeration'] = True
    bb = b6b.get((r['shift'], r['seed'])) if (r['dataset'] == 'BRFSS' and r['b'] == 6) else None
    if bb and not r['two_computed']:
        assert abs(bb['fixed_ratio'] - r['fixed_ratio']) < 1e-5
        r['two'] = bb['round2_ratio_upper']; r['two_lower'] = bb['round2_ratio_lower']; r['two_computed'] = True; r['two_bounded'] = bool(r['two'] - r['two_lower'] > 1e-3 * r['two'])  # a bracket closed to 0.1% counts as exact
s21 = load(R / 'scale_v14' / '*.json')
np21 = {(r['b'], r['seed']): r for r in load(R / 'scale_v15_np' / '*.json')}
for r in s21:
    sec = r['full_var'] + r['delta'] ** 2; r['lower_c'] = r['full_var'] / (r['Gamma_P'] * sec - r['delta'] ** 2)
    a = np21.get((r['b'], r['seed'])); r['centered_upper'] = a['centered_upper'] if a else None
    c = comp.get(('BRFSS21', r['b'], False, r['seed'])); r['computable'] = c['computable'] if c else None; r['items'] = c['items'] if c else None
    r['two'] = 1.0 if (r['fixed_ratio'] <= 1 + 1e-6 or r['computable']) else None
def frac(r, key):
    fx = r['fixed_ratio']; v = r.get(key)
    if v is None or fx <= 1.01: return None
    return float(np.log(fx / max(v, 1.0)) / np.log(fx))
def grp(ds, b): return [r for r in sc if r['dataset'] == ds and (r['b'] == b if b else True)]
head = (r'Data, $b$ & runs & Best & [min, max] & Fitted & Label & Two & Two fit. & Uniform & $1/\rho_P^2$ & PS & $N_P$ \\')
ml = [r'\begin{table*}[t]', r'\centering',
      r'\caption{Screening trees: records needed relative to branching, which asks the tree\textquotesingle s own questions and attains the full-information variance (medians over targets and seeds; the range is over runs). Best: optimal fixed design over all forms at the target law. Fitted: the same program on source records, evaluated at the target. Label: optimal fixed design whose form probabilities may depend on the label. Two: exact optimal two-round design (TWOSIXNOTE). Two fit.: two-round design fitted on source records. Uniform: balanced random forms (uniform over all $\binom{12}b$ forms) with the optimal scores for that design. $1/\rho_P^2$, $N_P$: the ends of Theorem~\ref{thm:bracket}; PS: optimized path-set design. -- not computed.}',
      r'\label{tab:screening}', r'\footnotesize', r'\setlength{\tabcolsep}{5pt}', r'\begin{tabular}{lrrlrrrrrrrr}', r'\toprule', head, r'\midrule']
def mrow(lab, rr, full=True):
    two = [r['two'] for r in rr if r.get('two_computed')]
    return (f"{lab} & {len(rr)} & {f2(med([r['fixed_ratio'] for r in rr]))} & [{f2(mn([r['fixed_ratio'] for r in rr]))}, {f2(mx([r['fixed_ratio'] for r in rr]))}] & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & "
            f"{f2(med([r.get('label_fixed_ratio') for r in rr]))} & {(('$\\le$' if any(r.get('two_bounded') for r in rr) else '') + f2(med(two))) if len(two) == len(rr) else '--'} & {f2(med([r.get('round2_fit_ratio') for r in rr]))} & {f2(med([r.get('uniform_opt_ratio') for r in rr]),1)} & "
            f"{f2(med([r['lower_c'] for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r.get('centered_upper') for r in rr]),1)} \\\\")
S['screen'] = {}
for b in [3, 4, 5, 6]:
    rr = grp('BRFSS', b)
    if not rr: continue
    ml.append(mrow(f'BRFSS, {b}', rr))
    gain = [r for r in rr if r['fixed_ratio'] > 1.01]
    S['screen'][b] = dict(n=len(rr), ngain=len(gain), best=med([r['fixed_ratio'] for r in rr]), min=mn([r['fixed_ratio'] for r in rr]), max=mx([r['fixed_ratio'] for r in rr]),
                          fit=med([r['fixed_fit_ratio'] for r in rr]), label=med([r.get('label_fixed_ratio') for r in rr]),
                          label_drop_max=mx([1 - r['label_fixed_ratio'] / r['fixed_ratio'] for r in rr if r.get('label_fixed_ratio')]),
                          strat_drop_max=mx([1 - r['strat_fixed_ratio'] / r['fixed_ratio'] for r in rr if r.get('strat_fixed_ratio')]),
                          two=med([r['two'] for r in rr if r['two_computed']]), ntwo=sum(1 for r in rr if r['two_computed']), ntwo_gain=sum(1 for r in gain if r['two_computed']),
                          two_max=mx([r['two'] for r in rr if r['two_computed']]),
                          twofit=med([r.get('round2_fit_ratio') for r in rr]), twofit_max=mx([r.get('round2_fit_ratio') for r in rr]),
                          unif=med([r.get('uniform_opt_ratio') for r in rr]), unif_min=mn([r.get('uniform_opt_ratio') for r in rr]), unif_max=mx([r.get('uniform_opt_ratio') for r in rr]),
                          unifht=med([r.get('uniform_ht_ratio') for r in rr]), unifht_min=mn([r.get('uniform_ht_ratio') for r in rr]), unifht_max=mx([r.get('uniform_ht_ratio') for r in rr]),
                          lower=med([r['lower_c'] for r in rr]), ps=med([r['ps_ratio'] for r in rr]), upper=med([r.get('centered_upper') for r in rr]),
                          heur=med([r.get('heur2_ratio') for r in rr]), fracheur=med([frac(r, 'heur2_ratio') for r in rr]))
rr = grp('Thyroid', None)
if rr: ml.append(mrow('Thyroid, 3--6', rr)); S['thyroid'] = dict(n=len(rr), maxfixed=mx([r['fixed_ratio'] for r in rr]), unif=med([r.get('uniform_opt_ratio') for r in rr]))
if s21:
    ml.append(r'\addlinespace[2pt]')
    for b in [3, 4]:
        rr = [r for r in s21 if r['b'] == b]
        if rr:
            ml.append(f"BRFSS-21, {b} & {len(rr)} & {f2(med([r['fixed_ratio'] for r in rr]))} & [{f2(mn([r['fixed_ratio'] for r in rr]))}, {f2(mx([r['fixed_ratio'] for r in rr]))}] & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & -- & {'1.00' if all(r['two'] == 1.0 for r in rr) else '--'} & -- & -- & {f2(med([r['lower_c'] for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['centered_upper'] for r in rr]),1)} \\\\")
    S['scale'] = {b: dict(n=len([r for r in s21 if r['b'] == b]), best=med([r['fixed_ratio'] for r in s21 if r['b'] == b]), max=mx([r['fixed_ratio'] for r in s21 if r['b'] == b]),
                         fit=med([r['fixed_fit_ratio'] for r in s21 if r['b'] == b]), ps=med([r['ps_ratio'] for r in s21 if r['b'] == b]),
                         mins=med([r['fixed_seconds'] / 60 for r in s21 if r['b'] == b])) for b in [3, 4]}
ml += [r'\bottomrule', r'\end{tabular}', r'\end{table*}']
n6 = sum(1 for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 6 and r['two_computed'])
n6all = sum(1 for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 6)
nb6 = sum(1 for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 6 and r.get('two_bounded'))
note = ('at $b=6$ for ' + str(n6) + ' of the ' + str(n6all) + ' runs') if n6 < n6all else (('at $b=6$ the median includes certified upper bounds from feasible two-round designs for ' + str(nb6) + ' runs, Table~\\ref{tab:runs}') if nb6 else 'all runs')
(M / 'v15_screening_table.tex').write_text('\n'.join(ml).replace('TWOSIXNOTE', note) + '\n')
S['n6_two'] = n6; S['n6_all'] = n6all
# two-round recovery over all BRFSS runs with a gain and a computed two-round optimum
br_gain = [r for r in sc if r['dataset'] == 'BRFSS' and r['fixed_ratio'] > 1.01]
for r in br_gain: r['two_frac'] = float(np.log(r['fixed_ratio'] / max(r['two'], 1.0)) / np.log(r['fixed_ratio'])) if r['two_computed'] else None
fr2 = [(r['two_frac'], r) for r in br_gain if r['two_computed']]
ex2 = [(x, r) for x, r in fr2 if not r.get('two_bounded')]; bd2 = [(x, r) for x, r in fr2 if r.get('two_bounded')]
S['screen_two'] = dict(n=len(ex2), ngain=len(br_gain), rec_min=mn([x for x, _ in ex2]), ratio_max=mx([r['two'] for _, r in ex2]), bounded_rec_min=mn([x for x, _ in bd2]), bounded_ratio_max=mx([r['two'] for _, r in bd2]), bounded_ratio_min=mn([r['two'] for _, r in bd2]), computable=sum(1 for r in sc if r['dataset'] == 'BRFSS' and r.get('computable')), nbrfss=sum(1 for r in sc if r['dataset'] == 'BRFSS'), comp_agree=comp_agree, bounded=sum(1 for _, r in fr2 if r.get('two_bounded')), bounded_gap=mx([r['two'] - r['two_lower'] for _, r in fr2 if r.get('two_bounded')]),
                       fit_max=mx([r.get('round2_fit_ratio') for r in br_gain]), nfit=len(fin([r.get('round2_fit_ratio') for r in br_gain])),
                       fit_med=med([r.get('round2_fit_ratio') for r in br_gain]))
gains_all = [r for r in sc + s21 if r['fixed_ratio'] > 1.01]
psg = [max(0.0, r['ps_ratio'] / r['fixed_ratio'] - 1) for r in gains_all]
S['ps_gap'] = dict(n=len(psg), med=med(psg), max=mx(psg), np_over=med([r['centered_upper'] / r['fixed_ratio'] for r in gains_all if r.get('centered_upper')]),
                   low_under=med([r['fixed_ratio'] / r['lower_c'] for r in gains_all]))
lab = [r for r in sc if r.get('label_fixed_ratio') is not None]
S['label'] = dict(n=len(lab), drop_max=mx([1 - r['label_fixed_ratio'] / r['fixed_ratio'] for r in lab]), drop_med=med([1 - r['label_fixed_ratio'] / r['fixed_ratio'] for r in lab if r['fixed_ratio'] > 1.01]),
                  cert_gap=mx([r['label_fixed_ratio'] - r['label_fixed_ratio_lower'] for r in lab]),
                  strat_n=len([r for r in lab if r.get('strat_fixed_ratio')]), strat_drop_max=mx([1 - r['strat_fixed_ratio'] / r['fixed_ratio'] for r in lab if r.get('strat_fixed_ratio')]))
fitdev = [r['fixed_fit_ratio'] / r['fixed_ratio'] - 1 for r in gains_all]
S['fit'] = dict(med=med(fitdev), max=mx(fitdev), n=len(fitdev))
# appendix: detail by target
dl = [r'\begin{table}[h]', r'\centering', r'\caption{All screening settings (medians over three seeds). Ratios are records needed relative to branching. Best/Fitted: optimal and fitted fixed designs; Label, Strat.: optimal fixed designs whose form probabilities depend on the label, and on the label and sex; PS: optimized path-set design (oracle/fitted); H2: heuristic two-round design; $r{=}2,3$: exact optimal $r$-round designs; 2 fit.: fitted two-round design; U-HT, U-opt: uniform design over all forms with monomial Horvitz--Thompson scores and with optimal scores; $1/\rho_P^2$, $N_P$: ends of Theorem~\ref{thm:bracket}.}', r'\label{tab:screeningdetail}',
      r'\scriptsize', r'\setlength{\tabcolsep}{2.0pt}', r'\begin{tabular}{lllrrrrrrrrrrrrrrrr}', r'\toprule',
      r'Data & $b$ & Target & Acc. & Paths & Best & Fitted & Label & Strat. & PS & PS fit & H2 & $r{=}2$ & $r{=}3$ & 2 fit. & U-HT & U-opt & $1/\rho_P^2$ & $N_P$ \\', r'\midrule']
for ds in ['BRFSS', 'Thyroid']:
    for b in [3, 4, 5, 6]:
        for sh in [False, True]:
            rr = [r for r in sc if r['dataset'] == ds and r['b'] == b and r['shift'] == sh]
            if not rr: continue
            two = [r['two'] for r in rr if r['two_computed']]
            dl.append(f"{ds} & {b} & {'other sex' if sh else 'random half'} & {f2(med([r['accuracy'] for r in rr]),3)} & {f2(med([r['path_sets'] for r in rr]),0)} & {f2(med([r['fixed_ratio'] for r in rr]))} & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med([r.get('label_fixed_ratio') for r in rr]))} & {f2(med([r.get('strat_fixed_ratio') for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['ps_fit_ratio'] for r in rr]))} & {f2(med([r.get('heur2_ratio') for r in rr]))} & {f2(med(two)) if two else '--'} & {f2(med([r.get('round3_ratio') for r in rr]) if b > 3 else float('nan'))} & {f2(med([r.get('round2_fit_ratio') for r in rr]))} & {f2(med([r.get('uniform_ht_ratio') for r in rr]),1)} & {f2(med([r.get('uniform_opt_ratio') for r in rr]),1)} & {f2(med([r['lower_c'] for r in rr]))} & {f2(med([r.get('centered_upper') for r in rr]),1)} \\\\")
dl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v15_screening_detail.tex').write_text('\n'.join(dl) + '\n')
def twocell(r):
    if not r['two_computed']: return '--'
    if r['two'] - r['two_lower'] > 2e-3: return f"[{r['two_lower']:.3f}, {r['two']:.3f}]"
    return f2(r['two'], 3)
# appendix: every BRFSS run (traceability of ranges and maxima)
rl = [r'\begin{table}[h]', r'\centering', r'\caption{Every BRFSS screening run (twelve items; R: random-half target, S: other-sex target; seeds 0--2) and every 21-item run: records needed relative to branching. Items: number of items the decision depends on. Two: exact optimal two-round design; a bracket gives the certified lower and upper bounds reached within the time budget. -- not computed.}', r'\label{tab:runs}',
      r'\scriptsize', r'\setlength{\tabcolsep}{3.2pt}', r'\begin{tabular}{llrrrrrrrrrr}', r'\toprule', r'Run & $b$ & Acc. & Items & Paths & Best & Fitted & Label & Two & Two fit. & PS & $1/\rho_P^2$ \\', r'\midrule']
for b in [3, 4, 5, 6]:
    for sh in [False, True]:
        for r in sorted([r for r in sc if r['dataset'] == 'BRFSS' and r['b'] == b and r['shift'] == sh], key=lambda r: r['seed']):
            rl.append(f"{'S' if sh else 'R'}{r['seed'] - 20261108} & {b} & {f2(r['accuracy'],3)} & {r.get('items', '--')} & {r['path_sets']} & {f2(r['fixed_ratio'],3)} & {f2(r['fixed_fit_ratio'],3)} & {f2(r.get('label_fixed_ratio'),3)} & {twocell(r)} & {f2(r.get('round2_fit_ratio'),3)} & {f2(r['ps_ratio'],3)} & {f2(r['lower_c'],3)} \\\\")
rl.append(r'\addlinespace[2pt]')
for r in sorted(s21, key=lambda r: (r['b'], r['seed'])):
    rl.append(f"21 items, R{r['seed'] - 20261108} & {r['b']} & {f2(r['accuracy'],3)} & {r['items']} & {r['path_sets']} & {f2(r['fixed_ratio'],3)} & {f2(r['fixed_fit_ratio'],3)} & -- & {'1.000' if r['two'] == 1.0 else '--'} & -- & {f2(r['ps_ratio'],3)} & {f2(r['lower_c'],3)} \\\\")
rl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v15_runs_table.tex').write_text('\n'.join(rl) + '\n')
# 21-item table (appendix)
same21 = sum(1 for r in s21 if any(q['dataset'] == 'BRFSS' and q['b'] == r['b'] and not q['shift'] and q['seed'] == r['seed'] and abs(q['fixed_ratio'] - r['fixed_ratio']) < 1e-3 and abs(q['accuracy'] - r['accuracy']) < 1e-9 for q in sc) and r['b'] == 4)
S['scale_same_tree_b4'] = same21
tl = [r'\begin{table}[h]', r'\centering', r'\caption{All 21 BRFSS variables (random-half target; medians over three seeds). Forms: $\binom{21}b$. Time: median minutes for the certified fixed design on one core.}', r'\label{tab:scale}', r'\small',
      r'\begin{tabular}{rrrrrrrrrr}', r'\toprule', r'$b$ & forms & Acc. & items used & Best & Fitted & PS & $1/\rho_P^2$ & $N_P$ & time \\', r'\midrule']
for b in [3, 4]:
    rr = [r for r in s21 if r['b'] == b]
    if rr: tl.append(f"{b} & {rr[0]['forms']} & {f2(med([r['accuracy'] for r in rr]),3)} & {f2(med([r['used_features'] for r in rr]),0)} & {f2(med([r['fixed_ratio'] for r in rr]))} & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['lower_c'] for r in rr]))} & {f2(med([r['centered_upper'] for r in rr]),1)} & {f2(med([r['fixed_seconds'] / 60 for r in rr]),1)} \\\\")
tl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v15_scale_table.tex').write_text('\n'.join(tl) + '\n')
# position effects (unchanged computation)
pos = [r for r in sc if 'position' in r]
S['position'] = dict(n=len(pos), branch=med([r['position']['0.1']['bias_branch_se'] for r in pos if r['dataset'] == 'BRFSS']), fit=med([r['position']['0.1']['bias_fit_se'] for r in pos if r['dataset'] == 'BRFSS']),
                     rmse_win=sum(r['position']['0.1']['rmse_branch'] < r['position']['0.1']['rmse_fit'] for r in pos if r['dataset'] == 'BRFSS'), nb=len([r for r in pos if r['dataset'] == 'BRFSS']))

# ================================================================== pilot-learned designs
pil = [r for r in load(R / 'pilot_v15' / '*.json') if 'learned' in r]
S['pilot'] = {}
if pil:
    n1s = sorted({int(k) for r in pil for k in r['learned']})
    pt_ = [r'\begin{table}[h]', r'\centering', r'\caption{Learning the design from a pilot of the audit itself (BRFSS runs with a gain). The pilot interviews $n_1$ target respondents with the uniform design on the tree\textquotesingle s path sets; the path-set design is re-optimized at the estimated cell masses. Entries: variance of the learned design relative to the oracle path-set design at the target law, median over runs of the median over 40 pilot draws [largest 90th percentile over runs]. Cells: number of (form, pattern, label) masses to estimate. Reference: design fitted on 20,000 source records.}',
           r'\label{tab:pilot}', r'\small', r'\begin{tabular}{rrr' + 'l' * len(n1s) + 'r}', r'\toprule', r'$b$ & runs & cells & ' + ' & '.join(f'$n_1={k}$' for k in n1s) + r' & reference \\', r'\midrule']
    for b in sorted({r['b'] for r in pil}):
        rr = [r for r in pil if r['b'] == b]; cells = []
        S['pilot'][b] = dict(n=len(rr), cells=med([r['cells'] for r in rr]), ref=med([r['ps_reference'] / r['ps_oracle'] for r in rr]), pilot_design=med([r['pilot_design'] / r['ps_oracle'] for r in rr]))
        for k in n1s:
            v = [r['learned'][str(k)]['median'] / r['ps_oracle'] for r in rr if str(k) in r['learned']]; hi = [r['learned'][str(k)]['q90'] / r['ps_oracle'] for r in rr if str(k) in r['learned']]
            S['pilot'][b][k] = dict(med=med(v), max=mx(v), q90=mx(hi)); cells.append(f"{f2(med(v))} [{f2(mx(hi))}]")
        pt_.append(f"{b} & {len(rr)} & {f2(S['pilot'][b]['cells'],0)} & {' & '.join(cells)} & {f2(S['pilot'][b]['ref'])} \\\\")
    pt_ += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v15_pilot_table.tex').write_text('\n'.join(pt_) + '\n')

# ================================================================== model-based comparators on the capped records
au = load(R / 'audit_v15' / '*.json'); sh = load(R / 'shift_mi_v14' / '*.json'); iid = load(R / 'screening_mi_v13' / 'BRFSS_b*_iid.json')
names = {'iid': 'none', 'sex': 'sex', 'education': 'education', 'costbar': 'cost barrier', 'physhlth': 'poor health'}
S['em'] = {}; S['em_big'] = {}
if au:
    big = max(r['n'] for r in au); hasbig = big > 1000
    el = [r'\begin{table}[h]', r'\centering', r'\caption{A working model on the capped records: simulated BRFSS audits with $n=1000$ and $n=BIGN$ target respondents (REPS replications each). Design-based scores (branching; fitted fixed form) against maximum likelihood under a two-way log-linear model for the label and the items the rule uses, fitted by EM to the fitted-form records (EM, fitted forms) and to balanced random forms (EM, uniform forms). Bias, SD and RMSE are multiplied by 100; coverage of nominal 95\% intervals (delete-a-group jackknife for EM) has Monte Carlo standard error about MCSE. -- not computed.}',
          r'\label{tab:em}', r'\scriptsize', r'\setlength{\tabcolsep}{2.8pt}', r'\begin{tabular}{lrrlrrrrrrrr}', r'\toprule',
          r' & & & & \multicolumn{4}{c}{$n=1000$} & \multicolumn{4}{c}{$n=BIGN$} \\', r'Shift & $b$ & items & Estimator & Bias & SD & RMSE & Cov. & Bias & SD & RMSE & Cov. \\', r'\midrule']
    for key in ['iid', 'sex', 'education', 'costbar', 'physhlth']:
        for b in [4, 5]:
            rr = [r for r in au if r['shift'] == key and r['b'] == b and r['n'] == 1000]
            rb = [r for r in au if r['shift'] == key and r['b'] == b and r['n'] == big and hasbig]
            if not rr: continue
            r = rr[0]; R2 = rb[0] if rb else None; first = True
            for src, dst in [(r, S['em']), (R2, S['em_big'])]:
                if src is None: continue
                dst[f'{key}_b{b}'] = {k: dict(bias_sd=abs(src[k]['bias']) / src['branch']['sd'], bias_own=abs(src[k]['bias']) / src[k]['sd'], cov=src[k]['coverage'], rmse=src[k]['rmse'] / src['branch']['rmse'], rmse_fix=src[k]['rmse'] / src['fixed']['rmse']) for k in ['fixed', 'em_fit', 'em_unif']}
                dst[f'{key}_b{b}']['reps'] = src['reps']; dst[f'{key}_b{b}']['items'] = src['items_used']; dst[f'{key}_b{b}']['br_cov'] = src['branch']['coverage']
            for k, lab_ in [('branch', 'branching'), ('fixed', 'fitted fixed form'), ('em_fit', 'EM, fitted forms'), ('em_unif', 'EM, uniform forms')]:
                s = r[k]; s2 = R2[k] if R2 else None
                right = f"{100*s2['bias']:.2f} & {100*s2['sd']:.2f} & {100*s2['rmse']:.2f} & {s2['coverage']:.3f}" if s2 else '-- & -- & -- & --'
                el.append(f"{names[key] if first else ''} & {b if first else ''} & {r['items_used'] if first else ''} & {lab_} & {100*s['bias']:.2f} & {100*s['sd']:.2f} & {100*s['rmse']:.2f} & {s['coverage']:.3f} & {right} \\\\"); first = False
    el += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    reps = au[0]['reps']
    (M / 'v15_em_table.tex').write_text('\n'.join(el).replace('REPS', str(reps)).replace('MCSE', '%.3f' % np.sqrt(0.95 * 0.05 / reps)).replace('BIGN', '{:,}'.format(big) if hasbig else '--') + '\n')
S['shift'] = {f"{r['shift']}_b{r['b']}": dict(reg_bias_sd=abs(r['regimp']['bias']) / r['branch']['sd'], reg_cov=r['regimp']['coverage'], mi_cov=r['mi']['coverage'], fix_cov=r['fixed']['coverage'], br_cov=r['branch']['coverage'],
                                               reg_rmse=r['regimp']['rmse'] / r['branch']['rmse'], mi_rmse=r['mi']['rmse'] / r['branch']['rmse'], fix_rmse=r['fixed']['rmse'] / r['branch']['rmse'],
                                               fix_var_ratio=(r['fixed']['sd'] / r['branch']['sd']) ** 2) for r in sh}
S['shift'].update({f"iid_b{r['b']}": dict(reg_bias_sd=abs(r['regimp']['bias']) / r['branch']['sd'], reg_cov=r['regimp']['coverage'], mi_cov=r['mi']['coverage'], fix_cov=r['fixed']['coverage'], br_cov=r['branch']['coverage'],
                                           reg_rmse=r['regimp']['rmse'] / r['branch']['rmse'], mi_rmse=r['mi']['rmse'] / r['branch']['rmse'], fix_rmse=r['fixed']['rmse'] / r['branch']['rmse'],
                                           fix_var_ratio=(r['fixed']['sd'] / r['branch']['sd']) ** 2) for r in iid})

# one table for imputation from complete source records: no shift (random half) and the four pre-specified shifts
hl = [r'\begin{table}[h]', r'\centering', r'\caption{Imputation from complete source records: simulated BRFSS audits with $n=1000$ target respondents and 400 replications, for the random-half target (shift: none) and the four pre-specified shifts. The trees are those of seed 0; the first two blocks are runs R0 and S0 of Table~\ref{tab:runs}. Bias, SD and RMSE are multiplied by 100; coverage of nominal 95\% intervals has Monte Carlo standard error about 0.011. TV: total variation distance between source and target item profiles. Regression imputation: conditional mean of $t$ given the asked items and the label among the source records, naive standard error. Multiple imputation: ten proper hot-deck imputations from the same source records, Rubin\textquotesingle s rules.}', r'\label{tab:shift}', r'\scriptsize', r'\setlength{\tabcolsep}{2.6pt}',
      r'\begin{tabular}{lrrlrrrrr}', r'\toprule', r'Shift & $b$ & TV & Estimator & Bias & SD & RMSE & Coverage & Width \\', r'\midrule']
for key in ['iid', 'sex', 'education', 'costbar', 'physhlth']:
    for b in [4, 5]:
        rr = [r for r in (iid if key == 'iid' else sh) if (key == 'iid' or r['shift'] == key) and r['b'] == b]
        if not rr: continue
        r = rr[0]; first = True
        for k, lab_ in [('branch', 'branching'), ('fixed', 'fitted fixed form'), ('regimp', 'regression imputation'), ('mi', 'multiple imputation')]:
            s = r[k]; hl.append(f"{names[key] if first else ''} & {b if first else ''} & {(f2(r['tv_profiles']) if key != 'iid' else '0') if first else ''} & {lab_} & {100*s['bias']:.2f} & {100*s['sd']:.2f} & {100*s['rmse']:.2f} & {s['coverage']:.3f} & {100*s['width']:.2f} \\\\"); first = False
hl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v15_shift_table.tex').write_text('\n'.join(hl) + '\n')

# ================================================================== pointer tree
pt = load(R / 'pointer_v14' / '*.json')
if pt:
    ptl = [r'\begin{table}[h]', r'\centering', r'\caption{Round constants of the binary pointer tree $B_{b-1}$ ($m=2^b-1$). Entries are $M_r(\U)$, a lower bound on $V_r$; the brackets give the worst profile of the uniform-optimal design, an upper bound on $V_r$, when it differs. The last columns are the upper bound $2^{b-2}$ of Theorem~\ref{thm:rounds}(a) and the lower bound $2^{b-1}/(b+1)^2$ of Theorem~\ref{thm:rounds}(c) for $r=2$.}', r'\label{tab:pointer}', r'\small',
           r'\begin{tabular}{rrllllrr}', r'\toprule', r'$b$ & $m$ & fixed & $r=2$ & $r=3$ & $r=4$ & $2^{b-2}$ & $2^{b-1}/(b+1)^2$ \\', r'\midrule']
    for r in sorted(pt, key=lambda r: r['b']):
        cells = []
        for k in range(1, 5):
            if k > r['b'] - 1 and k > 1: cells.append('' if k > r['b'] else '1.000'); continue
            lo = r.get(f'M{k}'); up = r.get(f'V{k}_upper')
            cells.append((f"{lo:.3f}" + (f" [{up:.3f}]" if (up is not None and up - lo > 5e-4) else '')) if lo is not None else '--')
        ptl.append(f"{r['b']} & {r['m']} & {' & '.join(cells)} & {2 ** (r['b'] - 2)} & {2 ** (r['b'] - 1) / (r['b'] + 1) ** 2:.2f} \\\\")
    ptl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v15_pointer_table.tex').write_text('\n'.join(ptl) + '\n')
    S['pointer'] = {r['b']: {k: r.get(k) for k in ['M1', 'M2', 'M3', 'M4', 'V2_upper', 'V3_upper']} for r in pt}

# ================================================================== overall extremes and macros
runmax = max(sc + s21, key=lambda r: r['fixed_ratio'])
S['max_run'] = dict(value=runmax['fixed_ratio'], dataset=runmax['dataset'], b=runmax['b'], shift=runmax.get('shift', False), seed=runmax['seed'])
S['max_forest'] = max(S['cap'][b]['max'] for b in S['cap'])
S['max_all'] = max(S['max_run']['value'], S['max_forest'])
tworec = [x for x in allrec] + [x for x, _ in ex2]
S['two_all'] = dict(n=len(tworec), rec_min=mn(tworec))
json.dump(S, open(R / 'v15_summary.json', 'w'), indent=1, default=str)

def pctfloor(x): return str(int(np.floor(100 * x + 1e-9)))
sb = S['screen']; bsg = [b for b in (4, 5, 6) if b in sb]
N['nMaxAll'] = f2(S['max_all']); N['nMaxForest'] = f2(S['max_forest']); N['nMaxScreen'] = f2(S['max_run']['value'])
N['nUnifLo'] = f2(mn([sb[b]['unif_min'] for b in bsg]), 0); N['nUnifHi'] = f2(mx([sb[b]['unif_max'] for b in bsg]), 0)
N['nUnifHtLo'] = f2(mn([sb[b]['unifht_min'] for b in bsg]), 0); N['nUnifHtHi'] = f2(mx([sb[b]['unifht_max'] for b in bsg]), 0)
N['nTwoMinPct'] = pctfloor(S['two_all']['rec_min']) if np.isfinite(S['two_all']['rec_min']) else '--'
N['nTwoForestLo'] = pctfloor(S['forest_two']['rec_min']) if fr else '--'; N['nTwoForestHi'] = f2(100 * S['forest_two']['rec_max'], 0) if fr else '--'
N['nTwoForestMed'] = f2(100 * S['forest_two']['rec_med'], 0) if fr else '--'; N['nTwoForestN'] = str(S['forest_two']['n']); N['nTwoForestRatioMax'] = f2(S['forest_two']['ratio_max'])
N['nTwoForestRatioMed'] = f2(S['forest_two']['ratio_med'])
for b in S['cap']:
    w = {2: 'Two', 3: 'Three', 4: 'Four'}[b]; s = S['cap'][b]
    N[f'nCap{w}Med'] = f2(s['med']); N[f'nCap{w}Max'] = f2(s['max']); N[f'nCap{w}Min'] = f2(s['min']); N[f'nCap{w}N'] = str(s['n'])
    N[f'nCap{w}Fix'] = f2(s['capfix'], 1); N[f'nCap{w}Br'] = f2(s['capbr'], 1); N[f'nCap{w}Share'] = f2(100 * s['share'], 0)
N['nCapThreeMsix'] = f2(S['cap'][3]['m6']); N['nCapThreeMtwelve'] = f2(S['cap'][3]['m12'])
N['nCapFixLo'] = f2(mn([S['cap'][b]['capfix'] for b in S['cap']]), 1); N['nCapFixHi'] = f2(mx([S['cap'][b]['capfix'] for b in S['cap']]), 1)
N['nCapBrLo'] = f2(mn([S['cap'][b]['capbr'] for b in S['cap']]), 1); N['nCapBrHi'] = f2(mx([S['cap'][b]['capbr'] for b in S['cap']]), 1)
N['nForestFitDev'] = f2(100 * mx([S['cap'][b]['fitdev'] for b in S['cap']]), 0)
N['nScreenBestLo'] = f2(mn([sb[b]['best'] for b in bsg])); N['nScreenBestHi'] = f2(mx([sb[b]['best'] for b in bsg]))
N['nScreenRunLo'] = f2(mn([sb[b]['min'] for b in bsg])); N['nScreenRunHi'] = f2(mx([sb[b]['max'] for b in bsg]))
N['nScreenTwoN'] = str(S['screen_two']['n']); N['nScreenGainN'] = str(S['screen_two']['ngain']); N['nScreenTwoMax'] = f2(S['screen_two']['ratio_max'], 3)
N['nScreenTwoFitMax'] = f2(S['screen_two']['fit_max']); N['nScreenTwoFitMed'] = f2(S['screen_two']['fit_med']); N['nScreenTwoFitN'] = str(S['screen_two']['nfit'])
N['nSixTwoN'] = str(n6); N['nSixAll'] = str(n6all)
N['nLabelMax'] = f2(100 * S['label']['drop_max'], 1); N['nLabelN'] = str(S['label']['n']); N['nStratMax'] = f2(100 * S['label']['strat_drop_max'], 1); N['nStratN'] = str(S['label']['strat_n'])
N['nPsGapMed'] = f2(100 * S['ps_gap']['med'], 1); N['nPsGapMax'] = f2(100 * S['ps_gap']['max'], 1); N['nPsGapN'] = str(S['ps_gap']['n']); N['nNpOver'] = f2(S['ps_gap']['np_over'], 1); N['nLowUnder'] = f2(S['ps_gap']['low_under'])
N['nFitMed'] = f2(100 * S['fit']['med'], 0); N['nFitMax'] = f2(100 * S['fit']['max'], 0)
N['nHeurLo'] = f2(100 * mn([sb[b]['fracheur'] for b in bsg]), 0); N['nHeurHi'] = f2(100 * mx([sb[b]['fracheur'] for b in bsg]), 0)
if 'scale' in S and 4 in S['scale']:
    N['nScaleBest'] = f2(S['scale'][4]['best']); N['nScaleMax'] = f2(S['scale'][4]['max']); N['nScaleFit'] = f2(S['scale'][4]['fit']); N['nScalePs'] = f2(S['scale'][4]['ps']); N['nScaleMin'] = f2(S['scale'][4]['mins'], 0)
N['nPosBranch'] = f2(S['position']['branch']); N['nPosFit'] = f2(S['position']['fit']); N['nPosWin'] = str(S['position']['rmse_win']); N['nPosN'] = str(S['position']['nb'])
for b in S['pilot']:
    w = {4: 'Four', 5: 'Five', 6: 'Six'}[b]
    for k in (250, 500, 1000, 2000, 4000):
        if k in S['pilot'][b]: N[f'nPilot{w}N{ {250: "a", 500: "b", 1000: "c", 2000: "d", 4000: "e"}[k] }'] = f2(100 * (S['pilot'][b][k]['med'] - 1), 0)
    N[f'nPilot{w}Ref'] = f2(100 * (S['pilot'][b]['ref'] - 1), 0); N[f'nPilot{w}Cells'] = f2(S['pilot'][b]['cells'], 0)
if S['em']:
    E_ = S['em']; ks = sorted(E_)
    N['nEmReps'] = str(E_[ks[0]]['reps'])
    N['nEmRmseLo'] = f2(mn([E_[k]['em_fit']['rmse_fix'] for k in ks])); N['nEmRmseHi'] = f2(mx([E_[k]['em_fit']['rmse_fix'] for k in ks]))
    N['nEmBrLo'] = f2(mn([E_[k]['em_fit']['rmse'] for k in ks])); N['nEmBrHi'] = f2(mx([E_[k]['em_fit']['rmse'] for k in ks]))
    N['nEmCovLo'] = f2(mn([E_[k]['em_fit']['cov'] for k in ks]), 3); N['nEmCovHi'] = f2(mx([E_[k]['em_fit']['cov'] for k in ks]), 3)
    N['nEmBiasHi'] = f2(mx([E_[k]['em_fit']['bias_sd'] for k in ks])); N['nEmBiasLo'] = f2(mn([E_[k]['em_fit']['bias_sd'] for k in ks]))
    N['nEmUnifLo'] = f2(mn([E_[k]['em_unif']['rmse_fix'] for k in ks])); N['nEmUnifHi'] = f2(mx([E_[k]['em_unif']['rmse_fix'] for k in ks]))
    B_ = S['em_big']; kb = sorted(B_)
    if kb:
        N['nEmBigN'] = '{:,}'.format(max(r['n'] for r in au)); N['nEmBigSettings'] = str(len(kb))
        N['nEmBigCovLo'] = f2(mn([B_[k]['em_fit']['cov'] for k in kb]), 3); N['nEmBigCovHi'] = f2(mx([B_[k]['em_fit']['cov'] for k in kb]), 3)
        N['nEmBigBelow'] = str(sum(1 for k in kb if B_[k]['em_fit']['cov'] < 0.90))
        N['nEmBigRmseLo'] = f2(mn([B_[k]['em_fit']['rmse'] for k in kb])); N['nEmBigRmseHi'] = f2(mx([B_[k]['em_fit']['rmse'] for k in kb]))
        N['nEmBigWorse'] = str(sum(1 for k in kb if B_[k]['em_fit']['rmse_fix'] > 1.0)); N['nEmBigWorseBr'] = str(sum(1 for k in kb if B_[k]['em_fit']['rmse'] > 1.0))
        N['nEmBigBiasHi'] = f2(mx([B_[k]['em_fit']['bias_own'] for k in kb]))
        N['nEmBigFixCovLo'] = f2(mn([min(B_[k]['fixed']['cov'], B_[k]['br_cov']) for k in kb]), 3); N['nEmBigFixCovHi'] = f2(mx([max(B_[k]['fixed']['cov'], B_[k]['br_cov']) for k in kb]), 3)
        N['nEmBigUnifCovLo'] = f2(mn([B_[k]['em_unif']['cov'] for k in kb]), 3)
    N['nEmSettings'] = str(len(ks)); N['nEmBelow'] = str(sum(1 for k in ks if E_[k]['em_fit']['cov'] < 0.925))
    N['nEmUnifCovLo'] = f2(mn([E_[k]['em_unif']['cov'] for k in ks]), 3); N['nEmUnifCovHi'] = f2(mx([E_[k]['em_unif']['cov'] for k in ks]), 3)
    N['nEmFixCovLo'] = f2(mn([E_[k]['fixed']['cov'] for k in ks]), 3); N['nEmFixCovHi'] = f2(mx([E_[k]['fixed']['cov'] for k in ks]), 3)
sh_ = S['shift']; good = [v for k, v in sh_.items() if k.startswith('iid') or k.startswith('sex')]
N['nImpRmseLo'] = f2(mn([min(v['reg_rmse'], v['mi_rmse']) for v in good])); N['nImpRmseHi'] = f2(mx([max(v['reg_rmse'], v['mi_rmse']) for v in good]))
N['nImpGoodCovLo'] = f2(mn([min(v['reg_cov'], v['mi_cov']) for v in good]), 3); N['nImpGoodCovHi'] = f2(mx([max(v['reg_cov'], v['mi_cov']) for v in good]), 3)
bad = [v for k, v in sh_.items() if (v['reg_cov'] < 0.925 or v['reg_bias_sd'] > 0.5) and not (k.startswith('iid') or k.startswith('sex'))]
N['nImpBadN'] = str(len(bad)); N['nImpBiasHi'] = f2(mx([v['reg_bias_sd'] for v in bad])); N['nImpCovLo'] = f2(mn([v['reg_cov'] for v in bad]), 3); N['nImpCovHi'] = f2(mx([v['reg_cov'] for v in bad]), 3)
N['nMiCovLo'] = f2(mn([v['mi_cov'] for v in bad]), 3); N['nMiCovHi'] = f2(mx([v['mi_cov'] for v in bad]), 3)
N['nDesCovLo'] = f2(mn([min(v['br_cov'], v['fix_cov']) for v in sh_.values()]), 3); N['nDesCovHi'] = f2(mx([max(v['br_cov'], v['fix_cov']) for v in sh_.values()]), 3)
# sample sizes for a 95% interval of half-width two accuracy points (0.04 on the contrast scale), BRFSS b = 5 medians
b5 = [r for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 5]
nb = (1.96 / 0.04) ** 2 * med([r['full_var'] for r in b5])
def rnd(x): return '{:,}'.format(int(round(x / 100.0) * 100))
N['nSsBranch'] = rnd(nb); N['nSsFixed'] = rnd(nb * med([r['fixed_ratio'] for r in b5])); N['nSsFit'] = rnd(nb * med([r['fixed_fit_ratio'] for r in b5]))
N['nSsUnif'] = rnd(nb * med([r.get('uniform_opt_ratio') for r in b5])) if fin([r.get('uniform_opt_ratio') for r in b5]) else '--'
N['nForestGapMax'] = ('%.0e' % S['forest_two']['gap_max']) if fr else '--'
N['nForestOverlapN'] = str(S['forest_engine_overlap']['n']); N['nForestOverlapMax'] = f2(100 * S['forest_engine_overlap']['max_rel'], 1) if ov else '--'
N['nForestOverlapAgree'] = str(S['forest_engine_overlap']['agree']); N['nForestOverlapRest'] = str(S['forest_engine_overlap']['n'] - S['forest_engine_overlap']['agree'])
N['nThreeForestMed'] = f2(100 * S['forest_round3_b4']['rec'], 0) if 'forest_round3_b4' in S else '--'
N['nLabelCert'] = '%.0e' % max(S['label']['cert_gap'], 1e-12)
N['nScaleSame'] = str(S.get('scale_same_tree_b4', '--'))
N['nCompAgree'] = str(S['screen_two']['comp_agree']); N['nCompBrfss'] = str(S['screen_two']['computable']); N['nBrfssRuns'] = str(S['screen_two']['nbrfss']); N['nTwoBounded'] = str(S['screen_two']['bounded'])
N['nScreenTwoRecMin'] = pctfloor(S['screen_two']['rec_min'])
N['nTwoBoundMax'] = f2(S['screen_two']['bounded_ratio_max']); N['nTwoBoundMin'] = f2(S['screen_two']['bounded_ratio_min']); N['nTwoBoundRec'] = pctfloor(S['screen_two']['bounded_rec_min']) if bd2 else '--'
N['nSixExact'] = str(sum(1 for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 6 and r['two_computed'] and not r.get('two_bounded')))
out = ['% generated by Research/code/v15_tables.py from Research/results; do not edit']
for k, v in N.items(): out.append('\\newcommand{\\%s}{%s}' % (k, v))
(M / 'v15_numbers.tex').write_text('\n'.join(out) + '\n')
json.dump(dict(summary=S, macros=N), open(R / 'v15_summary.json', 'w'), indent=1, default=str)
print(json.dumps(N, indent=0))
