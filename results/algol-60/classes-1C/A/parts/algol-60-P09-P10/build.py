import os,sys,json,glob,importlib.util
BASE='/Users/christopherhay/cp-roles/classifier-1C-A/results/algol-60/tokens'
def ntok(path):
    return sum(1 for _ in open(os.path.join(BASE,path+'.tokens.tsv')))-1
def load(fn):
    spec=importlib.util.spec_from_file_location('m',fn);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m.S
def spans(text,S):
    n=ntok(text);out=[];
    starts=[s[0] for s in S]
    assert starts[0]==0, text
    assert starts==sorted(starts) and len(set(starts))==len(starts), (text,[s for s,t in zip(starts,starts[1:]) if t<=s])
    for i,(st,c,con,r) in enumerate(S):
        en=(S[i+1][0]-1) if i+1<len(S) else n-1
        assert st<=en<n,(text,st,en,n)
        assert c in 'PCRSH'
        out.append({'from':st,'to':en,'class':c,'construct':con,'rule':r})
    return out,n
if __name__=='__main__':
    for fn in sorted(glob.glob('specs/*.py')):
        b=os.path.basename(fn)[:-3]; cfg,f=b.split('_',1); text=cfg+'/'+f
        sp,n=spans(text,load(fn)); tot={}
        for s in sp: tot[s['class']]=tot.get(s['class'],0)+s['to']-s['from']+1
        print(text,n,tot)
