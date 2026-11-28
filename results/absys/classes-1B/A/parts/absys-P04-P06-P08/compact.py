import json,sys,glob,os
def comp(path, rawlen):
    d=json.load(open(path))
    r=d['run']
    out=[f"#### {path} | {r['mode']} | {r['program']['path']} | faults={len(d.get('harness_faults') or [])}"]
    for s in d['stages']:
        for a in s['attempts']:
            for c in a['computations']:
                e=c['execution_state']
                q=c['queries'][0] if c['queries'] else {}
                st=c['steps']
                out.append(f"  S{s['stage']}.{a['attempt']} {a['posed']['how']}/{a['posed']['reason']} states={e['states']} err={(e['error_verbatim'] or '')[:120]!r} ended={q.get('ended_by')} n={len(q.get('answers',[]))} alts={c['alternatives']['at_boundary']} susp={c['suspended']['at_boundary']} {c['suspended'].get('items')} steps={st.get('stage')} restated={st.get('restated')} rw={st.get('repeated_work')}")
            ob=a['observe']
            if ob and rawlen:
                out.append('    '+(ob.get('raw') or '')[:rawlen].replace('\n','\n    '))
    print('\n'.join(out))
rawlen=int(sys.argv[1])
for p in sys.argv[2:]: comp(p,rawlen)
