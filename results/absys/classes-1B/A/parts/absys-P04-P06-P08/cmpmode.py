import json,glob,sys,re
def norm(raw):
    raw=re.sub(r'derivation #\d+','derivation #N',raw)
    raw='\n'.join(l for l in raw.split('\n') if not re.match(r'^#\d+: |^\S+ does not occur|^no derivation survives',l))
    return raw.strip()
for c in ['absys','absys-depth-first','absys-wake-back']:
  for p in sys.argv[1:]:
    recs={}
    for f in sorted(glob.glob(f'{c}/{p}/raw/*.json'))+sorted(glob.glob(f'{c}/{p}/raw-rerun-m2/*.json')):
        d=json.load(open(f)); r=d['run']
        prog=r['program']['path'].split('/',3)[3]
        stg=[]
        for s in d['stages']:
            a=s['attempts'][-1]; c0=a['computations'][0]
            stg.append((s['stage'],tuple(c0['execution_state']['states']),norm((a['observe'] or {}).get('raw') or ''),a['posed']['how']))
        recs.setdefault((r['instance'],prog),[]).append((r['mode'],f,stg))
    for k,lst in sorted(recs.items()):
        beh=[x for x in lst if x[0]=='behaviour']
        assert len(beh)==1,(k,lst)
        for m,f,stg in lst:
            if m=='behaviour': continue
            for a,b in zip(beh[0][2],stg):
                if a[:3]!=b[:3]: print(c,k,m,f,'\n   beh:',a,'\n   mode:',b)
            if len(stg)!=len(beh[0][2]): print('LEN',c,k,m)
