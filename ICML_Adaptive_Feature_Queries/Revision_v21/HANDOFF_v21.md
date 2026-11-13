# Handoff — v21 (round 11) of "The Statistical Value of Adaptive Feature Queries"

Target venue: ICML 2027 (not submitted). This folder is the complete v21 working state. Earlier snapshots are in `../Revision_v13` ... `../Revision_v20` and are unchanged.

## Status of the user's loop
- Standing instruction: keep revising until three independently simulated ICML reviewers each give at least 4 (Weak accept); before each revision round run a web-search novelty check, and abandon the direction if only a narrow direction remains; report after each round and wait for the user before starting the next.
- For round 11 the user asked that the scores stop moving between 3 and 4 and that the round reach three 4s at once. It did not: the single official round gave R1 = 3 (borderline), R2 = 4 (low), R3 = 3. Round 12 has not been started.
- Eleven-round history (R1/R2/R3): 3/3/3, 3/4/4, 4/4/3, 3/3/3, 4/4/3, 3/3/3, 3/4/3, 4/4/3, 3/4/3, 3/4/3, 3/4/3. Three 4s have never occurred.

## What round 11 established
- The outcome 3/4/3 is stable. Official rounds 9, 10 and 11 and the round-11 dress rehearsal are four independent draws per reviewer profile on four different versions; all four gave R1 = 3, R2 = 4, R3 = 3. The versions differ by a rewritten body, a conditional-independence theorem, an extra-questions theorem, a mean-budget statement, a families-of-targets proposition, per-question accounting, further rules and candid pilot results. None of this moved a score.
- No reviewer has found an error in a proof in rounds 8-11.
- The three reviews now agree on the reason, and it is about the problem, not the execution:
  1. the headline theorem is elementary for an ML theory audience (folklore conversion made exact, plus the multiplexer and standard duality);
  2. the gap needs a knife-edge (one known target, cap equal to depth, about 2^{b-1} relevant features) that trained rules do not approach, and the theory is not parameterised by what the experiments show to matter (the number of relevant items beyond the depth);
  3. the practical price is small (1.0-2.4) and removable by one extra question, one follow-up round or a working model, so the actionable message is optimal design of forms, which is classical;
  4. the ML motivation is not convincing (R3 rejects the on-device example: a device can evaluate the tree locally).
- Rehearsal: mock reviews of a draft before the freeze gave the same 3/4/3 and concrete requests; every feasible one was implemented before the official round (see ROUND_LOG_v21.md). The official reviews credit those additions and keep the scores.

## Recommendation (the decision is the user's)
Further rounds of the same kind are very unlikely to produce three 4s. The remaining requests are either new research with uncertain outcome (a theorem tight up to constants in (b, w, c) with w the number of relevant items beyond the depth; a tight two-round bound), or resources this project does not have (a real audit; a use case in which pre-commitment is forced), or a different paper (realistic scale with weights; multi-rule designs). Two coherent ways forward:
1. Keep the work and change the venue. All three profiles say it reads as a statistics or survey-methodology journal paper compressed to eight pages; R2, the profile closest to that audience, has given 4 in nine of ten rounds. A journal version would put Theorems 1-2, the extra-question and mean-budget results, Theorem 4(b) and the all-monomials proposition in full, with the certified solver and the BRFSS study.
2. Keep the venue and change the problem. Under the user's rule (abandon when only a narrow direction remains), the evidence now supports treating this direction as too narrow for ICML: the novelty gate passed in every round, so the narrowness is in the setting, not in pre-emption. A new direction should be chosen offline first, as the rule says. Two leads that came out of the reviews and are not yet done by this paper: (a) an instance-dependent theory of the price in terms of the number of relevant items beyond the depth (R1's question 1 in round 11), which would turn the knife-edge into a parameter; (b) structurally inapplicable items (R2's question 5): in real skip logic follow-up items are undefined off-path, which is exactly the address structure, so the worst case may be the typical case for questionnaires with filter questions.
A round 12 on the present paper should be run only if one of the hard results in (a) is actually proved first.

## What changed from v20 to v21
- New Theorem `thm:augment` (Appendix C.2): forms with c extra questions (simulation factor 2^{b-1-j(c)} < 2^{b+1}/(c+3); address contrast exactly 2^{b-1}/(c+1); products of address blocks 2^{b(1-o(1))} for c = O(b)); part (d): mean budgets for general contrasts.
- New Proposition `prop:family` (Appendix C.3): for all monomials of degree b at once, uniform forms are minimax among all designs with unbiased scores, branching included.
- `capcurve_v21.py`: optimal forms of size b + c on trained rules (52 rules at c = 1), per-question accounting, path-set upper bounds for all rules including the five with more than 13 items.
- Body: Section 2 defines designs and constants; Theorem 2 covers rounds and extra questions with an in-body sketch of the potential argument and an explicit statement of what is not tight; Theorem 4 has three parts; Table 1 has eight columns; Figure 2 is full width with three panels; the constants table, the worked-example drawing and the further-rules table left the body.
- Three independent checks before the freeze (theorem and body; post-rehearsal edits; families proposition) and one dress rehearsal.

## Not completed (stated as such in the paper unless noted)
- No theorem in terms of the number of relevant items beyond the depth; no tight rounds bound; no quantitative weak-dependence theorem.
- Extra-question optima exist for 52 of 60 rules (not for rules with 13 or more items at cap six; one Spambase rule was stopped unfinished).
- No survey weights, no label-stratified selection, no smoothing sensitivity for the screening trees, no end-to-end audit with a pilot-learned design and coverage, no real audit; exact adaptive designs only for m <= 12, b <= 6 and m = 20 at b = 3.
- "accrues round by round" in Section 8 is not established (R1, round 11) and should be reworded if the paper is revised again; appendix numbering does not mirror the main theorems; the abstract is long.
- Author verification: every row of `Manuscript/AUTHOR_VERIFICATION.md` is "Not confirmed". References added in rounds 3-11 were entered from memory or search results.

## Pitfalls
- Memory: `cd.Engine` for rules with 13 or more items at cap six takes several gigabytes; four such workers killed a worker pool and three restarted the container. Run large rules one at a time under `ulimit -v`, lightest first, and compute cheap quantities (path-set program) before expensive ones.
- A K = 11 rule at cap six takes 20-30 minutes for sizes b, b + 1, b + 2; plan for it or lower `--maxsize`.
- Result files can arrive after the tables were generated: rerun `v21_tables.py` and rebuild immediately before a freeze.
- After relabelling parts of a theorem, grep proofs, table captions and appendix paragraphs for the old letters. Main Theorem 4 has parts (a)-(c); the appendix Theorem E.5 has (a)-(e).
- Statements about extra questions: only "at most c + 1" is proved for the worst case (the pointer tree at b = 3, c = 2 leaves 1.8). Statements about families: the upper bound in `prop:family` is for monomials.
- A foreground `sleep` followed by other commands is blocked by the harness; wait with a background `until ...; do sleep 20; done` command.
- The main text ends at the bottom of page 8; any added line needs a cut.
- arxiv.org, alphaxiv.org and bls.gov are not reachable from the sandbox.
- Save reviews verbatim. Do not invent reviewer scores, author verification, experiments or references. A rehearsal is not an official round and must be labelled as such. Simulated reviews are not real ICML feedback.

## Build
`cd Research/code && python3 v21_tables.py && python3 v21_rounds_figure.py`, then in `Manuscript/`: `pdflatex paper && bibtex paper && pdflatex paper && pdflatex paper`. The packaged `Manuscript/paper.pdf` (md5 d6b6fdf4f7a69e438e701a49ba4e92be, 68 pages) is the file the round-11 reviewers read.
