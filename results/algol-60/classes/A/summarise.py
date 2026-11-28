# Summarise every raw record of algol-60 batch 1A: per stage, the facts needed for classification.
import json, sys, glob, os
ROOT = "."
def summ(path):
    r = json.load(open(path))
    run = r["run"]
    out = {"record": os.path.relpath(path, ROOT), "configuration": run["configuration"], "instance": run["instance"],
           "mode": run["mode"], "program": os.path.basename(run["program"]["path"]), "posing": run.get("posing"),
           "complete": run.get("complete"), "faults": r.get("harness_faults"), "manual": r.get("manual_actions"), "stages": []}
    for s in r["stages"]:
        atts = []
        for a in s["attempts"]:
            comps = []
            for c in a["computations"]:
                comps.append({"id": c["id"],
                              "answers": [(q["id"], q["cap"], [x["verbatim"] for x in q["answers"]], q["ended_by"]) for q in c["queries"]],
                              "states": c["execution_state"]["states"], "determined": c["execution_state"]["determined"],
                              "err": c["execution_state"]["error_verbatim"],
                              "steps": {k: c["steps"].get(k) for k in ("stage", "restated", "restart_cost", "to_first_answer", "to_end", "budget_exhausted", "repeated_work")},
                              "susp": c["suspended"]["items"], "alts": c["alternatives"]["by_type"], "ops": c.get("problem_operations")})
            atts.append({"attempt": a["attempt"], "posed": (a["posed"]["how"], a["posed"]["reason"], a["posed"]["replayed"]),
                         "observe": a["observe"]["raw"], "bindings": a["observe"]["bindings"], "comps": comps,
                         "safety": a["safety_limit"]["hit"], "exit": a["exit"], "manual": a["manual_actions"],
                         "store": a["store"]["quantities"] if r["run"]["mode"] == "storage" else None,
                         "notes": a.get("notes")})
        out["stages"].append({"stage": s["stage"], "attempts": atts})
    return out
if __name__ == "__main__":
    for p in sorted(glob.glob(ROOT + "/results/algol-60/*/P0?/raw/*.json")):
        print(json.dumps(summ(p), ensure_ascii=False))
