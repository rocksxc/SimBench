# Round 6 — simulated review R3 (applied ML evaluation) of v16 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 3 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words, not the abstract)

The paper studies a measurement problem that reverses the usual active-testing cost structure. Every sampled record has its label observed for free, but at most b of m binary features may be queried per record (a hard per-record cap). The target is a known functional of Fourier degree at most b, typically the accuracy of a frozen depth-b tree or the accuracy difference of two depth-b forests. Estimators must be unbiased by design at every feature profile, with no model for unasked features.

The question is how many more records are needed when each record's feature subset is fixed before the record is seen ("fixed forms") than when later questions may depend on earlier answers ("branching"), with r-round batch protocols in between.

Theory:
- **Theorem 1.** The first-order minimax constant of any finite protocol class is a convex program with an explicit dual. Adaptation across records and label-dependent choices do not change it.
- **Theorem 2.** Fixed forms need at most K = min{2^(b-1), C(m-1, b-1)} times the records of branching at every population. This is tight for an "address" function and nearly tight in polynomial dimension.
- **Theorem 3.** r rounds lose at most 2^(b-r). A binary pointer tree shows that a constant number of rounds can still lose 2^(b(1-o(1))).
- **Theorem 4.** At a given population the ratio is bracketed by 1/ρ² (best single-form R²) and an effective number of tree paths.

A column-generation solver with dynamic-programming pricing computes certified optimal fixed, r-round and branching designs at an empirical population.

Experiments (three small UCI sets for forest updates; BRFSS and thyroid for screening trees; m ≤ 12, or 21 for fixed forms only; b ≤ 6):
- Optimised fixed forms need 1.0–1.98 times the records of branching.
- One adaptive round recovers most of the gap.
- Naive uniform designs are much worse.
- A two-way log-linear working model fitted to the same capped records beats the design-based estimator at n ≤ 4,000 and loses for a third of trees at n ≥ 16,000.

**Strengths**

1. The question is clean and, to my knowledge, has not been posed in this form. The answer is unusually complete: worst case, per-population bracket, round hierarchy, and a solver that certifies instance-level optima with primal and dual bounds.
2. The paper is candid about the limits of its own message. It reports that a simple model-based estimator is more accurate at realistic sizes, that the cap costs more than pre-commitment for ensembles, that order effects produce biases comparable to the gains, that the pilot-learned design fails at b = 6, and that four two-round programs did not close.
3. The proofs I spot-checked appear correct. These were the path-guessing simulation and its centred version (C.1, E.1), the address-function energy computation, the witness bound of Theorem 4, Proposition E.3, and the structure of the van Trees converse (B.3.3, C.7). I also read the first steps of the pointer-tree potential argument (D.1). The centring device that makes the K bound hold for variances at every population, not only for second moments, is a nice touch.
4. Unbiasedness is exact for fitted and pilot-learned designs, since only variance depends on the reference. This is a useful property for evaluation practitioners, and it is tested: fitted designs cost about 5–7% more, and the all-in pilot cost is reported.
5. The naive-design comparisons (U-paths, U-items, U-all in Table 3) give a practitioner-relevant takeaway. Uniform matrix sampling over all forms costs 9–23 times the records of branching, while optimised forms cost at most 2 times.
6. Certificates, an independent dense implementation, and sensitivity to the smoothing mass are provided, and code is promised.

**Weaknesses**

1. **[major] The setting is narrow and its ML motivation is thin.** It needs all of the following at once:
   - labels observed for every record at no cost;
   - a hard per-record feature cap, since under a mean budget the paper itself shows the gap collapses to m/b (C.5.1);
   - a single estimand fixed in advance;
   - a contrast of Fourier degree ≤ b on binary features;
   - no order or mode effects.

   The degree condition excludes almost every model ML practitioners evaluate, including thresholded ensembles, boosted trees with links, logistic models and neural nets; the paper says identification "fails for most thresholded or link-transformed ensembles at small caps". What remains is depth-≤b trees and probability-averaged forests of such trees on median-binarised features. No concrete ML evaluation scenario is given in which labels are free, features are hard-capped per record, and the evaluator must pre-commit.

2. **[major] For the headline application, the adaptive optimum is trivial.** For a single screening tree, "branching" simply runs the tree on each record and averages Y·d(X). Table 3 confirms it attains the full-information variance. The BRFSS and thyroid study therefore prices a self-imposed handicap: refusing to run the rule one is evaluating. The paper does not argue convincingly when an evaluator could deploy a depth-b branching rule yet must validate it with pre-committed forms. The case where the theory and solver earn their keep is forest updates, where no tree computes the contrast. That case is only run at toy scale: 20-tree forests trained on 60–1,000 records, m ≤ 12, b ≤ 3, and b = 4 only at m = 6.

3. **[major] The empirical effect is small, and the paper's own baseline erases it at practical sample sizes.**
   - Optimised forms cost a median 1.35–1.58 times the records of branching on BRFSS and 1.0 on thyroid.
   - 17 of 24 BRFSS trees are exactly computable in two rounds.
   - A two-way log-linear model on the fixed-form records has RMSE 0.80–0.88 of the design-based form score, "on a par with branching at 0.82", for every tree up to n = 4,000.
   - The authors conclude that at survey sizes "a parsimonious model on optimized forms is therefore the more accurate tool, and adaptivity adds little to it."

   This is honest, but the practically actionable content reduces to two points: do not use uniform matrix sampling, and the design-based constants matter mainly for very large audits or when model-free claims are mandatory. That is a modest payoff for an ICML audience. The exponential worst case is realised only by address and pointer constructions, far from the trained models.

4. **[major] Scale and generality of the experiments.**
   - All features are binary, with m ≤ 12; m = 21 is run for fixed forms at b = 4 only, where the trees coincide with the 12-item ones.
   - b ≤ 6. Solver cost grows as C(m,b)·4^b per iteration; b = 5 at m = 21 and b = 4 forests at m ≥ 9 did not finish.
   - There are five tabular datasets. Screening results are medians over 3 seeds × 2 targets.
   - The "exact" constants are exact for smoothed empirical laws, and the designs are oracle-tuned to those laws, including the centring constant c = Δ(P), which is the estimand itself.
   - When the design must be learned from a pilot, the all-in price rises to 1.65–1.80 at N = 4,000–8,000 and to 3.30 at b = 6, against an oracle 1.58.

   The asymptotic "records ratio" reading needs many records per cell, a regime the paper concedes is beyond typical audit sizes.

5. **[major] Presentation is very dense for a general ML audience.** The 8-page body compresses four theorems, a solver, and about ten experimental sub-studies. The abstract is a wall of constants. The vocabulary (forms, interviews, booklets, contrasts, c-optimality, Elfving dual, van Trees) comes from survey statistics and optimal design and is used with little introduction. Table 3 has 11 columns. Several claims can only be understood from the 48-page appendix, and Appendices G and H are, by the authors' own guide, unused by the main text. I had to read the appendix to understand what "Fitted", "Two fit." and the pilot protocol mean. The paper is not self-contained in 8 pages and reads like a compressed journal article.

6. **[minor] The per-population bracket of Theorem 4 is loose in practice.** On BRFSS the lower end is below the realised ratio by a median factor 1.31 and the upper end is above it by 4.3 (for example [1.08, 5.4] around 1.35 at b = 5). Its value as a planning tool is limited. The reference-data "screen" in F.2 is an after-the-fact rule calibrated on the same runs.

7. **[minor] The worst-case separation is acknowledged as qualitatively known.** Address and indexing functions, pointer chasing, the huge-object model and LDP round separations are prior work. Theorem 1 is assembled from standard duality and van Trees tools, and the population program is c-optimal design with AIPW scores. The new elements are exact variance constants, validity at every population, and the variance-scale round hierarchy. These are real, but incremental for readers outside this niche.

8. **[minor] Some comparisons ML readers would expect are absent.**
   - No hybrid design mixing a small complete-record subsample with capped records in the experiments (only the address function in theory, Proposition C.6).
   - No model-assisted estimator that uses the working model as an augmentation while staying design-unbiased at finite n, with estimated rather than oracle tables.
   - No connection to off-policy or AFA-evaluation estimators beyond a citation.

9. **[minor] Small inconsistencies and things I could not verify.**
   - The main text describes the small-cap pointer-tree numbers as "the constants" computed by the solver. Appendix D.4 says they are values at the uniform law, a lower bound on V_r, with a separate upper bound that differs at b = 4.
   - The smoothing sensitivity is cited as Appendix F.1 but appears in F.2, and covers only 15 forest tasks.
   - "The first-order constant of the biased regime remains open" is confusing given that Theorem 1's converse covers biased estimators; presumably the non-identifiable case is meant.
   - Several 2026 citations could not be checked. The Li et al. (2026) title ("semantic regular expressions") does not obviously match the tree-evaluation round bound attributed to it.
   - The paper discloses that a generative model helped derive and check proofs. With 40+ pages of proofs, some checked "on random states", the burden on reviewers is high. I verified only a subset.

**Soundness** (1-4): 3 — The proofs I spot-checked are correct and the computations are certified. The experimental conclusions are honestly stated but rest on oracle-tuned designs, smoothed empirical laws, few seeds and toy scale, and I could not verify the full appendix.

**Presentation** (1-4): 2 — Precise but over-compressed and written in survey-design idiom. Not self-contained in the main body for an ML reader.

**Significance** (1-4): 2 — A careful answer to a narrow question. On real models the gap is small, and at practical sample sizes it is matched by a simple model-based alternative. Applicability is restricted to shallow trees and forests on a dozen binary features.

**Originality** (1-4): 3 — The framing (price of pre-commitment in records, exact constants per protocol class, variance-scale round hierarchy, certified solver over combinatorial menus) is new. The ingredients and the qualitative separation are known.

**Key Questions for Authors**

1. What is a concrete ML evaluation scenario with free labels, a hard per-record feature cap, a single pre-specified low-degree estimand, and an evaluator who cannot simply run the rule? For a single tree, why is "branching" not just deployment of the rule with logged outcomes? A convincing, realistic use case, ideally with data from it, would raise my significance score and could move me to weak accept.

2. The two-way working model matches branching's RMSE on fixed-form records up to n = 4,000. Is there an estimator that keeps design-unbiasedness and captures most of that finite-sample gain, such as a model-assisted or PPI-style augmentation with cross-fitted tables? What does the fixed-versus-branching comparison look like for such estimators at n = 1,000–4,000? If the price of pre-commitment stays around 1.3–1.6 for the estimators practitioners would actually use, the paper's constants become more relevant. If it vanishes, the practical message is essentially negative.

3. Can the forest-update study, the only one where branching is non-trivial, be scaled to something closer to practice: m in the tens, non-binarised or multi-level features, forests trained on realistic sample sizes, b ≥ 4 at m ≥ 12? Failing that, can heuristic designs with certified gaps be reported where the exact solver does not close? Evidence that the 1.1–1.9 range and the "two rounds suffice" finding persist at larger scale would strengthen the experiments materially.

4. All W-ratios compare designs tuned to the target law, including c = Δ(P). For forest contrasts, what are the realised ratios when both the fixed and the branching design are learned from a charged pilot or a shifted reference, at n of a few thousand? Table 10 covers only screening trees, where branching needs no learning. If the learned-design ratio for ensembles differs substantially from the oracle ratio, the headline numbers need requalifying.

5. Under an average budget of b queries, or a mixed budget where a small fraction of records may be complete, how much of the empirical gap on BRFSS and the forests remains? Since the hard cap is what drives the theory, an empirical version of Appendix C.5 would show how robust the conclusions are to the cost model. If the gap vanishes with even a small complete subsample, I would weigh significance lower.

**Limitations**

Yes. The limitations section is unusually thorough: design-based scope, oracle tuning, order effects, identification failure for thresholded ensembles, solver scale, sampling error of the empirical populations, and model-based alternatives being more accurate at moderate n. One addition would help: state explicitly that for single-tree targets the adaptive optimum is the rule itself, so the comparison there prices pre-commitment relative to a trivially available protocol.

**Overall Recommendation**: 3 — Weak reject

This is a rigorous, honest and technically careful paper with clear merits. From the standpoint of ML evaluation practice, however, the setting is narrow, the experiments are toy-scale, the measured effect is small and matched by a simple model-based baseline at realistic sizes, and the presentation is too compressed for the main body to stand alone. I would not be upset to see it accepted on the strength of the theory if theory-focused reviewers verify the proofs. It may be better served by a statistics or learning-theory venue, or by a longer format.

**Confidence**: 3 — I am confident in my assessment of the problem setting, experiments and practical significance. I checked the core arguments for Theorems 2 and 4 and parts of Theorems 1 and 3, but not the full appendix (polynomial-dimension products, finite-sample converses, solver correctness). I may be missing related work in survey design or TCS.

**What would move you up one point**

- A realistic, well-argued ML use case for the cost model (free labels, hard feature cap, forced pre-commitment), with at least one experiment on data from it. This should preferably be an ensemble or update contrast, where branching is non-trivial.
- Forest or ensemble experiments at a less toy scale (m ≥ 20, b ≥ 4, multi-level features), or scalable approximate designs with certified optimality gaps where the exact solver stalls.
- A finite-sample comparison, at n = 1,000–4,000, of fixed versus branching using estimators practitioners would deploy: learned designs with the pilot charged for both classes, and a model-assisted design-unbiased estimator. This would show whether the price of pre-commitment survives outside the oracle, large-n regime.
- A restructured main body: fewer results stated more slowly, a plain-language protocol and estimator box, Table 3 simplified, and the unused Appendices G and H dropped or clearly separated.

Any two of the first three plus the fourth would move me to a 4. Without new evidence on practical relevance, nothing realistic would move me higher than that.
