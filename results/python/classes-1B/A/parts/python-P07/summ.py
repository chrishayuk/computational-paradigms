import json,glob,os
B='/Users/christopherhay/cp-roles/classifier-1B-A/'
out=[]
for f in sorted(glob.glob(B+'results/python/*/P07/raw/*.json')):
    d=json.load(open(f))
    r=d['run']
    for st in d['stages']:
        for a in st['attempts']:
            for c in a['computations']:
                ans=[x['verbatim'] for q in c['queries'] for x in q['answers']]
                out.append(dict(rec=os.path.relpath(f,B),cfg=r['configuration'],inst=r['instance'],mode=r['mode'],
                  prog=r['program']['path'].split('/')[-1],stage=st['stage'],attempt=a['attempt'],
                  ans=ans,ended=[q['ended_by'] for q in c['queries']],
                  states=c['execution_state']['states'],det=c['execution_state']['determined'],err=c['execution_state']['error_verbatim'],
                  susp=c['suspended']['at_boundary'],alt=c['alternatives']['at_boundary'],
                  steps=c['steps']['stage'],budget=c['steps']['budget_exhausted'],
                  raw=a['observe']['raw'],stdout=a['stdout'],stderr=a['stderr'],manual=a['manual_actions'],
                  posed=a['posed']['how'],faults=d['harness_faults'],complete=r['complete'],notes=d['notes'],anotes=a['notes'],
                  safety=a['safety_limit']['hit'],popsn=c.get('problem_operations')))
json.dump(out,open('summary.json','w'),indent=1)
for o in out:
    print(o['cfg'][:4],o['inst'],o['mode'][:4],o['states'],o['det'],'susp',o['susp'],'ans',o['ans'],'steps',o['steps'],'faults',len(o['faults']),'att',o['attempt'],o['posed'],'safety',o['safety'])
