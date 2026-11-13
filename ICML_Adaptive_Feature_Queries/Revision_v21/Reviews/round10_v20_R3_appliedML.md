# Round 10 — simulated review R3 (applied ML evaluation) of v20 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 3 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in your own words, not the abstract)

The paper studies a data-collection problem for evaluation. Each sampled record reveals at most b of m binary features (the label is always observed and free), and the goal is to estimate one known functional E[Y d(X)], for example the accuracy of a frozen rule or the accuracy difference of two frozen rules, where d has Fourier degree at most b. The question is how many more records are needed when each record's b feature queries are fixed before the record is seen ("fixed forms") rather than chosen adaptively within the record ("branching", a depth-b decision tree of queries), with r-round batched adaptivity in between.

Main results:
- **Exact simulation (Thm 1).** Any protocol on n branching records is reproduced exactly in law by a fixed-form protocol on a random number of records with mean K·n, K = min{2^(b-1), C(m-1, b-1)}. The method is to guess the tree's padded path set, keep the record if the path completes, and add an acceptance coin. An "address" (indexing) function shows 2^(b-1) is attained.
- **Rounds (Thm 2).** r rounds need at most 2^(b-r); a pointer-chasing construction shows a constant number of rounds can still lose nearly everything.
- **Constants (Thm 3).** The worst-case constant V and population constant W(P) are characterised as convex programs, with a bracket [1/ρ², N_P]. A column-generation solver with dynamic-programming pricing over trees returns primal/dual certified optimal designs for each protocol class.
- **Working models (Thm 4).** The simulation bound holds in every parametric model. The gap is at most 2 under features independent given the label (and 0 if forms may depend on the label), polynomial in b near product laws for bounded-order log-linear models, and again exponential under strongly coupled pairwise laws.
- **Experiments.** On depth-b CART screening trees (BRFSS, thyroid, Spambase) and small random-forest updates (WDBC, Spambase, Ionosphere), with m ≤ 12 (up to 21/57 raw variables but rules with ≤ 13 items) and b ≤ 6:
  - optimised fixed forms need 1.0–2.38× the records of branching;
  - uniform randomisation is far worse (2–4×, or 9–23× over all items);
  - two rounds are within 1.32× of branching;
  - a pairwise working model shrinks the price to ≤ 1.28× but adds a non-vanishing bias.

**Strengths**

1. A clean, well-posed question with a complete worst-case answer. I checked the proof of Thm 1(i) (Appendix C.1, Thm C.1) and it is correct and elegant. For every profile exactly one padded path set completes, so success has probability 1/|S_τ| independent of the record, and the acceptance coin makes the simulation exact in law with a geometric record count. This is a comparison of experiments, so it covers every estimator, loss and model at once. The matching address-function lower bound (C.1.4) is also correct as far as I checked.
2. The population-level version (Thm E.1) is done carefully. The centring trick (returning c + L(H − c)) is needed to make the K-factor a bound on variance rather than second moment at accurate rules, and the proof I spot-checked is sound.
3. The experimental section is unusually honest for a theory-driven paper.
   - It compares optimised designs of each class rather than a strawman.
   - It separates "design optimisation" from "adaptivity" (Q2), which is the most practically useful finding.
   - It reports cases with no gap (thyroid, rules with ≤ b items).
   - It reports where the working model fails: bias equal to variance at about 69k records, coverage down to 0.855.
   - It reports that designs are useless for other rules (1.55–317×) and that imputation from complete records beats every capped design when it transports.
4. Certified numbers. Every reported constant comes with primal and dual bounds; uncomputed cases are flagged, not extrapolated. Pointwise unbiasedness of the design-based score is independent of the reference law used to tune it, a property practitioners care about.
5. The related-work positioning is candid: the 2^q simulation is called folklore, and the programs are identified as c-optimal design plus AIPW scores. The "In practice" paragraph gives actionable guidance.

**Weaknesses** (numbered; mark each as [major] or [minor])

1. [major] **The setting is narrow and its practical motivation for an ML audience is not convincing.** The model requires all of the following at once:
   - a hard per-record cap on features, not a cost or mean budget (under a mean budget the gap is at most m/b, as the paper notes);
   - labels that are free and observed for every record;
   - a single target functional, known and frozen before collection;
   - binary features;
   - a rule of Fourier degree ≤ b, which excludes thresholded ensembles, boosted models, anything with continuous inputs, and essentially all modern models;
   - an operational reason why questions must be pre-committed.

   No concrete deployed scenario is given in which all of these hold. In ML evaluation the label is usually the expensive item; in the paper's own screening example the label is a diabetes diagnosis. Modern surveys and clinical decision support are computer-administered, where skip logic is essentially free. The paper acknowledges that for a single screening tree the adaptive optimum is "administer the rule and take a plain mean", so the headline comparison "prices paper forms against computer-assisted administration". That is a legitimate question for survey methodology, but its importance for ICML readers is not established.

2. [major] **The empirical stakes are small and the regime is tiny.**
   - On real rules the price is typically about 1.3–1.6× (max 2.38×), drops to ≤ 1.32× with one follow-up batch, and to ≤ 1.28× under a pairwise working model. The exponential worst case therefore appears to be a property of adversarial index/pointer functions, not of trained rules.
   - Everything is computed for m ≤ 12, b ≤ 6 (m = 20 only at b = 3), 20-tree depth-≤4 forests, and rules with ≤ 13 items. Five rules were not computed, and b = 4 forests ran only at m = 6.
   - Pricing costs on the order of C(m,b)·4^b, so the solver, which the paper says "is needed" because the analytic bracket is loose (e.g. [1.13, 10.5]), does not reach the scale of real questionnaires or feature sets.

   The practitioner take-away reduces to "optimise your split-questionnaire design for the target instead of randomising uniformly". That is useful, but it is a c-optimal-design message more than an adaptivity message.

3. [major] **The cap is always set equal to the rule's depth.** This is the knife-edge most favourable to branching: branching then attains the full-information variance. A validation study is not obliged to use the same burden as the rule. I could not find, for the real rules, how the fixed/branching ratio decays when the cap is b+1, b+2, …, K; at cap K it is exactly 1 (only a synthetic budget curve, Thm C.4/Fig. 4, is given). The forest results suggest the cap itself, not pre-commitment, is the dominant cost (1.4–4.1× vs. complete records). Without this curve it is hard to know whether the reported 1.35–1.58 is robust or disappears with one or two extra questions.

4. [major] **Presentation is too dense for the main track audience and not self-contained.** Eight pages carry four multi-part theorems, a solver, three experimental questions and about a dozen distinct constants (V, W, W_r, W^T, W^(k), W^ci, W^lab, K_{m,b}, K_r, ρ²_P, N_P, ν_k, L_k), followed by about 55 pages of appendix.
   - Section 6 is largely numbers in running prose.
   - Table 2 has ten columns with a seven-line caption and mixed entry types (medians, ranges, bounds with ≤/≥).
   - Survey vocabulary ("interview", "form", "audit", "tables", "contrast") is layered on ML vocabulary without a single formal definition of the estimator a practitioner would compute.
   - Theorem 4 has five parts whose proofs are entirely in the appendix.
   - The abstract is hard to parse on first reading.

   I could verify Thms 1 and E.1 but could not realistically verify Thm 2(b,c), Thm 4(c–e) or the solver within a normal review budget. The appendix also contains leftover artefacts, such as a script path inside the text of the discussion of Thm E.5(b).

5. [major] **The single-functional restriction undermines the evaluation use case.** Evaluation data is almost always reused for several models, metrics, subgroups and later model versions. The paper's own check shows records collected under one rule's optimal design can need up to 317× the records for another tree of the same depth on the same items. A joint design for three known rules costs +10% median (up to +51%). The comparison that matters in practice is against a robust, rule-agnostic design; that is the 9–23× "uniform over all items" row, which is not analysed further.

6. [minor] **The reference-data setting partly begs the question.** The "fitted" designs use 20,000 complete, labelled source records. In the random-half setting those records already estimate the accuracy directly. In the shifted settings the paper shows imputation from them beats every capped design unless transport fails (biased in 3 of 8 pre-specified shifts). The pilot-based alternative costs 11–20% over the oracle with model smoothing, is "too small" at b = 6, and has no non-asymptotic guarantee. The connection of the fitted-table score to AIPW/prediction-powered estimators (the tables as a learned augmentation) is not spelled out for ML readers.

7. [minor] **Asymptotic constants only.** Ratios of W are first-order and tuned to P. The finite-sample theorem carries a factor of 10^4. The simulations support the ordering at n ≥ 500 on 12 trees, but confidence-interval coverage for the design-based score dips to 0.87–0.89 for at least one tree.

8. [minor] **Reporting conventions make headline numbers harder to interpret.** Medians in Table 3 are "over runs with a gain". Populations are empirical laws mixed with 1% uniform mass, with sensitivity shown only for the forest tasks at b = 3. BRFSS is used unweighted. No field audit was run. All are disclosed, but the abstract's "1.0 to 2.38 where it could be computed" hides a fair amount of conditioning.

9. [minor] **Technical novelty is moderate.** The core simulation is a short argument, and the paper itself calls the 2^q conversion folklore. The lower bound uses the standard indexing function, the rounds result uses pointer chasing, and the programs are c-optimal design and AIPW. The contribution is the exactness and sharp constant in this statistical framing plus the model-dependence results, which is a worthwhile synthesis but not a new technique.

**Soundness** (1-4) with one-line justification

3 — The proofs I spot-checked (Thm 1(i)/C.1, address lower bound C.1.4, Thm E.1(a–c)) are correct and the numerics are certified; I did not verify Thm 2(b,c), Thm 4(c–e) or the solver, and experimental claims are asymptotic oracle constants at smoothed empirical laws.

**Presentation** (1-4) with one-line justification

2 — Precise and honest, but severely over-compressed: too many constants and results for eight pages, tables and prose are hard to parse, and the paper is not self-contained for an ML reader without the long appendix.

**Significance** (1-4) with one-line justification

2 — A definitive answer to a narrow question; on real rules the price is about 1.5× and largely removed by one follow-up round, and the setting (free labels, hard cap, one known low-degree rule on ≤ 13 binary items) is far from mainstream ML evaluation practice.

**Originality** (1-4) with one-line justification

3 — Pricing within-record adaptivity in records with exact constants, a round hierarchy and model dependence is new as far as I know, although the ingredients (path guessing, indexing/pointer functions, c-optimal design, AIPW) are standard.

**Key Questions for Authors** (3-5 numbered; for each, say how the answer would change your evaluation)

1. **A concrete use case.** Can you give at least one concrete, current scenario (ideally with a citation or data) in which (a) per-record feature queries are hard-capped, (b) the questions must be pre-committed, (c) labels are available for every record at negligible cost, and (d) the estimand is the accuracy of one frozen low-degree rule? A convincing case with numbers would raise my significance score and likely my overall score by one point. If the honest answer is "paper questionnaires and batched lab panels", I would keep my score.

2. **Cap versus depth.** For the BRFSS and Spambase trees, what is W_fixed/W_branch (and both relative to complete records) as the audit cap grows from the rule depth b to the number of items K the rule uses? If the gap persists for several extra questions, the practical message is stronger. If it collapses at b+1 or b+2, the message is "ask one more question", and pre-commitment is of little practical importance.

3. **Rule-agnostic and multi-target designs.** What is the price of pre-commitment when the design must serve a family of targets, e.g. all depth-b trees on the K items, a few subgroup accuracies, or the next model version, rather than one rule? Is there a minimax-over-family version of your program, and how does its fixed/branching ratio compare with the single-rule numbers? Showing that the single-rule numbers are representative, or giving a tractable robust design that stays within about 2×, would address Weakness 5 and raise significance.

4. **Scalability.** Can the solver, or a certified relaxation or heuristic (e.g. the path-set menu of Prop. E.6, whose optimum you say is within a few percent of all-forms), produce useful designs at realistic sizes such as m ≈ 50–100 items, b ≈ 8–10, and gradient-boosted or deeper forests? Evidence that the path-set heuristic gives near-optimal fixed designs with a certified bracket at such sizes would make the contribution usable and would move me up.

5. **Relation to AIPW and prediction-powered inference.** Is the fitted-table design-based score exactly the efficient AIPW score with the augmentation computed from the reference law? If so, how does a standard PPI-style estimator perform on the same forms: a predictor of t trained on the source records, plus an inverse-probability rectifier on path-completing records? This would clarify what is new in the estimator versus the design, and help position the paper for the evaluation community. It affects presentation and originality more than the overall score.

**Limitations** ("yes" if adequately discussed, otherwise constructive suggestions)

Yes. Section 8 is candid about free labels, a single known low-degree target, order effects, asymptotic constants, unweighted smoothed populations, the absence of a field audit, and solver scale. Two suggestions:
- State in the abstract or introduction that for a single tree the adaptive optimum is trivially "administer the rule", so that the comparison is in effect capped pre-committed data against full-information data.
- Move the cap-equals-depth caveat and the multi-rule reuse result (1.55–317×) into the main limitations text rather than "Further checks".

**Overall Recommendation** (integer 1-6, with label)

3 — Weak reject. The paper is technically solid, careful and honest, with a neat exact-simulation theorem and a sharp constant. For the ICML main track, however, the practical significance is limited (narrow setting, tiny scale, modest and easily recovered empirical gaps), and the presentation is too compressed for the audience it targets. I would not be upset to see it accepted on the strength of the theory; a statistics or survey-methodology venue, or a longer journal format, seems a more natural fit for the current manuscript.

**Confidence** (1-5)

3 — I am confident in my assessment of the setting, experiments and significance for ML evaluation. I verified the main simulation theorem and the population bracket, but not the round-hierarchy lower bounds, the model-dependent results (Thm 4 c–e) or the solver internals.

**What would move you up one point** (concise, concrete list; be honest — if nothing realistic would, say so)

- A real, documented use case meeting the assumptions (Q1), stated up front, with the free-label assumption justified or relaxed in at least one experiment.
- The cap-versus-depth curve on the real rules (Q2), showing the gap is not a knife-edge artefact of cap = depth.
- Either a multi-target/robust design result (Q3) or evidence that a certified heuristic scales to realistic m and b and to non-toy ensembles (Q4).
- A restructured main text: one formal statement of the estimator and design program a practitioner would run, Thm 4 reduced to its two or three key parts, Section 6 reorganised around one or two readable figures instead of number-heavy prose, and Table 2 simplified.

Any two of the first three plus the presentation fix would move me to 4. I do not see a realistic path to 5 without a substantially broader setting (costly labels, non-binary features, or higher-degree targets).
