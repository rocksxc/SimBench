"""Run the 19 pretrained CIFAR-10 classifiers of chenyaofo/pytorch-cifar-models on the 10,000 test images (CPU).

Usage: python -I 02_cifar_pretrained_eval.py /abs/path/to/c1/data
Model definitions are imported from data/cifar10h/raw/pytorch-cifar-models (pinned snapshot of the repo);
weights are loaded from local files with torch.load(weights_only=True).
Preprocessing: uint8 -> [0,1] -> normalise with mean (0.4914,0.4822,0.4465), std (0.2023,0.1994,0.2010).
"""
import csv
import hashlib
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch

D = sys.argv[1]
RAW = os.path.join(D, "cifar10h", "raw")
OUT = os.path.join(D, "cifar10h", "predictions", "pretrained")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(RAW, "pytorch-cifar-models"))
import pytorch_cifar_models as pcm  # noqa: E402

torch.set_num_threads(4)
torch.manual_seed(0)
MEAN = torch.tensor([0.4914, 0.4822, 0.4465]).view(1, 3, 1, 1)
STD = torch.tensor([0.2023, 0.1994, 0.2010]).view(1, 3, 1, 1)

# advertised top-1 accuracy: parsed from the Model Zoo table (CIFAR-10 section) of the repo README
readme = open(os.path.join(RAW, "pytorch-cifar-models", "README.md")).read()
sec = readme.split("### CIFAR-10\n")[1].split("### CIFAR-100")[0]
advertised = {}
for line in sec.splitlines():
    m = re.match(r"\|\s*([a-z0-9_]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|", line)
    if m:
        advertised[m.group(1)] = (float(m.group(2)), float(m.group(3)))

t = np.load(os.path.join(D, "cifar10h", "cifar10_test.npz"), allow_pickle=False)
x = torch.from_numpy(t["images"]).permute(0, 3, 1, 2).float().div(255.0)
x = (x - MEAN) / STD
y = t["labels"].astype(np.int64)
counts = np.load(os.path.join(D, "cifar10h", "cifar10h_counts.npy"))
hplur = counts.argmax(1)
hsoft = counts / counts.sum(1, keepdims=True)

wdir = os.path.join(RAW, "model_weights")
rows = []
for fn in sorted(os.listdir(wdir)):
    m = re.match(r"cifar10_(.+)-([0-9a-f]{8})\.pt$", fn)
    name, h8 = m.group(1), m.group(2)
    path = os.path.join(wdir, fn)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    assert sha[:8] == h8, (fn, sha)
    model = getattr(pcm, "cifar10_" + name)(pretrained=False)
    sd = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(sd, strict=True)
    model.eval()
    t0 = time.time()
    outs = []
    with torch.inference_mode():
        for i in range(0, 10000, 500):
            outs.append(model(x[i:i + 500]))
    logits = torch.cat(outs).double()
    probs = torch.softmax(logits, 1).numpy().astype(np.float32)
    logits = logits.numpy().astype(np.float32)
    pred = probs.argmax(1).astype(np.int16)
    top5 = (np.argsort(-logits, 1)[:, :5] == y[:, None]).any(1).mean() * 100
    acc = (pred == y).mean() * 100
    adv1, adv5 = advertised[name]
    row = dict(model=name, source="pretrained (chenyaofo/pytorch-cifar-models)", weight_file=fn,
               n_params=sum(p.numel() for p in model.parameters()),
               top1_acc_vs_cifar10_labels=round(acc, 2), advertised_top1=adv1, diff_top1=round(acc - adv1, 2),
               top5_acc=round(top5, 2), advertised_top5=adv5,
               acc_vs_cifar10h_plurality=round((pred == hplur).mean() * 100, 2),
               mean_human_prob_of_predicted_class=round(float(hsoft[np.arange(10000), pred].mean()), 5),
               seconds=round(time.time() - t0, 1))
    rows.append(row)
    np.savez_compressed(os.path.join(OUT, f"{name}.npz"), probs=probs, logits=logits, pred=pred)
    print(row, flush=True)

with open(os.path.join(D, "cifar10h", "predictions", "pretrained_summary.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
ver = {"n_models": len(rows),
       "max_abs_diff_top1_vs_advertised": max(abs(r["diff_top1"]) for r in rows),
       "max_abs_diff_top5_vs_advertised": max(abs(r["top5_acc"] - r["advertised_top5"]) for r in rows),
       "torch_version": torch.__version__}
json.dump(ver, open(os.path.join(D, "cifar10h", "predictions", "verification_pretrained.json"), "w"), indent=1)
print(ver)
