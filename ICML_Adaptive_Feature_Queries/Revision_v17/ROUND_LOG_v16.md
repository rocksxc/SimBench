# v16 revision loop — round log (continues ROUND_LOG_v15.md, which contains the round-6 novelty gate)

## Round 6 — novelty gate
Run on 2026-11-12 at the user's request, before the revision; recorded at the end of ROUND_LOG_v15.md. Verdict: PASS. One close neighbour was found that v15 did not cite (Gonzalez & Eltinge 2008, adaptive matrix sampling); v16 cites and discusses it. The qualitative within-sample separation is known from the huge-object model (Adar & Fischer 2024); v16 says so.

## Round 5 -> v16 revision (addresses Reviews/round5_v15_*.md)
- Framing (R2, R3): the abstract and introduction lead with the finding on trained models (1.0-1.98x; one round recovers most of the gap) and present 2^{b-1} as the worst-case envelope; the design-based regime is called a deliberately demanding benchmark.
- Theory (R1): Proposition (gaps persist at every accuracy): for a +-1 rule with labels equal to the rule flipped independently with probability 1-p, Var(E[t | transcript, Y]) = sigma^4 E[e^2/(1 - Delta^2 e^2)] <= sigma^2 E[e^2], so the address contrast has W_fixed/W_branch = 2^{b-1} at every p in (0,1) and the pointer-tree round bounds hold at every p; checked numerically at b = 2, 3. Remark: the every-population bound holds for several contrasts served by one design. "Sharp" is qualified (attained for m >= b - 1 + 2^{b-1}; open at moderate m); Theorem 1 is slimmed (finite-sample version in the appendix); pointer chasing is moved out of Theorem 3 and the proof sketch of the pointer-tree bound is fuller; the relation to locally bounded adaptivity (Adar & Fischer) and to restricted-focus-of-attention learning is stated precisely. Not done: a round hierarchy tight up to poly(b) (open).
- Baselines (R2, R3): the headline comparison is no longer uniform over all forms. New naive designs with optimal scores: uniform over the tree's path sets and uniform over b-subsets of the items the rule depends on.
- Oracle versus deployable (R1, R2): the pilot is charged. Cross-fitted pilot scores plus the learned design give an all-in price for N records.
- Model-based analysis (R2, R3): RMSE of two- and three-way log-linear working models against the design-based score for all twelve BRFSS trees at b = 4, 5 and n = 500 ... 32,000. The paper now says plainly that at survey sizes the working model is the more accurate tool. A model-assisted score is not implemented; the appendix explains why it cannot beat the oracle tables.
- Single-use data (R3): reuse of one rule's design for another rule, and joint designs for two and three rules.
- Counts and consistency (R2, R3): the 21-item trees are no longer counted among the runs with a gain or shown in the main table; the two-round claim is split into computable / solved / bounded runs; Appendix A no longer says that every experiment is in Appendix F; the log-gap is defined in the main text; the notation r for data bits in the address computation is renamed.
- Limitations added: unweighted, sparse, smoothed empirical populations; oracle designs and local asymptotics behind the W ratios; four open two-round programs.

## Round 6 — experiment results at the v16 freeze
- Address contrast at accurate populations (solver, no smoothing): W_fixed/W_branch = 2.000000 (b = 2) and 4.000000 (b = 3) at p = 0.5, 0.6, 0.75, 0.9, 0.97.
- Naive designs with optimal scores, BRFSS b = 4-6 (records relative to branching): uniform over path sets 1.24-2.77 (median 30% above the optimized design, at most 58%); uniform over item subsets 1.00-4.73 (median 90% above); uniform over all forms 9-23; optimized 1.00-1.98.
- All-in price with a quarter of the records as a cross-fitted pilot (median over runs with a gain): N = 4000: 1.67 (b = 4), 1.80 (b = 5); N = 8000: 1.65, 1.63; oracle all-forms 1.52, 1.35. At b = 6 pilots up to 2000 are too small (all-in 3.30 against 1.58).
- Working models against the design-based form score, 12 trees, 400 replications: two-way model better for all 12 trees up to n = 4000 (median RMSE ratio 0.80-0.88 at every size); worse for 3 of 12 at 8000 and 4 of 12 at 16,000 and 32,000 (up to 1.36 and 1.81). Three-way model within 0.88-1.13 at every size; worse for 9 of 12 at 32,000. The round-5 impression of a crossover near 16,000 came from the seed-0 trees only and does not hold in the median.
- Reuse (BRFSS other-sex target, three trees per cap): records for one rule scored on another rule's design need 1.55-317 times the records of branching. Joint design for three rules: each rule a median 10% (at most 51%) above its own optimum; sum of ratios 4.6-5.0 against 9 for three separate branching subsamples.

## Round 6 — simulated reviews (2026-11-13)
Three fresh, mutually independent reviewer agents read the frozen v16 PDF (56 pages; md5 599e2ef526acdc094f97f4ec4fe4651a) through the packet `build_review_packet.py` produces (cleaned text and 100 dpi page images) with the unchanged prompt template. Full texts: `Reviews/round6_v16_R{1,2,3}_*.md`.

| Reviewer | Overall | Confidence | Soundness | Presentation | Significance | Originality |
| --- | --- | --- | --- | --- | --- | --- |
| R1 (theory) | 3 (Weak reject) | 4 | 3 | 3 | 2 | 3 |
| R2 (statistics) | 3 (Weak reject) | 4 | 3 | 2 | 2 | 3 |
| R3 (applied ML) | 3 (Weak reject) | 3 | 3 | 2 | 2 | 3 |

Goal (all three >= 4): not met. Round 5 was 4/4/3; R1 and R2 each moved down one point.
- R1 moved down mainly for an over-claimed sentence: linear-round necessity is proved for the single pointer tree (2^b - 1 features) only, while the abstract and Section 4 read as if it held on b^2 features. Checked after the review: the reviewer is right. The product contrast of Theorem 3(c) has k = floor(b/beta) blocks of depth beta = floor(log2 b); reading level j of every block in round j uses k*beta <= b questions and beta rounds and evaluates the contrast exactly. The theorem statements are correct; the "so" in the abstract and "exponential dimension is not needed" after the 0.37b sentence in Section 4 are not. The frozen PDF is left as reviewed; this is the first item for v17.
- R2 moved down for the regime: the working-model study that round 5 asked for shows a two-way model on the same fixed-form records matching branching up to n = 4,000, and v16 says so in the abstract; the reviewer concludes that the characterised constant does not govern accuracy where such audits run, and that the oracle range should not lead.
- R3 stays at 3 with the same request as in rounds 4 and 5 (a realistic use case; scale).
- No reviewer found an error in a proof. All three give Significance 2 for the third round in a row.
- R2 noted that "within 13-20% of the oracle" does not equal the ratio of the Table 10 medians. It is the median of per-run ratios (`v16_tables.py`, field `over`); the text should say so.
- R1 and R3 could not match Li et al. (2026) to the round bound attributed to it. The entry was found by web search in round 3 (ROUND_LOG_v13.md) and was read through search results only; it is unverified and must be checked by the authors or removed.

