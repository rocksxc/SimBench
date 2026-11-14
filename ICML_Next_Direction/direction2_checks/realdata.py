"""Experiments on benchmarks with many annotators per item: use n votes per item, compare with the full panel."""
import numpy as np, json, sys, os, time
from scipy.optimize import linprog
from scipy.stats import hypergeom, binom
import fewannot as fa
import designs as ds

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
XS, ABOVE, BELOW = fa.make_grid(0.5)

# ------------------------------------------------------------------------------------------- loading
def load(name):
    """returns votes (M,K), preds (m,M), model names, extra dict"""
    if name.startswith("chaosnli_"):
        s = name[len("chaosnli_"):]
        votes = np.load(f"{DATA}/chaosnli/chaosnli_{s}_counts.npy").astype(np.int64)
        z = np.load(f"{DATA}/chaosnli/chaosnli_{s}_model_predictions.npz", allow_pickle=True)
        return votes, z["pred"].astype(int), [str(m) for m in z["models"]], {"probs": z["probs"]}
    if name == "cifar10h":
        votes = np.load(f"{DATA}/cifar10h/cifar10h_counts.npy").astype(np.int64)
        z = np.load(f"{DATA}/cifar10h/predictions/all_models.npz", allow_pickle=True)
        return votes, z["pred"].astype(int), [str(m) for m in z["models"]], {"probs": z["probs"]}
    raise ValueError(name)

# ------------------------------------------------------------------------------------- vote subsampling
def subsample_votes(votes, n, rng):
    """n votes per item without replacement from the item's panel; returns (M,K) counts."""
    M, K = votes.shape
    out = np.zeros_like(votes); rem_tot = votes.sum(1).copy(); rem_n = np.full(M, n)
    for k in range(K - 1):
        x = rng.hypergeometric(votes[:, k], np.maximum(rem_tot - votes[:, k], 0), rem_n)
        x = np.where(rem_n > 0, x, 0)
        out[:, k] = x; rem_tot = rem_tot - votes[:, k]; rem_n = rem_n - x
    out[:, K - 1] = rem_n
    return out

def agree(votes, pred):
    return votes[np.arange(votes.shape[0]), pred]

# --------------------------------------------------------------------------------- general box interval
def ci_box_general(hists, mats, fs, alpha):
    """hists[s]: counts over the cells of stratum s; mats[s]: (cells x grid) matrix of cell probabilities given pi;
    fs[s]: target integrand on the grid.  Simultaneous Clopper-Pearson box over all cells, then two LPs."""
    M = sum(h.sum() for h in hists); ncell = sum(len(h) for h in hists); K = mats[0].shape[1]; S = len(hists)
    A_ub, b_ub = [], []
    for s in range(S):
        lo, hi = fa.clopper_pearson(hists[s], M, alpha / ncell)
        blk = np.zeros((len(hists[s]), S * K)); blk[:, s * K:(s + 1) * K] = mats[s]
        A_ub += [blk, -blk]; b_ub += [hi, -lo]
    A_ub = np.vstack(A_ub); b_ub = np.concatenate(b_ub)
    c = np.concatenate(fs); out = []
    for sg in (1, -1):
        r = linprog(sg * c, A_ub=A_ub, b_ub=b_ub, A_eq=np.ones((1, S * K)), b_eq=[1.0], bounds=(0, None), method="highs")
        out.append(sg * r.fun if r.status == 0 else np.nan)
    return out

def idset_projected(qbar, A, f):
    """Identified set for a count law that may lie slightly outside the model's range (finite item population):
    find the smallest sup-norm slack tau with a compatible law, then bound the target within slack 1.05 tau + 1e-9."""
    J, K = A.shape
    c = np.zeros(K + 1); c[-1] = 1
    A_ub = np.block([[A, -np.ones((J, 1))], [-A, -np.ones((J, 1))]]); b_ub = np.concatenate([qbar, -qbar])
    r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=np.concatenate([np.ones(K), [0]])[None, :], b_eq=[qbar.sum()], bounds=(0, None), method="highs")
    tau = max(r.fun, 0.0) * 1.05 + 1e-9
    A2 = np.vstack([A, -A]); b2 = np.concatenate([qbar + tau, -qbar + tau]); out = []
    for sg in (1, -1):
        r2 = linprog(sg * f, A_ub=A2, b_ub=b2, A_eq=np.ones((1, K)), b_eq=[qbar.sum()], bounds=(0, None), method="highs")
        out.append(sg * r2.fun if r2.status == 0 else np.nan)
    return out[0], out[1], r.fun

# ------------------------------------------------------------------------------------------ main job
def run_model(name, mi, ns=(3, 5, 9, 15), R_cheap=400, R_ci=40, alpha=0.05, seed=0):
    votes, preds, models, extra = load(name)
    M, K = votes.shape; n_full = votes.sum(1); pred = preds[mi]
    Xf = agree(votes, pred)
    Nref = int(n_full.min()); Nref -= (Nref % 2 == 0)
    res = {"dataset": name, "model": models[mi], "M": int(M), "K": int(K), "Nref": Nref,
           "ref": float(fa.panel_agreement(Xf, n_full, Nref).mean()),
           "soft_full": float((Xf / n_full).mean()),
           "full_strict": float((2 * Xf > n_full).mean()),
           "A_m_full": {str(m): float(fa.panel_agreement(Xf, n_full, m).mean()) for m in (1, 3, 5, 9, 15, 25, 45)},
           "by_n": {}}
    f_ref = fa.f_majority(Nref, XS); f_thr = ABOVE.astype(float)
    rng = np.random.default_rng(seed + 1000 * mi)
    for n in ns:
        A = fa.binom_matrix(n, XS)
        plug, a3, soft = [], [], []
        for r in range(R_cheap):
            X = rng.hypergeometric(Xf, n_full - Xf, n)
            plug.append((2 * X > n).mean()); a3.append(fa.panel_agreement(X, n, 3).mean()); soft.append((X / n).mean())
        # expected count law over sub-panels (item population fixed) and its projected identified sets
        qbar = hypergeom.pmf(np.arange(n + 1)[None, :], n_full[:, None], Xf[:, None], n).mean(0)
        id_ref = idset_projected(qbar, A, f_ref); id_thr = idset_projected(qbar, A, f_thr)
        ci_ref, ci_thr = [], []
        for r in range(R_ci):
            X = rng.hypergeometric(Xf, n_full - Xf, n)
            h = np.bincount(X, minlength=n + 1).astype(float)
            ci_ref.append(ci_box_general([h], [A], [f_ref], alpha)); ci_thr.append(ci_box_general([h], [A], [f_thr], alpha))
        ci_ref = np.array(ci_ref); ci_thr = np.array(ci_thr)
        res["by_n"][str(n)] = {
            "plug_mean": float(np.mean(plug)), "plug_sd": float(np.std(plug)),
            "a3_mean": float(np.mean(a3)), "a3_sd": float(np.std(a3)), "soft_mean": float(np.mean(soft)), "soft_sd": float(np.std(soft)),
            "id_ref": [float(id_ref[0]), float(id_ref[1])], "id_thr": [float(id_thr[0]), float(id_thr[1])], "proj_slack": float(id_ref[2]),
            "ci_ref_lo": float(ci_ref[:, 0].mean()), "ci_ref_hi": float(ci_ref[:, 1].mean()),
            "ci_ref_cover": float(np.mean((ci_ref[:, 0] <= res["ref"]) & (res["ref"] <= ci_ref[:, 1]))),
            "ci_thr_lo": float(ci_thr[:, 0].mean()), "ci_thr_hi": float(ci_thr[:, 1].mean()),
            "ci_thr_cover_full": float(np.mean((ci_thr[:, 0] <= res["full_strict"]) & (res["full_strict"] <= ci_thr[:, 1]))),
            "plug_in_ci_ref": float(np.mean((ci_ref[:, 0].mean() <= np.array(plug)) & (np.array(plug) <= ci_ref[:, 1].mean()))),
        }
    return res

def _job(args):
    t = time.time(); r = run_model(*args); r["seconds"] = time.time() - t; return r

if __name__ == "__main__":
    from multiprocessing import Pool
    name = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    votes, preds, models, _ = load(name)
    with Pool(workers) as p:
        out = p.map(_job, [(name, mi) for mi in range(len(models))])
    json.dump(out, open(f"../results/real_{name}.json", "w"), indent=1)
    for r in out:
        print(r["model"], "ref", round(r["ref"], 4), "soft", round(r["soft_full"], 4), {n: (round(v["plug_mean"], 4), [round(x, 4) for x in v["id_ref"]], round(v["ci_ref_lo"], 3), round(v["ci_ref_hi"], 3), v["ci_ref_cover"]) for n, v in r["by_n"].items()})
