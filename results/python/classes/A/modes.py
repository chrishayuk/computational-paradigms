# Compare cost and storage records with the behaviour record of the same configuration and instance.
import json, glob, os, re
ROOT = "/Users/christopherhay/cp-roles/classifier-A/results/python"
def key(path):
    b = os.path.basename(path).split(".")
    return b[:-3] if False else ".".join(b[:-3])  # instance id
def summ(r):
    out = []
    for st in r["stages"]:
        for at in st["attempts"]:
            for c in at["computations"]:
                ans = [a["verbatim"] for q in c["queries"] for a in q["answers"]]
                out.append(dict(stage=st["stage"], attempt=at["attempt"], answers=ans,
                    ended=[q["ended_by"] for q in c["queries"]], states=c["execution_state"]["states"],
                    susp=(c.get("suspended") or {}).get("at_boundary"), alts=(c.get("alternatives") or {}).get("at_boundary"),
                    observe=re.sub(r"0x[0-9a-f]+", "0x?", at["observe"]["raw"]), safety=at["safety_limit"]["hit"],
                    err=c["execution_state"].get("error_verbatim")))
    return out
recs = {}
for p in glob.glob(ROOT + "/*/P0?/raw/*.json"):
    rel = os.path.relpath(p, ROOT); conf = rel.split("/")[0]
    r = json.load(open(p)); recs[(conf, r["run"]["instance"], r["run"]["mode"])] = (rel, summ(r))
n = 0
for (conf, inst, mode), (rel, s) in sorted(recs.items()):
    if mode == "behaviour": continue
    brel, b = recs[(conf, inst, "behaviour")]
    if len(b) != len(s): print("LEN DIFF", rel); continue
    for x, y in zip(b, s):
        d = {k: (x[k], y[k]) for k in x if x[k] != y[k]}
        if d:
            n += 1; print(conf, inst, mode, "stage", x["stage"], {k: (str(v[0])[:300], str(v[1])[:300]) for k, v in d.items()})
print("differences:", n, "records compared:", sum(1 for k in recs if k[2] != "behaviour"))
