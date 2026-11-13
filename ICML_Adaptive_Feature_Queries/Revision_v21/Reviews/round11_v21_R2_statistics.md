# Round 11 — simulated review R2 (statistics / missing data) of v21 (`Manuscript/paper.pdf`) — official round

Overall Recommendation: **4 (Weak accept, "a low 4")** — Confidence 4 — Soundness 3 / Presentation 2 / Significance 2 / Originality 3.
(Simulated by an independent language-model reviewer agent on 2026-11-13; not real ICML feedback. Full text as returned.)

**Summary** (in my own words, not the abstract)

The paper studies planned-missingness designs for estimating a single known functional Δ(P) = E[Y d(X)], such as the accuracy of a frozen screening rule or the accuracy difference of two rules. Features are binary, at most b of m may be asked per record, and the label is always observed. It compares three design spaces:

- **Fixed forms**: split-questionnaire or matrix-sampling designs, which are MCAR by design.
- **r-round interviews**: a few batches of follow-up questions.
- **Fully branching interviews**: skip logic, which is a monotone coarsening-at-random design.

The main results are as follows.

1. **Exact simulation.** n branching records can be reproduced in law by fixed forms with a random number of records of mean K·n, where K = min{2^(b−1), C(m−1,b−1)}. The method is to guess the path set and accept or reject.
2. **Tightness.** A multiplexer ("address") contrast on b−1+2^(b−1) features attains 2^(b−1) exactly, at every accuracy of the rule.
3. **Relaxations.** Analogous upper and lower bounds are given for r rounds (2^(b−r) upper, a pointer-tree lower bound), for c extra pre-committed questions (the worst case falls only like 1/(c+1)), and for mean budgets.
4. **Constants.** The worst-case constant V and the population constant W_A(P) are the first-order (local) minimax risks. W is the known-coarsening semiparametric efficiency bound optimised over the design, computed by a column-generation c-optimal-design solver with primal and dual certificates.
5. **Working models.** The simulation bound survives in any model. Conditional independence of features given the label removes the gap (up to a factor 2 for label-blind designs). A pairwise log-linear model with strong couplings does not remove it.
6. **Experiments.** Oracle constants are computed at smoothed empirical laws (BRFSS-derived items, thyroid, Spambase, small forests), with simulated audits. For trained depth-b trees with cap b, the best forms need about 1.0–2.4 times the records of branching. One or two extra questions, one follow-up round, or a pairwise working model analysed by EM removes most of that. Per question asked, branching keeps roughly a 1.4 advantage.

**Strengths**

- **A clean question that the planned-missingness literature has not posed this way.** Split-questionnaire, two-phase and multistage-adaptive work optimises within one design space. Comparing the spaces with exact constants is a real conceptual contribution, and the paper is explicit about what is and is not new.
- **The core theory is correct where I checked it.** I verified the following by hand:
  - The path-guessing simulation (Thm 1(i), Thm C.1): the path-set count, the equivalence "completion ⇔ S = S_τ(x)", and the acceptance step that makes the accepted record an unbiased draw.
  - The energy calculation (5) and the dual bound giving V_fixed ≥ 2^(b−1).
  - The identity in Prop. E.3 that carries the gap to every accuracy level.
  - The centred score in Thm E.1(a).
  - The counting in Thm 2(c): 2^(j+1)−j−2 extra questions, K⁺ < 2^(b+1)/(c+3), and the address value 2^(b−1)/(c+1).
  - The identification of W_q(P) with the Robins–Rotnitzky–Zhao known-coarsening bound (App. E.7.1) and the van Trees local-minimax arguments (Props C.10, E.4), which are standard and correctly applied.
  - Thm E.5(a),(b): the tangent space of the conditional-independence model, the information formula through inclusion probabilities, and the factor-2 argument.
- **Honest positioning against classical theory.** The simulation is called folklore, the efficiency bound is attributed to RRZ and Tsiatis, and the solver is called c-optimal design. The paper claims only the cross-menu comparison and the exact optimisation over combinatorial menus.
- **Theorem 4 is of real interest to missing-data methodologists.** Under conditional independence a design matters only through inclusion probabilities, so adaptivity is worthless once the label may steer the form. The part (e) construction shows that "pairwise" parsimony is coding-dependent. Both are non-obvious and practically meaningful for dummy-coded items.
- **Comparisons are fairer than usual for this kind of paper.** Model-based alternatives are evaluated under misspecification (pseudo-true limits, sandwich variances, coverage). Imputation from external complete records is reported as winning when it transports and as biased in 3 of 8 shifts. Pilots are charged to the audit. Uniform matrix sampling is separated from optimised forms. Results are also given per question, not only per record. The centred-versus-uncentred point, that naive path guessing inflates variance by more than K for accurate rules, is a nice detail.
- **Pointwise unbiasedness** of fitted designs, whatever the reference law, is a useful design-based property and is used consistently.
- **Limitations are stated candidly**, including the "knife-edge" nature of cap = depth and the 104 factor in the finite-sample bracket.

**Weaknesses**

1. [major] **The increment over classical theory is moderate, and the headline theorem is its least novel part.** The upper bound is the folklore adaptive-to-non-adaptive conversion. The matching example is the addressing or multiplexer function, the textbook separation of adaptive from non-adaptive query complexity. W_A(P) is the RRZ efficiency bound minimised over a known design, that is, Elfving c-optimality. What remains new is (i) phrasing the separation as an exact variance constant across records, (ii) the rounds, extra-question and mean-budget refinements, and (iii) Theorem 4. Items (ii) and (iii) carry the novelty, but both are compressed into a few lines of main text with proofs entirely in the appendix. The rounds result is not tight beyond constant r.

2. [major] **Under standard survey practice the empirical "price" largely vanishes, which limits significance.** Planned-missing data are usually analysed by maximum likelihood or multiple imputation under a working model. In the paper's own simulated audits the pairwise EM estimate on forms is within 1.00–1.07 of branching up to n = 8,000, and its squared bias equals the variance only at a median of about 69,000 records. One extra pre-committed question takes the design-based median from 1.47 to 1.14. For a single tree the adaptive optimum is trivially "administer the rule". The practically relevant gap is therefore the price of three things at once: strictly design-based inference, a cap exactly equal to the depth, and one estimand fixed in advance. The paper says each of these, but the title, abstract and introduction frame the contribution more broadly than the evidence supports. The per-question advantage of about 1.39 is the more robust practical finding and is under-emphasised.

3. [major] **The "real-data" analysis is oracle computation at unweighted, smoothed empirical laws, on a narrow and partly censored set of rules.**
   - (a) BRFSS is a complex survey. The analysis ignores weights, stratification and raking, uses a Kaggle-derived extract, and binarises all items. Two of the datasets (Spambase, Ionosphere) and WDBC are not questionnaires at all.
   - (b) Headline medians rest on few rules: six runs per cap in Table 1, three seeds. The medians 1.47/1.14/1.02 are conditional on "rules with a gain" that were "computed".
   - (c) Non-computation is informative. The solver stops at more than 13 items, m ≤ 12 and b ≤ 6 for adaptive classes. Those are exactly the wide or deep rules where the price is largest: 2.38 at K = 13, certified only as at most 2.20–3.97 beyond, with uninformative brackets [1.14, 17.4]. The conclusion that trained rules are "far from the worst case and easy to fix" is therefore partly a consequence of small item pools (twelve items) and shallow trees. Ratios visibly increase with K and b, and practical trees are often deeper.
   - (d) Sensitivity to the 1% uniform smoothing mass is reported only for the b = 3 forest tasks, as far as I can find, not for the screening trees that carry the headline numbers.
   - (e) The bootstrap covers only target-law sampling. The paper acknowledges that rule-training variability, the dominant source, is represented by three seeds.

4. [major] **Presentation.** The paper is a 68-page monograph squeezed into eight pages. The abstract contains roughly fifteen numerical claims and several nested qualifications. Theorem 2 has three parts with different constructions. Theorem 4 has a five-part appendix version, of which the main text keeps three. Section 6 reports dozens of ratios over differently defined subsets (38 runs, 52 rules, 18 trees, 17 runs, 12 trees). A reader cannot tell from the main text which numbers are certified optima, which are upper bounds, and which condition on "a gain". The key practical object, the estimator and its standard error, gets one paragraph. For an ICML audience, the feature-acquisition and model-evaluation framing is thin relative to the survey-design content.

5. [minor] **Stylised assumptions beyond those in Scope.**
   - Labels are free, observed before any question, and iid. When the outcome is on the frame or in a registry, the first thing a survey statistician would do is stratify the selection of records by label, with Neyman allocation. Only label-dependent form probabilities are examined (Prop. E.2, at most 0.5%).
   - Every feature is defined for every record. Real skip logic creates structurally inapplicable items, which is exactly the address structure, so the worst case may be more natural than the experiments suggest.
   - There is no item or unit nonresponse and no mode effect, apart from one illustrative flip model.

6. [minor] **Oracle nature of W.** Both the form probabilities and the augmentation (centring at c = Δ(P)) are tuned to P, whereas branching needs no tuning. This asymmetry is the right comparison asymptotically. At realistic sizes the all-in pilot price (1.53–1.93 at N = 4,000) is the relevant number. It appears in the abstract, but only for one N and one pilot fraction in the main text. A multi-wave design in the spirit of McIsaac–Cook or Chen–Lumley is mentioned and not evaluated.

7. [minor] **Inference details are ad hoc.** The EM intervals use a delete-a-group jackknife with eight groups. Regression imputation uses a "naive" standard error. Multiple imputation uses ten hot-deck imputations. Coverage of the design-based intervals dips to 0.87 for one tree (skewed inverse-probability scores) without discussion. Monte Carlo sizes of 100–400 replications give a coverage standard error of about 0.011–0.02.

8. [minor] **Finite-sample statements are loose.** The minimax bracket carries a factor of 104, so "exactly attained" is a first-order statement in n. The exact simulation is finite-sample but uses a random number of records, or a Binomial number of usable ones.

9. [minor] **Verification burden.** I could not check Theorem 2(b) (the pointer-tree potential argument in D.1), Theorem E.5(c)–(e), or solver correctness. The manuscript discloses that a generative model took part in deriving and checking proofs. That is permitted, but with a 55-page appendix it raises the value of an independent check of those parts.

**Soundness** (1-4): 3 — Every proof I spot-checked is correct and the claims are carefully qualified. The empirical conclusions rest on oracle constants at unweighted empirical laws, with few rules and informative non-computation, and a sizeable part of the appendix is unverified.

**Presentation** (1-4): 2 — Precise and honest but severely over-compressed. The abstract and Section 6 are hard to parse and the main text depends on the appendix for almost everything.

**Significance** (1-4): 2 — A definitive answer to a well-posed but narrow question. The paper's own evidence shows the practical price is small and removable by classical means (one extra item, a working model).

**Originality** (1-4): 3 — The cross-design-space comparison, the extra-question, round and mean-budget refinements and the model theorem are new. The headline bound combines folklore with the addressing function and classical efficiency theory.

**Key Questions for Authors**

1. **Wider and deeper rules.** What happens at b = 8–10 and item pools of 50 or more, with K − b much larger than 3? Can the path-set upper bound together with the 1/ρ² lower bound, or a restricted-menu dual certificate, give informative brackets there? Please also show the trend of the ratio and of the benefit of c extra questions against K − b. If the price stays below about 2 and c = 1–2 still removes it, my concern in 3(c) goes away and significance rises. If it grows quickly, the paper's practical message needs to change, though the theory would then matter more.
2. **Complex-survey realism.** Do the BRFSS conclusions survive using the survey weights to define P, and allowing label-stratified selection of records with Neyman allocation for both classes? A stable ratio would substantially strengthen the real-data section. A material change would mean the current numbers describe an artificial population.
3. **Design-based versus model-based.** Given EM-on-forms at 1.00–1.07 up to n = 8,000, is the correct reading that pre-commitment costs essentially nothing for audits of ordinary size unless the analyst refuses a working model? Can you characterise, even heuristically through the misspecification bias in Table 24, the n beyond which the design-based price is the operative one? A clear decision rule would raise my significance score.
4. **Smoothing and conditioning.** Please report the screening-tree ratios at α ∈ {0.1%, 1%, 5%}, and the unconditional distribution of the ratio over all trained rules, including trivial ones and with bounds for those not computed, next to the "with a gain" medians. If the headline numbers are robust, weakness 3(b),(d) is resolved.
5. **Structurally missing items.** With filter questions the follow-up items are undefined off-path, so fixed forms waste questions by construction. Does your framework cover this, for example as a larger-alphabet case with an "inapplicable" level, and is the address bound then the typical rather than the worst case? A positive answer would make the theory considerably more relevant to actual questionnaires.

**Limitations**

Yes, largely. The Scope and "What the constants mean" paragraphs are unusually candid about the single known target, cap = depth, free labels, order effects, the oracle and asymptotic nature of W, unweighted populations and solver scale. Three additions would help:

- State explicitly that non-computed rules are systematically the widest ones, so the reported ranges are censored.
- Note that label-stratified selection of records and survey weights are not handled.
- Discuss structurally inapplicable items and nonresponse that differs between paper forms and adaptive administration.

**Overall Recommendation**: 4 — Weak accept

This is a low 4. The work is technically solid and unusually thorough, and it settles a clean question, but its novelty over classical theory is moderate, its practical price is small by its own evidence, and the main text is over-compressed.

**Confidence**: 4

I am expert in the missing-data, efficiency and survey-design aspects and checked the corresponding proofs. I did not verify the pointer-tree round lower bound, Theorem E.5(c)–(e) or the solver.

**What would move you up one point**

- Restructure the main text around fewer results (Theorem 1, the extra-question and round refinements, Theorem 4, one experiment table), with a readable abstract and a clear statement of which numbers are certified, which are bounds, and which are conditional.
- Add evidence at realistic scale, with deeper trees and larger item pools, using certified brackets where exact optima are unavailable, and report the unconditional distribution over rules.
- Give a survey-weighted, label-stratified version of the BRFSS analysis, plus the smoothing sensitivity for the screening trees.
- Add a short, explicit decision rule for practitioners on when design-based forms, model-based forms, extra questions or branching is the right choice, as a function of n and of whether records or questions are scarce.

These are realistic for a camera-ready or a resubmission. Moving to 6 is not realistic for this contribution.
