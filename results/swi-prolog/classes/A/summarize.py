import json,glob,os,sys
root='./results/swi-prolog'
def t(s,n=300):
    if s is None: return None
    s=str(s); return s if len(s)<=n else s[:n]+'...[%d chars]'%len(s)
out=[]
for f in sorted(glob.glob(root+'/*/P0?/raw/*.json')):
    r=json.load(open(f))
    run=r['run']
    for st in r['stages']:
        for a in st['attempts']:
            for c in a['computations']:
                q=c['queries'][0] if c['queries'] else {}
                ans=[x['verbatim'] for x in q.get('answers',[])]
                es=c['execution_state']
                out.append(dict(rec=os.path.relpath(f,'.'),cfg=run['configuration'],inst=run['instance'],prog=os.path.basename(run['program']['path']),mode=run['mode'],stage=st['stage'],att=a['attempt'],posed=a['posed']['how']+'/'+a['posed']['reason'],
                  nans=len(ans),answers=[t(x,200) for x in ans[:21]],ended=q.get('ended_by'),coll=q.get('collected_on'),states=es['states'],basis=t(es.get('basis'),250),err=t(es.get('error_verbatim'),300),
                  steps=c['steps'].get('to_end'),restated=c['steps'].get('restated'),budget_ex=c['steps'].get('budget_exhausted'),
                  susp=c['suspended'],alts=c['alternatives'].get('at_boundary'),altbud=c['alternatives'].get('at_budget'),
                  obs=t(a['observe'].get('raw'),300),obsm=t(a['observe'].get('method'),120),taken=a['observe'].get('taken_on'),
                  sep=None if a.get('separate_run') is None else t(json.dumps(a['separate_run']),600),
                  safety=a['safety_limit'],manual=a['manual_actions'],stdout_len=len(a.get('stdout') or ''),stderr=t(a.get('stderr'),200),
                  store=a.get('store',{}).get('quantities')))
json.dump(out,open('results/swi-prolog/classes/A/summary.json','w'),indent=1)
print(len(out))
