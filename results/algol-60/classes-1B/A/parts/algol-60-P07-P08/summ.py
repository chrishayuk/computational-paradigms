import json, glob, sys, os
R="/Users/christopherhay/cp-roles/classifier-1B-A/"
def summ(path, full=True):
    d=json.load(open(path))
    run=d["run"]
    out=[]
    out.append(f"== {path.replace(R,'')} posing={run['posing']} complete={run['complete']} faults={d.get('harness_faults')} manual={d.get('manual_actions')}")
    for st in d["stages"]:
        for at in st["attempts"]:
            for c in at["computations"]:
                ans=[a["verbatim"] for q in c["queries"] for a in q["answers"]]
                es=c["execution_state"]
                out.append(f" stage {st['stage']} att {at['attempt']} posed={at['posed']['how']}/{at['posed'].get('reason')} replayed={at['posed'].get('replayed')} states={es['states']} err={es['error_verbatim']!r}")
                out.append(f"   answers={ans}")
                out.append(f"   susp={c['suspended']['items']} alt={c['alternatives']['by_type']} ops={c['problem_operations']} steps={c['steps']['stage']} restated={c['steps']['restated']} rc={c['steps']['restart_cost']} budgetexh={c['steps']['budget_exhausted']}")
            if full:
                out.append("   observe="+repr(at["observe"]["raw"]))
                out.append(f"   exit={at.get('exit')} safety={at.get('safety_limit',{}).get('hit')} stderr={(at.get('stderr') or '')[-200:]!r}")
                out.append(f"   store={ {k:v for k,v in (at.get('store',{}).get('quantities') or {}).items()} if at.get('store',{}).get('quantities') else None}")
                out.append(f"   notes={[n[:200] for n in at.get('notes',[])]}")
    return "\n".join(out)
if __name__=="__main__":
    for p in sys.argv[1:]:
        print(summ(p, full="behaviour" in p))
