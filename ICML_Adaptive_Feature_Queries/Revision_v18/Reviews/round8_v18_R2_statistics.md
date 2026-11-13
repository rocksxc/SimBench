# Round 8 — simulated review R2 (statistics) of v18 (`Manuscript/paper.pdf`)

Overall Recommendation: **4 (Weak accept)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 3 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words, not the abstract)

The paper studies planned-missingness designs in which each sampled record reveals at most b of m binary features, with the label always observed. The estimand is a known low-degree functional Δ(P) = E[Y d(X)], such as the accuracy of a frozen depth-b screening tree or the accuracy difference of two forests. It asks how many more records are needed when each record's feature set is fixed in advance (a split-questionnaire "form", MCAR by design) than when it is chosen sequentially from earlier answers (a depth-b decision tree, i.e. randomized monotone coarsening), with r-round interviews in between.

Two regimes are treated:

- **No model ("design-based").** For any finite menu of interviews the first-order minimax constant is a convex program with a dual (Thm 1). At a fixed law P the constant W_A(P) is the known-coarsening semiparametric efficiency bound minimized over the design, shown to be a local asymptotic minimax risk (Prop C.8).
- **The gap.** A rejection-sampling ("path guessing") argument shows that K = min{2^(b-1), C(m-1,b-1)} times as many fixed-form records reproduce the branching experiment exactly, for every law, estimator and loss (Thm 2 / C.1). An "address" contrast attains 2^(b-1), at every accuracy of the rule.
- **Rounds.** r rounds cost at most 2^(b-r); a pointer-tree construction shows a constant number of rounds can still lose nearly the full exponent (Thm 3).
- **At a population.** The ratio is bracketed by 1/ρ² (the best single-form R² of the target) and a Rényi-1/2 effective number of paths (Thm 4).
- **With a model.** Within an order-k log-linear model the same factors remain upper bounds. At and near product laws the gap is at most about (b+1)^k, and it is exactly 1 for the address contrast under the pairwise model. Strongly coupled pairwise laws restore 2^(b-1)/b (Thm 5).

A column-generation SOCP solver with dynamic-programming pricing computes certified optimal designs for forms, r-round and branching menus. Experiments use CART screening trees on 12 binarized BRFSS or thyroid items and small random-forest updates on three UCI datasets.

- Without a model, optimized forms need 1.0–1.98 times the records of branching (medians 1.35–1.58 at caps 4–6).
- A second round removes most of that gap.
- Under a fitted pairwise model the ratio is 1.02–1.13.
- In simulated audits, pairwise ML on forms is about as accurate as on branching records up to n = 8,000, after which model bias takes over.

**Strengths**

1. **Clean question with sharp answers.** The exact-simulation theorem (C.1) is a Blackwell-type comparison of experiments. It is simple, model-free and estimator-free, and it yields the 2^(b-r) bounds for V, for W(P) at every P, and inside every parametric model at once. I checked this proof, the centred-score version (E.1(a)), the witness bound (E.1(b)), the bracket (E.1(c)), Prop E.3 and Prop C.8. They are correct.
2. **Honest about what is classical.** The paper states that for a single menu its programs are c-optimal design, and that for a fixed design the optimal score is the Robins–Rotnitzky–Zhao/Tsiatis efficient augmented IPW score (Section 3, App. C.5.2, E.7.1, E.6). The claimed novelty is the comparison across menus and the exact optimization over combinatorial menus. That is the right framing.
3. **The missing-data structure is non-standard and handled correctly.** There are no complete cases and the patterns are non-monotone. Identification comes from the low degree of the target (a sum of functions of at most b coordinates). The "shared-coordinate corrections" (Prop E.7) correctly characterize the full augmentation space.
4. **Theorem 5 carries a real message for planned-missingness practice.** Whether a low-order log-linear model rescues pre-committed forms depends on dependence and on feature coding, not on the nominal order of the model. Parts (b)–(d) with Table 19 make this concrete. I verified the algebra of L_k(b), including L_3 and L_(b+1), and the pairwise value σ²/b for the address contrast.
5. **Certified computation.** Every reported constant comes with primal and dual bounds, and unclosed programs are reported as intervals.
6. **Broader and fairer baselines than usual for an ML paper.** These include reference-fitted designs, pilot-learned designs with the pilot charged, EM maximum likelihood under working pairwise and three-way models on the capped records, a cross-fitted model-assisted (AIPW-type) score, and regression and multiple imputation from external complete records under pre-specified shifts.
7. **Unfavourable findings are reported.** Model bias dominates at n ≥ 16k, the unsmoothed pilot costs 4.33 at b = 6, records are nearly useless for another rule (up to 317 times), and complete records undercut forms once a label costs more than 4–15 questions.
8. **Internal consistency.** Every main-text number I cross-checked against Tables 2, 3, 9–11, 14, 18 and 20 and against F.10 matched.

**Weaknesses** (numbered; [major] or [minor])

1. **[major] The cap is not binding in any realistic sense in the applications, so practical significance is limited.**
   - The flagship example caps a validation study at 4–6 yes/no items out of 12, with the "label" (self-reported diabetes) free. The trees depend on only K = 4–10 items, so a cap of K yes/no questions removes the problem entirely.
   - The paper's own F.10 shows complete records beat optimized forms once a label costs more than about 4–15 feature questions. That is the normal situation in screening validation, where the gold standard is the expensive item.
   - The setting where the cap bites (laboratory panels, reflex testing) is not studied with real costs.
   - What remains empirically is a factor of at most 2 that disappears with two rounds or a pairwise working model. The exponential separations live on address and pointer functions with m exponential in b.

2. **[major] The model-based regime is evaluated at a law that is not the population, for a target the model cannot represent.**
   - The accuracy of a depth-b tree involves interactions of up to b items with the label, so M_2 and M_3 are misspecified by construction.
   - W^(k) is computed at the complete-data ML fit P_k. Under planned missingness the pseudo-true law of the working-model MLE depends on the design q (it is a KL projection of the observed-data laws), so forms and branching target different limits.
   - Table 20 therefore mixes variance with design-specific bias: 0.40 versus 0.33 SD at 32k, and single-tree ratios up to 4.97.
   - The statement that "the model removes a median 80% of the log-gap" is about a hypothetical population. No misspecification-robust (sandwich, pseudo-true) constant is given.
   - The audit comparison uses the rule's own padded tree rather than the model-optimal branching design.

3. **[major] The "benign regime of Theorem 5" is asserted for BRFSS but not verified.**
   - Thm 5(b) holds at product laws and on an unquantified neighbourhood ("up to a factor 1+ε").
   - BRFSS items (hypertension, cholesterol, BMI, age, general health) are strongly dependent.
   - Appendix E.2 itself lists a type-(b) bound at laws with dependence as open.
   - The abstract's "at and near uniform laws" therefore has no quantitative content away from independence. The small empirical model-based ratios are an observation on six trees per cap, not a consequence of the theorem.

4. **[major] Scope and density exceed what can be verified in a conference review.**
   - The 8-page body is a compressed index to a 50-page appendix containing five theorems with multi-part statements, about ten propositions and 22 tables.
   - The proofs that carry the most novelty for this venue are long and appendix-only: Thm 3(b,c) (the potential argument and its products) and Thm 5(c,d).
   - The abstract and Section 7 are walls of numbers; the main qualitative messages are hard to extract.
   - Several appendix items are tangential: C.4.3, E.8.3, G, Prop B.3 and Thm C.4.

5. **[major, lesser] What goes beyond classical theory is real but technically moderate.**
   - The universal upper bound is a short rejection-sampling argument.
   - The sharp instances are the address function and pointer chasing from decision-tree and communication complexity, translated into variance through the standard chi-square/energy dual.
   - The single-menu characterization is minimax linear-functional duality plus Elfving.
   - The synthesis is valuable, but a statistician will not be surprised by any individual result. The most original pieces are Thm 5(c,d) and the certified solver.

6. **[minor–major] The headline ratios compare oracle designs with asymmetric tuning burdens.**
   - For a single tree, branching needs no tuning (it administers the rule, W_branch = Var(t)).
   - The optimal form design and its tables require the cell masses and even Δ(P), which is the centring constant in E.1.
   - The price of learning is reported honestly: +5% with 20,000 complete reference records, +10–35% with a smoothed pilot, and 4.33 unsmoothed at b = 6.
   - The abstract leads with the oracle 1.0–1.98. The realistic "no reference" numbers (1.53–1.93 at N = 4,000) rely on a pairwise smoother and a path-set menu.

7. **[minor–major] The empirical base is thin and survey features are ignored.**
   - There are six trees per cap (two targets by three seeds; the other-sex target population is shared across seeds).
   - Only one dataset shows any gap for single trees; thyroid gives 1.00 throughout.
   - Items are hand-picked and binarized.
   - The forest "populations" are 171–3,101 held-out records spread over 4,096 profiles plus 1% uniform mass.
   - BRFSS weights, stratification, and unit or item nonresponse are ignored (acknowledged). Since W ratios depend on cell masses, recomputing at the weighted law is cheap and should be done.
   - "Design-based" here means form randomization with iid sampling from P. It is not design-based in the finite-population sense, and the term will confuse survey readers.

8. **[minor] The main-text summary of the imputation baseline is tilted.** "Covers only 0.515–0.902 under 3 of eight shifts" quotes regression imputation with a naive standard error. Proper MI in the same cells covers 0.667–0.935, and imputation has RMSE no larger than branching in most of the shown shift settings (Table 16). Similarly, "coverage 0.952–0.960" for the cross-fitted score is a range of medians; per-tree coverage is 0.870–0.980 with only 100–200 replications (Table 21).

9. **[minor] "Uniform matrix sampling over all forms needs 9–23 times" is a weak comparator.** It includes items the rule never uses. The sensible naive baseline is uniform over b-subsets of the rule's items (2.0–4.3 times), which should be the one quoted.

10. **[minor] The local-minimax reading of W(P) is outside its regime at the audit sizes used.** It is taken over the saturated model on 2^(m+1) = 8,192 cells and needs n much larger than the number of cells. At n = 500–8,000 this fails, which is why pairwise ML beats "design-based branching" (0.91–0.97). This is stated in the limitations but not where the ratios are introduced as "records needed".

11. **[minor] Identification of the working model under each design is not discussed.** Under branching, items on different branches are never observed together, and fitted forms need not cover all pairs. The pairwise parameters are then not identified even though Δ is. EM initialization and uniqueness of the estimate of Δ should be stated.

12. **[minor] Related-work gaps and reference quality.**
    - Missing, as far as I can tell from memory: adaptive/responsive survey design (Groves & Heeringa; Schouten, Peytchev & Wagner), composite and calibration estimators for matrix sampling (Merkouris), and IPW/AIPW for non-monotone MAR patterns (e.g. Sun & Tchetgen Tchetgen).
    - One reference lacks author initials (Jang, Zhu, Yu).
    - Several 2026 preprints carry load-bearing claims that I could not check.

13. **[minor] Theory covers binary or s-ary features; the experiments and solver are binary only.** The solver scales as C(m,b)·4^b; adaptive menus stop at m ≤ 12, b ≤ 6.

**Soundness** (1-4): 3 — The proofs I checked (C.1, E.1, E.3, C.8, E.4, parts of E.5) are correct and the numbers are internally consistent. The deductions are for the unverified "benign regime" claim, the misspecified-model interpretation, and the long proofs I could not fully verify (D.1, E.5(c,d)).

**Presentation** (1-4): 2 — Precise and candid, but severely over-compressed; it reads as a journal paper squeezed into 8 pages, and the abstract and Section 7 are number-dense to the point of obscuring the message.

**Significance** (1-4): 3 — A fairly complete theory of a well-posed question, useful to ML evaluation under feature budgets and to planned-missingness design. Practical impact is modest because realistic gaps are at most 2 and vanish with two rounds or a simple model, and the cap is artificial in the case studies.

**Originality** (1-4): 3 — A new synthesis: comparison of coarsening menus with exact constants, a rounds hierarchy in variance, the collapse and revival of the gap in log-linear models, and a certified solver. It is built from known tools and known hard instances.

**Key Questions for Authors**

1. **Misspecified working models.** For the BRFSS trees, what are the design-specific pseudo-true values Δ(P*_q) and sandwich-variance constants for pairwise ML under (a) optimized forms, (b) the rule's tree, and (c) the model-optimal branching design? Is "price about 1 under a pairwise model" still true as a ratio of asymptotic MSEs at fixed n once bias is design-specific? *A clean statement here, even if only computational, would resolve weakness 2 and raise my soundness and significance scores. If the conclusion flips for a non-trivial share of trees, the model-regime claims in the abstract need to be weakened.*

2. **Quantifying "near product laws".** Can Thm 5(b) be extended to bounded dependence (for example a Dobrushin-type condition or bounded coupling strength β, in line with the smooth growth in Table 19)? Failing that, can you report a dependence measure for the BRFSS fits showing they sit where the bound is informative? *A quantitative bound would move originality toward 4. Without it, "these populations are in the benign regime of Theorem 5" should be removed.*

3. **A setting where the cap is real.** Can you give one case study with real per-item costs and a costly label (for example laboratory panels or reflex testing, using the cost-weighted program of E.8.3), and recompute the BRFSS constants at the survey-weighted law? *If the gap and its removal by a second round persist under realistic costs and weights, significance rises. If complete records or a slightly larger cap dominate, the paper should be positioned as theory.*

4. **Multi-purpose surveys.** How do W_fixed/W_branch and the joint-design penalty scale with the number J of pre-specified targets? Table 15 has J ≤ 3; a branching interview administers one rule, whereas forms serve many. *If the adaptive advantage reverses for modest J, that is an important caveat for the survey motivation. If it persists, it strengthens the paper.*

5. **Identification under EM and the pilot at larger caps.** Are all item pairs co-observed under the fitted forms and under branching? How is EM initialized, and is the estimate of Δ invariant to the unidentified parameters? What pilot size is needed at b = 6 without the pairwise smoother? *This is mostly a soundness check on Tables 17 and 20; a satisfactory answer removes weakness 11.*

**Limitations**

Largely yes. Section 9 is unusually forthright: free labels, a single known target, order effects, the local and asymptotic meaning of W, ignored survey weights, and solver scale. Three additions would help:

- Say explicitly that the model-based constants are evaluated at a fitted law for a target the model cannot represent, and that the pseudo-true target depends on the design.
- Say that Theorem 5(b) does not cover dependent laws such as the BRFSS fits.
- Say that for single trees the practical gap disappears if the validation cap is the number of items the rule uses rather than its depth.
- Path-dependent nonresponse or break-off, mentioned only in the Impact Statement, belongs in the limitations.

**Overall Recommendation**: 4 — Weak accept. The paper is technically solid, with correct sharp results, and I found no errors. It advances the theory of evaluation under per-record feature caps and of planned-missingness design. It is held back by over-compression, an artificial cap in the applications, and a model-based story that is first-order at a fitted law. It is borderline; I would not fight a rejection motivated by presentation and fit.

**Confidence**: 4 — I am expert in the missing-data, efficiency and survey aspects and checked the corresponding proofs and tables. I did not fully verify the rounds lower bound (D.1) or Thm 5(c,d), and I could not check several very recent citations.

**What would move you up one point**

- Restructure the body around three results (exact simulation, the population bracket with the solver, Thm 5), with one complete proof in the body, a readable abstract, and tangential appendix material cut.
- Give a misspecification-aware treatment of the model regime (pseudo-true targets and sandwich constants per design, with model-optimal branching in the audits), or clearly weaken the claims.
- Either a quantitative weak-dependence version of Thm 5(b), or removal of the "benign regime" claim for BRFSS.
- One case study in which the cap genuinely binds under real costs, plus the BRFSS constants recomputed at the weighted law and on more trees and item sets, with variability across rules.
- Quote proper-MI coverage and the "uniform over the rule's items" baseline in the main text.

The first, second and fourth items together would make this a clear accept (5) for me. A 6 is not realistic given the modest practical gaps.
