# Compare behaviour records across the three configurations: print, states, ended_by, answer count per stage.
import json, glob, os, re
ROOT='/Users/christopherhay/cp-roles/classifier-A/results/absys'
def key(d):
    out=[]
    for s in d['stages']:
        a=s['attempts'][-1]; c=a['computations'][0]
        pr=re.sub(r'derivation #\d+','derivation #N',a['print'] or '')
        out.append((s['stage'],len(s['attempts']),tuple(c['execution_state']['states']),c['queries'][0]['ended_by'],len(c['queries'][0]['answers']),pr))
    return out
recs={}
for c in ['absys','absys-depth-first','absys-wake-back']:
    for p in glob.glob(f'{ROOT}/{c}/P0?/raw/*.behaviour.*.json'):
        inst=os.path.basename(p).split('.behaviour')[0]
        recs.setdefault(inst,{})[c]=p
for inst in sorted(recs):
    ks={c:key(json.load(open(p))) for c,p in recs[inst].items()}
    base=ks['absys']
    for c,k in ks.items():
        if c=='absys': continue
        if k==base: print(inst,c,'SAME as absys')
        else:
            for a,b in zip(base,k):
                if a!=b: print(inst,c,'DIFF stage',a[0],'absys:',a[:5],len(a[5]),'|',c,b[:5],len(b[5]), 'print-equal' if a[5]==b[5] else 'print-differs')
