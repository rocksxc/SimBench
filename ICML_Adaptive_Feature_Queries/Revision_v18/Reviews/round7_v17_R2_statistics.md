# Round 7 — simulated review R2 (statistics) of v17 (`Manuscript/paper.pdf`)

Overall Recommendation: **4 (Weak accept)** — Confidence 4 — Soundness 3 / Presentation 3 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in your own words, not the abstract)

The paper studies planned missingness under a hard per-record cap: each sampled unit reveals at most b of m binary features, the label is always observed at no charge, and the estimand is one known functional Δ(P) = E[Y d(X)] with deg(d) ≤ b (the accuracy of a frozen depth-b rule, or the accuracy difference of two rules). It asks how many more records are needed when each unit's b questions are fixed before the unit is seen ("fixed forms", MCAR by design) than when they are chosen from the unit's earlier answers ("branching", a monotone CAR coarsening), with r-round interviews in between.

The results, as I read them:

- **Characterization (Thm 1, Eq. 3, Prop C.7).** The worst-case first-order minimax constant of a finite menu of interviews is a convex program with an explicit dual. At a fixed full-support population, the analogous constant W_A(P) is the Robins–Rotnitzky–Zhao known-coarsening efficiency bound minimized over the design, i.e. a c-optimal design problem whose design points are interviews. The paper says so explicitly.
- **Worst-case gap (Thm 2).** Fixed forms need at most K = min{2^(b-1), C(m-1, b-1)} times the records of branching, at every population. The proof guesses the tree's padded path set and inverse-weights on completion. The multiplexer ("address") function on b-1+2^(b-1) features attains the bound.
- **Rounds (Thm 3).** r rounds lose at most 2^(b-r). A pointer-tree lower bound via a potential argument shows that a constant number of rounds can still lose 2^(b(1-o(1))).
- **Population bracket (Thm 4).** The ratio lies between 1/ρ² (the reciprocal of the best single-form R²) and a Rényi-1/2 effective number of paths.
- **Models (Thm 5).** The path-guessing argument is a garbling, so the same factor bounds the gap in any model and for any estimator. At product laws under an order-k log-linear model the gap is at most (b+1)^k. For the address contrast at the uniform law it is exactly 1 for k = 2 and at least linear in b for k = 3.
- **Computation and data.** A column-generation solver with exact DP pricing certifies optimal designs for each class. On BRFSS and thyroid screening trees and small forest updates, the design-based ratio is 1.0–1.98, and two rounds recover most of it. At fitted pairwise laws the ratio is 1.02–1.13. In resampling audits, pairwise ML on fixed forms is about as accurate as on branching records up to n ≈ 8,000, but is visibly biased and under-covers at larger n.

**Strengths**

1. A clearly posed question that links two literatures (query-complexity adaptivity; planned-missing and two-phase design). The paper is candid about which ingredients are classical: it states that the fixed-design score is the efficient AIPW estimator under known coarsening, that the per-menu program is c-optimal design, and that the duality and van Trees tools are standard (§3, App. B.3.1, C.5.2, E.7.1). This is rare and makes the contribution easy to locate.
2. The proofs I checked are correct:
   - Thm 2(i)–(ii), path guessing with centering.
   - The address-function energy calculation (C.1.3).
   - Thm 4 / E.1(b)–(c), witness bound and bracket.
   - Prop E.3, persistence of the gap at every accuracy.
   - Prop C.7 / E.4, local minimax via multivariate van Trees with the averaged design.
   - Thm E.5(a), the Jensen/garbling step, and (b), Cauchy–Schwarz over low-order monomials.
   - The k = 2 computation in E.5(c).
   - The structure of the potential argument in Thm D.3 (Steps 1–5).
3. Thm 5(a) is a useful observation: the fixed design contains a 1/K-thinned copy of the branching experiment. This makes the upper bound estimator-free and model-free, covering ML, Bayes and MI.
4. The model-order interpolation in Thm 5(c) is the most interesting statistical statement. It says the exponential value of adaptivity is a statement about interactions whose order grows with the cap. That is a real conceptual addition to the design-based versus model-based discussion of split questionnaires.
5. The computational contribution is solid. Optimizing over the combinatorial menu of depth-b trees and r-round interviews with exact pricing and primal/dual certificates goes beyond the vertex-direction methods of the design literature, and the solver is cross-validated against an independent dense implementation.
6. The empirical section does not oversell.
   - It reports cases where the ratio is exactly 1 (thyroid; BRFSS trees using at most b items).
   - It separates oracle, reference-fitted and pilot-learned designs, and charges the pilot.
   - It reports bias and under-coverage of the pairwise working model (coverage down to 0.855 at n = 16,000, Table 17).
   - It reports the failure of external-source imputation under shift, the brittleness of optimized designs for other rules (1.55–317×, Table 15), sensitivity to the smoothing mass, and a response-order perturbation.
   - The limitations section is unusually complete.

**Weaknesses** (numbered; mark each as [major] or [minor])

1. [major] **Statistical depth beyond classical efficiency theory is moderate.**
   - W_A(P) is the RRZ/Tsiatis bound plus Elfving-type design optimization, and Thm 1 is standard minimax duality for a linear functional.
   - The universal upper bound is a one-line thinning argument. Once Thm 5(a) is in hand, the centered-score construction of Thm 2(ii) is redundant: Binomial(n, 1/K) branching records are a garbling of n fixed-form records.
   - The extremal example is the multiplexer function, the textbook separation of adaptive from non-adaptive decision trees. It needs m ≥ b-1+2^(b-1) features and a target that no audit would pose.
   - The genuinely new mathematics is the round hierarchy (Thm 3(b,c)) and the interaction-order interpolation (Thm 5(c)). The former is query-complexity in flavour and is not what drives any empirical finding.
   - The paper is therefore better described as exact constants for a known qualitative phenomenon, plus a careful solver, than as new efficiency theory.

2. [major] **The model-based theory is proved only at independence laws, and the headline "gap exactly one under the pairwise model" is a degenerate local statement.**
   - Thm 5(b) requires X_1, …, X_m, Y mutually independent. Thm 5(c) is at the uniform law.
   - At that point the gradient of Δ in the pairwise model is supported only on the (data bit, label) pairs. The optimal designs read only data bits, the information matrix is singular, and Δ is not identified away from P. The paper says this after Prop E.4.
   - So W^(2) = σ²/b is a first-order statement at a point where the address structure has no first-order effect. It does not show that a pairwise model removes the gap at laws with dependence, which are the laws of interest (a rule with accuracy above chance).
   - The paper acknowledges that "a bound of type (b) at laws with dependence" is open. The abstract and contributions still state "at most (b+1)^k at uniform laws" and "exactly one under the pairwise model" as if they characterize what a model changes.
   - Away from independence the evidence is numerical only: 18 fitted laws, Table 18.

3. [major] **The empirical model-based numbers describe hypothetical populations, and the paper's own simulations undercut the practical importance of the design-based constants.**
   - The 1.02–1.13 ratios are computed at the pairwise fit P_k, not at the target law. At the target law the pairwise ML is inconsistent for Δ, since tree accuracy depends on interactions of order up to b+1.
   - In the audits the pairwise ML on fixed forms beats the design-based estimator under branching up to n ≈ 8,000 (0.91–0.97), then has bias of 0.4 SD and MSE ratios up to 4.97 for individual trees at 32,000.
   - Two consequences follow. First, the local-asymptotic "records ratio" W_fixed/W_branch is not a binding lower bound at survey sizes: the saturated model has 2^13 cells and n is 500–8,000. Second, where it does bind, the stake is a factor of at most 2.
   - The practical take-away is roughly that the usual planned-missing ML analysis is fine at survey sizes, and that for design-based claims a second round suffices. That is a reasonable and honest finding, but a modest one next to the exponential worst-case headline.

4. [major] **Realism of the sampling model.**
   - (a) Labels are free and always observed, and only features are capped. In audits of screening rules the usual cost structure is the reverse: cheap questionnaire items, expensive gold standard (two-phase verification designs). In split questionnaires the outcome is itself an item under the cap. App. F.10 shows complete records undercut the best fixed design once a label costs more than about 4–15 feature questions.
   - (b) The estimand is a single functional known before collection. Split-questionnaire and matrix-sampling designs exist because surveys are multi-purpose. Table 15 shows the optimized designs can be nearly useless for a second rule.
   - (c) The cap is hard for every record. Under a mean budget the worst-case gap falls from 2^(b-1) to at most m/b (Prop C.6), so the exponential result depends heavily on this modelling choice.
   - (d) For a single screening tree, the optimal adaptive protocol is trivially "administer the tree". The experiment therefore prices paper forms against the rule itself, and for a quarter of the BRFSS runs and all thyroid runs the answer is 1.
   - (e) Binary noiseless answers with no order or mode effects and no unit or item nonresponse. Pointwise unbiasedness is demanded at all 2^m profiles, including structurally impossible ones.
   - Each item is acknowledged. Together they make the design-based regime narrower than the introduction suggests.

5. [major] **Real-data analysis: plug-in constants with little uncertainty quantification.**
   - The BRFSS evidence is 6 runs per cap (2 targets × 3 seeds, all drawn from one file, so not independent). It is summarized by medians with ranges as wide as [1.00, 1.98].
   - No sampling uncertainty is given for the BRFSS constants. A bootstrap is reported only for 15 forest tasks.
   - Oracle designs are tuned to the same smoothed empirical law they are evaluated on. The reference-fitted column addresses this, which is good, and should be the headline.
   - BRFSS weights and the complex design are ignored, so "population" means the unweighted respondent file.
   - Items and cut points are hand-picked.
   - Forest experiments use tiny evaluation sets (171–3,101 records occupying 120–400 of 4,096 profiles), with the 1% uniform mass filling the rest.
   - The pilot study uses 12–30 pilots per run on the path-set menu only. Unsmoothed, it gives 4.33 at b = 6.
   - None of this invalidates the qualitative picture (ratios between 1 and 2). The specific numbers in the abstract carry more precision than the design supports.

6. [minor] **Fairness of the estimator comparisons is mostly good but incomplete.**
   - The "design score" is an AIPW estimator whose augmentation is fitted on 20,000 external reference records. The same-data version appears only inside the pilot design.
   - Table 19 has no standard cross-fitted model-assisted (doubly robust) estimator on fixed forms with a working pairwise or three-way augmentation estimated from the audit itself. That is the estimator a missing-data analyst would actually use to get design-consistency with model efficiency.
   - The imputation baseline (Table 16) uses complete external records, a different information set from every capped design.
   - Model-based branching in the audits is the rule's own padded tree, not the model-optimal branching design.
   - No model selection or regularized log-linear fit is tried between k = 2 and k = 3, which is where the bias–variance trade-off the paper describes would be settled.

7. [minor] **The finite-sample theory is weak.** Thm B.1 has a factor of 10^4. Everything else is first-order asymptotic with no sample-size threshold, in a saturated multinomial model. Prop E.9 is asymptotic with n_1 much larger than |A|·2^b. The only informative finite-n statement is Prop C.1, for the address contrast.

8. [minor] **Thm 4's bracket is loose in practice.** The lower end is a median 1.31× below and the upper end 4.3× above the realized ratio. The "interpretable quantities" are therefore of limited use as planning tools. The paper says so.

9. [minor] **Presentation.**
   - The main body is an eight-page digest of a 57-page paper. Section 7 is a dense run of numbers that cannot be parsed without Appendix F.
   - The abstract is overloaded with constants. I could not trace "1.33–2.40" to a main-text table.
   - Table 2 gives the oracle at b = 4 as 1.49, while the text compares the pilot against an oracle of 1.52 (presumably "runs with a gain"). This should be stated.
   - "Design-based" is used for randomization-unbiased inference under iid superpopulation sampling, which differs from the survey-sampling meaning and may confuse that audience.
   - The solver handles adaptive classes only for m ≤ 12, b ≤ 6.

10. [minor] **Missing context.**
    - Verification-bias and two-phase designs for diagnostic accuracy (Begg–Greenes; McNamee-type optimal two-stage designs), which have the opposite cost structure.
    - Multiple matrix sampling in educational testing.
    - Responsive and adaptive survey design.
    - The RRZ monotone-missingness literature, of which branching is an instance.
    - The appendix discloses that a generative model helped derive and check proofs. This is not a ground for rejection, but with 45 pages of appendix it raises the verification burden. I checked only the parts listed under Strengths.

**Soundness** (1-4) with one-line justification

3 — Every proof I spot-checked is correct and the numerics are certified and cross-validated. The guarantees are first-order and local in a saturated model, and the model-based theorems hold only at independence laws.

**Presentation** (1-4) with one-line justification

3 — Precise, well organized and honest about what is classical, but very dense; the experiments and several headline numbers rely heavily on the appendix.

**Significance** (1-4) with one-line justification

2 — A complete answer to a clean but narrow question; on real rules the price is at most 2× and largely disappears with a second round or a pairwise working model.

**Originality** (1-4) with one-line justification

3 — The comparison across coarsening menus with exact constants, the round hierarchy and the interaction-order interpolation are new; the efficiency-theoretic core and the extremal example are classical.

**Key Questions for Authors** (3-5 numbered; for each, say how the answer would change your evaluation)

1. **Dependence in the model-based theory.** Is the collapse for k = 2 robust away from the independence point? For example, compute W^(2)_fixed/W^(2)_branch for the address contrast (b = 3, 4) along a path of pairwise-model laws where the label and data bits are increasingly associated with the address bits, so that the information matrix of data-only designs is no longer sufficient. Can any bound of type 5(b) be proved under bounded dependence, such as a Dobrushin-type condition or bounded pairwise parameters? *If the ratio stays near 1 or a bound is proved, Thm 5 becomes a substantive statistical result and I would raise significance and the overall score. If it reverts toward the design-based gap, the "what a model changes" contribution should be reframed as numerical only.*

2. **When does the design-based local-minimax constant bind?** Your own audits show a biased estimator beating it up to n ≈ 8,000 with 2^13 cells. Can you give either a non-asymptotic population-level lower bound with a usable constant, or simulations with a data-driven estimator (model selection between k = 2, 3 and saturated, or a shrinkage or cross-fitted doubly robust estimator) on forms versus branching records across n? *If the forms/branching ratio for a sensible adaptive-order estimator tracks W_fixed/W_branch at realistic n, the records-ratio interpretation is vindicated and significance rises. If it stays near 1 until very large n, the design-based constants are mostly of theoretical interest.*

3. **A model-assisted comparator on the same records.** Please add to Table 19 a cross-fitted AIPW estimator on fixed forms whose augmentation comes from a pairwise or three-way working model fitted to the audit records themselves (no external reference), with coverage. *This is the standard estimator in my field. If it achieves most of ML's small-n gain while keeping coverage at 32,000, the paper's dichotomy between design-based scores and ML is incomplete and the practical price of pre-commitment is even smaller. If it does not, the comparison is fair as it stands and my baseline concern goes away.*

4. **Cost structure and multiplicity of estimands.**
   - (a) What happens to Thm 2 and to the BRFSS ratios if the label counts toward the cap, or is observed only for a verified subsample?
   - (b) Is there a version of the gap for a family of targets, for example all depth-b trees on K items, subgroup accuracies, or a rule chosen after collection?
   *A positive result on (b), or evidence that the single-functional conclusions survive (a), would substantially improve realism and move me up. If the gap is specific to one pre-specified functional with free labels, relevance to survey practice stays limited.*

5. **Uncertainty and weights in the BRFSS analysis.** Please report bootstrap intervals over target respondents for the per-run ratios, the effect of using BRFSS final weights to define the target law, and reference-fitted rather than oracle designs as the headline. *Stable intervals and weighted results would resolve weakness 5. Large instability would lower my confidence in the 1.35–1.58 medians.*

**Limitations** ("yes" if adequately discussed, otherwise constructive suggestions)

Yes; the limitations section is among the most candid I have seen (free labels, single known functional, order effects, ignored survey weights, asymptotic constants, the 10^4 factor, solver scale, model bias). Two additions:

- State in the main text, next to Thm 5, that parts (b) and (c) are local statements at independence laws and that the k = 2 optimum has singular information.
- State that the 1.02–1.13 figures refer to populations that satisfy the fitted model, not to the target laws.

**Overall Recommendation** (integer 1-6, with label)

4 — Weak accept. The paper is technically solid, unusually careful and honest, and gives a complete treatment (exact constants, rounds, models, certified computation) of a well-posed question. My reservations are that the efficiency-theoretic core is classical, the model-based theory is confined to independence laws, the assumptions are narrow, and the empirical stakes are small. I would not champion it, and I would not object to rejection on significance grounds, but I do not see a soundness reason to reject.

**Confidence** (1-5)

4 — I am expert in the missing-data, design and efficiency aspects. I read the main body carefully and checked the proofs listed above. I did not verify the full round-hierarchy appendix line by line (in particular the product construction and the pointer-chasing bound), the solver code, or every table.

**What would move you up one point** (concise, concrete list; be honest — if nothing realistic would, say so)

Realistic within a revision; any two of the following would move me to 5:

- A theorem, or a convincing numerical study, on the model-based gap at laws with dependence (Question 1), with the degenerate nature of the k = 2 result made explicit.
- The cross-fitted model-assisted estimator and an adaptive-order estimator added to the audits (Questions 2–3), showing where the design-based ratio actually governs.
- Bootstrap and weighted versions of the BRFSS constants, with reference-fitted designs as the headline (Question 5).
- A result or experiment for a family of estimands or for costed labels (Question 4).

A tighter main text would help but would not change my score on its own: fewer numbers in the abstract and §7, and the redundancy between Thm 2(ii) and Thm 5(a) removed.
