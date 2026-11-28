import json, sys, glob, os, re, collections
ROOT = "/Users/christopherhay/cp-roles/classifier-1B-A/results/swi-prolog"
def norm(s): return re.sub(r"_[0-9]+|_G[0-9]+", "_N", s or "")
def stageinfo(path):
    r = json.load(open(path)); out = {}
    for s in r["stages"]:
        a = s["attempts"][-1]; c = a["computations"][0]; q = c["queries"][0] if c["queries"] else {}
        src = c["steps"].get("restart_cost_source") or ""
        out[s["stage"]] = {"attempts": len(s["attempts"]), "posed": a["posed"]["how"], "answers": [x["verbatim"] for x in q.get("answers", [])],
            "ended_by": q.get("ended_by"), "states": c["execution_state"]["states"], "err": norm(c["execution_state"].get("error_verbatim")),
            "observe": a["observe"]["raw"], "reached": not re.search(r"before stage \d+ was posed|did not reach", src),
            "susp": c["suspended"]["items"], "safety": a["safety_limit"]["hit"]}
    return r, out
recs = collections.defaultdict(dict)
for p in sorted(glob.glob(os.path.join(ROOT, "*/P0[5-8]/raw*/*.json"))):
    r = json.load(open(p)); run = r["run"]
    conf = os.path.relpath(p, ROOT).split("/")[0]; sub = os.path.relpath(p, ROOT).split("/")[2]
    key = (conf, run["instance"], run["program"]["path"].split("/")[-1])
    recs[key].setdefault(run["mode"] + ("@" + sub if sub != "raw" else ""), []).append(os.path.relpath(p, ROOT))
for key, modes in sorted(recs.items()):
    if "behaviour" not in modes: print("NO BEHAVIOUR", key, modes); continue
    if len(modes["behaviour"]) > 1: print("MULTIPLE BEHAVIOUR", key, modes["behaviour"])
    _, b = stageinfo(os.path.join(ROOT, modes["behaviour"][0]))
    for m, paths in modes.items():
        if m == "behaviour": continue
        for p in paths:
            r, o = stageinfo(os.path.join(ROOT, p))
            for st in sorted(set(b) | set(o)):
                if st not in o or st not in b: print("MISSING STAGE", key, m, p, st); continue
                diffs = {k: (b[st][k], o[st][k]) for k in b[st] if b[st][k] != o[st][k] and k not in ("susp",)}
                if b[st]["susp"] != o[st]["susp"]: diffs["susp"] = (b[st]["susp"], o[st]["susp"])
                if diffs: print("DIFF", key, m, p, "stage", st, json.dumps(diffs)[:600])
print("keys", len(recs))
