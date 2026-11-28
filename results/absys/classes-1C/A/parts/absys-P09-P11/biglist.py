# Show a record's observe.raw / bindings with long lists shortened (classifier's checking script).
import json,gzip,sys,re
def load(p):
    if p.endswith('.gz'):
        with gzip.open(p,'rt') as f: return json.load(f)
    with open(p) as f: return json.load(f)
def shorten(s):
    def rep(m):
        t=m.group(0); items=t.split(';')
        return ';'.join(items[:6])+f';...<{len(items)} items>...;'+';'.join(items[-4:])
    return re.sub(r'\[[^\[\]]{400,}\]',rep,s)
for p in sys.argv[1:]:
    d=load(p)
    for st in d['stages']:
        for a in st['attempts']:
            ob=a.get('observe') or {}
            print('== stage',st['stage'],'attempt',a['attempt'])
            print(shorten(ob.get('raw') or ''))
            for c in a['computations']:
                s=c['steps']
                print(' comp',c['id'],'steps',s['stage'],s['restated'],s['restart_cost'],'to_end',s['to_end'],'rep',json.dumps(s['repeated_work'])[:300],'exh',s['budget_exhausted'])
                print(' alts',json.dumps(c['alternatives'])[:300]); print(' susp',json.dumps(c['suspended'])[:400])
            q=(a.get('store') or {}).get('quantities')
            if q: print(' store',json.dumps(q)[:1500])
            if a.get('notes'): print(' notes',a['notes'])
            if a.get('separate_run'): print(' separate_run',json.dumps(a['separate_run'])[:800])
