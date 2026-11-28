import json,sys
from lines import load
d=json.load(open('tokens.json'))
for t in sys.argv[1:]:
    src,toks,ctx=load(t)
    print('=====',t)
    for s in d[t]:
        print(f"{s['from']:4d}-{s['to']:4d} {s['class']} {s['construct'][:60]:60s} | "+' '.join(x[2] for x in toks[s['from']:s['to']+1])[:110])
