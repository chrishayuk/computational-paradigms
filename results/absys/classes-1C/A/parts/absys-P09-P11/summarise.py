# Read-only summariser of raw run records (classifier's own checking script).
import json, gzip, sys, os, glob
def load(p):
    if p.endswith('.gz'):
        with gzip.open(p,'rt') as f: return json.load(f)
    with open(p) as f: return json.load(f)
def trunc(s,n):
    if s is None: return None
    s=str(s); return s if len(s)<=n else s[:n]+f'...[{len(s)} chars]'
RAWN=int(os.environ.get('RAWN','1200'))
for p in sys.argv[1:]:
    d=load(p); r=d['run']
    print('#####',p)
    print(' program',r['program']['path'],'mode',r['mode'],'instance',r['instance'],'complete',r.get('complete'),r.get('incomplete_reason'))
    for k in ('notes','harness_faults','effects'):
        if k in d and d[k]: print(' ',k,':',trunc(json.dumps(d[k]),1500))
    for k in d:
        if k not in ('record_format','made_up','run','stages','notes','harness_faults','effects'): print('  topkey',k,trunc(json.dumps(d[k]),400))
    for st in d['stages']:
        for a in st['attempts']:
            po=a['posed']
            print(f" STAGE {st['stage']} attempt {a['attempt']} posed {po['how']}/{po['reason']} replayed {po['replayed']} cont_after_budget {po['continued_after_budget']}")
            for k in a:
                if k not in ('attempt','limit_s','posed','computations','observe','print','store','wall_time_s','cpu_time_s','max_rss_kb','stdout','stderr'):
                    print('   akey',k,trunc(json.dumps(a[k]),600))
            for c in a['computations']:
                print(f"   comp {c['id']} spawned {c['spawned']}")
                for q in c['queries']:
                    print('    query',q['id'],'cap',q['cap'],'ended_by',q['ended_by'],'n_answers',len(q['answers']))
                    for an in q['answers'][:3]:
                        print('     ANSWER',trunc(json.dumps(an),700))
                es=c['execution_state']; print('    state',es['states'],'|',trunc(es['basis'],300),'| err',trunc(es['error_verbatim'],300))
                s=c['steps']; print('    steps stage',s['stage'],'restated',s['restated'],'restart',s['restart_cost'],s.get('restart_cost_method'),'exhausted',s['budget_exhausted'],'to_end',s['to_end'],'rep',trunc(json.dumps(s['repeated_work']),200))
                al=c['alternatives']; print('    alts boundary',al['at_boundary'],'budget',al['at_budget'],'peak',trunc(json.dumps(al['peak']),100),al['held_as'])
                su=c['suspended']; print('    susp',su['at_boundary'],su['items'],'peak',trunc(json.dumps(su['peak']),100))
            ob=a.get('observe') or {}
            print('   OBS raw:',trunc(ob.get('raw'),RAWN))
            print('   OBS bindings:',trunc(json.dumps(ob.get('bindings')),RAWN))
            stq=(a.get('store') or {}).get('quantities')
            if stq: print('   store',trunc(json.dumps(stq),800))
