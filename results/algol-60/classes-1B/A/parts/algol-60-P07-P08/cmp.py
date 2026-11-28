import sys, collections
sys.path.insert(0,'.')
from classify import classify, TOK, FAMILY
for f in ["P07a","P07b","P07c","P07d","P07f","P07g","P08a","P08c"]:
    res={}
    for conf,ext in (("report","alg"),("x1","a60")):
        toks, ats, texts, cls, info, proc = classify(TOK+f"{conf}/{f}.{ext}.tokens.tsv", FAMILY[f])
        per=collections.defaultdict(list)
        for i,(a,b) in enumerate(ats):
            per[toks[a][1] if toks[a][2]!=';' or a==b else toks[a+1][1]].append((cls[i],texts[i]))
        res[conf]=per
    for line in sorted(set(res["report"])|set(res["x1"])):
        r=[c for c,t in res["report"].get(line,[])]; x=[c for c,t in res["x1"].get(line,[])]
        if set(r)!=set(x):
            print(f, line, res["report"].get(line), res["x1"].get(line))
