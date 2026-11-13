Scripts written by the independent checker of round 9 (rewritten body and the misspecification paragraph of Appendix F).
They are kept as written, except that the absolute working directory was replaced by the placeholder SCRATCH
(the directory that held `v19/Research/code` and the input data `inputs_v12`).
- test_misspec.py: small examples (3 items + label); a quasi-Newton maximiser with finite-difference derivatives against `misspec_v19.py`.
- test_mc.py, test_mc2.py: Monte Carlo of the actual maximum-likelihood estimator against the sandwich variance.
- real_check.py, real_check2.py: the first (EM) version of the computation on BRFSS trees from several starts; these found the non-convergence and the multiple limits that led to the multi-start maximiser.
