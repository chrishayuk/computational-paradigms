from pathlib import Path
from collections import Counter
import json,re
base=Path('/Users/christopherhay/cp-roles/classifier-1B-B')
out=Path(__file__).resolve().parent
x=json.loads((out/'swi-prolog.json').read_text())
manifest=[r.split('\t') for r in (base/'results/swi-prolog/tokens/TEXTS-1B-P05-P08.tsv').read_text().splitlines()[1:]]
assert set(x['tokens'])=={r[0] for r in manifest}
def ts(name):
 rows=(base/'results/swi-prolog/tokens'/(name+'.tokens.tsv')).read_text().splitlines()[1:]
 return [(int(i),t) for i,l,t in (r.split('\t',2) for r in rows)]
ct=Counter({k:0 for k in 'PCRSH'})
for r in manifest:
 name=r[0];stream=ts(name);spans=x['tokens'][name]
 covered=[i for s in spans for i in range(s['from'],s['to']+1)]
 assert covered==[i for i,t in stream],name
 assert len(covered)==len(set(covered))
 for s in spans:
  assert s['class'] in 'PCRSH' and s['construct'] and s['rule']
  ct[s['class']]+=s['to']-s['from']+1
 for alias in r[1].split() if len(r)>1 else []:assert ts(alias)==stream,(name,alias)
records=[]
for conf in ['constraints','coroutines','plain','session','tabling']:
 for prob in ['P05','P06','P07','P08']:
  for kind in ['raw','raw-rerun-m2']:
   for p in (base/'results/swi-prolog'/conf/prob/kind).glob('*.json'):
    z=json.loads(p.read_text());records.append((p,z))
expected={(p.relative_to(base).as_posix(),s['stage']) for p,z in records if z['run']['mode']=='behaviour' for s in z['stages']}
actual={(e['record'],e['stage']) for e in x['outcomes']}
assert expected==actual and len(actual)==len(x['outcomes'])
for e in x['outcomes']:
 if not e['reached']:
  assert e['semantic'] is None and e['representation'] is None and e['execution_state']==['not reached']
 if '.INVALID.' in e['record']:assert e['harness_fault'] is True
 if e['representation']=='residual':
  assert e['residual_size'] is not None and e['simplification'] is not None and isinstance(e['identical_to_posed'],bool)
 if e['instance'].startswith('P08'):assert set(e['semantic_by_reading'])=={'open','closed'}
# Independently check that the single changed report is the only changed answer set.
beh={(z['run']['configuration'],z['run']['instance'],z['run']['program']['path']):z for p,z in records if z['run']['mode']=='behaviour'}
diffs=[]
for p,z in records:
 if z['run']['mode']=='behaviour':continue
 b=beh[(z['run']['configuration'],z['run']['instance'],z['run']['program']['path'])]
 for s,t in zip(z['stages'],b['stages']):
  ans=lambda s:[a['verbatim'] for c in s['attempts'][-1]['computations'] for q in c['queries'] for a in q['answers']]
  if ans(s)!=ans(t):diffs.append((p.relative_to(base).as_posix(),s['stage']))
assert set(diffs)=={(e['record'],e['stage']) for e in x['mode_differences']}
assert len(x['late_definition'])==30
assert len(x['s_mechanisms'])==23
# Match the run log where rows are intact, without reading any result narratives.
log=(base/'results/swi-prolog/batch-log.tsv').read_text().splitlines()
logged=[]
for line in log:
 cols=line.split('\t')
 if len(cols)>=5 and cols[2].startswith(('P05','P06','P07','P08')) and cols[4]=='behaviour':logged.append(tuple(cols[1:4]))
raw_keys={(z['run']['configuration'],z['run']['instance'],Path(z['run']['program']['path']).name) for p,z in records if z['run']['mode']=='behaviour'}
assert set(logged)<=raw_keys
print('PASS: 48 texts /',sum(ct.values()),'tokens, exact once-only spans; aliases match.')
print('PASS:',len(expected),'behaviour stages from',len(beh),'records; 280 measurement records compared.')
print('PASS: one differing answer set, 30 late-definition judgements, 23 session S listings.')
print('Token totals:',dict(ct))
print('P08 reading totals:',{reading:dict(Counter(e['semantic_by_reading'][reading] for e in x['outcomes'] if e['instance'].startswith('P08'))) for reading in ['open','closed']})
print('Log behaviour rows matched:',len(logged),'/',len(beh),'(the log has a damaged tabling segment; every raw record is covered).')
