import json,os
base='./results/python/tokens/'
d=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'python.json')))
for p,sp in d['tokens'].items():
    n=sum(1 for _ in open(base+p+'.tokens.tsv'))-1
    cov=[0]*n
    for s in sp:
        assert s['class'] in 'PCRSH'
        for i in range(s['from'],s['to']+1): cov[i]+=1
    assert all(c==1 for c in cov),p
    print(p,n,'ok')
print(len(d['outcomes']),'outcomes')
