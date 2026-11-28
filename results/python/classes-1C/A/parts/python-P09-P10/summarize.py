# Summarize raw run records (read-only).
import json, sys, glob, os, gzip
REPO = "/Users/christopherhay/cp-roles/classifier-1C-A"
def load(p):
    return json.load(gzip.open(p) if p.endswith(".gz") else open(p))
def short(s, n=300):
    s = s if isinstance(s, str) else json.dumps(s)
    return s if len(s) <= n else s[:n] + "...(%d chars)" % len(s)
pats = sys.argv[1:]
for pat in pats:
    for p in sorted(glob.glob(f"{REPO}/results/python/{pat}")):
        r = load(p)
        print("=" * 100)
        print(os.path.relpath(p, REPO), r["run"]["mode"], r["run"]["posing"], "complete=", r["run"]["complete"], r["run"]["incomplete_reason"])
        if r["harness_faults"]: print(" HARNESS FAULTS", short(r["harness_faults"], 800))
        if r["notes"]: print(" notes", short(r["notes"], 800))
        for st in r["stages"]:
            for at in st["attempts"]:
                print(f"-- stage {st['stage']} attempt {at['attempt']} posed={at['posed']['how']}/{at['posed']['reason']} replayed={at['posed']['replayed']}")
                for c in at["computations"]:
                    es = c["execution_state"]
                    print(f"   [{c['id']}] states={es['states']} det={es['determined']} basis={short(es['basis'],200)}")
                    if es["error_verbatim"]: print("      error:", short(es["error_verbatim"][-400:], 400))
                    for q in c["queries"]:
                        print(f"      query {q['id']} ended_by={q['ended_by']} answers={[a['verbatim'] for a in q['answers']]}")
                    stp = c["steps"]
                    print(f"      steps stage={stp['stage']} restated={stp['restated']} budget_exh={stp['budget_exhausted']} restart={stp['restart_cost']} first={stp['to_first_answer']}")
                    a = c["alternatives"]; s = c["suspended"]
                    print(f"      alts bnd={a['at_boundary']} atbud={a['at_budget']} by_type={a['by_type']} pd={a['problem_defined']}; susp bnd={s['at_boundary']} items={short(s['items'],200)}")
                    if c.get("problem_operations"): print("      probops", c["problem_operations"])
                print("   observe.raw:", short(at["observe"]["raw"], 1200).replace("\n", "\n               "))
                print("   stdout:", short(at["stdout"], 400).replace("\n", " | "))
                if at["stderr"]: print("   stderr:", short(at["stderr"][-400:], 400).replace("\n", " | "))
                if at["store"]["quantities"]: print("   store:", short(at["store"]["quantities"], 400))
                print("   safety:", at["safety_limit"], "exit", at["exit"], "notes", short(at["notes"], 400))
