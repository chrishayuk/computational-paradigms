# Compare cost/storage records with the behaviour record of the same configuration/instance (read-only).
import json, glob, collections
REPO = "/Users/christopherhay/cp-roles/classifier-1C-A/results/swi-prolog"
def key(p):
    d = json.load(open(p)); r = d["run"]
    out = []
    for st in d["stages"]:
        a = st["attempts"][-1]
        for c in a["computations"]:
            out.append((st["stage"], len(st["attempts"]), c["id"], tuple(x["verbatim"] for q in c["queries"] for x in q["answers"]),
                        tuple(q["ended_by"] for q in c["queries"]), tuple(c["execution_state"]["states"]),
                        c["execution_state"].get("error_verbatim"), c["steps"]["restated"], c["steps"]["budget_exhausted"],
                        a["observe"]["raw"][:300]))
    return r["configuration"], r["instance"], r["mode"], out, d.get("harness_faults")
recs = collections.defaultdict(dict)
for p in sorted(glob.glob(REPO + "/*/P09/raw/*.json") + glob.glob(REPO + "/*/P1[01]/raw/*.json")):
    c, i, m, out, hf = key(p)
    recs[(c, i)][m] = (p.split('/results/')[-1] if '/results/' in p else p, out, hf)
for k, v in sorted(recs.items()):
    b = v.get("behaviour")
    for m in ("cost", "storage"):
        if m not in v: print("MISSING", k, m); continue
        path, out, hf = v[m]
        if hf: print("FAULTS", k, m, hf)
        for x, y in zip(b[1], out):
            diffs = [n for n, (p, q) in enumerate(zip(x, y)) if p != q]
            names = ["stage", "attempts", "comp", "answers", "ended_by", "states", "error", "steps", "budget_exh", "observe"]
            dn = [names[n] for n in diffs if names[n] not in ()]
            if dn:
                print(k, m, "stage", x[0], x[2], dn, [ (x[n] if names[n]!='observe' else x[n][:80], y[n] if names[n]!='observe' else y[n][:80]) for n in diffs if names[n] in ('answers','states','ended_by','error','steps','attempts','budget_exh','observe')])
