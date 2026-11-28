import json, gzip, sys
def load(p): return json.load(gzip.open(p) if p.endswith('.gz') else open(p))
for p in sys.argv[1:]:
    d = load(p); r = d['run']
    print('##', p, '| faults:', d['harness_faults'], '| notes:', [n for n in d['notes'] if 'system:' not in n and 'notation' not in n])
    for st in d['stages']:
        for a in st['attempts']:
            c = a['computations'][0]; q = c['queries'][0]; ob = a.get('observe') or {}
            raw = (ob.get('raw') or '')
            print('  s%d a%d %s/%s | ans %d %s | %s | alts %s peak %s | susp %s %s | steps stage %s restated %s restart %s rw %s | safety %s | head: %s' % (
                st['stage'], a['attempt'], a['posed']['how'], a['posed']['reason'], len(q['answers']), q['ended_by'],
                c['execution_state']['states'], c['alternatives']['at_boundary'], c['alternatives']['peak'],
                c['suspended']['at_boundary'], c['suspended']['items'], c['steps']['stage'], c['steps']['restated'],
                c['steps']['restart_cost'], c['steps']['repeated_work'], a['safety_limit']['action'], raw.split('\n')[0][:90]))
            if a.get('notes'): print('     notes:', str(a['notes'])[:600])
            sq = (a.get('store') or {}).get('quantities') or {}
            if sq: print('     store:', {k: (v.get('boundary'), (v.get('peak') or {}).get('value') if isinstance(v.get('peak'), dict) else v.get('peak')) for k, v in sq.items()})
