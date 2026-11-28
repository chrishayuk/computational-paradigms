# Summarise run records (read-only) for classification.
import json, sys, glob, os
ROOT = "/Users/christopherhay/cp-roles/classifier-1B-A/results/swi-prolog"
def trunc(s, n=400):
    if s is None: return None
    s = str(s)
    return s if len(s) <= n else s[:n] + "...[%d chars]" % len(s)
def summ(path, full=False):
    r = json.load(open(path))
    run = r["run"]
    out = {"path": os.path.relpath(path, ROOT), "instance": run["instance"], "mode": run["mode"],
           "program": run["program"]["path"].split("/")[-1], "complete": run.get("complete"),
           "incomplete_reason": run.get("incomplete_reason"), "harness_faults": r.get("harness_faults"),
           "manual_actions": r.get("manual_actions"), "notes": [trunc(n, 300) for n in (r.get("notes") or [])]}
    st = []
    for s in r["stages"]:
        for a in s["attempts"]:
            d = {"stage": s["stage"], "attempt": a["attempt"], "posed": a["posed"]["how"] + "/" + str(a["posed"].get("reason")),
                 "replayed": a["posed"].get("replayed")}
            for c in a["computations"]:
                for q in c["queries"]:
                    d["answers"] = [trunc(x["verbatim"], 300) for x in q["answers"]]
                    d["ended_by"] = q["ended_by"]; d["collected_on"] = q.get("collected_on")
                es = c["execution_state"]
                d["states"] = es["states"]; d["err"] = trunc(es.get("error_verbatim"), 300); d["basis"] = trunc(es.get("basis"), 250)
                d["steps"] = {k: c["steps"].get(k) for k in ("restated", "restart_cost", "to_end", "stage", "budget_exhausted")}
                d["susp"] = c["suspended"]["items"]; d["alt"] = {k: c["alternatives"].get(k) for k in ("at_boundary", "at_budget", "problem_defined", "by_type")}
            d["observe"] = trunc(a["observe"]["raw"], 300); d["obs_taken"] = a["observe"].get("taken_on")
            d["stdout"] = trunc(a.get("stdout"), 200); d["stderr"] = trunc(a.get("stderr"), 300)
            d["exit"] = a["exit"]; d["safety"] = a["safety_limit"]["hit"]
            if a.get("separate_run"): d["separate_run"] = trunc(json.dumps(a["separate_run"]), 600 if not full else 5000)
            if a.get("notes"): d["anotes"] = trunc(json.dumps(a.get("notes")), 400)
            st.append(d)
    out["stages"] = st
    return out
if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(json.dumps(summ(p), indent=1))
