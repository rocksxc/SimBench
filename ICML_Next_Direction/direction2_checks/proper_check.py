# Offline effect check for candidate 3: are distribution-comparison metrics computed against the votes of a
# small panel "proper"?  Data: ChaosNLI (100 votes per item, 9 models with logits).
import numpy as np, realdata as rd
from scipy.special import softmax

def tv(p, q): return 0.5 * np.abs(p - q).sum(-1)
def jsd(p, q):
    m = 0.5 * (p + q)
    def kl(a, b):
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(a > 0, a * np.log2(a / b), 0.0).sum(-1)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)
def ce(p, q): return -(p * np.log(np.clip(q, 1e-12, 1))).sum(-1)
def brier(p, q): return ((p - q) ** 2).sum(-1)
METRICS = {"TV": tv, "JSD": jsd, "CE": ce, "Brier": brier}

def panels(votes, n, R, rng):
    return np.stack([rd.subsample_votes(votes, n, rng) / n for _ in range(R)])      # R x M x K

rng = np.random.default_rng(0)
for name in ["chaosnli_snli", "chaosnli_mnli_m", "chaosnli_alphanli"]:
    votes, preds, models, extra = rd.load(name)
    P = votes / votes.sum(1, keepdims=True); M, K = P.shape
    z = np.load(f"{rd.DATA}/chaosnli/{name}_model_predictions.npz", allow_pickle=True); logits = z["logits"]
    print(f"== {name}: {M} items, {K} classes")
    emp = {n: panels(votes, n, 40, rng) for n in (3, 5, 10)}
    # (a) the oracle (the 100-vote distribution itself) against sharpened versions of itself
    cands = {"oracle p": P, "p^2 (sharpened)": P ** 2 / (P ** 2).sum(1, keepdims=True), "p^4": P ** 4 / (P ** 4).sum(1, keepdims=True),
             "one-hot argmax p": np.eye(K)[P.argmax(1)]}
    for n in (3, 5, 10):
        cands[f"p rounded to 1/{n}"] = None
    print("  (a) mean score (lower is better) of the oracle and of sharpened oracles")
    for met in ("TV", "JSD", "Brier"):
        row = []
        for n in (3, 5, 10, 100):
            tgt = emp[n] if n < 100 else P[None]
            sc = {k: METRICS[met](tgt, v[None]).mean() for k, v in cands.items() if v is not None}
            best = min(sc, key=sc.get)
            row.append(f"n={n}: oracle {sc['oracle p']:.3f}, one-hot {sc['one-hot argmax p']:.3f}, p^2 {sc['p^2 (sharpened)']:.3f}, p^4 {sc['p^4']:.3f} -> best: {best}")
        print(f"    {met:5s} " + " | ".join(row))
    # (b) real models: which temperature does each metric prefer, with n votes and with 100 votes?
    Ts = np.array([0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0])
    print("  (b) temperature preferred by each metric (argmin over a grid), per model: n=3 / n=5 / n=10 / n=100")
    for met in ("TV", "JSD", "CE", "Brier"):
        out = []
        for mi, m in enumerate(models):
            best = []
            for n in (3, 5, 10, 100):
                tgt = emp[n] if n < 100 else P[None]
                sc = [METRICS[met](tgt, softmax(logits[mi] / T, axis=1)[None]).mean() for T in Ts]
                best.append(Ts[int(np.argmin(sc))])
            out.append(f"{m[:10]}: " + "/".join(f"{b:g}" for b in best))
        print(f"    {met:5s} " + "; ".join(out[:5]))
    # (c) ranking of (model, temperature=1) versus (model, hard argmax): does the n-vote metric prefer hard labels?
    print("  (c) share of the 9 models for which the hard (one-hot) version scores better than the soft version")
    for met in ("TV", "JSD", "Brier"):
        row = []
        for n in (3, 5, 10, 100):
            tgt = emp[n] if n < 100 else P[None]; c = 0
            for mi in range(len(models)):
                soft = softmax(logits[mi], axis=1); hard = np.eye(K)[soft.argmax(1)]
                c += METRICS[met](tgt, hard[None]).mean() < METRICS[met](tgt, soft[None]).mean()
            row.append(f"n={n}: {c}/9")
        print(f"    {met:5s} " + ", ".join(row))
