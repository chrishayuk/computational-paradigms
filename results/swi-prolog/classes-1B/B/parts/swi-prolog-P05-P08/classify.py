from pathlib import Path
import json, collections, re
BASE=Path('.')
OUT=Path('results/swi-prolog/classes-1B/B/parts/swi-prolog-P05-P08')
TP=BASE/'results/swi-prolog/tokens'
manifest=[r.split('\t') for r in (TP/'TEXTS-1B-P05-P08.tsv').read_text().splitlines()[1:]]
aliases={r[0]:r[1].split() if len(r)>1 else [] for r in manifest}

def frozen(name):
 return [(int(i),int(l),t) for i,l,t in (r.split('\t',2) for r in (TP/(name+'.tokens.tsv')).read_text().splitlines()[1:])]

def split_top(ts,start,end,delim=','):
 parts=[];dep=0;lo=start
 for j in range(start,end+1):
  t=ts[j][2]
  if t in ['(', '[']:dep+=1
  elif t in [')',']']:dep-=1
  if dep==0 and t==delim:
   parts.append((lo,j-1));lo=j
   # separator belongs to following construct, skip it for depth only
 parts.append((lo,end));return parts

def classify_tokens(name):
 ts=frozen(name);sp=[]
 def add(a,b,c,why,rule):
  if a<=b:sp.append({'from':a,'to':b,'class':c,'construct':why,'rule':rule})
 def body(a,b,parent='P'):
  # Separate the clause terminator from the goals it encloses.
  for l,h in split_top(ts,a,b):
   q=l+1 if ts[l][2]==',' else l
   fun=ts[q][2]
   if fun in ['h_param','h_wait','h_count','h_held']:
    add(l,h,'H','fixed harness call '+fun,'12, 13, 20; harness README §12')
   elif fun=='freeze':
    # freeze(Variable, Goal): prefix and closing delimiter C; goal independent.
    dep=0;comma=None
    for k in range(q,h+1):
     t=ts[k][2]
     if t=='(':dep+=1
     elif t==')':dep-=1
     elif t==',' and dep==1:comma=k;break
    add(l,comma,'C','freeze suspension and watched variable','1, 10, 20')
    add(comma+1,h-1,'P','integer comparison held by freeze','1, 10')
    add(h,h,'C','freeze closing delimiter','10')
   elif fun=='when':
    dep=0;comma=None
    for k in range(q,h+1):
     t=ts[k][2]
     if t=='(':dep+=1
     elif t==')':dep-=1
     elif t==',' and dep==1:comma=k;break
    add(l,comma,'C','when suspension condition (two known places)','1, 10, 20')
    add(comma+1,h-1,'R','call of supplied directional arithmetic evaluator','3, 8, 14')
    add(h,h,'C','when closing delimiter','10')
   elif fun in ['relations']:
    add(l,h,'C','traverse the problem-specified order of conjuncts','1, 10, 20')
   elif fun in ['sum_known','diff_known','product_known','factor']:
    add(l,h,'R','supplied directional arithmetic evaluator call','3, 8, 14, 20')
   elif fun=='!':add(l,h,'C','cut commits to selected arithmetic mode/case','2, 20')
   else:
    add(l,h,'P','stage information / problem relation: '+' '.join(t[2] for t in ts[q:h+1]),'1, 3, 6, 7, 9, 10, 20')
 lo=0
 for j,_,t in ts:
  if t!='.':continue
  hi=j;first=ts[lo][2];vals=[z[2] for z in ts[lo:hi+1]]
  if first==':-':
   c='C' if any(z in vals for z in ['dynamic','table','set_prolog_flag']) else 'P'
   add(lo,hi,c,'declaration: '+' '.join(vals[1:-1]),'11 (dynamic/unknown); 1 (table); 12 (library vocabulary)')
  elif first in ['unknowns','query'] and ':-' not in vals:
   add(lo,hi,'H','fixed harness '+first+' declaration','13; harness README §12')
  elif first=='relations':
   add(lo,hi,'C','ordered traversal of conjuncts supplied as instance parameter','1, 10')
  elif first in ['sum','diff','product','sum_known','diff_known','product_known','factor']:
   sep=lo+vals.index(':-')
   add(lo,sep,'R','extra arithmetic evaluator definition/case head','3, 8, 14')
   if first in ['sum','diff','product'] and 'when' in vals:
    body(sep+1,hi-1)
   else:
    # These are explicit directional implementations, not a primitive relation.
    for l,h in split_top(ts,sep+1,hi-1):
     q=l+1 if ts[l][2]==',' else l
     c='C' if ts[q][2]=='!' else 'R'
     add(l,h,c,'commit to arithmetic mode' if c=='C' else 'directional arithmetic branch / known-place test','2, 20' if c=='C' else '3, 8, 14, 20')
   add(hi,hi,'R','arithmetic evaluator clause terminator','10, 14')
  elif first in ['stage','query','relation'] and ':-' in vals:
   sep=lo+vals.index(':-');c='H' if first in ['stage','query'] else 'R'
   add(lo,sep,c,'fixed stage/query interface head' if c=='H' else 'auxiliary numbered-conjunct dispatch head (extra arguments)','13; harness README §12' if c=='H' else '3, 5, 10')
   body(sep+1,hi-1)
   add(hi,hi,c,'enclosing '+first+' clause terminator','10')
  else:add(lo,hi,'P','problem fact, constant, or definition case: '+first,'1, 3, 6')
  lo=hi+1
 assert lo==len(ts)
 sp.sort(key=lambda x:x['from'])
 indices=[i for s in sp for i in range(s['from'],s['to']+1)]
 assert indices==list(range(len(ts))),(name,indices)
 return sp

TOKENS={name:classify_tokens(name) for name in aliases}
# No program text changes class across configurations: supporting code is external to the text.

records=[]
for conf in ['constraints','coroutines','plain','session','tabling']:
 for prob in ['P05','P06','P07','P08']:
  for kind in ['raw','raw-rerun-m2']:
   for p in sorted((BASE/'results/swi-prolog'/conf/prob/kind).glob('*.json')):
    records.append((p.relative_to(BASE).as_posix(),json.loads(p.read_text())))

def not_reached(x,s,a,c):
 src=c['steps'].get('restart_cost_source') or ''
 faults=' '.join(x['harness_faults'])
 return 'before stage '+str(s)+' was posed' in src or bool(re.search(r'stage '+str(s)+r' attempt \d+: the replay did not reach stage '+str(s)+r'\b',faults))

def classify_stage(path,x,s):
 r=x['run'];n=s['stage'];a=s['attempts'][-1];c=a['computations'][0];sub=r['subproblem'];conf=r['configuration'];prog=Path(r['program']['path']).name
 ans=[z['verbatim'] for q in c['queries'] for z in q['answers']];raw=a['observe']['raw'];states=c['execution_state']['states'];error='error' in states
 reached=not not_reached(x,n,a,c)
 e={'configuration':conf,'instance':r['instance'],'program':prog,'record':path,'stage':n,'reached':reached,'semantic':None,'representation':None,'simplification':None,'identical_to_posed':None,'residual_size':None,'execution_state':states if reached else ['not reached'],'residual_equivalence':None,'observations':{},'rule':'SPECIFICATION Outcomes 1–3; AMENDMENTS 3.1–3.4','harness_fault':'.INVALID.' in path or bool(x['harness_faults'])}
 obs=e['observations']
 obs.update({'withdrawn_conclusions':None,'withdrawal_protocol':'No explicit retract/withdraw event is recorded. Later stage reports filter earlier possible assignments; an error is recorded separately.','answers_verbatim':ans,'observe_verbatim':raw,'print_verbatim':a['print'],'bindings':a['observe']['bindings'],'unknowns':'Unbound Prolog logic variables; aliases and list structure are unification; attributed variables carry residual goals when present.','posing':a['posed'],'suspended':c['suspended'],'alternatives':c['alternatives'],'manual_actions':a['manual_actions']+x['manual_actions'],'error_verbatim':c['execution_state']['error_verbatim'],'record_execution_state':c['execution_state'],'measurements':'Null measurements are unavailable. Attributed-variable counts include internal variables and are not suspended-goal counts. Storage fields are measured only in storage mode.','harness_faults':x['harness_faults']})
 if not reached:
  if sub.startswith('P08'): e['semantic_by_reading']={'closed':None,'open':None}
  obs['stopped_by']=c['steps'].get('restart_cost_source') or ('Replay failed at stage 2; '+ ' '.join(x['harness_faults']))
  if error:obs['stopped_by_actual']='The earlier replay raised the recorded error; the restart-cost prose calls this budget, but the exception and budget_exhausted=false establish an error.'
  obs['classification_note']='Copied answers/state belong to the stopped replay, not to this unposed stage. No semantic or representation class is assigned.'
  return e
 # A bare true in an exception snapshot has no bindings and is not a successful answer.
 held=bool(a['observe'].get('bindings'))
 if error and not ans:
  if held:
   e['semantic']='unsound';e['representation']='solved form'
   e['residual_equivalence']='Not equivalent: the observed binding leaves other unknowns free and does not hold the remaining arithmetic relations; its assignments include invalid outcomes.'
  else:
   e['semantic']='none reported';e['residual_equivalence']=None
  obs['exception_snapshot']='Actual bindings readable before unwinding are reported (SPECIFICATION Outcomes 1). A bare true with no binding is only an empty snapshot, not a success or a residual.'
 elif ans or 'engine_waiting_for_next_stage' in c['suspended'].get('items',{}):
  e['semantic']='complete';e['representation']='explicit'
  e['residual_equivalence']='Equivalent: the enumerated values are exactly the valid outcomes in the problem file.'
 else:
  empty=(sub=='P05c' and n>=2) or (sub=='P06c' and n==2) or sub in ['P06e2','P07e','P07f']
  e['semantic']='complete' if empty else 'unsound';e['representation']='explicit'
  e['residual_equivalence']='Equivalent: false explicitly reports the valid empty set.' if empty else 'Not equivalent: false reports the empty set although the problem has valid outcomes.'
 if sub=='P05b' and n==1 and not error:
  e.update(representation='residual',simplification='reduced',identical_to_posed=True,residual_size={'input':{'relations':1,'unknown_occurrences':1},'residual':{'relations':1,'unknown_occurrences':1},'normalization':'An integer lower bound and a delayed > test both express the one primitive comparison.'},residual_equivalence='Equivalent over the integers: X in 2..sup, or the held comparison X>1, denotes exactly every integer greater than 1; no finite bound is imposed.')
 if sub in ['P06a','P06c'] and n==1 and not (conf in ['plain','tabling']):
  e.update(representation='residual',simplification='reduced',identical_to_posed=True,residual_size={'input':{'relations':1,'unknown_occurrences':1},'residual':{'relations':1,'unknown_occurrences':1}},residual_equivalence='Equivalent over all problem values: dif(X,1) is exactly not(X=1), including atoms and finite sequences; it does not restrict X to integers.')
 if sub.startswith('P07') and not error and ans and 'suspended' in states:
  cases={'P07b':(2,4,'reducible',conf=='coroutines','Adding and subtracting the equations gives 2X=14 and 2Y=6, hence X=7,Y=3. Both residual equations are equivalent but smaller solved bindings exist.'),'P07c':(1,2,'reduced',True,'The residual is exactly X+Y=10 over integer X,Y. It has infinitely many solutions; one primitive relation with two unknown places is reduced.'),'P07f':(2,4,'inconsistency undetected',True,'Subtracting X+Y=10 from X+Y=11 gives 0=1. The two retained equations denote the empty set, but the system has not reported false.'),'P07g':(1,2,'reducible' if conf=='coroutines' else 'reduced',conf=='coroutines','Over integers X*X=9 iff X=-3 or X=3. The coroutine retains the two occurrences of X; CLP(FD) reduces this to the exact two-element domain, one occurrence.')}
  rel,occ,simp,ident,reason=cases[sub]
  e.update(representation='residual',simplification=simp,identical_to_posed=ident,residual_size={'input':{'relations':rel,'unknown_occurrences':occ},'residual':{'relations':rel,'unknown_occurrences':1 if sub=='P07g' and conf!='coroutines' else occ},'normalization':'Count arithmetic primitives, erasing delay/control wrappers. Domain membership counts as one relation; solver propagator/internal variable counts are separate.'},residual_equivalence='Equivalent. '+reason)
  if conf=='coroutines':obs['arithmetic_mechanism']='One relation at a time: when/2 calls the mode-specific evaluator once two places are nonvar. No elimination or enumeration is performed.'
  else:obs['arithmetic_mechanism']='CLP(FD) propagation without labeling or an imposed finite domain.'
 if sub=='P07g' and conf in ['plain','tabling']:
  obs['failure_reason']='product(X,X,9) reaches factor(9,X,X). Its first clause unifies the divisor X with 0 and cuts, then 9=:=0 fails; both valid square roots are lost.'
 if sub.startswith('P07a') and conf not in ['plain','tabling']:obs['arithmetic_mechanism']='Coroutine propagation through the decomposed sums.' if conf=='coroutines' else 'CLP(FD) propagation; all six presentation orders produce (5,4,3).'
 if sub=='P07d' and conf not in ['plain','tabling']:obs['arithmetic_mechanism']='The integer product relation, with U=2,V=14, forces W=7; integer division is guarded by divisibility in coroutines.'
 if sub=='P07e' and conf not in ['plain','tabling']:obs['arithmetic_mechanism']='Divisibility rejects 15/2 over integers; false detects the inconsistency.'
 if sub in ['P06a','P06c'] and conf in ['plain','tabling'] and n==1:obs['negation_decided']='At stage 1: X=1 succeeds with X unknown, so negation as failure fails immediately. It does not hold disequality.'
 if sub.startswith('P06e'):obs['negation_decided']='student(P) and maths(K) enumerate ground atoms before not takes(P,K). Only brown misses c301; smith misses neither course. p and k are known before each negation.'
 if sub=='P06d':obs['negation_decided']='Each head element and the second list are ground when not mem is tested. The resulting list is [1,3].'
 if sub.startswith('P05'):
  obs['problem_alternatives']='Values are enumerated in fact order by member/2, one at a time with later clauses available for backtracking, rather than a simultaneous set of live bindings. Enumeration is exhausted at the boundary of the answer-collection run.'
  obs['withdrawn_conclusions']=('The earlier possible value 1 is filtered out by X>1; the current result set is {2,3}.' if sub=='P05a' and n==2 else 'The earlier possible value 2 is filtered out by dif(X,2); the current result is X=3.' if sub=='P05a' and n==3 else 'All three earlier possible values are eliminated; false reports the contradiction.' if sub=='P05c' and n==2 else None)
  if conf=='session' and sub in ['P05a','P05c'] and n==1 or conf=='session' and sub=='P05a' and n==2:
   e['execution_state']=['alternatives pending']
   obs['execution_state_judgement']='The separate answer-collection run is finished. The continuing engine holds the first surviving answer and must retain backtracking alternatives: the next stage demonstrably selects a later pick value. Storage reports 0 relative to its mark, which does not establish absence of earlier choicepoints.'
 if sub.startswith('P08'):
  closed=e['semantic'];opened=e['semantic'];cl_reason=e['residual_equivalence'];op_reason=cl_reason
  pending=conf=='session' and 'unknown-fail' not in prog and n in [2,3]
  if n==1:
   e['representation']='solved form' if sub!='P08c' else 'explicit'
   cl_reason=op_reason='Equivalent: A=[X,Y,Z] with other unknowns free.' if sub!='P08c' else 'Equivalent: the arriving conc definition poses no value restriction; the no-unknown success is true.'
  elif pending:
   closed='complete';opened='complete';e['representation']='residual';e['simplification']='reduced';e['simplification_by_reading']={'closed':'inconsistency undetected','open':'reduced'};e['identical_to_posed']=True
   e['residual_size']={'input':{'relations':(n if sub!='P08c' else 1),'unknown_occurrences':((6 if n==2 else 8) if sub!='P08c' else 1)},'residual':{'undecided_applications':1,'argument_unknown_occurrences':2 if sub!='P08c' else 1},'normalization':'Known equality information is solved by unification and is recorded verbatim alongside the pending application. The undefined rev application cannot yet be decomposed into arithmetic primitives; count it as one undecided relation.'}
   cl_reason='Equivalent under closed: the retained rev application denotes no assignments because its currently arrived definition has no applicable instances. The inconsistency is undetected, since the system waits instead of reporting false. Under open it is a pending application.'
   op_reason='Equivalent under open: the equations are retained and rev is an application awaiting code, imposing no further current restriction. B is free.'
   obs['pending_application']='One engine waiting for an undefined rev/2 definition, in addition to the 0 attributed variables and 0 projected residual goals. The engine state, not a printed echo, retains and later resumes this application.'
   if sub=='P08c' and n==3:obs['partial_definition']='The record remains suspended after the base case arrives, and stage 4 succeeds without reposing. The whole stage 3 boundary has a held application; no false conclusion is reported.'
  elif n==2 and 'unknown-fail' in prog:
   closed='complete';opened='unsound';cl_reason='Equivalent under closed: undefined rev is false, so no assignments satisfy it.';op_reason='Not equivalent under open: false excludes all assignments, while B should remain free and the other equations should hold.'
   obs['undefined_state']='State 1: undefined relation is false. No application is retained; all later stages stop during replay at stage 2.'
  elif error:
   obs['undefined_state']='State 3: undefined procedure error; no pending application is retained.'
   if sub in ['P08a','P08b']:
    closed='unsound';opened='complete';cl_reason='Not equivalent under closed: the observable binding A=[X,Y,Z] admits assignments, whereas closed rev has no instances.';op_reason='Equivalent under open to the other information alone: the binding A=[X,Y,Z] is readable by observe. rev is lost on error, not retained as a condition; execution remains error.'
   else:
    closed=opened='none reported';cl_reason=op_reason=None
  elif n>=4:
   e['representation']='explicit' if sub=='P08c' or n==6 else 'solved form'
   cl_reason=op_reason=({'P08a':{4:'Unfolding the three-element rev gives B=[Z,Y,X]; X=Y gives B=[Z,Y,Y]. C remains free.',5:'Adding Y=Z identifies X,Y,Z and yields A=B=[Z,Z,Z]; C remains free.',6:'The first element of B is 42, so X=Y=Z=42 and C=[42,42].'},'P08c':{4:'Unfolding rev([1,2],B) using both cases gives B=[2,1].'}}[sub][n])
  e['semantic']=opened
  e['semantic_by_reading']={'closed':closed,'open':opened}
  e['residual_equivalence']={'closed':cl_reason,'open':op_reason}
  obs['semantic_field_convention']='Top-level semantic uses open; semantic_by_reading gives both required judgements.'
 return e

beh={}
outcomes=[]
for p,x in records:
 if x['run']['mode']=='behaviour':
  entries=[classify_stage(p,x,s) for s in x['stages']];outcomes.extend(entries);beh[(x['run']['configuration'],x['run']['instance'],x['run']['program']['path'])]=entries

fields=['reached','semantic','semantic_by_reading','representation','simplification','simplification_by_reading','identical_to_posed','residual_size','execution_state','residual_equivalence']
diffs=[]
for p,x in records:
 if x['run']['mode']=='behaviour':continue
 old=beh[(x['run']['configuration'],x['run']['instance'],x['run']['program']['path'])]
 for s,b in zip(x['stages'],old):
  e=classify_stage(p,x,s)
  if any(e.get(k)!=b.get(k) for k in fields):
   diffs.append({'configuration':e['configuration'],'instance':e['instance'],'program':e['program'],'mode':x['run']['mode'],'record':p,'stage':e['stage'],'behaviour':{k:b.get(k) for k in fields},'this_mode':{k:e.get(k) for k in fields},'harness_fault':e['harness_fault'],'note':'Instrumentation disagreement: behaviour reports X=3; storage reports false. The behaviour classification stands. No measurement rerun was provided.'})

express=[];late=[];support=[]
programs=sorted({(x['run']['configuration'],x['run']['subproblem'],Path(x['run']['program']['path']).name) for p,x in records if x['run']['mode']=='behaviour'})
for conf,sub,prog in programs:
 if sub.startswith('P07') and conf in ['plain','tabling','coroutines']:
  exp='expressible with reformulation';why='The supplied arithmetic predicates replace primitive equations by invented known-place cases and directional evaluators (R). They preserve the integer equations when decided; the plain/tabling code can err or prematurely fail operationally, while coroutine code retains unresolved equations. Expressibility records the encoding, separately from those run outcomes.'
 else:exp='expressible';why='The problem facts, definitions, stage constraints, and query have a direct transcription; control and external mechanisms affect execution rather than adding a new problem definition.'
 direction=None
 if sub.startswith('P08'):direction='rev: known finite input to output; conc: concatenation in definitions and known prefix to suffix at P08a stage 6'
 dirs=[None]
 if sub.startswith('P08'):
  dirs=['rev: finite input list shape to reversed output']
  if sub!='P08b': dirs.append('conc: input first and second lists to concatenation (inside rev)')
  if sub=='P08a': dirs.append('conc: known prefix and whole list to suffix (stage 6)')
 for direction in dirs: express.append({'configuration':conf,'subproblem':sub,'direction':direction,'program':prog,'expressibility':exp,'reason':why})
 # List configuration S even for programs which do not activate the hook.
 if conf=='session':
  support.append({'configuration':conf,'program':prog,'mechanism':'wait for an undefined procedure (cp_session_wait)','listed_at_phase_4':True,'tokens':None,'source':'harnesses/swi-prolog/S/session-wait.pl','token_ranges':None,'class':'S (except its fixed h_wait call, H)','listed_total_tokens':158,'count_note':'Loaded for every session program; activated by primary P08a/b/c only. No frozen token TSV for this supporting file is supplied, so a classifier token count/range is unavailable; 158 is the phase-4 declaration, not a retokenization. Its own_clause/retry/waiting implementation is S under rule 12; h_wait is H under rule 13.'})
 if sub.startswith('P08'):
  canonical=next(k for k,v in aliases.items() if k==conf+'/'+prog or conf+'/'+prog in v)
  ts=frozen(canonical)
  rev_indices=[i for i,l,t in ts if t=='rev'];assert_indices=[i for i,l,t in ts if t=='assertz']
  kind='code awaited' if conf=='session' and 'unknown-fail' not in prog else 'neither'
  ev={'token_text':canonical,'application_tokens':[s for s in TOKENS[canonical] if s['class']=='P' and 'rev (' in s['construct'] and not 'assertz' in s['construct']],'definition_tokens':[s for s in TOKENS[canonical] if 'assertz' in s['construct']],'construct_indices':{'rev_occurrences':rev_indices,'assertz_occurrences':assert_indices},'reason':('The primary text contains calls at stage 2 and assertz of the actual clauses only at later stages; no readiness flag gates preloaded rev code. The separately loaded S hook installs a waiting clause. Records show one waiting engine at stages 2/3, then same-computation results at stage 4 (P08a/c), or continued waiting through the last stage (P08b).' if kind=='code awaited' else 'The default undefined call raises an existence error (state 3), or the unknown=fail directive makes it fail (state 1). The application is not held; replay stops at stage 2 and the later definition stages are never reached.'),'support_source':'harnesses/swi-prolog/S/session-wait.pl' if kind=='code awaited' else None}
  late.append({'configuration':conf,'program':prog,'kind':kind,'evidence':ev})

result={'tokens':TOKENS,'outcomes':outcomes,'mode_differences':diffs,'expressibility':express,'late_definition':late,'s_mechanisms':support}
(OUT/'swi-prolog.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
counts=collections.Counter({k:0 for k in 'PCRSH'})
for name,sp in TOKENS.items():
 for s in sp:counts[s['class']]+=s['to']-s['from']+1
summary={'distinct_texts':len(TOKENS),'token_totals':dict(counts),'behaviour_records':len(beh),'behaviour_stages':len(outcomes),'not_reached':sum(not e['reached'] for e in outcomes),'semantic_open_or_only':dict(collections.Counter(e['semantic'] for e in outcomes)),'representations':dict(collections.Counter(e['representation'] for e in outcomes)),'states':dict(collections.Counter(st for e in outcomes for st in e['execution_state'])),'mode_differences':len(diffs),'records_compared':sum(x['run']['mode']!='behaviour' for p,x in records),'invalid_records':sum('.INVALID.' in p for p,x in records),'faulted_behaviour_stages':sum(e['harness_fault'] for e in outcomes)}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2));print('DIFFERENCES',[(e['configuration'],e['instance'],e['stage'],e['mode']) for e in diffs])
