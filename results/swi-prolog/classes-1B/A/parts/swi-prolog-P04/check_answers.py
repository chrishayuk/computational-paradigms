# Checks each reported answer of every P04 record against the valid outcomes of problems/04.
import json, glob, os, re
RS = "./results/swi-prolog"
def valid(inst, v):
    v = v.strip().rstrip(".").strip()
    if inst in ("P04a","P04b"): return v == "X = 1"
    if inst in ("P04c","P04e"): return v == "true"
    m = re.fullmatch(r"S = \[(.*)\]", v)
    if not m: return False
    items = [x.strip() for x in m.group(1).split(",")] if m.group(1).strip() else []
    return all(x == "a" for x in items)
for f in sorted(glob.glob(f"{RS}/*/P04/raw*/*.json")):
    r = json.load(open(f)); inst = r["run"]["instance"]
    for s in r["stages"]:
        a = s["attempts"][-1]
        ans = [x["verbatim"] for x in a["computations"][0]["queries"][0]["answers"]]
        ok = [valid(inst, x) for x in ans]
        lens = None
        if inst in ("P04d","P04f") and ans:
            lens = [x.count("a") for x in ans]
        print(os.path.relpath(f, RS), "answers", len(ans), "valid", sum(ok), "invalid", len(ok)-sum(ok), "distinct", len(set(x.strip().rstrip('.').strip() for x in ans)), "lengths", lens)
