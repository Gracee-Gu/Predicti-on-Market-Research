from collections import Counter

def cohen_kappa(a,b):
    pairs=[(x,y) for x,y in zip(a,b) if x!='' and y!='']
    if not pairs: return None
    n=len(pairs); po=sum(x==y for x,y in pairs)/n
    ca=Counter(x for x,_ in pairs); cb=Counter(y for _,y in pairs)
    pe=sum(ca[k]*cb[k] for k in set(ca)|set(cb))/(n*n)
    return 1.0 if pe==1 else (po-pe)/(1-pe)

def krippendorff_alpha_ordinal(values_by_unit):
    rows=[[float(v) for v in vals if v!=''] for vals in values_by_unit]
    rows=[r for r in rows if len(r)>1]
    if not rows: return None
    allv=[v for r in rows for v in r]; lo,hi=min(allv),max(allv)
    if hi==lo: return 1.0
    do=sum((x-y)**2 for r in rows for i,x in enumerate(r) for y in r[i+1:])
    do/=sum(len(r)*(len(r)-1)/2 for r in rows)
    de=sum((x-y)**2 for i,x in enumerate(allv) for y in allv[i+1:])
    de/=(len(allv)*(len(allv)-1)/2)
    return 1.0 if de==0 else 1-do/de
