"""ChaosNLI: per-item counts of the 100 annotator labels and the model predictions shipped with ChaosNLI.

Usage: python3 -I 04_chaosnli.py /abs/path/to/c1/data
Class order: SNLI / MNLI-m -> [entailment, neutral, contradiction]; alphaNLI -> [hypothesis 1, hypothesis 2].
"""
import csv
import json
import os
import sys

import numpy as np

D = sys.argv[1]
RAW = os.path.join(D, "chaosnli", "raw")
OUT = os.path.join(D, "chaosnli")
ver = {}

SUBSETS = {
    "snli": ("chaosNLI_snli.jsonl", ["e", "n", "c"], 1514, "model_predictions_for_snli_mnli.json"),
    "mnli_m": ("chaosNLI_mnli_m.jsonl", ["e", "n", "c"], 1599, "model_predictions_for_snli_mnli.json"),
    "alphanli": ("chaosNLI_alphanli.jsonl", ["1", "2"], 1532, "model_predictions_for_abdnli.json"),
}
NLI_NAME = {"entailment": 0, "neutral": 1, "contradiction": 2}
# Scoreboard of the official README (easonnie/ChaosNLI): (JSD, KL, old accuracy, new accuracy)
README_SCORES = {
    ("snli", "bert-large"): (0.23, 0.5017, 0.7266, 0.7384), ("snli", "roberta-large"): (0.221, 0.4937, 0.749, 0.7867),
    ("snli", "xlnet-large"): (0.2259, 0.5054, 0.7431, 0.7807),
    ("mnli_m", "bert-large"): (0.3152, 0.8449, 0.6123, 0.5691), ("mnli_m", "roberta-large"): (0.3112, 0.8701, 0.6742, 0.6354),
    ("mnli_m", "xlnet-large"): (0.3116, 0.8818, 0.6742, 0.6185),
    ("alphanli", "bert-large"): (0.3055, 3.7996, 0.6802, 0.6821), ("alphanli", "roberta-large"): (0.2128, 1.3898, 0.8531, 0.8368),
    ("alphanli", "xlnet-large"): (0.2282, 1.8166, 0.814, 0.8133),
}


def softmax(z):
    z = z - z.max(-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(-1, keepdims=True)


def clip_norm(p, eps=1e-15):
    """Same numerical convention as ChaosNLI src/evaluation/tools.py: values below 1e-15 are set to 1e-15, then renormalised."""
    p = np.where(np.abs(p) < eps, eps, p)
    return p / p.sum(-1, keepdims=True)


def kl_nat(p, q):
    return (p * np.log(p / q)).sum(-1)


def js_distance_nat(p, q):
    """Jensen-Shannon distance with natural log (scipy.spatial.distance.jensenshannon default), as in the ChaosNLI scoreboard."""
    m = 0.5 * (p + q)
    return np.sqrt(np.maximum(0.5 * kl_nat(p, m) + 0.5 * kl_nat(q, m), 0))


preds_cache = {}
summary = []
total = 0
for sub, (fn, classes, n_expected, pf) in SUBSETS.items():
    v = {}
    rows = [json.loads(l) for l in open(os.path.join(RAW, fn), encoding="utf-8")]
    v["n_items"] = len(rows); v["n_items_expected"] = n_expected
    assert len(rows) == n_expected
    total += len(rows)
    uids = [r["uid"] for r in rows]
    v["uids_unique"] = len(set(uids)) == len(uids)
    C = len(classes)
    counts = np.array([[r["label_counter"].get(c, 0) for c in classes] for r in rows], dtype=np.int16)
    v["label_counter_keys"] = sorted({k for r in rows for k in r["label_counter"]})
    v["all_label_counter_sum_to_100"] = bool((counts.sum(1) == 100).all())
    v["label_counter_sum_min_max"] = [int(counts.sum(1).min()), int(counts.sum(1).max())]
    v["label_count_field_equals_label_counter"] = bool(all(list(map(int, r["label_count"])) == counts[i].tolist() for i, r in enumerate(rows)))
    v["total_annotations"] = int(counts.sum())
    if C == 3:
        old = np.array([classes.index(r["old_label"]) for r in rows])
        maj = np.array([classes.index(r["majority_label"]) for r in rows])
    else:
        old = np.array([int(r["old_label"]) - 1 for r in rows])
        maj = np.array([int(r["majority_label"]) - 1 for r in rows])
    mx = counts.max(1)
    tied = (counts == mx[:, None]).sum(1) > 1
    v["n_items_tied_plurality"] = int(tied.sum())
    v["majority_label_field_is_a_plurality_class_fraction"] = float((counts[np.arange(len(rows)), maj] == mx).mean())
    v["old_label_equals_majority_label_fraction"] = float((old == maj).mean())
    np.save(os.path.join(OUT, f"chaosnli_{sub}_counts.npy"), counts)
    with open(os.path.join(OUT, f"chaosnli_{sub}_items.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["row", "uid"] + [f"n_{c}" for c in classes] + ["old_label_idx", "majority_label_idx", "plurality_tied", "entropy_base2", "source"]
                   + (["old_labels_5"] if C == 3 else []))
        for i, r in enumerate(rows):
            w.writerow([i, r["uid"]] + counts[i].tolist() + [int(old[i]), int(maj[i]), bool(tied[i]), r["entropy"], r["example"]["source"]]
                       + (["|".join(r["old_labels"])] if C == 3 else []))

    # ---- model predictions
    if pf not in preds_cache:
        preds_cache[pf] = json.load(open(os.path.join(RAW, pf)))
    P = preds_cache[pf]
    models = sorted(P)
    v["models"] = models
    v["n_uids_in_prediction_file_per_model"] = sorted({len(P[m]) for m in models})
    v["items_missing_from_prediction_file"] = int(sum(u not in P[m] for m in models for u in uids))
    logits = np.array([[P[m][u]["logits"] for u in uids] for m in models], dtype=np.float64)   # [M, N, C]
    probs = softmax(logits)
    pred = logits.argmax(-1)
    if C == 3:
        given = np.array([[NLI_NAME[P[m][u]["predicted_label"]] for u in uids] for m in models])
    else:
        given = np.array([[int(P[m][u]["predicted_label"]) - 1 for u in uids] for m in models])
    v["predicted_label_equals_argmax_logits_fraction"] = float((given == pred).mean())
    np.savez_compressed(os.path.join(OUT, f"chaosnli_{sub}_model_predictions.npz"),
                        models=np.array(models), uids=np.array(uids), logits=logits.astype(np.float32),
                        probs=probs.astype(np.float32), pred=pred.astype(np.int8), predicted_label_in_file=given.astype(np.int8),
                        classes=np.array(classes))
    human = clip_norm(counts / counts.sum(1, keepdims=True))
    diffs = []
    for mi, m in enumerate(models):
        row = dict(subset=sub, model=m, n_items=len(rows),
                   acc_old_label=round(float((given[mi] == old).mean()), 4),
                   acc_majority_label=round(float((given[mi] == maj).mean()), 4),
                   jsd=round(float(js_distance_nat(human, clip_norm(probs[mi])).mean()), 4),
                   kl=round(float(kl_nat(human, clip_norm(probs[mi])).mean()), 4))
        ref = README_SCORES.get((sub, m))
        if ref:
            row.update(readme_jsd=ref[0], readme_kl=ref[1], readme_old_acc=ref[2], readme_new_acc=ref[3])
            diffs += [abs(row["jsd"] - ref[0]), abs(row["kl"] - ref[1]), abs(row["acc_old_label"] - ref[2]), abs(row["acc_majority_label"] - ref[3])]
        summary.append(row)
    v["max_abs_diff_vs_readme_scoreboard_over_3_large_models_x_4_metrics"] = float(max(diffs))
    ver[sub] = v

ver["total_items"] = total
ver["total_items_expected"] = 4645
keys = ["subset", "model", "n_items", "acc_old_label", "acc_majority_label", "jsd", "kl", "readme_jsd", "readme_kl", "readme_old_acc", "readme_new_acc"]
with open(os.path.join(OUT, "chaosnli_model_summary.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys, restval="")
    w.writeheader(); w.writerows(summary)
json.dump(ver, open(os.path.join(OUT, "verification_chaosnli.json"), "w"), indent=1)
print(json.dumps(ver, indent=1))
for r in summary:
    print(r)
