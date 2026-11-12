# Round 4 — simulated review R1 (learning theory) of v14 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-09; the agent was interrupted by a container restart and resumed from its saved transcript. Not real ICML feedback. Full text as returned.)

**Summary**

The paper asks how many extra records a data collector needs when it must fix each record's feature questions in advance, compared with choosing them adaptively. Each record may reveal at most b binary features, and its label is always observed. The target is a linear functional ∆(P)=E[Y d(X)], where d is a known contrast of Fourier degree ≤ b, for example the difference of two frozen probabilistic classifiers. Three protocol classes are compared: fixed forms, r-round batched interviews, and depth-b decision trees ("branching").

1. **Exact characterization (Thm 1).** For any finite menu of interviews, the first-order minimax constant is a convex program V(d,A). It is the smallest worst-profile second moment of a randomized, pointwise-unbiased score, and it has a sup-over-(µ,h) dual. The converse covers biased estimators, adaptation across records, and interview choices that see the current label. A finite-n program is within a factor 104 of the minimax risk.
2. **Worst-case gap (Thm 2).** V_fixed/V_branch ≤ min{2^{b−1}, C(m−1,b−1)}. The upper bound comes from drawing one of the tree's padded path sets and importance-weighting; the address (indexing) function attains it at m=b−1+2^{b−1}, and products of address blocks give 2^{b−O(b/log b)} with m ≤ b².
3. **Rounds (Thm 3).** r rounds lose at most 2^{b−r}. Pointer chasing gives a strict hierarchy, and a binary pointer tree on m=2^b−1 coordinates gives V_r ≥ 2^{b−1}/(3b)^r via a potential argument.
4. **Population-specific results (Thm 4, Props 5–6).** At a fixed population, the second-moment ratio lies between 1/Γ_P (the energy explained by the best single form) and N_P (the Rényi-1/2 effective number of path sets). An optimized path-set design tightens the upper end. A column-generation SOCP solver with dynamic-programming pricing over subcube partitions certifies optimal designs in every class without enumerating the 2^m profiles. A two-phase design learns the optimum while staying exactly unbiased.
5. **Experiments.** Forest updates (WDBC, Spambase, Ionosphere) and screening trees (BRFSS, thyroid, up to 21 items). Pre-commitment costs about 1.0–1.85× in records (medians 1.24–1.58). An optimal second round recovers essentially all of it on BRFSS. Imputation from complete source records wins when the conditional law of unasked items transports, and loses coverage under pre-specified shifts.

**Strengths**

- **Clean formulation.** It links adaptivity gaps (decision-tree and huge-object query complexity, interactivity in local differential privacy) with statistical efficiency under a hard per-record cap. The message is crisp: adaptivity within a record is worth up to 2^{b−1}, while adaptation across records is worth nothing at first order.
- **Key arguments are correct.** I checked:
  - the Sion/Fenchel duality behind (2), (B.2) and (B.3);
  - the van Trees converse with martingale Fisher information. A label-selected interview contributes ½Σ_y‖Π_{ι_y}h‖² ≤ J_µ(h), so the label-dependent case does go through;
  - the two-point χ²/Pinsker constant (ϑ=1/5 gives c²/103.4);
  - path guessing (completion happens iff S=S_τ(x)) and the Jensen merge over tree tags;
  - the address-function energy r·2^{s−2κ} ≤ 2^{−κ};
  - the pointer-chasing hit bound;
  - the potential inequality (D.2), E[M_t|T_{t−1}] ≤ (1+2a_t)M_{t−1}: summing over the deepest newly read node, each term is at most 2M_{t−1};
  - the AM–GM combination giving 2^{b−1}/(3b)^r.
- **Sharp results.** The worst-case constant is exact. The round hierarchy is tight up to poly(b) for fixed r. Exact small-cap constants are computed for the pointer tree (fixed forms lose 4 and 8; two rounds lose 1.80 and 3.32 at b ∈ {3,4}).
- **Strong computational component.** Primal and dual bounds are certified. Pricing costs O(C(m,b)4^b) per iteration. Results are validated against an independent dense implementation. Fitted designs stay exactly unbiased when the reference marginals are wrong, which is a nice practical property.
- **Honest scoping and results.** The paper reports modest gains, says plainly when imputation is the better tool, pre-specifies the shifts, quantifies order effects, runs sensitivity analyses, and releases code.

**Weaknesses**

1. **[major] Technical depth relative to known tools.**
   - Thm 1 applies well-established machinery: Donoho/Juditsky–Nemirovski-style linear-functional duality, Sion–Fenchel, van Trees with sequential Fisher information, and Le Cam two-point bounds.
   - Bounding a witness's information simultaneously over a channel family, including sequentially interactive protocols, is what Barnes–Han–Özgür and Acharya–Canonne–Tyagi already do. The label-dependent extension is a small modification. The claim that "what is new is that the witness is controlled simultaneously for every interview" overstates the novelty.
   - Thm 2 combines the natural randomized version of the standard non-adaptive simulation (guess the b−1 branch outcomes and importance-weight; essentially the device of the relaxed-LDC work the paper cites) with the canonical indexing function and a two-line Fourier computation.
   - Thm 4 is Cauchy–Schwarz plus the q ∝ √w allocation, and Prop 5 is restricting the menu.
   - The only genuinely new lower-bound argument is Thm 3(c). It is short, and it loses a factor 2^{r−1}(3b)^r.
   - Missing related work:
     - The population program is a c-optimal design problem (Prop C.7 makes this explicit), and the gauge C_A(d) is Elfving-type; neither connection is discussed.
     - The across-record result is the statistical analogue of the classical "adaption does not help for linear problems" results in information-based complexity (Smolyak, Bakhvalov, Novak).

2. **[major] The worst-case theory has little bearing on the practice it motivates.**
   - Every exponential separation needs m exponential in b: address m=b−1+2^{b−1}, pointer chasing m=Θ(2^{b−1}), pointer tree m=2^b−1. Only Thm 2 has a polynomial-dimension version, and the round lower bounds have none.
   - The witnessing populations have labels independent of the features (∆=0).
   - In the paper's own data, pre-commitment costs at most about 1.85×, and two rounds remove the cost.
   - So the headline exponential results do little for the motivating applications, while the parts practitioners would use (bracket, solver) are elementary or engineering. The paper is candid about this, but it limits significance.

3. **[major] Narrow scope.**
   - The setting is binary features, one known contrast of degree ≤ b, labels always observed and charged separately, no order effects, and the worst case over all laws on the cube.
   - Identifiability excludes most deployed models. Thresholded GBDT and MLP decisions have identification floors of 0.34–0.66 at b=3 (Table 12).
   - The forest experiments estimate accuracy differences of *randomized* (probability-output) rules, not of the thresholded decisions practitioners actually audit.
   - In the identifiable screening-tree case, branching reaches full information trivially.

4. **[minor] The variance-scale upper bound is loose and can exceed K_{m,b}; a per-population bound on records is missing.**
   - The upper end in Thm 4 and Cor. E.2, (N_P·E t² − ∆²)/σ², grows without bound as ∆² → E t², that is, for accurate rules.
   - Centering fixes this. The score ∆ + (t−∆)·1{S_τ(X)=S}/q_S with q_S ∝ (E[(t−∆)²1{S_τ=S}])^{1/2} is pointwise unbiased and gives W_fixed(P)/W_branch(P) ≤ N′_P ≤ L_τ ≤ K at every P.
   - For general d, centering the optimal branching design before simulating it gives W_fixed(P) ≤ K·W_branch(P).
   - I checked this on the worked example (m=3, b=2, X uniform, label correct with probability 1−ε, 1% smoothing) by solving the fixed-form program exactly. The records ratio is 2.000 at ε ∈ {0.25, 0.10, 0.05}, while the stated upper end is 2.32, 3.68 and 5.85.
   - This also contradicts the remark after Cor. E.2 that the variance-scale bracket is necessarily wider. Fixing it would turn the headline into a statement that holds at each population, not just in the worst case.

5. **[minor] Empirical reporting and traceability.**
   - (a) The headline "between one and 1.98" (abstract, contributions, discussion) appears in no table. The reported maximum is 1.85 (forests, b=3), and the b=5 forest runs mentioned in F.2 are not reported.
   - (b) "A median 100% of the log-gap at caps 4, 5 and 6" rests on 13 runs with a gain, and on a single tree at b=6. There are no two-round results for the forests or for the 21-item study.
   - (c) The "RMSE 0.89–0.99" range does not match Table 9, where 2.61/2.96 = 0.88.
   - (d) The rule "reference lower end ≤ 1.05 ⇒ no material gain" is said to have "no misses over all screening runs and forest tasks". For forests, 1/Γ_P is not a lower bound (no single tree computes d), 75 of 240 forest tasks realize a ratio below it, and only 2 forest tasks triggered the rule. Calling the lower end "conservative for forests" is therefore inaccurate.

6. **[minor] Presentation.**
   - The main text is extremely compressed, with many named constants and forward references, and Section 6 reads as a dense list.
   - The appendix contains stale, contradictory text:
     - Cor. C.9 says an exponential two-round-versus-branching separation "is not established here", and D.2 says the general exponential hierarchy "remains unsettled", yet Thm 3(c) and Cor. D.4 establish it.
     - After Cor. D.4, "V₂ ≥ 4/3 … remains the best statement we have" conflicts with Table 4, which gives 1.80 at b=3.
   - Editing artifacts: a truncated sentence ("The address contrast of Theorem 2 is th"), a stray "APP", a misplaced fragment at the start of Appendix E, and D.4 citing itself. The decision-rule table is cited as F.1 but sits in F.2.
   - The PISA appendix has no branching counterfactual and does not bear on the main question.

7. **[minor]** The finite-n factor 104 is loose, and the exact finite-n ratio between classes is left open (acknowledged).

**Soundness:** 3. The key proofs check out. Some empirical summary claims are loosely stated or untraceable, and one stated bracket is valid but loose.

**Presentation:** 2. The writing is precise but over-compressed and notation-heavy, and the appendix has stale contradictions and editing artifacts.

**Significance:** 2. The problem is niche, the exponential gaps appear only on artificial exponential-dimension instances, and the measured practical gains are at most about 2×, with two rounds sufficient.

**Originality:** 3. The formulation and the variance-based round hierarchy are new to my knowledge; the techniques are largely standard.

**Key Questions for Authors**

1. **Per-population bound.** Do you agree that centering (Weakness 4) gives W_fixed(P) ≤ N′_P·W_branch(P) ≤ K_{m,b}·W_branch(P) at every P, including general d via the centered optimal branching design? If you adopt it, Thm 4 becomes a per-population records guarantee. That would raise my significance assessment and fix the loose bracket.
2. **What is technically new?** Please state precisely what in Thms 1–3 goes beyond (i) Barnes–Han–Özgür / Acharya–Canonne–Tyagi per-channel bounds with the chain rule, (ii) importance-weighted path guessing, and (iii) standard pointer-chasing round bounds. A genuinely new ingredient I have missed would raise originality; otherwise please temper the claims.
3. **Round hierarchy in smaller dimension.** Is there a round-hierarchy instance with m = poly(b), for example products of small pointer trees, giving 2^{Ω(b)} for two rounds? Can the (3b)^r loss be reduced? Either would materially raise the significance of Thm 3.
4. **The 1.98 figure.** Where does 1.98 come from? Please report the maxima and full distributions per setting, including b=5 forests, and two-round results for the forests and the 21-item study. A clean answer would raise soundness to 4.
5. **Practical relevance.** Is there a realistic instance where pre-commitment costs at least 3×, or where the round analysis changes a design decision? How do the conclusions change for thresholded decisions? If gains are always at most about 2× and fixed by one extra round, the practical message is useful but modest.

**Limitations**

Yes, largely. The paper discusses single-functional scope, order effects, identification floors for nonlinear models, transport assumptions for imputation, and solver cost. Suggestions:
- State in the main text that the worst-case constants are attained at ∆=0 populations with exponential m.
- Make clear that the forest experiments use randomized-rule accuracy, and report the floors for thresholded decisions there.
- Bring the label-cost regime of F.7 into the main text, since it determines whether a hard cap is the binding constraint.

**Overall Recommendation:** 3 (Weak reject). The paper is correct, sharp and carefully executed, but the theory mostly applies standard tools, the exponential gaps live on artificial instances, and the measured practical stakes are modest. As it stands, the depth and significance fall slightly short of the ICML bar.

**Confidence:** 4

**What would move you up one point**

- Replace the variance-scale upper end with the centered bound and state W_fixed(P) ≤ K_{m,b}·W_branch(P) at every population.
- Delineate honestly what is new versus standard, add the c-optimal design (Elfving) and information-based-complexity references, and tone down the novelty claim for Thm 1.
- Fix the appendix contradictions and truncations, make "1.98" traceable or correct it, and qualify the forest decision-rule claim and the "median 100%" claim.

These three are realistic in a revision and together would move me to 4. Going beyond 4 would need a stronger technical result, such as a polynomial-dimension or tighter round hierarchy, or a realistic setting with large gains.
