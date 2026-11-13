# Round 5 — simulated review R2 (statistics / survey methodology) of v15 (`Manuscript/paper.pdf`)

Overall Recommendation: **4 (Weak accept)** — Confidence 4 — Soundness 3 / Presentation 3 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-12; not real ICML feedback. Full text as returned.)

**Summary** (in my own words)

The paper studies estimation of a known functional Δ(P) = E[Y d(X)] (e.g. accuracy of a frozen screening tree, or the accuracy difference of two frozen rules) when every sampled record has its label observed but at most b of m binary features may be queried. It compares three acquisition classes: fixed forms chosen before the record is seen (planned missingness / split questionnaires), r-round interviews, and fully branching interviews (depth-b decision trees). The question is how many more records the less adaptive classes need.

The main results are:

- **Theorem 1.** For any finite menu of interviews, the worst-case first-order minimax constant V(d, A) is a finite convex program with an Elfving-type dual. The converse covers biased estimators, across-record adaptation and label-dependent interview choice.
- **Theorem 2.** Fixed forms need at most K = min{2^(b-1), C(m-1, b-1)} times the records of branching. This holds for the worst-case constant and, via a centred simulation argument, for the population-specific efficiency constant W_A(P) at every P. It is attained by an "address" contrast.
- **Theorem 3.** r rounds lose at most 2^(b-r). Pointer-chasing and binary pointer-tree constructions show that a constant number of rounds can still lose 2^(b(1-o(1))), in polynomial dimension.
- **Theorem 4.** A population-level bracket 1/ρ²_P ≤ W_fixed/W_branch ≤ N_P, plus a column-generation solver with DP pricing that certifies the optimal design in each class.

The experiments (random-forest updates on three small UCI datasets; CART screening trees on BRFSS-derived and thyroid items) find that optimized fixed forms cost 1.0–1.98× branching, that a second round recovers most of the gap, and that uniform random forms cost 9–23×. Simulations compare the design-based scores with imputation from complete source records and with a two-way log-linear working model fitted by EM.

**Strengths**

1. A clean, well-posed question with sharp answers. The 2^(b-1) factor is exact, not just an order, and it holds at every population. The centring device (return c + K(H − c) with c = Δ(P)) that turns a second-moment simulation bound into a variance bound at every P is simple and correct. I verified the proof of Theorem E.1(a)–(d).
2. The paper is unusually honest about what is classical. It says explicitly that for a fixed menu W_A(P) is a c-optimal design problem, and that for a fixed design the optimal score is the Robins–Rotnitzky–Zhao/Tsiatis efficient augmented IPW estimator under known coarsening (Sec. 3, App. E.6, App. C.5.2: "not a new general efficiency principle"). The claimed novelty, comparison across menus and exact optimization over combinatorial menus, is accurately scoped.
3. The proofs I spot-checked hold up:
   - the two-point converse with the constant 104 (App. B.3.2; the arithmetic 8/15, 2/√15, 15·27² > 104² checks out);
   - the van Trees argument for the exact constant (B.3.3);
   - the address-contrast energy calculation (6) and its product version (Prop. C.4);
   - the local-minimax counterpart (Prop. C.7);
   - the two-phase self-calibration (Prop. E.6).
   
   The rounds lower bound (Theorem D.3, potential Q_t = M_t + 2^L π_t, multiplicative across blocks) is the most original mathematics. I followed it at reading depth and found no gap.
4. Statistically relevant extensions are handled, not ignored:
   - label-dependent (outcome-dependent) form probabilities (Prop. E.2; empirically worth ≤ 0.8%);
   - mean budget versus hard cap (the gap collapses to ≤ m/b, linking to two-phase designs);
   - non-binary alphabets;
   - identification floors when deg(d) > b.
5. Exact unbiasedness of fitted designs under a wrong reference law ("only the variance depends on the reference") is the right robustness property and is correctly argued.
6. The empirical section reports results unflattering to the method: the log-linear working model matches branching at n = 1000; complete records undercut fixed forms once labels are moderately expensive (F.8); order effects swamp the gains. The numbers are internally consistent wherever I cross-checked text against Tables 3, 7, 8, 10, 11 and 12 (17/24 two-round-computable trees, the 14 + 4 runs, 89% and 59% log-gap recoveries, the 2,100/2,800/26,700 sample sizes).
7. Appendix H analyses a real planned-missing archive (PISA 2012 rotated forms) with Fay BRR replicate weights and a chained-equations MI comparator. This is rare in an ML submission, and it is appropriately modest ("no branching benefit, MSE or coverage estimate is claimed").

**Weaknesses**

1. **[major] The paper's own evidence shows the phenomenon is small in practice, and the practically relevant regime is narrow.**
   - The exponential constants are attained by address/pointer contrasts. On every trained model the price of pre-commitment is at most 1.98×, and it is exactly 1 for all 24 thyroid runs and for 7 of 24 BRFSS runs.
   - At n = 1000, the size the paper uses for illustration, a two-way log-linear model fitted by EM to the same capped records has RMSE 0.90–1.01× that of branching, with coverage 0.920–0.968 (F.6, Table 12). A standard planned-missingness analysis therefore erases the fixed-versus-branching gap at survey sizes. Its bias only matters around n = 16,000.
   - F.8 shows complete records beat the best fixed design once a label costs more than about 4–15 feature questions. In screening validation that is nearly always true.
   - When a depth-b tree computes d and branching is allowed, the "optimal branching design" is simply to run the tree.
   - So the regime where the constants matter is: hard immutable cap, cheap labels, no acceptable working model, a single known low-degree target, and n large enough for model bias to dominate. The paper says most of this, but the abstract and introduction still lead with the 2^(b-1) message.

2. **[major] The headline "balanced random forms need 9–23×" compares against a straw man for this estimand.**
   - The uniform design ranges over all C(12, b) forms, including items the rule never uses. The factor is essentially the probability that a random form covers the tree's items (e.g. b = 3, rule on 2 items: 10/220).
   - Nobody auditing one known rule would randomize over irrelevant items. Balanced matrix-sampling designs exist for multipurpose estimation and are analysed by ML/MI, not by Horvitz–Thompson scores of one depth-b functional.
   - The paper's own Table 12 shows the EM analysis on those same uniform forms has RMSE 1.4–1.8× branching at n = 1000, i.e. roughly 2–3× in records, not 9–23×.
   - The fair naive baselines are uniform over the tree's path sets, or over forms inside the rule's items. Path guessing (N_P) is reported at about 3–10×; that should be the headline comparator. "Design matters more than adaptivity" is therefore overstated.

3. **[major] The "records needed" comparison at a population is an oracle comparison, and the cost of learning the design is not charged symmetrically.**
   - W_fixed(P) is attained by a design tuned to P (form probabilities, tables, centring constant). For a screening tree, branching needs no tuning.
   - Without a reference sample, the pilot scheme (Prop. 5 / E.6) estimates from phase-two records only, with n1 = o(n). Table 10 reports the per-record variance of the learned design and does not charge the pilot records.
   - At the paper's own example (b = 5, about 2,800 records for the oracle fixed design), a 1,000-record pilot plus a 19% variance excess gives a realized price nearer 2× than 1.35×. At b = 6 the learned design is 1.3–2.7× worse than the oracle path-set design for pilots up to 4,000.
   - The pilot scores are themselves unbiased and could be pooled, but this is neither done nor analysed. A cross-fitted or sequentially refitted estimator that uses all records is the standard remedy and is only mentioned in one sentence.

4. **[major, for significance] Novelty beyond classical theory is real but moderate.**
   - Theorem 1 combines standard pieces: linear-functional minimax duality, two-point plus van Trees converse, Elfving duality.
   - W_A(P) is the known-coarsening efficiency bound minimized over the design.
   - Theorem 2's upper bound is Horvitz–Thompson "guess the path" with at most 2^(b-1) supports. Its lower bound is the indexing function, i.e. the classical adaptive versus non-adaptive decision-tree separation re-expressed as explained variance.
   - Theorem 4 is a Cauchy–Schwarz bracket that is empirically loose: 1/ρ² is off by a median 1.30 and N_P by 3.6. The useful upper end is the path-set program, which is a computation, not a bound.
   - What is new is the statistical framing, the exactness at every P, the rounds hierarchy (Theorem 3c–d) and the certified solver. That is a respectable contribution, but a statistician will see largely familiar machinery applied to a new comparison.

5. **[major/minor] Optimality of W_A(P) is local-asymptotic in the saturated nonparametric model on 2^(m+1) cells.**
   - Prop. C.7 needs full support, manufactured by mixing 1% uniform mass into every empirical law, and an n → ∞ limit with the dimension fixed.
   - With m = 12 (8,192 cells) and n of about 10³, this asymptotic regime does not describe the experiments. That is exactly why the parsimonious working model wins at n = 1000.
   - A "model-assisted" middle ground is missing: design-consistent scores whose augmentation comes from a parsimonious working model fitted to the capped data, with model selection or richer interaction orders. Only the two extremes (saturated design-based, two-way model-based) are compared.

6. **[minor/major] Statistical soundness of the "exact, certified" real-data constants.**
   - "Certified" refers to optimization error (10⁻⁴) at a plug-in law, not to sampling error.
   - For the forest tasks the "population" is 171–269 held-out records (Ionosphere: 121 of 4,096 profiles occupied) plus 1% uniform mass. Both optima are infima over designs evaluated at the same sparse empirical law, so both are optimistically biased, and the branching menu is far richer.
   - A bootstrap of the same held-out records (max change 7.5%) cannot reveal support-sparsity bias. No interval is given for any ratio as an estimate of a population quantity.
   - The BRFSS evidence is on firmer ground (about 10⁵ records) but comes from one dataset, 12 hand-picked dichotomized items and 24 trees (2 targets × 3 seeds × 4 caps). The 21-item study reuses the same trees. The other survey-type dataset (thyroid) shows no gap at all.
   - "At least 80% in every case solved to optimality" conditions on solver success. The four unsolved b = 6 runs have certified recoveries as low as 59%.

7. **[minor] Sampling model.** "Design-based" here means iid draws from P with randomized forms. BRFSS is a complex sample, but the Kaggle/UCI-derived file is used as an unweighted population. Only the PISA appendix handles weights, replicates or clustering. How optimal form probabilities interact with unequal weights and design effects is not discussed.

8. **[minor] Motivation.** "A mailed form cannot branch" is not quite right: paper instruments routinely carry skip instructions. What they cannot do is print fewer items; the respondent still answers at most b. Laboratory batches and pre-printed rotated booklets are the better examples. Relatedly, a hard per-record cap with every label observed is an unusual cost structure, and the paper's own mean-budget result (ratio ≤ m/b) shows how much rests on the cap being hard.

9. **[minor] Baseline details.**
   - Regression imputation uses a "naive standard error".
   - The hot-deck MI over-covers (0.975–0.993) under no shift, so its interval widths are not comparable.
   - The shift variables were chosen so that imputation cannot condition on them. That is a legitimate stress test, but the reported bias is unsurprising, and there is no imputation model that includes available auxiliary covariates.
   - The EM comparator uses a delete-a-group jackknife with only eight groups.

10. **[minor] Presentation.**
    - The eight-page body is extremely dense and leans on a 40-page appendix.
    - The "log-gap recovered" metric is defined only in App. F.2.
    - Table 2's columns are hard to parse.
    - The statement "every experiment reported anywhere in this paper is described in Appendix F" is inconsistent with the additional analyses in Appendices G.1.1 and H.
    - The authors disclose that a generative model helped derive and check proofs. The parts I checked are correct, but the rounds proof (D.1) deserves a careful read by a complexity-theory reviewer.

**Soundness**: 3 — the theorems I checked (B.3, C.1, C.7, E.1, E.2, E.6, the address/product lower bounds) are correct and carefully stated; the weak points are empirical (plug-in "exact" constants at sparse, smoothed empirical laws, uncharged pilot records, a favourable naive baseline), not mathematical.

**Presentation**: 3 — precise, well hedged and internally consistent, but heavily compressed in the body and dependent on the appendix; several headline numbers need the appendix to interpret.

**Significance**: 2 — a clean reference result for budgeted evaluation and planned missingness, but the paper's own data show a gap of at most 2× that a routine working-model analysis removes at survey sizes, and the regime of hard cap, cheap labels and a single known target is narrow.

**Originality**: 3 — the cross-menu "price of pre-commitment in records" framing, the every-population sharpness and the rounds hierarchy are new; the individual tools (AIPW/known-coarsening bound, c-optimal design, the indexing-function separation) are classical and are acknowledged as such.

**Key Questions for Authors**

1. **Pilot accounting.** In Table 10 and Prop. 5, are the n1 pilot records used in the final estimate? Please report the total number of records (pilot plus main) needed for a fixed target precision, compared with branching, at b = 4, 5, 6. Include a version that pools the pilot's unbiased scores or refits sequentially.
   - If the all-in price stays near the oracle 1.35–1.6×, weakness 3 largely disappears.
   - If it is about 2× or worse at realistic n, the abstract's "1.0–1.98" should be presented as an oracle bound, and my significance score stays where it is.

2. **Fair naive baseline.** What are the ratios for (a) uniform randomization over the tree's path sets with optimal scores, and (b) a balanced design restricted to the items the rule uses? What is the records ratio of the EM/log-linear analysis on uniform forms relative to branching?
   - If the gap between sensible naive designs and the optimum is about 2–4× and not 9–23×, the "design matters more than adaptivity" claim and the abstract need rewording.
   - If it remains near an order of magnitude, I would raise significance.

3. **Model-assisted middle ground.** Fit the working model (two-way, three-way, or selected) to the capped records, use it only to build the augmentation tables of a pointwise-unbiased score (cross-fitted), and report RMSE and coverage at n = 1000 and n = 16,000.
   - If this recovers most of the EM efficiency at n = 1000 while keeping coverage at n = 16,000, it strengthens the practical case for the design-based constants and would raise my score.
   - If it does not, the paper should say plainly that at survey sizes model-based analysis dominates.

4. **Sampling uncertainty of the ratios.** For the forest tasks and the BRFSS runs, can you estimate W_fixed/W_branch at the population from a split sample (optimize on one half, evaluate both menus' designs on the other) and give intervals? Does the ratio change materially compared with the plug-in value?
   - Stable split-sample ratios would resolve weakness 6.
   - A systematic shift would lower my soundness score.

5. **Scope of the hard cap and iid sampling.** How do the population constants change under (a) a mean budget of b with a hard cap B > b (you have this for the address contrast in Prop. C.6; what about the BRFSS trees?), and (b) unequal sampling weights?
   - Evidence that the 1.3–1.6× gap persists under a modestly relaxed cap would increase the result's relevance to two-phase and multi-wave practice.
   - If it vanishes quickly, that should be stated as a limitation.

**Limitations**

Largely yes. Section 8 is candid about the single known low-degree target, the design-based versus model-based trade-off, order effects, the observed-label assumption, worst-case populations, and solver scale. Constructive additions:

- State that the population constants are oracle constants and give the all-in cost of learning the design (pilot records included).
- State that W_A(P) is a fixed-dimension asymptotic bound in the saturated model, and that at n of about 10³ and m = 12 it is not the operative benchmark.
- Note that the forest "populations" are sparse smoothed empirical laws and the ratios carry unquantified sampling error.
- Acknowledge that the uniform-forms comparator is a multipurpose design analysed in a way practitioners would not use.
- Note that the main-body survey analyses ignore complex-sample weights.

**Overall Recommendation**: 4 — Weak accept

Technically solid and unusually careful, with sharp theory and honest experiments. It advances a sub-area (budgeted evaluation, planned-missingness design) without, on its own evidence, demonstrating large practical stakes. I would not fight a rejection on significance grounds, but the correctness, the exactness and the candour put it above the bar for me.

**Confidence**: 4

I am expert on the missing-data, efficiency and survey aspects, and I checked the corresponding proofs and cross-checked the tables. I read the pointer-tree rounds argument but did not verify every step, and I cannot fully vouch for novelty relative to the most recent query-complexity literature.

**What would move you up one point**

- An all-in accounting of the learned fixed design (pilot or sequential refitting, all records used) showing the deployable price of pre-commitment stays close to the oracle ratios at realistic n, with the abstract adjusted if it does not.
- Replacing or supplementing the uniform-over-all-forms headline with sensible naive baselines (path-set uniform, used-item balanced designs, the EM analysis on balanced forms), and rewording "9–23×" accordingly.
- A model-assisted comparator (working-model augmentation inside a pointwise-unbiased, cross-fitted score) that shows whether design-based exactness and working-model efficiency can be had together at n of about 10³.
- Split-sample or interval estimates for the reported ratios, so that "exact" constants are separated from sampling error, and at least one additional real survey population in which a gap above 1 is observed.
- A reframed abstract and introduction that lead with the population-level finding (the gap is at most about 2× on trained models, and when it is 1) and present the 2^(b-1) results as the worst-case envelope.

With the first three delivered convincingly I would move to 5. Without them I stay at 4.
