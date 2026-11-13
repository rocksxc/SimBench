# Round 11 — DRESS REHEARSAL (not the official round): mock review R3 (applied ML evaluation) of a v21 draft (md5 b6b19eb2038a44dff14c2c51557ca34a, not the packaged PDF)

Overall Recommendation: **3 (Weak reject)** — Confidence 3 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Mock review by an independent language-model reviewer agent on 2026-11-13, used to revise the draft before the single official round; not real ICML feedback. Full text as returned.)

**Summary** (in your own words, not the abstract)

The paper studies a specific evaluation problem: estimating a known population functional (the accuracy of a frozen rule, or the accuracy difference of two frozen rules) when each sampled record reveals its label for free but at most b of m binary features. It compares "fixed forms" (the b features are chosen before the record is seen) with "branching interviews" (a depth-b decision tree of queries) and with r-round intermediates, and asks how many more records pre-commitment costs.

- **Worst case.** Fixed forms can simulate any branching protocol exactly in law with K = min{2^(b-1), C(m-1, b-1)} times the records (guess the tree's path set, accept when the guess completes). An address/indexing function shows 2^(b-1) is attained. r rounds reduce the bound only to 2^(b-r), and c extra pre-committed questions reduce the worst case by at most a factor c+1.
- **Per-population constants.** The minimax constant of each protocol class is a convex program, solved by column generation with primal/dual certificates. A restricted "path-set program" gives a practical, always-unbiased fixed-form estimator.
- **Working models.** Conditional independence given the label removes the gap up to a factor 2; a pairwise log-linear model need not.
- **Experiments.** On depth-4 to depth-6 CART screening trees (BRFSS, thyroid, Spambase) and small random-forest updates, optimized forms need 1.0–2.38 times the records of branching. One or two extra questions, or one follow-up round, remove most of that. Uniformly randomized forms cost 2–4 times (up to 9–23 times over all items).

I spot-checked the path-guessing simulation (Thm 1(i), App. C.1.1–C.1.3), the centered-score argument (Thm E.1(a)), the K+ arithmetic in Thm 2(c), the two-phase self-calibration result (Prop. E.9), and the experimental appendices F.1–F.7 and F.9–F.10. I did not verify the round lower bounds (App. D) or the model results (App. E.2).

**Strengths**

1. The question is crisp and the answer is exact: a matching upper and lower bound with the constant, not just a rate. The simulation argument is short, correct as far as I checked, and holds for every estimator, loss and sample size.
2. The robustness results (rounds and extra questions, Thm 2) ask the right follow-up question and are the most novel part of the theory to me.
3. The experiments do not oversell. The paper reports that on trained rules the price is 1.0–2.4 times rather than 2^(b-1), explains why (trained trees depend on a median of 3 items beyond their depth), and shows that much of what a naive comparison attributes to adaptivity is really design optimization.
4. The fixed-form estimator is unbiased at every population even when the reference used to tune it is wrong; only variance depends on the reference. That is the right property for an audit.
5. Certified computation (primal/dual gaps of 1e-4), an independent dense implementation, bootstrap and smoothing sensitivity, and pre-specified shifts make the numerical evidence trustworthy within its scope.
6. The limitations section is unusually candid: the knife-edge b = depth, free labels, the 10^4 finite-sample constant, the absence of a field audit, the compute limits.
7. The negative and boundary results are useful to a practitioner: design reuse across rules costs 1.55–317 times, imputation fails under 3 of 8 shifts, pairwise-model intervals under-cover at large n, and position effects bias the scores.

**Weaknesses** (numbered; mark each as [major] or [minor])

1. **[major] The setting is narrow and its realism for ML evaluation is not established.** The results need all of the following at once:
   - labels free and always observed;
   - a hard per-record cap on the number of features (the paper notes that under a mean budget the gap collapses to at most m/b, App. C.6.1);
   - binary features;
   - a target fixed before collection whose Fourier degree is at most b, which excludes thresholded ensembles, boosted models and anything neural;
   - in the headline experiments, a cap exactly equal to the rule's depth.

   This inverts the usual cost structure of ML evaluation, where labels are the expensive part. The paper acknowledges this in one sentence in Section 8.

   For a single tree the "adaptive optimum" is simply "run the tree and average". So the comparison prices a constraint (no skip logic, yet a cap of exactly b items) that I find hard to locate in practice. Paper questionnaires have long carried skip instructions. A batch-ordered lab panel would naturally include all K items the rule depends on (K − b has median 3 here), and then nothing is lost.

   No concrete deployment is given in which the cap is hard, equals the depth, and branching is infeasible.

2. **[major] The paper's own experiments show the practical stakes are small.** The price is 1.0–2.4 times, falling to a median 1.13 with one extra question and 1.02 with two, or about 1.0 with one follow-up round. The exponential worst case therefore does not describe trained rules. The actionable message reduces to "do not randomize forms uniformly; optimize the design", which is the classical message of c-optimal design and importance sampling, as the paper itself says in Sections 4 and 7.

   For the ensemble experiments, Tables 5–6 show the cap itself costs far more than pre-commitment. Fixed forms need 4.75–5.94 times the records of complete data at m = 12, b = 3. That exceeds m/b = 4, so by my arithmetic complete records are cheaper per feature query than the optimal fixed design even with free labels (branching at about 3.3 times is only modestly better than complete records). This strengthens the impression that the capped regime is not where a practitioner would want to operate unless the cap is truly immutable.

3. **[major] Scale and generality of the evidence.**
   - Adaptive classes are solved only for m ≤ 12, b ≤ 6, and for m = 20 only at b = 3; at m = 20, b = 4 the branching bound is uninformative ([1.03, 5.76]).
   - The forest experiments use twenty-tree forests trained on 60–1000 records, 6–12 median-binarized features chosen by position, and evaluation laws supported on 120–400 of 4,096 profiles.
   - All "records needed" figures are oracle population constants at smoothed empirical laws. Only the simulated audits involve sampling, and those are resampling from the same data. No audit was run in the field.

   For an ICML audience this is a thin empirical base for claims about "trained rules".

4. **[major] The recommended practical recipe is more fragile than the main text suggests.**
   - The reference-fitted designs need about 20,000 complete, labelled records from a related population. When those exist and transport holds, the paper's own Table 18 says imputation beats every capped design.
   - The headline "a charged pilot costs a median 11–20% more than the oracle" (Section 6, Table 1) holds only when the pilot's cell masses are smoothed with a pairwise log-linear model fitted by EM (Table 16) and the menu is restricted to path sets.
   - With empirical cell masses, the same pilot gives an all-in price of 4.33 at b = 6, N = 4,000 (Table 16), which is worse than uniform forms (4.18 in Table 1). App. F.5 says "at b = 6 pilots of this size are too small".

   The main text mentions only "smoothed cell masses". No non-asymptotic guarantee is given for the two-phase procedure (Prop. E.9 is asymptotic and discards the pilot).

5. **[major] Presentation and self-containment.** The eight-page body is a compressed digest of a 55-page appendix.
   - Four multi-part theorems, a dozen constants (V, W, K_{m,b}, K_r, K+_{b,c}, N_P, ρ_P, W^T, W^lab, ...) and survey vocabulary (interview, form, audit, record) are introduced in quick succession.
   - Section 6 is a dense sequence of numbers that leans on about 15 appendix tables (6, 8, 9, 11, 13, 16, 18–25). Several main-text claims cannot be checked from the body alone.
   - Theorem 3 is mostly declared "standard ingredients". Theorem 4(c) is not interpretable without App. E.2.

   An ML reader interested in active evaluation will struggle to extract the setting, the estimator and the takeaway. The volume of proof material is beyond what conference review can verify; the paper's finite numerical checks help but, as it says, "do not replace the proofs". A journal format looks like a better fit for the work as written.

6. **[minor] Designs are single-purpose.** Records collected under one rule's optimal design need 1.55–317 times the records for another tree (App. F.6). In ML practice an evaluation set is reused across model versions and metrics. A joint design works only for rules known in advance (+10% median, up to +51%). This deserves more than one sentence in "Further checks".

7. **[minor] Missing budget-matched baselines in the main text.** There is no comparison with complete records under a total feature budget or a mean cap, or with "ask all K rule items with probability b/K". App. F.10 treats only label cost.

8. **[minor] Reporting choices.**
   - "65% of the gap on a logarithmic scale" is an unusual headline statistic; the plain ratios (1.44 to 1.13 to 1.02) are clearer.
   - Table 1 reports 1.62 for the pilot at b = 4 while Table 16 gives 1.65 (and 1.67 unsmoothed); the run sets differ (six runs versus five with a gain) but this is not explained.
   - Section 8 says one adaptive round removes "at least 80% wherever its optimum was computed", but the four b = 6 runs have only upper bounds (within 1.32), which the summary sentence glosses over.
   - The first data row of Table 23 lacks its n.

9. **[minor] Finite-sample meaning.** The ratio statements are first-order. Theorem B.1 carries a factor of 10^4. The exact simulation gives a random sample size (or a binomial number of usable records). The simulated audits support the ratios at n ≥ 500, but only on 12 trees at b = 4, 5.

10. **[minor] Novelty of the core argument.** The upper bound is rejection sampling over at most 2^(b-1) path sets and the lower bound is the address function; the paper itself calls the conversion folklore in query complexity. The contribution is the exact constant in records and the surrounding robustness and model results, not a new technique.

**Soundness** (1-4) with one-line justification

3 — The parts I checked (simulation, centered scores, K+ arithmetic, Prop. E.9) are correct and the computations are certified, but the rounds and model proofs are long and unverified by me, and the empirical claims rest on oracle constants at small m.

**Presentation** (1-4) with one-line justification

2 — Precise but extremely compressed, heavy on notation and appendix pointers, and not self-contained for an ML audience; the experiments section is hard to parse.

**Significance** (1-4) with one-line justification

2 — A clean answer to a narrow question; under the paper's own evidence the practical gap is small and easily removed, and the setting (free labels, hard binary-feature cap equal to rule depth, m ≤ 12) is far from mainstream ML evaluation.

**Originality** (1-4) with one-line justification

3 — The question of the exact record price of pre-commitment for estimation, and its robustness to rounds and extra questions, is new to my knowledge; the individual techniques are standard.

**Key Questions for Authors** (3-5 numbered; for each, say how the answer would change your evaluation)

1. **Can you give one or two concrete, documented settings where (a) labels are observed for every record at negligible cost, (b) the per-record cap is hard and equals the rule's depth, and (c) branching is infeasible while b pre-committed items are feasible?** A convincing real instance, ideally with real per-item costs, would raise Significance to 3 and likely my score to 4. If the answer is "paper forms without skip logic", I remain at 3.

2. **Under a total feature-query budget (or a mean cap), how do optimal fixed forms, branching, complete records, and "all K rule items with probability b/K" compare on the BRFSS and forest tasks?** My reading of Tables 5–6 is that complete records beat optimal fixed forms for the forest updates. If the capped designs lose under budget-matched comparison, the practical case weakens further. If they win in a clearly delineated regime, please put that in the main text; it would help Significance.

3. **What is the all-in pilot cost without the pairwise-model smoothing, and with a misspecified smoother, for b = 4–6 and N between 2,000 and 16,000? Can you give a finite-sample guarantee for the two-phase procedure?** If the recipe works only with a large complete-record reference or a model-smoothed pilot, the "In practice" paragraph should say so. A robust pilot result would address weakness 4.

4. **Does the picture ("price 1–2.4 times, gone with 1–2 extra questions") persist for wider or more realistic rules — deeper trees, gradient-boosted or distilled trees, m in the 50–100 range with the path-set program, and non-binary features (App. C.4.2)?** Evidence at realistic scale, even if only certified upper bounds from the path-set program plus the 1/ρ² lower end, would address weakness 3 and move Soundness and Significance up.

5. **How should a practitioner evaluate several models, or a model not yet trained, under this framework, given the 1.55–317 times reuse penalty?** A minimax-over-a-class design (for example, all depth-b trees on a given item set) with its price would make the method relevant to routine ML evaluation and would improve my view of significance.

**Limitations** ("yes" if adequately discussed, otherwise constructive suggestions)

Mostly yes. Section 8 is frank about the knife-edge cap, free labels, single known target, order effects, the asymptotic nature of W and the compute limits. Three additions would complete it:
- State in the main text that the pilot result depends on model-based smoothing and fails at b = 6 without it.
- State that the reference-fitted design presupposes complete labelled records, in which case imputation is a serious competitor.
- State the budget-matched comparison with complete records for the ensemble tasks.

**Overall Recommendation** (integer 1-6, with label)

3 — Weak reject. The paper is technically careful, honest, and has clear merits (exact constants, certified solver, an always-unbiased estimator). For the ICML main track, though, the narrowness of the setting, the small practical effect the paper itself documents, the small-scale oracle-based experiments, and a main body that is not self-contained outweigh them in my assessment. I would not fight an acceptance driven by reviewers who verify and value the theory.

**Confidence** (1-5)

3 — Confident on the evaluation-methodology, experimental and practical-significance aspects. I checked the core simulation argument and the self-calibration proposition but not the round lower bounds or the model-based theorems.

**What would move you up one point** (concise, concrete list; be honest — if nothing realistic would, say so)

- A concrete, well-documented use case with real constraints (question 1), plus a budget-matched comparison against complete records and mean-cap designs in the main text (question 2).
- Evidence beyond m ≤ 12 and b ≤ 6 on more realistic rules, using the path-set upper bound and the 1/ρ² lower bound where exact optimization is infeasible (question 4).
- A candid main-text account of the pilot recipe (unsmoothed results, the b = 6 failure, the dependence on a reference or model), ideally with a finite-sample guarantee (question 3).
- A restructured main body: one clearly stated estimator or algorithm box, fewer theorem sub-parts, an experiments section built around two or three self-contained tables, and plain ratios rather than "log-gap removed".

The first two items together would move me to 4. The presentation changes alone would not. I do not see a realistic path to 5 for this audience without a demonstrated real-world or large-scale application.
