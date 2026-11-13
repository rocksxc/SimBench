import itertools, math, numpy as np, cvxpy as cp
from fam import *
rng=np.random.default_rng(0)
def fourier(m):
    X=cube(m); subs=[A for k in range(m+1) for A in itertools.combinations(range(m),k)]
    return X,subs,np.array([np.prod(X[:,list(A)],axis=1) for A in subs]).T
for (m,b) in [(3,2),(4,2),(4,3)]:
    X,subs,F=fourier(m); nx=len(X)
    hi=[i for i,A in enumerate(subs) if len(A)>b]
    # Boolean functions of degree<=b
    bools=[]
    for bits in itertools.product([-1.,1.],repeat=nx):
        d=np.array(bits)
        if d[0]<0: continue
        if np.allclose(F[:,hi].T@d,0): bools.append(d)
    nform=math.comb(m,b); qf=np.ones(nform)/nform
    # dedupe by value under uniform forms; report max
    vals=[]
    for d in bools:
        v,_,_=solve(m,b,'forms',[d],'max',q_fixed=qf)
        vals.append(v)
    vals=np.array(vals)
    print(f"m={m} b={b}: {len(bools)} Boolean targets of degree<={b} (up to sign); V under uniform forms: max={vals.max():.5f}, C(m,b)={nform}; #with V>C+1e-4: {(vals>nform+1e-4).sum()}",flush=True)
    # the table stated in the proposition vs the correct normalization
    A=subs[[i for i,S in enumerate(subs) if len(S)==b][0]]
    # homogeneous degree-b random targets with unit L2 norm
    hb=[i for i,S in enumerate(subs) if len(S)==b]
    mx=0
    for _ in range(20):
        c=rng.normal(size=len(hb)); c/=np.linalg.norm(c)
        d=F[:,hb]@c
        v,_,_=solve(m,b,'forms',[d],'max',q_fixed=qf); mx=max(mx,v)
    print(f"   homogeneous degree-{b}, unit L2 norm, 20 random: max V_unif={mx:.5f}")
    # simultaneous minimax over ALL Boolean deg<=b targets: forms vs trees
    if len(bools)<=200:
        for kind in ['forms','trees']:
            v,q,_=solve(m,b,kind,bools,'max')
            print(f"   simultaneous minimax over all Boolean deg<={b} targets, {kind}: {v:.5f}",flush=True)
