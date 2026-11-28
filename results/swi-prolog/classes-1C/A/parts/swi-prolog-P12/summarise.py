import json, glob, os, sys, hashlib
R='/Users/christopherhay/cp-roles/classifier-1C-A'
rows=[]
for f in sorted(glob.glob(R+'/results/swi-prolog/*/P12/raw*/*.json*')):
    d=json.load(open(f))
    run=d['run']
    prog=R+'/'+run['program']['path']
    sha=hashlib.sha256(open(prog,'rb').read()).hexdigest()
    for st in d['stages']:
        for at in st['attempts']:
            for c in at['computations']:
                q=c['queries'][0]
                rows.append(dict(file=os.path.relpath(f,R),conf=run['configuration'],inst=run['instance'],mode=run['mode'],
                    shaok=sha==run['program']['sha256'],stage=st['stage'],attempt=at['attempt'],
                    answers=[a['verbatim'] for a in q['answers']],steps_at=[a['steps_at'] for a in q['answers']],
                    alt_at=[a['alternatives_at'] for a in q['answers']],
                    ended=q['ended_by'],coll=q['collected_on'],states=c['execution_state']['states'],
                    to_end=c['steps']['to_end'],restated=c['steps']['restated'],budget_ex=c['steps']['budget_exhausted'],
                    cand=c['candidates_examined'],alts=c['alternatives'],susp=c['suspended']['at_boundary'],
                    obs=at['observe']['raw'][:200],print=at['print'][:300],store=at['store'],
                    safety=at['safety_limit']['hit'],stdout=at['stdout'][:100],stderr=at['stderr'][:200],
                    faults=d['harness_faults'],complete=run['complete'],posed=at['posed']['how'],notes=[n for n in d['notes'] if 'system_build' not in n],
                    exit=at['exit']['status'],sep=at['separate_run'],manual=at['manual_actions']))
json.dump(rows,open(sys.argv[1],'w'),indent=1)
print(len(rows))
