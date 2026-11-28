"""Build the requested artifact from frozen-token annotations and permitted raw records.
No benchmark program or implementation is executed. Expected finite answers below
come directly from P04-P06; residual equivalence is an algebraic identity proof.
"""
from classify import *
from hashlib import sha256

def manifest():
 return list(csv.DictReader((TR/'TEXTS-1B-P04-P06.tsv').read_text().splitlines(),delimiter='\t'))

def read_records():
 records=[]
 for cfg in ['report','x1','x1sim']:
  for problem in ['P04','P05','P06']:
   for subdir in ['raw','raw-rerun-m2']:
    for p in sorted((ROOT/'results/algol-60'/cfg/problem/subdir).glob('*.json')):
     j=json.loads(p.read_text());assert j['run']['problem']==problem
     records.append((p,j))
 return records

def expected(instance,k):
 if instance in ['P04a','P04b']:return {1}
 if instance in ['P04c','P04e','P06e1']:return {True}
 if instance=='P05a':return [{1,2,3},{2,3},{3}][k-1]
 if instance=='P05b' and k==2:return {2,3}
 if instance=='P05c':return {1,2,3} if k==1 else set()
 if instance in ['P06a','P06b'] and (instance=='P06b' or k==2):return {2}
 if instance=='P06c' and k==2:return set()
 if instance=='P06d':return {(1,3)}
 if instance=='P06e2':return set()
 if instance=='P06e3':return {'brown'}
 return None

def value(text,instance):
 if instance in ['P04c','P04e','P06e1']:assert text.strip()=='true';return True
 if instance=='P06d':return tuple(int(x.replace(' ','')) for x in re.findall(r'[+-]?\s*\d+',text))
 if instance=='P06e3':return text.split('=')[1].strip()
 m=re.search(r'=\s*([+-]?\s*\d+)',text)
 assert m,(text,instance)
 return int(m[1].replace(' ',''))

def classify_stage(p,j,s):
 run=j['run'];instance=run['instance'];k=s['stage'];a=s['attempts'][-1];c=a['computations'][0]
 answers=[v['verbatim'] for q in c['queries'] for v in q['answers']]
 obs=a['observe']['raw'];bindings=a['observe']['bindings'];states=c['execution_state']['states']
 stopped_prefix=[n for n in a.get('notes',[]) if 'replay' in n.lower() and ('not reach' in n.lower() or 'stopped' in n.lower())]
 assert not stopped_prefix,stopped_prefix # No such stages exist in this supplied subset.
 residual=(instance=='P05b' and k==1) or (instance in ['P06a','P06c'] and k==1)
 semantic='none reported';representation=None;simplification=None;identical=None;size=None;equiv=None
 if residual:
  semantic='complete';representation='residual';simplification='reduced';identical=True
  cond='x > 1' if instance=='P05b' else 'not (x = 1)'
  size={'input':{'primitive_relations':1,'unknown_occurrences':1},'residual':{'primitive_relations':1,'unknown_occurrences':1},'condition':cond}
  equiv=('Equivalent: the held c1 and arrival flag encode exactly x > 1, which by SPEC arithmetic means integer x > 1. No bound or finite enumeration is imposed.' if instance=='P05b' else
         'Equivalent: xk is false and r1 holds the disequality with c1 = 1. Its denotation is {v in Values | not(v = 1)}, precisely the valid outcome. The unused integer slot xv is not a chosen value or a domain constraint. The relation is actually consulted at stage 2, so this is held state, not an echoed input.')
  reason='One primitive condition remains, with one unknown occurrence; eliminating it would change the solution set. It is identical to the posed condition.'
 elif instance in ['P04d','P04f']:
  if answers:
   representation='explicit';semantic='partial'
   for idx,ans in enumerate(answers):
    assert re.sub(r'\s+','',ans)==('s=('+','.join(['a']*idx)+')')
   reason=f'{len(answers)} valid finite a-sequences are collected; no finite equivalent representation of all infinitely many sequences is reported.'
  else:reason='No answer or held residual was readable before the execution stop; this is not a report of the empty set.'
 else:
  valid=expected(instance,k)
  obtained={value(x,instance) for x in answers} if answers else set()
  # Readable bindings are reported even if the answer printer suppresses them (SPEC Outcomes 1).
  if instance=='P06c' and k==2 and bindings and 'x' in bindings:
   obtained.add(int(bindings['x'].replace(' ','')))
   semantic='unsound';representation='explicit'
   reason='The query answer channel reports no solution, correctly, but observe() also reports the unconditional binding x = 1. SPEC Outcomes 1 explicitly counts readable held bindings as reported; that binding is invalid in the empty valid outcome. The contradictory report is therefore unsound under this literal rule.'
  elif obtained:
   assert valid is not None
   semantic='unsound' if obtained-valid else 'complete' if obtained==valid else 'partial'
   representation='explicit';reason=f'The collected value set is {sorted(obtained,key=str)!r}; the problem-defined valid set is {sorted(valid,key=str)!r}.'
  elif 'no solution' in obs:
   assert valid==set(),(instance,k,valid)
   semantic='complete';representation='explicit';reason='The program explicitly reports no solution, matching the empty valid set.'
  else:reason='No answer or held residual was readable before the execution stop; absence of output does not assert that there are no solutions.'
 # Common observations, preserving the actual report and unavailable measurements.
 alts=c['alternatives'];susp=c['suspended']
 if residual:
  unknown='x is unbound: an arrival/knownness flag and held relation constant represent it; no integer value has been selected. For P06 the residual has the full Values domain.'
 elif instance.startswith('P05'):
  unknown='x has the surviving explicit values in xv with xa live flags; no additional free unknown is reported.'
 elif instance.startswith('P04'):
  unknown='The source uses Boolean knownness flags and value/cell-index slots. No boundary state was available at the stop.' if not obs else 'The ground query has no unknowns.'
 else:
  unknown='No unknown remains in the reported explicit query result.' if semantic!='none reported' else 'No readable boundary state.'
 if instance.startswith('P05') and alts.get('problem_defined') is not None:
  alternatives={'kind':'stored values, all live at once','problem_defined':alts['problem_defined'],'pending_enumeration':False,
                'explanation':'Every surviving value has already been printed; the array is retained for later filtering. This is not resumable work for an answers request.'}
 else:
  alternatives={'kind':alts['held_as'],'at_boundary':alts['at_boundary'],'at_budget':alts['at_budget'],'peak':alts['peak'],'by_type':alts['by_type'],'problem_defined':alts['problem_defined'],
                'explanation':'Null counts are unavailable, not zero. A stopped P04 stack cannot be observed by this harness.' if not obs else 'No pending search alternatives are reported.'}
 withdrawn=[]
 if instance=='P05a' and k==2:withdrawn=['Earlier answer x = 1 is absent; xa is cleared and the new answer set lists only 2 and 3. No separate retraction event is printed.']
 if instance=='P05a' and k==3:withdrawn=['Earlier answer x = 2 is absent; xa is cleared and only 3 is listed. No separate retraction event is printed.']
 if instance=='P05c' and k==2:withdrawn=['All earlier answers 1, 2 and 3 are removed, with no solution and zero live x values.']
 if instance=='P06c' and k==2:withdrawn=['The prior conditional disequality is inconsistent with new x = 1; no solution is printed, alongside the conflicting observable binding. No earlier unconditional solution was claimed.']
 notes=[]
 if instance=='P04f':
  all_answers=re.findall(r'\[answer\](.*?)\[/answer\]',a['stdout'],re.S)
  notes.append(f'{len(all_answers)} completed answer tags occur in raw stdout; only the first {len(answers)} are collected under the cap. Both sets are finite proper subsets of the infinite valid outcomes.')
  notes.append('The recursive right definition enumerates lengths in increasing order when its callbacks work. Fixed 20000-cell storage and finite machine resources prevent a literal guarantee that every length will be reached in this program; x1sim fails already at a procedure-argument descriptor.')
 if run['configuration']=='x1sim' and instance in ['P04a','P04b']:
  notes.append('SIGKILL is recorded, with empty stderr and safety_limit.hit = false. The record identifies this as error, not timeout. Its near-60-second duration alone does not establish who sent SIGKILL; no safety rerun is recorded.')
 if instance=='P06c' and k==2:notes.append('If one treats inconsistent := true as qualifying and invalidating the printed binding, the intended denotation is the empty set and the semantic class would instead be complete. The primary classification follows the explicit observe-binding rule, rather than silently discarding that tag.')
 if instance.startswith('P06e'):notes.append('student(p) and maths(k) supply ground p and k before takes(p,k) is negated; the source preserves their conjunct order.')
 observations={
  'answers_verbatim':answers,'observe_verbatim':obs,'bindings_verbatim':bindings,
  'unknowns':unknown,'alternatives':alternatives,
  'suspended':{'at_boundary':susp['at_boundary'],'peak':susp['peak'],'items':susp['items'],
               'explanation':'One held relation awaits later information.' if residual else 'No waiting-work tag is reported; null counts remain unavailable.'},
  'conclusions_withdrawn':withdrawn,'manual_actions':j['manual_actions']+a['manual_actions'],
  'posing':a['posed'],'attempt_notes':a.get('notes',[]),'execution_basis':c['execution_state']['basis'],
  'error_verbatim':c['execution_state']['error_verbatim'],'stderr_verbatim':a['stderr'],
  'exit':a['exit'],'safety_limit':a['safety_limit'],
  'metrics':{'steps':c['steps'],'problem_operations':c.get('problem_operations'),'store':a['store']},
  'notes':notes,
 }
 return {'configuration':run['configuration'],'instance':instance,'program':Path(run['program']['path']).name,
         'record':str(p.relative_to(ROOT)),'stage':k,'reached':True,'semantic':semantic,
         'representation':representation,'simplification':simplification,'identical_to_posed':identical,
         'residual_size':size,'execution_state':states,'residual_equivalence':equiv,
         'semantic_reason':reason,'observations':observations,
         'harness_fault':('.INVALID.' in p.name or bool(j['harness_faults'])),
         'rule':'SPECIFICATION Outcomes 1-3; P04/P05/P06 valid outcomes; AMENDMENTS 3.1-3.4'+('; SPEC Outcomes 1: observable bindings are reported' if instance=='P06c' and k==2 else '')}

def expressive(cfg,instance,program):
 direction=None
 if instance.startswith('P04'):
  direction='known s -> truth' if instance in ['P04c','P04e'] else 'enumerate s' if instance in ['P04d','P04f'] else 'unknown x -> values'
  if instance in ['P04a','P04b']:
   ex='expressible'
   reason='A recursive procedure directly transcribes the sole loop case; assignment and reporting transcribe the other branch in the stated order. No value of x is ever used by loop. The published program additionally supplies optional knownness flags and success-continuation arguments (R); these are counted, but are unnecessary for this one-stage direction. Operational divergence is an outcome, not a failure of expressibility (rules 3 and 6).'
  elif instance=='P04e':
   ex='expressible'
   reason='With s known, the right definition is a mode-faithful recursive Boolean test: test the empty case, otherwise decompose the a-headed sequence and test its tail. These are P case-head tests and encoding operations (rules 2, 3, 15). The published multidirectional callback implementation adds optional knownness and continuation arguments (R), but this direction needs neither. Its x1sim descriptor error is an execution result.'
  else:
   ex='expressible with reformulation'
   reason='The left definition first calls alist(m) with m unknown, or the query itself requests all unknown sequences. A scalar Boolean function cannot supply those successive solutions. The program introduces knownness flags, explicit success-continuation arguments and continuation definitions (R), preserving the stated cases/conjuncts. This is a problem-specific procedural encoding, not a general search engine. Divergence and resource/runtime errors are recorded separately.'
 elif instance.startswith('P05'):
  ex='expressible with reformulation'
  reason='Native ALGOL variables do not hold undecided relations or a set of alternative bindings. The program supplies a problem-specific array of values/live flags and arrived-relation flags (R, rule 19); its fully known comparison tests and input facts remain P. Filtering retains exactly the stated fact alternatives; it imposes no new integer domain. The 1000-slot array is a capacity bound, not an enumeration restriction on x.'
 elif instance in ['P06a','P06c']:
  ex='expressible with reformulation'
  reason='A native Boolean comparison cannot represent an undecided negation over an unbound x. A problem-specific knownness flag and held-relation flags preserve the full disequality condition until the equality arrives (R, rule 19). The mathematical evaluator then gives x its value or tests the relation (P). P06c has a conflicting observation tag after detecting inconsistency; that reporting issue does not require a general supporting mechanism.'
 elif instance=='P06b':
  ex='expressible'
  reason='The equality arrives before the negation, so assignment followed by a fully known negated equality directly transcribes both stages (rules 3 and 8). This particular program nevertheless reuses the problem-specific R holding loop; those optional R tokens are counted and do not establish that reformulation is necessary for this direction/order.'
 elif instance=='P06d':
  direction='known s1,s2 -> d';ex='expressible'
  reason='mem and setdiff are computed by their stated cases, in the query direction, using the systems-file sequence encoding. Construction/decomposition and equality are P under rules 3 and 15. No separately written inverse or general mechanism is needed.'
 else:
  direction='enumerate p' if instance=='P06e3' else 'known p -> truth';ex='expressible'
  reason='Iteration is over the stated student, maths and takes facts (P, rule 6), with the conjuncts in presentation order. Both p and k are known before takes is negated. The mode-faithful procedure and closed-world fact tests transcribe nonmajor (rules 2, 3); printing is H.'
 return {'configuration':cfg,'subproblem':instance,'direction':direction,'expressibility':ex,'reason':reason}

def main():
 ann=make_annotations();m=manifest();first=[r['text'] for r in m]
 assert set(first)==set(ann)
 aliases={};texts_verified=[]
 for row in m:
  name=row['text'];shared=row['also the text of'].split();base=rows(name)
  for alias in [name]+shared:
   # Frozen tokens, not a fresh tokenizer, decide text sharing.
   assert [r['token'] for r in rows(alias)]==[r['token'] for r in base],(name,alias)
   aliases[alias]=name
   texts_verified.append(alias)
 tokens={key:finalize(ann[key]) for key in first}
 records=read_records();beh={};outcomes=[];diffs=[];compared=[]
 for p,j in records:
  if j['run']['mode']=='behaviour':
   k=(j['run']['configuration'],j['run']['instance'],j['run']['program']['path'])
   assert k not in beh
   beh[k]=(p,j)
   outcomes.extend(classify_stage(p,j,s) for s in j['stages'])
 for p,j in records:
  if j['run']['mode']=='behaviour':continue
  k=(j['run']['configuration'],j['run']['instance'],j['run']['program']['path']);bp,bj=beh[k]
  assert len(j['stages'])==len(bj['stages'])
  for bs,s in zip(bj['stages'],j['stages']):
   b=classify_stage(bp,bj,bs);mval=classify_stage(p,j,s)
   fields=['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence','harness_fault']
   bclass={f:b[f] for f in fields};mclass={f:mval[f] for f in fields}
   bo=b['observations'];mo=mval['observations']
   # Check the observed forms as well as the axes; costs/stores need not equal behaviour.
   same_observation=(bo['answers_verbatim']==mo['answers_verbatim'] and bo['observe_verbatim']==mo['observe_verbatim'] and bo['bindings_verbatim']==mo['bindings_verbatim'])
   compared.append({'record':str(p.relative_to(ROOT)),'stage':s['stage'],'same_classification':bclass==mclass,'same_observation':same_observation})
   if bclass!=mclass:
    diffs.append({'configuration':k[0],'instance':k[1],'program':Path(k[2]).name,'mode':j['run']['mode'],'record':str(p.relative_to(ROOT)),
                  'stage':s['stage'],'behaviour':bclass,'this_mode':mclass,'note':'Compared with '+str(bp.relative_to(ROOT))})
   assert same_observation,(p,s['stage'])
 expressibility=[];mechanisms=[]
 for key,(p,j) in sorted(beh.items()):
  cfg,instance,pr=key;program=Path(pr).name
  expressibility.append(expressive(cfg,instance,program))
  mechanisms.append({'configuration':cfg,'program':program,'mechanism':'none','listed_at_phase_4':True,'tokens':0})
 result={'tokens':tokens,'outcomes':outcomes,'mode_differences':diffs,'expressibility':expressibility,'late_definition':[], 's_mechanisms':mechanisms}
 (OUT/'algol-60.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
 # Independent completeness/coverage checks against both the text manifest and batch log.
 counts=collections.Counter();pertext={}
 for key,spans in result['tokens'].items():
  frozen=rows(key);seen=[0]*len(frozen);local=collections.Counter()
  for span in spans:
   assert span['class'] in 'PCRSH' and span['from']<=span['to']<len(frozen)
   for i in range(span['from'],span['to']+1):seen[i]+=1
   local[span['class']]+=span['to']-span['from']+1
  assert all(x==1 for x in seen),(key,collections.Counter(seen))
  counts.update(local);pertext[key]=dict(local)
 lines=[line.split('\t') for line in (ROOT/'results/algol-60/batch-log.tsv').read_text().splitlines()]
 batch=[(x[1],x[2],x[3],x[4]) for x in lines if len(x)>=5 and x[2].startswith(('P04','P05','P06'))]
 actual=[(j['run']['configuration'],j['run']['instance'],Path(j['run']['program']['path']).name,j['run']['mode']) for _,j in records]
 assert collections.Counter(batch)==collections.Counter(actual)
 assert len(outcomes)==72 and len(beh)==48 and len(compared)==96
 expected_programs={f'{cfg}/{prog}' for cfg,inst,prog,mode in batch if mode=='behaviour'}
 assert expected_programs==set(aliases)
 assert all(o['reached'] for o in outcomes)
 assert not any(o['harness_fault'] for o in outcomes)
 summary={'distinct_texts':len(tokens),'program_paths':len(aliases),'token_totals':{c:counts[c] for c in 'PCRSH'},'token_total':sum(counts.values()),
          'per_text':pertext,'behaviour_runs':len(beh),'behaviour_stages':len(outcomes),'measurement_records':sum(j['run']['mode']!='behaviour' for _,j in records),
          'measurement_stage_comparisons':len(compared),'mode_differences':len(diffs),'semantic_totals':dict(collections.Counter(o['semantic'] for o in outcomes)),
          'representation_totals':dict(collections.Counter(str(o['representation']) for o in outcomes)),
          'execution_totals':dict(collections.Counter(st for o in outcomes for st in o['execution_state'])),
          'expressibility_totals':dict(collections.Counter(e['expressibility'] for e in expressibility)),
          'measurement_reruns':sum('raw-rerun-m2' in str(p) for p,j in records),'invalid_records':sum('.INVALID.' in p.name for p,j in records),
          'checks':'Every frozen index is covered exactly once; all manifest aliases verified against frozen tokens; all batch-log P04-P06 runs matched; every behaviour stage classified; both measured modes compared stage by stage.'}
 (OUT/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
 (OUT/'mode-comparisons.json').write_text(json.dumps(compared,indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k!='per_text'},indent=2))

if __name__=='__main__':main()
