from fractions import Fraction as F
from math import comb
bad=0
for kappa in range(0,7):
    D=2**kappa; m=kappa+D; b=kappa+1
    for B in range(b,m+1):
        c=B-b
        # max energy of forms of size <=B: r data, s address
        best=max(F(r*2**s,4**kappa) for s in range(kappa+1) for r in range(0,D+1) if s+r<=B)
        if best!=F(c+1,D): bad+=1; print('energy',kappa,B,best)
        # information per cost
        for s in range(kappa+1):
            for r in range(0,D+1):
                cc=s+r
                if 0<cc<=B and F(r*2**s,4**kappa)>F(cc*(B-kappa),B*D): bad+=1; print('ipc',kappa,B,s,r)
        # mean-budget ratio
        val=F(D*B,b*(B-kappa)); assert val==F(b+c,b)*F(2**(b-1),c+1); assert val>=F(2**(b-1),b)
        # mean-budget max info: max over forms J_T/|T| * b
        mi=max(F(r*2**s,4**kappa)/(s+r) for s in range(kappa+1) for r in range(0,D+1) if 0<s+r<=B)*b
        if 1/mi!=val: bad+=1; print('mb',kappa,B,1/mi,val)
# K+ bounds
for b in range(1,12):
    for c in range(0,2**(b-1)):
        j=max(j for j in range(b) if 2**(j+1)-j-2<=c); K=2**(b-1-j)
        lo=F(2**(b-1),c+1)
        if not (lo<=K and K<=F(2**(b+1),c+3) and K<4*lo): bad+=1; print('K',b,c,K,lo)
        if K>1 and not K<F(2**(b+1),c+3): bad+=1;print('Kstrict',b,c)
print('bad',bad)
import math
a=0.376; print(a*math.log2(1+2/a), math.log2(1+2/a)-2/((a+2)*math.log(2)))
for x in (1.38,1.39,1.46,1.5): print(x,1-1/x)
