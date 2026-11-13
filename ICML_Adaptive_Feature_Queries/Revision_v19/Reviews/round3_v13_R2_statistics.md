# Round 3 — simulated review R2 (missing data / survey statistics) of v13 (`Manuscript/paper.pdf`)

Overall Recommendation: **4 (Weak accept)** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 3 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-09; not real ICML feedback. Full text as returned.)

**Summary**

The paper studies estimation of a population functional Δ(P) = E[Y d(X)] (the accuracy difference of two frozen prediction rules, or more generally a fixed low-degree contrast) when every sampled record may reveal at most b of m finite-valued features but the label is always observed. It compares classes of acquisition protocols: pre-committed fixed forms (planned missingness / matrix sampling), r-round interviews, and fully branching depth-b interviews (decision-tree paths). Theorem 1 gives the exact first-order minimax constant for any finite menu as a convex program with a dual witness formula, with a converse valid for biased estimators, across-record adaptation, and label-dependent interview choice, plus a finite-sample version within a universal factor. Theorem 2 shows the worst-case fixed/branching ratio is exactly min{2^{b-1}, C(m-1,b-1)}, attained by an "address" contrast, with 2^{b-O(b/log b)} already in dimension m ≤ b². Theorem 3 gives a round hierarchy: r rounds lose at most 2^{b-r}, and a binary pointer-tree contrast shows at least 2^{b-1}/(3b)^r via a supermartingale/potential argument. Theorem 4 brackets the population-specific ratio M_fixed/M_branch between 1/Γ_P (inverse explained energy of the best single form) and the Rényi-1/2 effective number of path sets of the branching tree; column generation with a DP pricing step computes the branching constant exactly over all depth-b trees; Proposition 5 shows a two-phase design learns the optimal population design while staying exactly unbiased. Experiments on independently retrained depth-b forests (WDBC, Spambase, Ionosphere) and CART screening trees (BRFSS diabetes, thyroid) find realized gains of 1.0–2.0x, show that completion-only path guessing is 2–25x worse than optimized form scores, that branching restricted to the models' own trees misses most of the gain, and that multiple imputation from complete source records matches branching when the conditional law transports. A PISA 2012 rotated-form analysis demonstrates identification from real fixed forms.

**Strengths**

- A clean, well-posed question that, to my knowledge, has not been answered in the planned-missingness or two-phase sampling literature: the sharp price (in records, not queries) of pre-committing the measurement set versus within-record branching under a hard per-record cap.
- The theory is correct and complete as far as I checked. The duality (A3.1), the finite-sample converse via change of measure + KL chain rule including label-dependent interview selection (A3.2), the local van Trees argument for the exact constant (A3.3), both directions of Theorem 2 (padded path-set simulation and the address projection-energy calculation, eq. 6), the potential inequality (19) and its supermartingale combination in Theorem 20(c), the Cauchy–Schwarz/importance-sampling bracket of Theorem 22 and its variance-scale transfer (Cor. 23), and Propositions 15 and 24 all hold up. The 2^{b-1} constant is sharp, and the Fourier-degree identification criterion is the right one.
- Theorem 3(c) is the most original piece: a nearly tight round hierarchy in a statistical (variance) rather than worst-case-query sense, connecting to tree evaluation/pointer chasing, with a neat potential argument.
- The fixed-form design program (7)/(20) is correctly positioned as the optimal AIPW augmentation under known coarsening (Robins–Rotnitzky–Zhao; Tsiatis) jointly optimized with the form probabilities, with pointwise unbiasedness that survives calibration error. Proposition 26 correctly characterizes the full unbiased score space as pairwise shared-coordinate control variates.
- The experimental methodology is statistically careful: certified primal/dual bounds, sensitivity of the "exact ratios" to the smoothing mass (0.1%–10%) and to bootstrap resampling of the evaluation records, oracle vs. fitted designs, proper MI with Rubin's rules, a survey-weighted PISA analysis with Fay BRR replicates, and a position-effect sensitivity analysis.
- Unusually honest reporting of negative or deflating findings (imputation closes the gap when complete source records exist; GBDT/MLP updates have identification floors that make capped audits infeasible at b = 3; measurement effects of plausible size swamp the sampling gain).

**Weaknesses**

1. [major] Limited practical significance, by the paper's own evidence. The framework requires a single, known, degree-≤ b contrast, finite features, and a label observed on every record. Appendix A27 shows that ordinary model updates (GBDT, MLP, or any thresholded ensemble) have identification floors of 0.05–0.66 at b = 3, far above a useful half-width, so the ML motivation (auditing a model update under a feature cap) applies essentially only to depth-b tree ensembles. In the feasible cases the realized gain is a factor 1.0–2.0, which (i) is matched or beaten by MI/regression imputation whenever complete source records exist (Tables 6–7) — and any frozen rule was trained on such records — and (ii) is comparable to the bias induced by a modest position effect (A26). For the survey audience, a design tuned to one contrast is not a multipurpose split-questionnaire design. The paper acknowledges all of this, but it leaves the "statistical value of adaptive feature queries" modest in practice.

2. [major] Moderate theoretical originality. Theorem 1 is an application of standard tools (Donoho/Juditsky–Nemirovski/Polyanskiy–Wu duality, KL chain rule, van Trees), as the authors say; the two ingredients of Theorem 2 (guess-the-path simulation of an adaptive tree, and the address/indexing function) are classical in decision-tree complexity; Theorem 4 is Cauchy–Schwarz plus an optimal importance-sampling allocation; Proposition 5 is adaptive importance sampling with pointwise constraints. The genuinely new technical content is concentrated in Theorem 3(c), whose bound is informative only for b ≥ 10 and uses m = 2^b − 1 coordinates, whereas in the practical regime b ≤ 6 only a 4/3 separation is known.

3. [major] The population-specific bracket (Theorem 4) is loose where it matters. Its upper end is completion-only path guessing, which the paper itself shows is 2–17x worse than the optimal fixed design; in Table 3 the upper ends are 1.5–11.4 against realized ratios of 1.0–1.6. The lower end is tight only in the trivial case Γ_P = 1 (the tree uses at most b distinct items, so one form computes it), which is exactly what the thyroid "detection" amounts to. For BRFSS at b = 4–6 the lower end (1.08–1.18) is far below the realized ratio (1.35–1.58). The Spearman correlation of 0.78 over 48 screening runs includes 16 thyroid runs with ratio identically 1.

4. [major] Evaluation populations and missing protocol details. The "exact ratios" are exact for an artificial population: a held-out empirical law on up to 2^12 profiles (WDBC has 569 records in total, Ionosphere 351, split 20 ways into two disjoint training sets plus a held-out set) mixed with 1% uniform mass, and both compared designs are oracles tuned to that law. The held-out sample sizes are never stated, and the forest protocol's "minimum leaf size max{3, n0/30}" uses an n0 that A1 defines only as a pilot sample size. The smoothing and bootstrap sensitivity analyses are reassuring (≤ 8%), but the reader cannot judge how many profiles carry mass or whether Spambase (4,601 records) behaves differently from the tiny datasets.

5. [minor] Terminology in the imputation comparison. The A23 estimator (conditional mean of t from source donors with a naive SE) is regression imputation, not a model-assisted (GREG/difference-type, design-consistent) estimator; calling it "model-assisted" will mislead survey readers. The MI coverage of 0.975–0.993 under the random-half target also indicates Rubin's variance is conservative here, which should be noted.

6. [minor] Presentation and internal consistency. The main text is extremely dense (Section 6 is a wall of numbers; Theorem 1 bundles four distinct claims). The appendix refers repeatedly to experiments that the paper never introduces: SUSHI and SAPA (A12, A18.3, A25, A26, Fig. 4) first appear on p. 27 with no description of the data or task; yet the main-text Limitations section quotes A26's position-effect numbers that are computed on those "ten binary tasks". There are dangling references ("the sufficient count in Section 2", A27), mentions of "v12 results", "the earlier release", and "a separate supplementary report" that reviewers do not have, and the Table 4 "default choices" read like internal notes.

7. [minor] The finite-sample constant 104 (Theorem 1/6) and the factor-b and (3b)^r losses in Theorem 3 are loose; the paper is upfront about this but it limits the finite-sample story.

8. [minor] The label is assumed free and observed for every record, whereas in screening validation the label (e.g., a diagnostic test) is often the expensive item; A25 touches on cost regimes but only for the appendix-only SUSHI/SAPA tasks.

**Soundness** (3): The theorems I checked are correct and the evaluation is methodologically careful, but the headline empirical ratios are oracle comparisons at smoothed small-sample empirical laws with unstated held-out sizes, and the bracket's upper end is not a useful bound in practice.

**Presentation** (2): Precise sentence-level writing and good figures, but the main text is very dense and the appendix references datasets, experiments and reports that are never introduced, with several dangling cross-references.

**Significance** (3): A clean answer to a natural question that the missing-data/adaptivity sub-community will cite, but the practical value is modest by the paper's own evidence and the applicable model class (degree-≤ b contrasts) is narrow.

**Originality** (3): The question and the sharp constants are new; the constructions and tools are classical, with the pointer-tree potential argument being the genuinely novel technical contribution.

**Key Questions for Authors**

1. What are the training and held-out sample sizes (and the number of distinct observed profiles) for each (dataset, m) cell of the forest experiments, and what does n0 denote there? If the held-out sets for WDBC and Ionosphere at m = 12 are on the order of 100–200 records on 4,096 profiles, please report the exact ratio also with larger held-out fractions (Spambase allows this) to show the realized gain is not a small-sample artifact. A satisfactory answer would resolve weakness 4 and raise my soundness assessment.

2. Can the upper end of Theorem 4 be tightened by optimizing the pointwise-unbiased score over the tree's padded path-set menu with shared-coordinate augmentation (your program (20) restricted to L forms), which is still computable from reference data without the C(m,b) enumeration? A bracket whose upper end tracked "Best" in Table 3 would make Theorem 4 a genuinely useful planning tool and would raise my view of its significance. Relatedly, what is the detection power of the rule "lower end ≤ 1.05 ⇒ realized ≤ 1.25" — how many runs with realized gain > 1.25 had a lower end ≤ 1.05?

3. In what realistic setting is a frozen low-degree rule available but no trusted complete reference is, so that the design-based branching audit is the right tool? Under your "other sex" shift the regression-imputation bias is only 0.003–0.0045 (vs. SD ≈ 0.03). Can you construct or identify a realistic shift (e.g., a different survey mode or a different year of BRFSS) where imputation from source records fails while the design-based scores remain valid? A convincing case would address weakness 1 directly.

4. For the practically relevant range b ≤ 6, can your solver compute the exact sup over Boolean (or all identifiable) contrasts of V2/Vbranch for small (m, b), e.g., (5,3), (6,3), (7,4), to indicate whether the 4/3 separation of Corollary 17 is close to the truth? This would make Theorem 3 relevant in the regime of the experiments.

5. Given that A26 shows position effects of plausible size produce bias comparable to the sampling gain, do the PISA position checks (A24.4) or any other data offer an empirical estimate of order/branching effects for the item types considered, and how would the pointwise-unbiased scores be modified to target the latent Δ under a known measurement kernel K_T? The answer affects how I weigh the practical limitations.

**Limitations**

Yes. Section 8 and Appendices A25–A27 discuss the single-estimand restriction, the low-degree identification requirement and its failure for GBDT/MLP, the mode/position-effect assumption with a quantitative sensitivity analysis, the reliance on the target law for population-specific designs, the imputation alternative, and computational limits (m ≤ 12, b ≤ 6). Two constructive suggestions: (i) state the single-contrast, label-always-observed, degree-≤ b scope in the abstract and introduction rather than only in Section 8, because it governs applicability to both surveys and ML; (ii) either introduce the SUSHI/SAPA tasks in the paper or move every appendix section that depends on them (A12, A18.3, A25, A26, Fig. 4) to the supplementary report, since main-text claims currently rest on undescribed experiments.

**Overall Recommendation**

4: Weak accept — a technically solid paper that advances the statistical theory of adaptive data collection under per-record caps with sharp, correct results and careful experiments, but with modest practical significance and presentation problems.

**Confidence**

4

**What would move you up one point**

- A tightened, reference-computable upper end for Theorem 4 (optimal augmented path-set scores) so that the bracket is informative beyond the trivial Γ_P = 1 case, demonstrated on the screening runs.
- A realistic setting (real or semi-synthetic shift) where imputation from complete source records fails and the design-based capped audit remains valid, establishing the practical case the paper argues for.
- Extension of the round hierarchy into the b ≤ 6 regime (removal of the polynomial factors, or exact small-(m,b) frontiers for V2/Vbranch).
- A clean revision: state held-out sizes and define n0; introduce or remove SUSHI/SAPA; fix dangling references and remove "v12"/"earlier release"/"supplementary report" remnants; compress Section 6 into a protocol table plus a few headline numbers.
