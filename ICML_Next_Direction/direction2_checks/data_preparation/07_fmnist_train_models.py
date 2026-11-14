"""Fashion-MNIST: train a few classifiers of different strength on the 60,000 training images (CPU, fixed
seeds) and save predictions on the 10,000 test images (the items of Fashion-MNIST-H).
These are SELF-TRAINED models, not published ones.

Usage: python -I 07_fmnist_train_models.py /abs/path/to/c1/data
"""
import csv
import gzip
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

D = sys.argv[1]
RAW = os.path.join(D, "fashion_mnist_h", "raw", "fashion-mnist")
OUT = os.path.join(D, "fashion_mnist_h", "predictions", "selftrained")
os.makedirs(OUT, exist_ok=True)
torch.set_num_threads(4)


def read_idx(path):
    with gzip.open(path, "rb") as f:
        b = f.read()
    if int.from_bytes(b[:4], "big") == 2051:
        return np.frombuffer(b, np.uint8, offset=16).reshape(-1, 28, 28)
    return np.frombuffer(b, np.uint8, offset=8)


def prep(x):  # mean/std of the Fashion-MNIST training pixels, computed below
    return (torch.from_numpy(x.copy()).float().div(255.0).unsqueeze(1) - MEAN) / STD


xtr_u8 = read_idx(os.path.join(RAW, "train-images-idx3-ubyte.gz"))
MEAN, STD = float((xtr_u8 / 255.0).mean()), float((xtr_u8 / 255.0).std())
xtr, ytr = prep(xtr_u8), torch.from_numpy(read_idx(os.path.join(RAW, "train-labels-idx1-ubyte.gz")).astype(np.int64))
xte, yte = prep(read_idx(os.path.join(RAW, "t10k-images-idx3-ubyte.gz"))), read_idx(os.path.join(RAW, "t10k-labels-idx1-ubyte.gz")).astype(np.int64)
assert xtr.shape == (60000, 1, 28, 28) and xte.shape == (10000, 1, 28, 28)
counts = np.load(os.path.join(D, "fashion_mnist_h", "fmh_counts.npy"))
hplur = counts.argmax(1)


def cnn():
    return nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                         nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                         nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10))


SPECS = {  # name: (constructor, epochs, batch, max_lr, seed, n_train)
    "logreg_pixels_2k": (lambda: nn.Sequential(nn.Flatten(), nn.Linear(784, 10)), 3, 128, 0.01, 1, 2000),
    "logreg_pixels": (lambda: nn.Sequential(nn.Flatten(), nn.Linear(784, 10)), 5, 128, 0.01, 2, 60000),
    "mlp_1x128": (lambda: nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10)), 5, 128, 0.05, 3, 60000),
    "cnn_small_1ep": (cnn, 1, 128, 0.05, 4, 60000),
    "cnn_small_8ep": (cnn, 8, 128, 0.05, 5, 60000),
}
rows = []
for name, (ctor, epochs, bs, lr, seed, ntr) in SPECS.items():
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed)
    model = ctor()
    opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=epochs * ((ntr + bs - 1) // bs))
    t0 = time.time()
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(ntr, generator=g)   # the first ntr training images are used
        for k in range(0, ntr, bs):
            idx = perm[k:k + bs]
            loss = F.cross_entropy(model(xtr[idx]), ytr[idx])
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step(); sched.step()
    model.eval()
    with torch.inference_mode():
        logits = torch.cat([model(xte[i:i + 1000]) for i in range(0, 10000, 1000)]).double()
    probs = torch.softmax(logits, 1).numpy().astype(np.float32)
    logits = logits.numpy().astype(np.float32)
    pred = probs.argmax(1).astype(np.int16)
    row = dict(model=name, source="self-trained in this project", n_params=sum(p.numel() for p in model.parameters()),
               n_train_images=ntr, epochs=epochs, batch_size=bs, max_lr=lr, seed=seed,
               top1_acc_vs_fashion_mnist_labels=round(float((pred == yte).mean() * 100), 2),
               acc_vs_fmh_plurality=round(float((pred == hplur).mean() * 100), 2),
               train_seconds=round(time.time() - t0, 1), torch_version=torch.__version__)
    print(row, flush=True)
    rows.append(row)
    np.savez_compressed(os.path.join(OUT, f"{name}.npz"), probs=probs, logits=logits, pred=pred)
with open(os.path.join(D, "fashion_mnist_h", "predictions", "selftrained_summary.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
