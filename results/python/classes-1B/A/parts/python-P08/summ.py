import json,sys,glob
for f in sys.argv[1:]:
    d=json.load(open(f))
    r=d['run']
    print('=====',f, r['posing'], 'complete',r['complete'], r['incomplete_reason'], 'faults',d['harness_faults'], 'notes',d['notes'], 'manual', d['manual_actions'])
    for st in d['stages']:
        for at in st['attempts']:
            p=at['posed']
            for c in at['computations']:
                es=c['execution_state']
                err=(es.get('error_verbatim') or '').strip().splitlines()[-1:] 
                print(' S%d a%d %s rep=%s states=%s det=%s steps=%s/%s rc=%s ops=%s susp=%s alt=%s'%(st['stage'],at['attempt'],p['how'],p['replayed'],es['states'],es['determined'],c['steps']['stage'],c['steps']['restated'],c['steps']['restart_cost'],c['problem_operations'],c['suspended']['at_boundary'],c['alternatives']['at_boundary']))
                for q in c['queries']: print('   ans',q['answers'],q['ended_by'])
                if err: print('   ERR',err, '| basis:',es['basis'][:200])
            print('   OBS', at['observe']['raw'].replace('\n',' || ')[:1500])
            if at['print']: print('   PRINT', at['print'][:600].replace('\n',' || '))
            if at['notes']: print('   NOTES', at['notes'])
            if at['store']['quantities']: print('   STORE', json.dumps(at['store']['quantities'])[:300])
            if at.get('separate_run'): print('   SEP', json.dumps(at['separate_run'])[:300])
