# Round 9 — simulated review R3 (applied ML evaluation) of v19 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 3 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary**

The paper studies estimation of a population-level functional, Δ(P) = E[Y·d(X)] (e.g. the accuracy of a frozen rule, or the accuracy difference of two frozen rules), when each sampled record reveals at most b of m binary features and the label is always observed for free. It compares two acquisition regimes: "fixed forms" (the b features for a record are chosen before seeing any of its answers, possibly at random) and "branching interviews" (a depth-b decision tree of queries), with r-round batch-adaptive protocols in between.

- **Worst-case gap (Thm 1).** Any branching protocol can be simulated exactly by fixed forms using K = min{2^(b-1), C(m-1,b-1)} times as many records in expectation. The argument is "path guessing" plus rejection sampling. The factor is attained by an address (indexing) function.
- **Rounds (Thm 2).** r rounds reduce the bound to 2^(b-r), and a pointer-chasing construction shows a constant number of rounds can still lose nearly everything.
- **Exact constants (Thm 3).** The worst-case constant V and the population-level constant W are characterised as convex programs with a dual. A column-generation solver with certificates computes optimal fixed, r-round and branching designs at a given law.
- **Models (Thm 4).** Under log-linear models of order k the gap is polynomial in b near independence, but can be 2^(b-1)/b again under strong pairwise couplings.
- **Experiments.** On small tabular problems (BRFSS diabetes indicators, thyroid, Spambase, WDBC, Ionosphere; m ≤ 12 mostly, b ≤ 6), optimised fixed forms need 1.0–2.38x the records of the adaptive optimum. One extra round recovers most of the gap. Naive uniform form randomisation is far worse (2–4x, or 9–23x for uniform matrix sampling). A pairwise working model nearly closes the gap but introduces a non-vanishing bias.

**Strengths**

1. The question is cleanly posed and, to my knowledge, has not been asked in this form: the price in records, for estimation, of committing to a record's feature subset in advance. The related-work section is unusually thorough and honest about which ingredients are classical (folklore non-adaptive simulation, c-optimal design, AIPW under known coarsening, minimax duality for linear functionals).
2. Theorem 1 is elegant. The simulation is exact at the level of experiments (any estimator, loss, n, population), not just a variance bound, and the constant 2^(b-1) is tight. I checked the proof of (i) in C.1.1–C.1.3 and the energy computation and dual witness for the address contrast in C.1.4; both are correct. The bracket in Thm 3(c) (lower end via the witness h = t − Δ) also checks out.
3. Unlike many "adaptivity gap" papers, the authors compute what the gap is on trained models rather than stopping at an exponential worst case, and they report that it is modest (median ~1.35–1.58). They also report that much of the apparent benefit of adaptivity is actually design optimisation (uniform forms are 2–4x worse). This is the most practically useful message for practitioners.
4. Design-based scores are pointwise unbiased whatever reference data is used to tune the design, so mis-specified pilot or reference data costs only variance. The pilot is charged to the audit in the experiments, which is the right accounting.
5. The experiments are careful about their own caveats: primal/dual certificates, bootstrap of the target law, runs "not computed" disclosed, model misspecification analysed with sandwich variances, coverage numbers reported even when unflattering, and failure modes (reuse for another rule, order effects) quantified. Section 8 is a candid limitations section.
6. The practical recommendations in Section 8 are concrete and follow from the evidence.

**Weaknesses**

1. **[major] The setting is narrow and its relevance to ML evaluation is not convincingly established.** The results need all of the following to hold together:
   - labels are free and always observed, which is the reverse of the active-testing / PPI cost structure, as the authors note;
   - a hard per-record cap on features, since under a mean budget the gap collapses to ≤ m/b;
   - a single target rule known before data collection;
   - a target of Fourier degree ≤ b, i.e. essentially depth-≤b trees or probability-averages of them;
   - binary features and no order or mode effects.

   The degree condition excludes almost every model people actually audit: thresholded ensembles, boosted trees deeper than b, and any logistic or neural model on more than b features are not identifiable in this framework. The paper does not show a single deployed scenario where all the conditions hold. The survey and clinical motivations are plausible, but they read as motivation for a survey-methodology or statistics venue, not as an ML evaluation problem.

2. **[major] For the headline experimental setting, the adaptive optimum is trivial.** For a single screening tree of depth b, branching just administers the tree and takes a plain mean. So Q1 for trees reduces to "how much do you lose if you cannot administer the rule as designed?", with an answer of about 1.0–2x. The setting where the comparison is non-trivial is the forest contrast, and it is studied only at toy scale: 20 trees of depth 2–4, forests trained on 60–1000 records, m ∈ {6, 9, 12} median-binarised features, and evaluation laws supported on ~120–390 of 4096 cells. There the paper itself notes that the cap costs more than pre-commitment.

3. **[major] The theory's headline and the empirical reality point in different directions, and the theory does not predict the empirics.** The sharp constant is 2^(b-1) (32 at b = 6); observed ratios are 1.0–2.38. The interpretable bracket [1/ρ², N_P] is loose by a median factor of 1.31 below and 4.3 above. Theorem 4(b)'s neighbourhood is non-explicit, so by the authors' own statement it "does not predict these values". The practically relevant numbers therefore come entirely from the solver, and the long theoretical development (most of the 50-page appendix) contributes little to what a practitioner learns. Conversely, the exponential lower-bound instances (address and pointer functions) are not shown to resemble any trained rule.

4. **[major] Scalability.** Pricing costs on the order of C(m,b)·4^b. Adaptive classes were solved only for m ≤ 12, b ≤ 6 (and m = 20 at b = 3). Several runs are "not computed", b = 4 forests did not finish for m ≥ 9, and b = 6 two-round optima are only upper-bounded. Real questionnaires, lab panels and ML feature sets have m in the tens to hundreds. No scalable heuristic with a quality guarantee is offered for that regime, and the loose bracket gives no usable guidance there. The restriction to "forms on the rule's items" for the 21- and 57-feature experiments sidesteps the issue rather than addressing it.

5. **[major] A design optimised for one rule is close to useless for another.** Reusing records for a different tree costs 1.55–317x. In ML practice models are retrained and compared continuously, so an evaluation dataset tied to one frozen rule is a severe limitation. The joint design for three known trees (Appendix F.6) is a start, but a robust or minimax design over a class of plausible future rules is the practically relevant object and is absent.

6. **[major] Presentation is not accessible to an ML audience and the main body is not self-contained.**
   - The eight pages compress four multi-part theorems, several constructions, a solver and a very large number of experimental figures into dense prose.
   - Theorem 3 bundles three separate results, each resting on appendix propositions.
   - Section 6 is largely a stream of numeric ranges with pointers to more than 15 appendix tables.
   - Terminology ("interview", "form", "audit", "contrast", "menu") comes from survey statistics and is not translated.
   - The Table 2 caption is a paragraph, and Figure 3 is too small to read the two-round results.
   - A 63-page manuscript with roughly 50 pages of proofs and tables is beyond what can be verified in a conference review cycle.

7. **[minor] "Populations" are smoothed empirical laws.** Every reported constant is computed at a held-out empirical distribution mixed with 1% uniform mass, often with very sparse support relative to the cube. These are exact constants for a synthetic population, not estimates with uncertainty for the real one. The bootstrap and smoothing sensitivity checks help, but the main text should say plainly that Q1–Q3 are oracle computations and that only Figure 3b / Table 22 involve sampled audits (on 12 BRFSS trees only).

8. **[minor] Binarisation.** Continuous features are median-binarised before training. In practice one query of a lab value reveals the whole value and a tree may threshold it at several points. The binary-cube model changes both the trees and the price of a query. The s-ary extension is asserted in the appendix but not exercised empirically.

9. **[minor] Inconsistent headline numbers for the pairwise model.** The abstract says "at most 1.28", the introduction "1.02–1.28", Section 6 and Section 8 "1.02–1.13", and Table 3 shows medians up to 1.18. These refer to different run subsets (the 1.28 comes from 26 runs in Appendix F), but the reader cannot tell this from the main text.

10. **[minor] Finite-sample guarantees are weak.** The finite-sample minimax bracket carries a factor of 10^4, and the W-ratios are asymptotic "many records per cell" statements with no sample-size threshold. The design-based intervals from the cross-fitted score cover as low as 0.870 in some cells of the simulated audits, which deserves comment given that the design-based route is recommended when claims "must not rest on a model".

11. **[minor] Novelty of individual technical pieces is moderate.** The non-adaptive simulation of depth-b trees is folklore in query complexity. The address and pointer constructions are the standard hard instances. Theorem 3 is c-optimal design plus standard duality. The contribution is the transfer, the exactness, and the model analysis in Theorem 4, which is the most novel part but is the least connected to the experiments.

12. **[minor] Verification burden.** The paper discloses that a generative model participated in deriving and checking proofs. This is not a problem in itself, and the parts I checked are correct, but combined with the appendix length it raises the bar for independent verification of Theorems 2(b,c) and 4(b–d), which I could not fully check.

**Soundness**: 3 — The proofs I spot-checked (Thm 1 simulation, address lower bound, Thm 3(c) lower bracket, the 0.37b round claim) are correct and the experiments are certified and candidly reported. The empirical claims are oracle constants at small, smoothed empirical laws, and the bulk of the appendix could not be verified.

**Presentation**: 2 — Precise but extremely dense, written in survey-statistics vocabulary, with the main body functioning as an index into a 50-page appendix; not self-contained for an ML audience.

**Significance**: 2 — A clean answer to a narrow question; the ML-facing use case (free labels, hard feature cap, one known low-degree rule, binary features, m ≤ 12) is restrictive, and the measured gains are modest and mostly attributable to standard design optimisation.

**Originality**: 3 — The question and the exact "price in records" framing, the round-by-round analysis and the model-dependence results are new; the individual tools and hard instances are largely classical, as the authors acknowledge.

**Key Questions for Authors**

1. Can you point to a concrete ML evaluation or audit scenario, ideally with real constraints documented, where labels are free, a hard per-record feature cap binds, the audited rule has degree ≤ b, and the rule is fixed before collection? A convincing, worked real case would raise my Significance score and could move me to weak accept. If the honest answer is "split-questionnaire validation of a paper screening tool", the paper is better suited to a statistics or survey-methodology venue.
2. What does the framework deliver for targets that are not identifiable under the cap (thresholded forests, boosted trees with depth > b, logistic models on more than b features)? The appendix mentions an irreducible error δ and a bias-variance program Φ_n. Is there an experiment showing a usable bias bound plus variance for such a model? A positive result would substantially widen the scope and address weakness 1.
3. How do you obtain good, certified-near-optimal fixed and two-round designs at m ≈ 50–100 and b ≈ 8–10? Is there a greedy or restricted-menu heuristic with a provable or empirically tight gap, for example path sets plus the dual certificate? Evidence that the method scales beyond m = 12 would address weakness 4.
4. For the multi-rule problem, what is the price of a design that is minimax over a class, e.g. all depth-b trees on a given item set, or a set of candidate retrained models? If the price is a small constant, that would largely answer weakness 5. If it reverts to uniform-form performance (2–4x or worse), that should be stated as a central limitation.
5. How sensitive are the forest ratios in Table 4 to the sparsity of the evaluation law (121–388 occupied cells of 4096) and to the 1% smoothing mass, and what happens with non-binarised or multi-threshold features? If the ratios move materially, the Q1 conclusions for ensembles are not established; if stable, weakness 7 is resolved.

**Limitations**

Yes. Section 8 ("Scope", "What the constants mean") is candid and covers most of what I raise: single known rule, degree restriction, free labels, order effects, asymptotic nature of W, the 10^4 finite-sample factor, unweighted smoothed populations, and solver scale. I would add two things explicitly: (i) that all Q1–Q3 constants are oracle computations at smoothed empirical laws rather than outcomes of sampled audits, and (ii) that the theory's bounds do not predict the empirical ratios.

**Overall Recommendation**: 3 — Weak reject

The paper has clear merits: a neat exact simulation theorem with a tight constant, an honest empirical study, and a correct, careful treatment. From the standpoint of ML evaluation practice, the weaknesses outweigh them for ICML: the setting is narrow and its ML relevance is under-motivated, the non-trivial experiments are toy-scale, the theory does not explain the modest empirical gaps, and the presentation is not self-contained for this audience.

**Confidence**: 3 — I am confident in my assessment of the setting, experiments and the proofs I checked (Thm 1, parts of Thm 3). I did not verify Thm 2(b,c), Thm 4, or most of the appendix, and I am less expert in the query-complexity and local-privacy literature the lower bounds draw on.

**What would move you up one point**

- A real, documented use case or case study (even one) where the full set of assumptions holds and the optimised-form or two-round design is run as an actual sampled audit, with valid intervals, against the current practice of uniform matrix sampling or split questionnaires.
- Either an extension to non-identifiable, realistic model classes (bias-bounded estimation of thresholded or deeper models) or a robust multi-rule design with a quantified price.
- A scalable design procedure with certificates or tight empirical gaps at m in the tens to hundreds, replacing the "not computed" entries.
- A restructured main body: state Thm 1 and the practical message up front, cut Thm 4 and the round lower bounds to a paragraph each, give Section 6 one clear table and one readable figure per question, reconcile the pairwise-model ranges, and translate the survey vocabulary for ML readers.

Any two of the first three, plus the rewrite, would move me to 4. The rewrite alone would not.
