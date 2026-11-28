# Compare cost and storage records with the behaviour record (read-only).
import json, glob, re, os
REPO = "/Users/christopherhay/cp-roles/classifier-1C-A"
def key(r):
    out = []
    for st in r["stages"]:
        at = st["attempts"][-1]
        comps = {}
        for c in at["computations"]:
            comps[c["id"]] = (tuple(c["execution_state"]["states"]),
                              tuple(a["verbatim"] for q in c["queries"] for a in q["answers"]),
                              tuple(q["ended_by"] for q in c["queries"]),
                              c["suspended"]["at_boundary"], c["alternatives"]["at_boundary"],
                              json.dumps(c["alternatives"]["problem_defined"]))
        raw = re.sub(r"0x[0-9a-f]+", "0x", at["observe"]["raw"])
        out.append((st["stage"], len(st["attempts"]), at["posed"]["how"], comps, raw, at["stdout"]))
    return out
for cfg in ["core", "extended", "stdlib-concurrency"]:
    for prob in ["P09", "P10"]:
        recs = sorted(glob.glob(f"{REPO}/results/python/{cfg}/{prob}/raw/*.json*"))
        inst = {}
        for p in recs:
            b = os.path.basename(p); parts = b.split(".")
            mode = [x for x in parts if x in ("behaviour", "cost", "storage")][0]
            i = ".".join(parts[:parts.index(mode)])
            inst.setdefault(i, {})[mode] = p
        for i, m in inst.items():
            kb = key(json.load(open(m["behaviour"])))
            for mode in ("cost", "storage"):
                r = json.load(open(m[mode]))
                km = key(r)
                if r["harness_faults"]: print(cfg, i, mode, "FAULTS", r["harness_faults"])
                for sb, sm in zip(kb, km):
                    for idx, name in enumerate(["stage", "attempts", "posed", "comps", "raw", "stdout"]):
                        if sb[idx] != sm[idx]:
                            if name == "comps":
                                for cid in set(sb[3]) | set(sm[3]):
                                    if sb[3].get(cid) != sm[3].get(cid):
                                        print(cfg, i, mode, "stage", sb[0], cid, "B:", sb[3].get(cid), "M:", sm[3].get(cid))
                            else:
                                print(cfg, i, mode, "stage", sb[0], name, "B:", str(sb[idx])[:300], "| M:", str(sm[idx])[:300])
print("done")
