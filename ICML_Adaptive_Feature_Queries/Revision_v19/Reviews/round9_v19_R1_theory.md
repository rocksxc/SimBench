# Round 9 — simulated review R1 (theory) of v19 (`Manuscript/paper.pdf`)

Overall Recommendation: **3 (Weak reject)** — Confidence 4 — Soundness 3 / Presentation 3 / Significance 2 / Originality 2.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in your own words, not the abstract)

The paper studies estimation of one known linear functional, Delta(P) = E[Y d(X)], where d is a known function of Fourier degree at most b on {-1,1}^m (for example the accuracy of a frozen depth-b tree). Each record reveals its label for free and at most b features. Three protocol classes are compared: pre-committed b-subsets ("fixed forms"), r-round interviews, and fully adaptive depth-b trees ("branching").

- **Theorem 1.** Any branching protocol is simulated exactly by fixed forms using a geometric number of records with mean K = min{2^(b-1), C(m-1,b-1)} per branching record: guess one of the tree's padded path sets and reject otherwise. The factor 2^(b-1) is attained by the addressing (multiplexer) function, via a projection-energy computation plugged into a c-optimal-design dual.
- **Theorem 2.** r rounds reduce the simulation factor to 2^(b-r). A binary pointer tree gives a lower bound 2^(b-1)/(1+2b/r)^r via a potential argument, and products give a poly(b)-dimension version for constant r.
- **Theorem 3.** The worst-case first-order constant V and the population (local asymptotic minimax) constant W_A(P) are convex programs with a Cauchy-Schwarz/Sion dual. W_fixed/W_branch is bracketed by 1/rho^2 and a Renyi-1/2 "effective number of path sets". A column-generation solver certifies the optimum for each class.
- **Theorem 4.** Under an order-k log-linear model the simulation bound still holds. At product laws the gap is at most about (b+1)^k. For the address contrast it is 1 at k=2 and at least about b^(k-3) for k>=3. Near-deterministic pairwise laws on auxiliary one-hot and product features restore 2^(b-1)/b.
- **Experiments.** On BRFSS, thyroid, Spambase and forest updates, optimized forms need 1.0-2.38 times the records of branching. Two rounds remove most of the gap, and a pairwise working model nearly all of it, at the cost of a non-vanishing bias.

**Strengths**

1. A cleanly posed question with a crisp, exactly tight headline answer (2^(b-1) when m >= b-1+2^(b-1)). The simulation is estimator-, loss- and model-agnostic: a comparison of experiments rather than a risk bound, and hence stronger than what the lower bound alone would require.
2. The proofs I checked are correct:
   - Theorem 1(i)-(iii) and Theorem C.1;
   - the dual formulas (B.2)/(B.3) and the van Trees converse;
   - the energy computations for the address contrast and its products (Prop. C.5);
   - Theorem D.1(b) (lucky-hit argument);
   - Theorem D.3 (the potential Q_t = M_t + 2^L pi_t; I re-derived (D.3), including the G(u)F(u) decomposition and the multiplicativity across blocks);
   - Theorem E.1(a)-(c) and Prop. E.3;
   - Theorem E.5(a), (b) and (d).
3. The round result is the most interesting technical piece. The potential argument is neat. The conclusion that a constant number of rounds can lose 2^(b-O(r log b)), and that a polynomial-factor approximation on the pointer tree needs about 0.37b rounds, is a genuine round hierarchy for an estimation problem under a per-sample query cap.
4. The paper is unusually candid. It says the simulation is folklore in query complexity and the analogue of Joseph et al. (2019). It says the ingredients of Theorem 3 are standard. It lists the open gaps: m close to b, the rounds exponent, the product-law exponent between k-3 and k, and the non-explicit radius.
5. The constants are computable with primal/dual certificates, and the experiments report what the theory does not predict (the bracket is loose; Theorem 4 does not predict the model ratios). Prop. E.3, showing the worst case is not an artefact of chance-level rules, is a worthwhile detail.

**Weaknesses** (numbered; mark each as [major] or [minor])

1. [major] **The headline theorem is technically shallow, and the phenomenon is known.**
   - The upper bound is path guessing with rejection, the same device as the fully-to-sequentially-interactive LDP conversion and the standard adaptive-to-non-adaptive conversion in query complexity. The authors say so themselves.
   - The lower bound is the textbook addressing function with a three-line conditional-expectation computation, plugged into Elfving/Donoho-type duality.
   - Exponential adaptive versus non-adaptive separations under per-sample query access already exist for testing (huge-object model; the locally bounded class of Adar-Fischer; Chakraborty et al.).
   - What is new is the exact constant for a single linear functional and the "price in records" framing. That is a tidy observation, but not on its own an ICML-level theoretical contribution.
   - Theorem 3 is c-optimal design plus semiparametric efficiency under known coarsening.

2. [major] **Where the problem becomes non-trivial, the results are not tight.**
   - Rounds: the upper bound is 2^(b-r) and the lower bound 2^(b-1)/(1+2b/r)^r. For r = Theta(b) the exponents do not match. The lower bound is vacuous for r=2 until b >= 8.
   - The paper's own numerics show the pointer tree does not attain 2^(b-r) for r >= 2 (1.80 vs 2; 3.33 vs 4). No evidence is given that part (a) is sharp for any r >= 2.
   - In polynomial dimension the lower bound covers only r = o(log b / log log b).
   - Models: the product-law exponent lies between max{k-3,1} and k.
   - The regime K = C(m-1,b-1) is open: already at (m,b) = (4,3) the answer is only known to lie in [2.457, 3].

3. [major] **Theorem 4 supports the abstract's dichotomy only weakly.**
   - (b) holds at exactly product laws; the "neighbourhood" has a non-explicit radius that may be exponentially small in m and b. "Near independence the gap is polynomial" therefore has no quantitative content.
   - For k=2, the model actually used in the experiments, the bound nu_2 = Theta(b^2) appears far from the truth. The argument the paper uses for the address contrast in (c) seems to give W^(2)_fixed = W^(2)_branch for every contrast at uniform laws. The gradient is supported on {label} and the pairs {j, label}; the corresponding information block of any tree is diagonal with entries P(j read), summing to at most b; and any such inclusion-probability vector is realizable by forms. So at uniform laws the pairwise model has no adaptivity gap at all, and (b) says nothing useful there.
   - (d) is obtained at near-deterministic laws (beta to infinity) on b-1+3*2^(b-1) features, using the standard quadratic-penalty encoding of a product with auxiliary variables. It shows that M_2 with auxiliary features is universal, not that realistic strong dependence restores the gap. No dependence of the gap on coupling strength is given.
   - The W^T constants are only lower bounds on the local minimax risk when the optimal information is singular, which is exactly the k=2 address case.
   - As a result the empirically relevant regime (pairwise ratios 1.00-1.28 at dependent laws) is entirely outside the theory, as the authors acknowledge.

4. [major] **Scope and significance of the formulation.**
   - The estimand is one known functional of degree at most b, labels are free, and the cap equals the depth of the audited rule. For a single tree the adaptive side is trivial (run the rule), so the theory prices "not being allowed to run the rule".
   - The exponential worst case needs addressing-type rules and a hard per-record cap; under a mean budget the ratio is at most m/b.
   - On every trained rule examined the price is a small constant (median about 1.4, at most 2.38) and mostly disappears with one extra round.
   - The paper thus establishes a worst-case exponential that it then shows is largely absent in practice. That is an honest finding, but it limits impact on both the theory and the applied side.

5. [minor] **"Exact" is first-order or oracle.**
   - V is a limit of n*R; the finite-n characterization carries a factor 10^4.
   - W is tuned to P; the centred simulation score in Theorem E.1(a) uses c = Delta(P), the estimand itself.
   - The exact simulation needs a random number of records.
   - All of this is disclosed, but the abstract's "for every task, sample size and population" should be read with these caveats.

6. [minor] **Presentation.**
   - The 8-page body is extremely compressed, and the 50-page appendix contains many side results (C.2-C.8, E.6-E.9, G) that dilute the message.
   - Theorem 2(c) and Theorem 4(c),(d) are barely explained in the body.
   - Notation is overloaded: r is both rounds and the number of data bits; N_P versus N_{r,kappa}; K_r versus K_{m,b}.
   - The headline pairwise range is quoted as "at most 1.28" (abstract), "1.02-1.28" (introduction) and "1.02-1.13" (Sections 6 and 8) for different run sets, without saying so.

7. [minor] **Positioning.** The relation to the huge-object and locally bounded literature and to restricted-focus-of-attention / statistical-query views of fixed forms (forms reveal only b-wise marginals with the label) is asserted in one sentence each. A precise statement of what does and does not transfer is missing, for example whether Theorem 1(i) is literally the known conversion and whether the testing lower bounds imply an estimation lower bound up to constants.

**Soundness** (1-4) with one-line justification

3 — I found no errors in the proofs checked (Theorems 1, 2, D.3, E.1, E.5(a,b,d), the duality and the van Trees converse); the deduction is for first-order/oracle "exactness" and for model constants that are only lower bounds when information is singular.

**Presentation** (1-4) with one-line justification

3 — Well organised, with helpful figures and a constants table, but over-dense, with too many sub-claims per theorem and a sprawling appendix.

**Significance** (1-4) with one-line justification

2 — A narrow estimand and cap structure, an elementary headline result, and empirical gaps that are small constants; the main takeaway (optimize forms, add one round) is useful but modest.

**Originality** (1-4) with one-line justification

2 — The formulation and exact constant are new, but the simulation, the hard instance and the duality are standard; the round potential argument and Theorem 4(b)-(d) are the genuinely new, if incremental, technical parts.

**Key Questions for Authors** (3-5 numbered; for each, say how the answer would change your evaluation)

1. **Is the r-round upper bound 2^(b-r) attained, even for r=2, by any contrast, or can the lower bound be improved to 2^(b-r)/poly(b) for all r up to b?** Your own numerics (1.80, 3.33) suggest the pointer tree is not extremal. A matching bound for all r, or even a proof that 2^(b-2) is or is not attainable, would make Theorem 2 a real round-complexity result and would move me to accept.

2. **At uniform laws under the pairwise model, is W^(2)_fixed = W^(2)_branch for every contrast, as the diagonal-block argument in your proof of Theorem E.5(c) seems to give?** If so, what is the true worst-case ratio at general product laws for k=2 and for k>=3, and can the neighbourhood in (b) be made explicit, for example in terms of a Dobrushin-type or bounded-coupling condition? A quantitative weak-dependence theorem that explains the observed pairwise ratios of 1.0-1.3 would substantially raise significance.

3. **In Theorem 4(d), how does the gap depend on the coupling strength beta and on b?** Is there an exponential lower bound at couplings bounded by O(b) or O(log m), or without auxiliary features that d does not depend on? If the gap requires beta to infinity with auxiliary variables, I would regard (d) as a universality remark rather than one side of a dichotomy.

4. **Precisely which parts of Theorem 1 are not corollaries of known results?** Please state the relation to (i) the fully-to-sequentially-interactive LDP simulation, (ii) the locally bounded versus non-adaptive separations in the huge-object model, and (iii) the folklore 2^q conversion. If the answer is "the constant, and the estimation setting", I would keep my current assessment; a demonstration that the constant-level statement needs a new idea would raise originality.

5. **What is the extremal ratio when m is close to b (the C(m-1,b-1) regime), and with larger alphabets?** Is K_{m,b} ever attained when C(m-1,b-1) < 2^(b-1)? A complete answer would make "sharp" unconditional; this is a minor factor for my score.

**Limitations** ("yes" if adequately discussed, otherwise constructive suggestions)

Yes. The discussion is unusually thorough: free labels, the single known low-degree target, oracle and asymptotic constants, the factor 10^4, model misspecification, solver scale, and the open problems are all stated. I would only ask that the abstract reflect that the "near independence" statement has a non-explicit radius, and that the strong-coupling example is near-deterministic with auxiliary features.

**Overall Recommendation** (integer 1-6, with label)

3 — Weak reject. The paper is correct, careful and honest, and it is close to the bar. For a theory-led submission, however, the headline result is elementary and essentially known in spirit, the harder parts (rounds, models) are not tight, and the setting and empirical gaps limit significance.

**Confidence** (1-5)

4 — I verified the main proofs and know the neighbouring literature (information-constrained estimation, LDP interactivity, query/huge-object adaptivity) well. I did not check the solver, the experimental appendices, or every side proposition, and I could not look up the exact statements of the cited huge-object results.

**What would move you up one point** (concise, concrete list; be honest — if nothing realistic would, say so)

Any one of the following would move me to 4:

- A tight or near-tight r-round result: either 2^(b-r)/poly(b) for all r, or an improved upper bound matching the pointer tree, or the linear-rounds lower bound in polynomial dimension.
- A quantitative weak-dependence theorem for the pairwise or order-k model with an explicit condition and the right exponent, including the k=2 product-law case, which I believe is identically 1 at uniform laws; ideally with a coupling-strength interpolation towards (d).
- A precise novelty statement relative to the LDP and huge-object results, together with a trimmed, less overloaded main text. This alone would not suffice, but combined with partial progress on either point above it would.

Additional experiments would not change my score.
