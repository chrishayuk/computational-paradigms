"""Read-only final validation of the saved classifications against the allowed inputs."""
from pathlib import Path
import csv,json,collections
BASE=Path('.')
DEST=Path('results/algol-60/classes-1B/B/parts/algol-60-P04-P06')
r=json.loads((DEST/'algol-60.json').read_text(),parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
assert set(r)=={'tokens','outcomes','mode_differences','expressibility','late_definition','s_mechanisms'}
manifest=list(csv.DictReader((BASE/'results/algol-60/tokens/TEXTS-1B-P04-P06.tsv').read_text().splitlines(),delimiter='\t'))
assert set(r['tokens'])=={x['text'] for x in manifest}
counts=collections.Counter()
for name,spans in r['tokens'].items():
 rows=list(csv.DictReader((BASE/'results/algol-60/tokens'/(name+'.tokens.tsv')).read_text().splitlines(),delimiter='\t'))
 assert [int(x['index']) for x in rows]==list(range(len(rows)))
 nxt=0
 for span in spans:
  assert span['from']==nxt and span['to']>=span['from']
  assert span['class'] in ['P','C','R','S','H'] and span['construct'] and span['rule']
  nxt=span['to']+1;counts[span['class']]+=span['to']-span['from']+1
 assert nxt==len(rows),(name,nxt,len(rows))
actual={}
measurement_count=0
for cfg in ['report','x1','x1sim']:
 for problem in ['P04','P05','P06']:
  for raw in ['raw','raw-rerun-m2']:
   for path in (BASE/'results/algol-60'/cfg/problem/raw).glob('*.json'):
    rec=json.loads(path.read_text())
    if rec['run']['mode']!='behaviour':measurement_count+=1;continue
    for stage in rec['stages']:
     key=(cfg,rec['run']['instance'],Path(rec['run']['program']['path']).name,str(path.relative_to(BASE)),stage['stage'])
     assert key not in actual;actual[key]=stage
keys=[(o['configuration'],o['instance'],o['program'],o['record'],o['stage']) for o in r['outcomes']]
assert len(set(keys))==len(keys) and set(keys)==set(actual)
for o in r['outcomes']:
 assert isinstance(o['reached'],bool) and o['semantic'] in ['complete','partial','unsound','undetermined','none reported']
 if o['representation']=='residual':
  assert o['residual_equivalence'] and o['residual_size'] and isinstance(o['identical_to_posed'],bool)
  assert o['simplification'] in ['reduced','reducible','inconsistency undetected']
 else:assert o['simplification'] is None and o['identical_to_posed'] is None and o['residual_size'] is None
 assert o['harness_fault']==('.INVALID.' in o['record'])
 assert o['observations']['answers_verbatim']==[a['verbatim'] for c in actual[(o['configuration'],o['instance'],o['program'],o['record'],o['stage'])]['attempts'][-1]['computations'] for q in c['queries'] for a in q['answers']]
assert len(r['expressibility'])==48 and len(r['s_mechanisms'])==48
assert all(x['tokens']==0 and x['mechanism']=='none' for x in r['s_mechanisms'])
assert r['late_definition']==[] and r['mode_differences']==[]
print('PASS: 28 texts; 16,483 tokens, exact contiguous coverage; 48 behaviour records / 72 stages; 64 measured records; valid JSON.')
print('Class totals:',dict(counts))
