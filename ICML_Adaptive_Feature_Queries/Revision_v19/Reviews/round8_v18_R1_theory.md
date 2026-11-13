# Round 8 — simulated review R1 (theory) of v18 (`Manuscript/paper.pdf`)

Overall Recommendation: **4 (Weak accept)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words, not the abstract)

The paper studies estimating a known linear functional Δ(P) = E_P[Y d(X)] (accuracy, or accuracy difference, of frozen rules; d of Fourier degree ≤ b on {−1,1}^m) when each record reveals its label for free but at most b of its m features. It asks how many more records are needed when each record's b coordinates are fixed in advance ("fixed forms") than when they are chosen by a depth-b decision tree ("branching"), with r-round batching in between.

- **Theorem 1.** The worst-case first-order minimax constant V(d, A) of any finite menu of interviews is a convex program with an explicit dual (signal of a perturbation over the largest projection energy one interview captures). It is proved by Sion/Fenchel duality plus van Trees. A population-specific analogue W_A(P) is a c-optimal design value, shown to be the local asymptotic minimax constant (Prop. C.8).
- **Theorem 2.** Fixed forms need at most K_{m,b} = min{2^{b−1}, C(m−1, b−1)} times the records of branching. The argument pads a tree to b distinct queries per path, guesses one of its at most 2^{b−1} path sets, and keeps the record only if the path completes; this rejection step simulates the branching experiment exactly (Thm C.1). The address (indexing) function on b−1+2^{b−1} bits attains the factor 2^{b−1}; products of address blocks give 2^{b−O(b/log b)} with m ≤ b².
- **Theorem 3.** r rounds need at most 2^{b−r} times the records of branching. A binary pointer tree on 2^b−1 bits gives V_r ≥ 2^{b−1}/(1+2b/r)^r by a potential-function ("lucky hit") argument, and products give a weaker statement in polynomial dimension.
- **Theorem 4.** At a population P, the ratio is bracketed as 1/ρ²_P ≤ W_fixed/W_branch ≤ N_P(τ) ≤ K_{m,b}.
- **Theorem 5.** Within a parametric model, the same simulation factor bounds the gap. For order-k log-linear models at product laws the gap is at most ν_k ≤ (b+1)^k. For the address contrast at the uniform law it is exactly 1 under the pairwise model. A constructed pairwise law with near-deterministic couplings restores 2^{b−1}/b.
- **Computation and experiments.** A column-generation solver with primal/dual certificates computes the constants. On BRFSS trees and small forest contrasts the design-based ratios are 1.0–1.98, and about 1.02–1.13 under a fitted pairwise model.

**Strengths**

1. The theory I checked is correct, and the statements are carefully hedged. I verified:
   - the duality and van Trees argument for Theorem 1 (B.3.1, B.3.3);
   - the padding count and the rejection simulation (C.1.1–C.1.3);
   - the address energy computation λ2^{s−2κ} ≤ 2^{−κ} (C.1.4);
   - the potential inequality E[Q_t | T_{t−1}] ≤ (1+2n_t)Q_{t−1} and its combination (Thm D.3);
   - the centered path-guessing bound and the witness bound (Thm E.1);
   - Theorem E.5(a)–(d), including the diagonal-information argument for k = 2 and the quadratic-penalty construction in (d).
   
   I found no errors.
2. Theorem 2(i)/C.1 is a comparison of experiments, not just a variance bound. It therefore holds for every estimator, loss, sample size and model, and it transfers verbatim to Fisher information (E.5(a)). The centering trick (c = Δ(P)) that makes the factor hold for variances at every population is a nice touch.
3. The headline constant is tight: 2^{b−1} is matched exactly, at populations of every accuracy (Prop. E.3), with near-tightness in polynomial dimension and a finite-sample version for the address contrast (Prop. C.2).
4. The round analysis goes beyond the textbook two-round indexing example. The potential argument for the binary pointer tree is the most substantive technical piece and gives exponent b − O(r log b) for fixed r against the upper bound b − r.
5. The question "does a model remove the adaptivity gap?" is original. The answer (polynomial at product laws, exponential again under strong pairwise couplings) is conceptually interesting and well illustrated.
6. Open problems are stated explicitly rather than papered over: m close to b, the (1+2b/r)^r factor, linear-round lower bounds in poly(b) dimension, and the exponent between k−3 and k.
7. Constants are computed with certificates, and the experiments are consistent with the theory. They show that the worst case is far from typical, which is a useful negative finding.

**Weaknesses**

1. [major] **Technical depth and novelty of the central result are modest.** The upper bound in Theorem 2 is the classical fact that a depth-b tree uses at most 2^{b−1} query sets, turned into a guess-and-reject simulation. The lower bound is the indexing function with a two-line Fourier energy computation. The qualitative exponential separation between non-adaptive and per-sample ("locally bounded") adaptive access is known (Goldreich–Ron; Adar–Fischer), as the paper acknowledges. What is new is the accounting in records under a hard cap and the exact constant 2^{b−1}. Theorem 1 is standard minimax duality for linear functionals with a design variable (Donoho; Juditsky–Nemirovski; Elfving), and Theorem 4 is Cauchy–Schwarz plus importance sampling. The paper is a broad collection of mostly elementary results, not one deep one.

2. [major] **Several bounds beyond Theorem 2 are not tight.**
   - (a) Rounds: the lower bound 2^{b−1}/(1+2b/r)^r is vacuous for r above about 0.37b, while the upper bound 2^{b−r} suggests b − O(log b) rounds may be needed. At r = 1 it loses a factor 2b+1 against the truth, and it exceeds one for two rounds only when b ≥ 8.
   - (b) Polynomial dimension: the product instance is solved exactly in ⌊log₂ b⌋ rounds, so nothing is shown beyond r = o(log b / log log b).
   - (c) Models: the exponent of the model-based gap at product laws is only located between max{k−3, 1} and k. The bound ν_k is a crude count of monomials.
   - (d) Small dimension: the extremal ratio for m close to b is open (already at (m,b) = (4,3) it lies in [2.457, 3]).

3. [major] **The model-based "dichotomy" rests on two endpoints, not a theorem about dependence.**
   - Part (b) holds at product laws and on a non-explicit neighbourhood whose radius depends on m, b, k, λ, ε.
   - Part (c) is one contrast at one law. There the result is close to tautological: at the uniform law the pairwise tangent space sees only the degree-1 part of d, a linear functional that needs no adaptivity. The optimal designs read only data bits and have singular information, so Δ is not identified away from P.
   - Part (d) is a near-deterministic re-encoding that makes the degree-b target quadratic in auxiliary features.
   - Nothing is proved for the intermediate regime of weak but non-zero dependence (e.g., a Dobrushin or high-temperature condition), which is what the claim "depends on dependence and not on parsimony" needs. The abstract's "exactly one for the extremal contrast under the pairwise model" should say it is a first-order statement at the uniform law.

4. [major] **"Exact constants" are first-order, local and oracle.**
   - V is a limit of n·R_n. The only general finite-sample statement carries a factor 10⁴ (Thm B.1).
   - W_A(P) is a local asymptotic minimax constant in the saturated model on 2^{m+1} cells. It requires full support and n large relative to the number of cells.
   - The optimal designs and scores are tuned to P, including the centering constant c = Δ(P), which is the estimand.
   - The worst case for V sits at chance-level labels. Prop. E.3 repairs this only for Boolean d with symmetric label noise.
   - The paper is candid about all this, but there is no non-asymptotic, design-adaptive version of Theorems 4–5 with explicit thresholds, which limits what the "ratio of records" means at survey sizes.

5. [major] **The formulation is narrow.** It assumes one known functional fixed before collection, exact Fourier degree ≤ b (which excludes most thresholded ensembles), free and always-observed labels, binary noise-free answers, and a hard per-record cap; under a mean budget the gap collapses to at most m/b (C.5.1). For a single tree the branching optimum is simply "run the rule", so the comparison reduces to how well non-adaptive b-subsets can estimate the mean of a decision tree. This limits the reach of the results within ML theory.

6. [major] **Presentation.** The 8-page body compresses five multi-part theorems, a solver and three experimental studies; the abstract is a list of numbers. Theorem 5(c) and the round discussion are close to unreadable without the appendix. No proof appears in the body, and the supporting material runs to about 50 pages of appendix that a conference review cannot fully verify. The work reads like a journal paper squeezed into conference format.

7. [minor] **The exponential gap needs exponential or near-quadratic dimension and adversarial structure.** On every trained rule examined the ratio is below 2, Theorem 4's bracket is loose (lower end 1.31 below the realized ratio, upper end 4.3 above), and a second round or a pairwise model removes most of the gap. The theory's headline quantity is thus mostly irrelevant in the regimes tested. This is partly a finding, but it weakens the significance of the sharp worst-case constants.

8. [minor] **Missing connections.** The path-guessing score versus the Fourier-sampling baseline (‖d̂‖₁²) is mentioned only in the appendix. The literature on adaptivity gaps in stochastic probing, and Le Cam deficiency as the natural language for Theorem C.1, are not discussed. It is not stated whether Theorem 2 implies anything new for testing in the locally-bounded huge-object model.

9. [minor] **Small statement issues.**
   - Theorem 1 says the iid design "attains V/n", while V is an infimum (attainment is argued only later, in C.4.2).
   - The generic bound L_k(b) ≥ C(b−1, k−2)/b is trivial for k = 3; the linear bound there comes from a separate argument (U₃).
   - Fixed-form values such as "exactly 4 and 8" for the pointer tree are numerical, not proved (the theorem gives 2^{b−1}/b).

**Soundness** (1-4): 3 — All key proofs I spot-checked (Thms B.2, C.1, address bound, D.3 potential, E.1, E.5) are correct; the reservations concern the first-order/local/oracle nature of the constants and the unverifiable volume of appendix material, not errors.

**Presentation** (1-4): 2 — Well organized and honest, but badly overloaded: too many results per page, a number-laden abstract, no proofs in the body, and key statements that cannot be parsed without the appendix.

**Significance** (1-4): 2 — A clean answer to a new but narrow question; the worst-case exponential gap is expected from known query-complexity separations and is shown empirically to be far from typical.

**Originality** (1-4): 3 — The formulation (price of within-record adaptivity in records, with exact constants, rounds and models) and the model-based question are new; the techniques are standard, with the pointer-tree potential argument the main exception.

**Key Questions for Authors**

1. **Rounds.** Can the factor (1+2b/r)^r be removed, or can you show V_r ≥ 2^{b−r}/poly(b) for all r on some instance? Alternatively, can you prove an ω(log b)-round requirement on poly(b) coordinates? A tight round hierarchy would lift the technical contribution well above the folklore level and would move me up.
2. **Weak dependence.** Can Theorem 5(b) be proved with an explicit neighbourhood, e.g. for order-k log-linear laws with couplings bounded by a Dobrushin-type condition, giving a poly(b) gap uniformly over that class? Without this the dependence-versus-parsimony message is supported only at product laws and at a near-deterministic construction. A quantitative theorem would move me up; an explanation of why it fails would clarify the scope.
3. **Non-asymptotics.** For Theorems 2(ii), 4 and 5, can you give finite-n statements with explicit, reasonable constants and thresholds (as Prop. C.2 does for the address contrast), for estimators that do not know P or Δ(P)? In particular, how large must n be relative to 2^m, or to the number of occupied path cells, before W_fixed/W_branch is the operative ratio? A convincing answer would remove my main reservation about "exact constants".
4. **Relation to prior separations.** What does Theorem 2 add, beyond the sample-versus-query accounting, to the non-adaptive simulations and lower bounds of Goldreich–Ron and Adar–Fischer for locally-bounded adaptivity? Does your simulation or lower bound yield a new or tight statement in that testing model? If the result is essentially a transcription, I would lower originality; if it implies something new there, I would raise it.
5. **Singular-information designs in Theorem 5(c).** Since the k = 2 optimum reads only data bits and does not identify Δ away from the uniform law, is the ratio still 1 + o(1) for procedures required to be locally uniformly consistent over a fixed (not 1/√n) neighbourhood in M₂? If the equality survives only at the single point, the "exactly one" claim should be weakened in the abstract and introduction.

**Limitations**

Yes. Section 9 is candid about scope: single known low-degree target, free labels, order effects, first-order and oracle nature of the constants, the 10⁴ finite-sample factor, solver scaling, and unweighted populations. I would additionally ask the authors to state in the abstract and introduction that the model-based results are local statements at or near product laws, and that the exponential lower bounds require m exponential (or about b²) in b.

**Overall Recommendation**: 4 — Weak accept

The paper is technically solid and unusually complete (tight main constant, exact simulation, round and model extensions, certified computation, experiments), and it opens a reasonable sub-area. It is borderline: the central theorem is elementary and expected, the harder results are not tight, the setting is narrow, and the presentation is overloaded. I would not argue strongly against a reject from a reviewer who weighs depth and significance more heavily.

**Confidence**: 4

I am confident in the assessment of Theorems 1–3 and 5 and their proofs, which I checked in the appendix. I did not verify the solver, the experimental appendices (F), or the remaining auxiliary propositions (C.4, C.6–C.8, E.3–E.9) line by line, and I cannot check the 2026 references.

**What would move me up one point**

- A tight or near-tight round hierarchy: remove (1+2b/r)^r, or prove a super-logarithmic round lower bound in polynomial dimension.
- A quantitative weak-dependence version of Theorem 5(b) with an explicit neighbourhood, plus a matching lower-bound exponent in k, so that the dependence-versus-parsimony claim becomes a theorem and not two endpoints.
- Non-asymptotic versions of the population and model ratios with explicit thresholds and without oracle knowledge of P.
- A restructured main body: fewer results, one complete proof (the simulation and the address lower bound fit in half a page), precise standalone statements of Theorems 3 and 5, and an abstract that states the results without a list of numbers.

Any two of the first three, together with the fourth, would make this a clear accept for me. The fourth alone would not change the score.
