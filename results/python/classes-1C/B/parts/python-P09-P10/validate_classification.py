"""Read-only validation of classifier output against frozen tokens and raw records."""
import json, collections, gzip
from pathlib import Path
BASE=Path('/Users/christopherhay/cp-roles/classifier-1C-B')
HERE=Path(__file__).resolve().parent
r=json.loads((HERE/'python.json').read_text())
assert set(r)=={'tokens','outcomes','mode_differences','expressibility','late_definition','s_mechanisms'}
manifest=[x.split('\t') for x in (BASE/'results/python/tokens/TEXTS-1C-P09-P10.tsv').read_text().splitlines()[1:]]
assert set(r['tokens'])=={x[0] for x in manifest}
totals=collections.Counter()
for path,aliases in manifest:
 rows=(BASE/'results/python/tokens'/(path+'.tokens.tsv')).read_text().splitlines()[1:]
 indices=[int(x.split('\t',1)[0]) for x in rows]; counts=collections.Counter()
 for s in r['tokens'][path]:
  assert s['class'] in ('P','C','R','S','H') and s['construct'] and s['rule']
  assert isinstance(s['from'],int) and isinstance(s['to'],int) and s['from']<=s['to']
  counts.update(range(s['from'],s['to']+1)); totals[s['class']]+=s['to']-s['from']+1
 assert set(counts)==set(indices) and all(v==1 for v in counts.values()),path
 for alias in aliases.split():
  assert (BASE/'programs/python'/path).read_bytes()==(BASE/'programs/python'/alias).read_bytes()
  assert rows==(BASE/'results/python/tokens'/(alias+'.tokens.tsv')).read_text().splitlines()[1:]
expected=set();behaviour_records=set();all_records=set()
for cfg in ('core','extended','stdlib-concurrency'):
 for problem in ('P09','P10'):
  for folder in ('raw','raw-rerun-m2'):
   for p in (BASE/'results/python'/cfg/problem/folder).glob('*.json*'):
    all_records.add(str(p.relative_to(BASE)))
    with gzip.open(p,'rt') if p.suffix=='.gz' else p.open() as f:d=json.load(f)
    if d['run']['mode']!='behaviour':continue
    rel=str(p.relative_to(BASE));behaviour_records.add(rel)
    assert not d['harness_faults']
    for stage in d['stages']:
     for c in stage['attempts'][-1]['computations']:
      if c['queries']:
       for reading in ('P09d1','P09d2') if d['run']['instance']=='P09d' else (None,):expected.add((rel,stage['stage'],c['id'],reading))
actual=[(o['record'],o['stage'],o['computation'],o['reading']) for o in r['outcomes']]
assert len(set(actual))==len(actual) and set(actual)==expected
for o in r['outcomes']:
 assert o['reached'] and not o['harness_fault']
 assert o['semantic'] in ('complete','partial','unsound','undetermined','none reported')
 assert o['representation'] in (None,'explicit','solved form','residual','cyclic')
 if o['representation']=='residual':
  assert o['simplification'] in ('reduced','reducible','inconsistency undetected')
  assert isinstance(o['identical_to_posed'],bool)
  assert o['residual_size'] and o['residual_equivalence']
 else:assert all(o[k] is None for k in ('simplification','identical_to_posed','residual_size'))
 assert o['observations'] and o['rule'] and o['execution_state']
assert len(all_records)==90 and len(behaviour_records)==30
# There are six relevant job logs; all their rows name a covered mode/instance/program.
logged=[]
for p in (BASE/'results/python/logs').glob('*'):
 if p.is_file():
  for line in p.read_text().splitlines():
   f=line.split('\t')
   if len(f)>=6 and f[2].startswith(('P09','P10')):
    assert any(Path(path).name.startswith(f[2]+'.'+f[4]+'.') and '/'+f[1]+'/' in path for path in all_records),(p,line)
    logged.append(line)
assert len(logged)==90
assert r['late_definition']==[] and r['mode_differences']==[]
assert all(e['expressibility'] in ('expressible','expressible with reformulation','not expressible') for e in r['expressibility'])
# All 27 configuration/programs have an S inventory entry, including explicit none.
program_paths={p for a,b in manifest for p in [a]+b.split()}
assert {(m['configuration']+'/'+m['program']) for m in r['s_mechanisms']}==program_paths
for m in r['s_mechanisms']:
 if m['mechanism'] and not m['listed_at_phase_4']:
  ranges=m['token_ranges'];assert m['tokens']==sum(z['to']-z['from']+1 for z in ranges)
  own={i for z in r['tokens'][m['tokens_path']] if z['class']=='S' and z.get('mechanism')==m['mechanism'] for i in range(z['from'],z['to']+1)}
  assert own=={i for z in ranges for i in range(z['from'],z['to']+1)}
print('PASS: exact token coverage, shared texts, 90 logged records, 30 behaviour records, 72 unique outcome entries, residual fields, S inventories and JSON syntax.')
print('Frozen-text totals:',dict(totals))
print('Outcome totals:',dict(collections.Counter(o['semantic'] for o in r['outcomes'])))
