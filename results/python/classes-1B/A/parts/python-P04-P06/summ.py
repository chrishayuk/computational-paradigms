import json,sys,glob,os
def tr(s,n=300):
    s=str(s); return s if len(s)<=n else s[:n]+'...[%d]'%len(s)
for f in sys.argv[1:]:
    r=json.load(open(f))
    print('#####',f, 'faults=',r.get('harness_faults'),'notes=',r.get('notes'), 'manual=',r.get('manual_actions'))
    for st in r['stages']:
        for at in st['attempts']:
            print(' stage',st['stage'],'att',at['attempt'],'posed',at['posed']['how'],at['posed']['reason'],'replayed',at['posed']['replayed'],'cont',at['posed']['continued_after_budget'])
            for c in at['computations']:
                q=c['queries']
                print('   comp',c['id'],'answers',[ (len(x['answers']),tr(x['answers'],200),x['ended_by']) for x in q])
                es=c['execution_state']
                print('   state',es['states'],es['determined'],repr((es.get('error_verbatim') or '')[-160:]))
                sp=c['steps']; print('   steps',{k:sp.get(k) for k in ('stage','restated','to_end','restart_cost','to_first_answer','budget_exhausted')})
                print('   alts',tr(c['alternatives'],300)); print('   susp',tr(c['suspended'],300)); print('   probops',tr(c['problem_operations'],300))
            print('   observe',tr(at['observe']['raw'],600)); print('   bindings',tr(at['observe'].get('bindings'),200))
            print('   print',tr(at['print'],300)); print('   store',tr(at['store'],300)); print('   notes',tr(at['notes'],300),'exit',at['exit'],'safety',at['safety_limit']['hit'],'manual',at['manual_actions'])
