"""Round-4 diagnostic (R2, Table 7 vs Tables 9/10): which items do the trees of the shift study (shift_mi_v14.py)
split on? Reproduces the tree construction of shift_mi_v14.setup (seed 20261108, <= 20,000 source training records,
min_samples_leaf 50, balanced classes). Usage: python3 -I diag_shift_tree_items.py <code_dir> <inputs_v12_dir>"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, sys.argv[1])
import budget_trees as bt
from sklearn.tree import DecisionTreeClassifier

root = sys.argv[2]
X, y, names, sex = bt.load('BRFSS', root)
df = pd.read_csv(Path(root) / 'cdc_diabetes.csv')
for shift in ['sex', 'education', 'costbar', 'physhlth']:
    for b in [4, 5]:
        rng = np.random.default_rng(20261108)
        if shift == 'sex': src = np.flatnonzero(sex == 0)
        elif shift == 'education': src = np.flatnonzero(df.Education.to_numpy() == 6)
        elif shift == 'costbar': src = np.flatnonzero(df.NoDocbcCost.to_numpy() == 0)
        else: src = np.flatnonzero(df.PhysHlth.to_numpy() == 0)
        src = rng.permutation(src); tr = src[:min(20000, len(src) // 2)]
        clf = DecisionTreeClassifier(max_depth=b, min_samples_leaf=50, class_weight='balanced', random_state=20261108).fit(X[tr], y[tr])
        used = sorted(set(int(f) for f in clf.tree_.feature if f >= 0))
        print(shift, b, 'split items', len(used), used, 'leaves', clf.get_n_leaves())
