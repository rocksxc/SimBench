# Round 4 — simulated review R3 (applied ML evaluation) of v14 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-09; not real ICML feedback. Full text as returned.)

**Summary**
The paper studies capped data collection. Each sampled record can reveal at most b of m binary features, and its label is always observed (paid for separately). The goal is to estimate the population mean of a known per-record target t(x,y) = y·d(x). Here d is the difference of two frozen predictors: for example, the accuracy of a screening rule, or the accuracy gain of a model update. d is assumed to have Fourier degree at most b, so it can be estimated without bias both from randomized pre-committed forms and from adaptive decision-tree interviews. The question is how many more records fixed forms need than branching interviews, and how much is recovered by r rounds of batched questions.

The theory has five parts:
- **Minimax characterization.** For any finite menu of interview types, the first-order minimax constant is a convex program with a dual "witness" form. The lower bound covers biased estimators, adaptation across records, and interview choices that see the current label. A finite-sample version holds up to a factor of 104.
- **Worst-case gap.** The fixed/branching ratio is at most min{2^{b−1}, C(m−1, b−1)}, and the address (multiplexer) function attains it.
- **Rounds.** r-round interviews lose at most 2^{b−r}. Pointer-chasing and binary-pointer-tree constructions show the exponent is b − O(r log b).
- **Population-specific bracket.** At a given population the ratio lies between 1/Γ_P and N_P. Γ_P is the fraction of the target's energy captured by the best single form; N_P is a Rényi-1/2 effective number of tree paths. An optimized path-set design gives a tighter upper end.
- **Computation.** A column-generation solver with dynamic-programming pricing certifies optimal fixed, r-round and branching designs without enumerating the 2^m profiles. A two-phase variant learns the design from a pilot and stays exactly unbiased.

The experiments compute certified ratios for two settings:
- Random-forest updates on three median-binarized UCI datasets: medians 1.24–1.51.
- CART screening trees on BRFSS and thyroid: 1.00–1.58.

On BRFSS, an optimal two-round design nearly closes the gap. The paper also compares against imputation from complete source records under four pre-specified shifts, simulates question-order effects, and analyzes PISA 2012 rotated questionnaire forms.

**Strengths**
- **New, well-posed question.** The paper asks for the price of pre-commitment in records rather than in queries, for population quantities under a hard per-record cap. This links decision-tree and property-testing adaptivity, planned-missingness survey design, and model evaluation. I don't know of prior work giving exact constants for this comparison.
- **Careful, complete theory.** It covers worst-case, rounds, the population level and computation, with strong converses (biased estimators, sequential and label-dependent choices). I checked several proofs and found them correct:
  - the finite-sample Le Cam/KL converse in B.3.2, including label-dependent interview choice and the constant 104;
  - the path-guessing simulation (C.1) and the address-function lower bound;
  - the potential argument (D.2) and Steps 1–5 for the binary pointer tree;
  - Theorem E.1 and Proposition E.6.

  The potential-function bound for the binary pointer tree (each round raises the most likely leaf's probability by at most 1 + 2a_t) is a clean, non-trivial argument.
- **Unbiasedness survives a wrong reference.** Because unbiasedness is imposed at every profile, fitted designs stay exactly unbiased when the reference data are wrong; only variance is affected. Empirically, fitted designs come within about 3–6% of the oracle.
- **Useful computational tool.** Column generation with exact DP pricing over all r-round interviews gives certified primal–dual bounds (agreement to 1e−4 or better). The solver is cross-checked against a dense implementation and comes with sensitivity analyses for smoothing mass and bootstrap.
- **Candid scoping and negative results.** Imputation wins when its transport assumption holds; order effects can match the gains; thyroid shows no gain; the PISA archive has no branching counterfactual. The shifts were fixed before any results were computed, and all four are reported.
- **Thorough reproducibility material:** protocols, exact certificates and released code.

**Weaknesses**

1. **[major] The practical setting is narrow and weakly motivated for an ML audience.** The framework needs all of the following: a known contrast of degree ≤ b on binarized features, tiny caps (b = 2–6), a hard per-record cap, free and always-observed labels, and no transportable complete reference.
   - For screening trees, "branching" is just administering the tree, which already attains full information. The fixed-vs-branching comparison answers a question few practitioners face. The paper never describes a concrete case where a collector must pre-commit forms for a single contrast, and multipurpose surveys are explicitly excluded.
   - For forest updates, deploying either forest needs up to m features per record, so it is unclear why the audit would be capped at b = 2–4. WDBC, Spambase and Ionosphere are not capped-acquisition settings; App. G.1.1 says this itself about WDBC.
   - Common deployed model classes (GBDT with a logit link, MLPs, thresholded scores) have large identification floors at small caps (Table 12), so the framework mainly covers averages of depth-b trees.
   - Table 5 shows the cap itself costs 2–6× relative to full information, much more than non-adaptivity costs. Relaxing the cap may often be the more important lever (App. F.7).

2. **[major] The headline empirical claims rest on a narrow base and are partly overstated or untraceable.**
   - Screening gains appear only on BRFSS. Thyroid and BRFSS at b = 3 show none, because those trees use at most b items, as Proposition C.5 predicts.
   - "An optimal second round … recovers a median 100% of the log-gap … at caps four and five and six" rests on a single tree at b = 6 (Table 3 caption; Fig. 3a joins r = 1 to r = 6 with a dotted line). It was not computed at m = 21, nor for any forest update. The abstract states the conclusion without these qualifiers.
   - I could not find the value 1.98 (abstract, Discussion) in any table or appendix section. The reported maxima are 1.85 for forests and seed-medians of at most 1.70 for screening.
   - F.2 describes forest runs at b = 5, but none are reported.

3. **[major] The evidence against practical alternatives is thin for forests.**
   - The forest results are oracle asymptotic variance ratios only. There is no finite-sample audit simulation (RMSE, interval coverage) for forest updates.
   - There are no simple deployable baselines beyond "restricted branching" (the forests' own trees) — for example, uniform forms with Horvitz–Thompson weighting.
   - There is no imputation comparator, although the forest designs are fitted on complete same-distribution training records. By the paper's own analysis, that is exactly where imputation should win.
   - Proposition 6 (learning the design from a pilot of the audit itself) is never tried. Reference records stand in for the pilot.

4. **[major] Clarity and self-containedness.**
   - The main text is a compressed index into a roughly 40-page appendix. Notation is heavy (V, W, M, K, Φ, Γ, N, H_A), several results are packed per paragraph, and decisive caveats sit in parentheticals, e.g. "(at b = 6 for 1 of six trees)".
   - In Table 2, the "fitted" entry at b = 3 (1.67) refers only to the m = 12 tasks (Table 5), not to the 180 tasks the row summarizes.
   - An ML reader cannot rebuild the experimental pipeline from the main text.
   - Appendix D has typesetting artifacts: a truncated sentence ("is th", p. 31) that resumes after Table 4, a stray "APP", and a D.4 that repeats the main-text sentence with a self-reference.

5. **[minor] The theory is less novel than its presentation suggests.**
   - Theorem 1 combines standard convex duality with Le Cam / van Trees arguments, as the authors acknowledge.
   - The Theorem 2 upper bound is path-guessing simulation, and the address function is the canonical separating example.
   - Theorem 3(b) transposes classical pointer chasing.
   - Theorem 3(c) is informative only for b ≥ 10, beyond any practical cap; the practical round constants are numerical.
   - The factor 104 is too loose to guide practice.

6. **[minor] The "narrow bracket, enough to plan with" message is overstated.**
   - On BRFSS the lower end is 1.08–1.18 while the realized ratio is 1.35–1.58. The tight end is the path-set upper end, which is itself just a feasible restricted design.
   - The rule "reference lower end ≤ 1.05 ⇒ no material gain" is validated almost entirely on trees that use ≤ b items: 31 screening runs and 2 forest tasks.
   - For forests, the reference-based lower end exceeds the realized ratio in 75 of 240 tasks. That sits poorly with the paper calling it "conservative".

7. **[minor]** For non-identifiable d, the main text says the risk is "δ² + Θ(1/n)". App. C.3.3 states only an upper bound on the excess risk ("not a matching excess-risk rate").

8. **[minor]** In the paper's own (synthetic) position model, a 10% chance that the last answer flips biases estimates by 1.5–2.2 branching standard errors, comparable to the sampling gains. The practical message about order effects therefore depends on an unvalidated response model.

9. **[minor] Limited scalability and coarse features.**
   - Each solver iteration costs O(C(m,b)·4^b). Experiments reach m ≤ 21 for fixed forms only, and m ≤ 12 for branching and r-round designs.
   - Median binarization discards information, and the ordinal extension is not evaluated.

**Soundness** 3 — The proofs I checked are correct and the constants are certified. However, several headline empirical statements are overstated or untraceable: the 1.98 maximum, the two-round result at b = 6 (one tree), the "narrow bracket", and Θ(1/n) versus App. C.3.3.

**Presentation** 2 — Very dense and not self-contained for ML readers. Key caveats are buried, some table columns mix task subsets, and the appendix has typesetting artifacts.

**Significance** 2 — A clean answer to a narrow question. Applicability to deployed ML evaluation is limited (degree ≤ b contrasts, tiny caps, free labels), and the measured gains are moderate on a narrow empirical base.

**Originality** 3 — The record-count framing, the rounds analysis and the certified solver are new. The underlying tools (duality, Le Cam / van Trees, path guessing, address and pointer-chasing functions) are standard.

**Key Questions for Authors**
1. Please describe a concrete deployment where all of the following hold: the cap is immutable; the target is one known low-degree contrast; pre-committed forms or few rounds are actually under consideration; and no transportable complete reference exists. In particular, why would an audit of a forest update be capped at b = 2–4 when deploying either forest needs up to m features? A convincing, ideally data-backed scenario would raise my significance score and could move me to 4.
2. Where does 1.98 come from? How many b = 6 BRFSS trees have exact two-round optima, and what are the per-seed values? Can you report two-round constants for forest updates and for m = 21?
   - If two-round recovery holds broadly, the practical message gets much stronger.
   - If it is specific to unbalanced CART trees with few paths, the abstract should be narrowed. I would then lower my view of the empirical contribution.
3. For forest updates, what RMSE and interval coverage do the fitted fixed and fitted branching designs achieve at realistic n? Please compare with simple deployable baselines (uniform forms with Horvitz–Thompson, the forests' own trees) and with imputation from the training records. Have you tried Proposition 6 empirically, and how large must the pilot n1 be at m = 12, b = 4? Positive results would address Weakness 3 and raise soundness and significance.
4. Beyond trees: for thresholded logistic scores or GBDT with a logit link, what cap makes the contrast identifiable or approximable to a useful floor? Does the framework guide practice beyond the floor certificates in App. G? If it effectively applies only to averages of depth-b trees on binary features, saying so up front would make the paper more honest but would confirm my significance concern.
5. How does the "lower end ≤ 1.05" rule perform on the non-trivial cases, where the tree uses more than b items? Why is the lower end called conservative for forests when it exceeds the realized ratio in 75 of 240 tasks? Clear answers would determine whether I count the population-level bracket as a practical planning tool or only as a theoretical characterization.

**Limitations**
Mostly yes. The Discussion is candid: it names the single-functional scope, order effects, the low-degree restriction, reliance on reference data, the imputation and complete-record alternatives, and subgroup burden in the impact statement. Suggestions:
- **Gains need more than b items.** State in the abstract or introduction that gains arise only when the target depends on more than b items (Prop. C.5).
- **Two-round evidence.** State that the two-round evidence comes from 13 BRFSS runs, one of them at b = 6.
- **Model classes covered.** Say explicitly that common deployed model classes fail identification at small caps (Table 12).
- **Round-hierarchy lower bounds.** Note that these bounds are informative only for b ≥ 10.
- **Cost of the cap.** Add that the cap itself costs 2–6× relative to full information (Table 5) and that complete records can be cheaper (F.7).
- **Solver range.** Report the solver's practical range: m ≤ 21 for fixed forms, m ≤ 12 for branching and r-round designs.

**Overall Recommendation**
3 — Weak reject.

**Confidence**
4

**What would move you up one point**
- A realistic, end-to-end case study where the cap and the fixed / rounds / branching choice are real (e.g., a clinical rule validated with batched lab orders, or a computer-assisted survey). It should cover design fitting from the available reference, deployment, and finite-sample interval coverage, and show which decision the ratios inform.
- Two-round optima completed for all b = 6 BRFSS trees, for m = 21, and for forest updates. The 1.98 value made traceable (or corrected), and the b = 5 forest results reported or the mention removed.
- Finite-sample audit simulations for forest updates against simple deployable baselines and imputation, plus an empirical check of Proposition 6.
- A substantially clearer main text: fewer results explained properly, caveats stated explicitly, consistent tables, the appendix artifacts fixed, and the "narrow bracket" and Θ(1/n) statements toned down.

To be honest: items 2–4 are feasible in a revision, but without a convincing realistic scenario (item 1), I would most likely stay at borderline or weak reject.
