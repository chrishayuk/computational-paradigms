import json,sys
def summ(path, rawlen=1500):
    d=json.load(open(path))
    r=d['run']
    print('#####',path)
    print('mode',r['mode'],'prog',r['program']['path'],'complete',r['complete'],r['incomplete_reason'])
    print('faults',json.dumps(d.get('harness_faults'))[:800])
    print('notes',json.dumps(d.get('notes'))[:800])
    for s in d['stages']:
        for a in s['attempts']:
            print('-- stage',s['stage'],'attempt',a['attempt'],'posed',a['posed']['how'],a['posed']['reason'])
            for c in a['computations']:
                print(' exec',json.dumps(c['execution_state']))
                st=c['steps']; print(' steps', {k:st.get(k) for k in ['budget_exhausted','stage','restated','restart_cost','to_end']}, 'rw',st.get('repeated_work'))
                print(' alts',json.dumps(c['alternatives']))
                print(' susp',json.dumps(c['suspended'])[:600])
                for q in c['queries']:
                    print(' query',q['id'],'cap',q['cap'],'ended',q.get('ended_by'),'n',len(q['answers']))
            ob=a['observe']
            if ob:
                print(' RAW:\n'+(ob.get('raw') or '')[:rawlen])
                print(' BIND',json.dumps(ob.get('bindings'))[:600])
            sq=a.get('store',{}).get('quantities')
            if sq: print(' store',json.dumps(sq)[:900])
            if a.get('manual_actions'): print(' manual',a['manual_actions'])
            if a.get('notes'): print(' anotes',a['notes'])
for p in sys.argv[1:]:
    summ(p, 2500)
