import sys, json, collections
sys.path.insert(0,'.')
from classify import classify, TOK, FAMILY
texts = ["report/P07a.alg","report/P07b.alg","report/P07c.alg","report/P07d.alg","report/P07f.alg","report/P07g.alg","report/P08a.alg","report/P08c.alg",
         "x1/P07a.a60","x1/P07b.a60","x1/P07c.a60","x1/P07d.a60","x1/P07f.a60","x1/P07g.a60","x1/P08a.a60","x1/P08c.a60"]
out = {}
totals = {}
for t in texts:
    f = t.split("/")[1][:4]
    toks, ats, tx, cls, info, proc = classify(TOK + t + ".tokens.tsv", FAMILY[f])
    spans = []
    cover = [0]*len(toks)
    for i,(a,b) in enumerate(ats):
        assert cls[i] in "PCRSH" and len(cls[i])==1, (t, tx[i], cls[i])
        spans.append({"from": a, "to": b, "class": cls[i], "construct": f"{info[i][0]} [{proc[i]}: {tx[i][:70]}]", "rule": info[i][1]})
        for k in range(a,b+1): cover[k]+=1
    assert all(c==1 for c in cover), t
    out[t] = spans
    c = collections.Counter()
    for s in spans: c[s["class"]] += s["to"]-s["from"]+1
    totals[t] = dict(sorted(c.items())) | {"total": len(toks)}
json.dump(out, open("tokens.json","w"), ensure_ascii=False, indent=0)
for t,v in totals.items(): print(t, v)
json.dump(totals, open("totals.json","w"), indent=1)
