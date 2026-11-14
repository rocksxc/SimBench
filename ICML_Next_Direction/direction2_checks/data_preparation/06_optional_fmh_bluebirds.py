"""Optional dataset 4: Fashion-MNIST-H (many annotators per Fashion-MNIST test image) and the
"bluebirds" crowdsourcing set of Welinder et al. (39 annotators x 108 images, binary).

Usage: python3 -I 06_optional_fmh_bluebirds.py /abs/path/to/c1/data
"""
import gzip
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

D = sys.argv[1]
ver = {}

# ------------------------------------------------------------------ Fashion-MNIST-H
RAW = os.path.join(D, "fashion_mnist_h", "raw")
OUT = os.path.join(D, "fashion_mnist_h")
CLASSES = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]
# md5 values listed in the README of zalandoresearch/fashion-mnist
FM_MD5 = {"train-images-idx3-ubyte.gz": "8d4fb7e6c68d591d4c3dfef9ec88bf0d", "train-labels-idx1-ubyte.gz": "25c81989df183df01b3e8a0aad5dffbe",
          "t10k-images-idx3-ubyte.gz": "bef4ecab320f06d8554ea6380940ec79", "t10k-labels-idx1-ubyte.gz": "bb300cfdad3c16e7a12a480ee83cd310"}


def read_idx(path):
    with gzip.open(path, "rb") as f:
        b = f.read()
    magic = int.from_bytes(b[:4], "big")
    if magic == 2051:
        n, r, c = (int.from_bytes(b[4 + 4 * i:8 + 4 * i], "big") for i in range(3))
        return np.frombuffer(b, np.uint8, offset=16).reshape(n, r, c)
    assert magic == 2049
    return np.frombuffer(b, np.uint8, offset=8)


v = {}
fm = os.path.join(RAW, "fashion-mnist")
v["md5_vs_fashion_mnist_readme"] = {k: hashlib.md5(open(os.path.join(fm, k), "rb").read()).hexdigest() == m for k, m in FM_MD5.items()}
xt, yt = read_idx(os.path.join(fm, "t10k-images-idx3-ubyte.gz")), read_idx(os.path.join(fm, "t10k-labels-idx1-ubyte.gz")).astype(np.int64)
assert xt.shape == (10000, 28, 28) and yt.shape == (10000,)
np.savez_compressed(os.path.join(OUT, "fashion_mnist_test.npz"), images=xt, labels=yt.astype(np.int16), classes=np.array(CLASSES))

counts = np.loadtxt(os.path.join(RAW, "fmh", "fmh_counts.csv"), delimiter=",")
assert counts.shape == (10000, 10) and np.all(counts == np.round(counts))
counts = counts.astype(np.int16)
n = counts.sum(1)
v["counts_shape"] = list(counts.shape)
v["annotators_per_image_min"] = int(n.min()); v["annotators_per_image_max"] = int(n.max())
v["annotators_per_image_mean"] = float(n.mean()); v["annotators_per_image_median"] = float(np.median(n))
v["n_images_with_fewer_than_20_annotators"] = int((n < 20).sum())
v["total_votes"] = int(n.sum())
probs = np.loadtxt(os.path.join(RAW, "fmh", "fmh_probs.csv"), delimiter=",")
v["max_abs_diff_probs_csv_vs_counts_normalised"] = float(np.abs(probs - counts / n[:, None]).max())
np.save(os.path.join(OUT, "fmh_counts.npy"), counts)
mx = counts.max(1)
tied = (counts == mx[:, None]).sum(1) > 1
plur = counts.argmax(1)
v["n_images_with_tied_plurality"] = int(tied.sum())
v["plurality_agreement_with_fashion_mnist_test_labels"] = float((plur == yt).mean())
v["plurality_agreement_n_correct"] = int((plur == yt).sum())
v["human_vote_accuracy_all_votes"] = float(counts[np.arange(10000), yt].sum() / n.sum())
v["plurality_agreement_after_random_permutation_control"] = float((plur[np.random.default_rng(0).permutation(10000)] == yt).mean())

raw = pd.read_csv(os.path.join(RAW, "fmh", "fmh_raw.csv"))
v["raw_rows"] = int(len(raw)); v["raw_columns"] = list(raw.columns)
item = raw["Input.image_url"].str.replace(".jpg", "", regex=False).astype(np.int64).to_numpy()
v["raw_categories"] = sorted(raw["Answer.category"].unique().tolist())
lab = raw["Answer.category"].map({c: i for i, c in enumerate(CLASSES)})
assert lab.notna().all()
lab = lab.to_numpy().astype(np.int64)
rater = raw["PseudoWorkerId"].to_numpy().astype(np.int64)
rebuilt = np.zeros((10000, 10), dtype=np.int64)
np.add.at(rebuilt, (item, lab), 1)
v["counts_rebuilt_from_raw_equal_counts_csv"] = bool(np.array_equal(rebuilt, counts))
v["counts_rebuilt_from_raw_n_cells_differing"] = int((rebuilt != counts).sum())
v["raw_n_annotators"] = int(len(np.unique(rater)))
v["raw_duplicate_annotator_image_pairs"] = int(raw.duplicated(["Input.image_url", "PseudoWorkerId"]).sum())
per = pd.Series(rater).value_counts()
v["images_per_annotator_min_median_max"] = [int(per.min()), float(per.median()), int(per.max())]
order = np.lexsort((rater, item))
np.savez_compressed(os.path.join(OUT, "fmh_annotations_long.npz"), item_id=item[order].astype(np.int32),
                    rater_id=rater[order].astype(np.int32), rating=lab[order].astype(np.int8), classes=np.array(CLASSES))
ver["fashion_mnist_h"] = v
json.dump(v, open(os.path.join(OUT, "verification_fmh.json"), "w"), indent=1)

# ------------------------------------------------------------------ bluebirds (Welinder et al. 2010, cubam demo data)
import yaml  # noqa: E402

RAW = os.path.join(D, "bluebirds", "raw")
OUT = os.path.join(D, "bluebirds")
v = {}
gt = yaml.safe_load(open(os.path.join(RAW, "gt.yaml")))
labels = yaml.safe_load(open(os.path.join(RAW, "labels.yaml")))
items = sorted(gt)
raters = sorted(labels)
v["n_items"] = len(items); v["n_raters"] = len(raters)
mat = -np.ones((len(items), len(raters)), dtype=np.int8)
for j, r in enumerate(raters):
    for i, it in enumerate(items):
        if it in labels[r]:
            mat[i, j] = int(bool(labels[r][it]))
v["matrix_fill_fraction"] = float((mat >= 0).mean())
cnt = np.stack([(mat == 0).sum(1), (mat == 1).sum(1)], 1).astype(np.int16)   # columns [False, True]
g = np.array([int(bool(gt[i])) for i in items])
v["raters_per_item_min_max"] = [int(cnt.sum(1).min()), int(cnt.sum(1).max())]
v["ground_truth_true_fraction"] = float(g.mean())
tied = cnt[:, 0] == cnt[:, 1]
v["n_items_tied"] = int(tied.sum())
v["majority_vote_accuracy_vs_gt_excluding_ties"] = float(((cnt[:, 1] > cnt[:, 0]).astype(int)[~tied] == g[~tied]).mean())
v["mean_individual_rater_accuracy_vs_gt"] = float((mat == g[:, None]).mean())
np.savez_compressed(os.path.join(OUT, "bluebirds.npz"), item_ids=np.array(items), rater_ids=np.array(raters),
                    rating_matrix=mat, counts=cnt, ground_truth=g.astype(np.int8), count_columns=np.array(["False", "True"]))
pd.DataFrame({"item_id": items, "n_raters": cnt.sum(1), "n_False": cnt[:, 0], "n_True": cnt[:, 1], "ground_truth": g}).to_csv(
    os.path.join(OUT, "bluebirds_items.csv"), index=False)
ver["bluebirds"] = v
json.dump(v, open(os.path.join(OUT, "verification_bluebirds.json"), "w"), indent=1)
print(json.dumps(ver, indent=1))
