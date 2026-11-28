import json, gzip, sys
def load(p):
    return json.load(gzip.open(p) if p.endswith('.gz') else open(p))
def cut(s, n):
    if s is None: return None
    s = str(s)
    return s if len(s) <= n else s[:n] + f'...[{len(s)} chars]...' + s[-n//2:]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 600
d = load(sys.argv[1])
r = d['run']
print('RUN', r['configuration'], r['instance'], r['mode'], 'complete', r['complete'], r['incomplete_reason'])
print('faults', json.dumps(d['harness_faults'])[:3000])
print('notes', json.dumps(d['notes'])[:2000])
print('manual', d['manual_actions'])
for st in d['stages']:
    print('==== STAGE', st['stage'], 'attempts', len(st['attempts']))
    for a in st['attempts']:
        print(' attempt', a['attempt'], 'posed', json.dumps(a['posed'])[:400])
        for c in a['computations']:
            for q in c['queries']:
                print('  answers', len(q['answers']), 'ended_by', q['ended_by'])
                for an in q['answers'][:4]: print('   ', cut(an['verbatim'], n))
            print('  exec', json.dumps(c['execution_state'])[:800])
            print('  steps', json.dumps(c['steps'])[:600])
            print('  alts', json.dumps(c['alternatives'])[:400])
            print('  susp', json.dumps(c['suspended'])[:400])
        ob = a.get('observe') or {}
        print('  observe.raw', cut(ob.get('raw'), n))
        print('  bindings', cut(json.dumps(ob.get('bindings')), n))
        print('  store', cut(json.dumps(a.get('store')), 1500))
        print('  exit', a.get('exit'), 'safety', a.get('safety_limit'), 'wall', a.get('wall_time_s'))
        print('  stderr', cut(a.get('stderr'), 400))
        print('  sep', cut(json.dumps(a.get('separate_run')), 800))
        print('  notes', cut(json.dumps(a.get('notes')), 1500))
