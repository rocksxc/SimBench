"""Loading of the original CIFAR-10 python batches with a restricted unpickler.

The batch files are pickles; only the numpy reconstruction globals that the
original files need are allowed, anything else raises.
"""
import hashlib
import io
import os
import pickle

import numpy as np

# md5 values hard-coded in torchvision/datasets/cifar.py (class CIFAR10)
OFFICIAL_MD5 = {
    "data_batch_1": "c99cafc152244af753f735de768cd75f",
    "data_batch_2": "d4bba439e000b95fd0a9bffe97cbabec",
    "data_batch_3": "54ebc095f3ab1f0389bbae665268c751",
    "data_batch_4": "634d18415352ddfa80567beed471001a",
    "data_batch_5": "482c414d41f54cd18b22e5b47cb7c3cb",
    "test_batch": "40351d587109b95175f43aff81a1287e",
    "batches.meta": "5ff9c542aee3614f3951f8cda6e48888",
}

CLASSES = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]

_ALLOWED = {
    ("numpy.core.multiarray", "_reconstruct"),
    ("numpy._core.multiarray", "_reconstruct"),
    ("numpy", "ndarray"),
    ("numpy", "dtype"),
}


class _Restricted(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) not in _ALLOWED:
            raise pickle.UnpicklingError(f"global {module}.{name} is not allowed")
        if name == "_reconstruct":
            from numpy._core import multiarray
            return multiarray._reconstruct
        return getattr(np, name)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_batch(path, check_md5=True):
    """Returns (images uint8 [N,32,32,3], labels int64 [N], filenames list[str])."""
    name = os.path.basename(path)
    if check_md5:
        got = md5(path)
        if got != OFFICIAL_MD5[name]:
            raise ValueError(f"{name}: md5 {got} != official {OFFICIAL_MD5[name]}")
    with open(path, "rb") as f:
        d = _Restricted(io.BytesIO(f.read()), encoding="latin1").load()
    x = np.asarray(d["data"], dtype=np.uint8).reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
    y = np.asarray(d["labels"], dtype=np.int64)
    return np.ascontiguousarray(x), y, [str(s) for s in d["filenames"]]


def load_test(batch_dir):
    return load_batch(os.path.join(batch_dir, "test_batch"))


def load_train(batch_dir):
    xs, ys, fs = [], [], []
    for i in range(1, 6):
        x, y, f = load_batch(os.path.join(batch_dir, f"data_batch_{i}"))
        xs.append(x); ys.append(y); fs += f
    return np.concatenate(xs), np.concatenate(ys), fs
