import math

def eq(a,b):
    if isinstance(a,bool) or isinstance(b,bool): return type(a)==type(b) and a==b
    if isinstance(a,(float,int)) and isinstance(b,(float,int)): return math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-8)
    if type(a)!=type(b): return False
    if isinstance(a,(tuple,list)): return len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
    if isinstance(a,dict): return a.keys()==b.keys() and all(eq(a[k],b[k]) for k in a)
    return a==b
