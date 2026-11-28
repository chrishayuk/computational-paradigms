import json, csv
d=json.load(open("/Users/christopherhay/cp-roles/classes-1B-A/algol-60-P07-P08/algol-60.json"))
T="/Users/christopherhay/cp-roles/classifier-1B-A/results/algol-60/tokens/"
texts=[l.split("\t")[0] for l in open(T+"TEXTS-1B-P07-P08.tsv").read().splitlines()[1:]]
assert sorted(texts)==sorted(d["tokens"]), (set(texts)^set(d["tokens"]))
tot={}
for t,sp in d["tokens"].items():
    n=sum(1 for _ in open(T+t+".tokens.tsv"))-1
    cov=[0]*n
    for s in sp:
        assert s["class"] in "PCRSH"
        for k in range(s["from"],s["to"]+1): cov[k]+=1
    assert all(c==1 for c in cov), t
    c={}
    for s in sp: c[s["class"]]=c.get(s["class"],0)+s["to"]-s["from"]+1
    tot[t]=c
    print(t,n,c)
print("ok", len(d["outcomes"]))
