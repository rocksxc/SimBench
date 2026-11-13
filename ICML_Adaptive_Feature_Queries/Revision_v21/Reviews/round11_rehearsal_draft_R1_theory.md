# Round 11 — DRESS REHEARSAL (not the official round): mock review R1 (theory) of a v21 draft (md5 b6b19eb2038a44dff14c2c51557ca34a, not the packaged PDF)

Overall Recommendation: **3 (Weak reject, borderline)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Mock review by an independent language-model reviewer agent on 2026-11-13, used to revise the draft before the single official round; not real ICML feedback. Full text as returned.)

**Summary** (in my own words, not the abstract)

The paper studies estimation of a known linear functional Δ(P) = E_P[Y d(X)], where d has Fourier degree at most b on {−1,1}^m. Each of n records reveals at most b coordinates, and the label is free. Three protocol classes are compared: fixed forms (a b-subset chosen before the record is seen, possibly randomized and adapted across records), r-round interviews, and fully branching depth-b decision trees.

- **Theorem 1.** A rejection-sampling "path guessing" argument reproduces any protocol on n branching records, in law, from a geometric number of fixed-form records with mean K_{m,b}·n, where K_{m,b} = min{2^{b−1}, C(m−1,b−1)}. The addressing (index) function on b−1+2^{b−1} coordinates shows 2^{b−1} is attained, both for the first-order minimax constant V and for the population constant W at uniform profiles. Products give 2^{b−O(b/log b)} with m ≤ b².
- **Theorem 2.** For r rounds the simulation gives 2^{b−r}; a binary pointer tree gives the lower bound 2^{b−1}/(1+2b/r)^r via a supermartingale potential. With c extra pre-committed questions the worst-case price lies between 2^{b−1}/(c+1) and 2^{b+1}/(c+3).
- **Theorem 3.** V and W are characterized as convex programs with dual sup_h ⟨d,h⟩² / max_ι ‖E[h | transcript_ι]‖², using c-optimal-design duality and van Trees. A column-generation solver with dynamic-programming pricing computes them.
- **Theorem 4.** Inside parametric models the simulation bound persists. Under features independent given the label the gap is at most 2 (and 1 with label-dependent designs). A strongly coupled pairwise log-linear law recovers a gap of 2^{b−1}/b.
- **Experiments.** Oracle constants for CART screening trees (b ≤ 6, m ≤ 12–13 for exact optima) give ratios of 1.0–2.4. One extra question or one extra round removes most of the gap.

I checked the following in detail and found no errors:
- Theorem 1 with Appendix C.1 (C.1.1–C.1.4).
- Theorem C.2(a,b) on extra questions.
- The duality and converse in B.3.1–B.3.3, including the constant 104.
- Theorem D.1(a,b) and the potential argument of Theorem D.3 (Steps 1–5).
- Theorem E.1 and Proposition E.3.
- Theorem E.5(a), (b) and (e).
- Proposition C.9.

I did not verify E.5(c,d), the certificates of C.8, C.5–C.6 beyond a read, or any experimental numbers.

**Strengths**

- The question is clean and the headline answer is complete. Theorem 1(i) is a comparison of experiments, so it covers every estimator, loss and model at once, and it is matched by a lower bound for the simplest task, one linear functional, with the exact constant 2^{b−1} rather than Θ(2^b).
- The proofs I checked are correct and carefully stated. The lower bounds hold against biased estimators, across-record adaptivity and label-dependent interview choice.
- The potential argument for the binary pointer tree (Theorem D.3) is the technically interesting part. The potential Q = M + 2^L·π is well chosen, tensorizes across blocks, and gives 2^{b−O(r log b)} for constant r.
- The extra-question result is tight up to a factor below 4, and exactly tight for c ∈ {0,1}.
- Theorem 4(b) is a nice structural observation: under conditional independence a design matters only through inclusion probabilities, and the factor 2 comes from label-blindness.
- The paper is unusually candid. Open problems are stated, the mean-budget collapse to m/b is proved (C.6.1), and the experiments show the worst case is far from typical.
- Computed constants carry primal and dual certificates.

**Weaknesses**

1. **[major] The headline theorem is technically shallow relative to known results.** The upper bound is the folklore "guess the root-to-leaf path" conversion with an acceptance step, as the paper itself says in Section 7. It is the same rejection-sampling device used to convert fully interactive into sequentially interactive locally private protocols. The lower bound is the addressing function plus a three-line conditional-energy computation, fed into a standard χ²/van Trees dual. In Boolean-analysis terms the content is that any depth-b tree has a b-subset carrying at least 2^{−(b−1)} of the relevant energy (trivially, the most likely path set), and that addressing is extremal. The only new element is the exact constant. Theorem 3 is, by the authors' own account, Elfving-type duality plus standard information bounds. For a paper whose main selling point is theory, the depth of the core result is below what I expect at ICML; the harder material (Theorem D.3) is relegated to the appendix.

2. **[major] The tightness claims are narrower than the abstract and introduction suggest.**
   - Rounds: only the upper bound 2^{b−r} is general. The lower bound is smaller by a factor (1+2b/r)^r / 2^{r−1}, and is vacuous for r = 2 unless b ≥ 8. The paper's own numerics (1.80 against a bound of 2 at b=3, r=2; 3.32 against 4 at b=4) suggest 2^{b−r} may not be attained by this family. "r rounds of adaptivity lower the bound only to 2^{b−r}" reads as a sharp statement and is not one.
   - Polynomial dimension: the rounds result only covers r = o(log b / log log b).
   - Small m: the C(m−1,b−1) branch of K_{m,b} is never shown sharp. At (m,b) = (4,3) the paper only brackets the answer in [2.457, 3]. Exact sharpness needs m exponential in b; for m = O(b) only 2^{(1−ζ)b} is shown.

3. **[major] The phenomenon rests on a knife-edge formulation, which limits significance.** The gap needs all of the following: one known target fixed before collection; a hard per-record cap equal to the rule's depth; and wide rules (the extremal example depends on 2^{b−1}−1 items beyond its depth).
   - Under a mean budget the ratio is at most m/b (C.6.1).
   - In the paper's own experiments one extra question removes most of the gap.
   - Records collected by branching for one rule are "nearly useless for another" (F.6), whereas uniform b-way forms identify every degree-b contrast simultaneously.
   - For a single tree the adaptive optimum is simply "run the rule and average", so the comparison is exact evaluation against inverse-probability-style estimation from partial views.
   
   There is no result for a class of targets, for an unknown or data-dependent rule, or for the hybrid budget beyond the address family. Combined with empirical ratios of 1.0–2.4 at b ≤ 6, the theoretical 2^{b−1} carries little weight for ML practice.

4. **[major] Presentation and venue fit.** The submission is 67 pages with roughly 40 numbered statements. The eight-page body is a dense catalogue. Theorem 1 is stated using constants V and W defined two sections later. Theorems 2–4 pack several claims each, with one-sentence proof pointers. The only non-routine proof is not sketched in enough detail to follow without Appendix D. A reviewer cannot verify the whole appendix in a conference cycle. The paper would be easier to assess if the body concentrated on Theorems 1–2 with a real proof of D.3 and the rest moved to a journal version.

5. **[minor] "Exactly, for every sample size" needs qualification.** The simulation uses a random (geometric) number of records. With a fixed budget one gets a Binomial number of accepted records, and the fixed-n comparison is only first-order. The general finite-sample bracket has a factor 10⁴, though Proposition C.3 handles the address family for n ≥ 60·2^{b−1}.

6. **[minor] W is an oracle local constant.** Designs and the centering constant c = Δ(P) are tuned to P. This is fine as a local asymptotic minimax statement (Proposition C.9), but "records needed at a population" should be read that way. Experiments are oracle computations at smoothed empirical laws.

7. **[minor] Theorem 4(c) is the index lower bound in disguise.** It adds 2^b auxiliary features that deterministically encode one-hot(address) and its products with the data bits, so d becomes linear in features of which a form sees only b out of 2^{b−1}. It shows that interaction order is coding-dependent, but it says little about realistic pairwise models.

8. **[minor] Related work.** Identification by Fourier degree ≤ k under k-restricted focus of attention is, to my recollection, known in the RFA literature that followed Ben-David and Dichterman, and should be credited. Without web access I could not confirm some 2026 citations (for example Li et al., 2026) or how they relate.

9. **[minor] Scale of computation.** Adaptive optima are computed only for m ≤ 12 (m = 20 at b = 3). The empirical conclusions are therefore about very small instances.

**Soundness**: 3 — Every proof I checked is correct and the lower bounds are stated against the right class of procedures; I could not verify the full 55-page appendix, and a few headline phrasings are stronger than the theorems.

**Presentation**: 2 — Precise but severely over-compressed; key objects are used before they are defined and the non-trivial proof is not followable from the body.

**Significance**: 2 — A complete answer to a narrow, knife-edge question whose worst case the paper itself shows is fragile (mean budgets, extra questions, trained rules).

**Originality**: 3 — The framing (pricing within-record adaptivity in records, with exact constants and a model-based counterpart) is new; the core techniques are folklore or standard, and Theorem D.3 is the main original argument.

**Key Questions for Authors**

1. What in Theorem 1 goes beyond the folklore path-guessing conversion plus the addressing function? Can you show sharpness of the C(m−1,b−1) branch, or determine the supremum for m = O(b) (even m = b+1)? A new ingredient or a sharp (m,b) frontier would raise my originality and significance scores.

2. Is sup_d V_r/V_branch equal to 2^{b−r}, or strictly smaller, as your b = 3, 4 numerics hint? Can the factor (1+2b/r)^r be removed, or can you exhibit any contrast with V_2/V_branch = 2 at b = 3? Closing this, or proving the upper bound is not tight, would make Theorem 2 a real hierarchy theorem and would move me up.

3. What is the price for a class of targets (simultaneous estimation over a family of depth-b rules, or a rule chosen after collection)? Branching can never be worse, but I expect the gap to shrink sharply. A theorem showing it persists would strengthen significance; if it collapses, the headline should be reframed as a single-target statement.

4. For general contrasts, what is the worst-case ratio under the hybrid constraint (mean budget b, hard cap B)? You solve only the address family. If the answer is about m/b once B is moderately larger than b, is the hard-cap theorem the right headline? A general hybrid theorem would address weakness 3.

5. Can the polynomial-dimension rounds bound be extended beyond r = o(log b / log log b), or is there an obstacle, given that your product construction is exactly evaluable in log b rounds? Either answer would clarify how much of Theorem 2(b) is intrinsic.

**Limitations**

Yes. Section 8 is candid about the knife-edge cap, the single known target, free labels, the oracle nature of W, the 10⁴ factor and the computational limits. I would add two explicit statements to the body: that the r-round bounds are not matching, and that sharpness of K_{m,b} holds only for m ≥ b−1+2^{b−1}.

**Overall Recommendation**: 3 — Weak reject. This is borderline: the paper is technically solid, but the core theorem is elementary, the tightness is partial, and the significance is limited by the paper's own findings.

**Confidence**: 4

**What would move you up one point**

- Rewrite the abstract and introduction so that tightness claims match the theorems (rounds, small m), and position Theorem 1 explicitly as the folklore conversion made exact.
- Restructure the body around Theorems 1–2 with a real proof sketch of the pointer-tree potential argument; define V and W before using them; cut or defer the modelling and solver material.
- Add at least one substantive result: (a) a matching or provably non-matching r-round bound; (b) the sharp frontier in m for fixed forms; or (c) a theorem for a family of targets or the general hybrid budget, showing the gap is not an artefact of single target plus hard cap.

The first two are achievable in a revision and, with a convincing answer to Questions 1 and 3, would move me to 4. Item (c) or a tight round hierarchy would be new research. Nothing realistic within a rebuttal would take this to 5.
