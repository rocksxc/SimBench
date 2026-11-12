# Round 5 — simulated review R1 (learning theory) of v15 (`Manuscript/paper.pdf`)

Overall Recommendation: **4 (Weak accept; the reviewer calls it borderline, on the accept side)** — Confidence 4 — Soundness 3 / Presentation 3 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-12; not real ICML feedback. Full text as returned.)

**Summary** (in my own words, not the abstract)

The paper studies estimation of a known linear functional Δ(P) = E[Y d(X)] of a population on {−1,1}^m × {−1,1} (e.g. the accuracy difference of two frozen rules) when each sampled record reveals its label for free but at most b of its m features. Three classes of per-record query protocols are compared: fixed forms (the b coordinates are chosen before the record is seen, possibly at random), r-round interviews (r adaptive batches), and branching interviews (depth-b decision trees). The currency is the number of records needed, i.e. ratios of first-order minimax MSE constants.

The main results are:

- **Theorem 1.** For any finite menu of interviews, n × (minimax MSE) converges to the value V of a finite convex program, with a dual of the form "signal² / largest projection energy any single interview captures". The converse covers biased estimators, across-record adaptivity and label-dependent interview choice. A non-asymptotic version holds up to a factor 104.
- **Theorem 2.** V_fixed ≤ K_{m,b} · V_branch with K_{m,b} = min{2^{b−1}, C(m−1, b−1)}, and the same inequality for the population-specific (local-minimax) constants W(P) at every P. The address (indexing) function attains 2^{b−1}, and products of address blocks give 2^{b−O(b/log b)} with m ≤ b².
- **Theorem 3.** r rounds lose at most 2^{b−r}. A binary pointer tree loses at least 2^{b−1}/(1+2b/r)^r in r rounds, and its products give the same exponent up to o(b) in polynomial dimension. Hence a protocol that is polynomially competitive on every target needs at least about 0.37b rounds.
- **Theorem 4.** At a fixed P the ratio is bracketed by 1/ρ²_P (a population R² of the best single form) and a Rényi-1/2 effective number of tree paths.
- **Computation and experiments.** A column-generation solver with dynamic-programming pricing computes certified optimal designs for each class. On small trained trees and forests (m ≤ 12, or 21 for forms; b ≤ 6) the realized fixed-versus-branching ratios are 1.0–1.98, far below the worst case, and one adaptive round recovers most of the gap.

I checked in detail: Appendix B.3 (duality, finite-sample converse, van Trees), C.1 (simulation), C.1.3 and C.4.1 (address function and products), D.1 (round upper bound, pointer chasing, the binary-pointer-tree potential argument and Corollary D.4), E.1 (Theorem E.1) and the pricing recursion in E.3. I only skimmed Appendices F–H.

**Strengths**

1. **A clean, well-posed question with exact answers.** "How many more records does pre-commitment cost under a hard per-record cap?" is given a first-order minimax characterization, not an up-to-constants one. Fixed forms are allowed to be randomized per record, and the lower bounds allow sequential choice of forms and label-dependent forms, so the comparison is not rigged against the non-adaptive class.

2. **The core proofs appear correct.** I re-derived the following and found no error:
   - the Fenchel/Sion dual (B.2)–(B.3);
   - the two-point converse (the constant works out to about 1/103.4, consistent with the stated 104);
   - the van Trees limit;
   - the path-guessing simulation (pointwise second moment inflated by exactly L_τ ≤ K_{m,b});
   - the centered variant used for Theorem 2(ii);
   - the address-function energy ‖E[d | X_T]‖² = r·2^{s−2κ} ≤ 2^{−κ};
   - the product bound in Proposition C.4;
   - the hit argument for N_{r,κ};
   - the potential inequality E[Q_t | T_{t−1}] ≤ (1 + 2a_t + λ_t) Q_{t−1} for the binary pointer tree, its multiplicativity across blocks, and the AM–GM step;
   - the constant α* ≈ 0.376 and the arithmetic of the polynomial-dimension corollary.

3. **Tightness is taken seriously.** The 2^{b−1} factor is attained exactly, and there is a polynomial-dimension version. The mean-budget variant (Proposition C.6) usefully shows that the exponential gap is specific to the hard cap, collapsing to m/b under an expected budget. A (4,3) example with exact value (7+2√2)/4 shows the authors probed the small-(m,b) frontier honestly.

4. **The round hierarchy has some technical content.** The potential Q = M + 2^L·π is designed to be multiplicative across blocks under adaptive splitting of queries, which is what makes the polynomial-dimension statement go through. This is the most original argument in the paper.

5. **The experiments are honest about practical magnitude.** The paper reports that optimized fixed designs lose only 1.0–1.98×, that design optimization matters more than adaptivity, and that model-based competitors can win. Reported constants carry primal/dual certificates. Section 8 is candid about what is not covered.

6. **Statements are precise.** Table 1 and Figure 2 make a very dense paper navigable for an expert.

**Weaknesses** (numbered; [major] or [minor])

1. **[major] Limited technical depth of the headline results.**
   - Theorem 1 is, as the authors say themselves, an assembly of standard tools: c-optimal design, Sion plus Fenchel duality, and a Fisher-information bound uniform over a channel family in the style of Acharya–Canonne–Tyagi and Barnes–Han–Özgür.
   - Theorem 2's upper bound is "guess the path"; it rests on the observation that a depth-b tree has at most 2^{b−1} distinct path query sets. Its lower bound is the textbook indexing function with a three-line Fourier computation.
   - Theorem 4 is a single Cauchy–Schwarz inequality plus the same simulation with optimized probabilities.
   - Qualitatively, "within-sample adaptivity is worth exponentially much, witnessed by indexing or pointer chasing" is folklore in query complexity. It is already present in the huge-object testing literature the paper cites (Adar–Fischer's locally bounded adaptivity is adaptivity within a sample) and in the round-separation results for local differential privacy.
   - What is new is the translation into exact variance constants. That is a real but modest increment; only Theorem 3(c)–(d) required a new argument.

2. **[major] The round hierarchy is not tight, and the gap is wider than the main text suggests.**
   - Upper exponent b − r versus lower exponent b − 1 − r·log₂(1+2b/r). The lower bound is vacuous for r ≳ 0.37b.
   - In the range 0.37b < r < b the only evidence of any separation is numerical: 1.80 at b ∈ {3,4} and 4/3 at (4,3).
   - "Linear in b rounds are needed" is therefore proved with constant 0.37, while the upper bound only shows b − O(log b) rounds suffice. Whether r = b − ω(log b) rounds can be polynomially competitive is open.
   - The paper's own numerics (3.32 versus 4, 1.80 versus 2) suggest the truth for B_{b−1} at zero slack is close to 2^{b−r}. If so, the (1+2b/r)^r loss is an artifact of a potential that ignores that the cap equals the tree depth.

3. **[major] The formulation is narrow relative to the title and framing.**
   - The target is one known functional of Fourier degree at most b, with free and always-observed labels and order-independent, noiseless answers.
   - When a single depth-b tree computes d, "branching" is just running the classifier on each record, and the question becomes how much is lost by not being allowed to do so. For ensembles the cap itself costs more than pre-commitment, as the paper notes.
   - In the regime where the method is computable (b ≤ 6, m ≤ 21) the worst-case factor is a constant of at most 32, and the observed factor is at most 2. The asymptotics in b are of mainly theoretical interest, since identification already needs C(m,b)·2^b cell masses.
   - The extremal populations are uniform product laws with pure-noise labels (Δ = 0). The paper does not show that the exponential gap survives at populations where the rule is actually accurate, although Theorem 4 appears strong enough to do so (see Question 1).

4. **[minor] "Sharp" is overstated for K_{m,b}.** The bound is shown tight only when m ≥ b − 1 + 2^{b−1}. The C(m−1, b−1) branch is never shown to be attained; at (4,3) the truth lies in [2.457, 3]. In polynomial dimension the lower bound is 2^{b−O(b/log b)}. Table 1 calls K_{m,b} "the sharp gap" without this qualification.

5. **[minor] Theorem 2(ii) and the W-ratios compare oracle designs.** The centered simulation uses c = Δ(P), the estimand itself. Attainability without knowing P rests on Proposition 5, which is purely asymptotic. The pilot experiments show 19–30% excess at b = 5–6 with realistic pilots. A finite-n comparison statement for deployable fixed designs is missing.

6. **[minor] Asymptotic regime.** n·R → V requires n ≫ 2^b (for example n ≥ 60·2^{b−1} for the address function). Below that, the paper only has the factor-104 sandwich. The first-order constant in the non-identifiable (biased) regime is left open.

7. **[minor] Presentation density.**
   - The 8-page body is a compressed digest of a roughly 45-page appendix. The proofs of all four theorems are sketched in a few lines each.
   - The appendix contains many side results that dilute the message: C.2, C.3, C.5, C.7, G and H.
   - Theorem 3(b) is dominated by (c) and could give its space to a fuller proof of (c).
   - Notation is overloaded: r is rounds, the number of data bits in a form, and a block index; R is both a round count and a set; K_r versus K_{m,b}.

8. **[minor] Positioning.** The relation to restricted-focus-of-attention learning (which is exactly the fixed-form model) and to Adar–Fischer's adaptivity taxonomy is one sentence each. A precise statement of what does and does not follow from those works is needed to substantiate the novelty claim. I could not verify several cited 2026 preprints (e.g. the round lower bound for tree evaluation); nothing in the proofs depends on them.

9. **[minor] Computational scale.** Adaptive classes were solved only for m ≤ 12. Four of the b = 6 two-round runs and the b = 5 pointer tree did not close. "Certifies optimal designs of every protocol class" should be read with these disclosed limits.

**Soundness**: 3 — the main theorems and the proofs I checked (B.3, C.1, C.4.1, D.1, E.1) are correct; the reservations concern loose or overstated tightness claims, not errors.

**Presentation**: 3 — statements are precise and the structure is clear, but the body is over-compressed and the appendix sprawls; a non-expert would struggle.

**Significance**: 2 — correct and clean, but the worst-case results formalize largely expected phenomena in a narrow model, and the empirical value of adaptivity turns out small (at most 2×).

**Originality**: 3 — the records-ratio framing with exact constants and the pointer-tree potential argument are new; the remaining ingredients are standard and acknowledged as such.

**Key Questions for Authors**

1. **Do the extremal gaps survive at accurate populations?** Take the address contrast with X uniform and Y = d(X) with probability p > 1/2, so Δ ≠ 0. What are ρ²_P and W_fixed/W_branch? A quick calculation with Theorem 4 suggests the ratio stays Θ(2^{b−1}), because a form learns t − Δ only when it happens to contain the addressed bit. If you can state this (ideally "for every Δ ∈ (−1,1) there is P with ratio ≥ c·2^{b−1}"), the "labels independent of features" caveat disappears and my Significance score would rise. If the gap degrades with accuracy, that is important to know and would lower it.

2. **Round hierarchy tightness.**
   - (a) For B_{b−1} at zero slack (cap equal to depth), can you prove V_r = Θ(2^{b−r}), or at least 2^{b−r}/poly(b), as the b ≤ 4 numerics suggest?
   - (b) Conversely, with slack (cap b > β), is there an r-round upper bound showing the (1+2b/r)^r factor is real for the pointer tree?
   - (c) Is there any provable separation V_{b−1}/V_b ≥ c > 1 for all b?
   
   A matching bound, or a proof that r = b − O(log b) rounds are necessary for polynomial competitiveness, would move Theorem 3 from "partial" to "sharp" and would raise my overall score.

3. **Relation to known separations.** Which of your separations can be derived, even up to constants, from the address and pointer-chasing separations in Adar–Fischer's locally bounded model, Joseph et al., or the RFA literature, and which cannot? If the answer is "the qualitative separations are known; the exact constants and the estimation setting are new", please say so explicitly. If there is a real obstacle to transferring them, explaining it would strengthen Originality.

4. **Intermediate (m, b).** Is C(m−1, b−1) ever attained, or even approached, for b < m < b − 1 + 2^{b−1}? Is there any improvement on the trivial upper bound at (4,3), or a conjecture for sup V_fixed/V_branch as a function of m/b? A sharper frontier would justify the word "sharp" in the regime relevant to practice (m = O(b) to b²).

5. **Deployable version of Theorem 2(ii).** Can you give a non-asymptotic statement, for example a fixed-form two-phase procedure with n records whose MSE is at most K_{m,b}·(1 + ε_n) times the local-minimax branching risk with explicit ε_n? As it stands, the "at every population" claim is about oracle constants. An explicit rate would resolve Weakness 5.

**Limitations**

Yes. Section 8 is unusually forthright: single known functional, design-based guarantees only, order effects, free labels, identification floors, extremal populations with noise labels, solver scaling, and open problems. I would add two things to the main text: (i) K_{m,b} is tight only for exponentially large m; (ii) the W-comparisons are between oracle designs.

**Overall Recommendation**: 4 — Weak accept

The paper is technically solid, complete and honest, and I found no errors in the central proofs. The reservation is depth: the headline theorem is an elegant but elementary formalization, and the one technically new piece (rounds) is not tight. I regard this as borderline; it sits on the accept side because of correctness, exactness of constants, and the unusually careful empirical calibration of what the theory means in practice.

**Confidence**: 4 — I verified the main proofs line by line within my expertise; I did not check the experimental appendices or the code, and could not verify a few 2026 citations.

**What would move you up one point**

- A tight, or tight up to poly(b), r-round result: either sup_d V_r/V_branch = 2^{b−r}/poly(b) for all r, or a proof that polynomial competitiveness needs b − O(log b) rounds. This is the single most convincing upgrade.
- A statement that the exponential gap holds at populations with non-trivial accuracy (Question 1). This is probably easy from Theorem 4 and removes the main naturalness objection.
- A precise comparison with locally bounded adaptivity in the huge-object model and with RFA, making clear what is new beyond constants.
- Either a sharper frontier for moderate m (is C(m−1, b−1) ever relevant?) or toning down "sharp" accordingly.
- Restructuring: move a real proof of Theorem 3(c) into the body, drop Theorem 3(b) and peripheral appendix material.

Realistically, the first two items together would move me to 5; the others alone would not.
