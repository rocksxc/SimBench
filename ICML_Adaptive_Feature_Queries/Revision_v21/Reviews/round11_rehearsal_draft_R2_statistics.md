# Round 11 — DRESS REHEARSAL (not the official round): mock review R2 (statistics / missing data) of a v21 draft (md5 b6b19eb2038a44dff14c2c51557ca34a, not the packaged PDF)

Overall Recommendation: **4 (Weak accept)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Mock review by an independent language-model reviewer agent on 2026-11-13, used to revise the draft before the single official round; not real ICML feedback. Full text as returned.)

**Summary** (in my own words)

The paper studies estimation of a single known linear functional Δ(P) = E[Y d(X)] (the accuracy, or accuracy difference, of frozen rules on binary features) when each sampled record may reveal at most b of m features, the label being always observed and free. It compares acquisition menus: pre-committed forms (planned missingness, MCAR by design), r-round interviews, and fully branching interviews (depth-b trees; monotone CAR by design).

Main claims:

- **Simulation bound (Thm 1(i), Thm C.1).** Any protocol on n branching records can be reproduced in law by fixed forms using a random number of records with mean K·n, K = min{2^(b-1), C(m-1,b-1)}. The argument is rejection sampling: draw one of the tree's at most 2^(b-1) padded path sets, keep the record if its path completes inside it, and thin to equalise acceptance.
- **Sharpness (Thm 1(iii)).** The factor 2^(b-1) is attained for the first-order minimax constant V and the population constant W by an address (index) contrast on m = b-1+2^(b-1) features.
- **Robustness (Thm 2).** r rounds give an upper bound 2^(b-r), with pointer-tree lower bounds; c extra pre-committed questions reduce the worst case by at most a factor of about c+1.
- **Constants (Thm 3).** V is characterised by minimax duality. W_A(P) is the Robins–Rotnitzky–Zhao known-coarsening efficiency bound minimised over the design (a c-optimal design problem), with a local-asymptotic-minimax interpretation and a bracket 1/ρ² ≤ W_fixed/W_branch ≤ N_P(τ) ≤ K. A column-generation SOCP solver certifies optimal designs for each menu.
- **Working models (Thm 4).** The simulation bound survives in any model. Under features independent given the label, the gap is at most 2 (zero with label-dependent forms). A pairwise log-linear model with strong couplings can retain a gap of 2^(b-1)/b.
- **Experiments.** These are oracle computations of W-ratios at smoothed empirical laws (BRFSS-derived trees, thyroid, Spambase, small forests) plus simulated audits. With the cap equal to tree depth, optimal forms need 1.0–2.38 times the records of branching where computed. One extra question or a second round removes most of the gap, uniform forms are far worse than optimised ones, and a pairwise working model on pair-covering forms nearly closes the gap at moderate n at the cost of a non-vanishing bias.

**Strengths**

1. **A clean, exactly sharp headline result.** Thm C.1 is a comparison of experiments (deficiency zero at a K-fold record cost), not only a variance bound. It therefore covers every estimator, loss, model and sequential protocol at once, and the matching lower bound gives the exact constant. I checked the proof of Thm C.1, the padding and path-set counting, the address-contrast energy computation (eq. 3; w·2^(1-w) ≤ 1), the centred-score proof of Thm E.1(a)–(c), the witness bound, and the arithmetic of Thm 2(c) (2^(j+1)-j-2 extra questions; K⁺ < 2^(b+1)/(c+3)). I found no errors.
2. **Honest positioning against classical theory.** The paper says explicitly that W_q(P) is the RRZ/Tsiatis bound for a known coarsening mechanism, that optimising over q is Elfving-type c-optimal design, and that the simulation is the across-record version of a folklore conversion. It isolates what is new: the cross-menu comparison, exact constants, the rounds and extra-question trade-offs, and the model results. Appendices E.7.1 and C.6.2 state this in the right language. The local minimax statement (Prop. C.9, van Trees, sequential designs, biased estimators allowed) is correctly formulated, including the full-support qualification.
3. **Useful structural insight.** The centring remark (Thm E.1 and the "uncentered bracket" discussion) is correct and practically important: naive path-guessing or Horvitz–Thompson scores inflate the variance by more than K for accurate rules; the augmented score does not.
4. **Pointwise unbiasedness.** The score remains exactly unbiased under a mis-specified reference law, with only the variance affected (Props E.8/E.9). This is the right design-based property and is used well: fitted and pilot-learned designs, with the pilot charged to the audit.
5. **The model-based section is better than usual for an ML venue.** Thm 4(b) is a correct and interpretable efficiency calculation: only inclusion probabilities matter under conditional independence, and the factor 2 comes from label-proxying. I verified the form of the bound against the Hoeffding-projection influence function. Thm 4(c) appropriately warns that the order of a log-linear model is coding-dependent.
6. **Comparators are unusually thorough and mostly fair.** They include uniform matrix sampling with optimal and with Horvitz–Thompson tables, EM under two-way and three-way log-linear models on the capped records, misspecification analysed with sandwich variance at the pseudo-true value, the pair-coverage identifiability condition for split questionnaires, hot-deck multiple imputation and regression imputation from external complete records under pre-specified shifts, and a cross-fitted model-assisted estimator. The paper reports results unfavourable to its own headline: the model-based estimator on forms matches branching up to n ≈ 8k, and imputation wins when transport holds.
7. **The limitations section is candid.** It covers the knife-edge cap, free labels, the single estimand, the absence of a field audit, the unweighted data, and the 10^4 finite-sample factor.

**Weaknesses**

1. **[major] Limited novelty beyond classical ingredients for the parts that matter in practice.** For a single tree, W_branch(P) = Var(t) trivially, because branching observes t. So W_fixed/W_branch is simply the design effect of an optimally allocated planned-missingness design under the nonparametric RRZ bound, relative to complete data on the score. That is a c-optimal split-questionnaire design for one functional, which is classical in kind. The new theory is the worst-case combinatorics: Thm 1's upper bound is a short rejection-sampling argument, and its lower bound is the index function, the standard adaptive versus non-adaptive separation. Thm 2(b) and Thm 4(c)/E.5(c–e) are the technically substantive parts, but they concern constructions (pointer trees, one-hot couplings) that the paper's own experiments show are far from trained rules. I regard the cross-menu framing as a real contribution, but a moderate one.

2. **[major] The paper's own evidence deflates the practical significance.** On trained rules the gap is 1.0–2.4, and only at the knife-edge where the cap equals the depth. It largely vanishes with one or two extra questions or one follow-up batch. Under a standard pairwise working model, which is how planned-missing data are actually analysed, it is 1.02–1.13 in constants and about 1.00–1.07 in simulated MSE up to n = 8,000. The exponential worst case needs m exponential in b, or 2^(b(1-o(1))) with m ≤ b². The Thm 3(c) bracket [1/ρ²_P, N_P] is nearly uninformative on real rules: Table 9 at b = 6 gives 1.13 and 10.5 against a truth of 1.58, so the theory does not predict the empirical numbers and only the solver does. The message that survives for practitioners is "optimise the forms, don't randomise uniformly; add a question if you can". That is sensible, but it is a design-optimisation message more than a statement about the value of adaptivity. The title and abstract lead with 2^(b-1).

3. **[major] The headline empirical numbers are oracle quantities, asymmetrically favourable to forms and censored by computability.**
   - (a) W_fixed(P) is attained by form probabilities and tables tuned to P, including centring at Δ(P), the estimand itself. The branching benchmark is a plain mean that needs no tuning. The operational figure is the charged-pilot column of Table 1 (1.53–1.93 at N = 4,000), not 1.35–1.58, yet the abstract quotes the oracle range.
   - (b) The oracle design is optimised at the very empirical law at which it is evaluated. For Spambase, about 2,300 target records populate up to 2^14 cells, so in-sample design optimism is likely. The bootstrap check re-optimises on resamples with the same support and does not address this. Source-fitted, out-of-sample ratios are given for the 12-item BRFSS runs only.
   - (c) The range "1.0–2.38" excludes the 5 widest rules (more than 13 items), which are the ones where the gap should be largest. For these only the bracket [1.14–1.43, 2.20–3.97] is known, so the true maximum may well exceed 2.38. "Where it was computed" is stated, but the selection correlates with the outcome. Medians are also conditional on "runs with a gain".
   - (d) Forms are restricted to the rule's items, and the 1% uniform smoothing mass enters every constant. I did not verify the sensitivity analysis said to be in App. F.1.

4. **[major] The assumptions are restrictive relative to the survey and clinical settings invoked.**
   - Every record's label is observed at no cost. In validating a screening rule the reference-standard label is usually the binding cost, and App. F.10 shows that complete records undercut the best forms once a label costs more than about 4–15 questions.
   - There is a single, pre-specified, low-degree functional. The paper's own App. F.6 shows the optimised design can be 1.55–317 times worse for another rule, whereas real surveys are multipurpose.
   - Features and label are binary, with a hard identification threshold deg(d) ≤ b.
   - There is no unit or item nonresponse, and no mode or order effects, so coarsening is ignorable only by fiat. Branching and forms differ exactly in the dimension where mode and order effects arise.
   - The BRFSS extract is treated as an unweighted iid population, ignoring weights, strata and PSUs. The data are a single 2015 Kaggle-derived file, and the "several health outcomes" are five outcomes from that one file. Thyroid shows no gap at all, and Spambase is not a questionnaire.
   - No audit was actually fielded.
   
   Each point is acknowledged, but together they make the real-data section an illustration of the constants rather than evidence about audits.

5. **[major] Presentation.** The 8-page body is a compressed index into a 55-page appendix. Theorems 1–4 each bundle three to five claims with forward references, and only Thm 1 has an in-body proof sketch. The experimental section reports many medians over shifting denominators (38 runs, 49 rules, 18 of 24 trees, 17 runs, 12 trees, 60 rules), with "≤" entries and "where computed" qualifiers. A conference reviewer cannot verify Appendices D and E.2 (about 20 pages of potential arguments and log-linear constructions) in the time available. I spot-checked B, C.1, C.2 (arithmetic only), C.6.2, E.1, E.7–E.9 and the statement and part (a) of Thm E.5, but not D.1 or E.5(c)–(e). The paper reads like a journal paper cut down to fit.

6. **[minor] "Exact" and "for every sample size" need care.** The simulation is exact with a random number of records; with a fixed budget one gets Binomial(n', 1/K) usable records. V is a first-order constant and the finite-n bracket has a factor 10^4. W is local-asymptotic with the centre P known, on a nonparametric model with 2^(m+1) cells. For n in the low thousands and K = 6–13 items this "many records per cell" regime is not reached, which is precisely why the pairwise model wins in the simulations.

7. **[minor] Statistical details of the simulated audits.**
   - EM intervals use a delete-a-group jackknife with eight groups. A sandwich or profile interval would be standard, and the under-coverage at n = 16k is driven by bias rather than the variance estimator.
   - The "early-stopped EM from the uniform law" is an ad hoc regulariser when no interior MLE exists, so the comparator is not the MLE in those cases.
   - Multiple imputation uses 10 hot-deck imputations with exact matching on asked items and label from external records. The shift variables were deliberately chosen so that the imputer cannot condition on them. This is fair as a stress test but should be described as such.
   - There are only 3 seeds per configuration.

8. **[minor] The accuracy estimand is not the natural target for screening.** Accuracy of a class-balanced CART tree on a 14%-prevalence outcome (0.63–0.74, below the trivial classifier) is not what a screening validation would report. Sensitivity and specificity (label-conditional contrasts) are the natural targets, and the label-dependent design machinery of Prop. E.2 would fit them directly.

9. **[minor] Related work omits some neighbours.** The closest classical neighbours are named, but not multiple-matrix-sampling efficiency results (Shoemaker; Munger & Lloyd) or optimal planned-missing design work in psychometrics, and not the computerized-adaptive-testing versus linear-forms efficiency literature. The latter is the most direct precedent for "adaptive versus pre-committed items", although for latent-trait estimands.

10. **[minor] Thm 4(b)'s factor 2 is somewhat beside the point in the paper's own setting.** Labels are observed before the interview, so label-dependent forms are always available, and the experiments show they change the nonparametric ratio by at most 0.5%.

**Soundness**: 3 — The proofs I checked (simulation, address lower bound, centred scores, witness bound, local minimax, extra-question counting, conditional-independence constant) are correct. The empirical constants are certified but are oracle, in-sample and selectively computed quantities, and large parts of Appendices D and E.2 could not be verified.

**Presentation**: 2 — Precise and honest, but severely over-compressed: overloaded theorems, results sections that are lists of medians over changing subsets, and essential content in a 55-page appendix.

**Significance**: 2 — A definitive worst-case answer to a clean question, but the regime where it bites is artificial, and on realistic rules the price is small and removed by mild relaxations or a standard working model. The actionable part is c-optimal design of split questionnaires for one functional.

**Originality**: 3 — The cross-menu "price of pre-commitment in records" with exact constants, the rounds and extra-question trade-offs and the model results are new as a package. The individual ingredients (path guessing, index function, RRZ bound, Elfving design, van Trees) are classical.

**Key Questions for Authors**

1. **Operational versus oracle ratios.** For all rules in Tables 1–2 (not only the 12-item BRFSS runs), what are the ratios when form probabilities and tables are fitted on source or pilot data and evaluated out of sample, with the centring constant estimated? Is the Spambase range stable under a split of the target records into a design half and an evaluation half? If the out-of-sample, pilot-charged figures become the headline and remain in the reported range, my concern 3(a,b) is resolved. If they are materially larger (for example above 2 in the median), the "easy to remove" narrative needs revising.

2. **The five excluded rules.** Can you compute, or bound tightly from below with dual witnesses from column generation restricted to forms, W_fixed for the rules with more than 13 items? If these are near their upper bounds (2.2–4.0), the abstract's range is misleading and should be replaced. If they fall below 2.4, the headline stands and my concern 3(c) disappears.

3. **Beyond classical theory at a population.** For a single tree, is there any statement about W_fixed(P) beyond "RRZ bound plus c-optimal allocation" that is both new and informative on real rules? For example, a bracket that is tight within a small constant for trained trees, or a characterisation in terms of the K−b items beyond the depth that predicts the roughly 65% log-gap removal per extra question. A sharp, predictive population-level result would raise my significance and originality scores. If the answer is "only the solver", the practical contribution is computational.

4. **Costly or partially observed labels, and nonresponse.** How do the menu comparison and the simulation bound change if (i) labels cost c feature-units and may be subsampled (two-phase on Y), or (ii) items are subject to nonresponse with unknown propensity, so that coarsening is no longer known? If Thm C.1 and the design program extend with labels as a queryable coordinate, and you can show the ratios on BRFSS under a realistic label cost, my concern 4 is substantially reduced. If the comparison changes qualitatively (complete records or two-phase designs dominate), the scope should be narrowed in the abstract.

5. **Survey design and the model comparator.** Do the BRFSS conclusions survive using the survey weights (target law equal to the weighted law, with design-consistent variance)? For the pairwise comparator, does a design-consistent, model-assisted version (optimal forms plus pairwise-smoothed tables, as in Tables 16 and 24) recover most of the pairwise model's gain at n ≤ 8k without its bias? If so, the practical recommendation becomes much cleaner ("optimised forms plus model-assisted tables are roughly as good as branching and unbiased"), and I would view the empirical contribution more favourably.

**Limitations**

Yes, largely. Section 8 is unusually candid about the knife-edge cap, free labels, the single estimand, unweighted smoothed laws, the absence of a field audit, order effects, and the solver's scale limits. I suggest three additions:
- State in the abstract that the 1.0–2.38 range is an oracle constant that excludes the widest rules.
- State that a standard working model removes most of the price at moderate n.
- Note that item and unit nonresponse and complex-survey features are outside the theory.

**Overall Recommendation**: 4 — Weak accept

The paper is technically solid, careful and honest, and it settles a clean question with a sharp constant plus a full set of robustness, model-based and computational results. I hold this recommendation with reservations. The core theorem is elementary once posed, the population-level theory is classical efficiency theory plus optimal design, and the paper's own experiments show the phenomenon is modest and fragile on realistic rules. The presentation is also poorly suited to a conference. I would not argue strongly against a reject from a reviewer who weighs significance and readability more heavily.

**Confidence**: 4

I am confident in the missing-data, efficiency and design aspects and in the proofs I checked. I did not verify the pointer-tree round lower bounds (App. D) or the strong-coupling log-linear construction (Thm E.5(e)) in detail.

**What would move me up one point**

- Re-centre the paper on operational quantities: headline the out-of-sample, pilot-charged ratios for all rules; resolve the five excluded rules, or report the range as a bracket including them; and add a design/evaluation split for the small-sample targets.
- Give one population-level result that is both new and predictive for trained rules, such as a tight bracket or a law for the effect of extra questions in terms of K−b, rather than the loose [1/ρ², N_P].
- Run one realistic analysis: the survey-weighted BRFSS law with design-based variance, a screening-relevant estimand (sensitivity/specificity via label-dependent designs), and a label-cost or two-phase-on-Y variant.
- Restructure the body: one theorem per claim, a single consistent set of rules across all experimental summaries, and D.1 and E.5(c–e) either moved to a companion paper or given verifiable in-body proof sketches.

The first and last items are feasible in a revision and would make me comfortable at 5 only together with the second or third. Without a stronger population-level or realistic-data result, I do not see this going above 4.
