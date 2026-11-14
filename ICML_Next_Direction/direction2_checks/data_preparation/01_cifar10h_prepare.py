"""CIFAR-10H: annotator counts, CIFAR-10 test images/labels, annotator-level long table, order checks.

Usage: python3 -I 01_cifar10h_prepare.py /abs/path/to/c1/data
(-I does not put the script directory on sys.path, so it is added explicitly below.)
"""
import io
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import cifar_io

D = sys.argv[1]
RAW = os.path.join(D, "cifar10h", "raw")
OUT = os.path.join(D, "cifar10h")
ver = {}

# ---- counts
counts = np.load(os.path.join(RAW, "cifar10h", "cifar10h-counts.npy"), allow_pickle=False)
probs = np.load(os.path.join(RAW, "cifar10h", "cifar10h-probs.npy"), allow_pickle=False)
assert counts.shape == (10000, 10) and probs.shape == (10000, 10)
assert np.all(counts == np.round(counts)) and counts.min() >= 0
counts_i = counts.astype(np.int16)
n = counts_i.sum(1)
ver["counts_shape"] = list(counts.shape)
ver["counts_raw_dtype"] = str(counts.dtype)
ver["annotators_per_image_min"] = int(n.min())
ver["annotators_per_image_max"] = int(n.max())
ver["annotators_per_image_mean"] = float(n.mean())
ver["annotators_per_image_median"] = float(np.median(n))
ver["total_votes"] = int(n.sum())
ver["max_abs_diff_probs_vs_counts_normalised"] = float(np.abs(probs - counts / n[:, None]).max())
np.save(os.path.join(OUT, "cifar10h_counts.npy"), counts_i)

# ---- CIFAR-10 test set, original order
bd = os.path.join(RAW, "cifar-10-batches-py")
ver["md5_vs_torchvision"] = {k: cifar_io.md5(os.path.join(bd, k)) == v for k, v in cifar_io.OFFICIAL_MD5.items()}
xt, yt, ft = cifar_io.load_test(bd)
assert xt.shape == (10000, 32, 32, 3) and yt.shape == (10000,)
np.savez_compressed(os.path.join(OUT, "cifar10_test.npz"), images=xt, labels=yt.astype(np.int16),
                    filenames=np.array(ft), classes=np.array(cifar_io.CLASSES))
np.save(os.path.join(OUT, "cifar10_test_labels.npy"), yt.astype(np.int16))
ver["test_label_class_counts"] = np.bincount(yt, minlength=10).tolist()

# ---- order check 1: plurality of human counts vs CIFAR-10 test labels
mx = counts_i.max(1)
ties = (counts_i == mx[:, None]).sum(1) > 1
plur = counts_i.argmax(1)  # first maximum on ties
ver["n_images_with_tied_plurality"] = int(ties.sum())
ver["plurality_agreement_argmax_first_on_ties"] = float((plur == yt).mean())
ver["plurality_agreement_n_correct"] = int((plur == yt).sum())
ver["plurality_agreement_excluding_ties"] = float((plur[~ties] == yt[~ties]).mean())
ver["label_is_among_plurality_set"] = float((counts_i[np.arange(10000), yt] == mx).mean())
ver["human_vote_accuracy_all_votes"] = float(counts_i[np.arange(10000), yt].sum() / n.sum())
# negative control: a shuffled order should give ~10% agreement
rng = np.random.default_rng(0)
ver["plurality_agreement_after_random_permutation_control"] = float((plur[rng.permutation(10000)] == yt).mean())

# ---- annotator-level raw data
with zipfile.ZipFile(os.path.join(RAW, "cifar10h", "cifar10h-raw.zip")) as z:
    raw = pd.read_csv(io.BytesIO(z.read("cifar10h-raw.csv")))
ver["raw_csv_rows"] = int(len(raw))
ver["raw_csv_columns"] = list(raw.columns)
ver["raw_n_annotators"] = int(raw.annotator_id.nunique())
main = raw[raw.is_attn_check == 0].copy()  # NB: the csv column is named cifar10_test_test_idx (README says cifar10_test_set_idx)
ver["raw_rows_non_attention_all_annotators"] = int(len(main))
# The published counts are reproduced exactly only after dropping annotators who got fewer than
# 8 of their 10 attention-check trials right (found empirically; see verification below).
att = raw[raw.is_attn_check == 1].groupby("annotator_id").correct_guess.agg(["sum", "size"])
assert (att["size"] == 10).all()
excluded = sorted(int(a) for a in att.index[att["sum"] < 8])
ver["annotators_excluded_attention_lt_8_of_10"] = excluded
ver["n_annotators_excluded"] = len(excluded)


def build(m):
    r = np.zeros((10000, 10), dtype=np.int64)
    np.add.at(r, (m.cifar10_test_test_idx.to_numpy().astype(np.int64), m.chosen_label.to_numpy().astype(np.int64)), 1)
    return r


ver["counts_rebuilt_from_ALL_annotators_n_cells_differing"] = int((build(main) != counts_i).sum())
main = main[~main.annotator_id.isin(excluded)]
ver["n_annotators_kept"] = int(main.annotator_id.nunique())
idx = main.cifar10_test_test_idx.to_numpy().astype(np.int64)
lab = main.chosen_label.to_numpy().astype(np.int64)
assert idx.min() == 0 and idx.max() == 9999
rebuilt = build(main)
ver["counts_rebuilt_from_kept_annotators_equal_counts_npy"] = bool(np.array_equal(rebuilt, counts_i))
ver["counts_rebuilt_from_kept_annotators_n_cells_differing"] = int((rebuilt != counts_i).sum())
# order check 2: the raw csv carries the true label for each test-set index
ver["raw_true_label_equals_cifar10_test_label_fraction"] = float((main.true_label.to_numpy() == yt[idx]).mean())
ver["raw_duplicate_annotator_image_pairs"] = int(main.duplicated(["annotator_id", "cifar10_test_test_idx"]).sum())
per_ann = main.groupby("annotator_id").size()
ver["raw_images_per_annotator_min_max"] = [int(per_ann.min()), int(per_ann.max())]
order = np.lexsort((main.annotator_id.to_numpy(), idx))
np.savez_compressed(
    os.path.join(OUT, "cifar10h_annotations_long.npz"),
    item_id=idx[order].astype(np.int32),            # index in the CIFAR-10 test set (0..9999)
    rater_id=main.annotator_id.to_numpy()[order].astype(np.int32),
    rating=lab[order].astype(np.int8),               # chosen class 0..9
    reaction_time_ms=main.reaction_time.to_numpy()[order].astype(np.float32),
)
ver["long_table_rows"] = int(len(order))

with open(os.path.join(OUT, "verification_cifar10h.json"), "w") as f:
    json.dump(ver, f, indent=1)
print(json.dumps(ver, indent=1))
