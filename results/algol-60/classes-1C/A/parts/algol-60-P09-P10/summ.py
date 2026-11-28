import json,sys,glob,gzip
def ld(p):
    return json.load(gzip.open(p) if p.endswith('.gz') else open(p))
for p in sys.argv[1:]:
    r=ld(p); run=r['run']
    print('#####',p.split('/results/')[-1], run['mode'], 'posing',run.get('posing'),'complete',run.get('complete'), run.get('incomplete_reason'))
    print(' faults',r.get('harness_faults'),' notes',str(r.get('notes'))[:400])
    for st in r['stages']:
        for at in st['attempts']:
            print(f" stage {st['stage']} att {at['attempt']} posed {at['posed'].get('how')}/{at['posed'].get('reason')} repl {at['posed'].get('replayed')} exit {at.get('exit')} wall {at.get('wall_time_s')} safety {at.get('safety_limit',{}).get('hit')}")
            for c in at['computations']:
                es=c['execution_state']; s=c['steps']
                print(f"   comp {c['id']} spawned {c.get('spawned')} states {es.get('states')} det {es.get('determined')} err {es.get('error_verbatim')!r} basis {str(es.get('basis'))[:200]!r}")
                print(f"     steps stage {s.get('stage')} restated {s.get('restated')} budget {s.get('budget')} exh {s.get('budget_exhausted')} rw {s.get('repeated_work')} first {s.get('to_first_answer')} end {s.get('to_end')}")
                for q in c['queries']:
                    print(f"     q {q['id']} cap {q['cap']} ended {q['ended_by']} answers {[a.get('text', a) if isinstance(a,dict) else a for a in q['answers']]}")
                print(f"     alts {c.get('alternatives')} susp {c.get('suspended')} ops {c.get('problem_operations')}")
            print('   observe', repr(at['observe'].get('raw'))[:600], at['observe'].get('bindings'))
            if at.get('store'): print('   store', json.dumps(at['store'])[:500])
            print('   stderr', repr(at.get('stderr'))[:300], 'manual', at.get('manual_actions'), 'notes', repr(at.get('notes'))[:300])
