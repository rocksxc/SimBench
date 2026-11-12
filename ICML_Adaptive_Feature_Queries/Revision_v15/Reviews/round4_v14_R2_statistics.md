# Round 4 — simulated review R2 (statistics / survey methodology) of v14 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 4 — Soundness 3 / Presentation 3 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-09; the agent was interrupted by a container restart and resumed from its saved transcript. Not real ICML feedback. Full text as returned.)

**Summary**

The paper asks how many extra records a data collector pays when each record's feature questions must be fixed in advance (split questionnaire, matrix sampling, fixed panel) rather than chosen adaptively from earlier answers. Each record may reveal at most b of m binary features, and its label is always observed. The estimand is a known contrast Δ(P) = E[Y d(X)] of Fourier degree at most b, for example the accuracy of a frozen screening tree or the accuracy gain of a forest update. Every estimator is design-unbiased at every profile: these are known-coarsening, HT/AIPW-type scores.

The results come at three levels.
- **Theorem 1 (exact characterization).** For any finite menu of interviews, n times the minimax MSE converges to a convex program V(d, A) with an explicit dual.
  - The lower bound covers biased estimators, adaptation across records, and interview choices that depend on the current label.
  - A finite-sample program is within a factor of 104 of the minimax risk.
- **Theorems 2–3 (worst case and rounds).**
  - V_fixed/V_branch ≤ min{2^{b−1}, C(m−1, b−1)}, which is sharp via the address (multiplexer) function.
  - r-round interviews lose at most 2^{b−r}. Pointer-chasing and a binary pointer tree give lower bounds of order 2^{(b−1)/r}/b and 2^{b−1}/(3b)^r.
  - Under an expected (mean) budget the ratio is at most m/b.
- **Theorem 4 and Propositions 5–6 (given population).**
  - The optimal second-moment ratio lies between 1/Γ_P and N_P, the Rényi-1/2 effective number of tree paths. An optimized path-set design tightens the upper end.
  - A column-generation solver with dynamic-programming pricing certifies optimal fixed, r-round and branching designs.
  - A two-phase pilot can learn the design asymptotically without bias.

The experiments compute exact ratios on forest updates (WDBC, Spambase, Ionosphere) and on screening trees (BRFSS with 12 and 21 items, and thyroid).
- Fixed forms need about 1.0–1.85 times as many records.
- An optimal two-round design closes nearly all of the BRFSS gap.
- Simulations compare against imputation from an external complete source under four pre-specified shifts.
- A position-effect model illustrates order effects.
- A PISA 2012 secondary analysis shows identification from real rotated forms.

**Strengths**

1. **A well-posed question, answered at three levels.** The question matters for planned-missingness design, and the worst-case, round and population answers complement each other. The mean-budget result (ratio ≤ m/b, Prop. C.6) usefully shows that the exponential gap is a hard-cap phenomenon.
2. **Technical care.** I checked the proofs closest to my expertise and found no errors:
   - the finite-sample converse (B.3.2): the tilted law ν, the χ² to KL to Pinsker chain, and the arithmetic behind 104;
   - the van Trees argument for the exact constant (B.3.3);
   - the path-guessing simulation and the Jensen step that merges tags (C.1);
   - the address-function energy bound r·2^{s−2κ} ≤ 2^{−κ};
   - local asymptotic minimaxity of W_A(P) (C.7);
   - the Cauchy–Schwarz bracket (E.1);
   - two-phase self-calibration (E.8).

   Classes are compared at their respective efficient estimators, which is fair. Prop. C.7 shows that restricting to pointwise-unbiased scores costs nothing at first order at full-support laws. The paper is commendably explicit about which parts are classical (C.5.2, E.5, E.6.1).
3. **Computation.** Writing pointwise unbiasedness as Fourier-coefficient identities (Prop. E.4) turns the efficient known-coarsening augmentation into a finite second-order cone program that never enumerates the 2^m profiles. For non-monotone patterns that augmentation normally has no closed form.
   - Dynamic-programming pricing over r-round interviews and trees is a genuinely nice idea.
   - Bounds are certified by primal and dual values that agree to within 1e−4.
   - The small extremal examples carry exact rational certificates (Prop. C.8, Cor. C.9).
   - The theory also covers larger answer alphabets and Brier/log-loss targets.
4. **Honest empirical practice.**
   - The shifts were fixed in advance, and all four are reported, including those where imputation works.
   - Sensitivity to the smoothing mass and a bootstrap of held-out records are reported.
   - Order effects are shown to be as large as the gains.
   - The cost-regime analysis (F.7) is included.
   - The PISA analysis correctly uses the final weights with 80 Fay BRR replicates (k = 0.5) and a within-sample MI comparator.
5. **A frank limitations section.**

**Weaknesses**

1. [major] **The population-level machinery is largely classical, and its lineage is under-credited.**
   - By Prop. C.7, W_A(P) = min_q cᵀ(Σ_ι q_ι I_ι(P))^† c. This is a c-optimal design problem over a combinatorial design space of interviews.
   - The witness bound in Theorem 4 / E.1(a), (E[th])²/max_ι E[E(h | ℓ_ι, Y)²], is the standard Elfving / equivalence-theorem dual.
   - Column generation that adds "the most informative interview" is the vertex-direction (Fedorov–Wynn / Frank–Wolfe) method.
   - For fixed q, the form program is the efficient AIPW projection under known CAR coarsening (Robins–Rotnitzky–Zhao; Tsiatis). Proposition 6 is an adaptive two-phase design.
   - None of the following are cited:
     - the optimal-design literature (Elfving; Kiefer–Wolfowitz; Fedorov; Pukelsheim);
     - optimal two-phase designs for AIPW estimation of a mean (e.g., Gilbert, Yu & Rotnitzky, 2014);
     - minimax design–estimator strategies in finite-population sampling (Stenger, 1979; Gabler, 1990).
   - Related Work also mischaracterizes two-phase designs as adapting "across waves". In classical two-phase sampling, whether a unit's phase-2 variables are measured depends on that unit's own phase-1 values. That is within-record adaptivity: a 2-round interview under an expected rather than a hard budget. The finding that "a second round recovers most of the gap" should be framed against that literature.
   - What is genuinely new is (a) the class-comparison constants of Theorems 2–3 and (b) dynamic-programming pricing over trees and r-round interviews. The paper should say so plainly.

2. [major] **Practical significance is limited by the estimand and the setting.**
   - The paper targets one known low-degree contrast. The main real use of fixed forms, multipurpose split questionnaires, is out of scope (the authors acknowledge this).
   - For screening trees, the optimal branching design is simply to administer the tree, which any validation study would do; skip logic is routine in CAPI/CAWI. Table 3 therefore mostly quantifies the cost of not doing the obvious. The informative parts are Γ_P and the two-round results.
   - Auditing a forest update under a hard per-record feature cap is a contrived scenario. Table 5 shows that the cap itself dominates: fixed-form variance is 2.1–5.9 times the full-information variance, against an adaptivity factor of 1.36–1.73. The main text never reports the cost of the cap.
   - The exponential worst-case gaps need m exponential in b (address function, pointer trees) or products with m ≤ b².
   - The r-round lower bounds are vacuous for b < 10, and at realistic caps (b ≤ 6) the realized ratios are at most about 1.6–1.85.
   - Features are median-binarized, and nonresponse and mode effects are excluded.

3. [major] **The imputation baselines are not the ones a planned-missingness analyst would use, and one natural design class is missing.**
   - **(a) Transport-dependent comparators.** The imputation comparators borrow the conditional law of unasked items from an external complete source. They are tested under shifts defined by variables (sex, education, cost barrier, poor health) that the imputation model is never given. Failure when transport fails is the textbook model-based versus design-based tradeoff.
     - Standard practice for split questionnaires imputes from the target's own capped records. There, MAR holds by design and no transport is needed.
     - The authors do exactly this for PISA (H.4) but not for BRFSS.
     - Fair comparators would be:
       - within-sample MI, or EM under a log-linear model containing the identified (b+1)-way margins;
       - AIPW with augmentation fitted on the target's own capped records;
       - imputation that conditions on the shift variable when it is recorded.
   - **(b) No naive standard design.** No uniform or balanced-incomplete-block design with HT or MI is reported. Readers therefore cannot separate gains due to the design from gains due to the estimator.
   - **(c) Label-dependent fixed designs are excluded.** In the population program, form probabilities do not depend on the always-observed label (q_ι has no label index in E.3).
     - Outcome-dependent allocation, as in case–control two-phase designs, is natural when Y is known.
     - With about 16% prevalence of diabetes or prediabetes, it could materially shrink the headline 1.35–1.58.
     - The worst-case fact that label access does not help (D.3) does not carry over to a fixed P.

4. [minor] **The population bracket is weaker than the main text suggests.**
   - On BRFSS the lower end 1/Γ_P is far from the optimum: 1.18, 1.08 and 1.13 against 1.49, 1.35 and 1.58.
   - The narrow part of the bracket is the path-set design (PS) against the best fixed design. PS is itself a feasible fixed design, so this narrowness only says that the path-set menu nearly suffices.
   - For ensembles the premise of Theorem 4 (one depth-b tree computes d) fails. The lower end computed from the reference exceeds the realized ratio in 75 of 240 forest tasks (F.2), yet the text calls it "conservative".
   - The "no misses" rule rests on only two forest tasks with a lower end at most 1.05, and the main text cites F.1 for it when the material is in F.2.
   - "Computable from reference data" gives a plug-in estimate at the target, not a bound, and no uncertainty is reported for it.

5. [minor] **Traceability and consistency of the reported numbers.**
   - The headline range "between one and 1.98" (abstract, contributions, Discussion) appears in no table or figure. The largest reported values are 1.85 (forests, b = 3) and 1.60/1.70 (BRFSS, b = 6, best/fitted).
   - Forest runs at b = 5 are mentioned in F.2 but never reported.
   - For the sex shift at b = 4, Tables 9/10 give fitted-form and branching SDs of 3.12 and 3.06. That implies a variance ratio of about 1.04, while Table 7 reports a fitted ratio of 1.61 for the same setting. Which seed or tree was simulated?
   - The "median 100% of the log-gap at caps 4, 5 and 6" includes only one tree at b = 6, and every screening result rests on three seeds.
   - Table 2's "fitted" column was computed only at m = 12 but sits beside all values of m.
   - Section 6 writes "W_fixed/W_r" where W_A/W_branch is meant.

6. [minor] **Proposition 6 is asymptotic and untested.**
   - It needs n₁ much larger than the total cell count, about 1.9×10⁵ cells for fixed forms alone at m = 21, b = 4.
   - No experiment learns the design from the audit itself; reference records stand in for phase one.
   - The pilot records are discarded, and finite-n behaviour is never shown.
   - The contributions bullet ("learns it from the audit itself without bias") should be qualified accordingly.

7. [minor] **Data and analysis details.**
   - The BRFSS-derived UCI/Kaggle extract carries no survey weights or design variables, so the "populations" are unweighted pseudo-populations. That is fine as a testbed but should be stated.
   - The 1% uniform smoothing is ad hoc. Its sensitivity is checked only for 15 forest tasks, not for the screening runs.
   - In the order-effects model, fixed forms ask items in index order rather than an optimized or randomized order.
   - In PISA, item nonresponse is coded as non-endorsement, and allocation is spiraled within schools rather than iid with q = 1/3.
   - In PISA the optimized form score is no more efficient than the simple block HT score. Interval widths are 6.81 against 6.66 ×10⁻³ for the Brier contrast, and 0.00715 against 0.00720 for accuracy. This tempers the practical value of the form program on real data.

8. [minor] **Precision and presentation.**
   - The main text claims that for d ∉ H_A "the risk is δ² + Θ(1/n)". C.3.3 proves only δ² ≤ R ≤ δ² + V/n and explicitly disclaims a matching rate.
   - On p.4 the Γ_P display overruns into the right column.
   - On p.31 the sentence "The address contrast of Theorem 2 is th…" breaks off and resumes as "e case r = 1…" under the heading of Section E on p.32.
   - D.4 contains a stray "APP" and refers to itself.
   - The main text is extremely compressed, and the 48 pages include tangents (GBDT/MLP floor certificates, AUC) that dilute the focus.

**Soundness**: 3. The key proofs check out and the computations are certified, but several empirical and interpretive claims are overstated or untraceable, and the baselines are incomplete.

**Presentation**: 3. The paper is logically organized, with a helpful worked example and table of constants, but it is very dense, overclaims in places and has layout glitches.

**Significance**: 2. The question is interesting, but the realized gains are modest, the scope is a single known contrast, and much of the population-level machinery is classical.

**Originality**: 3. The sharp class-comparison constants, the round hierarchy and the dynamic-programming pricing over interviews are new. The building blocks (path guessing, multiplexer, pointer chasing, AIPW, van Trees, c-optimal duality) are standard.

**Key Questions for Authors**

1. **Label-dependent forms.** What is W_fixed(P)/W_branch(P) on BRFSS when form probabilities may depend on the observed label, and on a free frame variable such as sex or age group?
   - If most of the 1.35–1.58 gap survives, the practical message is stronger and I would raise Significance.
   - If it largely disappears, the headline cost of pre-commitment is mainly an artifact of the restricted fixed class.
2. **Fair imputation comparators.** Under the four shifts, how do the following perform: within-sample MI or EM (log-linear in the identified margins), AIPW with augmentation fitted on the target's own capped records, and imputation that conditions on the shift variable?
   - If the design-based scores still win on coverage at comparable RMSE, the "information versus design" conclusion becomes informative.
   - If not, that conclusion should be restricted to external-reference imputation.
3. **Traceability.** Where does the 1.98 maximum come from? Can you reconcile Table 7 with Tables 9/10 (a fitted ratio of 1.61 against an implied ~1.04 for the sex shift at b = 4)? Will you report the b = 5 forest runs or drop the mention?
   - A clean reconciliation removes my traceability concern.
   - A real discrepancy would lower my Soundness score.
4. **Positioning.** Beyond the DP pricing and the class constants, what is new relative to c-optimal design theory (Elfving, the equivalence theorem, vertex-direction methods) and to optimal two-phase designs for AIPW? A sharp answer would raise my Originality assessment and make the contribution claims more credible.
5. **Cost of learning the design.** At realistic pilot sizes (for example n₁ = 500–2,000 with m = 12, b = 4), how much variance does learning the design cost compared with the oracle and reference-fitted designs?
   - A small cost would support practical use.
   - A large cost would confine Proposition 6 to theory.

**Limitations**

Mostly yes. The single-estimand restriction, order effects, nonresponse, identification floors and transport are all discussed candidly. I suggest also stating:
- that the populations are unweighted pseudo-populations;
- that the exponential gaps require m exponential in b;
- that label-dependent or stratified fixed designs and within-sample imputation were not compared;
- that learning the design costs variance at finite n;
- that the population bracket is valid only when one depth-b tree computes the contrast.

**Overall Recommendation**: 3 (Weak reject)

**Confidence**: 4

**What would move you up one point**

- Add within-sample MI/EM and AIPW with augmentation fitted on the target's own capped records, plus imputation that uses the shift variable, to the BRFSS shift study.
- Add label-dependent (and frame-stratified) fixed designs to the population comparison, and report whether the gap survives.
- Position the population-level results relative to c-optimal design and two-phase AIPW design, state the new elements explicitly, and correct the description of two-phase designs.
- Qualify the bracket and self-calibration claims, and report the cost of the cap (fixed/full and branching/full) in the main text.
- Fix the traceability issues: the 1.98 maximum, Table 7 against Tables 9/10, the b = 5 runs, the cross-references and the δ² + Θ(1/n) statement.

All of these are feasible in a revision. If the first two were done and a gain of roughly 1.3x or more persisted, I would move to 4 (weak accept).
