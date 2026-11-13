# Research handoff — v17 (round 7)

Date: 2026-11-13. Paper: **The Statistical Value of Adaptive Feature Queries** (ICML 2027 target, not submitted). Current draft: `Manuscript/paper.pdf` (57 pages; main text exactly 8 pages; md5 2ed68fce4ce34c606158cbf66f0e8b5f; this is the PDF the round-7 reviewers read, unchanged since). Source: `Manuscript/paper.tex`, `Manuscript/v17_experiments_main.tex`, `Manuscript/v17_sentences.tex` and the appendix files `a14_*.tex`, `a15_*.tex`, `a17_*.tex`, all written by hand. Every number in the text is a macro in `Manuscript/v17_numbers.tex`, generated with all tables by `Research/code/v17_tables.py` from `Research/results`. v13-v16 snapshots are unchanged (`../Revision_v13` ... `../Revision_v16`).

## Status of the user's loop
| Round | Novelty | Reviews (R1 theory / R2 statistics / R3 applied ML) | Revision |
| --- | --- | --- | --- |
| 1 | PASS | v11: 3/3/3 | -> v12 |
| 2 | PASS | v12: 3/4/4 | -> v13 |
| 3 | PASS | v13: 4/4/3 | -> v14 |
| 4 | PASS | v14: 3/3/3 | -> v15 |
| 5 | PASS, narrower claim | v15: 4/4/3 | -> v16 |
| 6 | PASS | v16: 3/3/3 | -> v17 |
| 7 | PASS (ROUND_LOG_v17.md) | v17: 3/4/3 (Significance 2 from all three; Presentation 2/3/2) | paused at the round boundary for the user's report; goal not met |

## Where the loop stands
- Seven rounds: 3/3/3, 3/4/4, 4/4/3, 3/3/3, 4/4/3, 3/3/3, 3/4/3. No round has reached three scores of 4. Significance has been 2 from all three reviewers in rounds 4-7.
- No reviewer in rounds 5-7 found an error in a proof. Before the round-7 reviews an independent checking agent refereed the new appendix; its findings were repaired before the freeze (ROUND_LOG_v17.md).
- What round 7 changed in the reviews: R2 moved to 4 and calls the model theorem the most interesting statistical statement; R1 and R3 stayed at 3. Their remaining requests are new research, not edits (below).
- Assessment (the assistant's, not a reviewer's): the round-7 direction (what a model changes) was the right one and is not finished. Both theory-minded reviewers now ask for the same next step, the model-based gap at laws with dependence, and say it would move them (R1 to 4, R2 towards 5). R3's condition, a realistic use case with data or non-identifiable targets, has not been met in four rounds and should not be expected to be met by editing.

## Options for round 8 (full lists in Reviews/README.md)
1. Model-based gap at laws with dependence (R1 item 2, R2 Q1; together they would give R1 = 4 and strengthen R2).
   - Cheap numerical study first: the address contrast at b = 3, 4 along a path of pairwise-model laws in which label and data bits become associated with the address bits. `model_v17.ModelEngine` computes W^(2) and W^(3) for forms and branching at any law on up to about 12 items; `loglin_fit` projects a law onto the model.
   - Then a theorem: either a polynomial bound under a weak-dependence (high-temperature) condition, or a counterexample with a super-polynomial pairwise gap. The Cauchy-Schwarz proof of Theorem thm:structuredfull(b) uses only that E[phi_A | transcript] vanishes for sets A not inside the path set; under dependence these conditional expectations are low-order only approximately.
   - State next to Theorem 5 that (b) and (c) are local statements at independence laws, that the k = 2 optimum has singular information, and that the 1.02-1.13 ratios refer to populations that satisfy the fitted model (R2's two requested additions).
2. Restructure around the exact experiment simulation (R1 item 3; R2 weakness 1). With a uniform guess over the distinct padded path sets, completion has probability exactly 1/L at every profile, so rejection sampling reproduces any branching protocol with a negative-binomial number of fixed-form records of mean K n: every task, every loss, every finite n, no oracle centring. Theorems 2(i), 2(ii), 3(a) and 5(a) become corollaries, and the centred-score construction can go to a remark. Add an explicit comparison with the transcript-guessing conversion in local privacy (Joseph et al. 2019) and with locally bounded adaptivity (Adar & Fischer 2024), and the Fourier-l1 baseline V_fixed <= ||d-hat||_1^2 <= 4^b that path guessing improves to 2^{b-1} (R1 weakness 8).
3. Estimators in the audits (R2 Q2/Q3, R3 Q4): a cross-fitted model-assisted (AIPW) estimator on fixed forms whose augmentation is a pairwise or three-way model fitted to the audit records themselves, with coverage; model selection between k = 2, 3 and saturated; a sequentially updated design across records as a baseline for the one-shot pilot.
4. BRFSS uncertainty (R2 Q5): bootstrap intervals over target respondents for the per-run ratios; survey weights; reference-fitted designs as the headline column.
5. Rounds (R1 item 1): a matching exponent for all r on some family or a lower bound for omega(log b) rounds in polynomial dimension. Open since round 3; R1 suggested a layered pointer-chasing contrast with poly(b) registers per level (round 6).
6. R3: a realistic end-to-end case (real planned-missing or budgeted-acquisition data, m >= 30 with block forms), or non-identifiable targets (thresholded ensembles) through the bias-plus-variance program of Appendix B. Neither has been attempted.
Cheap fixes whatever is chosen:
- Trace "1.33-2.40" (abstract; range over runs of the smoothed all-in pilot price at N = 4,000) to a table, or replace it by the tabulated medians; say that the pilot paragraph's oracle values (1.52 at b = 4) are medians over runs with a gain while Table 2's (1.49) are over all runs.
- Remove vocabulary of earlier drafts from the appendix ("audit", "update", "respondent multiplier", Theorem C.3, Proposition B.3), enlarge Figure 3, verify or drop Li et al. 2026 (flagged by reviewers in rounds 6 and 7).
- Say in the main text that the forest estimand is not thresholded accuracy and that the simulated audits resample the law on which the constants were computed.

## What changed from v16 to v17
- Correction (found by R1 in round 6). Linear-round necessity is claimed only for the single pointer tree on 2^b - 1 features. The abstract, the contribution list, Section 4 and Appendix D now state that the product contrast on at most b^2 features is evaluated exactly in floor(log2 b) rounds, so it gives a lower bound only for r = o(log b / log log b); rounds in polynomial dimension are listed as open.
- New theory: what a model changes (Section 6, Appendix E.2, `Manuscript/a17_structured.tex`). Theorem `thm:structured` / `thm:structuredfull`: (a) path guessing compares experiments, so the factors K_r bound the gap for every model; (b) within the log-linear model with interactions of order <= k, the gap at product laws is at most nu_k <= (b+1)^k; (c) for the address contrast at the uniform law the gap is exactly 1 for k = 2, the fixed constant is at least L_k(b) >= C(b-1,k-2)/b for k >= 3 (below 4 for k = 3) and 2^{b-1} again at k = b+1. Proposition `prop:localmodel`: lower bound on the local minimax risk within a model.
- New solver: `Research/code/model_v17.py` computes the constants within an order-k log-linear model for fixed forms and for branching (column generation with the existing tree pricing; Elfving-dual master; certificates). Self-test: `python3 model_v17.py --selftest` (saturated model = capdesign.Engine).
- New experiments: `model_v17.py` (constants at pairwise and three-way fits of the BRFSS target laws; address contrast at b = 3, 4), `curve_v17.py` (audits under three collection designs, ML under pairwise and three-way models, 12 trees, n = 500 ... 32,000, 400 replications; replaces curve_v16 results), `pilot_v17.py` (pilot smoothed by a pairwise fit), `forest_scale_v17.py` (forests on 20 Spambase features; exact at b = 3, not closed at b = 4), `theory_checks/check_structured.py`.
- Presentation: deployable numbers in the abstract and in the main table (`tab:screening`, columns Oracle / Reference / Pilot / U-paths / Two rounds / Bracket / pairwise / three-way); the wide all-designs table is `tab:screeningfull` in Appendix F. Appendices G (nonlinear models; only the section on other proper scores is kept, as Appendix G) and H (planned-missing archive) are removed from the paper; their sources remain in `../Revision_v16/Manuscript` (`a14_G.tex`, `a14_H.tex`). Related work shortened; discussion rewritten (scope, meaning of the constants, open problems).
- Pipeline: `Research/code/v17_tables.py` writes every table and `Manuscript/v17_numbers.tex`; hand-written, result-dependent sentences are in `Manuscript/v17_sentences.tex`; `Research/code/v17_rounds_figure.py` writes `figures/v17_rounds.pdf`. `curve_v16.py` is kept only because `curve_v17.py` and `pilot_v17.py` import its `LogLin` class.


## Not completed (stated as such in the paper unless noted)
- Model-based bounds at laws with dependence; the exact worst-case exponent within the order-k model; an upper bound on the address ratio for k >= 3.
- A round hierarchy tight beyond constant r; rounds in polynomial dimension.
- Three-way branching constants at b = 6 are bracketed to 2.9%, not closed.
- Forests on 20 features at b = 4: one split run, branching not closed (interval [1.03, 5.76]); two splits not run.
- Exact two-round optima at b = 6 for four BRFSS runs, label-dependent designs at b = 6 and m = 21, forest caps b = 4 at m = 9, 12 and b = 5 (unchanged since v15).
- A model-assisted estimator on the audit's own records; survey weights; a second survey population; a realistic use case with its own data.
- Not stated in the paper: the points under "Cheap fixes" above.

## Pitfalls
- The container restarted once during round 7 while two b = 6 model runs, two forest runs and a LaTeX build were active (the build command returned exit code 137). Background jobs were lost; result files written per task survived. Start long jobs with `nohup setsid`, write one file per task, and make every driver skip existing files.
- `model_v17.py`: the first master used the multiplicative algorithm and needed about 20,000 iterations per solve; it was replaced by the Elfving dual as a cone program. Three-way models at b = 6 (p up to 231 parameters) take 15 minutes or more per run; `--budget` limits the branching column generation and the reported value then has a certified interval.
- The clock in this sandbox advances normally; tool calls are fast relative to it, so "it has been a long time" is usually wrong. Check `date`.
- At most four solver processes on this four-core machine, with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1`. Harness background commands are stopped after their time limit (at most two hours); detached `nohup setsid` jobs are not, but die with the container.
- `pgrep -f pattern` inside a `bash -c` wrapper matches the wrapper; use a bracket in the pattern. A foreground `sleep` followed by other commands is blocked by the harness; wait with a background `until ...; do sleep 15; done` command instead.
- `v17_tables.py` asserts that runs computed by different scripts agree. One forest task (Ionosphere, seed 4, m = 9) differs by 0.2% between the stored dense-engine run and the retrained forest; reported in Appendix F.
- arxiv.org, alphaxiv.org and bls.gov are not reachable from the sandbox; references added in rounds 3-7 were read through search results only.
- A reviewer agent's full review can be recovered from its transcript when the hand-back is long (`extract_review.py` in the scratch directory did this in rounds 6 and 7); save reviews verbatim.
- Have new proofs checked by a separate agent before the reviews. In round 7 this found that the three-way gap of the address contrast is not bounded, which the draft had suggested.
- Do not invent reviewer scores, author verification, experiments or references. Every row of `Manuscript/AUTHOR_VERIFICATION.md` is "Not confirmed". Simulated reviews are not real ICML feedback.
