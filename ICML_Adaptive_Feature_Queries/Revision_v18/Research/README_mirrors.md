# Data mirrors used for the v13 computations (no individual records are redistributed)

| Dataset | Source used here | Verification |
| --- | --- | --- |
| Spambase (UCI 94) | PMLB `datasets/spambase/spambase.tsv.gz` via `https://media.githubusercontent.com/media/EpistasisLab/pmlb/master/datasets/spambase/spambase.tsv.gz` (Git LFS; sha256 735e8d43f7ee78ac54ca17404510e95f4c8b364a721e4d9532a1b3221ed70961), written to `spambase/spambase.data` in UCI order (57 features + label) | reproduces stored v12 task `Spambase_20261108_6` to 9 decimals |
| Ionosphere (UCI 52) | PMLB `datasets/ionosphere/ionosphere.tsv.gz` (same host; target 1 -> 'g', 0 -> 'b'), written to `ionosphere/ionosphere.data` | reproduces stored v12 task `Ionosphere_20261108_6` to 9 decimals |
| WDBC | `sklearn.datasets.load_breast_cancer` | reproduces stored v12 task `WDBC_20261108_6` to 9 decimals |
| CDC diabetes health indicators (BRFSS 2015, 253,680 rows) | Git LFS object of `diabetes_binary_health_indicators_BRFSS2015.csv` (sha256 19f367e3e3350768f0c144c5d73ee5b355f67a57eaaa86ca7bd8aec594d8b1d0, 22,738,154 bytes), fetched from `media.githubusercontent.com/media/Vivektheprogrammer/ml_diabetes_risk_prediction/86e3bb713c16544f7bd2b02fae06002647a4f943/...`; the same object is referenced by an independent repository (Roaa-ElEmam/Diabetes-Health-Indicator) | reproduces stored v12 run `BRFSS_b3_iid_0` exactly (identical row order) |
| Thyroid (UCI 102, ann-train/ann-test) | `raw.githubusercontent.com/mikeizbicki/datasets/master/csv/uci/ann-{train,test}.data` (sha256 3da53a15..., c649ea19...), identical bytes at `jeffheaton/proben1/master/thyroid/` | 3,772 + 3,428 rows, classes 93/191/3488 and 73/177/3178; reproduces stored v12 run `Thyroid_b3_iid_0` exactly |

PISA 2012 (NCES) was not re-downloaded; the PISA results are unchanged from v11/v12.
