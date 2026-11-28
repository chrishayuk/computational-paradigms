import json, glob, os
root = "/Users/christopherhay/cp-roles/classifier-1B-A2/results/swi-prolog"
for c in ["plain","tabling","coroutines","constraints","session"]:
    for f in sorted(glob.glob(f"{root}/{c}/P04/raw*/*.json")):
        r = json.load(open(f))
        for s in r["stages"]:
            for a in s["attempts"]:
                comp = a["computations"][0]; q = comp["queries"][0]
                ans = [x["verbatim"] for x in q["answers"]]
                print(c, os.path.basename(f)[:20], "att%d" % a["attempt"], a["posed"]["how"], "n=%d" % len(ans), q["ended_by"], comp["execution_state"]["states"],
                      "steps", comp["steps"]["restated"], "first", comp["steps"]["to_first_answer"],
                      "alts_b", comp["alternatives"]["at_boundary"], "alts_bud", comp["alternatives"]["at_budget"], "pk", comp["alternatives"]["peak"],
                      "susp", comp["suspended"]["at_boundary"], "obs", json.dumps(a["observe"]["raw"])[:40], "taken", a["observe"]["taken_on"],
                      "ans1", json.dumps(ans[:2])[:60], "exit", a["exit"]["status"], "faults", len(r["harness_faults"]), "sep", bool(a.get("separate_run")))
