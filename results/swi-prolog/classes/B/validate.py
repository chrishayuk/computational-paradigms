#!/usr/bin/env python3
"""Validate the delivered JSON against permitted manifests and recorded evidence.
This script reads data only and never executes Prolog or repository code.
"""
import collections,csv,hashlib,json,re
from pathlib import Path
R=Path('/Users/christopherhay/cp-roles/classifier-B')
O=Path('/Users/christopherhay/cp-roles/classes-B/swi-prolog')
x=json.loads((O/'swi-prolog.json').read_text())
assert set(x)=={'tokens','outcomes','mode_differences','expressibility'}
manifest=list(csv.reader((R/'results/swi-prolog/tokens/TEXTS.tsv').open(),delimiter='\t'))[1:]
assert set(x['tokens'])=={p for p,_ in manifest}
counts=collections.Counter({c:0 for c in 'PCRSH'});expanded={};files=set()
for p,aliases in manifest:
    rows=list(csv.DictReader((R/f'results/swi-prolog/tokens/{p}.tokens.tsv').open(),delimiter='\t'))
    frozen=[int(t['index']) for t in rows];assert frozen==list(range(len(rows)))
    coverage=collections.Counter()
    subtotal=collections.Counter({c:0 for c in 'PCRSH'})
    for s in x['tokens'][p]:
        assert set(s)=={'from','to','class','construct','rule'}
        assert s['class'] in 'PCRSH' and s['construct'] and s['rule']
        assert 0<=s['from']<=s['to']<len(rows)
        for i in range(s['from'],s['to']+1):coverage[i]+=1
        counts[s['class']]+=s['to']-s['from']+1
        subtotal[s['class']]+=s['to']-s['from']+1
    assert set(coverage)==set(frozen) and set(coverage.values())=={1},p
    for alias in [p]+aliases.split():
        files.add(alias)
        other=list(csv.DictReader((R/f'results/swi-prolog/tokens/{alias}.tokens.tsv').open(),delimiter='\t'))
        assert [t['token'] for t in other]==[t['token'] for t in rows]
        cfg=alias.split('/')[0]
        expanded.setdefault(cfg,collections.Counter({c:0 for c in 'PCRSH'})).update(subtotal)
assert len(files)==90
records={}
for p in (R/'results/swi-prolog').glob('*/P0?/raw/*.json'):
    r=json.loads(p.read_text());v=r['run'];key=(v['configuration'],v['instance'],Path(v['program']['path']).name,v['mode'])
    assert key not in records;records[key]=(p,r)
    source=R/v['program']['path']
    assert source.relative_to(R/'programs/swi-prolog').as_posix() in files
    assert hashlib.sha256(source.read_bytes()).hexdigest()==v['program']['sha256'],str(source)
log=list(csv.reader((R/'results/swi-prolog/batch-log.tsv').open(),delimiter='\t'))
assert len(records)==len(log)==270
assert set(records)=={(row[1],row[2],row[3],row[4]) for row in log}
expected=set()
for key,(p,r) in records.items():
    if key[-1]!='behaviour':continue
    for s in r['stages']:
        for reading in (['finite','rational'] if key[1]=='P01c' else [None]):expected.add(key[:-1]+(s['stage'],reading))
actual=set()
norm=lambda s:re.sub(r'\s+','',s).rstrip('.')
for o in x['outcomes']:
    k=(o['configuration'],o['instance'],o['program'],o['stage'],o.get('reading'))
    assert k not in actual;actual.add(k)
    p,r=records[k[:3]+('behaviour',)]
    assert o['record']==p.relative_to(R).as_posix()
    stage=next(s for s in r['stages'] if s['stage']==o['stage']);a=stage['attempts'][-1];c=a['computations'][0]
    assert o['observations']['answers_verbatim']==[z['verbatim'] for q in c['queries'] for z in q['answers']]
    assert o['observations']['observe_raw']==a['observe']['raw']
    if not o['reached']:
        assert o['status']=='not reached' and 'before stage' in c['steps']['restart_cost_source']
        assert all(o[f] is None for f in ['semantic','representation','execution_state','simplification','identical_to_posed','residual_size','residual_equivalence'])
        continue
    assert o['semantic'] in ['complete','partial','unsound','undetermined','none reported']
    assert o['execution_state']==c['execution_state']['states']
    if o['representation']=='residual':
        assert o['simplification'] in ['reduced','reducible','inconsistency undetected']
        assert type(o['identical_to_posed']) is bool and o['residual_size'] is not None
        assert o['residual_equivalence']['equivalent'] is True
    else:assert all(o[f] is None for f in ['simplification','identical_to_posed','residual_size'])
    answers=o['observations']['answers_verbatim'];ni=o['instance']
    if ni.startswith('P03') and o['configuration']!='tabling' or (ni.startswith('P03') and ni!='P03f'):
        expected_answers={
          'P03a':['C=[1,2,3]'],'P03b':['A=[],B=[1,2]','A=[1],B=[2]','A=[1,2],B=[]'],
          'P03c':['B=[2,3]'],'P03d':['A=[1,2]'],'P03e':['B=[3,2,1]'],'P03f':['A=[3,2,1]']}
        assert [norm(v) for v in answers]==expected_answers[ni]
    if ni.startswith('P02') and o['semantic']=='complete':
        if o['representation']=='explicit':assert [norm(v) for v in answers]==['U=2,V=14,W=7']
        elif o['representation']=='solved form':assert [norm(v) for v in answers] in [['U=2'],['U=2,V=14']]
        else:
            raw=norm(a['observe']['raw'])
            if o['configuration'] in ['constraints','session']:
                assert raw in ['U+V#=16','W*U#=V','U+V#=16,W*U#=V','W*U#=V,U+V#=16','U=2,W*2#=V']
            else:
                assert ('sum_known(U,V,16)' in raw) or ('product_known(W,U,V)' in raw) or ('product_known(W,2,V)' in raw)
                assert raw.count('when(')==o['residual_size']['residual']['relations']
assert actual==expected and len(actual)==185
assert len(x['mode_differences'])==4
assert {(d['configuration'],d['instance'],d['mode'],d['stage']) for d in x['mode_differences']}=={(cfg,'P03f','storage',1) for cfg in ['plain','coroutines','constraints','session']}
for d in x['mode_differences']:
    assert d['behaviour']['semantic']=='unsound' and d['behaviour']['execution_state']==['budget']
    assert d['this_mode']['semantic']=='complete' and d['this_mode']['execution_state'] is None
    assert d['harness_faults'] and d['observations']['steps']['to_end'] is None
assert len(x['expressibility'])==90
for cfg in expanded:
    entries=[e for e in x['expressibility'] if e['configuration']==cfg]
    assert len(entries)==18 and len({e['subproblem'] for e in entries})==18
print('PASS: exact frozen-token coverage, all aliases, program hashes, all batch records and behaviour stages, both P01c readings, arithmetic/relation answer evidence, mode differences, and expressibility coverage.')
print('Distinct-text token totals:',dict(counts),'total',sum(counts.values()))
print('Expanded configuration totals (shared text counted for each using configuration):')
for cfg in sorted(expanded):print(cfg,dict(expanded[cfg]),'total',sum(expanded[cfg].values()))
