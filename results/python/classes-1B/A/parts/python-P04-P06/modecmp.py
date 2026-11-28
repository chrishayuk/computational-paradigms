import json,glob,re,os
base='/Users/christopherhay/cp-roles/classifier-1B-A/results/python'
def key(r):
    out=[]
    for st in r['stages']:
        at=st['attempts'][-1]
        c=at['computations'][0]
        es=c['execution_state']
        err=(es.get('error_verbatim') or '').strip().splitlines()[-1:] 
        obs=re.sub(r'0x[0-9a-f]+','0x',at['observe']['raw'])
        obs=re.sub(r'\(<generator object children at 0x>, 0\), ','',obs)
        out.append(dict(stage=st['stage'],natt=len(st['attempts']),answers=[a['verbatim'] for q in c['queries'] for a in q['answers']],ended=[q['ended_by'] for q in c['queries']],
          states=es['states'],err=err,obs=obs[:3000],print=at['print'][:3000],bud=c['steps']['budget_exhausted'],alts=c['alternatives']['at_boundary'],susp=c['suspended']['at_boundary'],exit=at['exit'],posed=at['posed']['how']))
    return out
for conf in ['core','extended','stdlib-concurrency']:
    for d in sorted(glob.glob(f'{base}/{conf}/P0[456]/raw')):
        for b in sorted(glob.glob(d+'/*.behaviour.*.json')):
            inst=os.path.basename(b).split('.')[0]
            kb=key(json.load(open(b)))
            for mode in ['cost','storage']:
                for m in glob.glob(f'{d}/{inst}.{mode}.*.json'):
                    rm=json.load(open(m)); km=key(rm)
                    for sb,sm in zip(kb,km):
                        diffs={k:(sb[k],sm[k]) for k in sb if sb[k]!=sm[k] and k not in ('exit',)}
                        ex = sb['exit']!=sm['exit']
                        if diffs or ex: print(conf,inst,mode,'stage',sb['stage'],{k:(str(v[0])[:200],str(v[1])[:200]) for k,v in diffs.items()}, 'EXIT' if ex else '', sb['exit'],sm['exit'])
                    if len(kb)!=len(km): print(conf,inst,mode,'STAGECOUNT',len(kb),len(km))
                    if rm.get('harness_faults'): print(conf,inst,mode,'FAULTS',rm['harness_faults'])
