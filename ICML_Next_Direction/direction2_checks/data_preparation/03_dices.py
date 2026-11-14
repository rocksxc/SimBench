"""DICES-350 and DICES-990: per-conversation counts of the rater-level Q_overall rating, item metadata
(expert labels), rater table and a long (item, rater, rating) table.

Usage: python3 -I 03_dices.py /abs/path/to/c1/data
Rating coding everywhere: 0 = "No", 1 = "Unsure", 2 = "Yes"  (Q_overall; "Yes" = rater flagged the
final chatbot response as unsafe on at least one sub-question, verified below).
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd

D = sys.argv[1]
RAW = os.path.join(D, "dices", "raw")
OUT = os.path.join(D, "dices")
CODE = {"No": 0, "Unsure": 1, "Yes": 2}
ver = {}

for n in (350, 990):
    v = {}
    df = pd.read_csv(os.path.join(RAW, f"diverse_safety_adversarial_dialog_{n}.csv"))
    v["rows"] = int(len(df)); v["n_columns"] = int(df.shape[1])
    v["n_items"] = int(df.item_id.nunique()); v["n_raters"] = int(df.rater_id.nunique())
    v["duplicate_item_rater_pairs"] = int(df.duplicated(["item_id", "rater_id"]).sum())
    v["Q_overall_values"] = {str(k): int(c) for k, c in df.Q_overall.value_counts(dropna=False).items()}
    assert set(df.Q_overall.unique()) <= set(CODE)

    # --- how Q_overall relates to the granular questions (all columns starting with Q2..Q6 that are not *_overall)
    gran = [c for c in df.columns if re.match(r"Q[2-6]", c) and not c.endswith("_overall")]
    g = df[gran]
    any_yes = (g == "Yes").any(axis=1)
    any_unsure = (g == "Unsure").any(axis=1)
    derived = np.where(any_yes, "Yes", np.where(any_unsure, "Unsure", "No"))
    v["n_granular_questions"] = len(gran)
    v["Q_overall_equals_rule_anyYes_elif_anyUnsure_else_No_fraction"] = float((derived == df.Q_overall.to_numpy()).mean())

    # --- item-level metadata must be constant within item
    meta_cols = [c for c in ["degree_of_harm", "harm_type", "safety_gold", "safety_gold_reason"] if c in df.columns]
    nun = df.groupby("item_id")[meta_cols + ["context", "response"]].nunique(dropna=False)
    v["item_metadata_constant_within_item"] = {c: bool((nun[c] == 1).all()) for c in nun.columns}
    v["n_items_with_more_than_one_distinct_context_string"] = int((nun["context"] > 1).sum())
    items = df.groupby("item_id")[meta_cols].first()

    # --- counts
    df["rating"] = df.Q_overall.map(CODE).astype(np.int8)
    ct = pd.crosstab(df.item_id, df.Q_overall).reindex(columns=["No", "Unsure", "Yes"], fill_value=0)
    ct.columns = ["n_No", "n_Unsure", "n_Yes"]
    ct.insert(0, "n_raters", ct.sum(axis=1))
    assert (ct.n_raters == df.groupby("item_id").rater_id.nunique()).all()
    v["raters_per_item_min"] = int(ct.n_raters.min()); v["raters_per_item_max"] = int(ct.n_raters.max())
    v["raters_per_item_mean"] = float(ct.n_raters.mean())
    out = ct.join(items)
    out["frac_Yes"] = out.n_Yes / out.n_raters
    cnt3 = out[["n_No", "n_Unsure", "n_Yes"]].to_numpy()
    mx = cnt3.max(1)
    out["crowd_plurality"] = np.array(["No", "Unsure", "Yes"])[cnt3.argmax(1)]
    out["crowd_plurality_tied"] = (cnt3 == mx[:, None]).sum(1) > 1
    v["n_items_tied_plurality"] = int(out.crowd_plurality_tied.sum())
    v["crowd_plurality_distribution"] = {k: int(c) for k, c in out.crowd_plurality.value_counts().items()}
    for c in meta_cols:
        if c != "harm_type" and c != "safety_gold_reason":
            v[f"items_by_{c}"] = {str(k): int(c2) for k, c2 in items[c].value_counts(dropna=False).items()}
    v["n_items_with_degree_of_harm"] = int(items.degree_of_harm.notna().sum())
    v["mean_frac_Yes_by_degree_of_harm"] = {str(k): round(float(x), 4) for k, x in
                                            out.groupby("degree_of_harm", dropna=False).frac_Yes.mean().items()}
    if "safety_gold" in out.columns:
        # polarity of the expert label, established from the data (not assumed)
        v["mean_frac_Yes_by_safety_gold"] = {str(k): round(float(x), 4) for k, x in out.groupby("safety_gold").frac_Yes.mean().items()}
        v["crosstab_safety_gold_x_degree_of_harm"] = {f"{a}|{b}": int(c) for (a, b), c in
                                                      out.groupby(["safety_gold", "degree_of_harm"]).size().items()}
        v["crosstab_safety_gold_x_crowd_plurality"] = {f"{a}|{b}": int(c) for (a, b), c in
                                                       out.groupby(["safety_gold", "crowd_plurality"]).size().items()}
        empty = out.safety_gold_reason.fillna("[]").astype(str).str.strip().isin(["[]", ""])
        v["fraction_empty_safety_gold_reason_by_safety_gold"] = {str(k): round(float(x), 4) for k, x in
                                                                 empty.groupby(out.safety_gold).mean().items()}
        # agreement of the expert label with the crowd under both polarity readings
        no_tie = ~out.crowd_plurality_tied
        cp = out.crowd_plurality[no_tie]
        v["agreement_gold_vs_crowd_if_gold_Yes_means_unsafe"] = float((out.safety_gold[no_tie] == cp).mean())
        v["agreement_gold_vs_crowd_if_gold_Yes_means_safe"] = float(
            (out.safety_gold[no_tie].map({"Yes": "No", "No": "Yes"}) == cp).mean())
    out.reset_index().to_csv(os.path.join(OUT, f"dices{n}_items.csv"), index=False)
    item_ids = out.index.to_numpy().astype(np.int64)
    np.save(os.path.join(OUT, f"dices{n}_counts.npy"), cnt3.astype(np.int16))   # columns [No, Unsure, Yes]

    # --- raters
    rcols = [c for c in df.columns if c.startswith("rater_") and c != "rater_id"] + ["phase"]
    rn = df.groupby("rater_id")[rcols].nunique(dropna=False)
    v["rater_metadata_constant_within_rater"] = {c: bool((rn[c] == 1).all()) for c in rcols}
    v["n_raters_with_inconsistent_metadata"] = int((rn[rcols] > 1).any(axis=1).sum())
    raters = df.groupby("rater_id")[rcols].first()   # first row's value where a rater's metadata varies
    for c in rcols:
        raters[f"{c}_n_distinct"] = rn[c]
    raters["n_items_rated"] = df.groupby("rater_id").size()
    raters["n_Yes"] = df[df.rating == 2].groupby("rater_id").size().reindex(raters.index, fill_value=0)
    readme = open(os.path.join(RAW, f"README_{n}.md")).read()
    removed = [int(s) for s in re.findall(r"'(\d{12,})'", readme.split("removed_raters")[1])]
    raters["in_readme_removed_raters_list"] = raters.index.isin(removed)
    v["readme_removed_raters_listed"] = len(removed)
    v["readme_removed_raters_found_in_csv"] = int(raters.in_readme_removed_raters_list.sum())
    v["items_per_rater_min"] = int(raters.n_items_rated.min()); v["items_per_rater_max"] = int(raters.n_items_rated.max())
    raters.reset_index().to_csv(os.path.join(OUT, f"dices{n}_raters.csv"), index=False)
    rater_ids = raters.index.to_numpy().astype(np.int64)

    # --- long table + dense matrix (items x raters, -1 = not rated)
    long = df[["item_id", "rater_id", "rating"]].sort_values(["item_id", "rater_id"]).reset_index(drop=True)
    long.to_csv(os.path.join(OUT, f"dices{n}_ratings_long.csv"), index=False)
    ii = np.searchsorted(item_ids, long.item_id.to_numpy()); rr = np.searchsorted(rater_ids, long.rater_id.to_numpy())
    mat = -np.ones((len(item_ids), len(rater_ids)), dtype=np.int8)
    mat[ii, rr] = long.rating.to_numpy()
    assert (mat >= 0).sum() == len(long)
    np.savez_compressed(os.path.join(OUT, f"dices{n}_ratings.npz"),
                        item_id=long.item_id.to_numpy().astype(np.int64), rater_id=long.rater_id.to_numpy().astype(np.int64),
                        rating=long.rating.to_numpy().astype(np.int8),
                        item_ids=item_ids, rater_ids=rater_ids, rating_matrix=mat,
                        rating_code=np.array(["No", "Unsure", "Yes"]))
    # round trip
    rebuilt = np.stack([(mat == k).sum(1) for k in range(3)], 1)
    v["counts_rebuilt_from_matrix_equal"] = bool(np.array_equal(rebuilt, cnt3))
    v["matrix_fill_fraction"] = float((mat >= 0).mean())
    ver[f"dices{n}"] = v

json.dump(ver, open(os.path.join(OUT, "verification_dices.json"), "w"), indent=1)
print(json.dumps(ver, indent=1))
