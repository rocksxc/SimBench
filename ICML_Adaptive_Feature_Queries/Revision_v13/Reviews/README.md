# Simulated ICML 2027 reviews — v13 rounds (continues Revision_v12/Reviews/README.md)

Procedure, profiles and scale are unchanged from `Revision_v12/Reviews/README.md` (PyMuPDF packet: cleaned text + 100 dpi page images; three fresh independent agents with `reviewer_prompt_template.md`; ICML 2026 six-point scale; goal: all three >= 4).

## History
| Round | Paper | R1 (theory) | R2 (statistics) | R3 (applied ML) | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | v11 | 3 (conf 4) | 3 (conf 4) | 3 (conf 4) | `Revision_v12/Reviews/round1_v11_*.md` |
| 2 | v12 (`ICML_paper_v12_current.pdf`) | 3 (conf 4); S4/P3/Sig2/O3 | 4 (conf 4); S3/P2/Sig3/O3 | 4 (conf 4); S3/P2/Sig3/O3 | `round2_v12_*.md` (this folder) |

Round-2 "what would move me up one point":
- R1: a two-round lower bound with exponent near b−2 (or a matching upper bound); a rate-matching theory for the approximately identifiable regime; a realistic >2x case with a bracket-driven design decision; M-vs-W fix and trimmed presentation (needed for any accept).
- R2: smoothing-mass and evaluation-sample sensitivity of the exact ratios; a non-toy identifiable target at a meaningful cap above 1.5x and above the order-effect noise floor, or several functionals jointly; honest 25x, one scale for the bracket, trimmed supplement; MST/CAT, optimal split-questionnaire and multiwave two-phase related work.
- R3: realistic scale with a scalable certified computation and a >=2x case predicted by 1/Gamma_P; a finite-sample ML-relevant study with label costs and doubly-robust baselines; streamlined self-contained presentation with a constructions figure and a pruned/quarantined appendix; closing an open theoretical end.

These are simulated reviews by language-model agents, not real ICML feedback. Never report a score that was not actually produced.
