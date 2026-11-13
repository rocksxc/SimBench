# Round 6 — simulated review R1 (theory) of v16 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 4 — Soundness 3 / Presentation 3 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words, not the abstract)

The paper studies estimating a known linear functional Δ(P) = E[Y d(X)] (e.g. the accuracy difference of two frozen rules) on {−1,1}^m when the label is always observed and at most b features may be queried per record. It compares three protocol classes by the number of records they need: fixed forms (coordinate set chosen before the record is seen), r-round interviews, and fully branching interviews (depth-b decision trees).

- **Theorem 1.** For any finite menu of interviews, n times the minimax MSE converges to a convex-program value V(d, A), with a dual of the form sup ⟨d,h⟩² / max_ι ‖E[h | transcript_ι]‖². Adaptation across records and label-dependent interview choice do not change V.
- **Theorem 2.** V_fixed ≤ K·V_branch with K = min{2^(b−1), C(m−1, b−1)}, via importance-weighted "path guessing". The same factor holds for the population-specific constant W(P) at every P, via a centred version of the simulation. An address (multiplexer) contrast attains 2^(b−1), at every accuracy of the rule.
- **Theorem 3.** r-round interviews lose at most 2^(b−r). A binary pointer tree loses at least 2^(b−1)/(1+2b/r)^r, proved by a supermartingale potential. Products of small pointer trees give 2^(b−o(b)) for constant r on m ≤ b² features.
- **Theorem 4.** At a population, 1/ρ²_P ≤ W_fixed/W_branch ≤ N_P(τ) ≤ K, where ρ²_P is a best single-form R² and N_P a Rényi-1/2 effective number of paths.
- **Computation and experiments.** A column-generation solver with dynamic-programming pricing certifies optimal designs for each class. On trained trees and forests the fixed/branching ratio is 1.0–1.98, two rounds recover most of the gap, and a log-linear working model beats the design-based estimator at moderate n.

**Strengths**

1. The formulation is clean and the paper says precisely which ingredients are standard (linear-functional minimax duality, van Trees, c-optimal design, known-coarsening efficiency) and which are new (the comparison across menus). I appreciated this candour.
2. I checked the main arguments and found them correct:
   - the Sion/Fenchel duality (B.2)/(B.3) and the van Trees converse, including label-dependent interview choice;
   - the padding and path-guessing simulation (C.1), and the centred variant giving the bound at every P (E.1(a));
   - the address-function energy computation, and its accurate-population version (Prop. E.3);
   - the Cauchy–Schwarz bracket (E.1(b,c));
   - the potential inequality (D.3) and its tensorisation across blocks, re-derived by hand, including the step that drops the indicator at the deepest newly read node;
   - Prop. C.8 and Cor. C.9, verified numerically from the printed tables: the decomposition is pointwise unbiased with maximum second moment (7+2√2)/4, the dual certificate matches, and all ten J(S) entries are as stated.
3. Theorem 2(ii) is stronger than the usual worst-case statement: the 2^(b−1) factor holds at every population, not just for sup-constants. The centring trick is simple but is exactly what is needed, and the factor is attained at every accuracy.
4. Theorem 3(b) is a new and reasonably elegant argument. The potential M_t + 2^L·π_t (most-likely-leaf mass plus already-read mass) makes the bound multiplicative across blocks under adaptive query splitting. It turns an exact-evaluation round lower bound into a variance statement.
5. The certified computation is solid (primal/dual certificates, repair to exact feasibility, exact dynamic-programming pricing over r-round interviews).
6. The experiments are unusually honest. They report that the gap is small on trained models, that learned designs cost extra, and that a parsimonious model beats the design-based estimator at survey sizes. The limitations section is substantive.

**Weaknesses**

1. [major] **Depth of the core theory.** Three of the four theorems are obtained by expected arguments.
   - Theorem 1 is standard, as the authors say.
   - The upper bound of Theorem 2 is Horvitz–Thompson weighting over at most 2^(b−1) padded path sets (a few lines). Its lower bound is the textbook adaptive/non-adaptive decision-tree separation (multiplexer) with a one-line Fourier energy computation.
   - Theorem 4 is Cauchy–Schwarz in both directions.
   - The qualitative separation is already known in the huge-object / locally-bounded-adaptivity literature, which the paper acknowledges.
   - What is added is exact constants on the variance scale and validity at every P. That is neat, but for the fixed-versus-branching question it is a translation of known query-complexity facts into inverse-probability weighting. The only technically new argument is Theorem 3(b,c).

2. [major] **The round hierarchy is not tight, and one headline claim is stated more strongly than what is proved.**
   - The bounds 2^(b−1)/(1+2b/r)^r and 2^(b−r) agree up to poly(b) only for constant r. For r = Θ(b) they differ by an exponential factor (0.37b versus b − O(log b) rounds for polynomial competitiveness).
   - It is not shown that 2^(b−r) is attained for any r ≥ 2. The paper's own computed values for the pointer tree (1.80 < 2 at b = 3; 3.33 < 4 at b = 4) suggest it is not attained by that instance.
   - The "linear in b rounds" conclusion is proved only for the single pointer tree with m = 2^b − 1 features. The polynomial-dimension contrast of Theorem 3(c) is a product of k = ⌊b/β⌋ trees needing β = ⌊log₂ b⌋ queries each. It is therefore evaluated exactly in ⌊log₂ b⌋ rounds within the cap (follow all blocks in parallel), so it can only show a loss for r = o(log b / log log b).
   - The abstract ("…targets on at most b² features for which a constant number of rounds still loses 2^(b(1−o(1))), so a protocol within a polynomial factor … needs a number of rounds linear in b") and Section 4 ("…r ≥ 0.37b − … rounds … And exponential dimension is not needed") read as if linear-round necessity held in polynomial dimension. It does not follow from what is proved.

3. [major] **The worst-case theory does not explain the regime the paper motivates.**
   - When a depth-b tree computes d (the screening-tree case), branching is "run the rule on each record" and equals full information (W_branch = σ²_P). The value of adaptivity is then just the cost of fixed forms relative to complete data for one known tree.
   - The extremal instances need m ≥ b − 1 + 2^(b−1) independent uniform features. On the trained models the ratio is at most 1.98 and two rounds are nearly optimal.
   - The instance bracket [1/ρ²_P, N_P] is loose where it matters (N_P = 10.5 against a realised 1.58 at b = 6; median slack 1.31 below and 4.3 above). No result explains why trained trees are benign, for example in terms of shared coordinates, feature dependence or path-mass concentration.
   - For ensemble contrasts not computed by one tree, there is no theory for W_branch beyond the solver, and the paper's own data show the cap costs more than pre-commitment there.

4. [major, on scope] **"Exact constants" are exact for a restricted regime.**
   - W_A(P) is the optimum over pointwise-unbiased, oracle-tuned designs. Its interpretation as a bound for arbitrary estimators is local-asymptotic in the saturated model on 2^(m+1) states, with full support enforced by an artificial 1% uniform mixture and no quantified sample-size threshold.
   - The paper's own Figure 3(b) shows a two-way log-linear model beating this benchmark for all trees up to n = 4,000 and for two thirds of them at 32,000.
   - The general finite-sample theorem (B.1) carries a factor 104, so it certifies no separation for b ≤ 7. Only the address instance has a sharp finite-n statement (Prop. C.1).
   - The title and abstract ("the statistical value of adaptive feature queries", "we characterize it exactly") are therefore broader than the result. The first-order constant in the biased or structured regime, which is the regime that wins in practice, is left open; the authors do acknowledge this.

5. [minor] **Small-dimension frontier.** For C(m−1, b−1) < 2^(b−1) the bound K_{m,b} is not known to be tight (already [2.457, 3] at (m,b) = (4,3)). The dependence of the extremal gap on m is not characterised between m ≈ b and m ≈ 2^b beyond product constructions.

6. [minor] **Presentation density.**
   - The eight pages compress four theorems, a solver and five experimental studies. The full statements of Theorems 3 and 4 live in the appendix (D.1, D.3, E.1).
   - The 44-page appendix contains many side results the main text does not use (one-feature audit, budget curve for sortedness blocks, hybrid budgets, Appendices G and H), which dilutes the paper and increases the checking burden.
   - Notation is overloaded: V_r is both a round constant and a dynamic-programming value in E.3; r is rounds, a data-bit count in C.1.3 and a calibration size in E.7.2; B is a batch, the hard cap and the pointer tree.

7. [minor] **Literature.** I could not match Li et al. (2026), whose title concerns semantic regular expressions, to the tree-evaluation round bound attributed to it. Please check this and the other 2026 preprints. Classical work on round-bounded (parallel) decision trees and average-case pointer-chasing bounds is the natural comparison for Theorem 3(b) and deserves an explicit statement of what is and is not implied. Responsive/adaptive survey design is also a relevant applied literature.

**Soundness**: 3 — Every proof I checked (Theorems 1, 2, 3(a,b), 4; Props C.1, C.4, C.8, C.9, E.3, E.7) is correct; the deduction is for the linear-rounds claim being worded beyond what is proved and for "exact" being exact only in the design-unbiased/local-asymptotic sense.

**Presentation**: 3 — Precise and honest about what is standard, with helpful figures, but extremely dense, with key statements deferred to a sprawling appendix.

**Significance**: 2 — Clean answers to a narrow question; the exponential separations sit far from the regime studied empirically, where the gap is under 2× and a simple model wins.

**Originality**: 3 — The variance-scale formulation of fixed/r-round/branching gaps and the potential argument for rounds are new; the fixed-versus-branching theory is a re-expression of known query-complexity phenomena with standard statistical tools.

**Key Questions for Authors**

1. **Tightness in r.** Can you give an r-round upper bound for the pointer tree, or in general, that matches 2^(b−1)/(1+2b/r)^r up to poly(b), or else show sup_d V_r/V_branch = 2^(b−r) for some r ≥ 2? A characterisation of the r-round exponent up to lower-order terms for all r, not just constant r, would make Theorem 3 a substantially stronger contribution and would raise my score.

2. **Linear rounds in polynomial dimension.** Do you agree that the Theorem 3(c) contrast is exactly computable in ⌊log₂ b⌋ rounds, so that linear-round necessity is shown only for m = 2^b − 1? Can a layered pointer-chasing contrast with a shared table of D = poly(b) registers per level (m = O(bD log D)) give Ω(b/log b) rounds for polynomial competitiveness? Your hit/deep argument in D.1(b) looks adaptable, up to controlling collisions of composed random pointers. A correct statement in polynomial dimension, or at least a corrected abstract and Section 4, is necessary for me to consider the claims accurately stated.

3. **Beyond design-unbiasedness.** Can you make Prop. C.7 non-asymptotic, with an explicit n beyond which no estimator beats (1−ε)·W_A(P)/n locally, in terms of ‖h‖∞, J and cell masses? More importantly, does any separation survive in a structured model, for example when the law of (X,Y) is restricted to a k-way log-linear family? If the 2^(b−1) gap collapses to O(1) there, please say so; if it persists for natural families, that would materially increase significance.

4. **Explaining the benign instances.** Is there an instance-level quantity that is provably within a small constant of W_fixed/W_branch for tree-computable d? W_PS is empirically within about 2–4% of the optimum; does it admit a closed form or a two-sided bound in terms of path masses and shared coordinates? A result of this kind would connect the theory to Section 6 and change my view of weakness 3.

5. **Novelty of the potential bound.** Please state how Theorem D.3(b) relates to known average-case round/query lower bounds for tree evaluation or pointer chasing with bounded adaptivity, and clarify the Li et al. (2026) attribution. If the per-round factor (1+2a) is essentially known in the exact-evaluation setting, the remaining novelty is the variance interpretation, which would lower my originality assessment.

**Limitations**

Mostly yes; the limitations section is candid about design-basedness, oracle tuning, order effects, identification and solver scale. Three additions would help:
- State explicitly that linear-round necessity is proved only with exponentially many features.
- State that the general finite-sample theorem loses a constant (104) larger than the gap itself at the caps studied (b ≤ 6).
- State that the "records ratio" interpretation for arbitrary estimators is asymptotic with an unquantified threshold, and that Figure 3(b) shows it is not yet binding at the sample sizes considered.

**Overall Recommendation**: 3 — Weak reject

The paper is correct, careful and complete in what it sets out to do, and I see it as borderline. Against the bar I apply as a theory reviewer, the central fixed-versus-branching results are elementary translations of known separations, the one new argument (rounds) leaves an exponential gap and is partly over-claimed, and the paper's own experiments show the worst-case phenomena are far from the practical regime, where the design-unbiased benchmark is beaten by a simple model. I would not argue strongly against acceptance if other reviewers value the theory–computation–experiment package.

**Confidence**: 4

I verified the main proofs and one exact example numerically and I know the adjacent literature. I did not check the solver, the experimental appendices in detail, or every auxiliary proposition.

**What would move me up one point**

- Correct the abstract and Section 4 so that linear-round necessity is tied to m = 2^b − 1, or prove a super-logarithmic (ideally Ω(b/log b)) round requirement in polynomial dimension.
- Tighten Theorem 3 in at least one direction, so the r-round exponent is determined up to lower-order terms beyond constant r, or settle whether 2^(b−r) is attained for r = 2.
- Add one result that connects theory to the benign empirical regime: an instance-tight (constant-factor) characterisation of W_fixed/W_branch for tree-computable targets, or a statement about the gap under a structured (e.g. low-order log-linear) model.
- Streamline: move the full statements of Theorems 3 and 4 into the main text and drop appendix material the paper does not use.

The first item together with either the second or the third would move me to a 4. The first item alone would not.
