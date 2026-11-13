"""Build the cleaned, lettered v14 appendix from the v13 appendix files (run from the Manuscript folder).
NOTE (v15): the a14_*.tex files are edited by hand from v15 on; do not rerun this script over them.
Each group becomes one lettered section; former sections become subsections. Passages that relied on
experiments outside the paper are removed or rewritten here, so every edit is recorded in one place."""
import re
from pathlib import Path

M = Path('.')
def lines(f, a=None, b=None):
    L = (M / f).read_text().split('\n')
    return '\n'.join(L[(a - 1 if a else 0):(b if b else len(L))])

def demote(t):
    t = t.replace('\\subsection', '\\subsubsection').replace('\\section', '\\subsection')
    return t

def must_replace(t, old, new):
    assert t.count(old) == 1, ('not unique', old[:80], t.count(old))
    return t.replace(old, new)

out = {}
# ---------------------------------------------------------------- B: identification and Theorem 1
sr = (M / 'supporting_results_v13.tex').read_text()
cut = sr.index('\\section{Additional Sharpness Results}')
B = demote(sr[:cut]) + '\n' + demote((M / 'app_id_general_v13.tex').read_text())
out['a14_B.tex'] = '\\section{Identification and the Exact Characterization}\\label{app:B}\n' + B
# ---------------------------------------------------------------- C: the sharp gap and its extensions
C2 = sr[cut:]
C2 = must_replace(C2, ' The eight-feature empirical diagnostic solves the coefficient program directly.', '')
cl = (M / 'cost_local_theory.tex').read_text()
cl = must_replace(cl, """The center-dependent local design is an oracle, not a calibration algorithm.
The full-support qualification is essential to this regular argument. We
report both empirical-population coefficients and a fixed $1\\%$
uniformly smoothed population in the eight-feature experiment; only the
latter directly satisfies this proposition on its stated profile space.
The finite-sample globally unbiased bound applies at
boundary empirical laws.""", """The center-dependent local design is an oracle, not a calibration algorithm.
The full-support qualification is essential to this regular argument; this is
why every population in Section~\\ref{sec:experiments} mixes the empirical law
with a uniform mass, whose size is varied in Appendix~\\ref{app:capsens}.
The finite-sample globally unbiased bound applies at
boundary empirical laws.""")
bc = (M / 'app_budgetcurve_v13.tex').read_text()
bc = must_replace(bc, '\\section{Binary Experiments and the Budget Curve}\\label{app:sign}', '\\section{The Binomial Value and a Synthetic Budget Curve}\\label{app:sign}')
re_ = (M / 'review_extensions.tex').read_text().split('\n')
inst = '\n'.join(re_[0:34])   # instance certificates + four-bit certificate input
inst = inst.replace('\\section{Instance Certificates, Rounds and Observation Timing}\\label{app:instances}', '\\section{Instance Certificates}\\label{app:instances}')
inst = inst.replace(' The supplement records both bounds and the numerical equality residual.', ' Both bounds and the numerical equality residual are recorded with the code.')
C = demote((M / 'universal_proof.tex').read_text()) + '\n' + demote(C2) + '\n' + demote((M / 'revision_theory.tex').read_text()) + '\n' + \
    demote((M / 'structural_extensions.tex').read_text()) + '\n' + demote(cl) + '\n' + demote(inst) + '\n' + demote(bc)
out['a14_C.tex'] = '\\section{The Sharp Gap and Its Extensions}\\label{app:C}\n' + C
# ---------------------------------------------------------------- D: rounds
th = (M / 'v12_theory.tex').read_text(); pc = th.index('\\section{The Value of Adaptivity at a Given Population}')
th = must_replace(th, '''The constant separation $V_2\\ge4/3$ of Corollary~\\ref{cor:roundseparation}
is therefore not the end of the hierarchy. Part (a) and the corollary leave
the exponent for $2\\le r<b$ between $\\lfloor(b-1)/r\\rfloor-\\log_2b$ and $b-r$;
the exact frontier is open.''', '''The constant separation $V_2\\ge4/3$ of Corollary~\\ref{cor:roundseparation}
is therefore not the end of the hierarchy. Part (b) and the corollary place
the exponent for $2\\le r<b$ between $\\lfloor(b-1)/r\\rfloor-\\log_2b$ and $b-r$;
the binary pointer tree (Theorem~\\ref{thm:binarytree}) raises the lower end to
$b-1-r\\log_2(3b)$, and Appendix~\\ref{app:pointerexact} computes the constants of
that tree exactly at small caps.''')
pc = th.index('\\section{The Value of Adaptivity at a Given Population}')  # v15 fix: recompute after the replacement above (the v14 run used the stale index and moved 165 characters from D.1 to E)
assert th[:pc].rstrip().endswith('two-stage designs.')
rounds2 = '\n'.join(re_[34:54])
D = demote(th[:pc]) + '\n' + rounds2 + '\n\\input{a14_pointer}\n'
out['a14_D.tex'] = '\\section{Rounds of Adaptivity}\\label{app:D}\n' + D
# ---------------------------------------------------------------- E: population constants and computation
mv = (M / 'v12_moved_v13.tex').read_text(); mv = mv[:mv.index('\\section{Choosing a Collection Design}')]
mv = must_replace(mv, 'We use $\\beta=0.1$ for fitted designs in the earlier experiments and $\\beta=0.05$ in Section~\\ref{sec:experiments}.', 'Fitted designs in Section~\\ref{sec:experiments} use $\\beta=0.05$.')
mv = must_replace(mv, ' With restricted pilot records, its leaf--label reference can be fitted by EM from the observed form, stopping node and label (the supplementary report).', '')
mv = must_replace(mv, ' The \\emph{prefix} comparator uses the answers along the tree up to its first unavailable query, discarding other coordinates on the form.', '')
mv = must_replace(mv, 'For ordinal data, the implementation uses tensor contrasts on categories defined by the frozen tree\'s thresholds.', 'For ordinal data the same program applies to tensor contrasts on the categories defined by the frozen tree\'s thresholds.')
mv = must_replace(mv, '\\section{Fixed-Form Scores from Shared Coordinates}\\label{sec:pathdesign}', '\\section{The Form Program and the Path-Set Menu}\\label{sec:pathdesign}')
ff = (M / 'full_form_v13.tex').read_text(); ff = ff[:ff.index('\\paragraph{Calibration and certificates.}')]
ff = must_replace(ff, 'For ordinal features we split each coordinate at all thresholds used for it\nin the frozen tree,', 'For ordinal features one splits each coordinate at all thresholds used for it\nin the frozen tree,')
ff = must_replace(ff, '\\section{Complete Form Scores and Operational Comparisons}\\label{app:operational}\n\\subsection{Shared-Coordinate Corrections and the Complete Score Space}\n\\label{app:fullscores}',
                  '\\section{Shared-Coordinate Corrections and the Complete Score Space}\\label{app:fullscores}')
eff = '\n'.join(re_[54:64])
eff = must_replace(eff, ' (the finite-sample oracle of the supplementary report)', '')
pd = (M / 'path_design.tex').read_text()
pd = pd[:pd.index('\\subsection{Higher-Dimensional Benchmark}')] + pd[pd.index('\\subsection{Confidence Intervals and Costs}'):]
pd = pd.replace('We enforce $q_j\\ge\\beta/L$ with $\\beta=0.1$,', 'We enforce $q_j\\ge\\beta/L$,')
E_ = demote(th[pc:]) + '\n\\input{a14_upper}\n\\input{a14_engine}\n' + demote(mv) + '\n' + demote(ff) + '\n' + demote(eff) + '\n' + demote(pd) + '\n' + demote((M / 'v13_selfcal.tex').read_text())
out['a14_E.tex'] = '\\section{Population Constants and Their Computation}\\label{app:E}\n' + E_
# ---------------------------------------------------------------- G: beyond low-degree contrasts
dense = '\n'.join(re_[91:102])
G = demote((M / 'v9_extensions.tex').read_text()) + '\n' + demote(dense) + '\n' + demote((M / 'metric_extensions.tex').read_text())
out['a14_G.tex'] = '\\section{Beyond Low-Degree Accuracy Contrasts}\\label{app:G}\n' + G
# ---------------------------------------------------------------- H: PISA
pi = (M / 'archive_pisa_v13.tex').read_text(); pi = pi[:pi.index('\\section{Cost Regimes Under a Relaxable Cap}')]
pi = pi.replace('\\section{Analysis of a Genuine Planned-Missing Archive}\\label{app:pisa}', '\\section{A Real Planned-Missing Archive}\\label{app:pisa}')
out['a14_H.tex'] = pi
for k, v in out.items():
    (M / k).write_text(v + '\n'); print(k, len(v))
# report residual legacy words
for k, v in out.items():
    for w in ['SUSHI', 'SAPA', 'ten binary', '70 ', 'eight-feature', 'larger-tree', 'v12', 'v11', 'earlier release', 'supplementary report', 'earlier experiment', 'primary-split', 'primary split']:
        for mm in re.finditer(re.escape(w), v):
            s = max(0, mm.start() - 100); print('  RESIDUAL', k, w, '::', v[s:mm.end() + 100].replace('\n', ' '))
