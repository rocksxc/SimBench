# Round 7 — simulated review R3 (applied ML evaluation) of v17 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 3 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words)

The paper studies evaluation of a frozen predictor when each sampled record may reveal at most b of m binary features (labels are assumed observed for every record and costed separately). The estimand is a known functional Δ(P) = E[Y d(X)], with d of Fourier degree ≤ b: for example the accuracy of a depth-b screening tree, or the difference in predicted probabilities of two depth-b forests. The question is how many more records are needed if each record's feature set is fixed in advance ("fixed forms") than if questions are chosen adaptively within the record ("branching"), with r-round batch protocols in between.

- **Characterization (Thm 1).** The first-order minimax constant for any finite menu of interviews is a convex program with an explicit dual. Adaptivity across records does not change the constant.
- **Worst-case gap (Thm 2).** Fixed forms need at most K = min{2^(b-1), C(m-1, b-1)} times the records of branching, at every population. The upper bound is a "path guessing" simulation; an address (indexing) function attains it, at every accuracy level of the rule.
- **Rounds (Thm 3).** r rounds lose at most 2^(b-r); pointer-tree constructions give near-matching lower bounds.
- **Per-population bracket (Thm 4).** The records ratio lies between 1/ρ² (the inverse of the best single-form R²) and a Rényi-1/2 effective number of paths.
- **Models (Thm 5).** Under a log-linear model with interactions of order ≤ k, the gap is at most (b+1)^k at uniform product laws. For the extremal address contrast it is exactly 1 under the pairwise model.
- **Computation.** A column-generation solver with dynamic-programming pricing computes certified optimal designs for each protocol class.
- **Experiments.** On BRFSS and thyroid screening trees (12 binary items, b ≤ 6) and small forest updates (m ≤ 12, b ≤ 4):
  - oracle-optimized fixed forms need 1.0–1.98× the records of branching without a model;
  - a second round removes most of that gap;
  - under a fitted pairwise model the ratio is 1.02–1.13;
  - simulated audits reproduce these orders of magnitude and show the bias a pairwise working model incurs at large n.

**Strengths**

1. **A cleanly posed and, to my knowledge, new quantitative question.** The qualitative adaptive/non-adaptive separation is classical, which the paper says plainly. The exact variance-level price, its validity at every population, the round-by-round interpolation, and its collapse under low-order models are not in the active-testing, PPI, AFA-evaluation or planned-missingness literatures I know.
2. **The parts of the theory I checked hold up and are elegant.** I verified:
   - the path-guessing simulation (C.1.1–C.1.2);
   - the address-contrast energy computation (C.1.3);
   - the centred simulation, witness bound and bracket (Thm E.1 a–d);
   - Prop E.3 (the gap persists at every accuracy);
   - the two-point finite-sample converse arithmetic (B.3.2);
   - the structure of the local-minimax argument (Prop C.7).

   The centring trick (return c + K(H − c)) that makes the 2^(b-1) bound hold for the variance at every population is a real point, not a formality.
3. **Unusual candour about what the results mean.** The paper itself reports:
   - the Thm 4 bracket is loose on real data (1.31× below, 4.3× above);
   - the gap is exactly 1.00 on thyroid and on BRFSS trees using ≤ b items;
   - oracle designs are not deployable, and pilot-learned designs cost materially more (up to 4.33× unsmoothed at b = 6);
   - a pairwise model has non-vanishing bias and under-covers at large n;
   - a design optimized for one rule can be nearly useless for another (1.55–317×).

   The limitations section is one of the most honest I have seen.
4. **A useful robustness property for practice.** Pointwise unbiasedness regardless of the reference law used to tune the design means a wrong reference or pilot costs only variance, never validity.
5. **Certified computation.** Primal and dual bounds to 1e-4, cross-checked against an independent dense implementation. Intervals are reported where the solver did not close.
6. **Thm 5 is the most interesting message for an applied reader.** The exponential value of adaptivity is a statement about interactions whose order grows with the cap. With parsimonious structure, pre-commitment costs little. The simulated audits support this (pairwise ML on forms ≈ design-based mean under branching, 0.91–1.10).

**Weaknesses**

1. **[major] The setting is narrow and somewhat inverted relative to ML evaluation practice, and the motivating use case is thin.** Three assumptions must hold together:
   - labels are free and observed on every record;
   - features are hard-capped per record at a very small b (≤ 6 binary questions);
   - the target is a single known functional of Fourier degree ≤ b.

   This is the reverse of the cost structure in active testing, PPI and active statistical inference, and the paper offers no concrete ML deployment where all three hold. The 12 yes/no BRFSS items with a cap of 4–6 are a stylized stand-in, not a real burden constraint. For the headline use case (a single screening tree), the adaptive optimum is "administer the rule and average correctness". If skip logic is available one simply uses it; if it is not, the constant does not change what one does. The only actionable output is then the optimized form design, which is c-optimal design, as the paper acknowledges. The appendix further shows the gap needs a hard cap (under a mean budget the ratio is ≤ m/b), and that complete records undercut fixed forms once a label costs more than roughly 4–15 feature questions. Both narrow the regime where the headline constants matter.

2. **[major] The identifiability restriction (deg d ≤ b) excludes most models an ML audience would want to audit.** Only depth-≤ b trees and probability averages of them qualify. Thresholded ensembles, boosted trees with more than b distinct features on a path, logistic models on more than b features, and neural rules are out. For forests the estimand is the difference of predicted probabilities (accuracy of a randomized rule), not the accuracy of the deployed thresholded classifier. The appendix has a bias-plus-variance program (B.1) that could handle approximate identification, but it is never evaluated, and its finite-sample guarantee carries a factor of 104. As written, the framework says "not identifiable" for the typical ML model at small caps.

3. **[major] The empirical effect sizes are small, and the scale is toy.**
   - Without a model the oracle price of pre-commitment is at most 1.98× (medians 1.35–1.58). Under a pairwise model it is 1.02–1.13. One extra round reduces it to ≤ 1.05–1.09.
   - The exponential separations occur only on constructed address/pointer functions with m exponential in b (or products of them).
   - Experiments stop at m = 12 binarized features. At m = 20–21 only fixed forms (and b = 3 branching) are solved; four two-round programs at b = 6 did not close; b = 4 forests are completed only for m = 6.
   - Features are median-binarized, and forms are item-level rather than the block/module structure of real split questionnaires.
   - Screening results rest on six runs per cap (two targets × three seeds), reported as medians.

   The honest take-home, that pre-commitment costs less than 2× and almost nothing with a pairwise model, is a legitimate finding. It also means the practical stakes of the main theorems are modest on every real dataset shown.

4. **[major] Presentation is very dense for an ML venue; the main body is not self-contained.** Eight pages carry five multi-part theorems, a solver, a model-based theory, and four experimental studies, backed by a 45-page appendix.
   - The abstract and Section 7 are largely strings of numbers.
   - Table 2 needs a nine-line caption.
   - Many symbols (V, W, M, Φ_n, K, ρ², N_P, W^(k), W^T, W_PS, W^lab) are introduced within a few pages.
   - Key qualifiers appear in passing: ratios are between oracle designs, each tuned to P, in a local-asymptotic sense.
   - Some headline numbers are hard to trace. The abstract's "1.33–2.40 when the design is learned from a pilot" does not appear in Section 7 or in Tables 13–14, which report medians of 1.50–1.93 smoothed and up to 4.33 unsmoothed. The oracle value at b = 4 is 1.49 in Table 2 but 1.52 in the pilot paragraph, because the run subsets differ.

   The paper reads as a compressed statistics or theory journal article. The rounds results (Thm 3) in particular add little for the applied message, and their space would be better spent on explaining the experiments.

5. **[major] The deployable procedure is underdeveloped relative to the oracle constants.** W_fixed(P) requires P-specific cell masses, up to 1,728 cells at b = 6.
   - The only finite-sample route offered is a one-shot quarter-sample pilot with ad hoc choices (10% or 1% uniform mixing, 5% floor, pairwise EM smoothing, path-set menu only), and no non-asymptotic guarantee.
   - Sequentially updated designs across records are the natural strong baseline here (Neyman-allocation style, as in Hahn et al. or active statistical inference). They are not tried, even though the theory explicitly allows across-record adaptation.
   - The practitioner is left without guidance on choosing between the design-based score and pairwise ML. The paper shows the model wins at n ≤ 2,000 and loses for 3–5 of 12 trees at 16–32k, and concedes that "which trees these are cannot be read from the capped records".

6. **[minor] Simulated audits are resamples with replacement from the same smoothed empirical law used to compute the constants.** They validate the asymptotics but are not independent evidence. There is no real planned-missingness dataset (rotated booklets, NHANES-style matrix sampling) and no real budgeted-classifier log. BRFSS survey weights are ignored.

7. **[minor] Technical novelty of the ingredients is moderate.** Minimax duality for linear functionals, van Trees, c-optimal design/Elfving and AIPW under known coarsening are standard, as the paper acknowledges. The upper bound is a short simulation and the lower-bound instance is the classical indexing function. The contribution is the exact comparison across menus and the model-based collapse.

8. **[minor] A large body of appendix material cannot realistically be verified in review.** This includes Thm 3(b,c) (potential argument and products), Thm 5(b,c), the 4-feature example, and the hybrid-budget curve. Appendix H discloses that a generative language model took part in deriving and checking proofs and in drafting. That is permitted, and the authors list extensive numerical cross-checks, but it raises the importance of independent verification of the parts I did not check.

9. **[minor] The order-effects assumption is consequential for the very comparison studied.** Branching and fixed forms ask in different orders and modes. It is handled only by an illustrative flip model, which shows biases of 1.5–2.2 standard errors at n = 1,000.

**Soundness**: 3 — The proofs I spot-checked (Thm 2, Thm E.1, Prop E.3, B.3.2, Prop C.7 structure) are correct and the computed constants are certified. Remaining caveats are that the constants are oracle/local-asymptotic, the run counts are small, and I did not verify Thm 3(b,c) or Thm 5(b,c).

**Presentation**: 2 — Precise and honest, but over-compressed and number-heavy, with some untraceable headline figures; an ML reader cannot follow the experiments without the appendix.

**Significance**: 2 — A nice characterization for a niche regime (free labels, hard small per-record feature cap, degree-≤ b targets), where real-data gaps are below 2× and nearly vanish under a pairwise model; limited direct impact on ML evaluation practice.

**Originality**: 3 — The question and the exact cross-menu comparison (including rounds and the model-based collapse) are new; the tools and extremal instances are classical.

**Key Questions for Authors**

1. **Concrete use case.** Can you give one real scenario where (i) labels are available for all records, (ii) a hard per-record cap at small b binds, (iii) branching is infeasible or costly, and (iv) the target is a degree-≤ b functional — and say what decision the constants change there? A convincing end-to-end case, ideally on real planned-missing or budgeted-acquisition data, would raise my significance score and likely my recommendation.
2. **Non-identifiable targets.** What does the framework deliver for thresholded forests, GBDTs, or logistic models whose degree exceeds b? Can program (B.1), with its approximation residual, give useful fixed-vs-branching prices, and can you show one experiment? A positive answer would substantially broaden the relevance (significance 2 → 3).
3. **Scale and structure.** Can the solver, or the path-set relaxation, handle m ≈ 30–100, multi-category items, and block-structured forms, even with certified intervals rather than exact optima? Evidence at realistic questionnaire or feature-set sizes would address weakness 3.
4. **Learning the design.** Why a one-shot 25% pilot rather than sequential updating of form probabilities across records? What is the all-in price for a sequential scheme at N = 4,000 and b = 6? Relatedly, is there a diagnostic or a doubly robust/model-assisted estimator that gets the small-n gains of pairwise ML without its large-n bias? A principled, deployable recipe would move soundness and significance up.
5. **Traceability and uncertainty.** Where does "1.33–2.40" in the abstract come from? Can you report run-to-run uncertainty for the six-run medians in Table 2? This affects presentation only, but I would want it fixed.

**Limitations**

Yes. Section 9 and the appendix discuss the main limitations explicitly and candidly: single known target, free labels, order effects, oracle/asymptotic meaning of the constants, model bias, ignored survey weights, and solver scale. I would add two statements to the main text:
- an explicit note that the estimand for ensembles is not the accuracy of the thresholded classifier;
- an explicit note that the simulated audits resample the same law on which the constants were computed.

**Overall Recommendation**: 3 — Weak reject

This is a borderline case. The paper is technically solid, honest and original in its question, and I would not argue against acceptance if the theory reviewers confirm the unverified parts and value the exact constants highly. From an applied evaluation perspective, the weaknesses currently outweigh the merits for ICML: a narrow and weakly motivated regime, the degree-≤ b restriction, small and toy-scale empirical effects, an underdeveloped deployable procedure, and an over-compressed presentation.

**Confidence**: 3

I am confident about the setting, the experiments and their relation to the evaluation and missing-data literature. I checked the central proofs but not the rounds lower bounds, the model-based bounds, or the solver's correctness in detail.

**What would move you up one point**

- A realistic end-to-end demonstration: real planned-missing or budgeted-acquisition data, or at least m ≥ 30 with block forms and non-binarized items, where the constants or optimized designs change a concrete design decision.
- An evaluated extension to non-identifiable targets (thresholded ensembles or higher-degree models) via the bias-plus-variance program, so the framework applies to models that ML practitioners actually deploy.
- A deployable design-learning procedure with a sequential baseline and a finite-sample statement, plus actionable guidance or a diagnostic for choosing between design-based and pairwise-model analysis.
- A restructured main body: move Thm 3 details to the appendix, state the oracle/local-asymptotic qualifiers up front, make every abstract number traceable to a table, and give the experiments a readable narrative.

The first two would be the most persuasive. The last alone would not change my score, but together with any one of the first three it would move me to a 4.

**Files read**: only the prompt, `paper_clean.txt` and page images in `/tmp/claude-0/-home-user-SimBench/3b198ae7-bda9-5880-b22e-39bc53bf11f2/scratchpad/review_v17/` (plus my own tool-output dump of Appendix F prose); no web search, no files modified.
