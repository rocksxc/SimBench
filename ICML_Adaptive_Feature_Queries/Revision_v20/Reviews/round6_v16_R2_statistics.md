# Round 6 — simulated review R2 (statistics) of v16 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words)

The paper studies estimation of one known linear functional Δ(P) = E[Y d(X)] (the accuracy contrast of two frozen rules) when every sampled record reveals its label but at most b of m binary features. It compares three classes of acquisition design: pre-committed forms, r-round interviews, and fully branching interviews. In missing-data terms these are MCAR-by-design patterns of size b, versus sequentially randomised (CAR) monotone patterns with a limited or unlimited number of stages.

The main results are:

- **Theorem 1.** The worst-case first-order minimax constant of a menu is a convex program with an explicit dual. Adaptation across records and label-dependent choices do not change it.
- **Population constant W_A(P).** This is the smallest variance of a pointwise-unbiased score, i.e. the known-coarsening efficiency bound minimised over the design. Proposition C.7 shows it is the local asymptotic minimax risk for arbitrary estimators.
- **Theorem 2.** W_fixed ≤ min{2^(b−1), C(m−1,b−1)}·W_branch at every P, sharp for an address (index) function.
- **Theorem 3.** r rounds lose at most 2^(b−r), and for pointer-tree targets at least 2^(b−1)/(1+2b/r)^r.
- **Theorem 4.** A population bracket 1/ρ²_P ≤ W_fixed/W_branch ≤ N_P.
- **Solver.** Column generation with exact dynamic-programming pricing computes certified optimal designs of each class.

On trained screening trees (BRFSS, thyroid) and small random-forest contrasts (three UCI sets), oracle-optimised forms need 1.0–1.98 times the records of branching, and a second round removes most of the gap. A two-way log-linear EM fit on the same fixed-form records is more accurate than the design-based score for every tree up to n = 4,000.

**Strengths**

- **A clean, new question for the missing-data literature.** How much efficiency can a sequentially randomised (CAR) design gain over an MCAR design of the same per-record size, uniformly over populations? I do not know of a sharp answer to this in the two-phase or planned-missingness literature, and 2^(b−1) with attainment at every accuracy level is a quotable fact.
- **The proofs I checked are correct.** I went through:
  - B.3: Sion plus Fenchel duality, the two-point converse, and the van Trees argument, including label-dependent interview choice.
  - C.5.2 (Proposition C.7): local minimax equals min_q v'(Σ q_ι I_ι)^† v.
  - E.1: the centred path-guessing simulation, the Cauchy–Schwarz witness bound, and Proposition E.3.
  - E.8 (Proposition E.7).
  
  The centring device, returning c + K(H − c) with c = Δ(P), is the right way to make the bound hold for variances rather than second moments at accurate rules. The authors show the uncentred version fails (1.36 = 3.78σ² in the worked example).
- **Classical ingredients are credited accurately.** The text names Elfving and c-optimality, Robins–Rotnitzky–Zhao augmentation, vertex-direction methods, and Bakhvalov/Novak, and says explicitly that the efficiency geometry is not new (E.5, E.6.1).
- **The numerical work is careful.** Primal and dual certificates, an independent dense implementation, repair to exact feasibility, sensitivity to the smoothing mass, and a bootstrap of held-out records are all reported.
- **The baselines are fair, and the paper reports results that go against it.** These include:
  - label-dependent and stratified form probabilities (gain at most 0.5–0.8%);
  - naive designs (uniform matrix sampling costs 9–23×);
  - learned designs with the pilot charged;
  - hot-deck multiple imputation and regression imputation from a complete reference under pre-specified shifts;
  - EM under two- and three-way log-linear models on the same capped records, with coverage.
  
  The working model is even run on forms optimised for the competing design-based score.
- **The limitations section is unusually candid.**

**Weaknesses**

1. **[major] The quantity characterised exactly is not the one that governs accuracy at the sample sizes where such audits run.** W_A(P) is the efficiency bound of the saturated multinomial model and describes risk only when n is large relative to the number of b-way cells. The paper's own Figure 3(b) and Table 14 show the consequences:
   - A routine two-way log-linear EM on the same fixed-form records has smaller RMSE than the design-based score for all 12 trees up to n = 4,000.
   - Its median RMSE ratio is 0.80–0.88 at every size, the same as branching (0.82).
   - For two thirds of the trees it keeps this advantage to n = 32,000.
   
   The worked example needs 2,100–3,600 respondents. So for an analyst using standard planned-missing methodology in that range, the measured value of within-record adaptivity is approximately zero. The paper says so ("adaptivity adds little to it"), but the title, abstract lead and theorems are all about the saturated regime. There is no theory for the bias–variance regime (listed as open), and the middle ground is unexplored: hierarchical model selection or shrinkage between the two-way and saturated models, sieves growing with n, and forms optimised for the model-based estimator. As it stands, "the statistical value of adaptive feature queries" really means "the value within the nonparametric model, asymptotically".

2. **[major] The headline ratios are oracle ratios, and the comparison is asymmetric.** For a single tree, branching attains σ²_P by administering the tree with no knowledge of P. The fixed-form optimum needs the b-way cell masses for both the form probabilities and the augmentation tables. The realised prices are therefore higher than the abstract's "1.0–1.98":

   | Setting | Oracle (all forms) | Pilot-learned, all-in |
   |---|---|---|
   | b = 4, N = 4,000 | 1.52 | 1.67 |
   | b = 5, N = 4,000 | 1.35 | 1.80 |
   | b = 6, N = 8,000 | 1.58 | 3.30 |

   The near-oracle "fitted" designs (+5–7%) presuppose 20,000 complete reference records from a similar population. In that situation imputation from the reference is available, and the paper shows it is more accurate whenever the conditional law transports. The oracle numbers therefore apply only where a large complete reference exists but model-free claims are still required. The abstract should lead with deployable numbers.

3. **[major] The setting is narrow, and some assumptions run against typical audit cost structures.**
   - The target is one pre-specified functional of Fourier degree at most b. For the degree-1 and degree-2 estimands that dominate survey practice the bound is trivially at most 2.
   - The high-degree case is essentially the accuracy of a depth-b tree, where "branching" just means administering the rule. Pre-commitment is then a constraint only for paper forms or batch-ordered panels.
   - Records collected for one rule can be nearly useless for another (1.55–317×), yet multipurpose use is why split questionnaires exist.
   - Labels are free and always observed. Appendix F.9 shows that once a label costs more than about 4–15 questions, complete records beat optimised forms.
   - There is no item nonresponse and no order or context effects. The paper's illustrative order-effect model produces biases of 1.5–2.2 standard errors, as large as the gains being priced.
   - Sampling is iid.
   - Thresholded or link-transformed ensembles are not identified at small caps. The "forest update" experiments therefore concern a signed difference of predicted probabilities (randomised accuracy), not the accuracy of the deployed thresholded forests. The abstract's phrasing invites the stronger reading.

4. **[major, on significance] Worst-case theory and evidence do not meet.**
   - The extremal populations are independent uniform bits with index or pointer targets. On every trained model the gap is below 2.
   - The Theorem 4 bracket, presented as the interpretable population-level answer, is loose on the data. Its lower end is a median factor of 1.31 below the realised ratio and its upper end 4.3 above. At b = 6 the bracket is [1.13, 10.5] against a realised 1.58, so the solver is needed anyway.
   - The round lower bound of Theorem 3(b) is vacuous for two rounds until b ≥ 8, beyond every cap at which anything is computed (b ≤ 6). At b = 3, 4 the pointer-tree constants come from the solver, not the theorem.
   - The statistical machinery of Theorem 1 and W_A(P) is classical, as the authors say. The upper bound of Theorem 2 is a one-step inverse-probability "guess the path" argument, and the lower bound is the textbook index function carried over to an L² projection.
   
   The genuinely new technical content is the round hierarchy (Appendix D) and the pricing dynamic program. Both are closer to query complexity and optimisation than to statistics.

5. **[minor–major] The empirical base is thin for the generality of the wording.**
   - All 18 screening runs with a non-zero gap come from one dataset (BRFSS), with 12 author-selected dichotomised items and 6 runs per cap. Thyroid shows no gap in all 24 runs.
   - The forest tasks use forests trained on 60–1,000 records with median-binarised features, and five splits for the two-round results.
   - Adaptive classes are computed only for m ≤ 12 and b ≤ 6. Four two-round programs at b = 6 did not converge.
   - The "exact" constants are plug-in functionals of unweighted empirical laws with 1% uniform smoothing. BRFSS weights and the complex design are ignored. Only a 27-resample bootstrap on forest tasks speaks to sampling error.
   - The "respondents needed for ±2 points" figures assume simple random sampling.

6. **[minor] The "share of log-gap recovered" metric flatters small gaps** (for example 1.14 → 1.02 counts as about 85%). Absolute ratios (two rounds need at most 1.09×, or at most 1.32× where only bounds exist) are more informative and should be in the abstract.

7. **[minor] One comparison is implied but not shown.** The paper says a model-assisted score cannot beat oracle tables, which is correct. But a parsimonious (log-linear-smoothed) estimate of the cell masses used only to choose tables and form probabilities keeps exact unbiasedness and could plausibly repair the pilot failure at b = 6 (1,728 cells from a pilot of 2,000). This is the natural calibration-style hybrid and is missing.

8. **[minor] Presentation.**
   - The manuscript is 56 pages and the abstract carries about ten numerical claims.
   - Every proof and the result that justifies reading W ratios as record ratios (Proposition C.7) sit in the appendix.
   - Appendices G and H (the PISA archive) are not used by the main text and dilute the paper.
   - The framing that would orient statistical readers (fixed forms as MCAR by design, branching as sequentially randomised monotone CAR, W as the design-optimised efficiency bound) appears only in E.6.
   - The discussion's "within 13–20% of the oracle" at N = 8,000 does not match the ratio of the Table 10 medians (1.65/1.52 ≈ 9%, 1.63/1.35 ≈ 21%). Presumably it is a median of per-run ratios; please say so.
   - The paper discloses that a generative model helped derive and check proofs. The parts I verified are sound, but I did not check the potential argument (D.3) line by line.

9. **[minor] Related-work gaps a statistician will notice.**
   - Optimisation of split-questionnaire designs, e.g. Adigüzel and Wedel (2008).
   - Responsive and adaptive survey design.
   - Randomised monotone missingness and sequential CAR in the Robins–Gill line.
   - Limits of adaptive sensing (Arias-Castro, Candès and Davenport), a statistical precedent for "adaptivity is worth little outside the worst case".

**Soundness**: 3 — The theorems I checked are correct and the computations are certified. The weak point is the interpretation of oracle, asymptotic constants as "records needed", which the paper's own finite-n experiments qualify substantially.

**Presentation**: 2 — Precise and honest, but overloaded: a journal-length manuscript compressed into eight pages, with an abstract that is hard to parse.

**Significance**: 2 — A sharp worst-case separation in a narrow model. Empirically the gap is below 2 and is erased at practical n by a standard working-model analysis.

**Originality**: 3 — The comparison of design classes and the round hierarchy are new. The minimax and efficiency machinery and the single-menu design problem are classical, and are acknowledged as such.

**Key Questions for Authors**

1. **Where does adaptivity pay for the estimator people would actually use?** Please report EM-2 and EM-3 (or a selected hierarchical model) fitted to branching records against the same models on optimised forms, across n. If model-based analysis on branching records is materially better than on forms, or if you can give a usable criterion for when the saturated benchmark is operative (n against cells on the used path sets, or higher-order interaction mass), the practical significance is restored and I would move up. If the gap vanishes, the contribution is essentially the worst-case theory.

2. **What is the best realised all-in ratio without a large complete reference at b = 5 and 6?** In particular, use a pilot whose cell masses are smoothed by a low-order log-linear fit, used only to choose tables and probabilities so that exact unbiasedness is kept. If this lands within about 10–15% of the oracle, the headline "1.0–1.98" is defensible. If it stays near 1.8–3.3, the abstract overstates what a practitioner gets.

3. **Is there any realistic rule and population with a large gap?** That is, not address or pointer targets under uniform bits, but a case where W_fixed/W_branch exceeds about 3 at feasible caps and the two-way model fails. Deeper trees (b = 8–10) could be handled with path-set upper bounds and witness lower bounds, and other surveys could be tried. One convincing case would raise my significance score. If the answer is no, the paper should say that the exponential worst case appears to be irrelevant for trained trees.

4. **When is "hard cap, free label" the binding regime?** F.9 shows complete records beat optimised forms once a label costs more than about 4–15 questions. Please give one concrete collection setting where labels are effectively free, the cap is immutable, branching is infeasible but two rounds are not, and model-free validity is required. A clear answer would change my view of the assumptions in weakness 3.

5. **How robust are the population constants?** Do the BRFSS ratios change materially with the final survey weights? For the forest tasks, what is the bootstrap spread per task rather than pooled? And please confirm that the forest estimand is the randomised-accuracy contrast and state what, if anything, can be said about thresholded accuracy at these caps. This affects soundness of the real-data claims only mildly.

**Limitations**

Yes. Section 8 and the appendices disclose the design-based and oracle nature of the constants, the superiority of working models at survey sizes, order effects, free labels, the single-estimand restriction, the unweighted empirical populations, and the solver's limits. My request is that the two most consequential limitations (weaknesses 1 and 2) be reflected in the abstract's lead claims, not only in its last sentence.

**Overall Recommendation**

3 — Weak reject.

This is a borderline case. The paper is technically solid and unusually honest, and I would not object to acceptance. But the exact constants concern a regime and a problem class whose practical bite the paper's own experiments show to be small. The statistical core is classical, and the manuscript reads as a compressed journal paper.

**Confidence**

4. I am confident on the efficiency-theory, design and missing-data aspects and on the proofs in B.3, C.5.2, E.1 and E.8. I am less able to judge the novelty of the round-complexity constructions against the query-complexity literature.

**What would move you up one point**

- Re-centre the abstract and introduction on deployable numbers (fitted and pilot-learned, with the pilot charged) and on the model-based finding, with the oracle range stated as such.
- Add the missing comparison of model-based analysis on branching versus fixed-form records (Question 1), and a parsimonious-pilot design at b = 5–6 (Question 2).
- Show at least one realistic setting with a practically large gap that a parsimonious model does not erase, or state plainly that none was found and position the paper as a worst-case and computational contribution.
- Bring the MCAR-versus-sequential-CAR framing and Proposition C.7 into the main text, and drop or shorten Appendices G and H and some secondary results to make room.

A convincing response on the first two items alone would bring me to a 4.
