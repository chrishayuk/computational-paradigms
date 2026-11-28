import sys,os
from show import load
R='/Users/christopherhay/cp-roles/classifier-1B-A/results/python/tokens/'
files=[f"{c}/P07{x}.py" for c in ['core','extended','stdlib-concurrency'] for x in 'abcdefg']
seen={}
for f in files:
    rows=load(f)
    by={}
    for i,l,t in rows: by.setdefault(l,[]).append(t)
    for l,toks in by.items():
        s=' '.join(t for t in toks if t not in('<INDENT>','<DEDENT>'))
        seen.setdefault(s,[]).append(f)
for s,fs in seen.items():
    print(len(fs),'|',s)
