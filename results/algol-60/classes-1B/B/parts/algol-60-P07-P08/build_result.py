#!/usr/bin/env python3
from classify import *
xs=[classify_tokens(r[0]) for r in TEXTS]
result={'tokens':{x.key:x.sp for x in xs},'outcomes':[],'mode_differences':[], 'expressibility':[], 'late_definition':[], 's_mechanisms':[]}
records=[]
for conf in ['report','x1','x1sim']:
 for problem in ['P07','P08']:
  for sub in ['raw','raw-rerun-m2']:
   for f in sorted((BASE/f'results/algol-60/{conf}/{problem}/{sub}').glob('*.json')):
    records.append((str(f.relative_to(BASE)),json.loads(f.read_text())))

def residual_size(ir,iu,rr,ru,conditions):
 return {'input':{'primitive_relations':ir,'unknown_occurrences':iu},'residual':{'primitive_relations':rr,'unknown_occurrences':ru},'conditions':conditions,'convention':'Count remaining relation applications and occurrences of unknowns in them; named relation applications count once, compound arithmetic is decomposed into primitive relations with fresh unknowns. Solved bindings and definitions are recorded separately, not counted as undecided residual relations.'}

def classification(inst,stage,reading):
 p=inst.split('.')[0]
 z={'reached':True,'semantic':'complete','representation':'explicit','simplification':None,'identical_to_posed':None,'residual_size':None,'execution_state':['finished'],'residual_equivalence':None}
 if p.startswith('P07'):
  if p in ['P07b','P07c','P07f']:
   conditions={'P07b':'x+y=10 and x-y=4','P07c':'x+y=10','P07f':'x+y=10 and x+y=11'}[p]
   z.update(representation='residual',simplification={'P07b':'reducible','P07c':'reduced','P07f':'inconsistency undetected'}[p],identical_to_posed=True,execution_state=['suspended'],residual_size=residual_size(1 if p=='P07c' else 2,2 if p=='P07c' else 4,1 if p=='P07c' else 2,2 if p=='P07c' else 4,conditions))
   reason={'P07b':'Adding the equations gives 2x=14, hence x=7 and y=3, and substitution satisfies both. The retained conjunction is exactly the posed conjunction, so it denotes that singleton despite no elimination. Identifying/binding the unknowns removes the undecided relations.',
   'P07c':'The retained equation is exactly the input over all integers. Its solutions are (t,10-t) for every integer t. One arithmetic relation is necessary because arithmetic expressions are not solved-form terms; neither a bound nor enumeration is imposed.',
   'P07f':'Subtracting the two retained equal left sides requires 10=11. The conjunction denotes the empty set, exactly the valid outcomes, although no inconsistency is reported.'}[p]
   z['residual_equivalence']={'equivalent':True,'reason':reason}
  return z
 if p in ['P08a','P08b']:
  if stage==1:
   z.update(representation='solved form',residual_equivalence={'equivalent':True,'reason':'a is the three-cell sequence of the free element unknowns x,y,z; b and c are unconstrained. This is exactly stage 1 under either reading.'})
  elif stage in [2,3,4,5]:
   rr,ru,cond={2:(1,4,'rev((x,y,z),b), pending'),3:(2,6,'rev((x,y,z),b), pending; x=y'),4:(1,2,'x=y; a=(x,y,z), b=(z,y,x) are held bindings'),5:(2,4,'x=y and y=z; a=(x,y,z), b=(z,y,x) are held bindings')}[stage]
   ir,iu=(2,6) if stage==2 else (3,8) if stage in [3,4] else (4,10)
   before=stage<4
   simp='inconsistency undetected' if before and reading=='closed' else 'reducible'
   if before and reading=='closed':reason='Interpreted as the reported residual relation under the closed reading, rev has no instances. Its conjunction with the held equations therefore denotes the empty set, exactly the valid outcomes. The program does not detect/report that emptiness: it describes a pending application. This is a denotational classification of the residual, not a claim that the program adopted closed-world failure.'
   elif before:reason='Under the open reading an unavailable rev imposes no current value restriction on b; its pending status is retained operationally. The other equations are exactly a=(x,y,z)'+(' and x=y' if stage==3 else '')+'. Thus the residual denotes exactly the valid current outcomes. A smaller current-stage solved form can omit the pending condition'+(' and identify x with y' if stage==3 else '')+'; such omission would lose future work, which is separately observed.'
   elif stage==4:reason='The recursive cases give rev((x,y,z),(z,y,x)). Together with the held x=y this yields a=(y,y,z), b=(z,y,y), exactly the valid outcomes for all values of y,z. Aliasing x and y eliminates the remaining equality.'
   else:reason='The bindings plus x=y and y=z imply x=y=z and a=b=(z,z,z). Conversely every such binding satisfies the two held equalities and the reversed sequence. Both equalities can be removed by identifying the elements.'
   z.update(representation='residual',simplification=simp,identical_to_posed=False,residual_size=residual_size(ir,iu,rr,ru,cond),execution_state=['suspended'],residual_equivalence={'equivalent':True,'reason':reason})
  else:
   z['residual_equivalence']=None
  return z
 if p=='P08c':
  if stage==1:z.update(representation='solved form',residual_equivalence={'equivalent':True,'reason':'No constraint has been posed on any unknown. The free b printed by the program adds no restriction; projection to the posed unknowns is the empty substitution.'})
  elif stage in [2,3]:
   if reading=='closed':reason='At stage 2 rev has no cases; at stage 3 its only case has the empty input. Neither includes (1,2). Consequently the held application denotes the empty set under the closed reading, exactly the valid outcomes, without an explicit no-solution report.'
   else:reason='With rev still open, the missing cases may supply the application; the report keeps b unconstrained and the application pending. This is exactly the open valid outcome. The smaller current-stage solved form is b free; dropping the pending application would discard future work.'
   z.update(representation='residual',simplification='inconsistency undetected' if reading=='closed' else 'reducible',identical_to_posed=True,residual_size=residual_size(1,1,1,1,'rev((1,2),b), pending'),execution_state=['suspended'],residual_equivalence={'equivalent':True,'reason':reason})
  return z
 raise ValueError(inst)

def observations(d,s,a):
 c=a['computations'][0];inst=d['run']['instance'];p=inst.split('.')[0];k=s['stage'];raw=a['observe']['raw']
 susp={}
 for name,num in re.findall(r'\[suspended ([^\] ]+)\s+([+\-\d\s]+)\]',raw):susp[name]=int(re.sub(r'\s','',num))
 answers=[r['verbatim'] for q in c['queries'] for r in q['answers']]
 if p.startswith('P07'):
  unknown='For each arithmetic unknown, an integer value slot and a separate known Boolean; held relation Booleans retain undecided equations. No finite domain is imposed.'
  if p=='P07g':unknown='The specialized square solver retains the two integer candidates in xs[1:2] with nx; no unresolved unknown remains on this input.'
 else:unknown='Sequences are cell indices in parallel hd/tl arrays with 0 for empty; unknown sequences have value slots and known flags.'
 if p in ['P08a','P08b']:unknown+=' Elements x,y,z have separate indices and ev/ek value/known slots. Equal unknowns remain distinct slots constrained by held equalities until a value propagates; they are not aliased.'
 alt={'resumable_alternatives':0,'held_as':'none','note':'No search/backtracking or resumable alternative structure is held.'}
 if p=='P07g':alt.update(retained_answer_values=[3,-3],retained_answer_count=2,values_held_as='all at once',note='Both computed candidate values remain in xs; both were printed. These are retained answers, not pending resumable alternatives.')
 mechanism={'P07a':'Repeated passes over the three specific relation evaluators in the requested order; one relation at a time computes a place from known places. All six presentation orders reach (5,4,3).',
 'P07b':'One pass holds both equations because neither place is known; no simultaneous elimination.',
 'P07c':'One pass holds the integer sum relation without enumeration or bounds.',
 'P07d':'u=2 and v=14 are bound, then divisibility-checked integer division computes w=7.',
 'P07e':'u=2 and v=15 are bound; the evaluator tests integer divisibility and explicitly reports no solution.',
 'P07f':'Both sum relations remain held; neither can assign an initially unknown place, and their contradiction is not compared/detected.',
 'P07g':'entier(sqrt(c1)+0.5) proposes a root; its square is checked and both signs are stored and printed. The two roots 3,-3 exhaust x*x=9; this is algebraic reformulation rather than search.'}.get(p)
 if not mechanism:
  mechanism='The procedure code is already present; permission flags model definition availability. The application is retained in q2 and examined by a problem-specific holding pass.'
  if p in ['P08a','P08b']:
   mechanism+=' At stage 4 defined permits recursive forward rev/conc on symbolic element indices; x=y and y=z continue to wait until stage 6 supplies the first known element.'
  else:mechanism+=' At stage 3 the empty-input case does not cover (1,2), and missing-case status keeps q2. Stage 4 permits case 2 and yields (2,1).'
 advance='fresh stage' if k==1 else "live x1sim process receives this stage" if d['run']['configuration']=='x1sim' else 'harness recreates the deterministic prefix for the stage budget; record labels posing incremental, with recreated_for_budget notes. This is automatic harness work, not manual intervention.'
 withdrawal={'reported_conclusion_withdrawn':False,'note':'No earlier reported conclusion is explicitly withdrawn.'}
 if p.startswith('P08') and k==4:withdrawal['note']='The closed-reading valid set changes from empty to nonempty. The program never explicitly reported no solutions earlier, so it does not withdraw a no-solution conclusion; it resolves its pending application when permission is enabled.'
 return {'answers_verbatim':answers,'observe_verbatim':raw,'bindings_verbatim':a['observe'].get('bindings'), 'unknowns_representation':unknown,'alternatives':alt,'suspended':{'items':susp,'count':sum(susp.values()),'basis':'Counts read directly from printed suspension tags; zero follows the printed held-relations none and absence of any pending flag.'},'mechanism':mechanism,'conclusions':withdrawal,'manual_actions':d.get('manual_actions',[])+a.get('manual_actions',[]),'posing':a['posed'],'continuity':advance,'error_after_end':a.get('stderr') or None,'error_after_end_note':'An exhausted-input diagnostic after [end] is the documented harness shutdown, not a stage error.' if a.get('stderr') else None,'problem_operations':c.get('problem_operations'),'measurements':{'steps_stage':c['steps'].get('stage'),'steps_restated':c['steps'].get('restated'),'restart_cost':c['steps'].get('restart_cost'),'repeated_work':c['steps'].get('repeated_work'),'store':a.get('store'),'note':'Null is unavailable, never zero. Boundary zero suspended/resumable work above is a program-state observation, not an unavailable storage measurement.'}}

beh={}
for path,d in records:
 if d['run']['mode']!='behaviour':continue
 key=(d['run']['configuration'],d['run']['instance'],d['run']['program']['path']);beh[key]=(path,d)
 for s in d['stages']:
  a=s['attempts'][-1]
  # These records all reach every stage; this assertion prevents silently classing an unreached replay.
  assert a['print'] and '[end]' in a['print']
  for reading in ([None] if d['run']['problem']=='P07' else ['closed','open']):
   z={'configuration':key[0],'instance':key[1],'program':Path(key[2]).name,'record':path,'stage':s['stage'],'reading':reading}
   z.update(classification(key[1],s['stage'],reading));z['harness_fault']=('.INVALID.' in path or bool(d.get('harness_faults')))
   z['observations']=observations(d,s,a)
   z['rule']='SPECIFICATION Outcomes 1–3 (denotation, representation, residual simplification); problem valid outcomes; AMENDMENTS 3.1–3.4. P08 is separately interpreted under each reading; see equivalence reasoning.'
   assert z['execution_state']==a['computations'][0]['execution_state']['states']
   result['outcomes'].append(z)

# Independent comparison of every original measurement record with the same behaviour run.
comparisons=[]
for path,d in records:
 if d['run']['mode']=='behaviour':continue
 key=(d['run']['configuration'],d['run']['instance'],d['run']['program']['path']);bp,bd=beh[key]
 assert len(bd['stages'])==len(d['stages'])
 for s,bs in zip(d['stages'],bd['stages']):
  a=s['attempts'][-1];ba=bs['attempts'][-1]
  # Identical denoting reports and state entail the same classifications, including both P08 readings.
  def signature(t):return (t['observe']['raw'],[[r['verbatim'] for q in c['queries'] for r in q['answers']] for c in t['computations']],[c['execution_state'] for c in t['computations']],t['print'])
  assert signature(a)==signature(ba),(path,s['stage'])
 comparisons.append({'record':path,'behaviour_record':bp,'stages_compared':len(d['stages']),'classification_differences':0})
(OUT/'mode-comparison-audit.json').write_text(json.dumps(comparisons,indent=2)+'\n')

reasons={
 'P07a':'The arithmetic equalities have P evaluators in every direction by rule 19, but ALGOL has no native unknown/held equation. Separate known and held flags plus repeated problem-specific passes are R. This preserves the integer relation on all six orders without a finite bound.',
 'P07b':'The program-specific R holding representation denotes both simultaneous integer equations, although it does no elimination. Expressibility concerns preserving the relation, not producing the most reduced answer.',
 'P07c':'The R sum holder denotes all integer pairs with the given sum; it does not impose a finite enumeration. The native language cannot directly hold such an undecided arithmetic relation.',
 'P07d':'R known/held state lets the P multiplicative evaluator compute or test each place, including integer divisibility and zero factors; no rational-domain substitution is made.',
 'P07e':'Same integer multiplicative evaluator and R holding scheme as P07d; divisibility detects this instance\'s inconsistency.',
 'P07f':'The R holder preserves both integer sum equations exactly. Lack of inconsistency detection is a simplification result, not a change in denotation.',
 'P07g':'The explicit square-root/sign algorithm is R: the same unknown occupies both multiplicative inputs, and the program replaces that constraint by a specialized root algorithm. It retains and checks both signs; no finite domain bound is used.',
 'P08a':'The forward rev/conc bodies transcribe the cases (P, rules 3/15), but unknowns, held equalities and pending application state are problem-specific R. Availability is reformulated as permission for already present procedures. The staged mathematical relation can be represented this way; literal delivery of procedure code is not demonstrated.',
 'P08b':'The same problem-specific R representation as P08a retains an application whose permission never arrives. The forward definitions are already in the source, despite their flag remaining false. This expresses staged availability by reformulation, not code arrival.',
 'P08c':'The original conc/rev cases are nested P constructs. Permission flags and an added success/failure/missing-case status protocol are C/R; q2 and repeated examination are R holding for this relation, not a general definition loader. This preserves the open pending relation and the closed denotation on these inputs; actual code is present from startup.'}
for conf in ['report','x1','x1sim']:
 for p,reason in reasons.items():
  result['expressibility'].append({'configuration':conf,'subproblem':p,'direction':None,'expressibility':'expressible with reformulation','reason':reason+' No generic S mechanism is supplied or used. This judgement is based on the public inputs and structural program logic, not inaccessible hidden-variant results.'})

lookup={x.key:x for x in xs}
for conf in ['report','x1','x1sim']:
 for p in ['P08a','P08b','P08c']:
  ext='alg' if conf=='report' else 'a60';firstconf='report' if conf=='report' else 'x1';firstp='P08a' if p=='P08b' else p;key=f'{firstconf}/{firstp}.{ext}';x=lookup[key]
  ranges=[]
  for l,r,role in ([(28,52,'rev and conc procedures already in the program'),(74,85,'application tests defined and ak before calling rev'),(240,240,'stage 4 sets defined true')] if p!='P08c' else [(37,72,'procedure cases already in source; concdef/rev1def/rev2def gate them'),(74,86,'status-driven evaluator retains or clears q2'),(151,151,'stage 1 enables conc'),(160,160,'stage 3 reads base-fact data and enables case 1'),(162,162,'stage 4 enables case 2')]):
   a=x.before(l);b=x.before(r+1)-1;ranges.append({'from':a,'to':b,'role':role})
  evidence='The source contains the procedure bodies before any message is read; the stage writes a Boolean, not code. The retained application is problem-specific R state, the definition gates are C.'
  if p=='P08a':evidence+=' Records: stage 2 pending application 1, stage 3 pending 1 plus equality 1; stage 4 computes b=(z,y,x), while x=y remains; stage 6 reaches the all-42 solution.'
  elif p=='P08b':evidence+=' Records stop after stage 3 with pending application 1 and held equality 1. Failure is distinguishable from this printed pending state; the definition permission is never enabled.'
  else:evidence+=' Records: stage 2 application held; stage 3 still held with case 1 enabled and case 2 disabled; stage 4 yields b=(2,1). Stage 3 supplies the base-fact sequences as data, but the procedure/case structure is precompiled. Missing-case flags, not an arriving definition body, enable progress.'
  result['late_definition'].append({'configuration':conf,'program':f'{p}.{ext}','kind':'permission awaited','token_text':key,'constructs':ranges,'evidence':evidence,'resumption':'The program retains q2 and reexamines it automatically. report/x1 runs recreate the deterministic prefix for budgeting; x1sim uses one live process. No manual reapplication is recorded.'})

(OUT/'algol-60.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('result:',len(result['tokens']),'texts;',len(result['outcomes']),'outcome entries;',len(result['expressibility']),'expressibility entries;',len(result['late_definition']),'late-definition entries;',len(comparisons),'measurement records compared')
