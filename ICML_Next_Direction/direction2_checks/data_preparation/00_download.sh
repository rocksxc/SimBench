#!/usr/bin/env bash
# Re-downloads every raw file used in c1/data. All URLs are pinned to a git commit
# (raw.githubusercontent.com) or to a GitHub release asset.
# Usage: bash 00_download.sh /abs/path/to/c1/data
set -euo pipefail
D="${1:?give the data directory}"
get() { mkdir -p "$(dirname "$2")"; curl -sS -L --fail -o "$2" "$1"; echo "ok $2"; }

# ---- CIFAR-10H (jcpeterson/cifar-10h @ 389f22d)
C10H=https://raw.githubusercontent.com/jcpeterson/cifar-10h/389f22d9d300ec71a4c44735d46f550c94b957ab
for f in data/cifar10h-counts.npy data/cifar10h-probs.npy data/cifar10h-raw.zip LICENSE.txt; do
  get "$C10H/$f" "$D/cifar10h/raw/cifar10h/$(basename $f)"
done

# ---- CIFAR-10 python batches (GitHub mirror 0Colin/cifar-10-batches-py @ 48ece5c;
#      md5 of every batch file equals the md5 hard-coded in torchvision/datasets/cifar.py)
C10=https://raw.githubusercontent.com/0Colin/cifar-10-batches-py/48ece5ce490482885f7a9a492fa031c1de79519c
for f in test_batch data_batch_1 data_batch_2 data_batch_3 data_batch_4 data_batch_5 batches.meta; do
  get "$C10/$f" "$D/cifar10h/raw/cifar-10-batches-py/$f"
done

# ---- pretrained CIFAR-10 weights (chenyaofo/pytorch-cifar-models release assets)
R=https://github.com/chenyaofo/pytorch-cifar-models/releases/download
for a in resnet/cifar10_resnet20-4118986f resnet/cifar10_resnet32-ef93fc4d resnet/cifar10_resnet44-2a3cabcb \
         resnet/cifar10_resnet56-187c023a vgg/cifar10_vgg11_bn-eaeebf42 vgg/cifar10_vgg13_bn-c01e4a43 \
         vgg/cifar10_vgg16_bn-6ee7ea24 vgg/cifar10_vgg19_bn-57191229 \
         mobilenetv2/cifar10_mobilenetv2_x0_5-ca14ced9 mobilenetv2/cifar10_mobilenetv2_x0_75-a53c314e \
         mobilenetv2/cifar10_mobilenetv2_x1_0-fe6a5b48 mobilenetv2/cifar10_mobilenetv2_x1_4-3bbbd6e2 \
         shufflenetv2/cifar10_shufflenetv2_x0_5-1308b4e9 shufflenetv2/cifar10_shufflenetv2_x1_0-98807be3 \
         shufflenetv2/cifar10_shufflenetv2_x1_5-296694dd shufflenetv2/cifar10_shufflenetv2_x2_0-ec31611c \
         repvgg/cifar10_repvgg_a0-ef08a50e repvgg/cifar10_repvgg_a1-38d2431b repvgg/cifar10_repvgg_a2-09488915; do
  get "$R/$a.pt" "$D/cifar10h/raw/model_weights/$(basename $a).pt"
done
# model definitions (chenyaofo/pytorch-cifar-models @ 786c162)
PCM=https://raw.githubusercontent.com/chenyaofo/pytorch-cifar-models/786c16252c0fc58ee9adac063f8337cc4a7a497a
for f in LICENSE README.md hubconf.py pytorch_cifar_models/__init__.py pytorch_cifar_models/resnet.py \
         pytorch_cifar_models/vgg.py pytorch_cifar_models/mobilenetv2.py pytorch_cifar_models/shufflenetv2.py \
         pytorch_cifar_models/repvgg.py pytorch_cifar_models/vit.py; do
  get "$PCM/$f" "$D/cifar10h/raw/pytorch-cifar-models/$f"
done

# ---- DICES (google-research-datasets/dices-dataset @ b5596d9)
DI=https://raw.githubusercontent.com/google-research-datasets/dices-dataset/b5596d9edd585361967991a591abc7b11fb1f7a3
get "$DI/README.md" "$D/dices/raw/README.md"
for n in 350 990; do
  get "$DI/$n/README.md" "$D/dices/raw/README_$n.md"
  get "$DI/$n/diverse_safety_adversarial_dialog_$n.csv" "$D/dices/raw/diverse_safety_adversarial_dialog_$n.csv"
done

# ---- ChaosNLI (official Dropbox link blocked; GitHub mirror TheGuy-26/chaosnli-deberta-modernbert @ 1e84e02)
CH=https://raw.githubusercontent.com/TheGuy-26/chaosnli-deberta-modernbert/1e84e025686d0d7a9b38747906788355041370b6/ChaosNLI/data
get "$CH/chaosNLI_v1.0/README.txt" "$D/chaosnli/raw/chaosNLI_v1.0_README.txt"
for f in chaosNLI_snli.jsonl chaosNLI_mnli_m.jsonl chaosNLI_alphanli.jsonl; do
  get "$CH/chaosNLI_v1.0/$f" "$D/chaosnli/raw/$f"
done
for f in model_predictions_for_snli_mnli.json model_predictions_for_abdnli.json; do
  get "$CH/model_predictions/$f" "$D/chaosnli/raw/$f"
done

# ---- optional: Fashion-MNIST-H (takashiishida/irreducible @ 670fbb6) + Fashion-MNIST (zalandoresearch/fashion-mnist @ b2617bb)
FMH=https://raw.githubusercontent.com/takashiishida/irreducible/670fbb6b7f0958735b0fbfa59ef3906e319d60c0
for f in data/fmh_counts.csv data/fmh_probs.csv data/fmh_raw.csv LICENSE README.md; do
  get "$FMH/$f" "$D/fashion_mnist_h/raw/fmh/$(basename $f)"
done
FM=https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/b2617bb6d3ffa2e429640350f613e3291e10b141
for f in data/fashion/t10k-images-idx3-ubyte.gz data/fashion/t10k-labels-idx1-ubyte.gz \
         data/fashion/train-images-idx3-ubyte.gz data/fashion/train-labels-idx1-ubyte.gz LICENSE; do
  get "$FM/$f" "$D/fashion_mnist_h/raw/fashion-mnist/$(basename $f)"
done

# ---- optional: bluebirds (welinder/cubam @ fe5ba70)
CU=https://raw.githubusercontent.com/welinder/cubam/fe5ba700f1adbb489c69af311558d64370d73d36
for f in demo/bluebirds/gt.yaml demo/bluebirds/labels.yaml LICENSE.TXT README.md; do
  get "$CU/$f" "$D/bluebirds/raw/$(basename $f)"
done
