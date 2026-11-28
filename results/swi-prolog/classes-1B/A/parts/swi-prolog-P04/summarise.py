import json, sys, glob, os
root = "./results/swi-prolog"
for c in ["plain","tabling","coroutines","constraints","session"]:
    for f in sorted(glob.glob(f"{root}/{c}/P04/raw*/*.json")):
        r = json.load(open(f))
        print("=====", os.path.relpath(f, root), "faults:", r.get("harness_faults"), "notes:", [n[:200] for n in r.get("notes",[]) if "system_build" not in n])
        for s in r["stages"]:
            for a in s["attempts"]:
                print(" stage", s["stage"], "attempt", a["attempt"], "limit", a["limit_s"], "posed", a["posed"]["how"], a["posed"]["reason"], "safety", a["safety_limit"], "exit", a["exit"])
                for comp in a["computations"]:
                    for q in comp["queries"]:
                        ans = q["answers"]
                        print("   answers n=%d ended_by=%s collected_on=%s" % (len(ans), q["ended_by"], q["collected_on"]))
                        for x in ans[:4]: print("     ", json.dumps(x)[:300])
                        if len(ans) > 4: print("      ... last:", json.dumps(ans[-1])[:300])
                    print("   state", comp["execution_state"]["states"], comp["execution_state"]["error_verbatim"])
                    st = comp["steps"]; print("   steps restated", st["restated"], "first", st["to_first_answer"], "to_end", st["to_end"], "between", st["between_answers"][:5])
                    print("   alts", {k: comp["alternatives"][k] for k in ["at_boundary","at_budget","peak","by_type"]})
                    print("   susp", comp["suspended"])
                print("   observe", json.dumps(a["observe"]["raw"])[:300], "|", a["observe"]["method"][:100], a["observe"]["taken_on"])
                print("   print", json.dumps(a["print"])[:300])
                print("   store", json.dumps(a["store"])[:400])
                if a["stderr"]: print("   stderr", a["stderr"][:300])
                if a.get("separate_run"): print("   separate", json.dumps(a["separate_run"])[:400])
                if a.get("manual_actions"): print("   manual", a["manual_actions"])
