# Round 5 — simulated review R3 (applied ML evaluation) of v15 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject; the reviewer calls it a borderline 3/4)** — Confidence 3 — Soundness 3 / Presentation 3 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-12; not real ICML feedback. Full text as returned.)

**Summary** (in my own words)

The paper studies how to estimate one known population functional — the accuracy (or accuracy difference) of frozen predictors, Δ(P) = E[Y d(X)] — when every sampled record reveals its label for free but at most b of m binary features. It compares three ways of choosing those b features:

- **Fixed forms:** the subset is drawn before seeing the record.
- **r-round interviews:** r batches, each chosen from earlier answers.
- **Branching:** a depth-b decision tree of questions.

The currency is the number of records needed by a design-unbiased estimator. The main results are:

1. **Theorem 1.** The first-order minimax constant of any finite menu of interviews is a convex program with a dual "witness" form. Adaptation across records and label-dependent interview choice do not change it.
2. **Theorem 2.** Fixed forms need at most K = min{2^(b-1), C(m-1, b-1)} times the records of branching, at every population, and an "address" function attains this.
3. **Theorem 3.** r rounds lose at most 2^(b-r). A binary pointer tree shows r rounds can still lose 2^(b-1)/(1+2b/r)^r, with a product version on at most b² features.
4. **Theorem 4.** At a given population the ratio is bracketed by 1/ρ² (the best single-form R² of the target) and a Rényi-1/2 effective number of tree paths.
5. **Solver.** Column generation with dynamic-programming pricing computes certified optimal fixed, r-round and branching designs.

Experiments cover random-forest updates on three small UCI datasets (m ≤ 12, b ≤ 4) and CART screening trees on 12 or 21 binarized BRFSS and thyroid items (b ≤ 6). They find:

- Optimized fixed forms cost 1.0–1.98× the records of branching.
- Uniform random forms cost roughly 10–20×.
- One adaptive round removes most of the gap.
- A two-way log-linear working model fitted to the same capped records beats the design-based fixed-form estimator at n = 1000, but is biased at n = 16,000.

**Strengths**

- **A crisp question with sharp answers.** Converting the classical query-complexity cost of non-adaptivity into a sample-complexity cost under a hard per-record cap is a nice idea. The 2^(b-1) constant is exact, holds at every population via the centring trick, and is matched.
- **The proofs I checked hold up.** I spot-checked path guessing with padding (C.1), the address-function energy bound (C.1.3), the centred simulation and Cauchy–Schwarz bracket (E.1), the local-minimax interpretation (Prop. C.7), and the potential argument for the pointer tree (D.1, Steps 1–5). I found no errors at that level of reading.
- **Useful robustness property.** Designs are pointwise unbiased whatever reference data they were tuned on; only the variance depends on the reference. Fitted designs lose about 5–7%, and Table 10 gives a finite-pilot analysis.
- **Certified numerics.** Primal and dual bounds are reported, an independent dense implementation is used as a cross-check, and uncompleted runs are stated.
- **Unusual candour.** The paper reports where its own regime loses: the log-linear model wins at n = 1000 (Table 12), imputation from complete records wins when it transports (Table 11), order effects are comparable in size to the gains (F.7), and the cap matters more than pre-commitment for ensembles (Table 2). The limitations section is thorough.
- **A practically useful by-product.** The "path-set" design (Prop. E.3) is cheap (at most 2L·2^b variables) and within 2–4% of the all-forms optimum on every screening run.

**Weaknesses**

1. **[major] The setting is narrow and inverted relative to ML evaluation.** Five conditions must hold together:
   - labels are observed for every record and are free;
   - there is a hard, immutable per-record feature cap;
   - the target has Fourier degree ≤ b, which in every experiment is arranged by setting the cap equal to the model's own tree depth;
   - features are binary with m ≤ 21;
   - there is a single known estimand.

   For a depth-b screening tree, the branching audit is just "run the tree and record the label". The fixed-form question then arises only when the audit cannot branch although the rule itself does, and I find that hard to picture. For forest updates, a deployed forest of 20 trees already needs all its features per case, so a cap of b in the audit is artificial. Appendix F.8 concedes that once a label costs more than about 4–15 feature questions, complete records beat the best fixed design — and that is the usual ML regime. The paper notes it "reverses our cost structure" relative to active testing and prediction-powered inference, but gives no concrete ML use case where the reversed structure binds.

2. **[major] Degree ≤ cap excludes most models people actually evaluate.** Thresholded or link-transformed ensembles, GBDT probabilities, neural networks, and any model using more than b features non-additively are not identifiable. The paper then offers only identification floors (Appendix G, Table 14). The headline theory and all main-body experiments say nothing about the price of pre-commitment in that biased regime, which the paper lists as open.

3. **[major] The paper's own experiments show the practical stakes are small.**
   - Observed gaps are 1.0–1.98×, and exactly 1.00 on all 24 thyroid runs and most BRFSS b = 3 runs. The structural reason is simple: the tree uses ≤ b items.
   - One extra round brings the ratio to ≤ 1.04 where solved.
   - A two-way log-linear model on the same fixed-form records has RMSE 0.77–0.97× that of the design-based form score at n = 1000, "on a par with branching".

   So at realistic audit sizes the cost being priced is the cost of insisting on design-unbiasedness in a saturated model on 2^(m+1) cells. The local-minimax justification (Prop. C.7) is an n → ∞ statement with the cube fixed; with m = 12 and n = 1000 it does not describe the operating regime. Table 1's "ratios of W are ratios of the numbers of records that two protocol classes need" is stronger than what is shown.

4. **[major] The headline baseline is a strawman.** "Balanced random forms need 9–23×" is uniform sampling over all C(12, b) forms, when the rule depends on only 2–10 of the 12 items; most such forms spend queries on irrelevant items. Nobody validating one known tree would do this. Matrix sampling is uniform because it serves many estimands, which this framework does not. A fair naive baseline would be uniform over the tree's path sets, or over forms within the rule's items, with optimal scores. The only nearby number is the N_P column (1.5–10.5), which is completion-only path guessing with optimized probabilities, not that baseline. The abstract's 9–23× is also the BRFSS range at caps 4–6 only; thyroid is 2.4–10.8 (Table 7).

5. **[major] Small scale, and the solver stops where it gets interesting.**
   - Forests at b = 4 were completed only for m = 6 (15 tasks).
   - Two-round designs at b = 6 were not solved for 4 of the 5 non-trivial runs after one hour; the certified upper ends reach 1.32.
   - The pointer tree at b = 5 and the m = 21, b = 5 case were not completed.
   - The 21-item study reuses the same trees as runs R0–R2, so it adds no new population, yet its rows appear in Table 3 and its b = 4 runs are counted among the "21 runs with a gain" (18 distinct trees plus 3 duplicates).
   - The claim "one round recovers ≥ 80% in every case solved to optimality" is conditioned on solvability. Among BRFSS trees that are not two-round computable (7), only 3 were solved (1.018, 1.040, 1.013). The "14 runs" in the text include runs where two rounds trivially compute the tree.
   - Model-based comparisons use seed 0 only.
   - The populations are empirical laws of 171–3,101 records on a 4,096-profile cube, plus 1% uniform mass.

6. **[major] Single-use data.** The optimized design concentrates on a few forms tailored to one frozen contrast. Data collected this way generally cannot evaluate the next model, and under the path-set menu a different tree is typically not even identifiable. Model comparison and iteration are the norm in ML evaluation, so this limits practical value. It is acknowledged in one sentence but not quantified.

7. **[minor] Density and venue fit.** The eight pages carry four multi-part theorems, a solver, six experimental sub-studies and a long related-work section, with constant forward references into a 40-page appendix. Theorem 1 bundles three claims, and its "universal factor 104" bound is never used again in the main body. The survey vocabulary ("interview", "form", "log-gap") and 11-column tables make it hard going for an ML reader. Much of the appendix (Prop. B.3, Thm. C.3, C.7–C.8, G, H) is only loosely tied to the main claims.

8. **[minor] Small inconsistencies.**
   - Section 6 says "the three 21-item trees" are two-round computable; Tables 3 and 8 list six 21-item runs.
   - Appendix A says every experiment is described in Appendix F, but G.1.1 (Table 14) and H (PISA, Table 15) are experiments outside F and never referenced from Section 6.
   - The PISA archive analysis ends with "no branching benefit, MSE or coverage estimate is claimed", so it does not support the paper's thesis.

9. **[minor] Novelty calibration.** The paper itself says Theorems 1 and 4 assemble standard tools (minimax duality, c-optimal design, AIPW under known coarsening). The upper bound of Theorem 2 is importance sampling over at most 2^(b-1) path sets, and the lower bound is the index function. The new technical content is mainly the round hierarchy in Theorem 3(c–d). Several 2026 preprints the paper positions itself against (Li et al.; Goldberg et al.; Xu; Aronow & Lopatto) are ones I could not verify from my own knowledge; theory reviewers should check the delta to Li et al. on the pointer tree.

**Soundness**: 3 — the theory I spot-checked is correct and the numerics are certified, but several headline empirical framings (uniform baseline, "every case solved to optimality", W-ratio as "records needed") are more generous than the evidence.

**Presentation**: 3 — precise, honest, with helpful figures, but overloaded and not self-contained for an ML audience without the appendix.

**Significance**: 2 — elegant worst-case theory, but the setting is niche for ML evaluation and the paper's own experiments show small gaps that a second round or a simple working model removes.

**Originality**: 3 — the queries-to-records reframing and the round hierarchy under a per-record cap are new to my knowledge; the characterization and population program are acknowledged recombinations.

**Key Questions for Authors**

1. Can you give one concrete evaluation scenario, ideally with real data, in which labels are observed for all records at negligible cost, the per-record cap is immutable, the audit cannot branch, and the target has degree ≤ cap for reasons other than "cap := model depth"? A convincing instance would raise my significance score and probably my overall score. The PISA appendix is the natural candidate but currently claims nothing.
2. What are the ratios against a fair naive baseline: uniform (or simple heuristic) probabilities over the tree's path sets, or over forms restricted to the items the rule uses, with optimal scores? If the "design matters more than adaptivity" factor shrinks to about 1.5–3×, the abstract should change. If it stays near 10×, weakness 4 is resolved.
3. Table 12 shows the log-linear model on fixed-form records matching branching at n = 1000. At what n, for these targets, does the design-based ordering (branching < fixed form) become the operative one for a practitioner — for example, RMSE crossover curves over n for two- and three-way models, across all seeds? If the crossover is at n ≫ 10⁴, I would regard the constants as mainly of theoretical interest; if it is at a few thousand with a modestly richer model, I would weigh the practical case more favourably.
4. How does a design optimized for model A perform (variance, or identifiability at all) when the collected records are reused to evaluate a retrained model B or a second contrast? Can the program be extended to a set of estimands at modest cost? A positive answer would address weakness 6.
5. For targets that are not identifiable (thresholded forests, GBDT with a link, cap < depth), can you report at least empirical fixed-versus-branching comparisons of the finite-n program Φ_n in (3) on the Table 14 models? Evidence that the story carries over to that regime would substantially broaden relevance.

**Limitations**

Yes. The limitations section and Section 6 are unusually forthright about single estimand, design-based scope, order effects, the label-cost regime, identification floors and solver scaling. I would add two explicit statements: that data collected under an optimized design are essentially single-purpose, and that the local-minimax interpretation of W requires n large relative to 2^(m+1).

**Overall Recommendation**: 3 — Weak reject

This is a borderline 3/4. The theory is solid and I would not object to acceptance if theory-oriented reviewers champion it on the strength of Theorems 2–3. On the criteria I am asked to weigh — realism of the setting, practical significance for ML evaluation, and experiments against strong baselines — the weaknesses currently outweigh the merits. The setting is niche, the measured effects are small and removed by one round or a simple model, the prominent 10–20× comparison uses a weak baseline, and the computations stop at m ≤ 12, b ≤ 6.

**Confidence**: 3

I read the main body fully and spot-checked the proofs of Theorems 2, 3(a, c) and 4, Prop. C.7, and the experimental appendix (Tables 7–12). I did not verify Theorem 1's finite-sample constant, the product constructions, or the unfamiliar 2026 references.

**What would move me up one point**

- A realistic, end-to-end case in which the cap and free labels are genuine and the optimized fixed or two-round design delivers a measurable saving over what a practitioner would otherwise do.
- Replacing or supplementing the uniform-over-all-forms baseline with fair naive baselines, and adjusting the abstract accordingly.
- All-seed model-based comparisons with RMSE-versus-n crossover curves and at least one richer working model, so the regime where the constants matter is delimited.
- Some evidence beyond cap = depth and m ≤ 12: a multi-estimand or reuse analysis, or fixed-versus-branching comparisons in the non-identifiable regime, using the scalable path-set program.
- A leaner main body: state Theorem 1 briefly, move the Φ_n bound and peripheral appendix material out, fix the count inconsistencies, and qualify the "records needed" interpretation of W.

These are all feasible in a revision. None requires new theory.
