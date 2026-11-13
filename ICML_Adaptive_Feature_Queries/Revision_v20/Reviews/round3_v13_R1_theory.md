# Round 3 — simulated review R1 (learning theory / TCS) of v13 (`Manuscript/paper.pdf`)

Overall Recommendation: **4 (Weak accept)** — Confidence 4 — Soundness 4 / Presentation 2 / Significance 3 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-09; not real ICML feedback. Full text as returned.)

**Summary**

The paper studies estimation of a known linear functional ∆(P) = E_P[Y d(X)] (e.g., the accuracy difference between two frozen classifiers, or the accuracy of a screening tree) when every sampled record reveals its label but only b of m binary features. It compares two protocol classes under a hard per-record cap: pre-committed "fixed forms" (the feature set is drawn before the record is seen) and "branching interviews" (depth-b decision trees that choose each question from earlier answers), with r-round batch protocols interpolating between them. The currency is the number of records, not queries. Main results: (1) for any finite menu of interviews the first-order minimax constant is an explicit convex program with a dual "witness" form, the converse holding against biased estimators, across-record adaptation and label-dependent interview choice, plus a finite-sample version tight within a universal factor 104; (2) fixed forms lose at most min{2^{b-1}, C(m-1,b-1)} relative to branching, sharp via an address (indexing) contrast, with a polynomial-dimension (m ≤ b²) construction losing almost the full exponent; (3) r rounds lose at most 2^{b-r}, pointer-chasing separates r from r+1 rounds, and a binary pointer-tree contrast gives V_r ≥ 2^{b-1}/(3b)^r, so bounded rounds lose almost the whole exponent and Ω(b/log b) rounds are necessary to be within poly(b) of branching; (4) at a fixed population the second-moment ratio is bracketed by 1/Γ_P (inverse explained energy of the best single form) and N_P (Rényi-1/2 effective number of path sets of the branching tree), and the branching constant over all depth-b trees is computed exactly by column generation with DP pricing; a two-phase self-calibrating design learns the population-optimal design without reference data while remaining exactly unbiased. Experiments on retrained random forests (m ≤ 12 median-binarized features, b ∈ {2,3,4}) and CART screening trees (BRFSS, thyroid; b ≤ 6) report realized record-count ratios between 1 and ~2, show the completion-only path-guessing baseline is 2–25× worse, and show that imputation from complete reference records closes the gap when the conditional law transports.

**Strengths**

- The question is natural and well posed, and the answer is clean: the sample cost of non-adaptivity under a per-record cap is characterized exactly (Theorem 1), with a sharp worst-case constant 2^{b-1} (Theorem 2). The lower bounds are stated against biased, sequentially adaptive and label-dependent procedures, which is the right generality.
- I checked the proofs of Theorems 1–4 and Propositions 5, 12, 14, 15, 16 in the appendix. The Sion/Fenchel dual (A3.1), the change-of-measure + χ²/KL chain-rule + Le Cam converse with the explicit constant (A3.2), the van Trees first-order argument (A3.3), the path-guessing simulation and the address-function energy bound r2^{s-2κ} ≤ 2^{-κ} (A6), and the Cauchy–Schwarz / optimized path-guessing bracket (A14) are all correct as written.
- Theorem 3(c) is the most interesting technical contribution: the potential M_t (2^L × the conditional probability of the most likely leaf) with the supermartingale inequality E[M_t | past] ≤ (1+2a_t)M_{t-1}, combined with the dual witness, gives a clean quantitative "variance cost of too few rounds" for the tree-evaluation instance. I verified Steps 1–5 line by line; the argument is correct and the resulting exponent b − O(r log b) is near-tight for constant r.
- The population-specific bracket has interpretable endpoints (Rényi-1/2 path entropy; best single form's explained energy) and is computable before any collection; the lower end is shown to predict realized gains (Spearman 0.78 on screening runs, never exceeding the realized ratio).
- Column generation with an exact O(m b 2^b) DP pricing step and certified bounds over all ~1.5×10^7 depth-3 trees on 12 features is a nice piece of methodology; the certificate (any dual witness yields a valid lower bound on M_branch via Theorem 4(a)) is correct.
- The experimental section is unusually honest: it reports negative results (thyroid gain exactly 1, predicted in advance by Γ_P = 1; imputation closes the gap when a trusted complete reference exists; order-effect biases comparable to the gains), sensitivity analyses over smoothing mass and bootstrap resamples, and Monte Carlo confirmation of the computed variance ratios (I re-derived several Table 3/5/6 entries from the reported accuracies and they are internally consistent).

**Weaknesses**

1. [major] Much of the theory is a direct application of standard tools and classical constructions. Theorem 1 is linear-functional minimax duality (Donoho; Juditsky–Nemirovski; Polyanskiy–Wu) specialized to a finite channel menu, as the authors acknowledge. Theorem 2 is the classical adaptive-vs-non-adaptive decision-tree separation (simulate a depth-b tree by guessing one of its ≤ 2^{b-1} paths; the addressing function is tight) re-expressed as a variance inflation; both directions are short. Theorem 4 is Cauchy–Schwarz plus optimized importance weights. The genuinely new technical content is concentrated in Theorem 3(c) and the exact computational machinery.

2. [major] Missing related work on the closest conceptual precedent: within-record ("fully interactive") vs across-record ("sequentially interactive") protocols in local differential privacy (Joseph, Mao, Neel, Roth, FOCS 2019; Joseph, Mao, Roth, SODA 2020), where exponential separations between interactivity classes are proved with pointer-chasing-type constructions and sample complexity is the currency, and the interactive/non-interactive comparisons in information-constrained inference (Acharya, Canonne, Liu, Sun, Tyagi; Duchi–Jordan–Wainwright). The paper's framing (within-record adaptivity paid in records, across-record adaptation does not help the constant) is a noiseless, exact-constant analogue of that line, and this should be discussed. Budgeted learning with adaptive vs non-adaptive feature acquisition (Lizotte–Madani–Greiner and follow-ups) is also absent.

3. [major] Presentation. The 8-page main text is a compressed index into a 40-page appendix with 30 sections. Results are referred to by number only (Theorems 6, 7, 11, 18, 20, 22; Propositions 8, 9, 12, 14, 15, 24, 26; Corollaries 10, 17, 19, 21, 23), the numbering interleaves main-text and appendix objects, and the appendix repeatedly refers to experiments that do not exist in the paper ("the ten binary tasks" in A26, "the eight-feature experiment" in A9.2, "70 binary tasks", "the larger-tree experiment", a SUSHI loader in A30). Key quantities (V, W, M, Γ_P, N_P, K_{m,b}) are introduced in dense paragraphs with little intuition or a worked example. A typical ICML reader cannot verify the main claims from the main text.

4. [major] Practical significance for ML is modest and the experimental regime is small. All exact computations use m ≤ 12 median-binarized features and b ≤ 6 (Table 2 has cells left incomplete at b = 4, m ≥ 9 after ~49 min/task); realized gains are 1.0–1.85× (forests) and 1.0–1.98× (screening); the paper itself shows that model-assisted imputation from complete source records attains RMSE 0.89–1.00 of branching, and that a 10% last-answer flip rate biases both designs by 0.5–1.8 standard errors—comparable to the gains. The exact programs scale as C(m,b)2^b and m^b 2^b, so the methodology does not obviously extend to typical feature counts.

5. [minor] The round-hierarchy lower bound (Theorem 3(c)) is informative only for b ≥ 10, while all experiments are at b ≤ 6 where only a 4/3 separation between two rounds and branching is known (Corollary 17). The abstract's "tight up to polynomial factors in b" is accurate only for constant r (the gap between 2^{b-1}/(3b)^r and 2^{b-r} is (3b)^r 2^{r-1}, not polynomial when r grows).

6. [minor] The headline "pre-committed forms need at most 2^{b-1} times as many records" compares worst-case constants taken separately over populations (acknowledged in Section 4), and on the variance scale at a fixed population the ratio W_fixed/W_branch can exceed K_{m,b} when ∆ ≠ 0 (Corollary 23). The abstract and introduction should carry this qualification.

7. [minor] The local-asymptotic-minimax interpretation of W_A(P) (Proposition 15) requires full support, which the experiments enforce by mixing 1% uniform mass over all 2^m profiles and both labels—an artificial population. The sensitivity analysis (≤ 5.3% change for masses 0.1–10%) mitigates but does not remove the concern that the reported constants are properties of a smoothed law.

8. [minor] The finite-sample constant 104 is very loose and the exact finite-n minimax ratio even for the address instance is left open; the exact first-order constant of the biased (non-identifiable) regime is also open. These are acknowledged.

9. [minor] Labels are assumed observed and charged separately for every record; in the screening applications the label (diagnosis) is often the expensive part, which changes the economics (A25 discusses this only briefly).

**Soundness** (4): I verified the core proofs (Theorems 1–4, Propositions 5, 12, 14, 15, 16) and found them correct; experiments are internally consistent and come with certificates and sensitivity analyses; the only issues are a few overstated phrasings in the abstract.

**Presentation** (2): The prose is precise, but the main text is an over-compressed index into a 40-page appendix with confusing cross-numbering and dangling references to experiments absent from the paper.

**Significance** (3): A clean, exact treatment of a natural question in information-constrained estimation with a new round hierarchy; the direct impact on ML practice is limited by modest realized gains, toy-scale exact computations, and the demonstrated fragility to order effects.

**Originality** (3): The problem formulation (within-record adaptivity priced in records under a hard cap), the exact-constant comparison, the potential-function round bound and the Rényi-entropy bracket are new; the constructions (address, pointer chasing, tree evaluation) and most tools are classical, and a closely related interactivity literature in LDP is not acknowledged.

**Key Questions for Authors**

1. How does your framework relate to the sequential-vs-full interactivity separations in local differential privacy (Joseph–Mao–Neel–Roth 2019; Joseph–Mao–Roth 2020) and to interactive inference under information constraints (Acharya et al.)? In particular, is your pointer-chasing round separation a noiseless specialization of theirs, or does the exact-constant/variance framing give something those results cannot? A convincing differentiation would raise my originality assessment; if the separations are essentially known in that setting, it would lower it.

2. Theorem 3(c) bites only for b ≥ 10, while your experiments live at b ≤ 6. Can you compute V_2(B_L, b) and V_r exactly (your programs are small for m = 2^b − 1 at b = 3, 4, 5) to show how large the two-round loss actually is in the experimental regime? Evidence that few rounds already lose a substantial factor at small b would strengthen the link between theory and experiments and move me up.

3. Does the methodology scale beyond m = 12? Can Γ_P and N_P (or restricted-master column generation with certificates) be computed for m = 30–100 features with b ≤ 6, and how loose is the bracket there? Even one realistic-dimension demonstration would materially raise the significance.

4. Given that the position-effect model in A26 produces biases of 0.5–1.8 standard errors at n = 1000—comparable to the 1–2× sampling gains—what design (e.g., randomized question order with anchors) would preserve the branching gain while controlling order effects, and does Theorem 1 extend to such kernels? A credible answer would change my view of the practical relevance; a negative answer would reinforce weakness 4.

5. The appendix refers to "the ten binary tasks", "the eight-feature experiment", "70 binary tasks" and a SUSHI dataset that appear nowhere in the main text. Which results in the paper depend on them, and will the final version be self-contained? (This affects my presentation score only.)

**Limitations**

Yes. Section 8 and the Impact Statement discuss the single-estimand restriction, order/mode effects, identification floors for nonlinear models, dependence on the target law, imputation closing the gap when complete references exist, and computational scaling. Two suggestions: state explicitly in the abstract/introduction that the realized gains (1–2×) are of the same order as plausible order-effect biases, and that the worst-case 2^{b-1} statement compares worst cases taken separately.

**Overall Recommendation** 4: Weak accept

**Confidence** 4

**What would move you up one point**

- A restructured main text that is self-contained for the four theorems (consistent numbering, a two-paragraph worked example of V, W, Γ_P, N_P on a small tree, and removal of appendix references to experiments not in the paper).
- Closing the polynomial gap in Theorem 3 (or exact numerics for V_2 on the binary pointer tree at b = 3–6) so the round hierarchy is informative in the regime where the experiments live.
- A proper discussion of the LDP interactivity literature with a precise statement of what is new relative to it.
- At least one experiment at realistic feature counts (m ≥ 30) showing the bracket and fitted designs remain computable and predictive.
- Evidence that the branching gain survives a realistic order-effect model, or a design that provably controls it.
