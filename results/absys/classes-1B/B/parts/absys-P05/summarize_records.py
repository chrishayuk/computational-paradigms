import json,gzip,re,gc
from pathlib import Path
ROOT=Path('.')
OUT=Path('results/absys/classes-1B/B/parts/absys-P05')

def state_summary(raw):
 blocks=re.split(r'(?=^  derivation #)',raw,flags=re.M)[1:]
 result=[]
 for b in blocks:
  lines=b.splitlines(); h=lines[0]
  m=re.search(r'^    x(?: = ([^\n]+)|  uninstantiated)',b,re.M)
  todo=re.search(r'^    to do +(.*)$',b,re.M)
  result.append({'header':h,'x':m.group(1) if m else None,'susp_count':b.count('(waits '),'todo':todo.group(1) if todo else None,'prefix':b[:420], 'suffix':b[-420:] if 'still elaborating' in h else None})
 return {'length':len(raw),'header':raw.splitlines()[0] if raw else None,'blocks':len(blocks),'finished_values':[x['x'] for x in result if 'hibernating' in x['header']], 'active':[x for x in result if 'still elaborating' in x['header']], 'unknown_blocks':sum(x['x'] is None for x in result)}

summaries=[]
for conf in ['absys','absys-depth-first','absys-wake-back']:
 for directory in ['raw','raw-rerun-m2']:
  folder=ROOT/'results/absys'/conf/'P05'/directory
  if not folder.exists():continue
  for f in sorted(folder.iterdir()):
   if not(f.name.endswith('.json') or f.name.endswith('.json.gz')):continue
   op=gzip.open if f.suffix=='.gz' else open
   with op(f,'rt') as h:d=json.load(h)
   z={'record':str(f.relative_to(ROOT)),'run':d['run'],'faults':d['harness_faults'],'notes':d['notes'],'manual_actions':d['manual_actions'],'stages':[]}
   for s in d['stages']:
    ss={'stage':s['stage'],'notes':s.get('notes'),'attempts':[]}
    for a in s['attempts']:
     aa={k:v for k,v in a.items() if k not in ['stdout','observe','print','separate_run','computations']}
     aa['stdout_length']=len(a['stdout']);aa['stdout_tail']=a['stdout'][-400:]
     aa['observe']=state_summary(a['print'] or a['observe']['raw']);aa['observe_method']=a['observe']['method']
     aa['computations']=[]
     for c in a['computations']:
      cc=dict(c); cc['queries']=[{**q,'answers':[ans for ans in q['answers'] if len(ans['verbatim'])<1000], 'answer_count':len(q['answers'])} for q in c['queries']];aa['computations'].append(cc)
     ss['attempts'].append(aa)
    z['stages'].append(ss)
   summaries.append(z)
   print(f'{f.relative_to(ROOT)}: '+str([(s['stage'],[(a['attempt'],a['computations'][0]['execution_state']['states'],a['observe']['blocks']) for a in s['attempts']]) for s in z['stages']]),flush=True)
   del d;gc.collect()
(OUT/'record_summaries.json').write_text(json.dumps(summaries,indent=2,ensure_ascii=False))
