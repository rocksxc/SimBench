# Simulated ICML 2027 reviews — v13 rounds (continues Revision_v12/Reviews/README.md)

Procedure, profiles and scale are unchanged from `Revision_v12/Reviews/README.md` (PyMuPDF packet: cleaned text + 100 dpi page images; three fresh independent agents with `reviewer_prompt_template.md`; ICML 2026 six-point scale; goal: all three >= 4).

## History
| Round | Paper | R1 (theory) | R2 (statistics) | R3 (applied ML) | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | v11 | 3 (conf 4) | 3 (conf 4) | 3 (conf 4) | `Revision_v12/Reviews/round1_v11_*.md` |
| 2 | v12 (`ICML_paper_v12_current.pdf`) | 3 (conf 4); S4/P3/Sig2/O3 | 4 (conf 4); S3/P2/Sig3/O3 | 4 (conf 4); S3/P2/Sig3/O3 | `round2_v12_*.md` (this folder) |
| 3 | v13 (`Manuscript/paper.pdf`, 2026-11-09) | 4 (conf 4); S4/P2/Sig3/O3 | 4 (conf 4); S3/P2/Sig3/O3 | 3 (conf 4); S3/P2/Sig3/O3 | `round3_v13_*.md` (this folder); goal not yet met (R3 = 3) |

Round-2 "what would move me up one point":
- R1: a two-round lower bound with exponent near b−2 (or a matching upper bound); a rate-matching theory for the approximately identifiable regime; a realistic >2x case with a bracket-driven design decision; M-vs-W fix and trimmed presentation (needed for any accept).
- R2: smoothing-mass and evaluation-sample sensitivity of the exact ratios; a non-toy identifiable target at a meaningful cap above 1.5x and above the order-effect noise floor, or several functionals jointly; honest 25x, one scale for the bracket, trimmed supplement; MST/CAT, optimal split-questionnaire and multiwave two-phase related work.
- R3: realistic scale with a scalable certified computation and a >=2x case predicted by 1/Gamma_P; a finite-sample ML-relevant study with label costs and doubly-robust baselines; streamlined self-contained presentation with a constructions figure and a pruned/quarantined appendix; closing an open theoretical end.

Round-3 common points (all three): the appendix is not self-contained (SUSHI/SAPA, "ten binary tasks", "70 controlled tree tasks", "v12", "earlier release", "separate supplementary report" are referenced but never introduced, and the Section 8 position-effect numbers 0.5-1.8 SE rest on them); the main text is too dense (Presentation 2 from all three); realized gains 1-2x are matched by imputation whenever complete source records exist, so the practical regime (no trusted complete reference, labels free, degree <= b contrasts) must be stated up front; exact computations stop at m <= 12 (b=4 cells at m >= 9 left incomplete); the rounds lower bound bites only for b >= 10 while experiments live at b <= 6; the 25x headline is against a straw man.

Round-3 "what would move me up one point":
- R1 (4): self-contained main text (consistent numbering, worked example of V, W, Gamma_P, N_P; remove appendix references to absent experiments); close the polynomial gap in Theorem 3 or exact V_2 numerics on the binary pointer tree at b=3-6; discuss the LDP interactivity literature (Joseph-Mao-Neel-Roth 2019, Joseph-Mao-Roth 2020; Acharya et al.; budgeted learning Lizotte-Madani-Greiner); one experiment at m >= 30; evidence that the gain survives a realistic order-effect model.
- R2 (4): a tightened, reference-computable upper end for Theorem 4 (optimal augmented path-set scores) that tracks "Best" on the screening runs; a realistic shift where imputation from source records fails while the design-based audit stays valid; the round hierarchy in the b <= 6 regime; state held-out sizes and define n0; introduce or remove SUSHI/SAPA; rename "model-assisted" to regression imputation and note the conservative MI variance; compress Section 6.
- R3 (3): self-contained submission (describe or remove SUSHI/SAPA and the ten-binary/70-tree tasks, re-derive the position-effect numbers on in-paper tasks); reframe as a theory of adaptivity gaps with the regime stated in the abstract and drop the 25x headline; one experiment that changes the practical picture (scale demonstration at m >= 20-30 with certified restricted masters, or a realistic shift where imputation fails, or exact optimal two-round constants at b=4-6); readability (constants table, shorter abstract, consistent cross-references, define "binding", "Restr.", "Fix/full").

These are simulated reviews by language-model agents, not real ICML feedback. Never report a score that was not actually produced.
