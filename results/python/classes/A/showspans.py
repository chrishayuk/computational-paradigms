import json, sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keys import load
d = json.load(open("tokens.json"))
t = sys.argv[1]; src, toks = load(t)
for s in d[t]:
    txt = " ".join(toks[i][2] for i in range(s["from"], s["to"] + 1))
    print("%4d-%-4d %s %-55s | %s" % (s["from"], s["to"], s["class"], s["construct"][:55], txt[:110]))
