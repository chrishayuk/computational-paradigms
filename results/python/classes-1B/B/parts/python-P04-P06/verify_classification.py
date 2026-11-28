"""Independent artifact checks; no study program is executed or imported."""
import csv, hashlib, json
from pathlib import Path
from collections import Counter
ROOT=Path('.')
OUT=Path(__file__).resolve().parent
r=json.loads((OUT/'python.json').read_text())
rows=list(csv.reader((ROOT/'results/python/tokens/TEXTS-1B-P04-P06.tsv').open(),delimiter='\t'))[1:]
assert set(r['tokens'])=={row[0] for row in rows}
counts=Counter();expanded=Counter();bycfg={}
for row in rows:
 p=row[0];ts=list(csv.DictReader((ROOT/'results/python/tokens'/f'{p}.tokens.tsv').open(),delimiter='\t'))
 coverage=[];c=Counter()
 for span in r['tokens'][p]:
  assert span['class'] in 'PCRSH' and span['construct'] and span['rule']
  assert 0<=span['from']<=span['to']<len(ts)
  coverage.extend(range(span['from'],span['to']+1))
  c[span['class']]+=span['to']-span['from']+1
 assert coverage==list(range(len(ts))),p
 counts.update(c)
 for alias in filter(None,row):
  bycfg.setdefault(alias.split('/')[0],Counter()).update(c)
  expanded.update(c)
  ats=list(csv.DictReader((ROOT/'results/python/tokens'/f'{alias}.tokens.tsv').open(),delimiter='\t'))
  assert [x['token'] for x in ts]==[x['token'] for x in ats]
  assert (ROOT/'programs/python'/p).read_bytes()==(ROOT/'programs/python'/alias).read_bytes()
expected=[];measurement=0;faults=[]
for cfg in ('core','extended','stdlib-concurrency'):
 for prob in ('P04','P05','P06'):
  for p in sorted((ROOT/'results/python'/cfg/prob/'raw').glob('*.json')):
   rec=json.loads(p.read_text());run=rec['run']
   assert hashlib.sha256((ROOT/run['program']['path']).read_bytes()).hexdigest()==run['program']['sha256']
   if '.INVALID.' in p.name:faults.append(str(p))
   if run['mode']=='behaviour':
    for s in rec['stages']:expected.append((cfg,run['instance'],Path(run['program']['path']).name,str(p.relative_to(ROOT)),s['stage']))
   else:measurement+=1
actual=[(x['configuration'],x['instance'],x['program'],x['record'],x['stage']) for x in r['outcomes']]
assert Counter(expected)==Counter(actual)
assert all(n==1 for n in Counter(actual).values())
assert len(r['expressibility'])==48
assert not r['late_definition']
for x in r['outcomes']:
 if x['representation']=='residual':
  assert x['simplification'] in ('reduced','reducible','inconsistency undetected')
  assert isinstance(x['identical_to_posed'],bool)
  assert x['residual_size'] and x['residual_equivalence']['equivalent'] is True
 else:assert x['simplification'] is None and x['identical_to_posed'] is None and x['residual_size'] is None
for x in r['s_mechanisms']:
 if x['token_ranges'] is not None:
  canonical=x['source'].removeprefix('programs/python/')
  labels={i:s['class'] for s in r['tokens'][canonical] for i in range(s['from'],s['to']+1)}
  assert x['tokens']==sum(t['to']-t['from']+1 for t in x['token_ranges'])
  assert all(labels[i]=='S' for t in x['token_ranges'] for i in range(t['from'],t['to']+1))
print(json.dumps({'distinct_texts':len(rows),'token_counts':counts,'expanded_48_program_counts':expanded,'expanded_counts_by_configuration':bycfg,'behaviour_stages':len(actual),'measurement_records_compared':measurement,'mode_differences':len(r['mode_differences']),'invalid_records':faults},indent=2))
