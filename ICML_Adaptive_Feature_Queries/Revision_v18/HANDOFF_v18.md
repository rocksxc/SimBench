# Research handoff — v18 (round 8)

Date: 2026-11-13. Paper: **The Statistical Value of Adaptive Feature Queries** (ICML 2027 target, not submitted). Current draft: `Manuscript/paper.pdf` (60 pages; main text exactly 8 pages; md5 f9c7700f27786fb1007813fc5f7dea79; this is the PDF the round-8 reviewers read, unchanged since). Source: `Manuscript/paper.tex`, `Manuscript/v18_experiments_main.tex`, `Manuscript/v18_sentences.tex` and the appendix files `a14_*.tex`, `a15_*.tex`, `a17_*.tex`, all written by hand. Every number in the text is a macro in `Manuscript/v18_numbers.tex`, generated with all tables by `Research/code/v18_tables.py` from `Research/results`. v13-v17 snapshots are unchanged (`../Revision_v13` ... `../Revision_v17`).

## Status of the user's loop
| Round | Novelty | Reviews (R1 theory / R2 statistics / R3 applied ML) | Revision |
| --- | --- | --- | --- |
| 1 | PASS | v11: 3/3/3 | -> v12 |
| 2 | PASS | v12: 3/4/4 | -> v13 |
| 3 | PASS | v13: 4/4/3 | -> v14 |
| 4 | PASS | v14: 3/3/3 | -> v15 |
| 5 | PASS, narrower claim | v15: 4/4/3 | -> v16 |
| 6 | PASS | v16: 3/3/3 | -> v17 |
| 7 | PASS | v17: 3/4/3 | -> v18 |
| 8 | PASS (ROUND_LOG_v18.md) | v18: 4/4/3 (Significance 2/3/2; Presentation 2 from all three) | paused at the round boundary for the user's report; goal not met, one point short at R3 |

## Where the loop stands
- Eight rounds: 3/3/3, 3/4/4, 4/4/3, 3/3/3, 4/4/3, 3/3/3, 3/4/3, 4/4/3. The best outcome, two 4s and one 3, has now occurred three times (rounds 3, 5, 8); three 4s has not occurred.
- R3 (applied ML) has given 3 in six of the last seven rounds, each time with the same first condition: a credible use case for the cost structure (free labels, hard per-record cap, feasible adaptivity) with data from it, and evidence beyond 12 binary features. In round 8 R3 adds that the feasible items (restructuring, separating design optimization from adaptivity) would give "a borderline 3/4, not a firm 4".
- No reviewer in rounds 5-8 found an error in a proof. New proofs were refereed by a separate agent before the reviews in rounds 7 and 8.
- Assessment (the assistant's, not a reviewer's): the theory track responded to revision (R1 3 -> 4, R2 Significance 2 -> 3). The remaining gap to the goal is not a theory gap. It needs either new evidence of the kind R3 asks for, which this project has not been able to produce from public data in the sandbox, or a paper that presents fewer results more readably (Presentation is 2 from all three reviewers). The second is feasible and is the first item below.

## Options for round 9 (full lists in Reviews/README.md)
1. Restructure the body (asked by all three; R1 and R2 make it a condition for a higher score). Three results in the body: the exact simulation with its proof and the address lower bound (half a page, R1), the population bracket with the solver, and Theorem 5. Move the polynomial-dimension round results and the details of Theorem 5(c) to the appendix; an abstract without a list of numbers; ML-facing terms next to the survey terms; one notation for kappa; one b = 4 median with the others explained; readable Table 3 headers.
2. Weak dependence (R1, R2): a quantitative version of Theorem 5(b) (explicit neighbourhood under bounded couplings or a Dobrushin-type condition), or remove the sentence that the BRFSS populations are in the benign regime of the theorem and report a dependence measure for the BRFSS fits. Say in the abstract that the pairwise value one is a first-order statement at the uniform law.
3. Misspecification (R2): pseudo-true targets and sandwich variances of the pairwise MLE per design (optimized forms, the rule's tree, the model-optimal branching design from `model_v17.ModelEngine.design`), and the model-optimal branching design in the audits. The pseudo-true law under a design q is the KL projection of the observed-data laws; it can be computed by running EM on expected counts.
4. Baselines as R2 asks: quote proper-MI coverage (0.667-0.935) and the uniform-over-the-rule's-items baseline (2.0-4.3 times) in the main text; state per-tree coverage of the cross-fitted score.
5. BRFSS at the survey-weighted law, bootstrap intervals for the per-run ratios, more trees and item sets (R2, rounds 7 and 8).
6. R3's conditions: a use case with its own data (laboratory panels or reflex testing with real per-item costs; the cost-weighted program is in Appendix E.8.3), targets of degree above b through the approximation error delta of Appendix B.2, larger m and b with certified approximate designs, an out-of-sample-validated pre-collection diagnostic. None attempted.
7. Related work named in round 8: adaptivity gaps in stochastic optimization and adaptive submodularity (Golovin & Krause; Dean, Goemans & Vondrak), batched bandits, adaptive versus non-adaptive group testing, Le Cam deficiency; responsive survey design (Groves & Heeringa), Merkouris on matrix sampling, AIPW for non-monotone MAR. None checked yet.
Small defects found by the reviewers in v18 (not fixed in the frozen PDF): Theorem 1 says the iid design "attains V/n" although V is an infimum; the bound L_k(b) >= C(b-1,k-2)/b is trivial at k = 3; the pointer-tree values "exactly 4 and 8" for fixed forms are numerical; the reference Jang, Zhu & Yu lacks initials; Li et al. 2026 still unverified.

## What changed from v17 to v18
- Exact simulation (Theorem `thm:simulation`, Appendix C.1; Theorem 2(i) in the body): an r-round protocol reproduces any branching protocol exactly, for every law, task and sample size, with a geometric number of records per branching record (mean K_r), independent of the output; n' records give Binomial(n', 1/K_r) branching records. The inequalities for V, W and the model constants are presented as its consequences, with the ranges in which each follows; the centred score remains as the explicit unbiased score for a fixed sample size.
- Model-based gap at laws with dependence (Theorem `thm:structuredfull`): (b) the polynomial bound is stable on a neighbourhood of every product law for k <= b (no explicit radius); (d) for b >= 3 there are full-support pairwise laws, on b - 1 + 3 * 2^{b-1} features (the address contrast plus a one-hot copy of the address and product indicators, tied by strong pairwise couplings), at which W^(k)_fixed / W^(k)_branch >= (1 - eps) 2^{b-1}/b for every k >= 2. The abstract, the contribution list, Section 6 and the discussion now say that a model removes the gap under weak dependence and not by parsimony alone.
- New computations: `Research/code/dependence_v18.py` (constants along the strong-coupling path at b = 3: ratio 1.00 at beta = 0 to 1.66 at beta = 6; pairwise and three-way fits of noisy address populations: pairwise ratio 1.00 at every accuracy); `Research/code/aipw_v18.py` (cross-fitted model-assisted estimator on fixed forms from the audit's own records: MSE 1.00-1.01 of the reference-table score, median coverage 0.952-0.960).
- Checks: `Research/code/theory_checks/simulation_dependence_referee/` (written by the checking agent).
- Presentation: abstract gives the tabulated pilot medians; shorter rounds sketch; larger fonts in Figure 3; leftover wording removed in Appendices B and C.

## Not completed (stated as such in the paper unless noted)
- A quantitative weak-dependence bound; the exact exponent within the order-k model; an upper bound on the address ratio for k >= 3.
- Misspecification-robust model constants; model-optimal branching in the audits (not stated in the paper as a limitation; R2 round 8).
- A round hierarchy tight beyond constant r; rounds in polynomial dimension.
- Three-way branching constants at b = 6 bracketed to 2.9%; the strong-coupling path at beta = 6 has a certified lower bound only for the branching constant.
- Forests on 20 features at b = 4; exact two-round optima at b = 6 for four BRFSS runs; label-dependent designs at b = 6 and m = 21; forest caps b = 4 at m = 9, 12 and b = 5 (unchanged).
- Survey weights; bootstrap intervals for BRFSS ratios; a second survey population; a use case with its own data; targets of degree above b.

## Pitfalls
- At most four solver processes on this four-core machine, with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1`. Start long jobs with `nohup setsid`, one result file per task, drivers that skip existing files; the container restarted once in round 7 and killed all background jobs.
- A foreground `sleep` followed by other commands is blocked by the harness; wait with a background `until ...; do sleep 15; done` command, which wakes the session when it exits (its time limit applies).
- `model_v17.rule_interview` searches exhaustively and does not finish for more than about 10 items; build known trees explicitly (`dependence_v18.address_tree`).
- `cd.Engine.solve` at strongly unbalanced laws (accuracy 0.9 and above for the address contrast) returns values up to 0.6% above the theoretical bound; the dependence table quotes the theoretical value 2^{b-1} for the design-based ratio there and does not print the solver's.
- When the main text is at the page limit, every added sentence needs a cut; measure with the text of page 9 before "Impact Statement" (see the build commands in ROUND_LOG or rerun pdflatex, bibtex, pdflatex twice).
- arxiv.org, alphaxiv.org and bls.gov are not reachable from the sandbox; references added in rounds 3-8 were read through search results only.
- Save reviews verbatim (they can be recovered from the reviewer agent's transcript). Do not invent reviewer scores, author verification, experiments or references. Every row of `Manuscript/AUTHOR_VERIFICATION.md` is "Not confirmed". Simulated reviews are not real ICML feedback.
