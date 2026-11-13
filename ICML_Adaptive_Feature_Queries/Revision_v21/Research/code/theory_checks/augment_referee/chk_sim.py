"""Independent check of thm:augment(a): construction F_g for random padded depth-b trees.
Verifies: |F_g| <= b - j + 2^{j+1} - 2 <= b + c; for every profile exactly one g is followed; on that event the whole
path lies in F_g and the transcript is a function of x_{F_g}; and (statistically exact) that the centred score
c0 + K+(H - c0) 1{follows g} is pointwise unbiased with variance K+ Var(H). Also j(c) values and K+ < 2^{b+1}/(c+3)."""
import itertools, numpy as np
rng = np.random.default_rng(7)

def jc(c, b):
    return max(j for j in range(0, b) if 2 ** (j + 1) - j - 2 <= c)

# j values and inequality
print('j(c) for large b:', {c: jc(c, 50) for c in (0, 1, 2, 3, 4, 10, 11, 25, 26, 57)})
bad = []; maxratio = 0
for b in range(1, 13):
    D = 2 ** (b - 1)
    for c in range(0, 2 ** (b + 2)):
        j = jc(c, b); Kp = 2 ** (b - 1 - j)
        if j < b - 1: assert 2 ** j > (c + 3) / 4
        if not Kp < 2 ** (b + 1) / (c + 3): bad.append((b, c, Kp, 2 ** (b + 1) / (c + 3)))
        if c <= D - 1:
            maxratio = max(maxratio, Kp * (c + 1) / D)
            if c in (0, 1): assert Kp * (c + 1) == D, (b, c)
print('max over b<=12, 0<=c<=D-1 of K+ / (2^{b-1}/(c+1)) = %.4f (claim < 4)' % maxratio)
print('cases with K+ >= 2^{b+1}/(c+3): first few', bad[:6], ' smallest c per b:', {b: min(c for bb, c, _, _ in bad if bb == b) for b in sorted({x[0] for x in bad})})

def random_tree(m, b):
    q = {}
    def rec(prefix, asked):
        if len(prefix) == b: return
        j = int(rng.choice([i for i in range(m) if i not in asked])); q[prefix] = j
        for v in (0, 1): rec(prefix + (v,), asked + [j])
    rec((), [])
    return q

ntest = 0
for trial in range(200):
    b = int(rng.integers(1, 6)); m = int(rng.integers(b, b + 9)); q = random_tree(m, b)
    X = ((np.arange(1 << m)[:, None] >> np.arange(m)) & 1)
    # path of every profile
    paths = []
    for x in range(1 << m):
        pre = ()
        for _ in range(b): pre = pre + (int(X[x, q[pre]]),)
        paths.append(pre)
    for c in range(0, m - b + 1):
        j = jc(c, b); G = list(itertools.product((0, 1), repeat=b - 1 - j)); F = {}
        for g in G:
            form = []; pre = ()
            for a in g: form.append(q[pre]); pre = pre + (a,)
            npath = len(form) + 1   # the last guessed node itself is asked too
            sub = [pre]; nodes = 0
            while sub:
                p_ = sub.pop()
                if len(p_) == b: continue
                form.append(q[p_]); nodes += 1; sub += [p_ + (0,), p_ + (1,)]
            assert npath == b - j and nodes - 1 == 2 ** (j + 1) - 2, (b, j, npath, nodes)
            F[g] = sorted(set(form)); assert len(F[g]) <= b - j + 2 ** (j + 1) - 2 <= b + c
        count = np.zeros(1 << m, int)
        for g in G:
            Fg = F[g]; follows = np.array([paths[x][:len(g)] == g for x in range(1 << m)])
            count += follows
            # (i) 'follows g' and (ii) the transcript on that event are functions of x_{F_g}
            code = X[:, Fg] @ (1 << np.arange(len(Fg)))
            for cd_ in np.unique(code):
                sel = code == cd_
                assert follows[sel].all() or (~follows[sel]).all()
                if follows[sel].all(): assert len({paths[x] for x in np.flatnonzero(sel)}) == 1
            # the whole path lies in F_g on the event
            for x in np.flatnonzero(follows)[:50]:
                pre = ()
                for _ in range(b): assert q[pre] in Fg; pre = pre + (int(X[x, q[pre]]),)
        assert (count == 1).all()
        # centred score: exact moments at a random law with a random leaf score H
        Kp = len(G); P = rng.dirichlet(np.ones(1 << m)); leaf = {}
        H = np.array([leaf.setdefault(p_, rng.normal()) for p_ in paths]); c0 = P @ H
        mean = np.zeros(1 << m); second = 0.0
        for g in G:
            follows = np.array([paths[x][:len(g)] == g for x in range(1 << m)])
            S = c0 + Kp * (H - c0) * follows; mean += S / Kp; second += (P @ (S - c0) ** 2) / Kp
        assert np.allclose(mean, H) and np.isclose(second, Kp * (P @ (H - c0) ** 2))
        ntest += 1
print('construction verified on %d (tree, c) cases: sizes, exactly-one-g, measurability, centred score moments' % ntest)
