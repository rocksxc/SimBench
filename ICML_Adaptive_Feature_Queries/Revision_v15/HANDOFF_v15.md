# Research handoff — v15 (round 5)

Date: 2026-11-12. Paper: **The Statistical Value of Adaptive Feature Queries** (ICML 2027 target, not submitted). Current draft: `Manuscript/paper.pdf` (main text exactly 8 pages; impact statement and references from page 9; lettered appendix A-I). Source: `Manuscript/paper.tex` and `Manuscript/v15_experiments_main.tex`, written by hand. Every number in the text is a macro in `Manuscript/v15_numbers.tex`, generated with all tables by `Research/code/v15_tables.py` from `Research/results`; result-dependent sentences are in `Manuscript/v15_sentences.tex`. There are no `XX` placeholders and no fill script any more. The appendix files `a14_*.tex` and `a15_*.tex` are maintained by hand (do not rerun `tools/restructure_appendix.py`). v11-v14 snapshots are unchanged (`../Revision_v14`, `../Revision_v13`).

## Status of the user's loop
| Round | Novelty | Reviews | Revision |
| --- | --- | --- | --- |
| 1 | PASS | v11: 3/3/3 | -> v12 |
| 2 | PASS | v12: 3/4/4 | -> v13 |
| 3 | PASS | v13: 4/4/3 | -> v14 |
| 4 | PASS | v14: 3/3/3 | -> v15 |
| 5 | PASS with a narrower novelty claim (see ROUND_LOG_v15.md) | v15: 4/4/3 (R1 4, R2 4, R3 3, self-described borderline 3/4; Significance 2 and Presentation 3 from all three) | paused at the round boundary for the user's report; goal not met |

## Round-5 reviews: what to do in round 6 (see Reviews/README.md for the full lists)
Cheap, and asked for by at least two reviewers:
- Replace the uniform-over-all-forms headline by fair naive baselines: uniform over the tree's path sets, and uniform over forms inside the items the rule uses, each with optimal scores (`screening_v15.fixed_given_q` already computes optimal scores for a given form distribution; the path-set uniform design is `E.solve(psf, beta=1.0)`). Reword the abstract.
- Charge the pilot: report total records (pilot plus main) for a target precision, with the pilot's unbiased scores pooled (`pilot_v15.py` already computes the pilot design's own variance as `pilot_design`).
- Fix the count inconsistencies: "three 21-item trees" versus six 21-item runs; the 21-item runs counted among the "21 runs with a gain" although they duplicate R0-R2; "every experiment is in Appendix F" versus G.1.1 and H; "at least 80% in every case solved to optimality" (state it per class, with the b = 6 brackets next to it).
- Qualify "sharp" for K_{m,b} (tight only for m >= b - 1 + 2^{b-1}) and the "records needed" reading of W (oracle designs; local asymptotics with the cube fixed).
- R1 Q1, probably easy from Theorem E.1(b)-(c): the address contrast with Y = d(X) with probability p > 1/2. Compute rho_P^2 there and state that the ratio stays of order 2^{b-1} at accurate populations (check numerically with the solver at b = 2, 3 first).
Larger:
- A model-assisted comparator: working-model augmentation inside a cross-fitted pointwise-unbiased score, at n = 1000 and 16,000 (R2), and RMSE-versus-n curves for two- and three-way models over all seeds (R3).
- Split-sample intervals for the ratios; a second real survey population with a gap above one.
- A realistic end-to-end case (R3's condition for moving up; two rounds of reviews have asked for it).
- A tighter round hierarchy (R1's condition for 5; open).
Risk for the round-6 novelty gate: unchanged from round 5. The reviewers accept the novelty of the class comparison and of the round hierarchy; the standing objection is significance (narrow regime, small realized gaps), which a revision can clarify but not remove.

## What changed from v14 to v15
- Theory. (i) The gap holds at every population: W_fixed(P) <= K_{m,b} W_branch(P) and W_r(P) <= 2^{b-r} W_branch(P), by simulating the centered score (Theorem E.1(a); main Theorems 2(ii), 3(a)). (ii) The population bracket is now on the records scale at both ends: 1/rho_P^2 <= W_fixed/W_branch <= N_P <= K, with centered weights; the centered lower end dominates the old one. (iii) New potential for the pointer tree, Q = M + 2^L pi, which is multiplicative across blocks: V_r >= 2^{b-1}/(1+2b/r)^r for the single tree, a product construction on m <= b^2 coordinates with log2 V_r >= b - O(r b loglog b / log b), and the consequence that polynomially competitive protocols need r >= 0.37 b - O(log b) rounds. (iv) Label-dependent designs (Proposition E.2): V unchanged, the program decouples over labels, the gap bound still holds.
- Positioning. The population program for one menu is stated to be c-optimal design with an Elfving-type dual, its score the efficient AIPW estimator under known coarsening, column generation a vertex-direction method; the across-record statement is related to "adaption does not help" in information-based complexity; two-phase designs are described as two-round interviews under an expected budget. New references are listed in `Manuscript/AUTHOR_VERIFICATION.md` (all "Not confirmed").
- Experiments (all new scripts are `Research/code/*_v15.py`).
  - Label-dependent and sex-stratified fixed designs on the screening runs at b <= 5.
  - Balanced random forms (uniform over all forms) with Horvitz-Thompson and with optimal scores.
  - Fitted two-round designs.
  - Exact two- and three-round designs for 60 forest tasks.
  - Designs learned from a pilot of the audit (empirical check of the self-calibration proposition).
  - A log-linear working model fitted by EM to the capped records, at n = 1000 and n = 16,000.
  - An enumeration that decides which trees are two-round computable.
  - Certified upper bounds for two-round designs at b = 6.
- Defects of v14 fixed: untraceable 1.98 (now the per-run Table `tab:runs` and a [min, max] column); truncated sentence and misplaced fragment (D.1/E); stray "APP" and duplicated sentence (D.4); stale statements that contradicted the round results; b = 5 forest runs mentioned but not run; the mixed "fitted" column of the forest table; "delta^2 + Theta(1/n)"; the "conservative for forests" claim; two imputation tables merged into one.

## Corrections to earlier notes
- HANDOFF_v14.md said that the shift study (old Tables 9/10) used different trees from Table 7. That was wrong. The simulated audits use the seed-0 trees of the screening study (runs R0 and S0 of `tab:runs`); Table 7 reported medians over three seeds, and the S0 tree at b = 4 has an exact records ratio of 1.000. The diagnostic script that supported the wrong reading was removed.
- v14 reported "two rounds recover 100% at b = 6" from the single run that had finished. That run is the only b = 6 tree that a two-round interview computes exactly. The other five are not two-round computable, so their ratio exceeds one; v15 reports certified upper bounds for them (R0: at most 1.32).

## Not completed in round 5 (stated as such in the paper)
- Exact two-round optima at b = 6 for four of six BRFSS runs. The exact job (`screening_v14.py --max_round 2`) was started with four workers while six other jobs were running, made little progress and was stopped by the two-hour limit of the session's background jobs; it was not restarted. Instead `Research/code/two_round_computable_v15.py` decides by enumeration which trees a two-round interview computes exactly (ratio exactly one; agrees with the solver on all 43 runs that have both), and `Research/code/two_round_b6_v15.py <data> <out> <iid|shift> <seed> <seconds>` runs column generation for one tree with a wall-clock budget and reports the certified bracket reached. With 60 minutes per tree on a free core: S0 computable (1.000), S1 closed at 1.013, R2 in [1.012, 1.031], R1 at most 1.063, S2 at most 1.109, R0 at most 1.320 (the last three have only the trivial lower bound one). A longer budget would tighten these; the script does not save its interviews, so a rerun starts from scratch.
- Label-dependent designs at b = 6 and at m = 21 (each needs several all-forms programs with 59,136 cells per label).
- Forest caps: b = 4 for m = 9, 12 and all of b = 5 (unchanged from v14); binary pointer tree at b = 5; 21 items at b = 5.

## Pitfalls
- Do not run more than four solver processes at once on this four-core machine, and set `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1`. In round 5 ten concurrent processes ran at 30-50% CPU each and a two-hour job was lost.
- Background jobs in this environment are killed after two hours. Split long computations into jobs that fit, and write results per task.
- `pgrep -f pattern` inside a `bash -c` wrapper matches the wrapper itself; use a bracket in the pattern (`screening_v15[.]py`).
- `v15_tables.py` asserts that runs computed by different scripts agree (fixed ratios, Delta, two-round computability against the solver). One forest task (Ionosphere, seed 4, m = 9) differs by 0.2% between the stored dense-engine run and the retrained forest; this is reported in Appendix F.
- Solver settings as in v14: Clarabel tolerance 1e-10, Wentges anchor separate from the Jensen certificate, no column pruning, exact repair only for the final design.
- arxiv.org is not reachable from the sandbox; abstracts of the new references were read through search results only.
- Do not invent reviewer scores, author verification, experiments or references. `Manuscript/AUTHOR_VERIFICATION.md` has v15 rows, all "Not confirmed". Simulated reviews are not real ICML feedback.
