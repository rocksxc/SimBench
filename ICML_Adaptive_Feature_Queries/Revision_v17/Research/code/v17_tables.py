"""Generate the v17 tables (LaTeX), the summary results/v17_summary.json and the number macros Manuscript/v17_numbers.tex.
Every number quoted in the v17 text is one of these macros or sits in one of these tables. Robust to partial results."""
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
(M / 'v17_capgrid_table.tex').write_text(txt + '\n')
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
(M / 'v17_capgrid_detail.tex').write_text('\n'.join(det) + '\n')
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
base16 = {(r['dataset'], r['b'], r['shift'], r['seed']): r for r in load(R / 'baselines_v16' / '*.json')}
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
    bz = base16.get((r['dataset'], r['b'], r['shift'], r['seed']))
    if bz:
        assert abs(bz['delta'] - r['delta']) < 1e-9 and abs(bz['ps_oracle'] - r['ps_ratio']) < 1e-4 * max(1, r['ps_ratio'])
        r['uniform_ps'] = bz['uniform_ps']; r['uniform_items'] = bz['uniform_items']; r['item_forms'] = bz['item_forms']; r['pilot16'] = bz.get('pilot')
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
head = (r'Data, $b$ & runs & Best & [min, max] & Fitted & Label & Two & Two fit. & U-paths & U-items & U-all & $1/\rho_P^2$ & $N_P$ \\')
ml = [r'\begin{table}[h]', r'\centering',
      r'\caption{Screening trees on twelve items, all designs without a model: records needed relative to branching, which asks the tree\textquotesingle s own questions and attains the full-information variance (medians over two targets and three seeds; the range is over runs). Best: optimal fixed design over all forms at the target law. Fitted: the same program on source records, evaluated at the target. Label: optimal fixed design whose form probabilities may depend on the label. Two: exact optimal two-round design (TWOSIXNOTE). Two fit.: two-round design fitted on source records. Naive pre-committed designs with the best scores for each: U-paths, uniform over the tree\textquotesingle s question paths; U-items, uniform over all $b$-subsets of the items the rule depends on; U-all, uniform over all $\binom{12}b$ forms. $1/\rho_P^2$, $N_P$: the ends of Theorem~\ref{thm:bracket}. -- not computed.}',
      r'\label{tab:screeningfull}', r'\footnotesize', r'\setlength{\tabcolsep}{4.6pt}', r'\begin{tabular}{lrrlrrrrrrrrr}', r'\toprule', head, r'\midrule']
def mrow(lab, rr, full=True):
    two = [r['two'] for r in rr if r.get('two_computed')]
    return (f"{lab} & {len(rr)} & {f2(med([r['fixed_ratio'] for r in rr]))} & [{f2(mn([r['fixed_ratio'] for r in rr]))}, {f2(mx([r['fixed_ratio'] for r in rr]))}] & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & "
            f"{f2(med([r.get('label_fixed_ratio') for r in rr]))} & {(('$\\le$' if any(r.get('two_bounded') for r in rr) else '') + f2(med(two))) if len(two) == len(rr) else '--'} & {f2(med([r.get('round2_fit_ratio') for r in rr]))} & "
            f"{f2(med([r.get('uniform_ps') for r in rr]))} & {f2(med([r.get('uniform_items') for r in rr]))} & {f2(med([r.get('uniform_opt_ratio') for r in rr]),1)} & "
            f"{f2(med([r['lower_c'] for r in rr]))} & {f2(med([r.get('centered_upper') for r in rr]),1)} \\\\")
S['screen'] = {}
for b in [3, 4, 5, 6]:
    rr = grp('BRFSS', b)
    if not rr: continue
    ml.append(mrow(f'BRFSS, {b}', rr))
    gain = [r for r in rr if r['fixed_ratio'] > 1.01]
    S['screen'][b] = dict(n=len(rr), ngain=len(gain), best=med([r['fixed_ratio'] for r in rr]), min=mn([r['fixed_ratio'] for r in rr]), max=mx([r['fixed_ratio'] for r in rr]),
                          fit=med([r['fixed_fit_ratio'] for r in rr]), label=med([r.get('label_fixed_ratio') for r in rr]),
                          unif=med([r.get('uniform_opt_ratio') for r in rr]), unif_min=mn([r.get('uniform_opt_ratio') for r in rr]), unif_max=mx([r.get('uniform_opt_ratio') for r in rr]),
                          unifht_min=mn([r.get('uniform_ht_ratio') for r in rr]), unifht_max=mx([r.get('uniform_ht_ratio') for r in rr]),
                          ups_min=mn([r.get('uniform_ps') for r in rr]), ups_max=mx([r.get('uniform_ps') for r in rr]), uit_min=mn([r.get('uniform_items') for r in rr]), uit_max=mx([r.get('uniform_items') for r in rr]),
                          ups_over=med([r['uniform_ps'] / r['fixed_ratio'] - 1 for r in gain if r.get('uniform_ps')]), ups_over_max=mx([r['uniform_ps'] / r['fixed_ratio'] - 1 for r in gain if r.get('uniform_ps')]),
                          uit_over=med([r['uniform_items'] / r['fixed_ratio'] - 1 for r in gain if r.get('uniform_items')]), uit_over_max=mx([r['uniform_items'] / r['fixed_ratio'] - 1 for r in gain if r.get('uniform_items')]),
                          lower=med([r['lower_c'] for r in rr]), ps=med([r['ps_ratio'] for r in rr]), upper=med([r.get('centered_upper') for r in rr]),
                          heur=med([r.get('heur2_ratio') for r in rr]), fracheur=med([frac(r, 'heur2_ratio') for r in rr]))
rr = grp('Thyroid', None)
if rr: ml.append(mrow('Thyroid, 3--6', rr)); S['thyroid'] = dict(n=len(rr), maxfixed=mx([r['fixed_ratio'] for r in rr]), unif=med([r.get('uniform_opt_ratio') for r in rr]))
if s21:
    S['scale'] = {b: dict(n=len([r for r in s21 if r['b'] == b]), best=med([r['fixed_ratio'] for r in s21 if r['b'] == b]), max=mx([r['fixed_ratio'] for r in s21 if r['b'] == b]),
                         fit=med([r['fixed_fit_ratio'] for r in s21 if r['b'] == b]), ps=med([r['ps_ratio'] for r in s21 if r['b'] == b]),
                         mins=med([r['fixed_seconds'] / 60 for r in s21 if r['b'] == b])) for b in [3, 4]}
ml += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
n6 = sum(1 for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 6 and r['two_computed'])
n6all = sum(1 for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 6)
nb6 = sum(1 for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 6 and r.get('two_bounded'))
note = ('at $b=6$ for ' + str(n6) + ' of the ' + str(n6all) + ' runs') if n6 < n6all else (('at $b=6$ the median includes certified upper bounds from feasible two-round designs for ' + str(nb6) + ' runs, Table~\\ref{tab:runs}') if nb6 else 'all runs')
(M / 'v17_screening_full.tex').write_text('\n'.join(ml).replace('TWOSIXNOTE', note) + '\n')
S['n6_two'] = n6; S['n6_all'] = n6all
# two-round recovery over all BRFSS runs with a gain and a computed two-round optimum
br_gain = [r for r in sc if r['dataset'] == 'BRFSS' and r['fixed_ratio'] > 1.01]
for r in br_gain: r['two_frac'] = float(np.log(r['fixed_ratio'] / max(r['two'], 1.0)) / np.log(r['fixed_ratio'])) if r['two_computed'] else None
fr2 = [(r['two_frac'], r) for r in br_gain if r['two_computed']]
ex2 = [(x, r) for x, r in fr2 if not r.get('two_bounded')]; bd2 = [(x, r) for x, r in fr2 if r.get('two_bounded')]
S['screen_two'] = dict(n=len(ex2), ngain=len(br_gain), rec_min=mn([x for x, _ in ex2]), ratio_max=mx([r['two'] for _, r in ex2]), bounded_rec_min=mn([x for x, _ in bd2]), bounded_ratio_max=mx([r['two'] for _, r in bd2]), bounded_ratio_min=mn([r['two'] for _, r in bd2]), computable=sum(1 for r in sc if r['dataset'] == 'BRFSS' and r.get('computable')), nbrfss=sum(1 for r in sc if r['dataset'] == 'BRFSS'), comp_agree=comp_agree, bounded=sum(1 for _, r in fr2 if r.get('two_bounded')), bounded_gap=mx([r['two'] - r['two_lower'] for _, r in fr2 if r.get('two_bounded')]),
                       fit_max=mx([r.get('round2_fit_ratio') for r in br_gain]), nfit=len(fin([r.get('round2_fit_ratio') for r in br_gain])),
                       fit_med=med([r.get('round2_fit_ratio') for r in br_gain]))
gains_all = [r for r in sc if r['fixed_ratio'] > 1.01]  # the 21-item trees coincide with runs R0-R2 and are not counted again
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
dl = [r'\begin{table}[h]', r'\centering', r'\caption{All screening settings (medians over three seeds). Ratios are records needed relative to branching. Best/Fitted: optimal and fitted fixed designs; Label, Strat.: optimal fixed designs whose form probabilities depend on the label, and on the label and sex; PS: optimized path-set design (oracle/fitted); H2: heuristic two-round design; $r{=}2,3$: exact optimal $r$-round designs; 2 fit.: fitted two-round design; U-p, U-i: uniform designs over the tree\textquotesingle s path sets and over the $b$-subsets of the items the rule depends on, with optimal scores; U-HT, U-opt: uniform design over all forms with monomial Horvitz--Thompson scores and with optimal scores; $1/\rho_P^2$, $N_P$: ends of Theorem~\ref{thm:bracket}.}', r'\label{tab:screeningdetail}',
      r'\scriptsize', r'\setlength{\tabcolsep}{1.7pt}', r'\begin{tabular}{lllrrrrrrrrrrrrrrrrrr}', r'\toprule',
      r'Data & $b$ & Target & Acc. & Paths & Best & Fitted & Label & Strat. & PS & PS fit & H2 & $r{=}2$ & $r{=}3$ & 2 fit. & U-p & U-i & U-HT & U-opt & $1/\rho_P^2$ & $N_P$ \\', r'\midrule']
for ds in ['BRFSS', 'Thyroid']:
    for b in [3, 4, 5, 6]:
        for sh in [False, True]:
            rr = [r for r in sc if r['dataset'] == ds and r['b'] == b and r['shift'] == sh]
            if not rr: continue
            two = [r['two'] for r in rr if r['two_computed']]
            dl.append(f"{ds} & {b} & {'other sex' if sh else 'random half'} & {f2(med([r['accuracy'] for r in rr]),3)} & {f2(med([r['path_sets'] for r in rr]),0)} & {f2(med([r['fixed_ratio'] for r in rr]))} & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med([r.get('label_fixed_ratio') for r in rr]))} & {f2(med([r.get('strat_fixed_ratio') for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['ps_fit_ratio'] for r in rr]))} & {f2(med([r.get('heur2_ratio') for r in rr]))} & {f2(med(two)) if two else '--'} & {f2(med([r.get('round3_ratio') for r in rr]) if b > 3 else float('nan'))} & {f2(med([r.get('round2_fit_ratio') for r in rr]))} & {f2(med([r.get('uniform_ps') for r in rr]))} & {f2(med([r.get('uniform_items') for r in rr]))} & {f2(med([r.get('uniform_ht_ratio') for r in rr]),1)} & {f2(med([r.get('uniform_opt_ratio') for r in rr]),1)} & {f2(med([r['lower_c'] for r in rr]))} & {f2(med([r.get('centered_upper') for r in rr]),1)} \\\\")
dl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v17_screening_detail.tex').write_text('\n'.join(dl) + '\n')
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
(M / 'v17_runs_table.tex').write_text('\n'.join(rl) + '\n')
# 21-item table (appendix)
same21 = sum(1 for r in s21 if any(q['dataset'] == 'BRFSS' and q['b'] == r['b'] and not q['shift'] and q['seed'] == r['seed'] and abs(q['fixed_ratio'] - r['fixed_ratio']) < 1e-3 and abs(q['accuracy'] - r['accuracy']) < 1e-9 for q in sc) and r['b'] == 4)
S['scale_same_tree_b4'] = same21
tl = [r'\begin{table}[h]', r'\centering', r'\caption{All 21 BRFSS variables (random-half target; medians over three seeds). Forms: $\binom{21}b$. Time: median minutes for the certified fixed design on one core.}', r'\label{tab:scale}', r'\small',
      r'\begin{tabular}{rrrrrrrrrr}', r'\toprule', r'$b$ & forms & Acc. & items used & Best & Fitted & PS & $1/\rho_P^2$ & $N_P$ & time \\', r'\midrule']
for b in [3, 4]:
    rr = [r for r in s21 if r['b'] == b]
    if rr: tl.append(f"{b} & {rr[0]['forms']} & {f2(med([r['accuracy'] for r in rr]),3)} & {f2(med([r['used_features'] for r in rr]),0)} & {f2(med([r['fixed_ratio'] for r in rr]))} & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med([r['ps_ratio'] for r in rr]))} & {f2(med([r['lower_c'] for r in rr]))} & {f2(med([r['centered_upper'] for r in rr]),1)} & {f2(med([r['fixed_seconds'] / 60 for r in rr]),1)} \\\\")
tl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
(M / 'v17_scale_table.tex').write_text('\n'.join(tl) + '\n')
# position effects (unchanged computation)
pos = [r for r in sc if 'position' in r]
S['position'] = dict(n=len(pos), branch=med([r['position']['0.1']['bias_branch_se'] for r in pos if r['dataset'] == 'BRFSS']), fit=med([r['position']['0.1']['bias_fit_se'] for r in pos if r['dataset'] == 'BRFSS']),
                     rmse_win=sum(r['position']['0.1']['rmse_branch'] < r['position']['0.1']['rmse_fit'] for r in pos if r['dataset'] == 'BRFSS'), nb=len([r for r in pos if r['dataset'] == 'BRFSS']))

# ================================================================== pilot-learned designs, all-in accounting (baselines_v16)
pil = [r for r in sc if r.get('pilot16')]
S['pilot'] = {}
if pil:
    n1s = sorted({int(k) for r in pil for k in r['pilot16']})
    pt_ = [r'\begin{table}[h]', r'\centering', r'\caption{Learning the design from a pilot of the audit itself, with the pilot charged (BRFSS runs with a gain; medians over runs of the median over 30 pilots). Pilot: per-record variance of the cross-fitted scores of the $n_1$ pilot respondents (uniform design on the path sets). Learned: per-record variance of the path-set design learned from the pilot. All-in: variance of the estimator that uses all $N=4n_1$ records with weights proportional to sample sizes, $[n_1\cdot\text{pilot}+3n_1\cdot\text{learned}]/N$. All entries are relative to branching; the last columns give the oracle path-set design and the oracle design over all forms. Cells: number of (form, pattern, label) masses to estimate.}',
           r'\label{tab:pilot}', r'\small', r'\begin{tabular}{rrrrrrrrr}', r'\toprule', r'$b$ & runs & cells & $n_1$ & pilot & learned & all-in & oracle PS & oracle all forms \\', r'\midrule']
    for b in sorted({r['b'] for r in pil}):
        rr = [r for r in pil if r['b'] == b]; S['pilot'][b] = dict(n=len(rr), cells=med([2 * r['path_sets'] * (1 << b) for r in rr]), ps=med([r['ps_ratio'] for r in rr]), best=med([r['fixed_ratio'] for r in rr]))
        for i, k in enumerate(n1s):
            cf = med([r['pilot16'][str(k)]['pilot_cf'] for r in rr]); ln = med([r['pilot16'][str(k)]['learned'] for r in rr])
            allin = med([0.25 * r['pilot16'][str(k)]['pilot_cf'] + 0.75 * r['pilot16'][str(k)]['learned'] for r in rr])
            over = med([(0.25 * r['pilot16'][str(k)]['pilot_cf'] + 0.75 * r['pilot16'][str(k)]['learned']) / r['fixed_ratio'] - 1 for r in rr])
            S['pilot'][b][k] = dict(cf=cf, learned=ln, allin=allin, over=over)
            pt_.append(f"{b if i == 0 else ''} & {len(rr) if i == 0 else ''} & {f2(S['pilot'][b]['cells'],0) if i == 0 else ''} & {k} & {f2(cf)} & {f2(ln)} & {f2(allin)} & {f2(S['pilot'][b]['ps']) if i == 0 else ''} & {f2(S['pilot'][b]['best']) if i == 0 else ''} \\\\")
    pt_ += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v17_pilot_table.tex').write_text('\n'.join(pt_) + '\n')

# ================================================================== reuse and joint designs (reuse_v16)
ru = load(R / 'reuse_v16' / '*.json'); S['reuse'] = {}
if ru:
    rl2 = [r'\begin{table}[h]', r'\centering', r'\caption{Using one set of records for several rules (BRFSS, other-sex target; the three trees of seeds 0--2 at each cap are rules A, B, C). Entries are records needed relative to branching for that rule alone. Own: the rule\textquotesingle s own optimal fixed design. Reuse: best scores for the rule on records collected under another rule\textquotesingle s optimal design mixed with a 5\% uniform floor (minimum and maximum over the two other designs). Joint: the fixed design that minimizes the sum of the records ratios of the rules in the group.}',
           r'\label{tab:reuse}', r'\small', r'\begin{tabular}{rlrrrrrrr}', r'\toprule', r'$b$ & Rule & Own & Reuse min & Reuse max & Joint A,B & Joint A,C & Joint B,C & Joint A,B,C \\', r'\midrule']
    for r in sorted(ru, key=lambda r: r['b']):
        b = r['b']; pen = []; reuse_all = list(r['reuse'].values())
        for j, nm in enumerate('ABC'):
            rs = [r['reuse'][f'{i}->{j}'] for i in range(3) if i != j]
            cells = []
            for pair in ['0,1', '0,2', '1,2']:
                ids = [int(x) for x in pair.split(',')]
                cells.append(f2(r['joint'][pair][ids.index(j)]) if j in ids else '')
            trip = r['joint']['0,1,2'][j]; pen.append(trip / r['own'][j] - 1)
            rl2.append(f"{b if j == 0 else ''} & {nm} & {f2(r['own'][j])} & {f2(min(rs), 1 if min(rs) >= 10 else 2)} & {f2(max(rs), 1 if max(rs) >= 10 else 2)} & {' & '.join(cells)} & {f2(trip)} \\\\")
        pairpen = [r['joint'][pair][k_] / r['own'][int(pair.split(',')[k_])] - 1 for pair in ['0,1', '0,2', '1,2'] for k_ in range(2)]
        S['reuse'][b] = dict(own=r['own'], reuse_min=min(reuse_all), reuse_max=max(reuse_all), reuse_med=med(reuse_all), reuse_pen_med=med([r['reuse'][f'{i}->{j}'] / r['own'][j] for i in range(3) for j in range(3) if i != j]),
                             triple=r['joint']['0,1,2'], triple_pen_max=max(pen), triple_pen_med=med(pen), triple_sum=sum(r['joint']['0,1,2']), pair_pen_max=max(pairpen), pair_pen_med=med(pairpen),
                             pair_sum_max=max(sum(r['joint'][pair]) for pair in ['0,1', '0,2', '1,2']))
    rl2 += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v17_reuse_table.tex').write_text('\n'.join(rl2) + '\n')

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
    (M / 'v17_em_table.tex').write_text('\n'.join(el).replace('REPS', str(reps)).replace('MCSE', '%.3f' % np.sqrt(0.95 * 0.05 / reps)).replace('BIGN', '{:,}'.format(big) if hasbig else '--') + '\n')
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
(M / 'v17_shift_table.tex').write_text('\n'.join(hl) + '\n')

# ================================================================== pointer tree
pt = load(R / 'pointer_v14' / '*.json')
if pt:
    ptl = [r'\begin{table}[h]', r'\centering', r'\caption{Round constants of the binary pointer tree $B_{b-1}$ ($m=2^b-1$). Entries are $M_r(\U)$, a lower bound on $V_r$; the brackets give the worst profile of the uniform-optimal design, an upper bound on $V_r$, when it differs. The last columns are the upper bound $2^{b-2}$ of Theorem~\ref{thm:rounds}(a) and the lower bound $2^{b-1}/(b+1)^2$ of Theorem~\ref{thm:rounds}(b) for $r=2$.}', r'\label{tab:pointer}', r'\small',
           r'\begin{tabular}{rrllllrr}', r'\toprule', r'$b$ & $m$ & fixed & $r=2$ & $r=3$ & $r=4$ & $2^{b-2}$ & $2^{b-1}/(b+1)^2$ \\', r'\midrule']
    for r in sorted(pt, key=lambda r: r['b']):
        cells = []
        for k in range(1, 5):
            if k > r['b'] - 1 and k > 1: cells.append('' if k > r['b'] else '1.000'); continue
            lo = r.get(f'M{k}'); up = r.get(f'V{k}_upper')
            cells.append((f"{lo:.3f}" + (f" [{up:.3f}]" if (up is not None and up - lo > 5e-4) else '')) if lo is not None else '--')
        ptl.append(f"{r['b']} & {r['m']} & {' & '.join(cells)} & {2 ** (r['b'] - 2)} & {2 ** (r['b'] - 1) / (r['b'] + 1) ** 2:.2f} \\\\")
    ptl += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v17_pointer_table.tex').write_text('\n'.join(ptl) + '\n')
    S['pointer'] = {r['b']: {k: r.get(k) for k in ['M1', 'M2', 'M3', 'M4', 'V2_upper', 'V3_upper']} for r in pt}

# ================================================================== overall extremes and macros
runmax = max(sc, key=lambda r: r['fixed_ratio'])
S['max_run'] = dict(value=runmax['fixed_ratio'], dataset=runmax['dataset'], b=runmax['b'], shift=runmax.get('shift', False), seed=runmax['seed'])
S['max_forest'] = max(S['cap'][b]['max'] for b in S['cap'])
S['max_all'] = max(S['max_run']['value'], S['max_forest'])
tworec = [x for x in allrec] + [x for x, _ in ex2]
S['two_all'] = dict(n=len(tworec), rec_min=mn(tworec))
json.dump(S, open(R / 'v17_summary.json', 'w'), indent=1, default=str)

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
    w = {3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six'}[b]
    for k, tag in ((500, 'b'), (1000, 'c'), (2000, 'd')):
        if k in S['pilot'][b]:
            N[f'nAllIn{w}{tag}'] = f2(S['pilot'][b][k]['allin']); N[f'nAllInOver{w}{tag}'] = f2(100 * S['pilot'][b][k]['over'], 0); N[f'nLearn{w}{tag}'] = f2(S['pilot'][b][k]['learned'])
    N[f'nPilot{w}Cells'] = f2(S['pilot'][b]['cells'], 0); N[f'nPilot{w}Best'] = f2(S['pilot'][b]['best'])
ups = [r for r in sc if r['dataset'] == 'BRFSS' and r['b'] >= 4 and r.get('uniform_ps')]
N['nUpsLo'] = f2(mn([r['uniform_ps'] for r in ups])); N['nUpsHi'] = f2(mx([r['uniform_ps'] for r in ups])); N['nUitLo'] = f2(mn([r['uniform_items'] for r in ups])); N['nUitHi'] = f2(mx([r['uniform_items'] for r in ups]))
upg = [r for r in ups if r['fixed_ratio'] > 1.01]
N['nUpsOverMed'] = f2(100 * med([r['uniform_ps'] / r['fixed_ratio'] - 1 for r in upg]), 0); N['nUpsOverMax'] = f2(100 * mx([r['uniform_ps'] / r['fixed_ratio'] - 1 for r in upg]), 0)
N['nUitOverMed'] = f2(100 * med([r['uniform_items'] / r['fixed_ratio'] - 1 for r in upg]), 0); N['nUitOverMax'] = f2(100 * mx([r['uniform_items'] / r['fixed_ratio'] - 1 for r in upg]), 0)
if S.get('reuse'):
    R_ = S['reuse']
    N['nReuseMin'] = f2(mn([R_[b]['reuse_min'] for b in R_])); N['nReuseMax'] = f2(mx([R_[b]['reuse_max'] for b in R_]), 0); N['nReusePenMed'] = f2(med([R_[b]['reuse_pen_med'] for b in R_]), 1)
    N['nJointPenMed'] = f2(100 * med([R_[b]['triple_pen_med'] for b in R_]), 0); N['nJointPenMax'] = f2(100 * mx([R_[b]['triple_pen_max'] for b in R_]), 0)
    N['nJointSumLo'] = f2(mn([R_[b]['triple_sum'] for b in R_]), 1); N['nJointSumHi'] = f2(mx([R_[b]['triple_sum'] for b in R_]), 1)
    N['nJointPairPenMax'] = f2(100 * mx([R_[b]['pair_pen_max'] for b in R_]), 0); N['nJointPairSumMax'] = f2(mx([R_[b]['pair_sum_max'] for b in R_]), 1)
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
N['nSsUps'] = rnd(nb * med([r.get('uniform_ps') for r in b5])) if fin([r.get('uniform_ps') for r in b5]) else '--'
N['nForestGapMax'] = ('%.0e' % S['forest_two']['gap_max']) if fr else '--'
N['nForestOverlapN'] = str(S['forest_engine_overlap']['n']); N['nForestOverlapMax'] = f2(100 * S['forest_engine_overlap']['max_rel'], 1) if ov else '--'
N['nForestOverlapAgree'] = str(S['forest_engine_overlap']['agree']); N['nForestOverlapRest'] = str(S['forest_engine_overlap']['n'] - S['forest_engine_overlap']['agree'])
N['nThreeForestMed'] = f2(100 * S['forest_round3_b4']['rec'], 0) if 'forest_round3_b4' in S else '--'
N['nLabelCert'] = '%.0e' % max(S['label']['cert_gap'], 1e-12)
N['nScaleSame'] = str(S.get('scale_same_tree_b4', '--'))
N['nGainComputable'] = str(sum(1 for r in br_gain if r.get('computable'))); N['nGainExactNon'] = str(sum(1 for _, r in ex2 if not r.get('computable')))
N['nGainExactNonMin'] = pctfloor(mn([x for x, r in ex2 if not r.get('computable')]))
N['nCompAgree'] = str(S['screen_two']['comp_agree']); N['nCompBrfss'] = str(S['screen_two']['computable']); N['nBrfssRuns'] = str(S['screen_two']['nbrfss']); N['nTwoBounded'] = str(S['screen_two']['bounded'])
N['nScreenTwoRecMin'] = pctfloor(S['screen_two']['rec_min'])
N['nTwoBoundMax'] = f2(S['screen_two']['bounded_ratio_max']); N['nTwoBoundMin'] = f2(S['screen_two']['bounded_ratio_min']); N['nTwoBoundRec'] = pctfloor(S['screen_two']['bounded_rec_min']) if bd2 else '--'
N['nSixExact'] = str(sum(1 for r in sc if r['dataset'] == 'BRFSS' and r['b'] == 6 and r['two_computed'] and not r.get('two_bounded')))
# ================================================================== v17: constants within log-linear models (model_v17)
mo = load(R / 'model_v17' / 'BRFSS_*.json'); S['model'] = {}
if mo:
    nt = [r for r in mo if not r.get('trivial')]
    tgt_ = lambda r: 'other sex' if r['shift'] else 'random half'
    ml = [r'\begin{table}[h]', r'\centering', r'\caption{Constants within log-linear models for the BRFSS screening trees whose rule depends on more than $b$ items (NMODEL of NALL runs; in the others one form of the rule\textquotesingle s items is complete data). $P_k$ is the maximum-likelihood fit of the order-$k$ model to the target law on the label and the rule\textquotesingle s $K$ items. All entries are relative to $\Var_{P_k}(t)$, the constant of design-based branching. Design: $W_{\rm fixed}(P_k)$ without a model. Complete: efficiency bound for complete records in the model. Fixed, Branch: $W^{(k)}$ for forms of $b$ of the $K$ items and for depth-$b$ trees, certified to a relative gap of GAPMAX or better, except the three-way branching constants at $b=6$ ($^\ast$), where column generation was stopped after 15 minutes with a certified gap of at most GAPSIX\%; the value shown is the upper bound, so the ratio is a lower bound that is at most that much too small. Ratio: fixed over branch.}',
          r'\label{tab:model}', r'\scriptsize', r'\setlength{\tabcolsep}{3.2pt}', r'\begin{tabular}{rlrr r rrrr r rrrr}', r'\toprule',
          r' & & & & & \multicolumn{4}{c}{pairwise model, $k=2$} & & \multicolumn{4}{c}{three-way model, $k=3$} \\', r'\cmidrule{6-9}\cmidrule{11-14}',
          r'$b$ & target & seed & $K$ & Design & Complete & Fixed & Branch & Ratio & Design & Complete & Fixed & Branch & Ratio \\', r'\midrule']
    gaps = []; gaps6 = []
    for r in sorted(nt, key=lambda r: (r['b'], r['shift'], r['seed'])):
        o2, o3 = r['order2'], r['order3']; g3 = 1 - o3['branch_lower'] / o3['branch']; loose = g3 > 1e-3
        gaps += [1 - o2['branch_lower'] / o2['branch']] + ([] if loose else [g3]) + [1 - o['fixed_lower'] / o['fixed'] for o in (o2, o3)]; gaps6 = gaps6 + [g3] if loose else gaps6
        ml.append(f"{r['b']} & {tgt_(r)} & {r['seed'] - 20261108} & {r['items']} & {f2(o2['design_fixed_at_fit'])} & {f2(o2['full'])} & {f2(o2['fixed'])} & {f2(o2['branch'])} & {f2(o2['fixed'] / o2['branch'])} & {f2(o3['design_fixed_at_fit'])} & {f2(o3['full'])} & {f2(o3['fixed'])} & {f2(o3['branch'])}{'$^\\ast$' if loose else ''} & {f2(o3['fixed'] / o3['branch'])} \\\\")
    ml += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    S['model']['gap_max'] = mx(gaps)
    (M / 'v17_model_table.tex').write_text('\n'.join(ml).replace('NMODEL', str(len(nt))).replace('NALL', str(len(mo))).replace('GAPMAX', '$10^{%d}$' % int(np.ceil(np.log10(max(mx(gaps), 1e-12))))).replace('GAPSIX', f2(100 * mx(gaps6), 1) if gaps6 else '0') + '\n')
    S['model']['gap6_max'] = mx(gaps6) if gaps6 else 0.0; S['model']['n_loose'] = len(gaps6); N['nModelGapSix'] = f2(100 * S['model']['gap6_max'], 1) if gaps6 else '0'
    for k in (2, 3):
        key = f'order{k}'; rat = [r[key]['fixed'] / r[key]['branch'] for r in nt]
        S['model'][k] = dict(n=len(nt), ratio_med=med(rat), ratio_min=mn(rat), ratio_max=mx(rat), design_med=med([r[key]['design_fixed_at_fit'] for r in nt]), design_min=mn([r[key]['design_fixed_at_fit'] for r in nt]), design_max=mx([r[key]['design_fixed_at_fit'] for r in nt]),
                             fixed_min=mn([r[key]['fixed'] for r in nt]), fixed_max=mx([r[key]['fixed'] for r in nt]), fixed_med=med([r[key]['fixed'] for r in nt]), branch_med=med([r[key]['branch'] for r in nt]), branch_min=mn([r[key]['branch'] for r in nt]), branch_max=mx([r[key]['branch'] for r in nt]),
                             full_med=med([r[key]['full'] for r in nt]), tree_med=med([r[key]['rule_tree'] for r in nt]), desforms_over=med([r[key]['model_on_design_forms'] / r[key]['fixed'] - 1 for r in nt]),
                             share_removed=med([1 - np.log(r[key]['fixed'] / r[key]['branch']) / np.log(r[key]['design_fixed_at_fit']) for r in nt if r[key]['design_fixed_at_fit'] > 1.01]),
                             by_b={b: med([r[key]['fixed'] / r[key]['branch'] for r in nt if r['b'] == b]) for b in sorted({r['b'] for r in nt})})
    S['model']['design_by_b'] = {b: med([r['order2']['design_fixed_at_fit'] for r in nt if r['b'] == b]) for b in sorted({r['b'] for r in nt})}
    S['model']['delta_shift'] = mx([abs(r[f'order{k}']['delta_fit'] - r['delta_emp']) for r in nt for k in (2, 3)])
    N['nModelRuns'] = str(len(nt)); N['nModelAll'] = str(len(mo))
    for k, w in ((2, 'Two'), (3, 'Three')):
        s = S['model'][k]
        N[f'nModel{w}Lo'] = f2(s['ratio_min']); N[f'nModel{w}Hi'] = f2(s['ratio_max']); N[f'nModel{w}Med'] = f2(s['ratio_med'])
        N[f'nModel{w}FixLo'] = f2(s['fixed_min']); N[f'nModel{w}FixHi'] = f2(s['fixed_max']); N[f'nModel{w}BrLo'] = f2(s['branch_min']); N[f'nModel{w}BrHi'] = f2(s['branch_max'])
        N[f'nModel{w}FixMed'] = f2(s['fixed_med']); N[f'nModel{w}BrMed'] = f2(s['branch_med']); N[f'nModel{w}Removed'] = f2(100 * s['share_removed'], 0); N[f'nModel{w}DesForms'] = f2(100 * s['desforms_over'], 0)
    N['nModelDesignLo'] = f2(S['model'][2]['design_min']); N['nModelDesignHi'] = f2(S['model'][2]['design_max']); N['nModelDesignMed'] = f2(S['model'][2]['design_med'])
ad = load(R / 'model_v17' / 'address_b*.json'); S['address_model'] = {}
if ad:
    from math import comb
    def Nsj(s_, j): return sum(comb(s_, i) for i in range(j + 1))
    def Lk(b, k): return Nsj(b - 1, k - 2) ** 2 / max((b - s_) * Nsj(s_, k - 2) for s_ in range(b))
    al = [r'\begin{table}[h]', r'\centering', r'\caption{The address contrast at the uniform law within the order-$k$ log-linear model: constants relative to $\sigma_P^2=1$, computed by the solver (certified gaps below $10^{-5}$). Complete: bound for complete records. $L_k(b)$: the lower bound of Theorem~\ref{thm:structuredfull}(c) on the fixed constant. Without a model the ratio is $2^{b-1}$.}',
          r'\label{tab:addressmodel}', r'\small', r'\begin{tabular}{rrrrrrrr}', r'\toprule', r'$b$ & $m$ & $k$ & Complete & Fixed & Branch & Ratio & $L_k(b)$ \\', r'\midrule']
    for r in sorted(ad, key=lambda r: r['b']):
        for k in sorted(int(key[5:]) for key in r if key.startswith('order')):
            if k > r['b'] + 1: continue
            o = r[f'order{k}']; S['address_model'][f"{r['b']},{k}"] = dict(fixed=o['fixed'], branch=o['branch'], ratio=o['fixed'] / o['branch'])
            al.append(f"{r['b']} & {r['items']} & {k} & {f2(o['full'], 3)} & {f2(o['fixed'], 3)} & {f2(o['branch'], 3)} & {f2(o['fixed'] / o['branch'])} & {f2(Lk(r['b'], k), 3)} \\\\")
            assert o['fixed'] >= Lk(r['b'], k) - 1e-6
    al += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v17_address_table.tex').write_text('\n'.join(al) + '\n')

# ================================================================== v17: audits under three collection designs (curve_v17)
c7 = load(R / 'curve_v17' / '*.json'); S['curve17'] = {}
if c7:
    ns7 = sorted(int(k) for k in c7[0]['curve']); cb = [r for r in c7 if r['branch_ok']]
    def mse_ratio(r, n, a, b_): return (r['curve'][str(n)][a]['rmse'] / r['curve'][str(n)][b_]['rmse']) ** 2
    cl7 = [r'\begin{table}[h]', r'\centering', r'\caption{Simulated audits under three collection designs with the same cap (NTREES BRFSS trees: caps 4 and 5, two targets, three seeds; REPS replications per tree and size). Entries are ratios of mean squared errors, the finite-sample analogue of a records ratio: median over trees [minimum, maximum]. Design-based: the fitted form score against the mean of $t$ under branching. ML-2 and ML-3: maximum likelihood under the pairwise and three-way log-linear models, on the fitted forms (optimized for the design-based score) and on forms optimized for the pairwise model, each against the same model fitted to branching records (the rule administered and padded to $b$ questions). Last column: pairwise ML on fitted forms against the design-based mean under branching.}',
           r'\label{tab:curve}', r'\scriptsize', r'\setlength{\tabcolsep}{3pt}', r'\begin{tabular}{rllllll}', r'\toprule',
           r' & Design-based & \multicolumn{2}{c}{ML-2: forms / branching records} & \multicolumn{2}{c}{ML-3: forms / branching records} & ML-2 on forms / \\',
           r'$n$ & forms / branching & fitted forms & model forms & fitted forms & model forms & design-based branching \\', r'\midrule']
    for n in ns7:
        row = {}
        for name, a, b_ in [('design', 'fixed', 'branch'), ('em2_forms', 'forms_em2', 'branch_em2'), ('em2_mforms', 'mforms_em2', 'branch_em2'), ('em3_forms', 'forms_em3', 'branch_em3'), ('em3_mforms', 'mforms_em3', 'branch_em3'),
                            ('em2_vs_branch', 'forms_em2', 'branch'), ('em2_vs_fixed', 'forms_em2', 'fixed'), ('em3_vs_fixed', 'forms_em3', 'fixed'), ('bem2_vs_branch', 'branch_em2', 'branch'), ('mem2_vs_branch', 'mforms_em2', 'branch'), ('bem3_vs_branch', 'branch_em3', 'branch'), ('em3_vs_branch', 'forms_em3', 'branch')]:
            v = [mse_ratio(r, n, a, b_) for r in cb]
            row[name] = dict(med=med(v), min=mn(v), max=mx(v), q25=float(np.percentile(v, 25)), q75=float(np.percentile(v, 75)), above=sum(1 for x in v if x > 1.0))
        row['bias_sd_forms'] = med([abs(r['curve'][str(n)]['forms_em2']['bias']) / r['curve'][str(n)]['forms_em2']['sd'] for r in cb])
        row['bias_sd_branch'] = med([abs(r['curve'][str(n)]['branch_em2']['bias']) / r['curve'][str(n)]['branch_em2']['sd'] for r in cb])
        S['curve17'][n] = row; c_ = lambda k_: f"{f2(row[k_]['med'])} [{f2(row[k_]['min'])}, {f2(row[k_]['max'])}]"
        cl7.append(f"{n:,} & {c_('design')} & {c_('em2_forms')} & {c_('em2_mforms')} & {c_('em3_forms')} & {c_('em3_mforms')} & {c_('em2_vs_branch')} \\\\")
    cl7 += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v17_curve_table.tex').write_text('\n'.join(cl7).replace('NTREES', str(len(cb))).replace('REPS', str(c7[0]['reps'])) + '\n')
    C7 = S['curve17']; small = [n for n in ns7 if n <= 4000]; big = [n for n in ns7 if n >= 16000]
    N['nCurveTrees'] = str(len(cb)); N['nCurveReps'] = str(c7[0]['reps']); N['nCurveAllTrees'] = str(len(c7))
    N['nAudDesignLo'] = f2(mn([C7[n]['design']['med'] for n in ns7])); N['nAudDesignHi'] = f2(mx([C7[n]['design']['med'] for n in ns7]))
    for nm, w in (('em2_forms', 'TwoForms'), ('em2_mforms', 'TwoMforms'), ('em3_forms', 'ThreeForms'), ('em3_mforms', 'ThreeMforms'), ('em2_vs_branch', 'TwoVsBranch'), ('bem2_vs_branch', 'BranchTwoVsBranch'), ('em2_vs_fixed', 'TwoVsFixed'), ('em3_vs_fixed', 'ThreeVsFixed'), ('mem2_vs_branch', 'MformsTwoVsBranch')):
        N[f'nAud{w}Lo'] = f2(mn([C7[n][nm]['med'] for n in ns7])); N[f'nAud{w}Hi'] = f2(mx([C7[n][nm]['med'] for n in ns7]))
        N[f'nAud{w}SmallLo'] = f2(mn([C7[n][nm]['med'] for n in small])); N[f'nAud{w}SmallHi'] = f2(mx([C7[n][nm]['med'] for n in small]))
        N[f'nAud{w}BigLo'] = f2(mn([C7[n][nm]['med'] for n in big])); N[f'nAud{w}BigHi'] = f2(mx([C7[n][nm]['med'] for n in big]))
        N[f'nAud{w}MaxAll'] = f2(mx([C7[n][nm]['max'] for n in ns7])); N[f'nAud{w}MinAll'] = f2(mn([C7[n][nm]['min'] for n in ns7]))
        N[f'nAud{w}SurveyLo'] = f2(mn([C7[n][nm]['med'] for n in ns7 if n <= 8000])); N[f'nAud{w}SurveyHi'] = f2(mx([C7[n][nm]['med'] for n in ns7 if n <= 8000])); N[f'nAud{w}SurveyMax'] = f2(mx([C7[n][nm]['max'] for n in ns7 if n <= 8000]))
    lastb = [n for i, n in enumerate(ns7) if all(C7[m_]['em2_vs_fixed']['above'] == 0 for m_ in ns7[:i + 1])]
    N['nCurveLastAllBetter'] = '{:,}'.format(max(lastb)) if lastb else '--'
    for n, tag in ((16000, 'c'), (32000, 'd')):
        N[f'nCurveTwoWorse{tag}'] = str(C7[n]['em2_vs_fixed']['above']); N[f'nCurveTwoMax{tag}'] = f2(np.sqrt(C7[n]['em2_vs_fixed']['max']))
        N[f'nAudBranchTwoWorse{tag}'] = str(C7[n]['bem2_vs_branch']['above'])
    N['nAudBiasFormsSmall'] = f2(C7[1000]['bias_sd_forms']); N['nAudBiasBranchSmall'] = f2(C7[1000]['bias_sd_branch'])
    N['nAudBiasFormsBig'] = f2(C7[max(ns7)]['bias_sd_forms']); N['nAudBiasBranchBig'] = f2(C7[max(ns7)]['bias_sd_branch'])

# ================================================================== v17: pilot smoothed by a pairwise fit (pilot_v17)
p7 = [r for r in load(R / 'pilot_v17' / '*.json') if r.get('pilot')]; S['pilot17'] = {}
if p7:
    fr_ = {(r['b'], r['shift'], r['seed']): r['fixed_ratio'] for r in sc if r['dataset'] == 'BRFSS'}
    pl7 = [r'\begin{table}[h]', r'\centering', r'\caption{The pilot of Table~\ref{tab:pilot} with its cell masses smoothed by a pairwise log-linear fit (BRFSS runs with a gain; medians over runs of the median over DRAWS pilots; $N=4n_1$). Empirical: cell masses from the pilot\textquotesingle s frequencies, as in Table~\ref{tab:pilot}. Pairwise fit: cell masses from the pairwise model fitted to the pilot by EM. Pilot, learned and all-in are per-record variances relative to branching, as in Table~\ref{tab:pilot}; over oracle is the median over runs of the all-in price divided by that run\textquotesingle s oracle optimum over all forms.}',
           r'\label{tab:pilotsmooth}', r'\small', r'\setlength{\tabcolsep}{4pt}', r'\begin{tabular}{rrr rrr rrrr rr}', r'\toprule',
           r' & & & \multicolumn{3}{c}{empirical} & \multicolumn{4}{c}{pairwise fit} & \multicolumn{2}{c}{oracle} \\', r'\cmidrule(lr){4-6}\cmidrule(lr){7-10}\cmidrule(lr){11-12}',
           r'$b$ & runs & $n_1$ & pilot & learned & all-in & pilot & learned & all-in & over oracle & PS & all forms \\', r'\midrule']
    for b in sorted({r['b'] for r in p7}):
        rr = [r for r in p7 if r['b'] == b]; S['pilot17'][b] = dict(n=len(rr), ps=med([r['ps_oracle'] for r in rr]), best=med([fr_[(r['b'], r['shift'], r['seed'])] for r in rr]))
        for i, k in enumerate(sorted(int(x) for x in rr[0]['pilot'])):
            g_ = lambda tag, f_: med([r['pilot'][str(k)][tag][f_] for r in rr])
            over = {tag: med([r['pilot'][str(k)][tag]['allin'] / fr_[(r['b'], r['shift'], r['seed'])] - 1 for r in rr]) for tag in ('emp', 'll')}
            S['pilot17'][b][k] = dict(emp=g_('emp', 'allin'), ll=g_('ll', 'allin'), ll_learned=g_('ll', 'learned'), over_emp=over['emp'], over_ll=over['ll'], ll_max=mx([r['pilot'][str(k)]['ll']['allin'] for r in rr]), ll_min=mn([r['pilot'][str(k)]['ll']['allin'] for r in rr]))
            pl7.append(f"{b if i == 0 else ''} & {len(rr) if i == 0 else ''} & {k:,} & {f2(g_('emp', 'pilot_cf'))} & {f2(g_('emp', 'learned'))} & {f2(g_('emp', 'allin'))} & {f2(g_('ll', 'pilot_cf'))} & {f2(g_('ll', 'learned'))} & {f2(g_('ll', 'allin'))} & +{f2(100 * over['ll'], 0)}\\% & {f2(S['pilot17'][b]['ps']) if i == 0 else ''} & {f2(S['pilot17'][b]['best']) if i == 0 else ''} \\\\")
    pl7 += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v17_pilotsmooth_table.tex').write_text('\n'.join(pl7).replace('DRAWS', '12') + '\n')
    for b, w in ((4, 'Four'), (5, 'Five'), (6, 'Six')):
        if b not in S['pilot17']: continue
        for k, tag in ((1000, 'c'), (2000, 'd')):
            s = S['pilot17'][b][k]; N[f'nSmooth{w}{tag}'] = f2(s['ll']); N[f'nSmoothEmp{w}{tag}'] = f2(s['emp']); N[f'nSmoothOver{w}{tag}'] = f2(100 * s['over_ll'], 0); N[f'nSmoothEmpOver{w}{tag}'] = f2(100 * s['over_emp'], 0)
        N[f'nSmooth{w}Best'] = f2(S['pilot17'][b]['best'])
    allc = [r['pilot']['1000']['ll']['allin'] for r in p7]; N['nSmoothRunLo'] = f2(mn(allc)); N['nSmoothRunHi'] = f2(mx(allc)); N['nSmoothRuns'] = str(len(p7))
    N['nSmoothOverLo'] = f2(100 * mn([S['pilot17'][b][2000]['over_ll'] for b in S['pilot17']]), 0); N['nSmoothOverHi'] = f2(100 * mx([S['pilot17'][b][2000]['over_ll'] for b in S['pilot17']]), 0)

# ================================================================== v17: forests on twenty features (forest_scale_v17)
f7 = load(R / 'forest_scale_v17' / '*.json'); S['forest_scale'] = {}
if f7:
    fl7 = [r'\begin{table}[h]', r'\centering', r'\caption{Forest updates on $m=20$ median-binarized Spambase features (twenty-tree forests of depth $b$, 3,101 held-out records, 1\% smoothing). The fixed optimum is certified over all forms. Column generation over two-round and branching interviews was stopped after a wall-clock budget, so their constants are certified intervals and the ratios to branching are intervals: fixed / branch $\in[W_{\rm fixed}/\overline W_{\rm branch},\,W_{\rm fixed}/\underline W_{\rm branch}]$. Used: features on which the forests split. Iter.: column-generation iterations for branching.}',
           r'\label{tab:forestscale}', r'\small', r'\setlength{\tabcolsep}{4pt}', r'\begin{tabular}{rrrrrllr}', r'\toprule', r'$b$ & seed & forms & used & fixed / complete & fixed / branch & two rounds / branch & iter. \\', r'\midrule']
    for r in sorted(f7, key=lambda r: (r['b'], r['seed'])):
        two = f"[{f2(r['round2_ratio_lower'])}, {f2(r['round2_ratio_upper'])}]" if 'round2_ratio_upper' in r else '--'
        fl7.append(f"{r['b']} & {r['seed'] - 20261108} & {r['forms']:,} & {r['features_used']} & {f2(r['fixed_vs_full'], 1)} & [{f2(r['fixed_ratio_lower'])}, {f2(r['fixed_ratio_upper'])}] & {two} & {r['branch_iterations']} \\\\")
    fl7 += [r'\bottomrule', r'\end{tabular}', r'\end{table}']
    (M / 'v17_forestscale_table.tex').write_text('\n'.join(fl7) + '\n')
    for b, w in ((3, 'Three'), (4, 'Four')):
        rr = [r for r in f7 if r['b'] == b]
        if not rr: continue
        S['forest_scale'][b] = dict(n=len(rr), lo=mn([r['fixed_ratio_lower'] for r in rr]), hi=mx([r['fixed_ratio_upper'] for r in rr]), lo_max=mx([r['fixed_ratio_lower'] for r in rr]), hi_min=mn([r['fixed_ratio_upper'] for r in rr]))
        N[f'nFScale{w}Lo'] = f2(S['forest_scale'][b]['lo']); N[f'nFScale{w}Hi'] = f2(S['forest_scale'][b]['hi']); N[f'nFScale{w}N'] = str(len(rr)); N[f'nFScale{w}LoMax'] = f2(S['forest_scale'][b]['lo_max'])
        two = [r for r in rr if 'round2_ratio_upper' in r]
        if two: N[f'nFScale{w}TwoHi'] = f2(mx([r['round2_ratio_upper'] for r in two])); N[f'nFScale{w}TwoLo'] = f2(mn([r['round2_ratio_lower'] for r in two]))

# ================================================================== v17: main-text table for the screening trees
mkey = {(r['b'], r['shift'], r['seed']): r for r in mo} if mo else {}
pkey = {(r['b'], r['shift'], r['seed']): r for r in p7} if p7 else {}
def mratio(r, k):
    q = mkey.get((r['b'], r['shift'], r['seed']))
    if q is None: return None
    return 1.0 if q.get('trivial') else q[f'order{k}']['fixed'] / q[f'order{k}']['branch']
mt = [r'\begin{table*}[t]', r'\centering',
      r'\caption{BRFSS screening trees on twelve items (six runs per cap: two targets, three seeds): records that pre-committed forms need relative to branching interviews; medians over runs, range in brackets. \emph{Without a model} (design-unbiased scores; branching asks the tree\textquotesingle s own questions and attains the full-information variance): Oracle, optimal forms at the target law; Reference, forms fitted on 20,000 source records; Pilot, forms learned from a pilot of a quarter of $N=4{,}000$ audit records smoothed by a pairwise fit, pilot charged (runs with a gain); U-paths, uniform over the tree\textquotesingle s question paths with the best scores; Two rounds, optimal two-round design (TWOSIXNOTE); Bracket, the ends $1/\rho_P^2$ and $N_P$ of Theorem~\ref{thm:bracket}. \emph{Within a model}: $W^{(k)}_{\rm fixed}/W^{(k)}_{\rm branch}$ at the order-$k$ log-linear fit of the target law, with every class at its optimum (one for runs whose rule depends on at most $b$ items; at $b=6$, $k=3$ the branching optimum is bracketed to within \nModelGapSix\%, so the ratios are lower bounds). On thyroid (24 runs) every optimized ratio is $1.00$. -- not computed.}',
      r'\label{tab:screening}', r'\footnotesize', r'\setlength{\tabcolsep}{5pt}', r'\begin{tabular}{r l r r r r l l l}', r'\toprule',
      r' & \multicolumn{6}{c}{without a model} & \multicolumn{2}{c}{within a model} \\', r'\cmidrule(lr){2-7}\cmidrule(lr){8-9}',
      r'$b$ & Oracle & Reference & Pilot & U-paths & Two rounds & Bracket & pairwise ($k=2$) & three-way ($k=3$) \\', r'\midrule']
for b in [3, 4, 5, 6]:
    rr = grp('BRFSS', b)
    if not rr: continue
    two = [r['two'] for r in rr if r.get('two_computed')]
    twoc = (('$\\le$' if any(r.get('two_bounded') for r in rr) else '') + f2(med(two))) if len(two) == len(rr) else '--'
    pil_ = [pkey[(r['b'], r['shift'], r['seed'])]['pilot']['1000']['ll']['allin'] for r in rr if (r['b'], r['shift'], r['seed']) in pkey]
    def mc(k):
        v = [mratio(r, k) for r in rr]
        lb = k == 3 and b == 6 and S['model'].get('n_loose')
        return (('$\\ge$' if lb else '') + f"{f2(med(v))} [{f2(mn(v))}, {f2(mx(v))}]") if all(x is not None for x in v) else '--'
    mt.append(f"{b} & {f2(med([r['fixed_ratio'] for r in rr]))} [{f2(mn([r['fixed_ratio'] for r in rr]))}, {f2(mx([r['fixed_ratio'] for r in rr]))}] & {f2(med([r['fixed_fit_ratio'] for r in rr]))} & {f2(med(pil_)) if pil_ else '--'} & {f2(med([r.get('uniform_ps') for r in rr]))} & {twoc} & [{f2(med([r['lower_c'] for r in rr]))}, {f2(med([r.get('centered_upper') for r in rr]),1)}] & {mc(2)} & {mc(3)} \\\\")
mt += [r'\bottomrule', r'\end{tabular}', r'\end{table*}']
(M / 'v17_screening_table.tex').write_text('\n'.join(mt).replace('TWOSIXNOTE', note) + '\n')

out = ['% generated by Research/code/v17_tables.py from Research/results; do not edit']
for k, v in N.items(): out.append('\\newcommand{\\%s}{%s}' % (k, v))
(M / 'v17_numbers.tex').write_text('\n'.join(out) + '\n')
json.dump(dict(summary=S, macros=N), open(R / 'v17_summary.json', 'w'), indent=1, default=str)
print(json.dumps(N, indent=0))
