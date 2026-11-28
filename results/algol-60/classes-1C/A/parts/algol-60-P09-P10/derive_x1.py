# Derive x1 classes from the report classes by aligning the token sequences (the programs differ only in I/O and stropping).
import difflib,os,json,sys
from build import load,spans,BASE
def toks(path):
    return [l.rstrip('\n').split('\t')[2] for l in open(os.path.join(BASE,path+'.tokens.tsv'))][1:]
def norm(t):
    t=t.replace('̲','')
    return {'boolean':'Boolean'}.get(t,t)
res={}
END_H=('H','end of the X1 output compound begin PRINTTEXT(`[/observe]`); NLCR; PRINTTEXT(`[end]`) end','harness README 2.7.3')
LOOP_END=('H','end of the message loop','harness README 2.7.2')
OVR={'P09c':{717:END_H},'P09d':{374:END_H},'P09e':{766:END_H},
 'P09a.AB':{902:('P','end of inner block','rule 10')},
 'P10a':{202:LOOP_END},'P10b':{420:LOOP_END},'P10c':{280:LOOP_END},'P10d':{686:LOOP_END}}
for name in ['P09a.AB','P09b','P09c','P09d','P09e','P10a','P10b','P10c','P10d']:
    rp='report/'+name+'.alg'; xp='x1/'+name+'.a60'
    rs,_=spans(rp,load('specs/report_'+name+'.alg.py'))
    rcls=[None]*len(toks(rp))
    for i,s in enumerate(rs):
        for j in range(s['from'],s['to']+1): rcls[j]=i
    rt=[norm(t) for t in toks(rp)]; xt=[norm(t) for t in toks(xp)]
    xcls=[None]*len(xt)
    sm=difflib.SequenceMatcher(None,rt,xt,autojunk=False)
    for op,i1,i2,j1,j2 in sm.get_opcodes():
        if op=='equal':
            for k in range(i2-i1): xcls[j1+k]=rcls[i1+k]
        elif op in('replace','insert'):
            src=set(rcls[i1:i2]) if i2>i1 else {rcls[i1-1] if i1>0 else rcls[0], rcls[i1] if i1<len(rcls) else rcls[-1]}
            classes={rs[c]['class'] for c in src}
            if len(classes)!=1:
                print(name,'MIXED',op,rt[i1:i2],xt[j1:j2],[ (rs[c]['class'],rs[c]['construct'][:30]) for c in src])
            # choose: the class of the majority source span
            pick=max(src,key=lambda c:rcls[i1:i2].count(c)) if i2>i1 else min(src)
            for k in range(j1,j2): xcls[k]=pick
    tri=[(rs[c]['class'],rs[c]['construct']+' (as in report)',rs[c]['rule']) for c in xcls]
    for j,v in OVR.get(name,{}).items(): tri[j]=v
    S=[]
    for j,t in enumerate(tri):
        if S and S[-1][1:]==t: continue
        S.append((j,)+t)
    # merge consecutive identical spans index
    res[name]=S
    open('specs/x1_'+name+'.a60.py','w').write('# derived from report by derive_x1.py, then checked by hand\nS = '+repr(S).replace('), (','),\n(')+'\n')
