import json,glob,sys,re
# compare behaviour observe.raw & exec across configs, per (problem, program)
def key(f):
    d=json.load(open(f)); return d
probs=sys.argv[1:]
for p in probs:
    recs={}
    for c in ['absys','absys-depth-first','absys-wake-back']:
        for f in sorted(glob.glob(f'{c}/{p}/raw/*.json')):
            d=json.load(open(f)); r=d['run']
            prog=r['program']['path'].split('/',3)[3]
            k=(r['instance'],prog,r['mode'])
            stg=[]
            for s in d['stages']:
                a=s['attempts'][-1]
                c0=a['computations'][0]
                raw=(a['observe'] or {}).get('raw') or ''
                raw=re.sub(r'derivation #\d+','derivation #N',raw)
                stg.append((s['stage'],len(s['attempts']),tuple(c0['execution_state']['states']),raw,c0['alternatives']['at_boundary'],c0['suspended']['at_boundary']))
            recs.setdefault(k,{})[c]=(f,stg)
    for k,v in sorted(recs.items()):
        base=v.get('absys')
        for c,(f,stg) in v.items():
            if c=='absys': continue
            if base is None: print('NO BASE',k,c); continue
            if stg!=base[1]:
                print('DIFF',k,c)
                for a,b in zip(base[1],stg):
                    if a!=b: print('   absys:',a,'\n   ',c+':',b)
            
