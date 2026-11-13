"""Independent brute-force checks for Theorem structuredfull (d)."""
import itertools, sys
import numpy as np

# ---- gadget over 8 triples
print("gadget 3p+sz-2ps-2pz:")
for p, s, z in itertools.product((0, 1), repeat=3):
    v = 3 * p + s * z - 2 * p * s - 2 * p * z
    print("  p,s,z=", p, s, z, "pen=", v, "p==sz" if p == s * z else "")
    assert v >= 0 and ((v == 0) == (p == s * z))

# ---- inequality n*kap-(kap+1)(n-1)^2 < kap
for kap in range(1, 12):
    for n in range(2, 2 ** min(kap, 8) + 1):
        assert n * kap - (kap + 1) * (n - 1) ** 2 < kap
print("inequality n*kap-(kap+1)(n-1)^2<kap OK for kap<=11")


def setup(b):
    kap = b - 1; D = 1 << kap; m = kap + 3 * D
    N = 1 << m
    g = ((np.arange(N)[:, None] >> np.arange(m)) & 1).astype(np.int8)  # 0/1 bits
    a01 = g[:, :kap]; s = g[:, kap:kap + D].astype(int); z = g[:, kap + D:kap + 2 * D].astype(int); p = g[:, kap + 2 * D:].astype(int)
    a = 2 * a01.astype(int) - 1                      # +-1 address
    jb = 2 * ((np.arange(D)[:, None] >> np.arange(kap)) & 1) - 1  # sign vector of each data index
    ip = a @ jb.T                                     # <a,j>
    sel = (a01.astype(int) @ (1 << np.arange(kap)))   # selected index (ip==kap there)
    assert np.all(ip[np.arange(N), sel] == kap) and np.all((ip == kap).sum(1) == 1)
    H = (s * ip).sum(1) - (kap + 1) * (s.sum(1) - 1) ** 2 - (3 * p + s * z - 2 * p * s - 2 * p * z).sum(1)
    Z = 2 * z - 1
    d = Z[np.arange(N), sel]
    return dict(kap=kap, D=D, m=m, N=N, g=g, s=s, z=z, p=p, a=a, sel=sel, H=H, d=d, Z=Z)


def J_forms(P, h, g, m, b):
    """J_S(h)=E[E[h|X_S]^2] for all b-subsets S (label handled outside)."""
    out = {}
    w = P * h
    for S in itertools.combinations(range(m), b):
        key = np.zeros(len(P), dtype=np.int64)
        for i, c in enumerate(S):
            key |= g[:, c].astype(np.int64) << i
        num = np.bincount(key, weights=w, minlength=1 << b)
        den = np.bincount(key, weights=P, minlength=1 << b)
        ok = den > 0
        out[S] = float((num[ok] ** 2 / den[ok]).sum())
    return out


for b in (2, 3):
    G = setup(b); kap, D, m, N = G['kap'], G['D'], G['m'], G['N']
    H = G['H']
    mx = H.max(); arg = np.where(H == mx)[0]
    onehot = np.zeros((N, D), int); onehot[np.arange(N), G['sel']] = 1
    good = np.all(G['s'] == onehot, 1) & np.all(G['p'] == G['s'] * G['z'], 1)
    print(f"\nb={b}: m={m}, max H={mx} (kappa={kap}), #maximisers={len(arg)} expected {2**kap*2**D}; maximisers==claimed set: {set(arg)==set(np.where(good)[0])}")
    # second largest H value
    print("   gap to second largest H:", mx - np.max(H[H < mx]))
    Pinf = good / good.sum()
    # marginal of (a,z) on support uniform?
    d = G['d']; h0x = 2 * G['p'].sum(1) - 1
    print("   d == 2 sum p -1 on support:", np.all(d[good] == h0x[good]), "; off support equality fraction:", np.mean(d[~good] == h0x[~good]))
    # J_S(t) under P_inf for all forms. label independent uniform => J_S(t)=E[E[d|X_S]^2]
    J = J_forms(Pinf, d.astype(float), G['g'], m, b)
    best = max(J, key=J.get)
    names = [f"a{i}" for i in range(kap)] + [f"s{j}" for j in range(D)] + [f"z{j}" for j in range(D)] + [f"p{j}" for j in range(D)]
    print(f"   forms: {len(J)}; max_S J_S(t)={J[best]:.6f} at {[names[c] for c in best]}; bound b/D={b/D:.6f}; => limit lower bound 1/maxJ={1/J[best]:.4f} vs D/b={D/b:.4f}")
    assert J[best] <= b / D + 1e-12
    # count violations & top few
    top = sorted(J.items(), key=lambda kv: -kv[1])[:5]
    for S, v in top: print("      ", [names[c] for c in S], round(v, 6))
    # finite beta: lower bound Cov^2/max_S J_S(h0) (label uniform independent => E h0 = 0, J_S(h0)=E[E[h0x|X_S]^2])
    for beta in (0, 0.5, 1, 2, 3, 4, 6, 8, 12):
        w = np.exp(beta * (H - mx)); P = w / w.sum()
        cov = float((P * d * h0x).sum())
        Jb = J_forms(P, h0x.astype(float), G['g'], m, b)
        mJ = max(Jb.values())
        print(f"   beta={beta:5.1f}: P(support)={P[good].sum():.5f} Cov(t,h0)={cov:.5f} Var_x(h0)={float((P*h0x**2).sum()):.4f} max_S J_S(h0)={mJ:.5f} lower bound on W_fixed^(k)={cov**2/mJ:.5f}")

# b=4: only on the support of P_inf (2^3 * 2^8 points), all C(27,4) forms
b = 4; kap = 3; D = 8; m = kap + 3 * D
rows = []
for av in range(D):
    for zv in range(1 << D):
        zz = [(zv >> j) & 1 for j in range(D)]
        ab = [(av >> i) & 1 for i in range(kap)]
        s = [1 if j == av else 0 for j in range(D)]
        p = [s[j] * zz[j] for j in range(D)]
        rows.append(ab + s + zz + p + [2 * zz[av] - 1])
R = np.array(rows); g = R[:, :m]; d = R[:, m].astype(float); P = np.full(len(R), 1 / len(R))
J = J_forms(P, d, g, m, b)
best = max(J, key=J.get)
names = [f"a{i}" for i in range(kap)] + [f"s{j}" for j in range(D)] + [f"z{j}" for j in range(D)] + [f"p{j}" for j in range(D)]
print(f"\nb=4 (support only): forms {len(J)}, max_S J_S(t)={J[best]:.6f} at {[names[c] for c in best]}; b/D={b/D}; b/(2D-b)={b/(2*D-b):.6f}")
assert J[best] <= b / D + 1e-12
