import json,re,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('/Users/christopherhay/cp-roles/classifier-1B-B3')
D=json.loads((HERE/'record_summaries.json').read_text())
configs=['absys','absys-depth-first','absys-wake-back']

def span(a,b,c,construct,rule):return dict(from_=a,to=b,**{'class':c},construct=construct,rule=rule)
def s(a,b,c,construct,rule):
 d=span(a,b,c,construct,rule);d['from']=d.pop('from_');return d
P='METRICS: class P; rules 1, 6 (stated alternatives), 10 (construct scope).'
R='METRICS: class R (new definitions replacing primitive comparisons); PROTOCOL Writing a program 3; rule 10.'
tokens={}
for f in ['P05a.ab1','P05b.ab1','P05c.ab1']:
 rows=[s(0,18,'P','pick: closed-world definition, three cases in the stated order',P)]
 if f!='P05c.ab1':
  rows += [s(19,35,'R','gt: replace primitive greater-than by a positive arithmetic difference',R),s(36,56,'R','pos: new inductive positive-integer relation required by gt',R)]
 if f=='P05a.ab1':rows += [s(57,79,'R','ne: replace integer disequality by two gt cases',R)]
 base={'P05a.ab1':80,'P05b.ab1':57,'P05c.ab1':19}[f]
 names=['pk1','pk2','pk3']+({'P05a.ab1':['gtk','nek'],'P05b.ab1':['gtk'],'P05c.ab1':['xeq2','xeq3']}[f])
 for i,n in enumerate(names):rows.append(s(base+i*3,base+i*3+2,'P',f'constants table entry {n}: value supplied by the problem', 'METRICS class P; harnesses/absys/README 3.9, 3.12: constants are classed by their role, not automatically H.'))
 goals={'P05a.ab1':[(95,98,'P','stage 1 pick(x)'),(99,104,'R','stage 2 gt(x,gtk), reformulated greater-than'),(105,110,'R','stage 3 ne(x,nek), reformulated disequality')], 'P05b.ab1':[(69,74,'R','stage 1 gt(x,gtk), reformulated greater-than'),(75,78,'P','stage 2 pick(x)')], 'P05c.ab1':[(34,37,'P','stage 1 pick(x)'),(38,40,'P','stage 2 x=xeq2'),(41,43,'P','stage 3 x=xeq3')]}[f]
 for a,b,c,g in goals:rows.append(s(a,b,c,g,R if c=='R' else P))
 tokens['absys/'+f]=rows

def pending(o):
 n=0; omitted=0
 for b in o['active']:
  t=b['todo']
  if t:
   m=re.search(r'… (\d+) more',t)
   n+=len(t.split(';'))-(1 if m else 0)+(int(m[1]) if m else 0)
   if m:omitted+=int(m[1])
 return n,omitted

def classify(d,st):
 k=st['stage'];a=st['attempts'][-1];c=a['computations'][0];o=a['observe'];inst=d['run']['instance'];conf=d['run']['configuration']
 z=dict(configuration=conf,instance=inst,program=Path(d['run']['program']['path']).name,record=d['record'],stage=k,reached=True,semantic='complete',representation='explicit',simplification=None,identical_to_posed=None,residual_size=None,execution_state=c['execution_state']['states'],residual_equivalence=None,harness_fault=bool(d['faults']) or '.INVALID.' in d['record'],rule='SPECIFICATION Outcomes 1–3; P05 valid outcomes.')
 obs=dict(reported_verbatim_source='Last attempt computations[0].queries[0].answers and observe.raw in this record; the full state, including derivations beyond the cap, is observed.',unknowns='x is a concrete integer in each surviving finished derivation.',alternatives=dict(held=c['alternatives']['at_boundary'],held_as=c['alternatives']['held_as'],unit='derivation'),suspended=c['suspended'],conclusion_withdrawn=None,manual_actions=a['manual_actions'],posing=a['posed'],attempts=[dict(attempt=x['attempt'],limit_s=x['limit_s'],execution_state=x['computations'][0]['execution_state']['states'],safety_limit=x['safety_limit']) for x in st['attempts']],measurements='Behaviour step/store measurements are unavailable, not zero.',record_harness_faults=d['faults'])
 z['observations']=obs
 if inst=='P05a' and k>1:
  z.update(semantic='none reported',representation=None)
  obs.update(unknowns='No state was obtained for this stage.',outcomes_reported=None,alternatives=dict(held=None,held_as=c['alternatives']['held_as'],unit='derivation'),conclusion_withdrawn='Stage 2 should eliminate x=1; no post-constraint state or withdrawal was obtained.' if k==2 else None)
  if k==3:
   z.update(reached=False,semantic=None,execution_state=['not reached'],rule='AMENDMENTS 3.2: never reached is not a failure of the stage.')
   obs['stopped_by']='Replay of stage 2 timed out (both 60 s and 600 s attempts), before stage 3 could execute. Behaviour stdout contains only the completed prelude/stage-1 help replies; no completion reply for replayed stage 2. The separate restart measurement is not progress of this replay.'
  return z
 if inst=='P05b':
  obs['unknowns']='Unbound x and fresh d/e variables are printed as uninstantiated, with suspended arithmetic equations; some active branches already bind x but retain relations in their to-do queues.'
  obs['finished_values']=o['finished_values'];obs['active_derivations']=len(o['active']);obs['unbound_x_derivations']=o['unknown_blocks']
  obs['answers_cap']=20;obs['answers_collected']=c['queries'][0]['answer_count'];obs['answer_collection_ended_by']=c['queries'][0]['ended_by']
  obs['alternatives']['note']='All derivations are retained. Under depth-first only the first running one is elaborated until it hibernates/fails; finished ones remain available. There is no request-for-more-answers mechanism, hence no alternatives pending execution class.'
  n,omitted=pending(o)
  obs['retained_residual_size']=dict(suspended_primitive_additions=c['suspended']['at_boundary'],queued_top_level_relations=n,queue_entries_not_printed=omitted,derivations=o['blocks'],note='Queued relations include recursive pos calls and, at stage 2, pick. Some pending reactivations refer to arithmetic also retained as suspended, so these are storage occurrence counts, not a deduplicated constraint count. Unknown-occurrence count and complete primitive decomposition of abbreviated queues are unavailable.')
  if k==1:
   z.update(representation='residual',simplification='reducible',identical_to_posed=False,residual_size=f"Input: 1 primitive comparison x>1 (plus shared three-fact pick definition, not applied). Held: {o['blocks']} disjunctive derivations; {c['suspended']['at_boundary']} printed suspended primitive-addition occurrences and {n} queued top-level relation occurrences ({omitted} abbreviated). Exact distinct-relation/unknown-occurrence size unavailable; recursive pos is not a finite primitive expansion. These counts are not summed because reactivation queues may duplicate suspended relations.")
   z['residual_equivalence']='Equivalent to all integers x>1. By induction on its least definition, pos(q) denotes exactly the positive integers: base 1; each recursive case adds 1. Therefore exists d: x=1+d and pos(d) iff integer x>1. Each elaboration replaces a goal by equivalent cases or propagates an arithmetic equality. Completed cases together with all retained pending cases partition the original relation; the final pending pos tail preserves the unbounded remainder. A finite cap on answers does not discard the observe() state. The smaller equivalent representation is the single primitive comparison x>1.'
   obs['outcomes_reported']='Finite explicit prefix plus retained arithmetic/recursive frontier denoting the entire unbounded set; the comparison was reformulated and enumerated, not held as a native > constraint.'
   obs['answer_completeness']='Infinite: yes, the full held residual is a finite equivalent representation; the first 20 collected derivations bind x=2,...,21. Finished explicit prefix: x=2 through '+o['finished_values'][-1]+'.'
  else:
   z['residual_equivalence']='Equivalent as a whole to {2,3}. Finished derivations explicitly hold x=2 and x=3. Every unfinished branch retains pick(x), either directly printed or in the abbreviated pending queue, as well as its arithmetic/positive-tail conditions. These branches have candidate x>3 and are inconsistent with closed-world pick={1,2,3}; they add no outcomes. A binding such as x=1093 or x=1410 within such a branch is conditional on its pending pick and is not a separate unconditional solution. SPECIFICATION Outcomes 2 selects the valid, more explicit form {2,3}; redundant inconsistent branches are observations.'
   obs['outcomes_reported']='x=2 and x=3 explicitly, together with unfinished conditional branches that denote no further solutions.'
   obs['answer_completeness']='Finite: 2/2 valid values held; no invalid unconditional solution. Extra unfinished branches retain constraints that rule them out.'
   obs['conclusion_withdrawn']='The finite finished prefix from stage 1 loses all values other than 2 and 3. Their derivations disappear from the finished set; no separate retraction message is emitted. Some as-yet-unchecked active candidates remain with pick queued.'
   obs['supplementary_residual_simplification']='reducible as part of the whole union: all unfinished branches are inconsistent and could be dropped. Representation classification uses the valid explicit {2,3} form.'
  return z
 obs['outcomes_reported']=['x=1','x=2','x=3'] if k==1 else 'No derivation survives: the assertions are unsatisfiable.\n'
 obs['answer_completeness']='3/3 valid values, 0 invalid' if k==1 else 'Empty outcome explicitly reported: yes.'
 if inst=='P05c' and k>1:
  z['residual_equivalence']='Exact empty set: none of pick(1),pick(2),pick(3) equals 4; conjoining x=3 cannot restore a solution.'
  obs['conclusion_withdrawn']='All x=1,2,3 derivations were eliminated; the system prints the explicit unsatisfiability message.' if k==2 else 'No new withdrawal; the empty outcome remains empty. Stage 3 was accepted incrementally.'
 return z

outcomes=[];behaviours={}
for d in D:
 if d['run']['mode']=='behaviour':
  for st in d['stages']:
   z=classify(d,st);outcomes.append(z);behaviours[d['run']['configuration'],d['run']['instance'],st['stage']]=z
mode_differences=[]
for d in D:
 if d['run']['mode']=='behaviour':continue
 if d['run']['instance']!='P05b':continue
 if 'raw-rerun-m2' in d['record']:continue
 for st in d['stages']:
  b=behaviours[d['run']['configuration'],d['run']['instance'],st['stage']]
  this=dict(reached=True if st['stage']==1 else None,semantic='none reported',representation=None,simplification=None,identical_to_posed=None,residual_size=None,execution_state=['timeout'],residual_equivalence=None,harness_fault=bool(d['faults']) or '.INVALID.' in d['record'])
  if st['stage']==2:this['reachability_note']='Unavailable: the whole-text measurement has no per-assertion progress output. Its replayed stage 1 timed out in its own measured attempt, but this record cannot prove whether the stage-2 attempt got beyond that replay. Do not assign an independent failure to stage 2.'
  mode_differences.append(dict(configuration=d['run']['configuration'],instance='P05b',program='P05b.ab1',mode=d['run']['mode'],record=d['record'],stage=st['stage'],behaviour={k:b[k] for k in ['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence']},this_mode=this,note='Original measurement attempt and raised-limit rerun both timed out with no reported state. Steps/store unavailable, not zero. This is a measurement limit; the behaviour run retains complete information. The labelled m2 rerun is separately preserved and matches the final behaviour classification on both stages.'))
expressibility=[]
for conf in configs:
 for inst in ['P05a','P05b','P05c']:
  expressibility.append(dict(configuration=conf,subproblem=inst,direction=None,expressibility='expressible' if inst=='P05c' else 'expressible with reformulation',reason=('pick and added equalities directly transcribe the problem, without any R or S code.' if inst=='P05c' else 'The core has no >. The invented gt and pos definitions express a>b exactly over all integers, without a finite domain restriction: a=b+d, pos(d), where the least pos relation is all positive integers.'+(' ne(a,b)=gt(a,b) or gt(b,a) exactly expresses disequality on integers; the earlier > stage already restricts x to integers.' if inst=='P05a' else '')+' Nontermination/budget and poor simplification do not change declarative expressibility. R definitions and calls are identified in the token spans; no general supporting mechanism is supplied.')))
result=dict(tokens=tokens,outcomes=outcomes,mode_differences=mode_differences,expressibility=expressibility,late_definition=[],s_mechanisms=[])
(HERE/'absys.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')

# Validate against the frozen token indices, without invoking any tokenizer.
totals=collections.Counter()
for path,spans in tokens.items():
 lines=(ROOT/'results/absys/tokens'/(path+'.tokens.tsv')).read_text().splitlines()[1:]
 expected=[int(l.split('\t',1)[0]) for l in lines];actual=[]
 for row in spans:
  assert row['class'] in 'PCRSH'
  actual.extend(range(row['from'],row['to']+1));totals[row['class']]+=row['to']-row['from']+1
 assert actual==expected,(path,actual,expected)
manifest=(ROOT/'results/absys/tokens/TEXTS-1B-P05.tsv').read_text().splitlines()[1:]
assert set(tokens)=={l.split('\t')[0] for l in manifest}
assert len(outcomes)==24 and len(mode_differences)==12 and len(expressibility)==9
assert len({(x['configuration'],x['instance'],x['stage']) for x in outcomes})==24
assert all(x['harness_fault'] for x in outcomes if '.INVALID.' in x['record'])
# The m2 reruns agree in classified axes, including residual/explicit form.
for d in D:
 if 'raw-rerun-m2' in d['record']:
  for st in d['stages']:
   z=classify(d,st);b=behaviours[d['run']['configuration'],d['run']['instance'],st['stage']]
   assert all(z[k]==b[k] for k in ['reached','semantic','representation','simplification','identical_to_posed','execution_state','residual_equivalence'])
print('Validated token coverage:',dict(totals),'total',sum(totals.values()))
print('Behaviour outcomes:',collections.Counter(x['semantic'] if x['reached'] else 'not reached' for x in outcomes))
print('All 33 raw/rerun records compared; 24 behaviour stages; 12 original measurement differences; 12 m2 stages agree.')
