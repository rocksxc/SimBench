# Research handoff — v16 (round 6)

Date: 2026-11-13. Paper: **The Statistical Value of Adaptive Feature Queries** (ICML 2027 target, not submitted). Current draft: `Manuscript/paper.pdf` (56 pages; main text exactly 8 pages; this is the PDF the round-6 reviewers read, unchanged since). Source: `Manuscript/paper.tex`, `Manuscript/v16_experiments_main.tex` and `Manuscript/v16_sentences.tex`, written by hand. Every number in the text is a macro in `Manuscript/v16_numbers.tex`, generated with all tables by `Research/code/v16_tables.py` from `Research/results`. The appendix files `a14_*.tex` and `a15_*.tex` are maintained by hand. v13-v15 snapshots are unchanged (`../Revision_v13` ... `../Revision_v15`).

## Status of the user's loop
| Round | Novelty | Reviews (R1 theory / R2 statistics / R3 applied ML) | Revision |
| --- | --- | --- | --- |
| 1 | PASS | v11: 3/3/3 | -> v12 |
| 2 | PASS | v12: 3/4/4 | -> v13 |
| 3 | PASS | v13: 4/4/3 | -> v14 |
| 4 | PASS | v14: 3/3/3 | -> v15 |
| 5 | PASS, narrower claim | v15: 4/4/3 | -> v16 |
| 6 | PASS (end of ROUND_LOG_v15.md) | v16: 3/3/3 (Significance 2 from all three; Presentation 3/2/2) | paused at the round boundary for the user's report; goal not met |

## Where the loop stands
- Six rounds have produced 3/3/3, 3/4/4, 4/4/3, 3/3/3, 4/4/3, 3/3/3. No round has reached three scores of 4, and the scores do not trend upward.
- Significance has been 2 from all three reviewers in rounds 4, 5 and 6. The reason is the same each time and concerns the setting, not prior work: one known low-degree functional, tiny caps, free labels; exponential gaps only at address and pointer constructions; at most 1.98x on trained models; removed by one more round or by a two-way working model at survey sizes.
- No reviewer in rounds 5 and 6 found an error in a proof.
- Each round answered the previous round's requests, and the answers became the next round's objections. Round 5 asked for fair baselines, the charged pilot and RMSE-versus-n curves for working models. v16 supplied them, and they show that the practical value of adaptivity at survey sizes is small; R2 and R3 quote the paper's own sentence "adaptivity adds little to it".
- Assessment (the assistant's, not a reviewer's): further revisions of the same kind are unlikely to reach 4/4/4. What all three reviewers asked for in round 6, in different words, is the value of adaptivity for the estimator people would use (see below). That is a new piece of research, not an edit, and its outcome is not known in advance: it could show that the gap survives under a structured model, or that it vanishes.

## Must fix first (correctness of a claim, found by R1 in round 6 and confirmed)
The abstract says that there are targets on at most b^2 features for which a constant number of rounds still loses 2^{b(1-o(1))}, "so" a polynomially competitive protocol needs a number of rounds linear in b; Section 4 follows the 0.37b statement with "And exponential dimension is not needed"; the contribution list in the introduction joins the two in one sentence. Linear-round necessity is proved only for the single pointer tree on 2^b - 1 features. The product contrast on b^2 features (k = floor(b/beta) blocks of depth beta = floor(log2 b)) is evaluated exactly in beta rounds within the cap by reading one level of every block per round, so it shows a loss only for r = o(log b / log log b). The theorem statements (Theorem 3 and Appendix D) are correct. Rewrite the three passages so that (i) "constant r loses 2^{b(1-o(1))} on b^2 features" and (ii) "linear rounds are necessary on 2^b - 1 features" are separate statements, and add the log2 b upper bound for the product as a remark. Whether a super-logarithmic round requirement holds in polynomial dimension is open; R1 suggests a layered pointer-chasing contrast with poly(b) registers per level.

## Round-6 reviews: options for round 7 (full lists in Reviews/README.md)
Common to all three reviewers:
- The value of adaptivity under a structured model. R1 Q3: does any separation survive when the law is restricted to a k-way log-linear family? R2 Q1: EM (two-way, three-way or selected) on branching records against the same model on optimised forms, across n. R3 Q2: fixed versus branching for deployable estimators at n = 1,000-4,000. A k-way log-linear family is a finite-dimensional parametric model, so the per-design Fisher information and the efficiency bound for Delta are computable, and the design problem within a class is again c-optimal; the simulation side needs only `curve_v16.py` run on branching records. This is the one line of work that answers the top request of each reviewer.
Stated sufficient conditions:
- R2 to 4: abstract and introduction on deployable numbers, plus the EM-on-branching comparison and a pilot whose cell masses are smoothed by a low-order log-linear fit (used only for tables and probabilities, so unbiasedness is kept) at b = 5-6.
- R1 to 4: the wording fix above, plus either a tighter Theorem 3 beyond constant r (or 2^{b-r} attained or not for r = 2), or a result that explains the benign regime (instance-tight characterisation for tree-computable targets; the path-set optimum is empirically within 2-4%; or the structured-model gap).
- R3 to 4: two of {realistic ML use case with data, forests at m >= 20 and b >= 4 or scalable certified approximations, deployable finite-sample comparison} plus a restructured main body. R3 has asked for the realistic use case in rounds 4, 5 and 6; none has been found.
Cheap fixes:
- Say that "within 13-20% of the oracle" is a median of per-run ratios.
- "The constants" for small pointer trees are values at the uniform law (lower bounds on V_r); the smoothing sensitivity is in F.2, not F.1; "biased regime" should read "non-identifiable or structured regime".
- State in the limitations that for a single tree the adaptive optimum is the rule itself; that the finite-sample theorem carries a factor 104; that the forest estimand is the randomised-accuracy contrast, not thresholded accuracy.
- Verify or remove Li et al. (2026) (see `Manuscript/AUTHOR_VERIFICATION.md`).
- Presentation: full statements of Theorems 3 and 4 in the body, a protocol and estimator box, a simpler Table 3, the MCAR / sequential-CAR framing and Proposition C.7 in the main text, Appendices G and H dropped or separated (all three reviewers).
- Related work R2 lists: Adiguzel & Wedel 2008; responsive and adaptive survey design; randomised monotone missingness (Robins-Gill); limits of adaptive sensing (Arias-Castro, Candes & Davenport). None of these has been checked yet.

## What changed from v15 to v16
- Framing. Abstract and introduction lead with the finding on trained models (1.0-1.98x; one round recovers at least 80% where the optimum was computed and at least 59% by certified bounds elsewhere) and present 2^{b-1} as the worst-case envelope. The paper states that at survey sizes a parsimonious working model on optimised forms is the more accurate tool.
- Theory. Proposition `prop:labelnoise`: for a +-1 rule whose label equals the rule flipped independently with probability 1-p, the address contrast has W_fixed/W_branch = 2^{b-1} at every p, and the pointer-tree round bounds hold at every p (checked with the solver at b = 2, 3). Remark: the every-population bound holds for several contrasts served by one design. "Sharp" for K_{m,b} is qualified; Theorem 1 is slimmed (finite-sample version in Appendix B); relation to locally bounded adaptivity (Adar & Fischer 2024) and restricted-focus-of-attention learning stated; Gonzalez & Eltinge 2008 cited.
- Experiments (new scripts `Research/code/*_v16.py`): naive designs with optimal scores (uniform over path sets, uniform over item subsets); the pilot charged with cross-fitted scores (all-in price); RMSE of two- and three-way working models against the design-based score for twelve BRFSS trees at seven audit sizes; reuse of one rule's design for another rule and joint designs for two and three rules. Numbers are in ROUND_LOG_v16.md.
- Counts. 21-item trees are no longer counted among the runs with a gain; the two-round claim is split into computable / solved / bounded runs.

## Not completed (stated as such in the paper unless noted)
- A round hierarchy tight up to poly(b) (open).
- A model-assisted design-unbiased score with estimated tables (not implemented; the appendix argues it cannot beat oracle tables, which R2 accepts and R3 still asks for at finite n).
- Exact two-round optima at b = 6 for four BRFSS runs (certified brackets only), label-dependent designs at b = 6 and m = 21, forest caps b = 4 at m = 9, 12 and all of b = 5, 21 items at b = 5 (all unchanged from v15).
- A second survey population with a gap above one; split-sample intervals for the screening ratios; survey weights (R2).
- Not stated in the paper: the wording error above.

## Pitfalls
- At most four solver processes on this four-core machine, with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1`. Background jobs are killed after two hours; split long computations and write results per task.
- `pgrep -f pattern` inside a `bash -c` wrapper matches the wrapper; use a bracket in the pattern.
- `v16_tables.py` asserts that runs computed by different scripts agree. One forest task (Ionosphere, seed 4, m = 9) differs by 0.2% between the stored dense-engine run and the retrained forest; reported in Appendix F.
- arxiv.org and bls.gov are not reachable from the sandbox; abstracts of references added in rounds 3-6 were read through search results only.
- A reviewer agent's full review can be recovered from its transcript when the hand-back is long; save reviews verbatim.
- Do not invent reviewer scores, author verification, experiments or references. Every row of `Manuscript/AUTHOR_VERIFICATION.md` is "Not confirmed". Simulated reviews are not real ICML feedback.
