# Round 9 — simulated review R2 (statistics / missing data) of v19 (`Manuscript/paper.pdf`)

Overall Recommendation: **4 (Weak accept, borderline)** — Confidence 4 — Soundness 3 / Presentation 3 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words, not the abstract)

The paper studies planned missingness under a hard per-record cap. Each sampled unit has a free, always-observed binary label Y and m binary features, of which at most b may be observed. The estimand is one known linear functional, Δ = E[Y d(X)], with d of Fourier degree ≤ b (for example the accuracy of a frozen depth-b tree, or the difference of two forests' predicted probabilities). Two design classes are compared:

- **Fixed forms**: the b-subset is drawn before the record is seen (MCAR by design, as in split questionnaires).
- **Branching interviews**: a depth-b decision tree (a sequential CAR / monotone coarsening mechanism), with r-round interviews in between.

The contributions are:

1. **Exact simulation (Thm 1).** A "path-guessing" rejection argument shows that any protocol on n branching records is reproduced in law by fixed forms on a geometric number of records with mean K·n, where K = min{2^(b-1), C(m-1,b-1)}. So every variance constant, worst-case (V) or at a population (W), within or without a model, differs by at most K. The address (indexing) function attains 2^(b-1) at every label accuracy.
2. **Rounds (Thm 2).** r rounds reduce the bound to 2^(b-r). Pointer-tree constructions show that a constant number of rounds can still lose nearly the whole exponent.
3. **Constants (Thm 3).** V and W(P) are characterised as convex programs. This is c-optimal design combined with the known-coarsening AIPW efficiency bound, as the authors say. A column-generation solver with exact pricing over trees and r-round interviews gives primal/dual certificates.
4. **Models (Thm 4).** Within order-k log-linear models the gap is at most about (b+1)^k at and near product laws, but is again 2^(b-1)/b at pairwise laws with strong couplings.
5. **Experiments.** On BRFSS-derived screening trees, forests on small UCI sets and simulated audits:
   - optimal fixed designs need 1.0–2.38 times the records of branching without a model;
   - two rounds recover most of the gap;
   - a pairwise working model reduces the ratio to about 1.02–1.28, at the price of a non-vanishing bias and identification problems.

**Strengths**

- **A clean, correct structural result.** Thm 1(i)/C.1 is a comparison of experiments, not just of one estimator. Acceptance is exactly independent of (X,Y), so the bound transfers to any loss, any estimator, any model, ML, Bayes and MI alike. I checked the following and found no errors:
  - the padding and path-set counting, and the tag-averaging Jensen step (C.1.2);
  - the centred score that gives the bound at every P (E.1(a));
  - the witness bound and the bracket 1/ρ² ≤ W_fixed/W_branch ≤ N_P (E.1(b,c));
  - the energy computation (3) for the address contrast;
  - Prop. E.3 (the gap persists at every accuracy);
  - the Fisher-information form of the simulation (E.5(a)) and the Cauchy–Schwarz argument for product laws (E.5(b));
  - the van Trees local-minimax arguments (C.8, E.4);
  - the two-phase consistency argument (E.9).
  - I also verified by hand that W^(2)_fixed = W^(2)_branch = 1/b for the address contrast at the uniform law.
  - I only skimmed the potential-function proof of Thm 2(b,c) (D.1); the step I read, E[M_t | T_{t-1}] ≤ (1+2a)M_{t-1}, looks right.
- **Honest positioning against classical theory.** The paper says explicitly that W(P) for one menu is the Robins–Rotnitzky–Zhao/Tsiatis bound under known coarsening combined with Elfving-type design, and that the two-phase result is standard adaptive design. It claims novelty only for the comparison across design classes, the sharp constants, the rounds hierarchy, the model results and the solver. I agree with that delineation.
- **The question is new to the missing-data and survey literature as far as I know.** That literature optimises one mechanism within one design space (split-questionnaire design, optimal two-phase or multiwave sampling). It does not price MCAR-by-design against sequential CAR under a cardinality cap. The mean-budget remark (the gap collapses to m/b if only the average burden is capped) is a useful observation.
- **Careful computation.** Exact pricing over trees and r-round interviews, primal/dual certificates, exact repair to pointwise unbiasedness, and cross-validation against an independent dense implementation.
- **Candid empirical reporting.** The paper reports results that weaken its own headline:
  - thyroid shows no gap at all;
  - uniform matrix sampling, not pre-commitment, accounts for most of the naive gap;
  - a pairwise working model removes most of the remaining gap at realistic n;
  - optimised designs are nearly useless for a second rule (1.55–317×);
  - the pilot cost is charged;
  - order effects break unbiasedness.
- **Robustness-of-validity property.** Pointwise unbiasedness means reference or pilot misspecification costs only variance (E.5, E.9). This is the right way to use a working model in a design-based audit, and the cross-fitted model-assisted estimator (Table 23) is the appropriate AIPW-type baseline.

**Weaknesses** (numbered; marked [major] or [minor])

1. **[major] Practical significance is modest, and the paper's own evidence shows it.** The exponential gap needs m ≥ b-1+2^(b-1) features and an address or pointer structure. On trained rules:
   - the price is 1.0–2.4×;
   - one follow-up round removes ≥80% of the log-gap;
   - under the pairwise working model that practitioners of planned missingness would actually use (FIML/MI), it is 1.02–1.13× at the fits, with ML at least as accurate as design-based branching up to about 8,000 respondents.

   The net message is "adaptivity within a record is worth little in practice unless you insist on a fully model-free analysis and cannot ask one batch of follow-ups". That is useful, but it is a much smaller result than the abstract's framing around 2^(b-1) suggests.

2. **[major] In the main real-data experiment the adaptive comparator is trivial.** The cap is set equal to the tree depth and the target is the accuracy of that tree. Branching is therefore "administer the rule", which yields complete data on t, so W_branch = Var(t). Table 2 and Table 3 thus measure the efficiency of an optimal MCAR split-questionnaire design for one known functional relative to complete data. That is a classical c-optimal planned-missingness computation, not a comparison of two non-trivial design classes. The setting is also hard to motivate: a rule that is itself a branching questionnaire would be validated by administering it. Only the forest contrasts (m ≤ 12, b ≤ 4, three small UCI sets with 171–3,101 held-out records) exercise the adaptive design problem. There the cap itself costs more than pre-commitment.

3. **[major] The setting is narrow relative to what the titles and abstract suggest.** The restrictions are:
   - one known contrast fixed before collection;
   - binary (or binarised) items;
   - labels free and always observed;
   - a unit-cost cardinality cap;
   - degree ≤ b, which excludes thresholded ensembles;
   - no nonresponse;
   - answers invariant to order and mode.

   Real split questionnaires serve many estimands. The paper's own Appendix F.6 shows that the optimal single-rule designs are highly specialised. Each restriction is disclosed, but together they make the "in practice" recommendations in Section 8 thinner than they read.

4. **[major] The "populations" are smoothed empirical laws, and there is no real audit.** Every constant is a functional of the empirical measure of held-out records mixed with 1% uniform mass.
   - For BRFSS the survey weights and complex design are ignored. This is acknowledged, but the "population" is then the respondent pool, not the US adult population, and weights correlated with items would change the optimal forms.
   - For WDBC and Ionosphere the "population" is 269 or 171 points on a 4,096-cell cube. Oracle designs tuned to such a law can exploit its sparsity. The bootstrap resamples the same sparse sample and does not address this. The fitted-design columns (+1–5%) and the α-sensitivity help but do not fully settle it.
   - All "audits" are resamples with replacement from the same file under an iid model. There is no design effect, no item nonresponse and no real mode or order effect.

5. **[major] Censoring of the hard cases in the headline range.** In Table 3/13, 15 of 45 runs were not computed: 4 rules use more than 13 items, and 11 runs at caps five and six did not finish. These are plausibly the rules with the most paths and the largest ratios. The quoted "1.07–2.38 (median 1.35)" and the abstract's "between 1.0 and 2.38" are therefore ranges over a computability-selected subset, not over rules. The claim that two rounds recover ≥80% "wherever its optimum was computed" has the same selection, and at b = 6 only upper bounds are available. The abstract and Section 8 should say so, or the missing runs should at least be bracketed (1/ρ² and N_P are cheap).

6. **[major] The model-based comparison under misspecification is not on firm statistical footing, and misses a classical identification condition.**
   - Where the pairwise likelihood has no interior maximiser, the "ML" estimator in the simulated audits (Fig. 3b, Table 22) is an EM iterate from the uniform start, stopped at 500 iterations. That is an algorithm-defined regularised estimator, not ML. Its favourable small-n MSE is partly a shrinkage artefact of the stopping rule and should not be labelled "pairwise ML".
   - The paper presents "whether the estimator is well-defined depends on the design" as an empirical finding. The classical requirement for pairwise-model analysis of split questionnaires is that every pair of items be co-observed on some form with positive probability (Raghunathan & Grizzle; Rhemtulla & Little). The rule's own tree never co-observes items on different branches, and the design-based optimal forms have no reason to cover all pairs. A design satisfying this condition, or a 5% floor over pair-covering forms, should have been the model-based comparator.
   - The model menu is coarse: only saturated versus order-2 or order-3 log-linear. The realistic competitor lies between these, for example a penalised or hierarchical log-linear model, a latent-class imputation model, or TMLE with selected higher-order terms. The bias–variance frontier there is exactly what determines whether the design-based constants matter at n ≈ 10³–10⁴.
   - Two main-text statements are in tension: "squared bias equals the variance at a median of 118,000 records" (model-optimal forms, asymptotic sandwich) and "at 32,000 respondents the bias dominates" (fitted forms, early-stopped EM). The reader cannot tell which describes practice.

7. **[minor] The beyond-classical theory is technically light on the upper-bound side and imported on the lower-bound side.**
   - The simulation is rejection sampling, i.e. IPW with complete-case probability 1/|S_τ|.
   - The 2^q non-adaptive simulation, the indexing function and pointer chasing are standard in query and communication complexity, which the paper notes.
   - Thm 4(b) holds only at product laws where the label is independent of the features (a chance-level rule). The neighbourhood has non-explicit radius, so the theorem does not predict any of the empirical model-based ratios, as the authors concede.
   - Thm 4(d) obtains strong dependence by adding deterministic one-hot and product features, which effectively smuggles higher-order interactions into a pairwise model.
   - The W^T constants are only lower bounds when the optimal design has singular information. This is the case for the flagship example in 4(c).

8. **[minor] Inference for the design-based scores.** Normal-interval coverage of the pointwise-unbiased score falls to 0.87–0.89 for some trees (Table 23). This points to heavy-tailed 1/q-weighted scores. The MSE-only optimality criterion ignores it, and the only distribution-free interval offered is Hoeffding with M/q_min. A floor on q or a variance-stabilised interval deserves discussion, since the selling point of the design-based route is valid inference.

9. **[minor] Local-minimax interpretation of ratios.**
   - W(P) is a saturated-model bound: "n large relative to the number of cells", with the centre P available to the procedure. The matching finite-sample statement carries a factor of 10⁴. Attainment without an oracle is only asymptotic (E.9), and needs n₁ ≫ |A|·2^b.
   - Thm 3(a) allows the interview to depend on the current label, but W in 3(b) does not (W^lab ≤ W; Prop. E.2). The main text should state this asymmetry.

10. **[minor] Presentation and venue fit.** The paper is 63 pages with about 25 appendix tables, and has four multi-part theorems in an 8-page body. Section 6 is a dense stream of numbers with shifting denominators (6, 12, 17, 18, 28, 60 runs).
    - Several main-text claims are only meaningful after reading Appendix E, such as "to first order", "0/0 = 0" and "ill-posed likelihood".
    - There are small inconsistencies. For example, the body says "3 of eight pre-specified shifts" while F.7 pre-specifies four shifts (× two caps).
    - The authors disclose LLM assistance in deriving proofs. The proofs I checked are correct, but the volume exceeds what conference review can verify. A statistics journal would be a more natural home.

**Soundness**: 3 — The proofs I spot-checked (Thm 1, E.1–E.5(a,b), C.8, E.4, E.9, Prop. E.3) are correct and the constants are certified. The empirical analysis has disclosed but real limitations: unweighted empirical "populations", censored runs, and an early-stopped EM labelled as ML.

**Presentation**: 3 — Precise and unusually candid, but heavily compressed. The experimental section and the 50-page appendix are hard to audit.

**Significance**: 2 — A sharp worst-case characterisation, but on real rules the price is ≤ 2.4× and is largely removed by one follow-up round or a pairwise working model. The single-contrast, free-label, binary-item setting is narrow.

**Originality**: 3 — Pricing MCAR-by-design against sequential CAR under a per-record cap, with exact constants, a rounds hierarchy and model-dependent results, is new to my knowledge. The ingredients are standard: rejection simulation, indexing and pointer chasing, c-optimal design with AIPW, and column generation.

**Key Questions for Authors**

1. **Censored runs.** For the 15 uncomputed runs of Table 3/13 and the b = 6 two-round cases, can you report the cheap bracket [1/ρ²_P, N_P] and the optimised path-set upper bound W_PS, so that the headline range is not conditional on solver completion?
   - If the brackets stay within about 1–2.5, weakness 5 disappears.
   - If several lower ends exceed 2.4, the abstract's range is wrong and must change. That would raise the practical significance, though it would lower my confidence in the two-round claim.

2. **Fair model-based comparator.** What are the bias, sandwich variance and finite-sample MSE of genuine pairwise (and three-way) ML on forms constrained to co-observe every pair of the rule's items with a probability floor, the classical split-questionnaire identification condition? And what are they for one intermediate model, such as a ridge-penalised log-linear model with interactions up to order b+1 on the rule's items?
   - If a properly identified, mildly regularised working model stays within about 5–10% of branching with near-nominal coverage up to n ≈ 30,000, the practical price of pre-commitment is essentially nil. The paper should then be reframed as a mostly theoretical contribution; my score would not rise.
   - If instead bias or under-coverage appears at audit sizes of a few thousand, the design-based constants matter. I would then rate significance higher.

3. **Non-trivial adaptive optimum on real rules.** Can you give screening-type results where the cap is not tied to the tree depth and no interview computes t? Examples: a depth-b' tree or small boosted ensemble with deg(d) ≤ b < number of path items, or the multi-rule program of F.6 with branching also optimised jointly. Results at realistic m (≥ 20) are needed, even if only as certified intervals. This would show whether the comparison of design classes has empirical content beyond "administer the rule". A convincing table here would move me to a clear accept.

4. **Population and weights.** How do the BRFSS ratios and optimal forms change when P is the weighted law (final BRFSS weights) and the audit is simulated under the weights' implied unequal inclusion probabilities? For the small UCI sets, how do they change when the oracle design is tuned on one half of the held-out records and evaluated on the other? Stable ratios would remove weakness 4. Instability would mean the reported constants are properties of the particular sample.

5. **Reconciling the bias statements.** Which is the operative threshold for the pairwise model: about 118,000 records (Table 24) or about 16,000–32,000 (Table 22)? How much of the difference is due to the design (model-optimal versus fitted forms) and how much to the estimator (interior MLE versus early-stopped EM)? A clear answer determines whether the Section 8 recommendation ("pairwise model for audits of a few thousand") is supported.

**Limitations**

Mostly yes. Section 8 is unusually forthright about the single known contrast, free labels, degree restriction, order effects, unweighted populations, asymptotic meaning of W and solver scale. Constructive additions:

- State in the abstract and Section 8 that the reported ranges are over the runs the solver completed.
- State that for single trees the adaptive optimum is trivially the rule itself because the cap equals the depth.
- State the pair-co-observation identification condition for the pairwise analysis, and that the simulated "ML" is an early-stopped EM iterate where the likelihood is unidentified.
- Note that the design-based scores can be heavy-tailed, with under-coverage of normal intervals.
- Note that no result covers item nonresponse or informative breakoff, which branching interviews induce differently from fixed forms.

**Overall Recommendation**: 4 — Weak accept (borderline). The paper is technically solid, careful and honest, and gives the first exact account of what within-record adaptivity is worth for estimating a population functional under a per-record cap. My reservations are about practical significance, the narrow setting, the trivial adaptive comparator in the main real-data study, and the statistical footing of the model-based comparison. They are not about correctness.

**Confidence**: 4 — I am confident in the efficiency-theory, design and missing-data aspects and checked the corresponding proofs. I did not verify the pointer-tree round lower bounds (D.1, products) or the polynomial-dimension constructions line by line, and I did not run the code.

**What would move me up one point**

- A real-rule experiment in which the adaptive optimum is non-trivial (Question 3), at m ≥ 20, with certified intervals.
- Brackets for all censored runs, with correspondingly qualified headline ranges (Question 1).
- A properly identified, pair-covering model-based comparator and one intermediate regularised model, with genuine ML rather than early-stopped EM, and a reconciled statement of when model bias matters (Questions 2 and 5).
- BRFSS constants under survey weights, and a split-sample check of oracle designs on the small data sets (Question 4).
- A main text restructured around fewer results, with the classical parts of Thm 3 compressed and the label-dependence asymmetry and "to first order" caveats stated in the body.

The first three together would move me to 5. The last two alone would not.
