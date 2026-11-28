from pathlib import Path
import json, gzip, hashlib

ROOT=Path('.')
OUT=Path(__file__).parent
CONFIGS=['absys','absys-depth-first','absys-wake-back']
def compact(v, n=2200):
    if isinstance(v,str) and len(v)>n:
        return {'length':len(v),'sha256':hashlib.sha256(v.encode()).hexdigest(),'head':v[:n//2],'tail':v[-n//2:]}
    if isinstance(v,dict): return {k:compact(x,n) for k,x in v.items()}
    if isinstance(v,list): return [compact(x,n) for x in v]
    return v
records=[]
for cfg in CONFIGS:
    for prob in ['P09','P10','P11']:
        for directory in ['raw','raw-rerun-m2']:
            for f in sorted((ROOT/'results/absys'/cfg/prob/directory).glob('*.json*')):
                if f.name.endswith('.jsonl'): continue
                with (gzip.open(f,'rt') if f.suffix=='.gz' else f.open()) as h: obj=json.load(h)
                rec={'path':str(f.relative_to(ROOT)),'run':obj['run'],'notes':obj.get('notes'), 'harness_faults':obj.get('harness_faults'),'other_keys':list(obj),'stages':[]}
                for stage in obj['stages']:
                    s={'stage':stage['stage'],'attempts':[]}
                    for a in stage['attempts']:
                        b={k:compact(v) for k,v in a.items() if k not in ['stdout','stderr']}
                        b['stdout_summary']=compact(a.get('stdout',''),1000)
                        b['stderr_summary']=compact(a.get('stderr',''),1000)
                        s['attempts'].append(b)
                    rec['stages'].append(s)
                records.append(rec)
(OUT/'record_summaries.json').write_text(json.dumps(records,indent=2)+'\n')
print('records',len(records))
for r in records:
    if r['run']['mode']!='behaviour':continue
    print('\n',r['path'],r['run']['program']['path'])
    for s in r['stages']:
        for a in s['attempts']:
            print('stage',s['stage'],'attempt',a['attempt'],'posed',a['posed'],'notes',a['notes'])
            for c in a['computations']:
                print('  ',c['id'],c['execution_state'], 'alternatives',c['alternatives']['at_boundary'],'suspended',c['suspended']['at_boundary'])
                print('  queries',compact(c['queries'],800))
            print('  observe',compact(a['observe'],1800))
    if r.get('harness_faults'): print('FAULTS',r['harness_faults'])
