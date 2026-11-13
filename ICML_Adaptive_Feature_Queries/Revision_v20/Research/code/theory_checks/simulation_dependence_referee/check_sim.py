"""Exact (enumeration) check of Theorem simulation: one step of Pi' for r=1 and r>=2, random unbalanced trees,
label-dependent tree choice, arbitrary P. Then a Monte-Carlo check of a 2-record adaptive protocol (N indep. of output)."""
import itertools, math, random
from fractions import Fraction as F
from collections import defaultdict, Counter

rng = random.Random(7)


def rand_tree(m, b, used=(), depth=0, pstop=0.3):
    """Unpadded random tree: ('leaf', id) or (coord, left, right). Distinct coords along paths."""
    if depth == b or (depth > 0 and rng.random() < pstop):
        return ('leaf', rng.random())
    c = rng.choice([i for i in range(m) if i not in used])
    return (c, rand_tree(m, b, used + (c,), depth + 1, pstop), rand_tree(m, b, used + (c,), depth + 1, pstop))


def pad(tree, m, b, used=()):
    """Pad every path to b distinct coords with unused coords in increasing order; leaves keep the ORIGINAL leaf id."""
    if tree[0] == 'leaf':
        if len(used) == b: return tree
        c = min(i for i in range(m) if i not in used)
        sub = pad(tree, m, b, used + (c,))
        return (c, sub, sub)
    c, l, r = tree
    return (c, pad(l, m, b, used + (c,)), pad(r, m, b, used + (c,)))


def run(tree, x, avail=None):
    """Follow tree on profile x (tuple of 0/1). If avail given, stop when queried coord not in avail.
    Returns (completed, path coords, answers, leaf id or None)."""
    path = []; ans = []
    while tree[0] != 'leaf':
        c = tree[0]
        if avail is not None and c not in avail: return False, tuple(path), tuple(ans), None
        path.append(c); ans.append(x[c]); tree = tree[1 + x[c]]
    return True, tuple(path), tuple(ans), tree[1]


def orig_transcript(tree, x):
    path = []
    while tree[0] != 'leaf':
        c = tree[0]; path.append((c, x[c])); tree = tree[1 + x[c]]
    return tuple(path)


def node_at(tree, x, depth):
    for _ in range(depth): tree = tree[1 + x[tree[0]]]
    return tree


def pathsets(tree, m):
    """distinct coordinate sets of root-to-leaf paths of a (sub)tree"""
    out = set()
    def rec(t, acc):
        if t[0] == 'leaf': out.add(frozenset(acc)); return
        rec(t[1], acc + [t[0]]); rec(t[2], acc + [t[0]])
    rec(tree, [])
    return sorted(out, key=sorted)


def one_step(m, b, r, trees, P):
    """trees[y] = (orig, padded). Returns joint law of (accept, orig transcript, y) for one fresh record of Pi'."""
    Kr = min(2 ** (b - r), math.comb(m - r, b - r))
    acc = defaultdict(F); target = defaultdict(F); pacc_given = {}
    for (x, y), pxy in P.items():
        orig, padt = trees[y]
        tr = orig_transcript(orig, x)
        target[(tr, y)] += pxy
        # Pi': follow padded tree r-1 rounds (one query per round), then guess a path set of the subtree at v
        v = node_at(padt, x, r - 1)
        prefix = [c for c, _ in orig_transcript(padt, x)[:r - 1]]
        sets = pathsets(v, m); L = len(sets)
        assert L <= Kr, (L, Kr)
        pa = F(0)
        nsucc = 0
        for S in sets:
            avail = set(prefix) | set(S)
            assert len(avail) == b
            ok, path, ans, leaf = run(padt, x, avail)
            if ok:
                nsucc += 1
                # transcript of original tree must be recoverable from observed answers only
                obs = {c: x[c] for c in avail}
                t2 = []; tt = orig
                while tt[0] != 'leaf':
                    t2.append((tt[0], obs[tt[0]])); tt = tt[1 + obs[tt[0]]]
                assert tuple(t2) == tr
                pa += F(1, L) * F(L, Kr)
        assert nsucc == 1, nsucc          # exactly one guessed set completes the path
        pacc_given[(x, y)] = pa
        acc[(tr, y)] += pxy * pa
    assert all(v == F(1, Kr) for v in pacc_given.values())
    assert all(acc[k] == target[k] * F(1, Kr) for k in target)
    return Kr, len(target)


for trial in range(300):
    m = rng.choice([4, 5, 6]); b = rng.choice([2, 3, 4]); b = min(b, m)
    # arbitrary law incl. zero-mass points
    pts = [(x, y) for x in itertools.product((0, 1), repeat=m) for y in (0, 1)]
    w = [F(rng.randint(0, 5)) for _ in pts]; tot = sum(w)
    if tot == 0: continue
    P = {pt: wi / tot for pt, wi in zip(pts, w) if wi > 0}
    trees = {}
    for y in (0, 1):   # label-dependent tree
        o = rand_tree(m, b); trees[y] = (o, pad(o, m, b))
    for r in range(1, b + 1):
        Kr, ncell = one_step(m, b, r, trees, P)
print("exact one-step check passed: acceptance prob == 1/K_r for every (x,y); P(accept, transcript, y) == P(transcript, y)/K_r; r=1..b, label-dependent trees, non-full-support P")

# check path-set counts L_tau differ between labels sometimes (so thinning matters)
diff = 0
for _ in range(200):
    o0 = pad(rand_tree(5, 3), 5, 3); o1 = pad(rand_tree(5, 3), 5, 3)
    diff += len(pathsets(o0, 5)) != len(pathsets(o1, 5))
print("fraction of label pairs with different L_tau:", diff / 200)

# ---- Monte Carlo: 2-record across-record-adaptive, label-dependent protocol, r=1 and r=2
import numpy as np
nprng = np.random.default_rng(1)
m, b = 5, 3
pts = [(x, y) for x in itertools.product((0, 1), repeat=m) for y in (0, 1)]
pw = nprng.dirichlet(np.ones(len(pts)) * 0.3)
T = {}
for key in ['first0', 'first1'] + [('second', y, z) for y in (0, 1) for z in range(2)]:
    o = rand_tree(m, b); T[key] = (o, pad(o, m, b))


def choose_tree(past, y):
    if not past: return T['first%d' % y]
    tr, y0 = past[0]
    return T[('second', y, (len(tr) + y0 + sum(a for _, a in tr)) % 2)]


def Pi(n=2):
    past = []
    for _ in range(n):
        x, y = pts[nprng.choice(len(pts), p=pw)]
        o, _ = choose_tree(past, y); past.append((orig_transcript(o, x), y))
    return tuple(past)


def Pi_prime(r, n=2):
    Kr = min(2 ** (b - r), math.comb(m - r, b - r)); past = []; N = 0
    while len(past) < n:
        x, y = pts[nprng.choice(len(pts), p=pw)]; N += 1
        o, padt = choose_tree(past, y)
        v = node_at(padt, x, r - 1); prefix = [c for c, _ in orig_transcript(padt, x)[:r - 1]]
        sets = pathsets(v, m); S = sets[nprng.integers(len(sets))]
        ok, *_ = run(padt, x, set(prefix) | set(S))
        if ok and nprng.random() < len(sets) / Kr:
            past.append((orig_transcript(o, x), y))
    return tuple(past), N


R = 60000
ref = Counter(Pi() for _ in range(R))
for r in (1, 2):
    Kr = min(2 ** (b - r), math.comb(m - r, b - r))
    sims = [Pi_prime(r) for _ in range(R)]
    c = Counter(o for o, _ in sims); Ns = np.array([n for _, n in sims])
    keys = set(ref) | set(c)
    tv = 0.5 * sum(abs(ref[k] - c[k]) for k in keys) / R
    # independence: compare mean N across the most frequent outputs, and chi2 of (N<=median) vs output
    big = [k for k, _ in c.most_common(8)]
    means = [float(np.mean([n for o, n in sims if o == k])) for k in big]
    print(f"r={r}: K_r={Kr}; TV(output law Pi' vs Pi) = {tv:.4f} over {len(keys)} outputs (MC noise ~{0.5*np.sqrt(len(keys)/R)*0.8:.3f}); mean N={Ns.mean():.3f} (expect {2*Kr}); var N={Ns.var():.3f} (expect {2*Kr*(Kr-1)}); mean N by output: {np.round(means,2)}")

# calibration: TV between two independent samples of Pi itself
ref2 = Counter(Pi() for _ in range(R))
keys = set(ref) | set(ref2)
print("calibration: TV between two independent runs of Pi itself =", round(0.5 * sum(abs(ref[k] - ref2[k]) for k in keys) / R, 4))
