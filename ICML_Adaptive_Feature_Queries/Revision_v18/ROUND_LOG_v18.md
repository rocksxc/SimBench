# v18 revision loop — round log (continues ROUND_LOG_v17.md)

## Round 8 — novelty gate (web search, 2026-11-13, before the revision)
Verdict: PASS (unchanged).
- Main claim and the model-based direction: no new prior work found since the round-7 gate of the same day. A search for adaptive versus non-adaptive feature queries under log-linear or Ising models with strong couplings returned only adjacent work (graph property testing, crowdsourced feature discovery).
- Joseph, Mao, Neel & Roth 2019 (FOCS; arXiv:1904.03564): any fully interactive compositional locally private protocol can be transformed into a sequentially interactive one with a blow-up in sample complexity linear in the compositionality, and the blow-up is tight. This is the closest precedent for the simulation theorem of v18 (noiseless transcripts, blow-up K_r, exact for every task); v18 states the relation. Whether their reduction uses rejection sampling could not be confirmed from search results.
- Quadratization of pseudo-Boolean functions (Rosenberg 1975; surveyed by Boros & Hammer 2002): a product of two binary variables can be replaced by an auxiliary variable with a quadratic penalty that vanishes exactly when the auxiliary variable equals the product. v18 uses this standard gadget to build pairwise laws with strong couplings; cited as known.
- All read through search results only. Narrowness: as before, in the setting, not in pre-emption.

## Round 7 -> v18 revision (addresses Reviews/round7_v17_*.md)
- Exact simulation (R1 weakness 2 and item 3, R2 weakness 1). New Theorem `thm:simulation` (Appendix C.1): with a uniform guess over the distinct padded path sets and an extra coin that equalizes the acceptance probability at 1/K_r, an r-round protocol reproduces any branching protocol exactly, for every law, task and sample size, with a geometric number of records per branching record (mean K_r), independent of the output; n' records give Binomial(n', 1/K_r) branching records. Theorem 2 now starts with this statement; the inequalities for V, W and the model constants are presented as its consequences; the centred score is kept as the explicit unbiased score for a fixed sample size. The relation to the conversion of fully into sequentially interactive private protocols (Joseph et al. 2019) and the Fourier-l1 baseline (4^{b-1} for the address contrast against 2^{b-1}) are stated.
- Model-based gap at laws with dependence (R1 item 2 and Q3, R2 Q1). Theorem `thm:structuredfull` has two new statements.
  (b, stability) For k <= b the polynomial bound holds up to a factor 1 + eps on a neighbourhood of every product law (no explicit radius).
  (d, counterexample) Add to the address contrast a one-hot copy s of the address and the products p_j = s_j z_j. The pairwise laws P_beta proportional to exp(beta H), H = sum_j s_j <a,j> - (kappa+1)(sum_j s_j - 1)^2 - sum_j (3 p_j + s_j z_j - 2 p_j s_j - 2 p_j z_j), have full support and lie in M_2; as beta grows they concentrate where t = Y(2 sum_j p_j - 1), a polynomial of degree two. Hence W^(k)_fixed / W^(k)_branch >= (1 - eps) 2^{b-1}/b at such laws for every k >= 2, on m = b - 1 + 3 * 2^{b-1} features. A parsimonious model therefore removes the gap only under weak dependence; the abstract, the contribution list, Section 6 and the discussion say so.
- R2's two requested statements are next to Theorem 5: parts (b)-(c) are first-order statements at laws without dependence and the k = 2 optimum has singular information; the 1.02-1.13 ratios describe populations that satisfy the fitted model.
- New computations: `dependence_v18.py` (constants along the path P_beta at b = 3, and at pairwise and three-way fits of noisy address populations at b = 3, 4); `aipw_v18.py` (a cross-fitted model-assisted estimator on fixed forms that uses only the audit's records, with coverage; R2 Q3, R3 Q4).
- Traceability (R2, R3): the abstract gives the medians of Table 2 for the pilot-learned design instead of a range over runs; the pilot paragraph says that its oracle values are medians over the runs with a gain.
- Presentation: the rounds sketch in Section 4 is shortened; fonts of Figure 3 enlarged; leftover wording in Appendices B and C replaced ("audit", "update").
- Not done: a sharper rounds theorem; a quantitative weak-dependence condition with an explicit radius; survey weights and bootstrap intervals for the BRFSS constants; a sequential design baseline; non-identifiable targets; a realistic use case with its own data.

## Round 8 — independent check of the new proofs (before the reviews)
A fresh agent refereed Theorem `thm:simulation` and the new parts (b, stability) and (d) of Theorem `thm:structuredfull`, with its own exact enumerations and an independent solver (copied to `Research/code/theory_checks/simulation_dependence_referee/`). Result: no mathematical error. Repaired before the freeze:
- Simulation: wording for trees chosen from the current label (the simulating protocol is label-dependent only if the original is); the fixed-budget statement (a rule defined for every sample size; conditionally on B = k the output has the law of the first k transcripts); the first-order consequences are stated with their ranges (V always; W at full-support laws through the local minimax result, at every law through the centred scores; model constants through the information inequality); sharpness of the factor only for r = 1 and m >= b - 1 + 2^{b-1}; one guess per node drawn in advance for r >= 2.
- Part (d): the auxiliary features are free binary coordinates and the law puts mass at least 1 - eps on the set where they equal the one-hot code and the products; the statement is for b >= 3 (at b = 2 the bound is one and the computed ratio tends to one); Var(t) = 1 at every beta.
- The checker's own computations agree with `dependence_v18.py` on the fixed constants along the path (0.839, 1.465, 1.635 at beta = 2, 4, 6) and found max_S J_S(t) = b/(2D - b) at b = 2, 3, 4, which would improve the limit bound from 2^{b-1}/b to 2^b/b - 1; this sharper constant is not proved and not claimed.

## Round 8 — experiment results at the v18 freeze (PDF md5 f9c7700f27786fb1007813fc5f7dea79, 60 pages, main text 8 pages)
- Strong-coupling path (address contrast, b = 3, 14 features, pairwise laws P_beta): W^(2) fixed / branch = 0.333/0.333 (beta = 0), 0.432/0.425 (1), 0.839/0.761 (2), 1.223/0.892 (3), 1.465/0.934 (4), 1.635/0.987 (6; branching not closed within its budget, certified lower bound 0.795, so the ratio 1.66 is a lower bound). Ratios 1.00, 1.02, 1.10, 1.37, 1.57, 1.66. The theorem guarantees a limit of at least 4/3; the bound of part (a) is 4.
- Pairwise and three-way fits of noisy address populations (label equal to the rule with probability acc): pairwise ratio 1.00 at every accuracy (b = 3: acc 0.5 ... 0.97; b = 4: 0.5, 0.7, 0.9, 0.97); three-way ratio 2.46-2.68 at b = 3 and 2.75-3.35 at b = 4 (branching constant 1.000 throughout).
- Cross-fitted model-assisted estimator on fixed forms (12 BRFSS trees; 200 replications at b = 4, 100 at b = 5; n = 1,000, 4,000, 16,000): MSE relative to the reference-table score 1.00-1.01 (medians; single trees 0.95-1.05); coverage of the normal interval 0.952-0.960 (medians; single cells 0.870-0.980, against 0.890-0.990 for the reference tables on the same records; with 100 replications the Monte Carlo standard error of a coverage is about 0.02-0.03); |bias|/SD at most 0.24 (0.25 for the reference tables). It keeps design-unbiasedness without any reference data and does not capture the small-sample gain of pairwise maximum likelihood.
- Everything else is unchanged from v17 (ROUND_LOG_v17.md).

## Round 8 — simulated reviews (2026-11-13)
Three fresh, mutually independent reviewer agents read the frozen v18 PDF (60 pages; md5 f9c7700f27786fb1007813fc5f7dea79) through the usual packet with the unchanged prompt template. Full texts: `Reviews/round8_v18_R{1,2,3}_*.md`.

| Reviewer | Overall | Confidence | Soundness | Presentation | Significance | Originality |
| --- | --- | --- | --- | --- | --- | --- |
| R1 (theory) | 4 (Weak accept) | 4 | 3 | 2 | 2 | 3 |
| R2 (statistics) | 4 (Weak accept) | 4 | 3 | 2 | 3 | 3 |
| R3 (applied ML) | 3 (Weak reject) | 3 | 3 | 2 | 2 | 3 |

Goal (all three >= 4): not met; one point short, at R3. Round 7 was 3/4/3.
- R1 moved from 3 to 4. The simulation theorem and the dependence results are what the round-7 review asked for; the reviewer checked E.5(a)-(d) and found no errors, and now asks for a quantitative weak-dependence theorem, a tight rounds hierarchy or non-asymptotic ratios for a higher score.
- R2 stays at 4 and raises Significance from 2 to 3 (the first Significance score above 2 since round 3). New objection: the model-based constants are computed at the complete-data fit although the working model is misspecified for the target and its pseudo-true law depends on the design.
- R3 stays at 3 for the fifth round in a row, with the same first condition (a credible use case with its own data) and the statement that the feasible items alone would give "a borderline 3/4, not a firm 4".
- Presentation is 2 from all three reviewers: the body carries too many results for eight pages.

