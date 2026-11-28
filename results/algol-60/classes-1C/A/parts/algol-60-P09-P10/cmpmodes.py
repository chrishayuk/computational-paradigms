import json,glob,os
R='/Users/christopherhay/cp-roles/classifier-1C-A/results/algol-60'
def key(r):
    out={}
    for st in r['stages']:
        at=st['attempts'][-1]
        for c in at['computations']:
            out[(st['stage'],c['id'])]=(tuple(c['execution_state'].get('states') or []),tuple(a['verbatim'] for q in c['queries'] for a in q['answers']),tuple(q['ended_by'] for q in c['queries']),len(st['attempts']),at['observe'].get('raw'))
    return out
for cfg in ['report','x1']:
    for p in ['P09','P10']:
        for b in sorted(glob.glob(f'{R}/{cfg}/{p}/raw/*.behaviour.*.json')):
            inst=os.path.basename(b).split('.behaviour')[0]
            kb=key(json.load(open(b)))
            for m in ['cost','storage']:
                for f in glob.glob(f'{R}/{cfg}/{p}/raw/{inst}.{m}.*.json'):
                    km=key(json.load(open(f)))
                    diffs=[(k,kb.get(k),km.get(k)) for k in sorted(set(kb)|set(km)) if kb.get(k)!=km.get(k)]
                    print(cfg,inst,m,os.path.basename(f),'SAME' if not diffs else diffs)
