import itertools, sys, math, numpy as np, cvxpy as cp

def cube(m): return np.array(list(itertools.product([-1,1],repeat=m)))

def trees(m,b):
    """all padded depth-b trees: returns list of dict path(tuple of (coord,ans))->... as function x->cell id (T,u)"""
    def build(avail, depth):
        # returns list of subtrees; subtree = None (leaf) or (coord, sub_minus, sub_plus)
        if depth==0: return [None]
        out=[]
        for j in avail:
            rest=[k for k in avail if k!=j]
            subs=build(rest,depth-1)
            for s0 in subs:
                for s1 in subs:
                    out.append((j,s0,s1))
        return out
    return build(list(range(m)),b)

def cell(tree,x):
    T=[];u=[]
    t=tree
    while t is not None:
        j=t[0]; T.append(j); u.append(x[j]); t = t[2] if x[j]==1 else t[1]
    order=np.argsort(T)
    return (tuple(np.array(T)[order]), tuple(np.array(u)[order]))

def form_tree(S):
    t=None
    for j in reversed(S): t=(j,t,t)
    return t

def interviews(m,b,kind):
    X=cube(m)
    if kind=='forms':
        tl=[form_tree(S) for S in itertools.combinations(range(m),b)]
    else:
        tl=trees(m,b)
    # dedupe by partition
    seen={}; out=[]
    for t in tl:
        cells=[cell(t,x) for x in X]
        key=tuple(cells)
        if key in seen: continue
        seen[key]=1
        ids={}; idx=[]
        for c in cells:
            if c not in ids: ids[c]=len(ids)
            idx.append(ids[c])
        Ts=[None]*len(ids)
        for c,i in ids.items(): Ts[i]=c[0]
        out.append((np.array(idx),len(ids),Ts))
    return X,out

def solve(m,b,kind,targets,mode='max',q_fixed=None,solver='CLARABEL',verbose=False):
    X,ivs=interviews(m,b,kind)
    nI=len(ivs); nx=len(X)
    q=cp.Variable(nI,nonneg=True) if q_fixed is None else q_fixed
    t=cp.Variable()
    cons=[] if q_fixed is not None else [cp.sum(q)==1]
    for d in targets:
        tot=0; sm=0
        for i,(idx,nc,Ts) in enumerate(ivs):
            g=cp.Variable(nc); s=cp.Variable(nc)
            # s >= g^2/q_i
            qi = q[i]
            if q_fixed is not None and q_fixed[i]==0:
                cons.append(g==0); cons.append(s==0)
            else:
                cons.append(cp.SOC(s+qi, cp.vstack([2*g, s-qi]), axis=0))
            M=np.zeros((nx,nc)); M[np.arange(nx),idx]=1
            tot=tot+M@g; sm=sm+M@s
        cons.append(tot==d)
        if mode=='max': cons.append(sm<=t)
        else: cons.append(cp.sum(sm)/nx<=t)
    prob=cp.Problem(cp.Minimize(t),cons)
    prob.solve(solver=solver,verbose=verbose)
    return prob.value, (q.value if q_fixed is None else q_fixed), ivs

def monomials(m,b):
    X=cube(m)
    return [np.prod(X[:,list(A)],axis=1).astype(float) for A in itertools.combinations(range(m),b)]

if __name__=='__main__':
    for (m,b) in [(3,2),(4,2),(3,1),(4,3)]:
        tg=monomials(m,b)
        for kind in ['forms','trees']:
            X,ivs=interviews(m,b,kind)
            for mode in ['max','avg']:
                v,q,_=solve(m,b,kind,tg,mode)
                print(f"m={m} b={b} {kind:5s} n_interviews={len(ivs):4d} mode={mode}: value={v:.6f}  C(m,b)={math.comb(m,b)}",flush=True)
