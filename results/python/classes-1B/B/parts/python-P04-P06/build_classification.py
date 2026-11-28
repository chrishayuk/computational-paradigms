"""Independent classifier. Reads only the brief's permitted inputs; never imports programs.
Uses the frozen TSV tokens, with AST positions solely to locate constructs (no tokenizer).
"""
import ast, csv, json, re
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path('/Users/christopherhay/cp-roles/classifier-1B-B')
OUT = Path(__file__).resolve().parent
TEXTS = list(csv.reader((ROOT/'results/python/tokens/TEXTS-1B-P04-P06.tsv').open(), delimiter='\t'))[1:]
RULES = {
 'P': 'METRICS rules 1, 2, 3, 6, 9 and 10: problem definition, case head, facts, primitive or query in its used direction',
 'C': 'METRICS rules 1, 2, 10 and 12: search, scheduling or mechanism invocation',
 'R': 'METRICS rules 10 and 19: problem-specific holding, dispatch and incremental bookkeeping',
 'S': 'METRICS rules 12, 15 and 19: reusable mechanism beyond the configuration core',
 'H': 'METRICS rule 13; harnesses/python/README.md section 7: fixed harness calls and output adapters',
}
LOCAL_S = defaultdict(list)
TOKEN_DATA = {}

def text(n):
 return ast.unparse(n)

def classify_tokens(path):
 cfg, filename = path.split('/')
 src = (ROOT/'programs/python'/path).read_text()
 lines = src.splitlines()
 tree = ast.parse(src)
 rows = list(csv.DictReader((ROOT/'results/python/tokens'/f'{path}.tokens.tsv').open(), delimiter='\t'))
 tokens=[]; cursors=defaultdict(int)
 for row in rows:
  i, line, tok = int(row['index']), int(row['line']), row['token']
  assert i==len(tokens)
  col=None
  if tok not in ('<NEWLINE>','<INDENT>','<DEDENT>'):
   col=lines[line-1].find(tok,cursors[line])
   assert col>=0,(path,i,line,tok)
   cursors[line]=col+len(tok)
  tokens.append(dict(i=i,line=line,col=col,token=tok))
 labels=[None]*len(tokens)
 def mark(n,cls,desc,rule=None,mechanism=None):
  if rule is None and (desc.startswith('evaluator ') or desc.startswith('evaluate problem relation')):
   rule='METRICS rule 19 evaluator split; rule 10: computation/known test/wait verdict classed separately'
  key=(cls,desc,rule or RULES[cls],mechanism)
  for t in tokens:
   if t['col'] is not None and (n.lineno,n.col_offset)<=(t['line'],t['col'])<(n.end_lineno,n.end_col_offset):
    labels[t['i']]=key
 def family_function(n):
  name=n.name
  if name in ('show','report'): return 'H',f'output adapter {name}',None
  if name in ('unify','children','done','either','negation') and cfg=='extended':
   mech = 'term unification' if name=='unify' else 'negation-as-failure interpreter' if name=='negation' else 'goal-list resolution'
   return 'S',f'{mech}: {name}',mech
  if name in ('place','decide','told','hold','pose','settle') and filename.startswith(('P06a','P06b','P06c')):
   return 'S',f'evaluator-driven relation holder: {name}','evaluator-driven relation holder'
  if name in ('told','settle') and filename.startswith('P05'):
   return 'C',f'thread scheduling: {name}',None
  if name in ('arrive','hold','source','keep','holds','test','on_x','post') and filename.startswith('P05'):
   return 'R',f'P05 holding helper {name}',None
  return 'P',f'definition {name}',None
 def stmt(n, cls=None, context=None, mech=None):
  if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str): return
  desc=f'{type(n).__name__} at line {n.lineno}: {lines[n.lineno-1].strip().split("#")[0].strip()}'
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
   cls,desc,mech=family_function(n)
   if context=='S': cls,desc,mech='S',f'{context} helper method {n.name}',mech or 'evaluator-driven relation holder'
   mark(n,cls,desc,mechanism=mech)
   for b in n.body: stmt(b,cls,n.name,mech)
   return
  if isinstance(n,ast.ClassDef):
   cls='S';mech='evaluator-driven relation holder' if n.name=='Unknown' else 'generic evaluator-to-queue adapter'
   mark(n,cls,f'{mech}: class {n.name}',mechanism=mech)
   for b in n.body:
    if isinstance(b,ast.FunctionDef):
     mark(b,'S',f'{mech}: method {b.name}',mechanism=mech)
     # The representation-only method is an output adapter.
     if b.name=='__repr__': mark(b,'H',f'output adapter {n.name}.__repr__')
   return
  if cls is None: cls='P'
  st=text(n)
  # A reusable mechanism's internals keep S, and output adapters keep H.
  protected=cls in ('S','H') and context not in ('equal','not_equal')
  if isinstance(n,(ast.Import,ast.ImportFrom)):
   cls='C';desc='import mechanism interface: '+st
  elif not protected:
   if isinstance(n,(ast.While,ast.If)) and ('cp.stage()' in text(n.test) or text(n.test).startswith('s.k ') or 's.replay' in text(n.test)):
    cls='H';desc='stage delivery/dispatch or replay output guard at line '+str(n.lineno)
   elif isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and text(n.value.func).startswith(('cp.','print')):
    cls='H';desc='fixed harness call/output at line '+str(n.lineno)
   elif context in ('equal','not_equal') and filename.startswith(('P06a','P06b','P06c')):
    if isinstance(n,ast.If): cls='R';desc='evaluator tests which places are known'
    elif isinstance(n,ast.Return):
     cls='R' if isinstance(n.value,ast.Constant) and n.value.value is None else 'P'
     desc='evaluator waits' if cls=='R' else 'evaluator decides/computes equality or negation'
   elif context in ('holds','test','source'):
    if isinstance(n,ast.Return) and not (isinstance(n.value,ast.Constant) and n.value.value is None): cls='P';desc='evaluate problem relation / its fact-derived values'
   elif context=='on_x' and isinstance(n,ast.Assign) and text(n.targets[0])=='holds.__name__':
    cls='H';desc='diagnostic name output adapter for already defined predicate'
   elif context=='post' and isinstance(n,ast.If): cls='C';desc='post constraint through Store.relation'
   elif context in ('hold','arrive') and filename.startswith('P05'):
    if isinstance(n,(ast.With,ast.While)) or any(x in st for x in ('changed.','threading.Thread','count[','told()','seen =')):
     cls='C';desc='thread coordination / waiting bookkeeping at line '+str(n.lineno)
   elif context is None:
    if isinstance(n,ast.Assign):
     target=text(n.targets[0])
     if target in ('binder','trail','stack','store','q','changed','count'):
      cls='C';desc='initialise mechanism/control state '+target
     elif target=='UNKNOWNS': cls='H';desc='names used only by output adapter'
     elif filename.startswith('P05') and target in ('values','held','waiting','failed','x_has_values','X'):
      cls='R';desc='P05 incremental holding state '+target
     elif filename.startswith(('P06a','P06b','P06c')) and target in ('known','held','waiting','failed','EVALUATOR'):
      cls='S';mech='generic evaluator-to-queue adapter' if cfg=='extended' else 'evaluator-driven relation holder';desc='reusable relation holder state '+target
   # stage body (context inherited below)
   if context=='stage':
    if isinstance(n,ast.For): cls='C';desc='enumerate query solutions/search at line '+str(n.lineno)
    elif isinstance(n,ast.Assign) and text(n.targets[0]) in ('holds',): cls='H';desc='collect truth of already computed answers'
    elif isinstance(n,ast.Expr) and isinstance(n.value,ast.Call):
     fn=text(n.value.func)
     if fn in ('arrive','decide','pose','q.wait','q.run','settle'):
      cls='C' if fn in ('q.wait','q.run','settle','pose') or (fn=='arrive' and cfg=='stdlib-concurrency') else 'R' if fn=='arrive' else 'C'
      desc='invoke '+fn
     elif fn=='held.append': cls='C';desc='post to evaluator-driven relation store'
     elif fn=='report':cls='H';desc='invoke output adapter'
    elif isinstance(n,ast.Assign) and text(n.targets[0]).startswith('values[') and cfg=='extended':
     cls='H';desc='copy already computed Store domain for observation/output'
  mark(n,cls,desc,mechanism=mech if cls=='S' else None)
  # Nested statements take their own class; inherited H here is only the header.
  childctx=context
  if isinstance(n,ast.While) and 'cp.stage()' in text(n.test): childctx='stage'
  if isinstance(n,(ast.If,ast.For,ast.While,ast.With,ast.Try)):
   base=cls
   if childctx=='stage':base='P'
   elif context in ('hold','arrive','source','keep','holds','test','on_x','post') and filename.startswith('P05'):base='R'
   if isinstance(n,ast.If) and 's.replay' in text(n.test):
    childctx='output';base='H'
   for field in ('body','orelse','finalbody'):
    for b in getattr(n,field,[]): stmt(b,base,childctx,mech)
  # Explicit else connective has no separate AST node: mark it with parent header class.
  if isinstance(n,ast.If) and n.orelse:
   first=n.orelse[0]
   for t in tokens:
    if t['col'] is not None and t['token']=='else' and n.body[-1].end_lineno<=t['line']<=first.lineno:
     labels[t['i']]=(cls,desc,RULES[cls],mech if cls=='S' else None)
     j=t['i']+1
     if tokens[j]['token']==':': labels[j]=labels[t['i']]
 for n in tree.body:stmt(n)
 # Reading staged constants is explicitly H even when nested in problem information.
 for n in ast.walk(tree):
  if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Attribute) and text(n.value) in ('s.constants','s.params','cp.params'):
   mark(n,'H','read staged constant/parameter '+text(n))
 # Split control call wrappers from their problem arguments, retaining separator rule 20.
 for n in ast.walk(tree):
  if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call):
   call=n.value; fn=text(call.func)
   if fn in ('arrive','pose','held.append','q.wait') and n.lineno>next(x.lineno for x in tree.body if isinstance(x,ast.While)):
    for arg in call.args:
     mark(arg,'P','stage information argument: '+text(arg),'METRICS rules 1, 6, 10 and 20: posed relation nested in mechanism call')
     if fn=='q.wait' and isinstance(arg,ast.Call) and text(arg.func)=='Relation':
      # The adapter constructor is supporting code; its semantic arguments are P.
      mark(arg,'C','construct generic evaluator-to-queue adapter')
      for a in arg.args:mark(a,'P','relation name/evaluator/places '+text(a))
 for n in ast.walk(tree):
  if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Attribute) and text(n.value) in ('s.constants','s.params','cp.params'):
   mark(n,'H','read staged constant/parameter '+text(n))
 # Separators belong to the following construct (rule 20).
 for t in tokens:
  if t['token']==',':
   j=t['i']+1
   if j<len(tokens) and tokens[j]['col'] is not None:
    labels[t['i']]=labels[j]
 # Significant layout belongs to the introducing/closing construct. No tokenization.
 scope=[];prev=None
 for t in tokens:
  i=t['i'];tok=t['token']
  if tok=='<NEWLINE>':labels[i]=prev
  elif tok=='<INDENT>':
   assert prev is not None
   scope.append(prev);labels[i]=prev
  elif tok=='<DEDENT>':
   assert scope,(path,i)
   labels[i]=scope.pop()
  else:
   assert labels[i] is not None,(path,i,t)
   prev=labels[i]
 assert not scope
 assert all(labels)
 spans=[]
 for t,key in zip(tokens,labels):
  c,desc,rule,mech=key
  if spans and spans[-1]['_key']==key:
   spans[-1]['to']=t['i']
  else:spans.append({'from':t['i'],'to':t['i'],'class':c,'construct':desc,'rule':rule,'_key':key})
 for s in spans:
  mech=s.pop('_key')[3]
  if s['class']=='S':LOCAL_S[(path,mech)].append({'from':s['from'],'to':s['to']})
 assert spans[0]['from']==0 and spans[-1]['to']==len(tokens)-1
 for a,b in zip(spans,spans[1:]):assert a['to']+1==b['from']
 TOKEN_DATA[path]=tokens
 return spans

result={'tokens':{},'outcomes':[],'mode_differences':[],'expressibility':[],'late_definition':[],'s_mechanisms':[]}
for row in TEXTS:result['tokens'][row[0]]=classify_tokens(row[0])
print('texts',len(result['tokens']),'tokens',sum(len(x) for x in TOKEN_DATA.values()))
print('counts',Counter({c:sum(s['to']-s['from']+1 for spans in result['tokens'].values() for s in spans if s['class']==c) for c in 'PCRSH'}))

# Outcomes are computed from the records, checked against the mathematical cases.
# These checks do not import or execute any study program or S mechanism.
def constants_by_stage(path):
 d={};stage=None;inside=False
 for line in (ROOT/path).read_text().splitlines():
  if 'CONSTANTS BEGIN' in line:inside=True;continue
  if 'CONSTANTS END' in line:break
  if not inside:continue
  m=re.match(r'\s*# stage (\d+)',line)
  if m:stage=int(m[1]);d.setdefault(stage,{});continue
  if line.strip() and not line.lstrip().startswith('#'):
   n=ast.parse(line).body[0];d[stage][n.targets[0].id]=ast.literal_eval(n.value)
 return d

def observations(r,a,c,k,prev):
 cfg=r['run']['configuration']; inst=r['run']['instance']
 printed=a.get('print') or ''
 obs={
  'answers_verbatim':[x['verbatim'] for q in c['queries'] for x in q['answers']],
  'printed_verbatim':printed,
  'bindings_verbatim':a['observe']['bindings'],
  'held_state_verbatim':a['observe']['raw'],
  'alternatives':{'registered_pending_count':c['alternatives']['at_boundary'],'by_type':c['alternatives']['by_type'],'problem_defined':c['alternatives']['problem_defined']},
  'suspended_work':{'count':c['suspended']['at_boundary'],'items':c['suspended']['items']},
  'manual_actions':a.get('manual_actions',[])+r.get('manual_actions',[]),
  'error_verbatim':c['execution_state'].get('error_verbatim'),
  'posing':a['posed'],
  'conclusions_withdrawn':[],
  'measurement_availability':'Null/absent measurements are unavailable, never zero (AMENDMENTS 3.1); no metric is inferred from a missing field.',
 }
 if inst.startswith('P04'):
  obs['unknown_representation']='None sentinel in generators and a binding dictionary' if cfg!='extended' else 'S.suspend.Var, followed through deref; trail restores tentative bindings'
  obs['alternatives']['held_as']='depth-first generator frames; closed after recursion errors' if cfg!='extended' else 'depth-first chronological backtracking stack, not simultaneous live solutions'
  if inst in ('P04a','P04b','P04c','P04d'):
   obs['search_note']='The recursive first branch never yields (or, for b, begins only after x=1); error/budget is operational, not a proof that the mathematical query has no solutions. Unbound Var/name entries are not solution bindings and generator addresses are not readable residual constraints.'
  if inst in ('P04d','P04f'):
   obs['every_solution_eventually_reachable']= inst=='P04f' and cfg=='extended'
   obs['reachability_reason']=('Right-recursive, base-first iterative S search visits each finite length in order; the renderer walks tails iteratively. Resource limits aside, no recursive Python call stack grows with length.' if cfg=='extended' and inst=='P04f' else 'alist-left descends without reaching the base case.' if inst=='P04d' else 'Base-first generator reaches increasing finite lengths, but the fixed Python recursion limit ultimately prevents reaching every length even if the instruction budget is raised.')
   if inst=='P04f':
    obs['printed_answer_count']=len(printed.splitlines())
    obs['collected_answer_cap']=c['queries'][0]['cap']
    obs['answer_note']='All printed answers, including those beyond the collection cap, are valid; finitely many do not denote the entire infinite solution set. The boundary binding is also inspected.'
 elif inst.startswith('P05'):
  obs['unknown_representation']='a finite candidate list plus a separate has-values flag; before a source arrives x remains unrestricted with its held comparison' if cfg!='extended' else 'no domain until a source arrives; then the Store domain is exactly pick facts, not an arbitrarily imposed finite domain'
  obs['alternatives']['held_as']='all surviving x values held together as a list'+(' and Store finite domain' if cfg=='extended' else '')+'; not merely a backtracking choice'
  if k>1 and prev:
   old=[x for q in prev['computations'][0]['queries'] for x in q['answers']]
   now=set(obs['answers_verbatim'])
   obs['conclusions_withdrawn']=[x['verbatim'] for x in old if x['verbatim'] not in now]
   obs['withdrawal_method']='The current candidate list/domain and the current answer set replace the earlier set; empty stages print no solution. No separate retract event is emitted.'
  if inst=='P05c' and k==3:obs['contradiction_note']='x=3 is added to the already empty candidate set/domain; it does not replace x=4. Stage 3 is reached.'
 elif inst in ('P06a','P06b','P06c'):
  obs['unknown_representation']='named Unknown object plus known dictionary; None is the evaluator sentinel' if cfg!='extended' else 'S.suspend.Var; the queue holds Relation objects until binding'
  obs['alternatives']['held_as']='none; deterministic equality/negative-equality evaluation'
  obs['negation_decision']='not decided while x has no value; one negative equality is held' if k==1 and inst!='P06b' else 'decided only once both equality places are known; the positive equality can bind x'
  if inst=='P06c' and k==2:obs['failure_note']='The observed x=1 is a component of inconsistent state, not an independent successful solution: the failed negative equality and explicit no-solution report make the report empty.'
 else:
  obs['unknown_representation']='None as generator query sentinel, bindings held in dict' if cfg!='extended' else 'Var terms; search undoes their bindings after enumeration, so the collected answers remain the evidence of solutions'
  obs['alternatives']['held_as']='depth-first generators/choice points; exhausted at the boundary'
  if inst.startswith('P06e'):
   obs['negation_decision']='student(p) enumerates/binds p, then maths(k) enumerates/binds k, then not takes(p,k) is ground; both are known before negation'
 return obs

def classify_stage(p,r,s,prev=None):
 a=s['attempts'][-1]; k=s['stage'];c=a['computations'][0]
 cfg=r['run']['configuration'];inst=r['run']['instance'];name=Path(r['run']['program']['path']).name
 vals=constants_by_stage(r['run']['program']['path'])
 entry={'configuration':cfg,'instance':inst,'program':name,'record':str(p.relative_to(ROOT)),'stage':k,'reached':True,'semantic':None,'representation':None,'simplification':None,'identical_to_posed':None,'residual_size':None,'execution_state':c['execution_state']['states'],'residual_equivalence':None,'observations':observations(r,a,c,k,prev),'rule':'SPECIFICATION Outcomes 1–3; valid outcomes of problems/04, 05 or 06; AMENDMENTS 3'}
 if '.INVALID.' in p.name or r.get('harness_faults'):entry['harness_fault']=True
 # Amendment 3.2: a replay must actually reach the target stage.
 replay_note=' '.join(str(x) for x in a.get('notes',[]))
 not_reached=bool(re.search(r'(?:did not|never|not) reach|not posed|never posed', replay_note, re.I))
 if not_reached:
  entry.update(reached=False,semantic='none reported',execution_state=['not reached'])
  entry['observations']['stopped_by']=replay_note
  return entry
 answers=entry['observations']['answers_verbatim'];printout=a.get('print') or ''
 equivalent=True;reason=''
 if inst.startswith('P04'):
  if inst in ('P04a','P04c','P04d'):
   assert not answers and not printout
   entry['semantic']='none reported'
   reason='No answer or solved constraint representation is reported; pending search is not a residual report.'
   equivalent=None
  elif inst=='P04b':
   expected=f"x = {vals[1]['X_VALUE']}";assert answers==[expected]
   entry.update(semantic='complete',representation='explicit')
   reason='loop is empty in the least relation; the only valid solution is the displayed equality, which was reported before error/budget.'
  elif inst=='P04e':
   seq=vals[1]['SEQUENCE'];truth=all(x=='a' for x in seq)
   assert answers==(['true'] if truth else [])
   entry.update(semantic='complete',representation='explicit')
   reason='The finite input is an all-a list; the one truth outcome was reported and enumeration finished.'
  else:
   assert inst=='P04f'
   printed=printout.splitlines();assert printed
   lengths=[]
   for line in printed:
    assert line.startswith('s = ⟨') and line.endswith('⟩')
    content=line[5:-1]
    elems=[] if not content else content.split(',')
    assert all(e=="'a" for e in elems),(inst,line)
    lengths.append(len(elems))
   assert lengths==list(range(len(lengths)))
   assert answers==printed[:20]
   # Check observed boundary binding too, never infer it to be a solution merely from a name.
   bound=a['observe']['bindings']['s']
   if cfg=='extended':
    # No execution: parsing the finite cons representation as literal data only.
    term=ast.literal_eval(bound);n=0
    while term!=():
     assert isinstance(term,tuple) and len(term)==2 and term[0]=='a'
     term=term[1];n+=1
   else:
    term=ast.literal_eval(bound);assert all(x=='a' for x in term);n=len(term)
   entry.update(semantic='partial',representation='explicit')
   entry['observations']['boundary_sequence_length']=n
   equivalent=False;reason=f'{len(printed)} printed finite all-a sequences (lengths 0–{len(printed)-1}), plus the valid boundary binding of length {n}, form a nonempty finite subset of the infinite valid outcome set; no finite equivalent residual is reported.'
 elif inst.startswith('P05'):
  if inst=='P05b' and k==1:
   threshold=vals[1]['GREATER_THAN'];assert not answers and c['suspended']['at_boundary']==1
   entry.update(semantic='complete',representation='residual',simplification='reduced',identical_to_posed=True,residual_size={'input':{'relations':1,'unknown_occurrences':1},'residual':{'relations':1,'unknown_occurrences':1},'conditions':f'x > {threshold}'})
   reason=f'The held comparison means exactly all integer x>{threshold}. There is no finite domain before pick arrives. One undecided primitive relation and one unknown occurrence are necessary, so it is reduced and unchanged.'
  else:
   facts=list(vals[1 if inst!='P05b' else 2]['PICK_FACTS'])
   expected=list(facts)
   if inst=='P05a':
    if k>=2:expected=[x for x in expected if x>vals[2]['GREATER_THAN']]
    if k>=3:expected=[x for x in expected if x!=vals[3]['DIFFERENT_FROM']]
   elif inst=='P05b':expected=[x for x in expected if x>vals[1]['GREATER_THAN']]
   elif inst=='P05c':
    for st in range(2,k+1):expected=[x for x in expected if x==vals[st]['EQUAL_TO']]
   assert set(answers)=={f'x = {v}' for v in expected},(p,k,answers,expected)
   if not expected:assert 'no solution' in printout
   assert c['alternatives']['problem_defined']['values of x still held']==len(expected)
   entry.update(semantic='complete',representation='explicit')
   reason=f'Intersect the closed-world pick facts {facts} with every comparison/equality received through stage {k}; the result is {expected}. All and only those values are reported; empty lists/domains are explicitly declared no solution. The imposed domain is justified by pick itself (AMENDMENTS 3.4).'
 elif inst in ('P06a','P06b','P06c'):
  if k==1 and inst!='P06b':
   excluded=vals[1]['NOT_EQUAL_TO'];assert not answers and c['suspended']['at_boundary']==1
   entry.update(semantic='complete',representation='residual',simplification='reduced',identical_to_posed=True,residual_size={'input':{'relations':1,'unknown_occurrences':1},'residual':{'relations':1,'unknown_occurrences':1},'conditions':f'not (x = {excluded})'})
   reason=f'The retained negative equality excludes exactly {excluded} and imposes no integer restriction: integers, atoms and finite sequences other than that value are admitted. It is the original one-relation, one-unknown condition; no smaller solved form expresses that exclusion.'
  else:
   known={};neq=[]
   for st in range(1,k+1):
    if 'EQUAL_TO' in vals[st]:known['x']=vals[st]['EQUAL_TO']
    if 'NOT_EQUAL_TO' in vals[st]:neq.append(vals[st]['NOT_EQUAL_TO'])
   v=known['x'];valid=v not in neq
   assert answers==([f'x = {v}'] if valid else [])
   if not valid:assert 'no solution' in printout
   entry.update(semantic='complete',representation='explicit')
   reason=f'Equality binds x={v}; checking every received negative equality gives '+('the singleton displayed solution.' if valid else 'the empty set, which is explicitly reported. The failed relation ledger qualifies the internal binding; it is not a successful x=1 outcome.')
 elif inst=='P06d':
  first,second=vals[1]['FIRST'],vals[1]['SECOND'];expected=tuple(x for x in first if x not in second)
  expected_text='d = ⟨'+','.join(map(str,expected))+'⟩'
  assert answers==[expected_text]
  entry.update(semantic='complete',representation='explicit')
  reason=f'For each member of the finite first sequence, keep it exactly when membership in the finite closed second sequence is false. This yields {expected}, with order preserved, the one valid binding.'
 else:
  assert inst.startswith('P06e')
  v=vals[1];students=v['STUDENT_FACTS'];maths=v['MATHS_FACTS'];takes=v['TAKES_FACTS']
  expected={p for p in students if any((p,k) not in takes for k in maths)}
  if inst=='P06e3':assert set(answers)=={f"p = '{p}" for p in expected}
  else:
   truth=v['QUERY_STUDENT'] in expected;assert answers==(['true'] if truth else [])
   if not truth:assert 'false' in printout
  entry.update(semantic='complete',representation='explicit')
  reason=f'Finite closed-world fact check: a student is a nonmajor iff at least one maths course is missing from their takes facts. The nonmajors are {sorted(expected)}. student and maths ground both negated arguments before takes is tested.'
 entry['residual_equivalence']={'equivalent':equivalent,'reason':reason}
 return entry

records=[]
for cfg in ('core','extended','stdlib-concurrency'):
 for prob in ('P04','P05','P06'):
  for dirname in ('raw','raw-rerun-m2'):
   for p in sorted((ROOT/'results/python'/cfg/prob/dirname).glob('*.json')):
    records.append((p,json.loads(p.read_text())))
by_behaviour={}
for p,r in records:
 if r['run']['mode']!='behaviour':continue
 key=(r['run']['configuration'],r['run']['instance'],r['run']['program']['path'])
 assert key not in by_behaviour
 entries=[];prev=None
 for s in r['stages']:
  e=classify_stage(p,r,s,prev);result['outcomes'].append(e);entries.append(e);prev=s['attempts'][-1]
 by_behaviour[key]=(p,r,entries)

comparison_fields=['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state']
measurement_comparisons=0
for p,r in records:
 if r['run']['mode']=='behaviour':continue
 key=(r['run']['configuration'],r['run']['instance'],r['run']['program']['path'])
 bp,br,bes=by_behaviour[key]
 assert len(br['stages'])==len(r['stages'])
 prev=None
 for s,bs,be in zip(r['stages'],br['stages'],bes):
  e=classify_stage(p,r,s,prev);prev=s['attempts'][-1]
  measurement_comparisons+=1
  bcls={k:be[k] for k in comparison_fields};mcls={k:e[k] for k in comparison_fields}
  if bcls!=mcls:
   result['mode_differences'].append({'configuration':key[0],'instance':key[1],'program':Path(key[2]).name,'mode':r['run']['mode'],'record':str(p.relative_to(ROOT)),'stage':s['stage'],'behaviour':bcls,'this_mode':mcls,'note':'Instrumentation disagreement; behaviour remains the result of record.'})
  # Confirm more than the axes: every answer, print and normalized held state is identical.
  a=s['attempts'][-1];ba=bs['attempts'][-1]
  norm=lambda x:re.sub(r'0x[0-9a-f]+','ADDR',x or '')
  assert norm(a['observe']['raw'])==norm(ba['observe']['raw']),(p,s['stage'])
  assert a['observe']['bindings']==ba['observe']['bindings']
  assert a['print']==ba['print']
  assert e['observations']['answers_verbatim']==be['observations']['answers_verbatim']

# Log completeness (the log has no heading).
logrows=[x for x in csv.reader((ROOT/'results/python/batch-log.tsv').open(),delimiter='\t') if x[2].startswith(('P04','P05','P06'))]
assert len(logrows)==len(records)
assert Counter((x[1],x[2],x[3],x[4]) for x in logrows)==Counter((r['run']['configuration'],r['run']['instance'],Path(r['run']['program']['path']).name,r['run']['mode']) for p,r in records)

# Expressibility concerns what the configuration can express, not whether the author
# chose an unnecessarily general supporting implementation for this program.
for cfg in ('core','extended','stdlib-concurrency'):
 for inst in ['P04a','P04b','P04c','P04d','P04e','P04f','P05a','P05b','P05c','P06a','P06b','P06c','P06d','P06e1','P06e2','P06e3']:
  category='expressible';direction=None
  if inst.startswith('P04'):
   direction='ground membership' if inst in ('P04c','P04e') else 'enumeration'
   reason='The core generator has one branch per problem case and preserves case/conjunct order. None is only its query-mode sentinel. These are mode-faithful P transcriptions (rule 3); operational divergence/recursion errors do not change expressibility.'
   if cfg=='extended':reason+=' Extended includes that same core. Its supplied program instead uses P relation cases with S unification/resolution/search, all separately counted; the optional S implementation does not make a core-transcribable problem inexpressible.'
  elif inst.startswith('P05'):
   category='expressible with reformulation'
   reason='The problem-specific holder represents surviving x values and retains comparisons until a finite source arrives, dispatching only pick, >, != and = on x. That is R by rule 19; actual evaluators are P. Intersection with arriving information preserves the relation, including the empty set and the unbounded comparison before pick.'
   if cfg=='extended':reason+=' The supplied Store-based program additionally uses S, but extended admits the core problem-specific R holder. The domain used here comes only from pick/equality, not an arbitrary bound.'
  elif inst in ('P06a','P06b','P06c'):
   category='expressible with reformulation'
   reason='A relation-specific state holding an excluded value and an optional equality binding represents exactly negative equality until the binding arrives; it then tests the P equality/negation evaluator. Thus Python can express this staged problem with rule-19 holding reformulation, although a direct Python not on an unbound placeholder cannot transcribe it. The supplied programs choose a more general evaluator-driven S holder (or Queue plus a generic S Relation adapter), which is counted and not credited as native suspension. The evaluator known-place tests and wait verdicts are R. This expressibility judgement is about the configuration, not an assertion that the supplied run is S-free.'
  elif inst=='P06d':
   direction='s1,s2 -> d'
   reason='The core function computes d from known sequences with exactly the three stated cases in order. Rule 3 makes this return-value direction P; no inverse direction is requested.'
   if cfg=='extended':reason+=' Extended admits the same function. Its supplied relational version additionally uses S unification, resolution and ground negation-as-failure; those mechanisms are separately listed.'
  else:
   direction='p -> truth' if inst!='P06e3' else 'enumerate p'
   reason='student and maths enumerate stated facts (P, rule 6); nonmajor preserves student, maths, not takes order. Built-in in on closed takes facts is equivalent in the ground direction (P, rule 9). The same core generator serves ground/open student queries (rule 3).'
   if cfg=='extended':reason+=' Extended admits this core transcription; the supplied relational version uses separately counted S unification/resolution/ground negation-as-failure.'
  result['expressibility'].append({'configuration':cfg,'subproblem':inst,'direction':direction,'expressibility':category,'reason':reason})

# Supporting mechanisms: phase-4 code is counted once per mechanism/configuration;
# every use is listed. Program-local S spans refer to the canonical distinct text.
for cfg in ('core','extended','stdlib-concurrency'):
 for inst in ['P04a','P04b','P04c','P04d','P04e','P04f','P05a','P05b','P05c','P06a','P06b','P06c','P06d','P06e1','P06e2','P06e3']:
  path=f'{cfg}/{inst}.py';listed=[]
  if cfg=='extended':
   if inst.startswith('P05'):listed=[('constraint propagator','harnesses/python/S/propagate.py',1260),('backtracking search','harnesses/python/S/search.py',176)]
   elif inst in ('P06a','P06b','P06c'):listed=[('suspension queue / logic variables','harnesses/python/S/suspend.py',537)]
   else:listed=[('backtracking search','harnesses/python/S/search.py',176),('suspension queue / logic variables','harnesses/python/S/suspend.py',537)]
  for mech,source,count in listed:
   result['s_mechanisms'].append({'configuration':cfg,'program':inst+'.py','mechanism':mech,'listed_at_phase_4':True,'tokens':count,'source':source,'token_ranges':None,'counting':'phase-4 frozen size; counted once per mechanism in extended, not summed across users'})
  canonical=next(row[0] for row in TEXTS if path in row)
  for (tp,mech),ranges in LOCAL_S.items():
   if tp!=canonical:continue
   result['s_mechanisms'].append({'configuration':cfg,'program':inst+'.py','mechanism':mech,'listed_at_phase_4':False,'tokens':sum(x['to']-x['from']+1 for x in ranges),'source':'programs/python/'+canonical,'token_ranges':ranges,'counting':'S-token occurrences in this program; identical mechanism bodies shared across programs are counted once per configuration in mechanism totals'})

(OUT/'python.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print('behaviour records',len(by_behaviour),'behaviour stages',len(result['outcomes']),'measurement records',len(records)-len(by_behaviour),'measurement stage comparisons',measurement_comparisons,'mode differences',len(result['mode_differences']))
print('semantics',Counter(e['semantic'] for e in result['outcomes']))
print('representations',Counter(e['representation'] for e in result['outcomes']))
print('states',Counter(s for e in result['outcomes'] for s in e['execution_state']))
print('local S mechanisms',Counter((k[0].split('/')[0],k[1]) for k in LOCAL_S))
