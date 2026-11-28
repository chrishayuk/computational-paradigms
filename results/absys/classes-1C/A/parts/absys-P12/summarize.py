import json, glob, os, re, sys
ROOT='./results/absys'
rows=[]
for f in sorted(glob.glob(ROOT+'/*/P12/raw*/*.json*')):
    d=json.load(open(f))
    r=d['run']
    for st in d['stages']:
        for at in st['attempts']:
            for c in at['computations']:
                q=c['queries'][0]
                ss=[re.search(r"s = (.*)",a['verbatim']).group(1) if re.search(r"\n    s = (.*)",a['verbatim']) else '?' for a in q['answers']]
                ss=[re.search(r"\n    s = (.*)\n",a['verbatim']).group(1) if re.search(r"\n    s = (.*)\n",a['verbatim']) else 'NO-S' for a in q['answers']]
                sl=at['safety_limit']
                out=dict(file=os.path.relpath(f,ROOT),mode=r['mode'],stage=st['stage'],att=at['attempt'],posed=at['posed']['how'],
                  n_ans=len(q['answers']),ended=q['ended_by'],answers=ss,states=c['execution_state']['states'],
                  det=c['execution_state']['determined'],err=c['execution_state']['error_verbatim'],
                  safety=(sl['hit'],sl['action'],sl['how_stopped']),
                  alt=(c['alternatives']['at_boundary'],c['alternatives']['peak'],c['alternatives']['problem_defined']),
                  susp=(c['suspended']['at_boundary'],c['suspended']['peak']),
                  steps=(c['steps']['stage'],c['steps']['budget_exhausted'],c['steps']['to_end']),
                  faults=d['harness_faults'],exit=at['exit'],complete=r['complete'],incomplete=r['incomplete_reason'],
                  basis=c['execution_state']['basis'])
                rows.append(out)
for o in rows:
    print(json.dumps(o,ensure_ascii=False))
