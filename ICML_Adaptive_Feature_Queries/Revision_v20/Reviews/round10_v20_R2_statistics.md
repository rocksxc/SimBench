# Round 10 — simulated review R2 (statistics / missing data) of v20 (`Manuscript/paper.pdf`)

Overall Recommendation: **4 (Weak accept)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 3 (lower end) / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in your own words, not the abstract)

The paper studies a planned-missingness problem. Each sampled record reveals its label for free and at most b of m binary features. The target is one known functional, Δ(P) = E[Y d(X)], with d of Fourier degree at most b (the accuracy of a frozen depth-b tree, or the difference in predicted probability of two shallow forests). The question is how many more records are needed when each record's feature set is fixed before the record is seen ("fixed forms", MCAR by design) than when later questions may depend on earlier answers ("branching", a monotone CAR mechanism), with r-round interviews in between.

The contributions are:

1. **Simulation and sharp gap (Theorem 1).** A rejection-sampling argument ("path guessing") lets fixed forms reproduce any branching protocol exactly in law with K = min{2^(b-1), C(m-1, b-1)} times the records in expectation. An address (multiplexer) contrast attains 2^(b-1) through a dual-witness lower bound.
2. **Rounds (Theorem 2).** r rounds need at most 2^(b-r); a pointer-tree construction shows that a constant number of rounds can still lose nearly the whole exponent.
3. **Constants (Theorem 3).** The worst-case constant V and the population constant W_A(P) are characterised. W_A(P) is the known-coarsening semiparametric bound optimised over the design, i.e. a c-optimal design problem. A bracket [1/ρ², N_P] is given, and a column-generation solver with exact pricing over trees returns certified optima.
4. **Models (Theorem 4).** The 2^(b-r) bound survives in any model. Under conditional independence given the label the gap is at most 2, and it vanishes with label-dependent form probabilities. Under order-k log-linear models the gap is polynomial at and near product laws. Strongly coupled pairwise laws restore 2^(b-1)/b.
5. **Experiments.** On BRFSS-derived, thyroid, Spambase, WDBC and Ionosphere data (m ≤ 12–13 effective items, b ≤ 6), optimal forms need 1.0–2.38 times the records of branching. Uniform forms are much worse. Two rounds recover most of the gap. A pairwise working model shrinks the ratio to 1.00–1.28, at the cost of a bias that does not vanish.

**Strengths**

- The question is cleanly posed and answered with matching upper and lower bounds. Theorem 1(i) is a comparison of experiments, not just of one estimator's variance, so it covers every estimator, loss, sample size and model at once. That is the right level of generality.
- The positioning against classical theory is honest. The paper says explicitly that W_A(P) for one menu is c-optimal design plus the efficient augmented IPW score under known coarsening (Robins–Rotnitzky–Zhao, Tsiatis), that Theorem 3(a,b) uses standard duality and van Trees arguments, and that the simulation is a cross-record version of a folklore conversion. I spot-checked Appendix C.1 (simulation), C.5.2 (local minimax), E.1 (centred path guessing, witness bound, bracket), E.3 (path-set design), E.5(a)–(d) and E.7 and found no errors. The centring device that makes the K-fold bound hold for the variance at every P, not only for the second moment, is a nice touch.
- Theorem 4(b) is a useful result for split-questionnaire practice. Under conditional independence a design matters only through label-specific inclusion probabilities, so outcome-dependent form assignment removes the value of adaptivity and label-blind forms lose at most a factor 2. Parts (d) and (e) together make the correct point that the "order" of a log-linear model is not what controls the gap; dependence and coding are.
- The baselines are fair by the standards of the missing-data literature. The design-based comparator is the efficient AIPW score with optimised augmentation and optimised form probabilities, not plain Horvitz–Thompson, and uniform matrix sampling is shown separately. The model-based comparator is ML/EM on the capped records with pair-covering forms optimised for that model. Misspecification is treated with pseudo-true values and sandwich variances. Hot-deck multiple imputation with Rubin's rules is included, with shifts fixed in advance. A cross-fitted version that uses only the audit's records is reported.
- Negative findings are reported: non-vanishing bias, under-coverage of 0.855–0.953, multiple likelihood maxima, non-identification without pair coverage, reuse costs of up to 317 times, uncomputed cases, and the loose bracket.
- The Q2 finding has practical value. Much of what a naive comparison credits to adaptivity is really design optimisation (uniform item-forms need 2.0–4.2 times, optimal forms 1.35–1.58 times), and one follow-up batch recovers most of the remainder. This speaks directly to two-phase and adaptive matrix-sampling practice.
- The primal/dual certificates and the pointwise-unbiasedness property (a mis-tuned design costs variance, never bias) are good engineering.

**Weaknesses** (numbered; mark each as [major] or [minor])

1. [major] **The worst-case theory and the empirical findings are only loosely connected.** The 2^(b-1) gap needs m ≥ b-1+2^(b-1) features and a multiplexer-type target; the paper notes that the extreme ratio for m close to b is open. On trained rules the ratio is 1.0–2.4. The only instance-level tool, the bracket [1/ρ²_P, N_P], is uninformative there: Table 2 gives [1.13, 10.5] against a computed median of 1.58, and the authors conclude "the solver is needed". Nothing in the theory explains or predicts the small empirical constants. Theorem 4(c) covers only product laws and an unquantified neighbourhood; real items are dependent, and that regime is handled by numerics alone. From a classical-efficiency standpoint the headline theorem is a rejection-sampling argument plus a known hard function. The more novel statistical content is Theorem 2(b,c) and Theorem 4(b)–(e).

2. [major] **The setting is stylised in ways that limit relevance to surveys and audits.**
   - Labels are free and observed for every record, the reverse of most evaluation settings. Appendix F.10 shows complete records become cheaper once a label costs about 4–15 feature questions.
   - There is one known target fixed before collection. Optimised forms are close to useless for another rule (1.55–317 times), whereas real split-questionnaire designs are multipurpose.
   - Features are dichotomised.
   - There is no nonresponse and there are no order or mode effects. The authors' own sensitivity check shows a 10% flip of the last answer biases estimates by 1.5–2.2 standard errors at n = 1000, which is comparable to what the adaptivity gap is worth.
   - The cap is hard per record. Under a mean budget the gap is at most m/b.
   - For a single screening tree, branching simply administers the rule and observes t exactly. The "price of pre-commitment" is then the design effect of planned missingness relative to complete data on t, a much more familiar quantity than the framing suggests.
   - For forests the estimand is a difference of predicted probabilities, not the accuracy of the thresholded classifiers, which are not identifiable under small caps.

3. [major] **The constants are oracle and local, and the comparison is asymmetric in what each side needs to know.** W ratios compare designs tuned to P, with P available to the procedure. The finite-sample bracket carries a factor of 10^4. For a single tree, branching needs no tuning at all, while fixed forms need cell masses for up to C(m,b)·2^(b+1) cells. When the design is learned from a charged pilot, the all-in price is 11–20% above the oracle with pairwise smoothing and 15–146% without it; at b = 6 the pilots are too small, and no non-asymptotic guarantee is given. The abstract and discussion lead with the oracle range of 1.0–2.38. The realised price of pre-commitment without a good reference sample is larger and is not summarised as clearly.

4. [major] **The empirical base is narrow for the breadth of the conclusions.**
   - Adaptive classes are solved only for m ≤ 12, b ≤ 6 (m = 20 at b = 3).
   - There are six runs per cap (two targets by three seeds), with ranges as wide as 1.00–1.98.
   - The five largest rules (more than 13 items) were not computed. This selects toward small rules, and their bracket (above 1.14–1.43, below 8–20) does not exclude materially larger ratios.
   - The "populations" are unweighted empirical laws of a cleaned public BRFSS extract with 1% uniform smoothing. Design weights, clustering and item nonresponse are ignored, so the numbers are finite-population oracle computations for convenience laws, not survey estimates.
   - The bootstrap covers resampling of the target only, not training of the rule.
   - At b = 6 the two-round claim rests on upper bounds for 4 of the runs.
   - "No audit was run in the field" is acknowledged.

5. [major] **Presentation and verifiability.** The submission is a 65-page monograph with four multi-part theorems, about 26 tables and a 52-page appendix, compressed into 8 pages. The main text is essentially an annotated index to the appendix. Theorem 3 mixes three kinds of statement. The denominators in Section 6 change from sentence to sentence (18 trees, 17 runs, 12 trees, 38 of 45 runs, 57 cases, 60 tasks, 28 of 38). The relabelling (interview, form, audit, menu) adds a translation layer for readers from both communities. I could not check Appendix D (the potential argument for rounds) or Theorem E.5(e) in the time available, and I doubt any ICML reviewer can verify the whole. Internal script filenames are left in the text of Appendix E.2.

6. [minor] **"What a model changes" is, in the end, the classical efficiency–robustness trade-off, and the main text could say so more plainly.** Because coarsening is known, any model-assisted or AIPW estimator that stays design-consistent cannot beat W_fixed(P). The 1.5 to 1.07 improvement is bought entirely by believing a restriction that is false by construction, since tree accuracy involves order-b interactions. Further points:
   - The W^(k) ratios are evaluated at the fitted law inside the model, not at the truth.
   - The model-based estimator is fragile in practice: a non-concave likelihood, multiple interior maxima, EM "from the uniform law with early stopping" (an unstated regulariser), a 10% uniform floor to obtain pair coverage, and an 8-group jackknife.
   - "Price at most 1.28" is a variance ratio; the MSE comparison depends on n (the pairwise estimate is worse than the design-based form score for 5 of 12 trees at 32,000 records).
   - All of this is disclosed, but the abstract's "at most 1.28" will be read as a like-for-like number.

7. [minor] **Theorem 4 leaves the practically relevant middle open.** There is no explicit radius in (c). Already at product laws with an unbalanced label the pairwise constants of forms and trees differ (by up to 15% numerically). Part (e) needs 3·2^(b-1) auxiliary features.

8. [minor] **The outcome-dependent sampling result deserves an explanation.** Label-dependent form probabilities lower the ratio by at most 0.5% on real data, although outcome-dependent two-phase sampling is typically very valuable. Is this because the target is t = Y d(X) with tables already allowed to depend on Y, or because of class balance in these data?

9. [minor] **Inference for the design-based estimator is thin.** Only Hoeffding intervals and sample-variance normal intervals in simulation are given. There is no variance-estimation theory for the two-phase or cross-fitted procedures.

10. [minor] **Prior art on the fixed-form class.** The restricted-focus-of-attention literature (Ben-David & Dichterman) studies exactly this class. A sharper statement of what was known there about simulating adaptive attribute access would help calibrate the novelty of Theorem 1(i).

**Soundness** (1-4) with one-line justification

3 — The proofs I checked (C.1, C.5.2, E.1, E.3, E.5(a)–(d), E.7) are correct and the computations are certified; the remaining concerns are about oracle and local constants and the narrow, unweighted empirical base, not about errors.

**Presentation** (1-4) with one-line justification

2 — The sentences are precise and carefully hedged, but the paper is heavily over-compressed: a journal-length monograph whose main body cannot be assessed without the 52-page appendix, with shifting denominators and dense multi-part theorems.

**Significance** (1-4) with one-line justification

3 (lower end) — A definitive answer to a clean question, with usable guidance (optimise forms; one follow-up round), but the exponential gap is a worst-case artefact, the empirical constants are modest, and the setting (free labels, a single known target, m ≤ 12) limits reach.

**Originality** (1-4) with one-line justification

3 — The cross-menu comparison, the round hierarchy for estimation, and the model-dependence results (4b, 4d, 4e) are new to my knowledge; the per-menu efficiency theory and the simulation and address ingredients are classical or folklore, as the authors acknowledge.

**Key Questions for Authors** (3-5 numbered; for each, say how the answer would change your evaluation)

1. **Uncomputed and larger rules.** The path-set program of Proposition E.6 has only about L·2^b variables and gives a certified upper bound on W_fixed without enumerating forms. What does it give for the five rules with more than 13 items, and for trees on all 21 BRFSS variables or 57 Spambase features at b up to 8? If certified ratios stay within about 2.5, the selection concern in Weakness 4 disappears and the empirical message becomes credible at realistic sizes, which would raise my significance score. If they grow, the abstract's range needs to change.

2. **Hard cap versus mean budget on real rules.** Appendix C.5.1 bounds the ratio by m/b under an expected budget. For the BRFSS trees, what is the optimal fixed-design ratio when forms may have variable length with mean b, or a hard cap of b+1 or b+2? If one or two extra pre-committed questions close most of the gap, the practical case for branching and two-round designs is much weaker and should be stated; if not, the hard-cap framing is vindicated.

3. **Survey weights and complex design.** Does the design-based theory carry over when P is the weighted law and records enter with unequal weights or clustering (the variance is then not Var_P(H)/n)? Do the Table 2 ratios change when the actual BRFSS weights are used? A positive answer with numbers would remove one of my main reservations about the real-data analysis.

4. **Model choice at matched validity.** Suppose the order k, or a sparse set of interactions, is chosen from the capped records themselves (for example by BIC or cross-validated likelihood), and intervals are bias-aware or use the sandwich variance. What is the forms-to-branching MSE ratio, and what is the coverage, as a function of n? Equivalently: for each tree, at what n does the design-based fixed-form estimator overtake the pairwise estimator on pair-covering forms, and what is the range across trees (not just the median of 69,000)? If the crossover is below typical audit sizes for a substantial share of rules, the "1.00–1.28" headline should be demoted.

5. **Multipurpose designs.** A joint design for three known trees costs each a median 10% extra. How does this scale with the number J of rules, for example all trees of a forest, or a family of candidate rules? Is there a bound that interpolates between the single-rule optimum and uniform forms? Evidence that optimised forms remain worthwhile for J in the tens would address Weakness 2 substantially.

**Limitations** ("yes" if adequately discussed, otherwise constructive suggestions)

Yes — Section 8 is unusually candid about free labels, the single target, order effects, oracle and local constants, unweighted smoothed laws, the absence of a field audit, and computational limits. Two suggestions: (a) say in the abstract that the 1.0–2.38 range is for oracle designs and that pilot-learned designs cost a further 11–20% or more; (b) say explicitly that for a single tree the comparison is with complete data on t, and that the pairwise-model figures are variance ratios under a model known to be misspecified.

**Overall Recommendation** (integer 1-6, with label)

4 — Weak accept. The paper is technically solid and careful, gives a sharp answer to a well-posed question, and contains several results of real interest to planned-missingness design (the round-by-round bound, the conditional-independence theorem, design optimisation versus adaptivity). It falls short of a clear accept because the headline exponential gap is largely a transplant of known ideas with little bearing on the modest empirical constants, the setting and scale are restrictive, and the presentation is overloaded to the point of being hard to verify.

**Confidence** (1-5)

4 — I am confident on the missing-data, efficiency, design and survey aspects, and I checked the key population-level proofs. I did not verify the rounds lower bounds (Appendix D) or Theorem E.5(e), and I judged novelty relative to the query-complexity literature from general knowledge.

**What would move you up one point** (concise, concrete list; be honest — if nothing realistic would, say so)

- Certified results (exact, or tight path-set upper bounds with informative lower bounds) at realistic sizes: the uncomputed rules, m in the tens, b up to 8, more seeds, and the weighted BRFSS law. The realised (pilot or reference) price should be reported alongside the oracle price in the main table and the abstract.
- An instance-level result that explains the small empirical ratios: either a substantially tighter bracket than [1/ρ², N_P], or a version of Theorem 4(c) with an explicit dependence condition that the fitted BRFSS laws can be shown to satisfy.
- A mean-budget or relaxed-cap analysis on the real rules (Question 2) and a multipurpose analysis beyond three rules (Question 5).
- A restructured main text: move one theory block (for example the polynomial-dimension and product constructions, or parts of Theorem 4(d)) fully to the appendix, state the efficiency–robustness message of Section 5 and Q3 plainly, and stabilise the experimental denominators.

The first and fourth items are realistic for a revision. The second is the one that would most change my view of significance, and it may be hard. Without at least the first, plus either the second or third, I would stay at 4.
