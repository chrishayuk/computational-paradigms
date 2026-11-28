"""Check recorded P07 state against the hand proofs in python.json.

This checks the frozen outputs, not the programs. It uses no imposed
finite domain. The integer proofs are algebraic:
a: substitute z, then y, then x in the primitive decomposition;
b: add equations (2x=14), then substitute;
c: (n,10-n) parametrises all integer pairs;
d/e: integer divisibility of v by 2;
f: subtract equations, obtaining 0=1;
g: (x-3)(x+3)=0 over the integral domain Z.
"""
from pathlib import Path
import ast
import collections
import csv
import json
import re

SRC=Path('.')
OUT=Path(__file__).resolve().parent
j=json.loads((OUT/'python.json').read_text())
expected_residual={
 'b':[('+',('x','y',10)),('-',('x','y',4))],
 'c':[('+',('x','y',10))],
 'f':[('+',('x','y',10)),('+',('x','y',11))],
 'g':[('*',('x','x',9))],
}
expected_values={
 'a':{'x':'5','y':'4','z':'3'},
 'b':{},'c':{},'d':{'w':'7','u':'2','v':'14'},
 'e':{'u':'2','v':'15'},'f':{},'g':{},
}
checked=0
logged=[]
for conf in ('core','extended','stdlib-concurrency'):
 for path in sorted((SRC/'results/python'/conf/'P07/raw').glob('*.json')):
  d=json.loads(path.read_text());r=d['run'];letter=r['subproblem'][-1]
  logged.append((conf,r['instance'],Path(r['program']['path']).name,r['mode']))
  assert len(d['stages'])==len(d['stages'][0]['attempts'])==1
  a=d['stages'][0]['attempts'][0];c=a['computations'][0]
  raw=a['observe']['raw']
  susp=re.search(r'^main\.suspended\[[^\]]+\] = (.*)$',raw,re.M).group(1)
  if conf=='extended':
   rels=[]
   for op,args in re.findall(r'([+*=\-])\(([^()]*)\)',susp):
    places=tuple(int(v.strip()) if re.fullmatch(r'-?\d+',v.strip()) else v.strip() for v in args.split(','))
    rels.append((op,places))
   bindings={k:v for k,v in a['observe']['bindings'].items() if k!=v}
  else:
   rels=ast.literal_eval(susp)
   bindings=dict(a['observe']['bindings'])
   if letter=='a': assert bindings.pop('t')=='9'
  assert rels==expected_residual.get(letter,[]),(path,rels)
  assert bindings==expected_values[letter],(path,bindings)
  assert c['suspended']['at_boundary']==len(rels)
  assert c['alternatives']['at_boundary']==0
  expected_state=['suspended'] if rels else ['finished']
  assert c['execution_state']['states']==expected_state
  answers=[x['verbatim'] for q in c['queries'] for x in q['answers']]
  assert answers==({'a':['x = 5, y = 4, z = 3'],'d':['w = 7, u = 2, v = 14']}.get(letter,[]))
  if letter=='e': assert a['stdout'].startswith('no solution: these relations do not hold: ')
  elif answers: assert a['stdout']==answers[0]+'\n'
  else: assert a['stdout']==''
  assert not a['stderr'] and not d['harness_faults'] and d['run']['complete']
  checked+=1
log=[]
for line in (SRC/'results/python/batch-log.tsv').read_text().splitlines():
 cols=line.split('\t')
 if len(cols)>=5 and cols[2].startswith('P07'):
  log.append(tuple(cols[1:5]))
assert collections.Counter(logged)==collections.Counter(log)
assert checked==108
# Algebraic calculations supporting the proofs; the equivalence arguments
# themselves are in the module docstring and each outcome's reason.
z=3;y=7-z;t=12-z;x=t-y
assert (x,y,z)==(5,4,3) and x+y+z==12 and y+z==7
assert 10+4==2*7 and 7+3==10 and 7-3==4
assert divmod(14,2)==(7,0) and divmod(15,2)==(7,1)
assert 10!=11
assert (-3)*(-3)==3*3==9
# Recheck token coverage from the JSON artifact itself, not a reconstructed
# tokenizer, and check the copied S adapter token sequence is identical.
total=0;s_sequences=[]
for key,spans in j['tokens'].items():
 with (SRC/'results/python/tokens'/f'{key}.tokens.tsv').open() as f:
  rows=list(csv.DictReader(f,delimiter='\t'))
 covered=[];s_tokens=[]
 for s in spans:
  covered.extend(range(s['from'],s['to']+1))
  if s['class']=='S': s_tokens.extend(r['token'] for r in rows[s['from']:s['to']+1])
 assert covered==list(range(len(rows))),key
 total+=len(rows)
 if s_tokens: s_sequences.append(s_tokens)
assert len(s_sequences)==7 and all(seq==s_sequences[0] for seq in s_sequences)
assert len(s_sequences[0])==196
assert len(j['expressibility'])==21 and j['late_definition']==[]
assert len(j['outcomes'])==36 and j['mode_differences']==[]
print(f'PASS: {checked} recorded stages; exact match to 108 logged runs; {len(j["tokens"])} texts; {total} frozen tokens each covered exactly once; all algebraic checks passed; identical 196-token S adapter in seven texts.')
