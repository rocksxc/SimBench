# Round 7 — simulated review R1 (theory) of v17 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in your own words, not the abstract)

The paper studies estimation of a known linear functional Δ(P) = E_P[Y d(X)] on {−1,1}^m × {−1,1} (e.g. the accuracy of a frozen rule, or the accuracy difference of two rules) when each record reveals at most b of m features and the label is always observed for free. It compares three per-record acquisition menus: fixed forms (b coordinates committed before the record is seen), r-round interviews, and depth-b decision trees ("branching").

- **Theorem 1.** For any finite menu, n times the minimax MSE converges to a convex program V(d, A), with dual sup_{μ,h} ⟨d,h⟩²_μ / max_ι ‖E_μ[h | ℓ_ι]‖². A population version W_A(P) is a c-optimal design problem with a local-asymptotic-minimax interpretation.
- **Theorem 2.** V_fixed ≤ K_{m,b} V_branch with K_{m,b} = min{2^{b−1}, C(m−1,b−1)}, and the same holds for W at every P. The upper bound is "path guessing": pad the tree, draw one of its at most 2^{b−1} path coordinate sets, and importance-weight on completion. The addressing function on b−1+2^{b−1} bits attains 2^{b−1} exactly, at every noise level; products of address blocks give 2^{b−O(b/log b)} with m ≤ b².
- **Theorem 3.** r rounds lose at most 2^{b−r}. A binary pointer tree on 2^b−1 bits loses at least 2^{b−1}/(1+2b/r)^r, by a potential argument; products give a weaker statement with m ≤ b².
- **Theorem 4.** A population bracket 1/ρ²_P ≤ W_fixed/W_branch ≤ N_P(τ) ≤ K.
- **Theorem 5.** The same K bounds the gap in any parametric model. At product laws under a log-linear model of interaction order ≤ k the gap is at most ν_k ≤ (b+1)^k. For the address contrast it equals 1 at k=2 and is at least (4/9+o(1))b at k=3.
- **Computation and experiments.** A column-generation solver with DP pricing computes the constants with certificates. On BRFSS/thyroid trees and small forests the design-based gap is 1.0–1.98, mostly removed by a second round or a pairwise model.

**Strengths**

- The statements are precise and the proofs I checked are correct. I verified:
  - the duality and van Trees argument (B.3);
  - the path-guessing simulation and its centred version (C.1, E.1(a));
  - the address-function energy computation r·2^{s−2κ} ≤ 2^{−κ};
  - the m ≤ b² product construction (C.4.1);
  - the potential inequality (D.3) and its supermartingale/AM–GM combination;
  - Proposition E.3 (the gap at every accuracy);
  - Theorem E.5(a), (b), and the k=2 and k=3 computations in (c), including the Table 5 values 2.50 and 2.75 and the (4/9)b bound.
- The fixed-versus-branching constant is determined exactly (2^{b−1}, not 2^{Θ(b)}), with a matching instance, and nearly matched in polynomial and even linear dimension. The lower bounds hold against biased estimators, across-record adaptivity and label-dependent interview choice.
- Theorem 3(b) is a non-trivial argument. The potential M_t + 2^L π_t handles adaptive splitting across blocks cleanly.
- The paper is unusually candid. It says which ingredients are standard, lists open problems (rounds exponent, m close to b, non-product laws), and reports where its own bracket is loose and where solvers did not close.
- The treatment is complete: worst case, per-population, in-model, certified computation, and simulations that expose model bias.

**Weaknesses** (numbered; mark each as [major] or [minor])

1. **[major] The core results are elementary, and the qualitative phenomenon is known in neighbouring models.**
   - Theorem 1 is, as the authors say, linear-functional minimax duality plus a Fisher-information bound that is uniform over a channel family (the Acharya–Canonne–Tyagi / Barnes–Han–Özgür template with "channel" = interview).
   - Theorem 2's upper bound is a three-line importance-sampling argument, and its lower bound is a one-line Fourier computation on the canonical addressing function.
   - Theorems 3(a), 4 and 5(a) are the same simulation or a Cauchy–Schwarz step.
   - The guess-the-transcript simulation with exponential sample blow-up, and pointer-chasing round separations, are the same ideas as the fully-interactive to sequentially-interactive conversion and round separations in local privacy (Joseph et al. 2019, 2020) and the locally-bounded adaptivity results in the huge-object model (Adar & Fischer 2024). The paper cites these but does not compare the arguments.
   - What is new is the exact constant for one linear functional. That is a small increment for a paper whose headline is the theory.

2. **[major] The headline upper bound is more general and simpler than presented, which makes the surrounding machinery look heavier than its content.**
   - Under uniform path-set guessing, completion has probability exactly 1/L_τ at every profile, so it is independent of (X,Y).
   - Rejection sampling therefore simulates any branching protocol exactly, with a negative-binomial number of fixed-form records of mean ≤ K·n. This holds for every statistical task, every loss and every finite n, including across-record adaptivity.
   - Theorems 2(i), 2(ii), 3(a) and 5(a) are corollaries. Averaging t over completed records is exactly unbiased with no oracle centring at Δ(P).
   - The paper instead proves score-level statements with an oracle centre c = Δ(P), and mentions the experiment comparison only as an information inequality in Section 6.
   - Stated this way, the result is cleaner but also visibly folklore-level.

3. **[major] Tightness is incomplete in the parts with technical content.**
   - Rounds: the upper exponent is b−r and the lower exponent is b−1−r·log₂(1+2b/r). The lower bound is vacuous for r ≳ 0.37b, and already loses a factor b at r=1 on the pointer tree, where the numerics give exactly 2^{b−1}.
   - The paper's own small cases (1.80 < 2, 3.33 < 4) show that 2^{b−r} is not attained on this instance either.
   - In polynomial dimension the separation holds only for r = o(log b / log log b).
   - Models: the polynomial bound is proved only at product laws, with exponent between max{k−3,1} and k.

4. **[major] "What a model changes" rests on thin theory.**
   - Theorem 5(b) holds only where the features and the label are mutually independent. That is the least interesting point of a log-linear model, and ν_k degrades as ((1−λ)/λ)^k.
   - Theorem 5(c) is a single instance.
   - The k=2 "gap exactly one" is close to tautological. At the uniform law the pairwise tangent space sees t only through the D pairs (Z_j, Y), so the address structure is invisible. The optimal design reads only data bits, has singular information, and does not identify Δ away from P, as the authors note.
   - The claim that parsimony "removes most of the gap" at laws with dependence is supported only numerically (m ≤ 12).

5. **[major] The operational meaning of the population constants is asymptotic and oracle-based.**
   - W_A(P) is a local minimax constant over the saturated model on 2^{m+1} cells at a full-support P, with no sample-size threshold. The general finite-sample theorem carries a factor 10⁴.
   - Designs are tuned to P.
   - In the paper's own audits (n ≤ 32,000, m = 12), pairwise maximum likelihood on forms matches design-based branching. So "records needed" describes pointwise-unbiased scores, not estimators in general, at realistic n.
   - A non-asymptotic statement is easy on the upper side (see weakness 2) and missing on the lower side.

6. **[major/minor] The formulation is narrow.**
   - It needs a known functional of degree ≤ b, free and always-observed labels, a hard per-record cap (a mean budget collapses the gap to m/b), and a single target.
   - When one tree computes d, the branching optimum is "run the rule and average", so the comparison is against a trivial baseline.
   - For ensembles, where the problem is non-trivial, there is no structural theory of V_branch, only numerics at b ≤ 4.
   - Measured gaps are below 2 and mostly vanish with one extra round.

7. **[minor] Presentation is overloaded.**
   - Five theorems, a solver and three experimental studies sit in 8 pages; the abstract is a list of numbers; there are roughly a dozen constants (V, W, M, W^T, W^{(k)}, W_PS, W^{lab}, N_P, ρ_P, K, ν_k, L_k, U_3).
   - The 45-page appendix contains material in a different vocabulary ("audit", "update", "respondent multiplier", Theorem C.3, Proposition B.3) that reads as residue from another draft.
   - Figure 3 is too small to read.

8. **[minor] Missing comparisons and unverifiable references.**
   - The Fourier-ℓ₁ baseline is not mentioned: V_fixed ≤ ‖d̂‖₁² ≤ 4^b for depth-b trees, by monomial sampling. Path guessing improves this to 2^{b−1}, which is worth saying.
   - I could not verify a few 2026 references from memory, notably Li et al. as support for "round hierarchies for oracle evaluation". Please check them.

**Soundness** (1-4) with one-line justification

3 — Every proof I checked is correct and the claims are carefully scoped; the deductions are for the asymptotic/oracle nature of the W constants and the product-law restriction behind the model message, not for errors.

**Presentation** (1-4) with one-line justification

2 — Precise but extremely dense; too many constants and results for the page budget, and a sprawling, partly heterogeneous appendix.

**Significance** (1-4) with one-line justification

2 — A clean exact constant for a narrow problem, but the qualitative picture was known, the practical gaps are below 2, and the deeper parts (rounds, models) are only partially resolved.

**Originality** (1-4) with one-line justification

3 — The question (exact price in records of pre-commitment, by rounds and under models) and the certified computation over combinatorial menus are new; the techniques are standard.

**Key Questions for Authors** (3-5 numbered; for each, say how the answer would change your evaluation)

1. **Relation to the simulation in Joseph et al. (2019) and to Adar–Fischer.** Is Theorem 2(i)/3(a) more than the noiseless specialisation of the transcript-guessing conversion, and do you agree that rejection sampling gives an exact, task-agnostic, finite-n simulation with K·n expected records (weakness 2)? If you restate the upper bounds in that generality and delineate what is new, my originality and soundness assessments firm up. If a general statement fails for a reason I missed, that would raise my view of the centred-score analysis.

2. **Rounds.** Can you remove the (1+2b/r)^r factor, or show the true r-round constant is smaller than 2^{b−r} (your b=3,4 numerics suggest V_{b−1} ≈ 1.8, not 2)? Can you get any lower bound for r = Θ(b), or for r ≥ log b on poly(b) features? A matching exponent for all r, or a poly-dimension lower bound for r = ω(log b), would make Theorem 3 a substantial result and move me to accept.

3. **Models beyond product laws.** Is there a law in M_2 (or M_k with k fixed) with dependence at which W^{(k)}_fixed/W^{(k)}_branch is super-polynomial in b? Or can you prove a poly(b)^k bound under, say, a Dobrushin / high-temperature condition? Either answer would turn Section 6 from an example-driven observation into a theorem and raise significance by a point. If the ratio can be exponential in M_2, the abstract's message needs revision.

4. **Non-asymptotics.** For which n is W_fixed(P)/W_branch(P) a valid ratio of sample sizes against arbitrary estimators, given that your simulations show a misspecified pairwise MLE on forms matching design-based branching at n ≤ 8,000? A finite-n local lower bound with explicit dependence on the number of cells (or an honest restriction of the claim to unbiased estimators) would address weakness 5.

5. **Ensembles.** When no depth-b tree computes d, can you characterise or bound V_branch relative to full information, or show the fixed/branching gap can still approach K for probability-averaged forests? This is the only regime where the adaptive optimum is non-trivial; a positive answer would strengthen the case for the formulation.

**Limitations** ("yes" if adequately discussed, otherwise constructive suggestions)

Yes, largely. Section 9 and the appendix openly discuss the asymptotic/oracle nature of W, the 10⁴ factor, free labels, the single known target, order effects, model bias and solver scaling. Two suggestions:
- State prominently in the main text that Theorem 5(b) concerns laws with independent features and label.
- State that the "records needed" interpretation is for pointwise-unbiased scores, or n far larger than 2^m.

**Overall Recommendation** (integer 1-6, with label)

3 — Weak reject. The paper is correct, honest and thorough, but for a paper whose primary claim is theoretical the main theorems are elementary and qualitatively anticipated, the technically interesting parts (rounds, models) are left with sizeable gaps, and the formulation and measured effect sizes limit impact. It is borderline; I would not fight an acceptance if other reviewers find the statistical and design contribution compelling.

**Confidence** (1-5)

4 — I checked the main proofs (Theorems 1–5, including Appendices B.3, C.1, C.4, D.1, E.1, E.2) in detail. I did not verify the experiments or the solver. I am familiar with the adjacent literature but cannot rule out a closer prior result in survey design.

**What would move you up one point** (concise, concrete list; be honest — if nothing realistic would, say so)

Any one of the first three would move me to 4; the fourth alone would not.

- A sharper rounds theorem: a matching exponent b − r − O(1) or b − Θ(r) for all r on some family, or a lower bound for ω(log b) rounds in polynomial dimension.
- A model theorem at laws with dependence: a polynomial bound under a quantitative weak-dependence condition, or a counterexample.
- A restructured paper built on the exact experiment-simulation statement (any task, finite n, no oracle centring), with an explicit comparison to the LDP and huge-object arguments, a finite-n local lower bound, and the appendix reduced to what supports the main text.
- Presentation fixes alone (shorter abstract, fewer constants, a readable Figure 3) would not change my score.
