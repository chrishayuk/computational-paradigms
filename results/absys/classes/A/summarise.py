# Summarise raw records: per stage the facts needed for classing outcomes.
import json, sys, glob, os
ROOT = './results/absys'
def summ(path, maxprint=1200):
    d = json.load(open(path))
    r = d['run']
    out = [f"### {os.path.relpath(path, ROOT)}  mode={r['mode']} complete={r.get('complete')} {r.get('incomplete_reason')}"]
    if d.get('harness_faults'): out.append(f"  harness_faults: {d['harness_faults']}")
    if d.get('notes'): out.append(f"  notes: {d['notes']}")
    if d.get('manual_actions'): out.append(f"  manual_actions: {d['manual_actions']}")
    for s in d['stages']:
        for a in s['attempts']:
            p = a['posed']
            out.append(f" stage {s['stage']} att {a['attempt']} posed={p['how']}/{p['reason']} cab={p['continued_after_budget']} wall={a['wall_time_s']} safety={a['safety_limit']} exit={a['exit']}")
            if a.get('notes'): out.append(f"  att notes: {a['notes']}")
            if a.get('manual_actions'): out.append(f"  att manual: {a['manual_actions']}")
            for c in a['computations']:
                es = c['execution_state']
                st = c['steps']
                q = c['queries'][0] if c['queries'] else None
                out.append(f"  comp {c['id']}: states={es['states']} basis={es['basis']!r} err={es['error_verbatim']!r}")
                if q: out.append(f"   answers={len(q['answers'])} ended_by={q['ended_by']}")
                out.append(f"   steps: stage={st['stage']} restated={st['restated']} restart={st['restart_cost']} to_end={st['to_end']} exhausted={st['budget_exhausted']} rw={st['repeated_work']}")
                al = c['alternatives']; su = c['suspended']
                out.append(f"   alts: boundary={al['at_boundary']} peak={al['peak']} at_budget={al['at_budget']} held_as={al['held_as']}")
                out.append(f"   susp: boundary={su['at_boundary']} peak={su['peak']} items={su['items']}")
            stq = a['store']['quantities']
            if stq: out.append("   store: " + ", ".join(f"{k}={v.get('boundary')}/{(v.get('peak') or {}).get('value') if isinstance(v.get('peak'),dict) else v.get('peak')}" for k,v in stq.items()))
            pr = a['print'] or ''
            if len(pr) > maxprint: pr = pr[:maxprint] + f"\n...[{len(a['print'])} chars]...\n" + a['print'][-400:]
            out.append("   print:\n" + "\n".join("     |"+l for l in pr.splitlines()))
            b = a['observe']['bindings']
            if b:
                for k,v in b.items():
                    vv = v if len(v) < 600 else v[:600]+f'...[{len(v)}]'
                    out.append(f"   bind {k}: {vv!r}")
    return "\n".join(out)
if __name__ == '__main__':
    mp = int(os.environ.get('MAXPRINT', '1200'))
    for p in sys.argv[1:]:
        print(summ(p, mp)); print()
