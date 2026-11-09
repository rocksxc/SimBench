# v14 revision loop — round log (continues ROUND_LOG_v13.md)

## Round 4 — novelty gate (web search, 2026-11-09)
Searches (standard and extended): within-record vs across-record interactivity in local differential privacy (Joseph, Mao, Neel & Roth, FOCS 2019; Joseph, Mao & Roth, SODA 2020, pp. 515-527, pointer chasing for round separations); interactive inference under information constraints (Acharya, Canonne, Liu, Sun & Tyagi, IEEE Trans. IT 68(1):502-516, 2022); restricted-focus-of-attention learning (Ben-David & Dichterman, JCSS 1998); learning with partially observed attributes (Cesa-Bianchi, Shalev-Shwartz & Shamir, JMLR 2011); budgeted learning (Lizotte, Madani & Greiner, UAI 2003; Kapoor & Greiner, ECML 2005); adaptivity gaps for stochastic Boolean function evaluation (Hellerstein, Kletenik, Liu & Witter, arXiv 2208.03810); adaptivity in 1-bit mean estimation (Lau & Scarlett, AISTATS 2026; non-adaptive matching results in 2026 preprints); AFA policy evaluation (von Kleist et al., JMLR 2025; an Oct-2026 arXiv paper on AFA evaluation with tabular foundation models could not be confirmed by a second search and is not cited); planned-missing vs branching questionnaires under a per-respondent limit; ML audit sampling under model updates.
Closest new items and why they do not cover our question: the LDP separations compare interaction across users/rounds of noisy randomizers and count samples up to constant or logarithmic factors; here observations are noiseless coordinate reads, adaptivity is within one record under a hard per-record cap, the constants are exact, and across-record adaptation provably does not change the first-order constant. 1-bit mean estimation studies adaptivity across samples for a scalar mean. RFA / partially observed attributes / budgeted learning fit predictors, not population functionals, and do not compare protocol classes at their optima. **Verdict: PASS.** (arxiv.org is not reachable from this sandbox; checks used search snippets and mirrors.)

## Round 4 — pre-specified shift experiment (recorded before any result was seen)
Shifts for the imputation-versus-design comparison on BRFSS (variables outside the 12 model items): sex (female source, male target; as in v12/v13); education (college graduates -> no education beyond high school); cost barrier (no cost barrier to a doctor visit -> cost barrier); physical-health burden (no poor physical-health days -> 14 or more days). Caps b = 4, 5; seed 20261108; n = 1000 per audit; 400 replications; estimators branching, fitted fixed form, regression imputation, proper MI. All four shifts are reported whatever the outcome.

## Round 3 -> v14 revision (addresses Reviews/round3_v13_*.md)
Self-containment (all three reviewers): every appendix passage that relied on experiments not described in the paper (SUSHI/SAPA, "ten binary tasks", "70 controlled tree tasks", "eight-feature", "larger-tree", "v12", "earlier release", "separate supplementary report") was removed or rewritten; the full list of edits is in `tools/restructure_appendix.py`. The order-effect and cost-regime results were recomputed on the paper's own BRFSS/thyroid trees. The appendix is regrouped into nine lettered sections (A guide/notation/worked example; B Theorem 1; C sharp gap; D rounds; E population constants and computation; F experimental details; G higher-degree contrasts and proper scores; H PISA archive; I reproducibility) with section-scoped theorem numbers.
Presentation (all three): abstract states the regime (labels always observed, one known low-degree contrast, no trusted complete reference) and the worst-case qualification, and drops the 25x path-guessing headline; constants table and worked example in Section 2; "binding" defined; tighter rounds statement ("for every fixed r ... tight up to polynomial factors"); held-out sizes, profile counts and the meaning of the old leaf-size parameter stated; "model-assisted" renamed regression imputation; the "default choices" table removed.
Theory (R1, R2): Proposition (optimized path-set design) tightens the upper end of the bracket and is computable from reference marginals; the Fourier-restricted solver (Appendix E) prices every r-round class exactly by dynamic programming over partial assignments, certifies with dual witnesses and the Jensen bound, and never enumerates the 2^m profiles; exact round constants of the binary pointer tree at b = 3, 4 (lower bound M_r(U), upper bound from the worst profile of the uniform-optimal design).
Related work (R1): LDP interactivity (Joseph et al. 2019; Joseph, Mao & Roth 2020), interactive inference (Acharya et al. 2022 TIT), 1-bit mean estimation (Lau & Scarlett 2026), budgeted learning (Lizotte, Madani & Greiner 2003; Kapoor & Greiner 2005), with a precise statement of what is new.
Experiments (R1, R2, R3): see the results section below.

## Round 4 — experiment results at the v14 freeze (all on the new solver unless noted)
- Forest cap grid: b=2 (45 tasks, median 1.31), b=3 (180, 1.51; dense v12 engine), b=4 at m=6 (15, 1.24); b=4 at m=9,12 and b=5 NOT completed (the forest branching column generation remained too slow on 4 cores; marked -- in Table 2).
- BRFSS screening b=4: best fixed 1.49, fitted 1.57, exact two-round 1.00 (median), heuristic two-round 1.14, lower 1.18, path-set 1.53, N_P 3.6.
- BRFSS screening b=5: best fixed 1.35, fitted 1.42, exact two-round 1.00 (median), heuristic two-round 1.21, lower 1.08, path-set 1.36, N_P 5.9.
- BRFSS screening b=6: best fixed 1.58, fitted 1.68, exact two-round 1.00 (computed for 1 of the 6 BRFSS b=6 runs only), heuristic two-round 1.39, lower 1.13, path-set 1.61, N_P 11.4.
- Two rounds recover a median 100% of the log-gap and at least 90% in each of the 13 BRFSS runs with a gain; thyroid trees: every ratio 1 (Gamma_P = 1).
- Optimized path-set upper end (Proposition prop:uppermain): median 2.0% above the best fixed design (max 3.9%) over 21 runs with a gain; completion-only N_P overstates by a median factor 4.3.
- Position effects (last answer flips w.p. 0.1): BRFSS median bias 1.54 (branching) vs 2.17 (fitted form) clean branching SEs at n=1000; branching keeps the smaller RMSE in 24/24 BRFSS runs.
  - shift iid_b4: regression-imputation bias 0.15 SD, coverage reg 0.955 / MI 0.993 / branching 0.955 / fixed 0.965; RMSE ratio to branching reg 0.89.
  - shift iid_b5: regression-imputation bias 0.02 SD, coverage reg 0.958 / MI 0.975 / branching 0.950 / fixed 0.955; RMSE ratio to branching reg 0.91.
  - shift sex_b4: regression-imputation bias 0.10 SD, coverage reg 0.940 / MI 0.955 / branching 0.953 / fixed 0.948; RMSE ratio to branching reg 0.99.
  - shift sex_b5: regression-imputation bias 0.16 SD, coverage reg 0.948 / MI 0.983 / branching 0.965 / fixed 0.938; RMSE ratio to branching reg 0.98.
  - shift education_b4: regression-imputation bias 0.77 SD, coverage reg 0.863 / MI 0.920 / branching 0.948 / fixed 0.960; RMSE ratio to branching reg 1.18.
  - shift education_b5: regression-imputation bias 0.54 SD, coverage reg 0.902 / MI 0.935 / branching 0.950 / fixed 0.953; RMSE ratio to branching reg 1.09.
  - shift costbar_b4: regression-imputation bias 0.12 SD, coverage reg 0.930 / MI 0.980 / branching 0.945 / fixed 0.943; RMSE ratio to branching reg 0.88.
  - shift costbar_b5: regression-imputation bias 0.23 SD, coverage reg 0.925 / MI 0.960 / branching 0.935 / fixed 0.938; RMSE ratio to branching reg 0.94.
  - shift physhlth_b4: regression-imputation bias 0.21 SD, coverage reg 0.960 / MI 0.965 / branching 0.950 / fixed 0.950; RMSE ratio to branching reg 1.01.
  - shift physhlth_b5: regression-imputation bias 1.73 SD, coverage reg 0.515 / MI 0.667 / branching 0.945 / fixed 0.940; RMSE ratio to branching reg 1.97.
- Binary pointer tree b=3: M1 4.000, M2 1.8000 (upper 1.8000), M3 1.0000000002001839, branching 1. b=5 (m=31) not completed.
- Binary pointer tree b=4: M1 8.000, M2 3.3241 (upper 3.3341), M3 1.8000000000137797, branching 1. b=5 (m=31) not completed.
- 21 BRFSS items b=3: best fixed 1.00 (max 1.00), fitted 1.00, path-set 1.00, lower 1.00; 0.0 min per certified solve. b=5 and two-round at m=21 not completed.
- 21 BRFSS items b=4: best fixed 1.46 (max 1.55), fitted 1.54, path-set 1.50, lower 1.17; 6.1 min per certified solve. b=5 and two-round at m=21 not completed.
- Engine incidents fixed during the round (all affected results deleted and recomputed): solver tolerance 1e-8 gave suboptimal masters (restored 1e-10; consistency check fixed <= path-set and fitted); initializing the certificate with the Jensen bound had disabled Wentges smoothing (anchor and certificate separated); column pruning made column generation cycle (disabled); a placeholder branch wrote round ratios 1.0 for b=6 runs without round optimization (removed by Research/code/fix_b6_placeholders.py); the dense feasibility repair at every iteration was the bottleneck (moved to the final design).

## Round 4 — simulated reviews of v14 (2026-11-09; full texts in Reviews/round4_v14_*.md)
Packet: `paper.pdf` (48 pages) as cleaned text plus page images; three fresh independent agents (theory, statistics, applied ML) with the same prompt template as rounds 2-3. R1 and R2 were interrupted by a container restart and resumed from their saved transcripts; R3 ran uninterrupted.

| Reviewer | Overall | Confidence | Soundness | Presentation | Significance | Originality |
| --- | --- | --- | --- | --- | --- | --- |
| R1 theory | 3 (Weak reject) | 4 | 3 | 2 | 2 | 3 |
| R2 statistics | 3 (Weak reject) | 4 | 3 | 3 | 2 | 3 |
| R3 applied ML | 3 (Weak reject) | 4 | 3 | 2 | 2 | 3 |

Goal (all three >= 4) not met; the scores fell from 4/4/3 (v13) to 3/3/3. All three reviewers checked several proofs and found them correct. The scores fell on significance (2 from all three, previously 3) and on traceability and editing defects introduced in v14:
- the untraceable 1.98 maximum;
- unreported b=5 forest runs;
- a truncated sentence moved from D.1 to the start of Appendix E;
- a stray "APP" and duplicated sentence in D.4;
- stale statements contradicting the new round results;
- Table 7 vs Tables 9/10 computed on different trees without saying so.

Root causes are listed in HANDOFF_v14.md. New substantive requests:
- **R1:** a centered per-population upper end, W_fixed(P) <= K W_branch(P) at every P.
- **R2:** label-dependent and stratified fixed designs; within-sample imputation and AIPW comparators; positioning against c-optimal and two-phase AIPW design.
- **R3:** a realistic end-to-end case study; finite-sample forest audits with deployable baselines; an empirical check of Proposition 6.

At the user's request the loop is paused after this round; no round-5 novelty check or revision has been started.
