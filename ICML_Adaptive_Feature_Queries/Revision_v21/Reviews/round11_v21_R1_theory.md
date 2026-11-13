# Round 11 — simulated review R1 (theory) of v21 (`Manuscript/paper.pdf`) — official round

Overall Recommendation: **3 (Weak reject, borderline: "I could be argued to a 4")** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words)

The paper studies estimation of a known linear functional Δ(P) = E[Y·d(X)] (e.g. the accuracy of a frozen rule, or an accuracy difference) when each record reveals a free label and at most b of m binary features. It compares two per-record observation menus: "fixed forms" (a b-subset chosen before the record is seen, possibly randomized and adapted across records) and "branching interviews" (a depth-b decision tree on the record's own answers), with r-round interviews in between.

- **Theorem 1.** Any protocol on branching records is reproduced exactly in law by fixed forms with K = min{2^{b-1}, C(m-1,b-1)} times the records in expectation (guess one of the tree's padded path sets, then rejection-sample). The factor 2^{b-1} is attained in the first-order minimax MSE constant by the address (multiplexer) function on b-1+2^{b-1} features.
- **Theorem 2.** r rounds cost at most 2^{b-r}; a binary pointer tree gives the lower bound 2^{b-1}/(1+2b/r)^r. c extra questions buy between a (c+1) and roughly a (c+3)/4 factor in the worst case. Mean budgets are also treated.
- **Theorem 3.** The first-order minimax constants V (worst case) and W(P) (local, at a population) are convex programs with a dual "witness" form; a column-generation solver computes them with certificates.
- **Theorem 4.** The simulation bound survives any working model; under features conditionally independent given the label the gap collapses to at most 2; under a pairwise log-linear model a recoded address construction recovers 2^{b-1}/b.
- **Experiments.** On CART screening trees (BRFSS and others) the realised price is 1.0–2.4 in records, and largely disappears with one or two extra questions or one extra round.

**Strengths**

- The core statements I checked are correct, and I found no errors:
  - the path-set simulation (App. C.1, Thm C.1);
  - the address energy bound r·2^{s-2κ} ≤ 2^{-κ} and its use in the dual (C.1.4);
  - the noisy-label extension (Prop. E.3);
  - the extra-question count 2^{j+1}-j-2 and the address value 2^{b-1}/(c+1) (Thm C.2);
  - the pointer-tree potential argument (Thm D.3, inequality (D.3));
  - the van Trees converse for sequential and label-dependent protocols (B.3.3);
  - the conditional-independence calculation (Thm E.5(b));
  - the all-monomials proposition (C.3).
- The upper bound is stated in its strongest form, as an exact comparison of experiments for any task, estimator and loss. The lower bound holds against biased estimators, across-record adaptivity and label-dependent form choice, and at any rule accuracy. Exact constants, not rates, are obtained.
- The map of relaxations is systematic (rounds, extra questions, mean budgets, working models, families of targets), with upper and lower bounds side by side.
- The potential-function proof for the pointer tree is a neat argument and handles products cleanly.
- Two conceptual observations are worth having: the price vanishes for multipurpose collection (Prop. C.3), and within-record adaptivity has no first-order value under a naive-Bayes-type model once the label may drive the design (Thm 4(b)).
- The paper is unusually candid about what is folklore, what is open (m = 4, b = 3; rounds; polynomial dimension) and how far practice is from the worst case. Numerical claims come with primal/dual certificates.

**Weaknesses**

1. [major] **The headline theorem is technically shallow relative to the ICML theory bar.** Part (i) is the folklore adaptive-to-non-adaptive conversion plus a rejection step, as the authors say. The tightness proof is the canonical multiplexer example, with a three-line Fourier-weight computation plugged into a standard duality for linear functionals (Donoho / c-optimal design; the denominator max_ι‖E[h|ℓ_ι]‖² is the familiar χ²-information quantity of the information-constrained literature). The qualitative message, an exponential-in-b price that is tight, is what the decision-tree, huge-object and "locally bounded adaptivity" literature already leads one to expect. Theorem 3 is acknowledged to be standard. Theorem 4(b) is a short orthogonality computation. Theorem 4(c) is the address lower bound re-encoded through 2^b auxiliary one-hot and product features, at a loss of a factor b. The one new technique, the pointer-tree potential, sits mostly in the appendix and yields a non-tight bound.

2. [major] **The formulation that produces the gap is a knife-edge, and the adaptive side is degenerate.** In the headline comparison the cap equals the depth of a rule that a single tree computes, so "optimal branching" is just "run the rule and average" (W_branch = Var(t)), while forms sit exactly at the identification threshold deg(d) ≤ b.
   - The worst case needs the rule to depend on about 2^{b-1} features under an essentially product feature law.
   - It decays like 1/(c+1) with c extra questions, and is at most m/b under a mean budget.
   - The paper's own experiments show the realised price is about 1.5 and is gone by c = 2.
   - The setting also assumes free, always-observed labels and one known target fixed in advance, and excludes any contrast of degree above b, where both menus hit the same bias floor and only an upper bound is given (C.5.3).
   
   Taken together, the exponential theorem says little about the regimes the experiments and the motivation address. The theory is not parameterised by the quantity that the experiments identify as decisive, namely the number of relevant items beyond the depth.

3. [major] **Density and scope.** The submission is 68 pages. Roughly 2.5 pages of the main body carry all four theorems, and each depends on appendix material for definitions and proofs: Thm 3(b) on C.10; Thm 4 on E.5, whose statement has five parts; the solver on E.4. The abstract and introduction are walls of numbers. The local-minimax meaning of W(P) (oracle design tuned to P, full support, pointwise unbiasedness off-support) is not made clear where it is first used. This reads as a journal paper compressed into a conference format, and a reader cannot assess the main claims from the main body alone.

4. [minor] **The robustness claims are only partly tight.**
   - For rounds, the bounds 2^{b-r} and 2^{b-1}/(1+2b/r)^r differ by a factor exponential in r·log(b/r). The lower bound is vacuous for r ≳ 0.37b, and in polynomial dimension it covers only r = o(log b / log log b).
   - No contrast attaining 2^{b-r} is known for r ≥ 2, and the authors' own numerics for the pointer tree give 1.80 < 2 and about 3.33 < 4.
   - The Section 8 sentence that the value of adaptivity "accrues round by round" is therefore not established.
   - Tightness of Theorem 1 is proved only for m ≥ b-1+2^{b-1}. For m = poly(b) only 2^{b-O(b/log b)} is shown, and K_{m,b} is not shown tight for small m.

5. [minor] **The lower-bound populations are product feature laws.** The label is either pure noise or flipped at a constant rate. No theory covers feature dependence beyond the two extremes of Theorem 4 (near-product laws, or the artificial strong-coupling recoding); the intermediate regime is numerical only.

6. [minor] **Positioning.** The relation to the Acharya–Canonne–Tyagi framework should be stated precisely: forms and trees are two channel families, and across-record interactivity is orthogonal to the comparison. The same holds for k-RFA / weak-RFA learning (including work after Ben-David–Dichterman on which classes are k-RFA-estimable) and for the bounded-queries-per-sample results in the huge-object model. A few very recent citations (e.g. Li et al. 2026 for round hierarchies) I could not verify, and their relevance is unclear.

7. [minor] **Finite-sample statements are weak.** The general bracket has a factor 104. The simulation uses a random number of records, and the fixed-budget version is first-order only. "Exact price" should be read as an n → ∞ statement with m and b fixed.

**Soundness**: 3 — The key proofs I spot-checked (Thm 1, C.2, D.3, E.3, E.5(b), B.3) are correct and carefully stated. I could not verify all 55 appendix pages, and a few discussion sentences slightly outrun what is proved.

**Presentation**: 2 — Precise and honest, but severely over-compressed. The main body cannot be assessed without the appendix, and the abstract and introduction are overloaded with numbers.

**Significance**: 2 — A clean answer to a narrowly posed question. The worst case is exponential but requires a knife-edge cap, exponentially many relevant features and product laws, and the paper itself shows the practical price is small and easily removed.

**Originality**: 3 — The "price in records" formulation with exact constants, the pointer-tree potential bound, the conditional-independence collapse and the all-monomials result are new. The central upper and lower bounds use standard constructions and standard duality.

**Key Questions for Authors**

1. Can you state and prove the price as a function of the number of relevant variables k = b + w of the rule, jointly with c extra questions — a tight (up to constants) sup over depth-b trees on b + w variables? The experiments say w, not m, is the governing parameter. A sharp (b, w, c) characterisation would connect the theorem to the empirical findings and would raise my significance score.

2. For r = 2, is the truth 2^{b-2} up to constants, or can the simulation be improved (your pointer-tree numerics sit strictly below 2^{b-r})? Closing the two-round case up to constants, by a better construction or a better simulation, would make the robustness claim a theorem and would move me toward acceptance.

3. Precisely which statement here does not follow by a short reduction from (a) known adaptive versus non-adaptive simulations with bounded queries per sample in the huge-object model (Chakraborty et al. 2023; Adar–Fischer 2024), and (b) the χ²/Fisher-information lower bounds for a channel family taken as coordinate-subset channels? If the exact-constant estimation lower bound or the rounds bound needs an ingredient absent there, say which; a convincing answer raises originality, and an answer of "corollary" lowers it.

4. Beyond the knife-edge: is there a worst-case theorem when no single depth-b tree computes d (ensembles, where V_branch > ‖d‖²_∞ and both menus face a design problem), or when deg(d) > b and the criterion is MSE including the bias floor? Does 2^{b-1} remain attained there, and can theory explain the observed 1.5 (forms) and 1.09 (two rounds)? A positive answer would show the formulation reaches beyond "run the tree versus guess its path".

5. Is the supremum of V_fixed/V_branch at m = poly(b) equal to 2^{b-1} up to constants, and is there any improved upper bound over K_{m,b} for small m (e.g. m = 4, b = 3)? This is less decisive, but it would complete the "exact price" claim.

**Limitations**: Yes. Section 8 is candid about the scope (knife-edge cap, free labels, single known target, order effects, oracle constants, solver scale). I would add an explicit statement that the worst case requires about 2^{b-1} relevant features and product-like laws.

**Overall Recommendation**: 3 — Weak reject. This is a correct, thorough and honest paper with real merits, but the central theory is elementary for the venue, the gap-producing formulation is narrow, the robustness bounds are only partly tight, and the format makes the contribution hard to assess. It is borderline, and I could be argued to a 4.

**Confidence**: 4

**What would move me up one point**

- A convincing answer to Question 3, with the related-work section rewritten to say exactly what is new relative to huge-object and information-constrained results.
- One genuinely sharper theoretical result: either the (b, w, c) instance-dependent characterisation of Question 1, or the two-round gap settled up to constants (Question 2).
- A restructured main body: full statement and proof idea of the rounds lower bound and of Theorem 4(b), and a clear definition of what W(P) means (oracle design, local minimax, full support), with the density of experimental numbers in the abstract, introduction and Section 6 cut back.
- Removing or qualifying the unproved "accrues round by round" claim and the "exact price" wording for m below b-1+2^{b-1}.

The first and third items, with a credible partial result on the second, would bring me to 4. I do not see a realistic path to 5 within a rebuttal.
