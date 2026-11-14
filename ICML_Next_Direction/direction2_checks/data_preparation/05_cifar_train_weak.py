"""Train deliberately weak CIFAR-10 classifiers on the 50,000 training images (CPU, fixed seeds) and
save their predictions on the 10,000 test images. These are SELF-TRAINED models, not published ones.

Usage: python -I 05_cifar_train_weak.py /abs/path/to/c1/data
Models:  logreg_pixels      multinomial logistic regression on normalised pixels
         mlp_1x256          one hidden layer of 256 ReLU units
         cnn_small_1ep      2-conv CNN, 1 epoch
         cnn_small_5ep      same architecture, 5 epochs
         cnn_medium_12ep    6-conv CNN with batch norm, random flip/crop, 12 epochs
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import cifar_io

D = sys.argv[1]
ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 else None
RAW = os.path.join(D, "cifar10h", "raw")
OUT = os.path.join(D, "cifar10h", "predictions", "selftrained")
os.makedirs(OUT, exist_ok=True)
torch.set_num_threads(4)
MEAN = torch.tensor([0.4914, 0.4822, 0.4465]).view(1, 3, 1, 1)
STD = torch.tensor([0.2023, 0.1994, 0.2010]).view(1, 3, 1, 1)


def prep(x):
    return (torch.from_numpy(x).permute(0, 3, 1, 2).float().div(255.0) - MEAN) / STD


xtr_u8, ytr_np, _ = cifar_io.load_train(os.path.join(RAW, "cifar-10-batches-py"))
t = np.load(os.path.join(D, "cifar10h", "cifar10_test.npz"), allow_pickle=False)
xtr, ytr = prep(xtr_u8), torch.from_numpy(ytr_np)
xte, yte = prep(t["images"]), t["labels"].astype(np.int64)
assert xtr.shape == (50000, 3, 32, 32) and xte.shape == (10000, 3, 32, 32)
counts = np.load(os.path.join(D, "cifar10h", "cifar10h_counts.npy"))
hplur = counts.argmax(1)


def cnn_small():
    return nn.Sequential(
        nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Linear(64 * 8 * 8, 128), nn.ReLU(), nn.Linear(128, 10))


def cnn_medium():
    def block(i, o):
        return [nn.Conv2d(i, o, 3, padding=1, bias=False), nn.BatchNorm2d(o), nn.ReLU(),
                nn.Conv2d(o, o, 3, padding=1, bias=False), nn.BatchNorm2d(o), nn.ReLU(), nn.MaxPool2d(2)]
    return nn.Sequential(*block(3, 32), *block(32, 64), *block(64, 128),
                         nn.Flatten(), nn.Linear(128 * 4 * 4, 10))


SPECS = {
    # name: (constructor, epochs, batch, lr, weight_decay, augment, seed)
    "logreg_pixels": (lambda: nn.Sequential(nn.Flatten(), nn.Linear(3072, 10)), 10, 256, 0.002, 1e-3, False, 1),
    "mlp_1x256": (lambda: nn.Sequential(nn.Flatten(), nn.Linear(3072, 256), nn.ReLU(), nn.Linear(256, 10)), 10, 128, 0.02, 5e-4, False, 2),
    "cnn_small_1ep": (cnn_small, 1, 128, 0.03, 5e-4, False, 3),
    "cnn_small_5ep": (cnn_small, 5, 128, 0.03, 5e-4, False, 4),
    "cnn_medium_12ep": (cnn_medium, 12, 128, 0.05, 5e-4, True, 5),
}


def augment(xb, g):
    flip = torch.rand(xb.shape[0], generator=g) < 0.5
    xb = torch.where(flip.view(-1, 1, 1, 1), xb.flip(3), xb)
    pad = F.pad(xb, (4, 4, 4, 4), mode="reflect")
    i, j = (int(v) for v in torch.randint(0, 9, (2,), generator=g))
    return pad[:, :, i:i + 32, j:j + 32]


rows = []
for name, (ctor, epochs, bs, lr, wd, aug, seed) in SPECS.items():
    if ONLY and name not in ONLY:
        continue
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed)
    model = ctor()
    opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=wd)
    steps = epochs * ((50000 + bs - 1) // bs)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=steps)
    t0 = time.time()
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(50000, generator=g)
        tot = 0.0
        for k in range(0, 50000, bs):
            idx = perm[k:k + bs]
            xb = xtr[idx]
            if aug:
                xb = augment(xb, g)
            loss = F.cross_entropy(model(xb), ytr[idx])
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step(); sched.step()
            tot += loss.item() * len(idx)
        print(f"{name} epoch {ep + 1}/{epochs} train_loss {tot / 50000:.4f} elapsed {time.time() - t0:.0f}s", flush=True)
    model.eval()
    with torch.inference_mode():
        logits = torch.cat([model(xte[i:i + 1000]) for i in range(0, 10000, 1000)]).double()
        tr_acc = float(np.mean([(model(xtr[i:i + 1000]).argmax(1) == ytr[i:i + 1000]).float().mean().item()
                                for i in range(0, 50000, 1000)]) * 100)
    probs = torch.softmax(logits, 1).numpy().astype(np.float32)
    logits = logits.numpy().astype(np.float32)
    pred = probs.argmax(1).astype(np.int16)
    row = dict(model=name, source="self-trained in this project (weak baseline)",
               n_params=sum(p.numel() for p in model.parameters()), epochs=epochs, batch_size=bs, max_lr=lr,
               weight_decay=wd, augmentation=aug, seed=seed,
               top1_acc_vs_cifar10_labels=round(float((pred == yte).mean() * 100), 2),
               train_acc=round(tr_acc, 2),
               acc_vs_cifar10h_plurality=round(float((pred == hplur).mean() * 100), 2),
               train_seconds=round(time.time() - t0, 1), torch_version=torch.__version__)
    print(row, flush=True)
    np.savez_compressed(os.path.join(OUT, f"{name}.npz"), probs=probs, logits=logits, pred=pred)
    torch.save(model.state_dict(), os.path.join(OUT, f"{name}_state_dict.pt"))
    json.dump(row, open(os.path.join(OUT, f"{name}_info.json"), "w"), indent=1)

# summary over all self-trained models present on disk
infos = [json.load(open(os.path.join(OUT, f))) for f in sorted(os.listdir(OUT)) if f.endswith("_info.json")]
with open(os.path.join(D, "cifar10h", "predictions", "selftrained_summary.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(infos[0].keys()))
    w.writeheader(); w.writerows(infos)
