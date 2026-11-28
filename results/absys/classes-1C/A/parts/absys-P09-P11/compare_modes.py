# Compare cost/storage records with the behaviour record of the same configuration, instance and program
# (classifier's own read-only checking script).
import json,gzip,glob,os,re,sys,hashlib
ROOT='./results/absys'
def load(p):
    if p.endswith('.gz'):
        with gzip.open(p,'rt') as f: return json.load(f)
    with open(p) as f: return json.load(f)
def norm(s):
    s=s or ''
    lines=[l.strip() for l in s.split('\n')]
    lines=[l for l in lines if l and not re.match(r'^#\d+:',l) and l!='no derivation survives' and not l.endswith('does not occur')]
    s='\n'.join(lines)
    s=re.sub(r'#\d+','#N',s)
    return hashlib.sha1(s.encode()).hexdigest()[:10], len(s)
def summ(d):
    out={}
    for st in d['stages']:
        a=st['attempts'][-1]
        comps={}
        for c in a['computations']:
            comps[c['id']]=dict(states=c['execution_state']['states'],ended=c['queries'][0]['ended_by'],
                n=len(c['queries'][0]['answers']),ans=norm(''.join(x['verbatim'] for x in c['queries'][0]['answers']))[0],
                alts=c['alternatives']['at_boundary'],susp=c['suspended']['at_boundary'],
                steps=(c['steps']['stage'],c['steps']['restated'],c['steps']['restart_cost'],c['steps']['budget_exhausted']))
        out[st['stage']]=dict(attempts=len(st['attempts']),posed=(a['posed']['how'],a['posed']['reason']),
            safety=[x['safety_limit']['action'] for x in st['attempts']],raw=norm(a['observe']['raw']),comps=comps,
            effects=[e['entry'] for e in (a.get('effects') or [])], notes=a.get('notes'))
    return out
for conf in ['absys','absys-depth-first','absys-wake-back']:
    for prob in ['P09','P10','P11']:
        recs={}
        for p in sorted(glob.glob(f'{ROOT}/{conf}/{prob}/raw/*.json*')):
            if p.endswith('.jsonl'): continue
            d=load(p); r=d['run']
            key=(r['instance'],r['program']['path'].split(conf+'/',1)[1])
            recs.setdefault(key,{})[r['mode']]=(os.path.basename(p),summ(d),d.get('harness_faults'),d['run'].get('notes') if False else None)
        for key,m in recs.items():
            b=m.get('behaviour')
            print(f'=== {conf} {key} modes={sorted(m)}')
            for mode in ('behaviour','cost','storage'):
                if mode not in m: continue
                fn,s,hf,_=m[mode]
                print(f'  [{mode}] {fn} faults={hf}')
                for stg,v in s.items():
                    print(f'    st{stg} att={v["attempts"]} posed={v["posed"]} safety={v["safety"]} raw={v["raw"]} eff={v["effects"]}')
                    for cid,c in v['comps'].items():
                        flag=''
                        if mode!='behaviour' and b and stg in b[1] and cid in b[1][stg]['comps']:
                            bc=b[1][stg]['comps'][cid]
                            diffs=[k for k in ('states','ended','n','ans','alts','susp') if bc[k]!=c[k]]
                            if b[1][stg]['raw'][0]!=v['raw'][0]: diffs.append('raw')
                            flag=' DIFF:'+','.join(diffs) if diffs else ' same'
                        print(f'      {cid}: {c}{flag}')
