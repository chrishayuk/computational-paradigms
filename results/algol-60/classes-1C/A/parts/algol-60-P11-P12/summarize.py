"""Summarise ALGOL 60 P11/P12 raw records (read-only). Usage: python3 -I summarize.py RECORD..."""
import json, sys, gzip

def load(p):
    if p.endswith('.gz'):
        with gzip.open(p, 'rt') as f:
            return json.load(f)
    with open(p) as f:
        return json.load(f)

for p in sys.argv[1:]:
    d = load(p)
    r = d['run']
    print('#', p.split('/')[-1], r['configuration'], r['instance'], r['mode'], 'posing', r['posing'], 'complete', r['complete'])
    for s in d['stages']:
        for a in s['attempts']:
            po = a['posed']
            print(' stage', s['stage'], 'att', a['attempt'], po['how'], po['reason'], 'replayed', po['replayed'], 'rc', po['replayed_commitments'])
            for c in a['computations']:
                for q in c['queries']:
                    print('   answers', [x['verbatim'] for x in q['answers']], 'ended', q['ended_by'],
                          'steps_at', [x.get('steps_at') for x in q['answers']])
                es = c['execution_state']
                print('   state', es['states'], es['determined'], 'err', es['error_verbatim'])
                st = c['steps']
                print('   steps stage', st['stage'], 'restated', st['restated'], 'restart', st['restart_cost'],
                      'first', st['to_first_answer'], 'end', st['to_end'], 'budget', st['budget'], 'exh', st['budget_exhausted'],
                      'rw', st['repeated_work'])
                print('   alts', c['alternatives'].get('at_boundary'), c['alternatives'].get('held_as'), c['alternatives'].get('problem_defined'),
                      'susp', c['suspended'].get('at_boundary'), 'ops', c.get('problem_operations'), 'cand', c.get('candidates_examined'))
            print('   observe', repr(a['observe']['raw']))
            if a.get('store') and a['store'].get('quantities'):
                print('   store', json.dumps(a['store']['quantities']))
            if a.get('effects'):
                print('   effects', [(e['seq'], e['entry'], e['stage'], e['during_replay_of']) for e in a['effects']])
            print('   stderr', repr(a['stderr'][-200:]), 'exit', a['exit'], 'safety', a['safety_limit']['hit'])
            if a.get('manual_actions'):
                print('   manual', a['manual_actions'])
            for n in a.get('notes', []):
                print('   note', n[:400])
    if d.get('effects'):
        e = d['effects']
        print(' effects log_after_run', [(x['seq'], x['entry'], x['run_id'][-16:], x['stage'], x['during_replay_of']) for x in e.get('log_after_run', [])], 'before', e.get('entries_before_run'))
    print(' harness_faults', d.get('harness_faults'))
    print(' manual', d.get('manual_actions'))
    for n in d.get('notes', []):
        print(' rnote', n[:600])
