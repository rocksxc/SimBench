# How much does the size of the annotator panel change measured accuracy on real votes?  ChaosNLI, 100 votes per item.
import numpy as np, realdata as rd, fewannot as fa
from scipy.stats import binom
for name in ["chaosnli_snli", "chaosnli_mnli_m", "chaosnli_alphanli"]:
    votes, preds, models, _ = rd.load(name)
    nf = votes.sum(1)
    print(name, "items", len(nf))
    for mi, m in enumerate(models):
        Xf = rd.agree(votes, preds[mi]); pi = Xf / nf
        A = {k: fa.panel_agreement(Xf, nf, k).mean() for k in (1, 3, 5, 9, 99)}
        out = []
        for n in (3, 5):   # treating the 100-vote shares as population shares
            e = np.where(pi > 0.5, binom.cdf(n // 2, n, pi), binom.sf(n // 2, n, pi)); e[pi == 0.5] = 0
            out.append((e.mean(), (e * (pi > 0.5)).sum() / e.sum()))
        print(f"  {m:15s} A1 {A[1]:.3f} A3 {A[3]:.3f} A5 {A[5]:.3f} A9 {A[9]:.3f} A99 {A[99]:.3f} | P(E3) {out[0][0]:.3f} a3 {out[0][1]:.3f} | P(E5) {out[1][0]:.3f} a5 {out[1][1]:.3f}")
    if votes.shape[1] == 2:
        p = votes[:, 0] / nf
        sub = {n: float(np.mean([np.maximum(x := np.random.default_rng(s).hypergeometric(votes[:, 0], votes[:, 1], n), n - x).mean() / n for s in range(50)]).round(4)) for n in (3, 5, 9)}
        print("  ceiling E max(p,1-p): plug-in with 100 votes", np.maximum(p, 1 - p).mean().round(4), "; plug-in with n votes", sub)
