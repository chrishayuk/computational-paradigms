import json, sys, glob, os
ROOT = "./results/python"
mode = sys.argv[1]; pat = sys.argv[2] if len(sys.argv) > 2 else "*"
def t(s, n): s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False); return s if len(s) <= n else s[:n] + "..[%d]" % len(s)
for path in sorted(glob.glob(ROOT + "/%s/P0?/raw/*.%s.*.json" % (pat, mode))):
    r = json.load(open(path))
    print("##", os.path.relpath(path, ROOT), "faults=", r.get("harness_faults"), "manual=", r.get("manual_actions"))
    for st in r["stages"]:
        for at in st["attempts"]:
            for c in at["computations"]:
                ans = [a["verbatim"] for q in c["queries"] for a in q["answers"]]
                eb = [q["ended_by"] for q in c["queries"]]
                es = c["execution_state"]
                print(" s%s a%s %s/%s %s det=%s ans=%s ended=%s susp=%s alts=%s steps=%s ops=%s" % (st["stage"], at["attempt"], at["posed"]["how"], at["posed"]["reason"], es["states"], es["determined"], t(ans, 300), eb, c["suspended"]["at_boundary"] if c.get("suspended") else None, c["alternatives"]["at_boundary"] if c.get("alternatives") else None, c["steps"].get("stage"), c.get("problem_operations")))
                if es.get("error_verbatim"): print("   ERR", t(es["error_verbatim"], 400))
            print("   OBS", t(at["observe"]["raw"].replace("\n", " | "), int(sys.argv[3]) if len(sys.argv) > 3 else 500))
            if at.get("manual_actions"): print("   MANUAL", at["manual_actions"])
            if at["safety_limit"]["hit"]: print("   SAFETY", at["safety_limit"])
