# Compare each cost and storage record with the behaviour record of the same
# configuration and instance: per stage, final attempt's execution states,
# ended_by, answer count and printed state (derivation numbers kept).
import json, glob, os, re
ROOT='./results/absys'
def stage_facts(d):
    out={}
    for s in d['stages']:
        atts=s['attempts']; a=atts[-1]; c=a['computations'][0]
        q=c['queries'][0]
        out[s['stage']]=dict(attempts=len(atts), states=c['execution_state']['states'], ended_by=q['ended_by'],
            n_answers=len(q['answers']), answers=[x['verbatim'] for x in q['answers']], print=a['print'],
            att_states=[at['computations'][0]['execution_state']['states'] for at in atts],
            safety=[at['safety_limit']['action'] for at in atts], posed=a['posed']['how'],
            steps=c['steps'], alts=c['alternatives']['at_boundary'], susp=c['suspended']['at_boundary'])
    return out
for c in ['absys','absys-depth-first','absys-wake-back']:
    for b in sorted(glob.glob(f'{ROOT}/{c}/P0?/raw/*.behaviour.*.json')):
        inst=os.path.basename(b).split('.behaviour')[0]
        B=stage_facts(json.load(open(b)))
        for mode in ['cost','storage']:
            ms=glob.glob(f'{os.path.dirname(b)}/{inst}.{mode}.*.json')
            assert len(ms)==1,(inst,mode,ms)
            dm=json.load(open(ms[0])); M=stage_facts(dm)
            for k in B:
                x,y=B[k],M.get(k)
                diffs=[f for f in ['states','ended_by','n_answers','answers','print','alts','susp'] if x[f]!=y[f]]
                st=y['steps']
                print(f"{c:18} {inst:12} {mode:7} st{k} posed={y['posed']} att={y['attempts']} safety={y['safety']} steps(stage={st['stage']},restated={st['restated']},restart={st['restart_cost']},rw={st['repeated_work']}) diffs={diffs}")
                if diffs:
                    print('     behaviour:', x['states'], x['ended_by'], x['n_answers'], 'alts',x['alts'],'susp',x['susp'], 'print len',len(x['print'] or ''))
                    print('     this mode:', y['att_states'], y['ended_by'], y['n_answers'], 'alts',y['alts'],'susp',y['susp'], 'print len',len(y['print'] or ''))
                    if 'print' in diffs and len(x['print'] or '')<3000 and len(y['print'] or '')<3000:
                        print('     B:',repr(x['print'])); print('     M:',repr(y['print']))
            if dm.get('harness_faults'): print('     faults:',dm['harness_faults'])
            if dm.get('notes'): print('     notes:',[n for n in dm['notes'] if not n.startswith('system:') and not n.startswith('notation:')])
