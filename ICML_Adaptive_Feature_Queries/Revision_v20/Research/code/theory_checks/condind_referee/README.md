Scripts written by the independent checker of round 10 (Theorem 4(b) of v20 and the new computations). Kept as
written, except that the absolute working directory was replaced by the placeholder SCRATCH (the directory that
held `v20/Research/code`).
- ref_common.py, test_b_theorem.py, test_b_more.py: brute-force information matrices for forms, trees and r-round
  interviews (label-blind and label-dependent) against the formula of part (b); optimisation over all forms against
  the closed forms; mixtures of trees against the label-dependent optimum.
- test_gap_example.py: a law in the conditional-independence model (one feature a noisy copy of the label) at which
  label-blind forms need about 2(b-1)/b times the records of a label-blind tree, so the factor two of (b)(ii) is
  nearly attained.
- test_unbalanced.py: the pairwise model at product laws with an unbalanced label (item (iii) needs the balance).
- test_fill.py, test_waterfill2.py, test_pairs.py: fill_v20.py and misspec_v20.pair_coverage against brute force.
