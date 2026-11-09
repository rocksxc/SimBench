# The Statistical Value of Adaptive Feature Queries — v11

Anonymous editable manuscript, revised 2026-11-08. No submission has been made. The current PDF has seven pages through the main argument/impact statement, with references and technical appendices following; references begin on page seven. ICML 2026 style is provisional for an intended 2027 submission.

Build with `latexmk -pdf paper.tex`, or pdflatex, bibtex and pdflatex twice. The shipped TeX, bibliography, figures and styles suffice; experiments need not be rerun.

The main empirical sequence is genuine incomplete PISA archival analysis, independent bounded-depth forest updates, then controlled larger-gap and cost/bias diagnostics. `archive_and_forests.tex` supplies the new data definitions, actual-form Brier decomposition, survey uncertainty, imputation specification and full forest grid. The forest branching denominator is a feasible randomized interview menu, not free full-forest predictions. The PISA analysis is secondary work on actual planned-missing data, not an original agency deployment or a prospective adaptivity comparison.

The sharp hard-cap and mixed-budget theory is retained. Active feature count above the cap is necessary but insufficient for a large intrinsic gap. Current results do not claim that typical learned updates realize the exponential worst case.

The computational supplement supplies pinned inputs, `PROTOCOL_v11.json`, all task results, score tables and generators. Run `v11_tables.py --results /path/results --source /path/this/source` after any earlier table generators. Internal source filenames are stable dependency names, not revision-history prose.

See `REVIEWER_2_RESPONSE.md` for the evidence-based response; `AUTHOR_VERIFICATION.md` remains a pending human verification record. No author identity or verification is invented.
