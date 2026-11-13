# Round 10 — simulated review R1 (theory) of v20 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject, borderline)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in your own words, not the abstract)

The paper studies estimation of one known linear functional Δ(P) = E[Y d(X)] (accuracy, or accuracy difference, of frozen rules on X ∈ {−1,1}^m, deg d ≤ b) when each record reveals at most b features and the label is free. It compares three protocol classes by the number of records they need: "fixed forms" (the b coordinates are chosen before the record is seen, possibly using earlier records), r-round interviews, and fully adaptive depth-b decision trees.

Main claims:
- **Theorem 1.** Any branching protocol can be simulated exactly in law by fixed forms using K_{m,b} = min{2^{b−1}, C(m−1,b−1)} times the records in expectation. The construction guesses one of the tree's padded path sets and applies rejection sampling. The factor 2^{b−1} is attained by the address (index) function with m = b−1+2^{b−1}, via an L2-projection bound on what any b-subset explains.
- **Theorem 2.** r rounds reduce the upper bound to 2^{b−r}. A binary pointer tree gives the lower bound 2^{b−1}/(1+2b/r)^r via a potential argument; products give 2^{b(1−o(1))} for constant r in dimension ≤ b².
- **Theorem 3.** The worst-case first-order constant V and the population (local-asymptotic-minimax) constant W are convex programs with a dual "witness" form. At a population the ratio is bracketed by 1/ρ_P² and N_P(τ). A column-generation solver with dynamic-programming pricing over trees computes certified optima.
- **Theorem 4.** Under a parametric model the simulation bound persists. Under conditional independence given the label the gap is ≤ 2 (and 1 if forms may depend on the label). Under order-k log-linear models it is ≤ (b+1)^k at product laws. Strongly coupled pairwise laws restore 2^{b−1}/b.
- **Experiments.** On small trained trees and forests (m ≤ 12–13 items, b ≤ 6) the optimal fixed/branching ratio is 1.0–2.38, two rounds recover most of it, and a pairwise working model reduces it to ≤ 1.28 at the cost of non-vanishing bias.

**Strengths**

- **The statements I checked are correct.** I verified:
  - the path-guessing simulation (Thm C.1), including the claim that M_{τ,S}(x_S)=1 iff S = S_τ(x) and the independence of the acceptance event from (X,Y);
  - the address-function energy bound (3) and its product version (Prop. C.5);
  - the duality and van Trees converse (App. B.3), including the arithmetic of the 1/104 constant;
  - the pointer-chasing "lucky hit" bound (Thm D.1(b));
  - the potential argument (D.3) for the binary pointer tree and its tensorisation across blocks;
  - the centred-score argument for W_fixed ≤ K·W_branch (Thm E.1(a));
  - Thm E.5(a)–(e).
  I found no errors.
- **Theorem 1 is a clean, quotable, exactly tight statement.** The simulation is a comparison of experiments (any estimator, test or loss, non-asymptotic in the upper direction), not only a variance bound. It improves the textbook non-adaptive Fourier-sampling second moment ‖d̂‖₁² (4^{b−1} for the address function) to 2^{b−1}, with a matching lower bound against biased estimators, across-record adaptivity and label-dependent form choice.
- **The round hierarchy has some technical content.** The potential Q_t = M_t + 2^L π_t, which is multiplicative across blocks even when the interview splits its budget adaptively, pins the exponent for constant r at b − O(r log b). This is the most substantive proof in the paper.
- **The authors are candid about scope.** They state that the ingredients of Theorem 3 are standard, that Theorem 1(i) is the across-records version of a folklore conversion, and they list what is open: the (1+2b/r)^r factor, m close to b, rounds in polynomial dimension, and the absence of any bound between parts (c) and (e) of Theorem 4.
- **The computation is certified and the empirical message is honest.** The solver produces primal/dual certificates, and the paper reports that the exponential worst case is not what one sees on trained rules, and that much of the naive gap is design optimisation.

**Weaknesses** (numbered; mark each as [major] or [minor])

1. **[major] The headline theorem is elementary and close to folklore.** The upper bound in Theorem 1 is "guess the root-to-leaf path, keep the record if the guess is right", with at most 2^{b−1} path sets. The lower-bound instance is the index function, and the bound is a two-line projection computation plugged into a standard dual. The related-work section itself concedes that the 2^q conversion is folklore and that the contribution is carrying it out across records with an acceptance step. The exact constant and the Blackwell-type phrasing are nice, but for a theory audience the depth is that of a well-executed observation. Theorem 3 is standard by the authors' own account (Donoho-type duality, c-optimal design, AIPW efficiency). This leaves Theorem 2(b) and parts of Theorem 4 as the technically new material, and both are incomplete (points 2 and 3).

2. **[major] The round results are not tight beyond constant r.** The upper bound 2^{b−r} and the lower bound 2^{b−1}/(1+2b/r)^r differ by (1+2b/r)^r/2^{r−1}. The lower bound is vacuous for r ≳ 0.37b, while the upper bound is still 2^{0.63b} there. In polynomial dimension the lower bound is informative only for r = o(log b / log log b). The paper's own numerics (Table 5: 1.80 vs 2 and 3.33 vs 4) suggest the truth is c·2^{b−r}, so the polynomial loss looks like an artefact of the potential argument. The upper bound uses one query per round in the first r−1 rounds, which is unlikely to be optimal either. "Each round of adaptivity halves the bound" is therefore a statement about an upper bound, not about the price.

3. **[major] Theorem 4 is a set of endpoint calculations, not a theory of when a model removes the gap.**
   - Part (b) reduces to the observation that under conditional independence, information depends on a design only through inclusion probabilities; the factor 2 is averaging two inclusion vectors.
   - Part (c) holds only at product laws, where the label is independent of all features (a rule no better than chance), plus a neighbourhood of unspecified radius. It is a crude Cauchy–Schwarz over monomials. This sits awkwardly next to the emphasis elsewhere on "rules of any accuracy".
   - The exponent in (c)/(d) is only located between max{k−3,1} and k.
   - Part (e) obtains the pairwise "counterexample" as a β→∞ limit in which auxiliary features become deterministic functions (one-hot copy, products) of the others. On the limiting support the pairwise model is no restriction for this target. That is a legitimate remark about coding-dependence of log-linear order, but it is a degenerate construction.
   - The abstract's claim that the gap "depends on how strongly the features depend on one another" is supported by two extremes and numerics, with no quantitative theorem in between (the paper says so on p. 5).

4. **[major] The worst-case theory does not explain the empirical regime, and the exponential gap is fragile to the formulation.**
   - Extremality needs m ≥ b−1+2^{b−1} (or products with m ≈ b²), a uniform profile law, and address/pointer targets.
   - On real rules the ratio is 1.0–2.38, and the paper's instance-level bracket [1/ρ_P², N_P] is too loose to predict it (e.g. [1.13, 10.5] against 1.58 at b = 6). Every practically relevant conclusion comes from numerically solving small instances, not from the theorems.
   - The gap depends on the cap being hard. Under a mean budget the ratio is at most m/b (App. C.5.1), so in polynomial dimension the 2^{b(1−o(1))} separation collapses to poly(b).
   - There is no resource-augmentation statement (fixed forms with cap b+c or αb against trees with cap b), which is the natural robustness check for adaptivity gaps.
   - For a single tree, the adaptive "optimum" is simply evaluating the known rule, so the comparison is "observe t exactly" versus "guess the path". This is why W_branch = σ_P² trivially and why the question is less rich than the title suggests.

5. **[major] The presentation is overloaded for an 8-page conference paper.** The submission is 65 pages with four multi-part theorems, more than 20 propositions and corollaries in the appendix (many tangential: Prop. B.3, Thm C.4, Prop. C.7, Prop. C.9, App. G), and at least ten distinct constants (V, W, M, W^T, W^{(k)}, W^{lab}, W^{ci}, W_PS, N_P, ρ_P, K_r, ν_k, L_k, U_3). The main body contains proof sketches only. Theorem 4 has five parts stated in running text, and none of the central claims can be verified without the appendix. It reads like a compressed journal paper (Annals / JMLR / IEEE-IT), and the breadth obscures which result the authors consider the contribution.

6. **[minor] "Exact" is asymptotic on the lower-bound side.** nR_A → V and W/n is a local asymptotic minimax risk with an oracle design centred at P and a full-support requirement (hence the 1% uniform smoothing in every experiment). The finite-sample equivalence carries a factor 10⁴ (Thm B.1). Only the address function has an explicit finite-n ratio (Prop. C.2, n ≥ 60·2^{b−1} for half the gap). The abstract's "for every task, sample size and population" applies to the simulation upper bound, not to the attained gap.

7. **[minor] The restricted setting limits reach.** A single known functional is fixed in advance (the paper notes records can be nearly useless for another rule, with a factor up to 317). Labels are free and always observed, features are binary and noiseless, there are no order effects, and the solver's exact adaptive designs stop at m ≤ 12, b ≤ 6 (or m = 20, b = 3).

8. **[minor] Positioning.**
   - The non-adaptive Fourier/L1 baseline for decision trees (Kushilevitz–Mansour) should be cited as the classical comparison point. It is mentioned only in passing in App. C.1.3, without attribution.
   - The statistical literature on interactive versus non-interactive protocols for functional estimation under local privacy (e.g. Butucea–Rohde–Steinberger on quadratic functionals) and unified interactive lower bounds under information constraints (Acharya–Canonne–Sun–Tyagi) are closer analogues than several cited works.
   - I could not verify a few 2026 references from memory (Li et al.; Lau & Scarlett; Aronow & Lopatto). Please double-check them.

9. **[minor] Layout and details.**
   - There is a large blank block on p. 3.
   - In Table 2 the "two rounds" and "bracket" columns run together.
   - The main-text statement of Theorem 2(b) silently requires b ≥ 8 for r = 2 to be non-trivial (noted only in the appendix).

**Soundness** (1-4) with one-line justification

3 — All proofs I checked (Thms 1, 2, 3(a,c), 4(a–e), B.1, C.1, D.1, D.3) are correct; deductions are for the asymptotic/oracle nature of the "exact" constants and for numerical claims I could not verify.

**Presentation** (1-4) with one-line justification

2 — Individual statements are precise, but the paper is badly overloaded; the main body is a dense index to a 57-page appendix.

**Significance** (1-4) with one-line justification

2 — A tidy exact answer to a narrowly posed question, whose extremal regime is far from the empirical one (gaps ≤ 2.4) and sensitive to the hard-cap convention; the model theory is incomplete.

**Originality** (1-4) with one-line justification

3 — The "price in records" formulation and the comparison of design classes with exact constants are new to my knowledge; the techniques (path guessing, index function, pointer chasing, van Trees, c-optimal design) are standard.

**Key Questions for Authors** (3-5 numbered; for each, say how the answer would change your evaluation)

1. **What in Theorem 1 goes beyond folklore plus the index function?** Is there a non-obvious step, or a strictly stronger statement you can prove — for example the exact extremal ratio for all (m,b) including m close to b, or tightness of the experiment-comparison factor K (not only of V) for natural families? A substantive answer would raise my originality and significance scores. If the answer is "the constant and the framing", weakness 1 stands.

2. **Can you close the round gap?** Either remove the (1+2b/r)^r factor to get c·2^{b−r} (your Table 5 suggests this), or show an r-round simulation better than 2^{b−r} using multi-query early rounds; and can anything be said for r = Θ(b), or for r ≥ log b in polynomial dimension? A tight r-round theorem would be a real technical contribution and would move me to accept.

3. **Does Theorem 4(c) extend beyond fully independent laws?** As stated, the label is independent of the features. Can you give an explicit radius, or a bound for laws where features are (conditionally) independent but depend on the label under an order-k model, for example in terms of a Dobrushin-type or correlation-decay parameter? A quantitative interpolation between (b)/(c) and (e) would turn Section 5 from examples into a theorem and raise significance.

4. **How robust is the gap to the cap convention?** What is the fixed-versus-branching ratio when fixed forms get cap b+c or (1+α)b, or a mean budget b with hard cap B, for general targets in polynomial dimension (not only the address function of Prop. C.7)? If the exponential gap disappears under mild augmentation, the headline should be reframed as a hard-cap phenomenon (lower significance). If it persists, e.g. for the product constructions, that would strengthen the paper.

5. **Is there an instance-level quantity that determines W_fixed/W_branch up to a constant or log factor?** The [1/ρ_P², N_P] bracket is loose exactly where it matters. Can you explain structurally why trained trees sit at 1–2.4 (e.g. via path-mass concentration or shared prefixes)? A tight instance characterisation would connect the theory to the experiments and address weakness 4.

**Limitations** ("yes" if adequately discussed, otherwise constructive suggestions)

Mostly yes. Section 8 and the appendix are unusually forthright about the single known target, free labels, oracle/asymptotic constants, the 10⁴ factor, solver scale and open problems. Two additions would help in the main text:
- State prominently that the exponential gap needs a hard per-record cap and collapses to ≤ m/b under mean budgets.
- State that Theorem 4(c) applies at laws where the label is independent of the features.

**Overall Recommendation** (integer 1-6, with label)

3 — Weak reject. This is a borderline case. The paper is technically solid and I found no errors, but the headline result is elementary and near-folklore, the genuinely new parts (rounds, models) are not tight or are endpoint-only, the worst-case theory does not account for the empirical regime, and the presentation is that of a compressed journal paper. I would not strongly oppose acceptance if other reviewers value the formulation and the certified computations more than I do.

**Confidence** (1-5)

4 — I read the main body in full and checked the key proofs in Appendices B–E line by line. I did not verify the numerical experiments, the solver, or Appendices F–H.

**What would move you up one point** (concise, concrete list; be honest — if nothing realistic would, say so)

Any one of the first three would move me to 4; the fourth would help in combination with one of them.

- A tight r-round theorem: Θ(2^{b−r}) up to constants, or at least up to poly(b) for all r, not only constant r; or a matching improved upper bound.
- A quantitative version of Theorem 4(c) with an explicit dependence parameter that covers laws where the label depends on the features, interpolating to (e).
- An instance-level characterisation of W_fixed/W_branch that is tight up to constants and explains the 1–2.4 range, or a resource-augmentation / mean-budget theorem for general targets clarifying how much of the gap is a hard-cap artefact.
- A restructured submission: one focused story (Theorems 1–2 plus one of the computation or model sections) with complete proofs of the central results in the main body, tangential appendix results removed, the non-adaptive Fourier baseline and interactive-LDP functional-estimation literature properly positioned, and the abstract's "exact / every sample size" claims scoped to what is non-asymptotic.

A rebuttal alone is unlikely to deliver the first three; the fourth is realistic in a revision but on its own leaves me at borderline.
