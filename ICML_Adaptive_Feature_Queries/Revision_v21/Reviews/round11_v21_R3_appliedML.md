# Round 11 — simulated review R3 (applied ML evaluation) of v21 (`Manuscript/paper.pdf`) — official round

Overall Recommendation: **3 (Weak reject)** — Confidence 3 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words)

The paper studies how to estimate a population-level quantity (the accuracy of a frozen classifier, or the accuracy difference of two classifiers) when every record's label is observed for free but only b of m binary features may be queried per record. It compares two collection regimes: "fixed forms", where the b features are chosen before the record is seen, and "branching interviews", where each query may depend on earlier answers within the record. Intermediate regimes are r rounds of adaptivity, c extra pre-committed questions, and a mean rather than hard budget.

Theory:
- **Simulation and sharpness (Thm 1).** Any protocol on n branching records can be reproduced exactly in law from a random number of fixed-form records with mean K·n, K = min{2^(b-1), C(m-1,b-1)}: guess one of the tree's padded path sets, keep the record if the path completes, add a rejection step. The factor is attained by an "address" (indexing) function on b-1+2^(b-1) features.
- **Robustness (Thm 2).** With r rounds the simulation cost is 2^(b-r), with a pointer-tree lower bound that does not match. With c extra questions the worst-case price is 2^(b-1)/(c+1) for the address function.
- **Exact constants (Thm 3).** The first-order minimax constants are convex programs, solved with primal/dual certificates by column generation with dynamic-programming pricing over trees.
- **Working models (Thm 4).** Under conditional independence given the label the gap is at most 2; under pairwise log-linear models with strong couplings it can remain exponential.

Experiments compute these constants at smoothed empirical laws for CART screening trees (BRFSS, thyroid, Spambase) and small random-forest updates.
- With cap equal to tree depth, optimal fixed forms need 1.0–2.38 times the records of running the tree (median about 1.47).
- The gap shrinks to 1.14 and 1.02 with one and two extra questions, and nearly vanishes with one follow-up round.
- Uniform randomization over forms costs 2–4 times branching.
- A design learned from a charged pilot costs 1.5–1.9 times branching.
- Model-based alternatives (imputation from complete source records, pairwise EM) are compared, including their bias.

**Strengths**

1. A crisp question with an exact answer. The simulation in Theorem 1(i) is a comparison of experiments: estimator-free, loss-free and population-free. I checked the proof (padding, uniqueness of the completing path set, the rejection step that makes acceptance independent of (X,Y)), the worked example, the energy calculation (5), and the counting behind Theorem 2(c). All are correct.
2. The relaxations studied (a follow-up round, one or two extra questions, a mean budget) are the levers a practitioner actually has. Asking how robust the worst case is to them is the right follow-up.
3. The estimator is design-based and pointwise unbiased, so a wrong reference sample or pilot costs variance only, never validity (Prop. E.9, checked). That is the property an evaluation practitioner wants. The path-set program is small (at most 2^(b-1) forms regardless of m).
4. Computation carries certificates (primal value plus dual witness), and there is an independent dense implementation for cross-checking.
5. The reporting is unusually candid. The paper states that:
   - the exponential worst case does not materialize on trained rules;
   - most of what a naive comparison credits to adaptivity is design optimization;
   - imputation from complete source records beats every capped design when it transports (Table 17);
   - the pairwise working model wins at small n but its bias does not vanish;
   - an optimized design can be nearly useless for another rule (up to 317 times, Table 16);
   - no field audit was run.
   
   The "records vs. questions" accounting is a useful distinction.
6. The baselines are broad for the planned-missingness part: uniform forms with Horvitz–Thompson and optimal tables, label-dependent designs, regression and multiple imputation under four pre-specified shifts, EM under log-linear models, and a cross-fitted model-assisted estimator.
7. Internal consistency holds where I checked. I re-derived the Table 1 medians and ranges, and the "11 / 3 / 4" two-round counts, from the per-run Table 10. The run counts of Table 11 (38 with a gain, 5 not computed) also match the text.

**Weaknesses**

1. **[major] The setting is narrow and its ML motivation is not convincing.** The model requires free, always-observed labels, a hard per-record cap on features, binary features, a single contrast fixed before collection, and Fourier degree at most b. That is roughly the opposite of the usual ML evaluation bottleneck, as the related-work section itself notes.
   - The one ML-native motivation, on-device evaluation, does not seem to force pre-commitment. A device that holds all its features can evaluate a depth-b tree locally and return the transcript or leaf in one non-interactive message. That discloses at most b feature values and needs no availability across rounds. "One pre-specified query" can be "run this tree".
   - Pre-commitment is real only where the answerer cannot execute logic: paper questionnaires and lab panels ordered in one batch. Those are survey-methodology and biostatistics problems.
   - No ML evaluation scenario is demonstrated end to end.
2. **[major] The headline theory and the empirical findings point in different directions, and the theory does not predict the practice.**
   - For a single tree with cap equal to depth, the adaptive comparator is trivially "administer the rule and take a mean". The comparison is made at an admitted knife-edge; with cap b+1 or b+2 the median price is 1.14 or 1.02.
   - The top of the reported range (2.38) is a single run.
   - The practical message therefore reduces to "do not randomize forms uniformly; optimize them". That is c-optimal design with an optimal augmented inverse-probability-weighted score under planned missingness, which the paper acknowledges as standard for one menu.
   - The instance-level bracket [1/ρ², N_P] of Theorem 3(c) is very loose on real rules. Table 10 has lower ends of 1.07–1.26 against optima of 1.2–2.0. Table 11 has brackets such as [1.16, 16.5] and [1.43, 20.0].
   - The paper's explanation, that trained rules depend on few items beyond their depth, is an observation, not a result. There is no bound in terms of K−b or another checkable structural quantity that tracks the measured ratios.
   - No natural family of trained rules is shown where the gap is large.
3. **[major] Scale and scope of the method.**
   - Exact adaptive-class optimization is limited to m ≤ 12, b ≤ 6. At m = 20 only b = 3 was solved, with intervals for two rounds and no usable branching bound at b = 4.
   - Ensembles are the only case where the adaptive design problem is non-trivial. They are studied on 6–12 median-binarized features of WDBC, Ionosphere and Spambase. The "population" there is 171–3,101 held-out records occupying 121–388 of 4,096 profiles, with b = 4 completed only for m = 6.
   - Thresholded ensembles are not identifiable at small caps. Models with dozens to hundreds of features are out of reach.
   - The usable tool is the path-set program for one shallow tree on binarized items.
4. **[major] The experiments are mostly oracle computations, and the realistic regimes are thinner and less favourable.**
   - Headline ratios are asymptotic constants at a smoothed empirical law, with the design tuned to that same law.
   - Without a reference, the pilot-learned design costs 1.53–1.93 times branching (Table 1), and only after smoothing cell masses with a pairwise model. Unsmoothed at b = 6 and N = 4,000 it costs 4.33 (Table 15), no better than uniform forms with oracle tables (4.18).
   - With a reference of 20,000 complete source records, regression imputation dominates the design-based forms when there is no shift (RMSE 2.63 vs 3.60 against branching's 2.96, Table 17). The proposed estimator is then the method of choice only under shift or when model-free validity is required.
   - With neither, pairwise EM matches branching up to about 8,000 records.
   - Simulated audits resample the same empirical laws, use seed-0 trees or 12 trees, and I found no interval coverage for the pilot-learned design.
   - Evidence of a gap rests on two data sources (BRFSS, Spambase). Thyroid shows none. There are three seeds, and the rules are weak (accuracy 0.60–0.75).
   - Several headline medians are conditioned on "rules with a gain" (K > b), which excludes the trivial cases and inflates the summary. The unconditional share should be reported alongside.
5. **[major] Presentation is far too dense for the venue and not self-contained for an ML reader.**
   - The abstract is a list of more than fifteen numbers and qualifiers.
   - Four multi-part theorems, plus mean-budget, product-construction and working-model results, are squeezed into about four pages, often as one-sentence claims. Theorem 4(c) and Section 5 cannot be parsed without the appendix.
   - Appendix numbering does not mirror the main theorems (Thm 2 maps to D.1 and C.2; Thm 3 to B.1, B.2 and E.1; Thm 4 to E.5, whose part (e) is cited in Table 20), so locating a proof takes effort.
   - Section 6 is a stream of numbers pointing to more than 20 appendix tables. Figure 2 is small.
   - Survey vocabulary (interview, form, audit) replaces standard ML terms.
   - There is no algorithm box for the one procedure a practitioner should take away.
   - The 56-page appendix contains many side results (a four-feature exact example, budget curves, nonbinary alphabets, proper scores, AUC) that dilute the message. This reads as a journal paper compressed into eight pages, and a conference reviewer cannot verify most of it.
6. **[minor] Novelty should be calibrated.** Part (i) is the folklore adaptive-to-non-adaptive conversion, which the paper acknowledges. The address/indexing function is the classical separator. Theorem 3's ingredients are standard duality and optimal design. What is new is the exact constant across records, the relaxation bounds and the certified solver across menus. That is solid but incremental from an ML-evaluation standpoint.
7. **[minor] Reuse.** Evaluation data in ML are routinely reused for new models and model updates. A design optimized for one rule can cost 1.55–317 times branching for another. Joint designs help only for rules known in advance. This limits applicability to model-update workflows, which the paper names as a target, and deserves main-text prominence.
8. **[minor] Question accounting.** Branching is charged b questions per record even on short paths, and feature and label costs are uniform. Expected path lengths and a cost-weighted comparison (only sketched in F.10) would make the "about 1.39 per question" claim more interpretable.
9. **[minor] Smoothing sensitivity.** Sensitivity to the 1% uniform smoothing mass is reported for 15 forest tasks only. The screening results get bootstrap resampling but, as far as I could find, no variation of the smoothing mass.
10. **[minor] Related work on the ML side is thin.** Cost-sensitive active classifiers and active feature-value acquisition for evaluation are the nearest ML neighbours, beyond the acquisition-for-prediction papers cited. A short positioning against them would help.
11. **[minor] Verification burden.** Appendix H discloses that a generative model took part in deriving and checking proofs. That is fine in itself, and the listed numerical checks are welcome. Combined with the appendix length, the correctness of Appendices D and E.2 rests on verification a reviewer cannot do in the available time. I did not verify them.

**Soundness**: 3 — The proofs I spot-checked (Thm 1(i)–(iii), the Thm 2(c) counting, Prop. E.6, Prop. E.9) are correct and the computations are certified and internally consistent. The empirical claims are oracle and asymptotic, and much of the appendix is unverified by me.

**Presentation**: 2 — Careful and honest, but overloaded, written in non-ML vocabulary, with mismatched theorem numbering and a number-dense abstract and experiments section. It is not self-contained in eight pages.

**Significance**: 2 — A clean answer to a narrow question. On trained rules the price is small and removable, and the actionable advice ("optimize forms") is standard optimal design. Impact on ML evaluation practice is limited.

**Originality**: 3 — The exact-constant, across-records formulation, the relaxation bounds and the certified solver over adaptive menus are new. The core simulation and the separating function are classical.

**Key Questions for Authors**

1. In the on-device setting, why can a device not evaluate the tree locally and return its transcript in a single message? Please name a concrete ML deployment where labels are free, features are capped, and pre-commitment is truly forced. A convincing answer would raise my significance score; without one the paper is survey methodology in ML clothing.
2. Can you give a bound on W_fixed/W_branch in terms of a checkable structural property of the rule (for example K−b, or a path-set overlap statistic) that tracks the measured 1.0–2.4, rather than the loose [1/ρ², N_P] bracket? A predictive characterization of when the price is large would move significance and originality up.
3. Please report end-to-end finite-sample audits with no oracle and no reference, using the pilot-learned design. I would want MSE and interval coverage across n, including b = 6, against branching, pairwise EM and uniform forms, with unconditional summaries over all trained rules and not only those "with a gain". If the design-based forms keep nominal coverage and their advantage over uniform forms without the pairwise smoothing crutch, my soundness concern in W4 goes away.
4. What can be computed, with certificates or with an honest heuristic, for a soft-vote forest or boosted ensemble on m = 50–100 binarized features at b = 4–6? For example, the menu of the component trees' path sets, as in the "Restr." column of Table 4. Evidence that the method reaches a realistic model class would address W3.
5. Would you restructure the paper? I would move the rounds and mean-budget lower bounds and most of Section 5 to the appendix, add an algorithm box and one fully worked audit, and align appendix theorem numbers with the main text. A credible plan would raise presentation to 3.

**Limitations**

Largely yes. Section 8 is unusually candid about scope: the knife-edge cap, the single known target, free labels, order effects, asymptotic constants, the absence of a field audit and the solver limits. Three additions would complete it:
- State that medians "with a gain" are conditional, and give unconditional summaries.
- Discuss that a device able to compute locally removes the pre-commitment constraint.
- Bring the reuse penalty and the "imputation wins without shift" finding into the main-text practical guidance.

**Overall Recommendation**: 3 — Weak reject

The paper is technically careful and honest, and I would not object to acceptance if the theory reviewers vouch for the appendix. On the criteria I weigh most (realistic and well-motivated setting, practical significance for ML evaluation, convincing non-oracle experiments, clarity for an ML audience), the weaknesses currently outweigh the merits. The work would be a stronger fit, in its present form, for a statistics or survey-methodology journal or a theory venue.

**Confidence**: 3

I know the evaluation, acquisition and missing-data literature well and checked the main-body proofs and several appendix items and tables. I did not verify Appendices D and E.2, and I judged novelty from memory.

**What would move me up one point**

- A concrete, credible ML use case where pre-commitment is truly forced, or an honest reframing of the paper as a planned-missingness and survey contribution with that motivation in front.
- At least one realistic end-to-end audit without oracle designs: pilot-learned, finite n, coverage reported, unconditional over rules, ideally on a model class beyond single shallow trees on 12 items.
- A structural result or diagnostic that predicts the price for a given rule from quantities a practitioner can compute cheaply.
- A substantially decluttered main body: fewer side results, an algorithm box, consistent numbering and a readable abstract.

The first two, together with the last, would move me to 4. The theory alone, however sharp, would not.
