# One line per stage/attempt/computation of each record (read-only).
import json, glob, sys
REPO = "/Users/christopherhay/cp-roles/classifier-1C-A/results/swi-prolog"
def tr(s, n=160):
    s = "" if s is None else str(s)
    return s if len(s) <= n else s[:n] + f"..[{len(s)}]"
for pat in sys.argv[1:]:
    for p in sorted(glob.glob(REPO + "/" + pat)):
        d = json.load(open(p))
        r = d["run"]
        hf = " FAULTS" if d.get("harness_faults") else ""
        print(f"## {r['configuration']} {r['instance']} {r['mode']} {p.split('/')[-1]}{hf}")
        for st in d["stages"]:
            for a in st["attempts"]:
                po = a["posed"]
                for c in a["computations"]:
                    ans = [x["verbatim"] for q in c["queries"] for x in q["answers"]]
                    eb = [q["ended_by"] for q in c["queries"]]
                    on = [q["collected_on"] for q in c["queries"]]
                    s = c["steps"]
                    print(f"  s{st['stage']}a{a['attempt']} {po['how'][:3]}/{po['reason']} rc={po['replayed_commitments']} [{c['id']}] {c['execution_state']['states']} {eb} {on} ans={[tr(x,120) for x in ans]} err={tr(c['execution_state'].get('error_verbatim'),120)!r} steps={s['restated']}/{s['to_end']} rcost={s['restart_cost']} susp={c['suspended'].get('at_boundary')} alt={c['alternatives'].get('at_boundary')}/{c['alternatives'].get('at_budget')}")
                print(f"      observe({a['observe'].get('taken_on')})={tr(a['observe']['raw'],200)!r} print={tr(a['print'],160)!r}")
                if a.get("effects"): print(f"      effects={[(e['seq'], e['entry'], e['stage'], e.get('during_replay_of')) for e in a['effects']]}")
                if a.get("notes"): print(f"      notes={tr(json.dumps(a['notes']), 600)}")
                if a.get("separate_run"):
                    sr = a["separate_run"]
                    print(f"      separate_run keys={list(sr.keys())}")
                if a.get("stderr"): print(f"      stderr={tr(a['stderr'],200)!r}")
                if a.get("manual_actions"): print(f"      manual={a['manual_actions']}")
        if d.get("harness_faults"): print("  harness_faults:", tr(json.dumps(d["harness_faults"]), 600))
        if d.get("effects"):
            e = d["effects"]
            la = e.get("log_after_run") or []
            print(f"  effects: before={e.get('entries_before_run')} log={[(x['seq'], x['entry'], x['run_id'][-17:], x['stage'], x.get('during_replay_of')) for x in la]}")
