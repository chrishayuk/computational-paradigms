# Residual-equivalence check for P08a stages 4 and 5 (all three configurations print the same state).
# The system's state: bindings plus suspended equations between unknowns. We close the equations with
# union-find and substitute into a and b, then compare with the valid outcomes up to renaming of the
# free representatives.
def solve(bindings, eqs):
    parent={}
    def f(v):
        parent.setdefault(v,v)
        while parent[v]!=v: v=parent[v]
        return v
    for a,b in eqs: parent[f(a)]=f(b)
    sub=lambda t:[f(e) for e in t]
    return {k:sub(v) for k,v in bindings.items()}, f
def canon(lists):
    names={}; out=[]
    for l in lists:
        out.append([names.setdefault(e,'V%d'%len(names)) for e in l])
    return out
# stage 4: a = [x;y;z], b = [h5;h6;h1]; suspended x=y, x=h1, y=h2, z=h3, h3=h4, h4=h5, h2=h6
b4={'a':['x','y','z'],'b':['h5','h6','h1']}
e4=[('x','y'),('x','h1'),('y','h2'),('z','h3'),('h3','h4'),('h4','h5'),('h2','h6')]
r,f=solve(b4,e4)
sys4=canon([r['a'],r['b'],[f('x'),f('y'),f('z')]])
# valid stage 4: x = y, a = <y,y,z>, b = <z,y,y>
val4=canon([['y','y','z'],['z','y','y'],['y','y','z']])
print('stage 4 system',sys4,'valid',val4,'equivalent',sys4==val4)
# stage 5: add y = z
e5=e4+[('y','z')]
r,f=solve(b4,e5)
sys5=canon([r['a'],r['b'],[f('x'),f('y'),f('z')]])
val5=canon([['z','z','z'],['z','z','z'],['z','z','z']])
print('stage 5 system',sys5,'valid',val5,'equivalent',sys5==val5)
