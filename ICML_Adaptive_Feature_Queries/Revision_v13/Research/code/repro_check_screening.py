"""Reproduce stored v12 budget_trees runs from mirrored inputs (BRFSS Kaggle/LFS mirror, thyroid GitHub mirrors)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from budget_trees import run
root = sys.argv[1]; stored = Path(sys.argv[2])
for ds, b, shift, s in [('Thyroid', 3, False, 0), ('BRFSS', 3, False, 0)]:
    r = run(ds, root, b, 20261108 + s, shift)
    st = json.load(open(stored / f'{ds}_b{b}_{"shift" if shift else "iid"}_{s}.json'))
    keys = ['accuracy', 'delta', 'fixed_oracle_M', 'fixed_fit_M', 'Gamma_P', 'N_P', 'n_target']
    print(ds, b, {k: (round(r[k], 9), round(st[k], 9)) for k in keys}, flush=True)
