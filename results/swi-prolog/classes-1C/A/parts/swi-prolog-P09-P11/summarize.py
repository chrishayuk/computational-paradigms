# Summarise the raw records of P09-P11 (read-only), one block per stage.
import json, glob, sys, os
REPO = "/Users/christopherhay/cp-roles/classifier-1C-A/results/swi-prolog"
T = 400

def tr(s, n=T):
    if s is None: return None
    s = str(s)
    return s if len(s) <= n else s[:n] + f"...[{len(s)} chars]"

def summ(path):
    d = json.load(open(path))
    r = d["run"]
    print(f"##### {r['configuration']} {r['instance']} {r['mode']} {os.path.basename(path)} complete={r['complete']} {r.get('incomplete_reason')}")
    if d.get("harness_faults"): print("  harness_faults:", tr(json.dumps(d["harness_faults"]), 800))
    if d.get("notes"): print("  notes:", tr(json.dumps(d["notes"]), 800))
    if d.get("manual_actions"): print("  manual_actions:", d["manual_actions"])
    for st in d["stages"]:
        for a in st["attempts"]:
            p = a["posed"]
            print(f"  -- stage {st['stage']} attempt {a['attempt']} posed={p['how']}/{p['reason']} replayed={p['replayed']} commitments={p['replayed_commitments']}")
            for c in a["computations"]:
                q = c["queries"]
                for qq in q:
                    print(f"     [{c['id']}] query {qq['id']} cap={qq['cap']} ended_by={qq['ended_by']} on={qq['collected_on']} n={len(qq['answers'])}")
                    for an in qq["answers"][:6]:
                        print(f"        ans{an['index']}: {tr(an['verbatim'])!r} steps_at={an.get('steps_at')} alt_at={an.get('alternatives_at')}")
                es = c["execution_state"]
                print(f"     [{c['id']}] states={es['states']} determined={es['determined']}")
                print(f"        basis: {tr(es['basis'], 300)}")
                if es.get("error_verbatim"): print(f"        error: {tr(es['error_verbatim'], 600)!r}")
                s = c["steps"]
                print(f"        steps: restated={s['restated']} stage={s['stage']} restart={s['restart_cost']} ({s['restart_cost_method']}; {tr(s.get('restart_cost_source'),150)}) first={s['to_first_answer']} end={s['to_end']} budget={s['budget']} exhausted={s['budget_exhausted']}")
                al = c["alternatives"]
                print(f"        alternatives: boundary={al['at_boundary']} at_budget={al['at_budget']} peak={al['peak']} by_type={al['by_type']} problem_defined={al['problem_defined']}")
                print(f"        suspended: {json.dumps(c['suspended'])}")
                if c.get("problem_operations"): print("        problem_operations:", c["problem_operations"])
            o = a["observe"]
            print(f"     observe.raw: {tr(o['raw'], 700)!r} taken_on={o.get('taken_on')}")
            print(f"     observe.method: {tr(o.get('method'), 250)}")
            print(f"     observe.bindings: {tr(json.dumps(o.get('bindings')), 300)}")
            print(f"     print: {tr(a['print'], 500)!r}")
            print(f"     stdout: {tr(a['stdout'], 300)!r}")
            print(f"     stderr: {tr(a['stderr'], 500)!r}")
            if a.get("effects"): print(f"     effects: {json.dumps(a['effects'])}")
            if a.get("notes"): print(f"     attempt notes: {tr(json.dumps(a['notes']), 900)}")
            if a.get("manual_actions"): print(f"     manual_actions: {a['manual_actions']}")
            if a.get("separate_run"):
                sr = a["separate_run"]
                print(f"     separate_run: {tr(json.dumps({k: v for k, v in sr.items() if k not in ('stdout','stderr')}), 600)}")
                print(f"     separate_run stderr: {tr(sr.get('stderr'), 300)!r}")
            sl = a.get("safety_limit")
            if sl and sl.get("hit"): print("     SAFETY:", sl)
            if a.get("exit"): print("     exit:", a["exit"])
    if d.get("effects"):
        e = d["effects"]
        print("  effects record:", tr(json.dumps(e), 1500))

if __name__ == "__main__":
    for pat in sys.argv[1:]:
        for p in sorted(glob.glob(REPO + "/" + pat)):
            summ(p)
