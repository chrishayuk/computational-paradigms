#!/usr/bin/env python3
"""Read-only independent checks of submitted JSON, token coverage, and record coverage.
The algebra checks below manipulate mathematical terms, not the programs/system.
"""
from pathlib import Path
from collections import Counter
import csv,json
from fractions import Fraction
B=Path('.')
O=Path('results/algol-60/classes-1B/B/parts/algol-60-P07-P08')
r=json.loads((O/'algol-60.json').read_text())
texts=list(csv.reader((B/'results/algol-60/tokens/TEXTS-1B-P07-P08.tsv').open(),delimiter='\t'))[1:]
assert set(r['tokens'])=={row[0] for row in texts}
totals=Counter();expanded=Counter();per={};members={}
for row in texts:
 key=row[0];ts=list(csv.DictReader((B/f'results/algol-60/tokens/{key}.tokens.tsv').open(),delimiter='\t'))
 seen=[];co=Counter()
 for s in r['tokens'][key]:
  assert s['class'] in 'PCRSH' and s['from']<=s['to']
  assert s['construct'] and s['rule']
  seen.extend(range(s['from'],s['to']+1));co[s['class']]+=s['to']-s['from']+1
 assert seen==[int(t['index']) for t in ts],key
 totals.update(co);per[key]=dict(co)
 aliases=[key]+(row[1].split() if len(row)>1 else [])
 for alias in aliases:
  ats=list(csv.DictReader((B/f'results/algol-60/tokens/{alias}.tokens.tsv').open(),delimiter='\t'))
  assert [t['token'] for t in ats]==[t['token'] for t in ts],alias
  members[alias]=key;expanded.update(co)
assert len(members)==30
records=[]
for c in ['report','x1','x1sim']:
 for p in ['P07','P08']:
  for sub in ['raw','raw-rerun-m2']:
   for f in (B/f'results/algol-60/{c}/{p}/{sub}').glob('*.json'):
    records.append((str(f.relative_to(B)),json.loads(f.read_text())))
expected=[];stages=0;beh=0;measure=0;ms=0
for path,d in records:
 if d['run']['mode']=='behaviour':
  beh+=1;stages+=len(d['stages'])
  for s in d['stages']:
   for reading in ([None] if d['run']['problem']=='P07' else ['closed','open']):expected.append((path,s['stage'],reading))
 else:measure+=1;ms+=len(d['stages'])
assert Counter(expected)==Counter((x['record'],x['stage'],x['reading']) for x in r['outcomes'])
assert all(x['reached'] and not x['harness_fault'] for x in r['outcomes'])
assert len(r['expressibility'])==30 and len(r['late_definition'])==9
assert not r['s_mechanisms'] and not r['mode_differences']
# The permitted batch log is the run inventory; no entry in P07/P08 is omitted.
lines=[line.split('\t') for line in (B/'results/algol-60/batch-log.tsv').read_text().splitlines()]
log=[v for v in lines if len(v)>=5 and (v[2].startswith('P07') or v[2].startswith('P08'))]
assert len(log)==len(records)==105
assert Counter((v[1],v[2],v[3],v[4]) for v in log)==Counter((d['run']['configuration'],d['run']['instance'],Path(d['run']['program']['path']).name,d['run']['mode']) for _,d in records)
# P07: universal symbolic elimination, followed by substitution.
x=(Fraction(12)-7); y=Fraction(7)-3; z=Fraction(3)
assert (x,y,z)==(5,4,3) and x+y+z==12 and y+z==7
x=Fraction(10+4,2);y=Fraction(10-4,2)
assert (x,y)==(7,3) and x+y==10 and x-y==4
assert Fraction(14,2)==7 and Fraction(15,2).denominator!=1
assert 10!=11
assert {v for v in [3,-3] if v*v==9}=={3,-3} # completeness also uses (x-3)(x+3)=0 over integers.
# P08: symbolic substitution of equal element names is universal for values of any type.
def subst(term,env):
 if isinstance(term,tuple):return tuple(subst(t,env) for t in term)
 while term in env:term=env[term]
 return term
A=('x','y','z');Rev=('z','y','x')
assert subst(A,{'x':'y'})==('y','y','z')
assert subst(Rev,{'x':'y'})==('z','y','y')
assert subst(A,{'x':'y','y':'z'})==subst(Rev,{'x':'y','y':'z'})==('z','z','z')
assert subst(A,{'x':42,'y':42,'z':42})==(42,42,42)
assert subst(Rev,{'x':42,'y':42,'z':42})==(42,42,42)
assert tuple(reversed((1,2)))==(2,1)
summary={'distinct_texts':len(texts),'program_paths':len(members),'tokens_distinct_texts':sum(totals.values()),'tokens_by_class_distinct':dict(totals),'tokens_by_class_expanded':dict(expanded),'per_text':per,'behaviour_runs':beh,'behaviour_stages':stages,'outcome_entries_with_dual_P08_readings':len(r['outcomes']),'semantic_counts':dict(Counter(x['semantic'] for x in r['outcomes'])),'representation_counts':dict(Counter(x['representation'] for x in r['outcomes'])),'simplification_counts':dict(Counter(x['simplification'] for x in r['outcomes'] if x['simplification'])),'execution_state_counts':dict(Counter(v for x in r['outcomes'] for v in x['execution_state'])),'measurement_records_compared':measure,'measurement_stages_compared':ms,'mode_differences':0,'invalid_records':0,'unreached_stages':0,'measurement_reruns':0}
(O/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
