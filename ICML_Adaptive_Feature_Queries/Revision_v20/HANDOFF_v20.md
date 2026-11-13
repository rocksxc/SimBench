# Handoff — v20 (round 10) of "The Statistical Value of Adaptive Feature Queries"

Target venue: ICML 2027 (not submitted). This folder is the complete v20 working state. Earlier snapshots are in `../Revision_v13` ... `../Revision_v19` and are unchanged.

## Status of the user's loop
- Standing instruction: keep revising until three independently simulated ICML reviewers each give at least 4 (Weak accept); before each revision round run a web-search novelty check, and abandon the direction if prior work leaves only a narrow niche; report after each round and wait for the user before starting the next.
- Round 10 is finished and reported: novelty gate PASS; scores R1 = 3 (borderline), R2 = 4, R3 = 3. The goal is not met. Round 11 has not been started.
- Ten-round history (R1/R2/R3): 3/3/3, 3/4/4, 4/4/3, 3/3/3, 4/4/3, 3/3/3, 3/4/3, 4/4/3, 3/4/3, 3/4/3. Three 4s have never occurred.

## Where the loop stands
- No reviewer has found an error in a proof in rounds 8-10; in round 10 R1 checked all theorems and appendix proofs line by line.
- The scores have stayed in {3, 4} for seven rounds without a trend. Each round's additions were accepted as correct and did not change the assessment of significance: one known low-degree functional, free labels, a hard cap equal to the rule's depth, an exponential worst case that trained rules do not show (1.0-2.4), theory that does not predict the computed ratios.
- Adding results to the body costs presentation: round 9 (rewrite, fewer results) had Presentation 3/3/2; round 10 (one more theorem part, constant and table) has 2/2/2.
- What the reviewers now ask for is of two kinds. (i) Hard theory that may not exist in the form requested: a tight r-round theorem; a quantitative dependence theorem covering laws with label-feature association and feature couplings; an instance-level characterisation tight up to constants (R1). (ii) A different empirical question from the one the paper asks: what happens when the audit cap is larger than the rule's depth, when the design must serve many rules, at m in the tens, with weights, in a real audit (R2, R3).

## Options for round 11 (full lists in Reviews/README.md)
1. Cap versus depth (asked by all three in round 10; feasible with the existing solver). For the real rules, compute W_fixed/W_branch, and both relative to complete records, as the audit cap grows from the rule's depth b to the number of items K; with cap above the depth, branching is no longer "administer the rule" but a genuine design problem (R2's and R3's "non-trivial adaptive optimum"). On the theory side, a resource-augmentation statement: fixed forms with cap b + c against trees with cap b (the path sets of a depth-b tree fit into forms of size b + c in fewer guesses), and the mean-budget bound m/b for general targets. This would say whether the gap is a knife-edge of cap = depth.
2. Multi-rule designs (R2, R3): joint optimal designs for J rules (all trees of a forest; candidate rules) for forms and for branching; how the price scales with J between the single-rule optimum and uniform forms.
3. Scale (R2, R3): the path-set program (Proposition E.6) as a certified upper bound with the bracket's lower end for the five uncomputed rules and for trees on all 21 BRFSS variables or 57 Spambase features at b up to 8.
4. Fewer results in the body (all three; Presentation 2): Theorems 1 and 2 plus either the computation or the model section; move Theorem 4(c)-(e) to the appendix; one table and one figure per experimental question; stable denominators.
5. Change of venue or direction. R2 and R3 again say that a statistics or survey-methodology journal is the natural home; R1 calls the manuscript a compressed journal paper. Seven rounds without a trend suggest that the formulation, not the execution, sets the score at an ML conference. Under the user's rule (abandon if only a narrow direction remains) this is a decision for the user: the novelty gate has passed every round, so the narrowness is in the setting, not in pre-emption.

## What changed from v19 to v20
- Theorem 4 has a new part (b): features independent given the label. The information of every interview is determined by its label-specific inclusion probabilities; with label-dependent designs forms, r-round and branching interviews have the same closed-form constant; without the label forms are within a factor two (nearly attained in an example found by the independent checker); at balanced product laws the pairwise model has no gap for any contrast. Old parts (b), (c), (d) are now (c), (d), (e).
- `fill_v20.py`: closed-form conditional-independence constants for 60 rules; optimal forms for ten runs that v19 had not finished; brackets for the five rules with more than 13 items.
- `misspec_v20.py`: pair-covering comparator and pair coverage for every design; the appendix states the classical identification condition.
- The audit estimator is called an early-stopped EM estimate everywhere; the bias statements are reconciled.
- The independent check before the reviews corrected an overstatement ("no gap" under conditional independence holds only with label-dependent forms) and stale part labels (ROUND_LOG_v20.md).

## Not completed (stated as such in the paper unless noted)
- No quantitative weak-dependence theorem; no tight rounds result; no instance-level characterisation.
- Five rules with more than 13 items have only a bracket; the pairwise-model ratio exists only for rules with at most ten items.
- The simulated audits use the early-stopped EM estimate, not maximum likelihood; no intermediate regularised model; no model selection from the capped records.
- No survey weights; no real audit; no non-identifiable targets; exact adaptive designs only for m <= 12, b <= 6 and m = 20 at b = 3; the cap always equals the rule's depth.
- Script file names appear in the text of Appendix E.2 (R1, R2, R3 noted them); Table 2 columns "two rounds" and "bracket" are tight; a blank block on page 3 (float placement).
- Author verification: every row of `Manuscript/AUTHOR_VERIFICATION.md` is "Not confirmed". References added in rounds 3-10 were entered from memory or search results; R1 could not verify three 2026 references from memory (Li et al.; Lau & Scarlett; Aronow & Lopatto).

## Pitfalls
- At most four solver processes on this four-core machine, with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1`. Start long jobs with `nohup setsid`, one result file per task, drivers that skip existing files; order tasks by cost.
- Result files can arrive after the tables were generated: rerun `v20_tables.py` and rebuild immediately before a freeze, and check the counts in the text (the round-10 checker caught a draft one regeneration behind).
- After relabelling parts of a theorem, grep the proofs, table captions in `v20_tables.py` and the appendix paragraphs for the old letters.
- Statements about the conditional-independence result must say whether the design may use the label: no gap with label-dependent forms, a factor up to two without.
- EM on expected counts is not a reliable way to find a pseudo-true law (use `misspec_v20.pseudo_true`: several starts, expected-score stopping rule, boundary flag).
- `rules_v19.py` and `fill_v20.py` optimise forms over the rule's own items only (an upper bound on the optimum over all variables); Spambase uses all 57 binarized features and 2,300 training records.
- A foreground `sleep` followed by other commands is blocked by the harness; wait with a background `until ...; do sleep 20; done` command.
- The main text ends exactly at the bottom of page 8; any added line needs a cut (check that "Impact Statement" is the first text on page 9 or on page 8).
- arxiv.org, alphaxiv.org and bls.gov are not reachable from the sandbox.
- Save reviews verbatim. Do not invent reviewer scores, author verification, experiments or references. Simulated reviews are not real ICML feedback.

## Build
`cd Research/code && python3 v20_tables.py && python3 v20_rounds_figure.py`, then in `Manuscript/`: `pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper`. The packaged `Manuscript/paper.pdf` (md5 768324771e21134dcea00ce9cfa83e17, 65 pages) is the file the round-10 reviewers read.
