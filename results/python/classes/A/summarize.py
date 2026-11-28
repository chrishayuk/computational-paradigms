# Summarize raw run records: per stage, answers, states, observe.raw, print, errors.
import json, sys, glob, os
ROOT = "./results/python"
def trunc(x, n=600):
    s = x if isinstance(x, str) else json.dumps(x)
    return s if len(s) <= n else s[:n] + "...[%d chars]" % len(s)
mode = sys.argv[1] if len(sys.argv) > 1 else "behaviour"
for path in sorted(glob.glob(ROOT + "/*/P0?/raw/*.%s.*.json" % mode)):
    r = json.load(open(path))
    run = r["run"]
    print("##", os.path.relpath(path, ROOT), run["posing"], "complete=", run.get("complete"), "faults=", r.get("harness_faults"))
    for st in r["stages"]:
        for at in st["attempts"]:
            print("  stage", st.get("stage"), "attempt", at["attempt"], "posed", at["posed"]["how"], at["posed"]["reason"], "safety", at["safety_limit"]["hit"])
            for c in at["computations"]:
                for q in c["queries"]:
                    print("    answers:", trunc([a.get("text", a) if isinstance(a, dict) else a for a in q["answers"]]), "ended_by", q["ended_by"])
                es = c["execution_state"]
                print("    state:", es["states"], "det", es["determined"], "err", trunc(es.get("error_verbatim") or "", 300))
                print("    steps:", {k: c["steps"].get(k) for k in ("stage", "restated", "budget_exhausted")}, "alts", trunc(c.get("alternatives"), 200), "susp", trunc(c.get("suspended"), 300))
                if c.get("problem_operations"): print("    ops:", c["problem_operations"])
            print("    observe:", trunc(at["observe"]["raw"], 900))
            print("    print:", trunc(at["print"], 400))
            if at.get("manual_actions"): print("    manual:", at["manual_actions"])
            if at.get("notes"): print("    notes:", trunc(at["notes"], 300))
