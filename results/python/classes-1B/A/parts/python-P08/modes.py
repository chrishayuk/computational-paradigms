import json,glob,re,os
base='./results/python'
def key(f):
    d=json.load(open(f)); out=[]
    for st in d['stages']:
        for at in st['attempts']:
            c=at['computations'][0]
            out.append(dict(stage=st['stage'],how=at['posed']['how'],states=c['execution_state']['states'],
              answers=[a['verbatim'] for q in c['queries'] for a in q['answers']],
              ended=[q['ended_by'] for q in c['queries']],
              obs=re.sub(r'0x[0-9a-f]+','0x?',at['observe']['raw']),print=at['print'],
              err=(c['execution_state'].get('error_verbatim') or '').strip().splitlines()[-1:],
              susp=c['suspended']['at_boundary'],alt=c['alternatives']['at_boundary'],notes=at['notes'],
              ops=c['problem_operations'],store=at['store']['quantities'], steps=c['steps']['stage'], restated=c['steps']['restated']))
    return d,out
for cfg in ['core','extended','stdlib-concurrency']:
    for inst in ['P08a','P08b','P08c']:
        fs=sorted(glob.glob(f'{base}/{cfg}/P08/raw/{inst}.*.json'))
        beh=[f for f in fs if '.behaviour.' in f][0]
        _,B=key(beh)
        for f in fs:
            if f==beh: continue
            d,M=key(f)
            print('##',cfg,inst,os.path.basename(f),'faults',d['harness_faults'],'notes',d['notes'])
            for b,m in zip(B,M):
                diffs={k:(b[k],m[k]) for k in ['how','states','answers','ended','obs','print','err','susp','alt'] if b[k]!=m[k]}
                print('  S%d'%b['stage'], 'DIFF '+json.dumps(diffs,ensure_ascii=False)[:800] if diffs else 'same', '| ops',m['ops'],'| steps',b['steps'],m['steps'],'| store',json.dumps(m['store'])[:250])
