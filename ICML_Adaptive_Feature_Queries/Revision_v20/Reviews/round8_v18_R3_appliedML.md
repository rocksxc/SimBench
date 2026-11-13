# Round 8 — simulated review R3 (applied ML evaluation) of v18 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 3 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in your own words, not the abstract)

The paper studies estimating a known population functional, mainly the accuracy (or accuracy difference) of frozen binary-feature rules, Δ(P) = E[Y d(X)], when each sampled record may reveal at most b of m binary features and the label is always observed for free. It compares three ways of choosing the b features per record: a set fixed before the record is seen ("fixed forms"), r batches chosen from earlier answers, and a fully adaptive depth-b decision tree ("branching"). The question is how many more records non-adaptive acquisition needs.

Main results:

- **Exact characterization (Thm 1).** The first-order minimax MSE constant of any finite interview menu is a convex program with an explicit dual. A population-specific constant W_A(P) is defined as a c-optimal design problem and shown to be a local asymptotic minimax risk.
- **Universal gap (Thm 2).** Fixed forms can simulate any branching protocol exactly with K = min{2^(b-1), C(m-1, b-1)} times the records, by guessing the tree path's coordinate set. This is tight for an address (index) function.
- **Rounds (Thm 3).** r rounds need at most 2^(b-r) times the records; pointer-tree constructions show a few rounds can still lose nearly the full exponent.
- **Population bracket (Thm 4).** The ratio lies between 1/ρ²_P and a Rényi-1/2 effective path count N_P.
- **Models (Thm 5).** Under an order-k log-linear model the gap is at most (b+1)^k near product laws and exactly 1 for the extremal example at k = 2, but strongly coupled pairwise laws restore 2^(b-1)/b.
- **Computation and experiments.** A column-generation solver with DP pricing certifies optimal designs for each class. On CART screening trees (BRFSS, thyroid; 12 binary items, b ≤ 6) and small random-forest updates (three UCI sets, m ≤ 12, b ≤ 4), optimized fixed forms need 1.0–1.98× the records of branching without a model and 1.02–1.13× under a fitted pairwise model. Two rounds recover most of the gap. In resampled "audits", pairwise MLE on fixed forms is about as accurate as on branching records up to n ≈ 8,000, with model bias taking over at larger n.

**Strengths**

1. The question is clean and answered thoroughly: worst case, per-population, per-round and under a model, each with matching upper and lower statements and an explicit list of what remains open.
2. The simulation argument (Thm C.1) is simple and strong. It compares experiments, so it holds for every estimator, loss, sample size and model. I checked it, together with the centered path-guessing score (Thm E.1(a)–(c)), the finite-sample converse and van Trees argument (B.3.2–B.3.3), and the local-minimax proposition (C.8), and found no errors.
3. Theorem 5 is the most original part. It shows the worst-case exponential gap is driven by dependence rather than parsimony, vanishing under a pairwise model near product laws and returning under strong couplings. This is useful conceptually for anyone analysing planned-missing data with working models.
4. The experiments are unusually honest. Every constant has primal/dual certificates, unclosed programs are reported as brackets, and the pilot is charged. Negative findings are reported: thyroid ratios are all 1.00, the Theorem 4 bracket is loose, the pairwise MLE under-covers at large n, and reuse of records for another rule can cost up to 317×.
5. The baselines for the estimation side are reasonable: uniform matrix sampling, uniform over tree paths, Horvitz–Thompson tables, regression and multiple imputation from source records, EM maximum likelihood, and a cross-fitted model-assisted score.
6. The limitations section is candid and specific about free labels, the single known target, order effects, ignored survey weights and solver scaling.

**Weaknesses** (numbered; mark each as [major] or [minor])

1. **[major] The setting is narrow and weakly motivated for an ML audience.** Four assumptions must hold together: labels are free and always observed; a hard per-record feature cap applies; the target is one known functional of Fourier degree ≤ b fixed before collection; and features are binary. This is the reverse of the usual ML evaluation cost structure, where labels are expensive and features cheap.
   - For a single screening tree, the adaptive optimum is "administer the rule and average t". The headline comparison then prices paper forms against computer-assisted administration of the same rule, as the authors acknowledge.
   - For forests, the scenario is harder to believe. Deploying a 20-tree forest needs all its features on every case, so it is unclear why an audit of it would be capped at b = 3 features per record.
   - The paper's own Table 3 shows the cap costs far more than pre-commitment there: 1.4–4.1× for fixed designs versus complete records, and up to 5.9× in Table 6.
   - Appendix F.10 shows complete records undercut fixed forms once a label costs more than 4–15 feature questions.

2. **[major] The identifiability requirement excludes most deployed ML models.** The target must satisfy deg(d) ≤ b. The paper notes this "fails for most thresholded ensembles at small caps", so the forest experiments use differences of predicted probabilities, a soft-accuracy functional rather than the accuracy of the thresholded classifier. Boosted ensembles, neural models and continuous features (here median-binarized) are outside the theory except through the irreducible error δ of Appendix B.2, which is not explored empirically. This sharply limits the "evaluation of deployed ML systems" framing.

3. **[major] The practical payoff is modest, and the paper's own evidence says so.**
   - Without a model the realized gap is 1.0–1.98× (medians about 1.3–1.6×), against a worst case of 2^(b-1) = 8–32 at these caps.
   - Two rounds remove almost all of it; a pairwise working model reduces it to about 1.05×.
   - For forests, restricting branching to the forests' own trees captures only 17–49% of the log-gap (ratios 1.03–1.10 in Table 6). The adaptive gain there requires solving for optimal trees over all depth-b trees.
   - The largest practical effect in the paper is not adaptivity. Uniform matrix sampling costs 9–23× the records of branching, while optimized fixed forms cost about 1.5×. That gain comes from classical c-optimal design and known-coarsening AIPW scores, which the authors credit to prior work.
   - The honest take-away is "adaptivity rarely matters much; optimize your fixed design, or add one adaptive round". That is useful, but it is a weaker and less novel message than the title and abstract suggest.

4. **[major] The empirical base is small and consists mostly of computed population constants.**
   - Non-trivial screening results come from one dataset (BRFSS): 24 runs, 18 with a gain, six runs per cap. The trees have accuracy 0.60–0.75 and often very few distinct paths.
   - Thyroid contributes only 1.00s.
   - The forest tasks use held-out "populations" of 171–3,101 records occupying 3–10% of the 4,096 profiles, smoothed with 1% uniform mass.
   - Reported ratios are oracle-design, local-asymptotic constants at these smoothed empirical laws. The "audits" are resampling simulations from the same laws.
   - No real data were collected adaptively versus non-adaptively. The one robustness probe for order/mode effects (F.9) shows biases of 1.5–2.2 standard errors at n = 1,000 under a mild 10% flip model, the same order as the efficiency differences being measured.

5. **[major] Scalability.** The solver costs O(C(m,b)·4^b) per iteration. Adaptive classes were solved only for m ≤ 12, b ≤ 6, and for m = 20 at b = 3. Four two-round programs at b = 6 did not close in an hour, and b = 4 at m = 20 returned an uninformative bracket. The claims that two rounds suffice and that a pairwise model removes the gap are therefore untested at realistic scale (dozens to hundreds of features, deeper rules). No scalable heuristic with guarantees is offered beyond the path-set design.

6. **[major] Presentation is very dense and not self-contained for an ML reader.**
   - The 8-page body states five multi-part theorems, a solver and three experimental studies; essentially every proof, protocol and definition is deferred to a 50-page appendix.
   - The abstract is a long list of constants that cannot be parsed before reading the paper.
   - Survey vocabulary ("forms", "interviews", "booklets", "audits") is used throughout without mapping to ML terms.
   - The Table 2 caption is a paragraph; Table 3 columns ("Own", "Fit", "Cap: /full") are cryptic.
   - κ is used with two meanings on the same page (⌊log₂ b⌋ in Thm 2(iii), b−1 in the proof idea).
   - Three different b = 4 medians appear (1.49 over all runs, 1.52 over runs with a gain, 1.50 in F.8) without a clear signpost.
   - The scope is that of a long journal article (Annals/JASA/JMLR); as an 8-page conference paper the reader gets headline numbers and must take the rest on trust.

7. **[minor] "Exact" and "records ratio" need more prominent qualification.** W-ratios compare oracle designs tuned to P, in a local asymptotic sense, at full-support laws. The finite-sample theorem carries a factor of 10⁴. The at-every-P inequality in Thm 2(ii) uses a score centered at the unknown Δ(P). The authors state all of this, but mostly in Table 1's caption and the final paragraph. The pilot study (10–35% above oracle, with b = 6 needing model smoothing to avoid 4.33×) shows the oracle numbers are not what a practitioner gets.

8. **[minor] Related work misses the ML/optimization literature on the same conceptual question.** Not discussed:
   - adaptivity gaps in stochastic optimization and adaptive submodularity (Golovin & Krause; Dean–Goemans–Vondrák; stochastic probing);
   - limited rounds of adaptivity and batched bandits (Agarwal et al. 2017; Perchet et al. 2016; Gao et al. 2019);
   - adaptive versus static Bayesian experimental design;
   - adaptive versus non-adaptive group testing;
   - the folklore fact that a q-query adaptive tester is simulated by 2^q non-adaptive queries, of which Theorem 2(i) is the per-record-cap analogue.

9. **[minor] The model-based comparison in the audits is not like-for-like.** "Branching" in Table 20 is the rule's own padded tree, not the model-optimal branching design that Table 18 uses. The MSE ratios for pairwise ML range up to 4.97 for individual trees. The "about one" summary rests on medians over 12 trees with wide quartile bands (Fig. 3b), and the pairwise MLE under-covers (0.855–0.953 at n = 16,000).

10. **[minor] Verification burden.** Appendix H discloses that a generative model took part in deriving and checking proofs. That is within policy, and the parts I checked are correct. Still, Theorem 3(b,c) (potential argument, "checked exhaustively ... and on random states") and Theorem 5(c,d) are long and should be verified by a theory reviewer; I did not verify them.

**Soundness** (1-4) with one-line justification

3 — The proofs I spot-checked (Thms 1, 2, 4; C.1, C.8, E.1) are correct and the numerics are certified; reservations are that the constants are oracle/local-asymptotic and that I did not verify the round lower bounds or Theorem 5(b–d).

**Presentation** (1-4) with one-line justification

2 — Precise and candid, but overloaded and not self-contained in 8 pages; heavy jargon, an unreadable abstract and cryptic tables make it hard going for the ICML evaluation audience.

**Significance** (1-4) with one-line justification

2 — A complete answer to a clean question, but in a setting (free labels, hard cap, binary features, degree-≤b known target, m ≤ 12) with little reach into ML evaluation practice, and with small realized gaps.

**Originality** (1-4) with one-line justification

3 — The qualitative separation and the design/duality tools are classical, as the authors say; the exact constants, the exact simulation with a per-record cap, the round-by-round accounting and especially the model-dependence results (Thm 5) are new.

**Key Questions for Authors** (3-5 numbered; for each, say how the answer would change your evaluation)

1. **Is there a concrete ML deployment scenario for this cost structure?** I am looking for one where labels are free for every sampled record, features are hard-capped per record at about the rule's depth, within-record adaptivity is operationally feasible, and the target is a single pre-specified low-degree functional. For the forest experiments in particular, why would the audit be capped at b when the forest needs all its features at prediction time? A convincing scenario, ideally with data from it, would raise my Significance score and could move me to weak accept.

2. **What happens when deg(d) > b?** This covers thresholded forests, boosted ensembles and continuous features. Can the framework give a useful bias–variance statement using δ from Appendix B.2, and what do the fixed/branching comparisons look like empirically for such targets? If the approach degrades gracefully and the gap conclusions persist, weaknesses 1–2 would be substantially weakened.

3. **Do the two empirical regularities survive at scale?** The regularities are "two rounds recover ≥80% of the log-gap" and "a pairwise model reduces the gap to about 1.05×". I would want m in the tens to hundreds, b ≥ 8, more datasets, and trees that are not class-balanced CART with few paths. Is there a scalable approximate solver or bound, for example path-set designs plus a certified dual, that could show this? Evidence here would address weaknesses 4–5 and raise both Soundness of the empirical claims and Significance.

4. **How much of the benefit is adaptivity and how much is design optimization?** Uniform matrix sampling costs 9–23× while optimized fixed forms cost about 1.5×. Is the main practical contribution the optimized fixed design, and how does it compare with existing model-based optimal split-questionnaire designs (Adigüzel & Wedel; Chipperfield & Steel) on the same data? If the optimized fixed design is itself shown to be a clear advance over that prior art, I would weigh the practical contribution more heavily. If it is essentially known, the practical case rests on the 1.0–2.0× adaptivity gap alone.

5. **What should a practitioner do before collecting data?** The Theorem 4 bracket is loose, the solver needs the population, and pilots at b = 6 need model smoothing. Is there a validated, cheap pre-collection diagnostic for when adaptivity is worth implementing? The "screen at 1.05" in F.2 was evaluated in-sample on the same tasks. An out-of-sample-validated decision rule would make the paper considerably more useful to the audience I represent.

**Limitations** ("yes" if adequately discussed, otherwise constructive suggestions)

Mostly yes. Section 9 is unusually forthright about free labels, the single known target, order effects, oracle/asymptotic constants, ignored survey weights and solver scaling. Suggestions:

- State prominently, in the abstract or introduction, that targets must have degree ≤ b, which excludes thresholded ensembles and most deployed models.
- State there too that all reported ratios are oracle-design local-asymptotic constants at smoothed empirical laws.
- Say explicitly that non-trivial screening-tree gaps were observed on a single dataset.
- Say explicitly that for ensembles the adaptive gain requires optimizing over all depth-b trees rather than using the models' own trees.

**Overall Recommendation** (integer 1-6, with label)

3 — Weak reject.

The theory is careful and, as far as I checked, correct, and the paper is admirably honest. From the standpoint of evaluation methodology for ML systems, though, the setting is narrow, the model class it covers is small, the experiments are tiny-scale computations of population constants, and the measured value of adaptivity is modest. The presentation packs a journal-length paper into 8 pages. I would not block acceptance if theory and statistics reviewers verify the remaining proofs and judge the exact-constant results significant in their own right. On the criteria I was asked to weigh — practical significance, realism, convincing experiments, clarity for an ML audience — the weaknesses currently outweigh the merits.

**Confidence** (1-5)

3 — I read the main body in full and checked Appendices B.3, C.1, C.5.2, E.1 and most of F. I did not verify Theorem 3(b,c) or Theorem 5(b–d), and I may be missing closely related results in survey methodology or TCS.

**What would move you up one point** (concise, concrete list; be honest — if nothing realistic would, say so)

- A concrete, credible ML or auditing use case matching the cost structure (free labels, hard per-record cap, feasible adaptivity), preferably with an experiment on data from it. Failing that, an extension with label costs or a relaxable cap in the main analysis rather than a short appendix note.
- Evidence beyond m ≤ 12, b ≤ 6 and binary features: more datasets with non-trivial gaps, larger m and b via a scalable approximate solver with certificates, and at least one experiment with deg(d) > b targets (thresholded ensembles) using the approximation-error version.
- A restructured main body: fewer theorems in full generality (for example, move the polynomial-dimension round results and Thm 5(c,d) details to the appendix), a readable abstract, ML-facing terminology, and a clear "what a practitioner should do" paragraph backed by an out-of-sample-validated diagnostic.
- A clear separation of the gain from design optimization and the gain from adaptivity, with comparison to existing optimal split-questionnaire designs.

The first two items are substantial new work. The last two alone are realistic for a rebuttal or camera-ready but would probably move me only to a borderline 3/4, not a firm 4.
