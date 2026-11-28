"""Turn a spec of construct starts into inclusive token spans; check coverage."""
from toklines import load
LAYOUT={'<INDENT>','<DEDENT>'}
def resolve(rows):
    bylines={}
    for i,l,t in rows: bylines.setdefault(l,[]).append((i,t))
    lines=sorted(bylines)
    def first(l):
        idx=lines.index(l); start=bylines[l][0][0]
        # pull in preceding layout-only lines (docstring lines)
        j=idx-1
        while j>=0 and all(t in LAYOUT for _,t in bylines[lines[j]]):
            start=bylines[lines[j]][0][0]; j-=1
        return start
    def r(s):
        if isinstance(s,int): return s
        if isinstance(s,str): return first(int(s[1:]))
        l,k=s; l=int(l[1:]); toks=bylines[l]
        if k>=0: return toks[k][0] if k>0 else first(l)
        return toks[len(toks)+k][0]
    return r
def spans(path,spec):
    rows=load(path); r=resolve(rows); n=len(rows)
    starts=[(r(s),c,con,rule) for s,c,con,rule in spec]
    out=[]
    for j,(st,c,con,rule) in enumerate(starts):
        end=(starts[j+1][0]-1) if j+1<len(starts) else n-1
        assert end>=st, (path,j,st,end,con)
        out.append({"from":st,"to":end,"class":c,"construct":con,"rule":rule})
    assert out[0]['from']==0
    cov=[0]*n
    for s in out:
        for i in range(s['from'],s['to']+1): cov[i]+=1
    assert all(x==1 for x in cov),path
    return out,rows
