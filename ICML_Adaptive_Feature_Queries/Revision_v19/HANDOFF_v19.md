# Handoff — v19 (round 9) of "The Statistical Value of Adaptive Feature Queries"

Target venue: ICML 2027 (not submitted). This folder is the complete v19 working state. Earlier snapshots are in `../Revision_v13` ... `../Revision_v18` and are unchanged.

## Status of the user's loop
- Standing instruction: keep revising until three independently simulated ICML reviewers each give at least 4 (Weak accept); before each revision round run a web-search novelty check, and abandon the direction if prior work leaves only a narrow niche; report after each round and wait for the user before starting the next.
- Round 9 is finished and reported: novelty gate PASS; scores R1 = 3, R2 = 4 (borderline), R3 = 3. The goal is not met. Round 10 has not been started.
- Nine-round history (R1/R2/R3): 3/3/3, 3/4/4, 4/4/3, 3/3/3, 4/4/3, 3/3/3, 3/4/3, 4/4/3, 3/4/3. Three 4s have never occurred.

## Where the loop stands
- No reviewer has found an error in a proof in rounds 8 and 9. Presentation rose to 3 for R1 and R2 after the body was rewritten; Significance is 2 from all three.
- The scores have moved between 3 and 4 for six rounds without a trend. The reviews of rounds 4-9 agree on why: one known low-degree functional, free labels, a hard cap equal to the rule's depth (so the adaptive optimum for a tree is "administer the rule"), an exponential worst case that trained rules do not show (1.0-2.4 times), and theory that does not predict the computed ratios. R3 has given 3 six times in a row and says each time that rewriting alone cannot move the score.
- R1's round-9 review says explicitly that more experiments would not change its score; it wants a tight rounds result or a quantitative weak-dependence theorem. R1's score for nearly the same content was 4 in round 8 and 3 in round 9, so part of the variation is reviewer draw.

## Options for round 10 (full lists in Reviews/README.md)
1. Theory, cheap and concrete (R1): prove that under the pairwise model at uniform laws W^(2)_fixed = W^(2)_branch for every contrast (R1 sketches the argument: the gradient lives on the label and the item-label pairs; the information block of any tree on these is diagonal with the inclusion probabilities; any inclusion vector is realizable by forms). Then try product laws and a perturbation bound with an explicit coupling condition. This would replace the non-explicit neighbourhood in Theorem 4(b) for k = 2.
2. Theory, hard (R1): a rounds result that is tight for r >= 2 (is 2^{b-2} attained by any contrast at r = 2? the pointer tree gives 1.80 and 3.33 against 2 and 4), or a lower bound for more than logarithmically many rounds in polynomial dimension.
3. Model-based comparison on firmer footing (R2): a pair-covering form design (every pair of the rule's items co-observed with a probability floor) as the model-based comparator; genuine maximum likelihood in the audits instead of early-stopped EM; one intermediate regularised model; one reconciled statement of when the model's bias matters.
4. Censored runs (R2): report the bracket [1/rho^2, N_P] and the path-set upper bound for the 15 further-rule runs that were not computed, and qualify the headline range.
5. A non-trivial adaptive optimum on real rules (R2, R3): caps below the number of items on a path set, joint designs for several rules with branching also optimised, m >= 20 with certified intervals.
6. Change of direction or venue. Six rounds without a trend, with the same significance objection from all three profiles, suggest that the formulation, not the execution, limits the score. Both R2 and R3 say a statistics or survey-methodology journal is the more natural home. This is the user's decision.

## What changed from v18 to v19
- Body rewritten: Theorem 1 (exact simulation, V and W inequalities, sharp example) with its proof in the body; Theorem 2 (rounds); Theorem 3 (constants and bracket); Theorem 4 (models); experiments organised by three questions; a practice paragraph; abstract with one range of numbers.
- New experiments: `rules_v19.py` (further BRFSS outcomes and Spambase, bootstrap ranges, uniform over the rule's items, pairwise-model ratios); `misspec_v19.py` (the pairwise working model at the true law: multi-start maximiser, sandwich variance, which designs have an interior maximiser).
- An independent check before the reviews found that the first version of the misspecification computation (EM with an iteration cap) had not converged and had several limits; it was replaced. It also found a wrong multiplier in the in-body proof of Theorem 1(ii) and a list of overstatements; all were corrected before the freeze (ROUND_LOG_v19.md).
- Removed or corrected claims: "attains V/n"; "benign regime" for the BRFSS fits; "(b+1)^k near independence" without the uniform-law qualifier; "a few percent".

## Not completed (stated as such in the paper unless noted)
- 11 of 45 further-rule runs (caps five and six) were stopped unfinished and 4 rules have more than 13 items; the headline range 1.0-2.38 is over the computed runs (the paper states the counts in Tables 3 and 13, but the abstract does not qualify the range).
- The pairwise range is quoted for different run sets in different places (at most 1.28 in the abstract; 1.02-1.28 in the introduction; 1.02-1.13 for the diabetes trees in Sections 6 and 8). Not yet harmonised.
- In the simulated audits "pairwise maximum likelihood" is EM from the uniform start with early stopping; where the likelihood has no interior maximiser this is not maximum likelihood. The appendix says so; the figure legend and Table 22 still say ML.
- No quantitative weak-dependence theorem; no tight rounds result; no survey weights; no real audit; no non-identifiable targets; exact adaptive designs only for m <= 12, b <= 6 and m = 20 at b = 3.
- Author verification: every row of `Manuscript/AUTHOR_VERIFICATION.md` is "Not confirmed". References added in rounds 3-9 were entered from memory or search results.

## Pitfalls
- At most four solver processes on this four-core machine, with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1`. Start long jobs with `nohup setsid`, one result file per task, drivers that skip existing files.
- A driver's task list is fixed when it starts: heavy cap-six tasks at the front of a pool block the rest. Order tasks by cost or run light and heavy tasks in separate drivers.
- EM on expected counts is not a reliable way to find a pseudo-true law under planned missingness: it converges slowly, stops at the iteration cap silently, and the objective has several stationary points or none in the interior. Use `misspec_v19.pseudo_true` (several starts, expected-score stopping rule, boundary flag).
- `rules_v19.py` optimises forms over the rule's own items only (an upper bound on the optimum over all variables) and uses all 57 binarized Spambase features with 2,300 training records.
- A foreground `sleep` followed by other commands is blocked by the harness; wait with a background `until ...; do sleep 20; done` command, which wakes the session when it exits.
- `model_v17.rule_interview` searches exhaustively and does not finish for more than about 10 items; build known trees explicitly (`dependence_v18.address_tree`).
- `cd.Engine.solve` at strongly unbalanced laws returns values up to 0.6% above the theoretical bound for the address contrast; the dependence table quotes the theoretical value there.
- The main text currently ends on page 8 with a few lines to spare; measure with the position of "Impact Statement" (it must stay on page 8 or at the top of page 9 with no main text after it).
- arxiv.org, alphaxiv.org and bls.gov are not reachable from the sandbox.
- Save reviews verbatim (`extract_review.py` logic: take the reviewer agent's final message). Do not invent reviewer scores, author verification, experiments or references. Simulated reviews are not real ICML feedback.

## Build
`cd Research/code && python3 v19_tables.py && python3 v19_rounds_figure.py`, then in `Manuscript/`: `pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper`. The packaged `Manuscript/paper.pdf` (md5 7fee6462698ae528f087dfd50f745c2e, 63 pages) is the file the round-9 reviewers read.
