import json, sys
def short(s, n=300):
    if s is None: return None
    s = str(s)
    return s if len(s) <= n else s[:n] + f'...<{len(s)} chars>...' + s[-150:]
for path in sys.argv[1:]:
    r = json.load(open(path))
    run = r['run']
    print('#####', path.split('results/algol-60/')[-1])
    print(' mode', run['mode'], 'posing', run.get('posing'), 'complete', run.get('complete'), run.get('incomplete_reason'))
    print(' faults', r.get('harness_faults'), 'manual', r.get('manual_actions'))
    if r.get('notes'): print(' notes', short(r['notes'], 600))
    for st in r['stages']:
        for at in st['attempts']:
            print(f" stage {st['stage']} attempt {at['attempt']} posed {at['posed'].get('how')}/{at['posed'].get('reason')} replayed {at['posed'].get('replayed')} safety {at.get('safety_limit')}")
            for c in at['computations']:
                for q in c['queries']:
                    print('   answers', [a.get('verbatim') for a in q['answers']][:6], 'n', len(q['answers']), 'ended_by', q['ended_by'])
                es = c['execution_state']
                print('   state', es.get('states'), 'det', es.get('determined'), 'err', short(es.get('error_verbatim'), 200))
                s = c.get('steps') or {}
                print('   steps', {k: s.get(k) for k in ('budget', 'budget_exhausted', 'stage', 'restated', 'restart_cost', 'to_first_answer', 'to_end', 'repeated_work')})
                al=c.get('alternatives') or {}; su=c.get('suspended') or {}
                print('   alts', {k:al.get(k) for k in ('at_boundary','held_as','by_type','problem_defined')}, 'susp', {k:su.get(k) for k in ('at_boundary','items')}, 'ops', c.get('problem_operations'))
            print('   observe', short((at.get('observe') or {}).get('raw'), 500), (at.get('observe') or {}).get('bindings'))
            print('   store', short(json.dumps(at.get('store')), 400) if at.get('store') else None)
            print('   stdout', short(at.get('stdout'), 400), 'n_answers_in_stdout', (at.get('stdout') or '').count('[answer]'))
            print('   stderr', short(at.get('stderr'), 300), 'exit', at.get('exit'))
            if at.get('notes'): print('   notes', short(at.get('notes'), 400))
            if at.get('manual_actions'): print('   manual', at['manual_actions'])
