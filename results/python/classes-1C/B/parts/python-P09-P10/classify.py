"""Independent classifier B. Reads frozen tokens and raw records; executes no study code."""
from pathlib import Path
import json, re, gzip, collections, hashlib
BASE=Path('/Users/christopherhay/cp-roles/classifier-1C-B')
OUT=Path('/Users/christopherhay/cp-roles/classes-1C-B/python-P09-P10')
RULES={'P':'METRICS rules 1–3, 6–9 and 15: problem vocabulary, case, equation, query or encoding operation', 'C':'METRICS rules 1–2, 6, 10, 12 and 16: explicit scheduling, waiting, search or store reuse', 'R':'METRICS rules 3–5, 10 and 19: problem-specific holding, knownness, dependency or retraction machinery', 'S':'METRICS rules 12, 15 and 19: general reusable mechanism supplied by this program', 'H':'METRICS rule 13; harnesses/python/README.md §7: fixed harness operation or output adapter'}
manifest=[]
for row in (BASE/'results/python/tokens/TEXTS-1C-P09-P10.tsv').read_text().splitlines()[1:]:
 a,b=row.split('\t'); manifest.append((a,b.split()))

def frozen(path):
 rows=[]
 for row in (BASE/'results/python/tokens'/(path+'.tokens.tsv')).read_text().splitlines()[1:]:
  i,l,t=row.split('\t',2); rows.append((int(i),int(l),t))
 assert [r[0] for r in rows]==list(range(len(rows)))
 return rows

class Annotator:
 def __init__(self,path):
  self.path=path; self.src=(BASE/'programs/python'/path).read_text().splitlines(); self.rows=frozen(path)
  self.lines={i:('P',RULES['P'],None) for i in range(1,len(self.src)+2)}
 def mark(self,a,b,c,why=None,mechanism=None):
  for l in range(a,b+1): self.lines[l]=(c,why or RULES[c],mechanism)
 def one(self,ls,c,why=None):
  for l in ls: self.mark(l,l,c,why)
 def build(self):
  # A physical statement/header is a construct; nested constant reads and scheduling
  # arguments are split below using ONLY the supplied frozen token sequence.
  ann=[]; stack=[]; last_header=None
  for i,l,t in self.rows:
   c,rule,mech=self.lines[l]
   tx=self.src[l-1].strip() if l<=len(self.src) else 'end of module'
   name=f'line {l}: {tx.split("#")[0].strip()}'
   if t=='<INDENT>':
    assert last_header is not None,(self.path,i)
    stack.append(last_header); c,rule,mech,name=last_header; name='layout entering '+name
   elif t=='<DEDENT>':
    assert stack,(self.path,i)
    c,rule,mech,name=stack.pop(); name='layout closing '+name
   else:
    if t==':' and i+1<len(self.rows) and self.rows[i+1][2]=='<NEWLINE>':
     last_header=(c,rule,mech,name)
   ann.append([c,rule,mech,name])
  assert not stack
  # Fixed harness expressions, including when nested in P/R/C constructs.
  toks=[r[2] for r in self.rows]
  for k in range(len(toks)-2):
   if toks[k:k+3]==['s','.','constants'] or toks[k:k+3] in (['s','.','params'],['cp','.','params']):
    end=k+2
    if k+3<len(toks) and toks[k+3]=='[':
     depth=0
     for j in range(k+3,len(toks)):
      if toks[j]=='[':depth+=1
      if toks[j]==']':
       depth-=1
       if depth==0:end=j;break
    start=k-1 if k>0 and toks[k-1]==',' else k
    for j in range(start,end+1):ann[j]=['H',RULES['H']+'; rule 20 for preceding separator',None,f'line {self.rows[k][1]}: stage constants/parameters read']
  # In a mixed replay/readiness guard only the replay prefix is H.
  for k in range(len(toks)-2):
   if toks[k:k+3]==['s','.','replay'] and ann[k][0]!='H':
    start=k-2 if k>=2 and toks[k-2:k]==['if','not'] else k
    for j in range(start,k+3):ann[j]=['H',RULES['H'],None,f'line {self.rows[k][1]}: suppress output during stage replay']
  # Freeze/search/thread calls select execution; the enclosed problem goal is P.
  for l,method in self.goal_lines:
   ids=[i for i,ll,t in self.rows if ll==l and t not in ('<INDENT>','<DEDENT>','<NEWLINE>')]
   ts=[toks[i] for i in ids]
   try:
    if method=='queue':
     pos=ts.index('Goal') if 'Goal' in ts else ts.index('Relation')
     # q.wait(Goal(name, evaluator, problem-places)): wrapper is C, arguments P.
     beg=pos+2; end=len(ts)-2
    elif method=='search':
     pos=ts.index('search'); beg=pos+2
     # first argument of search is the query; find its top-level comma.
     dep=0; end=None
     for j in range(beg,len(ts)):
      if ts[j] in ('(', '[', '{'):dep+=1
      if ts[j] in (')',']','}'):dep-=1
      if ts[j]==',' and dep==0:end=j;break
     assert end is not None
    elif method=='pose':
     beg=ts.index('(')+1; end=len(ts)-1
    else: raise AssertionError(method)
    for j in range(beg,end):
     idx=ids[j]
     if ann[idx][0]!='H':ann[idx]=['P',RULES['P']+'; rule 10 nested goal',None,f'line {l}: problem goal inside scheduling call']
   except Exception as e:raise RuntimeError((self.path,l,ts)) from e
  # Extra stage/time tag in tell is R, relation and its parameters remain P.
  for l in self.tell_lines:
   ids=[i for i,ll,t in self.rows if ll==l and t not in ('<INDENT>','<DEDENT>','<NEWLINE>')]
   ts=[toks[i] for i in ids]; comma=ts.index(',')
   for j in range(comma,len(ids)-1):
    idx=ids[j]
    if ann[idx][0]!='H':ann[idx]=['P',RULES['P']+'; rules 5, 10 and 20 separate the added stage argument',None,f'line {l}: relation posed (inside time-tagged holding call)']
  spans=[]
  for i,a in enumerate(ann):
   c,r,m,n=a
   if spans and spans[-1]['to']==i-1 and (spans[-1]['class'],spans[-1]['rule'],spans[-1].get('mechanism'),spans[-1]['construct'])==(c,r,m,n):spans[-1]['to']=i
   else:
    z={'from':i,'to':i,'class':c,'construct':n,'rule':r}
    if m:z['mechanism']=m
    spans.append(z)
  return spans

A={}
for p,_ in manifest:
 a=Annotator(p); a.goal_lines=[]; a.tell_lines=[]; A[p]=a

def setm(p, specs):
 for item in specs:
  a,b,c,*rest=item; A[p].mark(a,b,c,*rest)

setm('core/P09a.py',[(53,60,'H'),(66,66,'H'),(68,68,'H'),(69,69,'C'),(71,71,'H'),(77,77,'H'),(79,86,'H')])
setm('core/P09b.py',[(40,40,'H'),(44,44,'H'),(46,46,'H'),(52,52,'H'),(54,61,'H')])
setm('core/P09c.py',[(29,29,'H'),(49,60,'H'),(65,66,'P'),(67,69,'H'),(71,72,'H')])
# else on line 69 belongs to the problem's success/failure dispatch, not its print.
A['core/P09c.py'].mark(69,69,'P')
setm('core/P09d.py',[(28,28,'H'),(44,55,'H'),(61,62,'H'),(65,66,'H')])
setm('core/P09e.py',[(28,28,'H'),(30,32,'R'),(34,36,'H'),(67,67,'H'),(69,95,'R'),(98,99,'H'),(100,102,'R'),(103,103,'H'),(104,104,'R'),(105,105,'H'),(106,106,'R'),(107,107,'H')])
setm('core/P10a.py',[(32,35,'H'),(37,37,'H'),(39,39,'H'),(41,42,'H')])
setm('core/P10b.py',[(36,36,'H'),(39,39,'R'),(41,42,'H'),(50,50,'H'),(53,57,'R'),(61,62,'H'),(63,63,'R'),(64,64,'H'),(66,66,'H'),(68,68,'H'),(70,70,'R'),(71,71,'R'),(72,72,'H')])
setm('core/P10c.py',[(32,32,'H'),(35,35,'H'),(43,46,'H'),(48,48,'H'),(50,50,'H'),(52,52,'H'),(54,55,'H')])
setm('core/P10d.py',[(36,39,'R'),(41,44,'H'),(59,59,'H'),(62,64,'R'),(69,88,'R'),(96,111,'R'),(107,109,'C'),(114,118,'H'),(121,122,'H'),(124,124,'R'),(125,125,'H'),(126,126,'R'),(127,127,'H'),(128,128,'R'),(129,130,'H')])
A['core/P10d.py'].tell_lines=[124,126]

setm('extended/P09a.py',[(38,39,'C'),(47,48,'C'),(52,69,'S',None,'term unification without occurs check'),(72,82,'S',None,'leftmost goal-list resolution'),(110,110,'H'),(121,136,'H'),(142,142,'H'),(143,143,'C'),(144,146,'H'),(152,152,'H'),(153,153,'C'),(154,156,'H'),(159,163,'H')])
for l in [145,155]:A['extended/P09a.py'].mark(l,l,'C'); A['extended/P09a.py'].goal_lines.append((l,'search'))
setm('extended/P09b.py',[(27,28,'C'),(38,38,'C'),(44,45,'H'),(47,47,'H'),(49,49,'C'),(50,50,'H'),(56,56,'H'),(58,65,'H')]); A['extended/P09b.py'].mark(45,45,'C')
setm('extended/P09c.py',[(31,31,'C'),(39,39,'C'),(42,42,'R'),(46,77,'H'),(89,89,'C'),(100,101,'R'),(110,110,'H'),(113,125,'S',None,'callable relation goal adapter'),(127,128,'H'),(131,132,'R'),(133,133,'H'),(134,138,'R'),(139,139,'H'),(142,143,'H'),(145,147,'C'),(148,148,'H'),(149,149,'R')])
A['extended/P09c.py'].goal_lines=[(89,'queue'),(145,'queue'),(146,'queue')]
setm('extended/P09d.py',[(33,33,'C'),(40,40,'C'),(43,43,'R'),(46,77,'H'),(86,86,'C'),(97,98,'R'),(107,107,'H'),(110,122,'S',None,'callable relation goal adapter'),(124,125,'H'),(128,129,'R'),(130,130,'H'),(131,135,'R'),(136,136,'H'),(139,140,'H'),(141,143,'C'),(144,144,'H'),(145,145,'R')])
A['extended/P09d.py'].goal_lines=[(86,'queue'),(141,'queue'),(142,'queue')]
setm('extended/P09e.py',[(24,24,'C'),(32,32,'C'),(35,35,'R'),(37,39,'H'),(70,70,'H'),(73,90,'S',None,'callable arithmetic relation adapter'),(92,93,'H'),(96,97,'H'),(98,100,'C'),(101,101,'H'),(102,102,'R'),(103,103,'H'),(105,107,'H')])
A['extended/P09e.py'].goal_lines=[(98,'queue'),(99,'queue')]
setm('extended/P10d.py',[(34,35,'C'),(44,45,'C'),(48,52,'R'),(54,59,'H'),(72,72,'H'),(75,77,'R'),(82,85,'R'),(86,86,'H'),(87,87,'R'),(90,93,'C'),(96,109,'R'),(110,110,'P'),(111,114,'C'),(117,140,'R'),(137,137,'C'),(143,147,'H'),(150,151,'H'),(153,153,'R'),(154,154,'H'),(155,155,'R'),(156,156,'H'),(157,157,'R'),(158,160,'H')]); A['extended/P10d.py'].tell_lines=[153,155]
# Constraint posting is C; the predicate that supplies a problem constraint is R
# as the extra representation, and the primitive evaluator itself is P.

for p,shift in [('stdlib-concurrency/P09c.py',0),('stdlib-concurrency/P09d.py',0)]:
 a=A[p]
 if p.endswith('P09c.py'):
  specs=[(32,32,'C'),(40,40,'S',None,'threaded relation dispatcher'),(49,50,'H'),(59,60,'H'),(66,69,'S',None,'threaded relation dispatcher'),(72,74,'H'),(77,79,'R'),(92,93,'R'),(95,95,'R'),(97,99,'R'),(105,107,'R'),(124,125,'R'),(134,134,'H'),(136,136,'R'),(139,185,'S',None,'threaded relation dispatcher'),(188,196,'H'),(199,200,'R'),(201,201,'H'),(202,204,'R'),(205,205,'H'),(208,209,'H'),(211,213,'C'),(214,214,'H'),(215,215,'R')]
  a.goal_lines=[(211,'pose'),(212,'pose')]
 else:
  specs=[(33,33,'C'),(40,40,'S',None,'threaded relation dispatcher'),(49,50,'H'),(59,60,'H'),(66,69,'S',None,'threaded relation dispatcher'),(71,73,'H'),(76,78,'R'),(91,92,'R'),(94,94,'R'),(96,98,'R'),(104,106,'R'),(120,121,'R'),(130,130,'H'),(132,132,'R'),(135,181,'S',None,'threaded relation dispatcher'),(184,192,'H'),(195,196,'R'),(197,197,'H'),(198,200,'R'),(201,201,'H'),(204,205,'H'),(206,208,'C'),(209,209,'H'),(210,210,'R')]
  a.goal_lines=[(206,'pose'),(207,'pose')]
 setm(p,specs)

setm('stdlib-concurrency/P09e.py',[(25,25,'C'),(33,33,'H'),(35,35,'C'),(37,38,'R'),(39,39,'C'),(41,43,'H'),(74,74,'H'),(76,81,'R'),(84,90,'C'),(93,95,'R'),(96,96,'C'),(97,98,'R'),(99,102,'C'),(103,110,'R'),(111,114,'C'),(117,127,'C'),(130,131,'H'),(132,134,'C'),(135,135,'H'),(136,136,'R'),(137,137,'H'),(138,138,'R'),(139,139,'H')]); A['stdlib-concurrency/P09e.py'].goal_lines=[(132,'pose'),(133,'pose')]
setm('stdlib-concurrency/P10b.py',[(29,29,'C'),(42,42,'H'),(44,44,'C'),(46,46,'R'),(47,47,'C'),(49,50,'H'),(58,58,'H'),(61,67,'C'),(70,74,'R'),(75,76,'C'),(77,77,'R'),(79,79,'R'),(80,90,'C'),(96,96,'C'),(98,98,'C'),(101,104,'C'),(107,108,'H'),(109,109,'C'),(110,110,'H'),(112,112,'H'),(114,114,'H'),(116,116,'C'),(117,117,'R'),(118,118,'H')]); A['stdlib-concurrency/P10b.py'].goal_lines=[(109,'pose')]
setm('stdlib-concurrency/P10d.py',[(33,33,'C'),(42,42,'C'),(43,46,'R'),(47,47,'C'),(49,52,'H'),(67,67,'H'),(70,72,'R'),(77,81,'R'),(84,90,'C'),(93,97,'R'),(98,98,'C'),(99,100,'R'),(101,104,'C'),(105,107,'R'),(108,108,'C'),(109,109,'R'),(110,124,'C'),(132,150,'R'),(134,134,'C'),(144,144,'C'),(146,147,'C'),(153,157,'H'),(160,161,'H'),(163,163,'R'),(164,164,'H'),(165,165,'R'),(166,166,'H'),(167,167,'R'),(168,168,'C'),(169,170,'H')]); A['stdlib-concurrency/P10d.py'].tell_lines=[163,165]

# A report wrapper that establishes which conclusion exists is R; its actual
# printing/enumeration is H (rule 13). Merely formatting show/elements remains H.
for p, header, test, call in [('core/P10d.py',114,115,130),('extended/P10d.py',143,144,160),('stdlib-concurrency/P10d.py',153,154,170)]:
 A[p].one([header,test,call],'R','METRICS rules 13 and 19: determine whether an empty-set conclusion is warranted; printing already computed values inside remains H by rule 10')

# Rule 19 explicitly splits arithmetic evaluators in every configuration.
for p, ranges in {
 'core/P09e.py':[(43,44),(47,47),(49,49),(51,51),(56,57),(60,60),(62,62),(64,64)],
 'extended/P09e.py':[(46,47),(50,50),(52,52),(54,54),(59,60),(63,63),(65,65),(67,67)],
 'stdlib-concurrency/P09e.py':[(50,51),(54,54),(56,56),(58,58),(63,64),(67,67),(69,69),(71,71)]}.items():
 for lo,hi in ranges:A[p].mark(lo,hi,'R','METRICS rule 19, evaluator split: knownness test or wait verdict; rule 10 preserves the P arithmetic inside')
# Heads/tests of the problem's cases, including failure after a failed head
# equality, remain P (rules 2–3), even in a supporting representation.

result={'tokens':{p:A[p].build() for p,_ in manifest},'outcomes':[],'mode_differences':[],'expressibility':[],'late_definition':[],'s_mechanisms':[]}
# Final JSON is written after the outcome checks below.
print('Token draft:',len(result['tokens']),'texts,',sum(len(a.rows) for a in A.values()),'tokens')
print('Totals:',dict(collections.Counter({c:sum(z['to']-z['from']+1 for spans in result['tokens'].values() for z in spans if z['class']==c) for c in 'PCRSH'})))

# Read every allowed behaviour/cost/storage record for these two problems.
records=[]
for cfg in ('core','extended','stdlib-concurrency'):
 for prob in ('P09','P10'):
  for folder in ('raw','raw-rerun-m2'):
   for p in sorted((BASE/'results/python'/cfg/prob/folder).glob('*.json*')):
    with gzip.open(p,'rt') if p.suffix=='.gz' else p.open() as f:d=json.load(f)
    records.append((str(p.relative_to(BASE)),d))
assert len(records)==90
bykey=collections.defaultdict(list)
for path,d in records:
 r=d['run']; key=(r['configuration'],r['instance'],r['program']['path'])
 bykey[key].append((path,d))

def classify_record(path,d):
 r=d['run']; cfg=r['configuration']; inst=r['instance']; prog=Path(r['program']['path']).name; outs=[]
 for st in d['stages']:
  a=st['attempts'][-1]; k=st['stage']; spawned=inst.startswith('P09a') or inst=='P09b'
  comps=[c for c in a['computations'] if c['queries']]
  assert len(comps)==(2 if spawned else 1)
  for c in comps:
   for reading in (['P09d1','P09d2'] if inst=='P09d' else [None]):
    cid=c['id']; answers=[z['verbatim'] for q in c['queries'] for z in q['answers']]
    ev=c['execution_state']; bindings=a['observe']['bindings'] or {}
    raw=a['observe']['raw']; alt=c['alternatives']; susp=c['suspended']
    reached=not any(re.search(r'(never posed|never reached|not reached|replay.*did not reach)',x,re.I) for x in a.get('notes',[])+st.get('notes',[]))
    o={'configuration':cfg,'instance':inst,'program':prog,'record':path,'stage':k,'computation':cid,'reading':reading,'reached':reached,'semantic':'complete','representation':'explicit','simplification':None,'identical_to_posed':None,'residual_size':None,'execution_state':ev['states'],'residual_equivalence':None,'observations':'','rule':'SPECIFICATION Outcomes 1–3; '+('problems/09-concurrent-goals.md' if inst.startswith('P09') else 'problems/10-state-replacement.md'),'harness_fault':bool(d['harness_faults']) or '.INVALID.' in path}
    notes=[]; reason=None
    if inst.startswith('P09a'):
     if cid=='A':
      o.update(semantic='none reported',representation=None)
      notes.append('loop(x) produced no answer; this is not a report of the empty solution set. '+('x is supplied to loop as the None placeholder, with no binding in known. RecursionError ended the recursive generator; no continuation/alternative survives.' if cfg!='extended' else 'Depth-first resolution is still descending loop(x) at the instruction budget; 12,821 pending search-stack entries are retained for backtracking, not distinct valid answers. x remains an unbound Var.'))
     else:
      assert answers==['b = ⟨3,2,1⟩']; reason='The only answer is exactly rev(⟨1,2,3⟩, b), b=⟨3,2,1⟩.'
      notes.append('B reports the unique reverse irrespective of spawn order; A does not prevent it. '+('At search exhaustion the trail restores the registered Var b to unbound; the earlier printed answer remains the valid explicit report.' if cfg=='extended' else 'The registered binding b=(3,2,1) is retained.'))
     if cfg=='stdlib-concurrency':notes.append('The configuration spawns A and B side by side in one interpreter; the record does not timestamp their relative progress finely enough to establish whether B printed before A errored.')
     else:notes.append('The configuration runs the spawned computations sequentially: in AB, B starts after A errors/reaches budget; in BA, B finishes before A starts. Both share one interpreter/database, with separate unknowns and budgets.')
     notes.append('Main only receives constants/registers spawn functions and is finished; it has no problem query.')
    elif inst=='P09b':
     if cid=='A':
      assert not answers and 'no solution: x = 1 and x = 2' in a['print']; reason='x=1 and x=2 has no solution; the program prints the contradiction and finishes, rather than reporting x=1 as a solution.'
      notes.append('The failed conjunction is explicitly printed as no solution; its tentative x=1 is absent/undone in observe().')
     else:
      assert answers==['y = 3']; reason='The independent equation y=3 has exactly the printed solution.'
      notes.append('B retains y=3; A’s failure does not affect it.')
     notes.append('Spawn is '+('side by side' if cfg=='stdlib-concurrency' else 'sequential A then B')+' in one interpreter. Main is finished and has no query.')
    elif inst=='P09c':
     assert answers==['s = ⟨1,2,3,4,5⟩, total = 6']
     reason='gen(1,s) terminates at n=6, hence s=⟨1,2,3,4,5⟩; its first three sum to 1+2+3=6. The printed pair is the unique valid outcome.'
     if cfg=='core':notes.append('Producer completes its recursive tuple before sum3 is called: consumer does not act early.')
     elif cfg=='extended':notes.append('FIFO q.wait/q.run interleaves cells and consumer retries; sum3 binds total after the third cell, before the finite producer finishes. No trace is recorded; the queue order and definitions establish this ordering.')
     else:notes.append('Registered bindings encode one cell at a time, with rest names and total=6. Threads allow early consumption; insertion order in the recorded bindings puts total before later tail bindings, evidencing consumption before producer completion.')
    elif inst=='P09d':
     if cfg=='core':
      assert not answers and not bindings
      o.update(semantic='none reported',representation=None)
      notes.append('Recursive finite tuple construction raises RecursionError before genu returns; sum3 is never called, no stream prefix or total binding is held. Both readings therefore have none reported, with error.')
     else:
      assert bindings.get('total')=='6' and not answers
      if reading=='P09d1':
       o.update(semantic='none reported',representation=None)
       notes.append('Finite least-relation genu has no instances. The unfinished producer’s total=6 binding is only an observation under P09d1’s explicit exception; no finished solution or empty-set conclusion is reported.')
      else:
       o.update(semantic='complete',representation='explicit')
       reason='Under the greatest-relation stream reading, genu from 1 denotes ⟨1,2,3,…⟩ and its first three elements force total=6. observe() reads total=6, so it is a complete explicit report for total even though cp.answer was never reached. The finite prefix alone is not asserted to be a solved representation of the whole stream.'
       notes.append('total=6 is readable through observe(), and thus reported for the stream query (SPECIFICATION, reported bindings). The producer remains budget-stopped; no finished conjunction is printed.')
      if cfg=='extended':
       stext=bindings['s']; n=len(re.findall(r'\d+',stext.split('⟩')[0])); notes.append(f'The record holds a prefix of {n} cells followed by an unbound rest Var. No held queue entries wait on bindings at the boundary; producer work is active/ready, not suspended. q.ready is not registered, so its exact runnable-work count is unavailable. The FIFO queue lets sum3 consume the first three before production ends.')
      else:
       n=len([x for x in bindings if x=='s' or x.startswith('rest')]); notes.append(f'The binding store contains {n} producer cells, named by s and successive rest unknowns, plus total=6. The last rest name has no binding. One relation thread at a time produces the next cell under the condition lock; the program’s busy counter is not registered, so its exact ready/running count is unavailable. No waiting relation entries remain at the boundary. Main waits in settle while producer instructions share its budget.')
      notes.append('The end-of-run SIGKILL after 5 seconds is cleanup of the budget-paused process, not a stage timeout.')
    elif inst=='P09e':
     assert susp['at_boundary']==2 and not answers
     o.update(representation='residual',simplification='reducible',identical_to_posed=True,residual_size={'input':{'primitive_relations':2,'unknown_occurrences':4},'residual':{'primitive_relations':2,'unknown_occurrences':4},'smaller_equivalent':{'primitive_relations':1,'unknown_occurrences':2}})
     reason='Held + (y,1,x) means y+1=x over integers; held − (x,1,y) means x−1=y. Subtracting/rearranging either gives x−y=1. Thus the two conditions are equivalent over all integer pairs to the valid outcomes {(y+1,y): y∈Z}. One duplicate relation can be removed, so this complete residual is reducible, not reduced. There is no imposed finite domain.'
     notes.append(('x and y are unbound S.suspend.Var objects, referenced by the Relation goals. ' if cfg=='extended' else 'x and y are represented by their string names in the held places, absent from the known dictionary. ')+ 'Neither x nor y has a value; both relations remain held and are genuinely evaluated by the program’s holding/waking code, rather than printed back. Two waiting items distinguish this mutual wait from completion; no deadlock diagnosis, enumeration or simplified relation is reported.')
    elif inst=='P10a':
     expected=[10,15,7][k-1]; assert answers==[f'b = {expected}']
     reason=f'Current b is {expected}; stage 2 evaluates old b+5 before replacing it. Exactly the valid current quantity is reported.'
     notes.append('b is a named quantity, not a logic unknown. Replacement is native dictionary assignment, with no time/version indexing. Only current b is retained; overwritten values are not retrievable through the registered state.')
     if k>1:notes.append(f'The prior b={[10,15][k-2]} conclusion is superseded by b={expected}; the registered dictionary is overwritten and the new value is printed. No explicit retraction message is emitted.')
    elif inst=='P10b':
     if k==1:
      assert not answers and not bindings
      o.update(representation='residual',simplification='reduced',identical_to_posed=True,residual_size={'input':{'primitive_relations':1,'unknown_occurrences':None,'unresolved_quantity_occurrences':2},'residual':{'primitive_relations':1,'unknown_occurrences':None,'unresolved_quantity_occurrences':2}})
      reason='The held tuple (2,b,d) denotes the standing integer relation d=2*b, with no current b or d. It is exactly the stage-1 information and already one undecided primitive relation; neither b nor d is a bound/free alias or term allowed by solved form, so it is a reduced residual.'
     else:
      expected=[(10,20),(15,30),(7,14)][k-2]; assert answers==[f'b = {expected[0]}, d = {expected[1]}']
      reason=f'Current b={expected[0]} and d=2*b={expected[1]}, exactly the valid stage-{k} pair. The more explicit valid binding form takes precedence over the standing residual (SPECIFICATION Outcomes 2).'
     notes.append('One standing relation is retained and waits for the next change even after its present values are explicit. '+('The relation is kept in standing and rechecked after each stage.' if cfg!='stdlib-concurrency' else 'A persistent relation thread is woken on each replacement and waits again on changed.'))
     notes.append('One dependent quantity d is recomputed for each replacement; cost mode’s registered times counter is the evidence, not a guessed step count. Overwritten quantity values are not versioned or retained as accessible old values.')
     if k>=3:notes.append('Both prior b and prior d are superseded, shown by overwritten bindings and the new printed pair; no explicit withdrawal message is emitted.')
    elif inst=='P10c':
     expected=[{'b':10},{'b':10,'d':20},{'b':15,'d':20},{'b':7,'d':20}][k-1]
     assert bindings=={n:str(v) for n,v in expected.items()}
     reason='The retained current quantities are '+str(expected)+'. d is evaluated once at stage 2 from the then-current b=10; later b replacements do not recompute d. This is exactly the snapshot outcomes.'
     notes.append('Native assignment replaces quantities, without indexing/history. '+('d has not yet been assigned a quantity value.' if k==1 else 'd=20 is a retained snapshot, not a maintained dependency.'))
     if k>=3:notes.append('The previous b conclusion is superseded by an overwritten binding and fresh printed current pair; d=20 remains valid. No explicit withdrawal message is emitted.')
    elif inst=='P10d':
     vals=[[1,2,3],[2,3],[1,2,3]][k-1]; assert answers==[f'x = {v}' for v in vals]
     reason='The closed-world facts give {1,2,3}; applying x>1 gives {2,3}; withdrawing that comparison restores {1,2,3}. The reported answers enumerate exactly the corresponding set. The finite domain is justified by pick itself, not artificially imposed (AMENDMENTS 3.4).'
     notes.append(f'{len(vals)} values of x are held all at once as problem-defined alternatives. All have been printed; these are not unrequested pending search answers. The saved information is a second form; explicit answers are used for representation classification.')
     if k==2:notes.append('x=1 is removed from the live values/domain; the new enumeration omits it. No separate withdrawal event is printed.')
     if k==3:notes.append('x=1 returns. '+('The store trail is undone to the mark preceding stage 2, restoring the domain and removing its constraint; stage 1 is not reposed.' if cfg=='extended' else 'The saved unwithdrawn information is replayed by the program into a cleared candidate list'+(' using new threads' if cfg=='stdlib-concurrency' else '')+'; the harness does not repose stages.'))
    else:raise AssertionError(inst)
    if not reached:
     o.update(semantic='none reported',representation=None,simplification=None,identical_to_posed=None,residual_size=None,execution_state=['not reached']); notes.append('AMENDMENTS 3.2: replay stopped before this stage; see attempt notes.')
    if o['representation'] in ('residual','solved form'):o['residual_equivalence']=reason
    o['observations']=' '.join(notes)+f' Registered pending alternatives: {alt["at_boundary"]}; registered suspended/waiting entries: {susp["at_boundary"]}. No manual action is recorded. Unmeasured peaks/counts are unavailable, not zero.'
    if reason and o['residual_equivalence'] is None:o['equivalence_reason']=reason
    if spawned:
     subset={n:v for n,v in bindings.items() if n.startswith(cid+':')}
    else:subset=bindings
    # Full bindings (including the stream cells) are manageable; the enormous
    # pending stack is cited by record and counted, not copied as 12,821 addresses.
    evidence={'answers_verbatim':answers,'bindings_verbatim':subset,'print_verbatim':a['print'],'execution_basis':ev['basis'],'error_verbatim':ev['error_verbatim'],'alternatives':alt,'suspended':susp,'posing':a['posed'],'manual_actions':a['manual_actions'],'attempt_notes':a.get('notes',[]),'steps':c['steps'],'problem_operations':c['problem_operations'],'store':a['store']}
    if len(raw)<3000:evidence['observe_verbatim']=raw
    else:evidence['observe_reference']=path+'#/stages/'+str(k-1)+'/attempts/'+str(len(st['attempts'])-1)+'/observe/raw'
    o['evidence']=evidence
    outs.append(o)
 return outs

behaviours={}
for key,rs in bykey.items():
 b=[(p,d) for p,d in rs if d['run']['mode']=='behaviour']; assert len(b)==1
 path,d=b[0]; entries=classify_record(path,d); result['outcomes']+=entries; behaviours[key]=(path,entries)
 for p,m in rs:
  if m['run']['mode']=='behaviour':continue
  mes=classify_record(p,m)
  assert len(mes)==len(entries)
  for bentry,mentry in zip(entries,mes):
   fields=['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence','harness_fault']
   diffs=[f for f in fields if bentry[f]!=mentry[f]]
   if diffs:
    result['mode_differences'].append({'configuration':key[0],'instance':key[1],'program':mentry['program'],'mode':m['run']['mode'],'record':p,'stage':mentry['stage'],'computation':mentry['computation'],'reading':mentry['reading'],'behaviour':{f:bentry[f] for f in fields},'this_mode':{f:mentry[f] for f in fields},'note':'Classification differences: '+', '.join(diffs)})
   assert bentry['evidence']['answers_verbatim']==mentry['evidence']['answers_verbatim'],(p,'answer mismatch')

# Expressibility is distinct from successful execution. Optional S does not make
# a demonstrably available mode-faithful core transcription inexpressible.
for cfg in ('core','extended','stdlib-concurrency'):
 def expr(sub,direction,kind,reason):result['expressibility'].append({'configuration':cfg,'subproblem':sub,'direction':direction,'expressibility':kind,'reason':reason})
 expr('P09a','loop: unknown x -> enumeration','expressible','The sole recursive loop case is transcribed with no extra relation case/argument or algorithm change. Divergence, budget and recursion error are execution outcomes. In extended, optional search/resolution is S; the core generator demonstrates a transcription requiring no such S.')
 expr('P09a','rev: known sequence -> b','expressible','One branch per rev and conc case suffices in the only direction queried (METRICS 3); cons/tuple encoding preserves finite sequences. Extended uses optional search and unification; these do not make this forward direction require supporting code.')
 expr('P09b',None,'expressible','Assignments and equality tests transcribe the two ground equations and independent y binding. Extended uses optional S Var bindings/trail; the core text demonstrates that the queried equations need no added algorithm.')
 expr('P09c','gen: n -> s; sum3: s -> total','expressible','Both finite forward definitions are transcribed case for case. Core produces s before consuming it. Threads/queue and goal adapters change scheduling and representation; the general mechanisms are counted separately as S/C. Early consumption is not required for the finite valid outcome.')
 expr('P09d1','genu: n -> finite s; sum3: s -> total','expressible','The recursive genu case has no finite derivation and is directly transcribed. A missing successful answer before recursion error/budget is not itself inexpressibility; no spurious base case is introduced.')
 if cfg=='core':expr('P09d2','genu: n -> stream; sum3: stream -> total','not expressible','The supplied tuple transcription constructs only finite values and cannot expose an infinite sequence or its prefix before the recursive call returns. No stream reformulation is supplied in this configuration’s program; a different generator/dataflow representation would be needed. This is a program-of-record judgment, not a proof about all Python algorithms.')
 else:expr('P09d2','genu: n -> stream; sum3: stream -> total','not expressible','The supplied program reaches the stream total only through a general supporting dataflow mechanism: '+('the phase-4 suspension queue plus the newly supplied callable goal adapter' if cfg=='extended' else 'the newly supplied threaded relation dispatcher')+'. By the expressibility criterion’s supporting-code clause this is a supported result, not a native transcription of the stream reading. Its bindings are nevertheless complete for total. No S-free stream reformulation is provided.')
 expr('P09e',None,'expressible with reformulation','The core program holds these two arithmetic relations and tests knownness, R under rule 19, then reports an equivalent unreduced residual over all integers. This problem-specific holding reformulation is available in all three configurations. '+('The recorded extended program additionally uses S variables/queue and a generic Relation adapter.' if cfg=='extended' else 'The recorded stdlib program adds explicit thread/condition control.' if cfg=='stdlib-concurrency' else 'It is not general propagation or algebraic elimination.'))
 expr('P10a',None,'expressible','Native assignment directly expresses absolute and relative replacement; old b is evaluated on the right before replacement. No time argument, added case or changed algorithm.')
 expr('P10b','standing d from current b','expressible with reformulation','R stores a persistent relation, tests whether its source is available and reevaluates it after replacements. The times arithmetic itself is P. No general S propagator is necessary: the same problem-specific standing loop is present in core/extended; stdlib adds condition/thread C.')
 expr('P10c','snapshot d from current b','expressible','Native assignment evaluates 2*b once at the snapshot stage and retains it while b changes. Mode-faithful times and replacements are P, not a standing relation.')
 expr('P10d',None,'expressible with reformulation','The supplied core reformulation stores time-tagged information and candidate values, narrows them and reconstructs from unwithdrawn information. R covers that representation/recovery; pick/in and > evaluators are P. It is available across configurations. Extended instead uses the phase-4 store and undo trail (S counted separately), and stdlib adds threads. The only finite domain is exactly the problem’s stated pick facts.')

# Supporting mechanisms: external module sizes are the frozen phase-4 figures,
# counted once per configuration, with every using program listed here.
listed={
 'extended/P09a.py':[('backtracking search',176),('suspension queue',537)],
 'extended/P09b.py':[('backtracking search',176),('suspension queue',537)],
 'extended/P09c.py':[('suspension queue',537)],
 'extended/P09d.py':[('suspension queue',537)],
 'extended/P09e.py':[('suspension queue',537)],
 'extended/P10d.py':[('constraint propagator',1260),('backtracking search',176)]}
for first,also in manifest:
 spans=result['tokens'][first]
 for path in [first]+also:
  cfg,prog=path.split('/')
  custom=collections.defaultdict(list)
  for s in spans:
   if s['class']=='S':custom[s['mechanism']].append({'from':s['from'],'to':s['to']})
  for name,n in listed.get(path,[]):result['s_mechanisms'].append({'configuration':cfg,'program':prog,'mechanism':name,'listed_at_phase_4':True,'tokens':n,'token_ranges':None,'source':'harnesses/python/S-mechanisms.md','counting':'Full mechanism size, counted once per configuration; repeated entries identify programs using it, not additional size.'})
  for name,ranges in custom.items():result['s_mechanisms'].append({'configuration':cfg,'program':prog,'mechanism':name,'listed_at_phase_4':False,'tokens':sum(s['to']-s['from']+1 for s in ranges),'token_ranges':ranges,'tokens_path':first,'counting':'S implementation spans in the supplied program; deduplicate the same mechanism across using programs within a configuration.'})
  if not custom and path not in listed:result['s_mechanisms'].append({'configuration':cfg,'program':prog,'mechanism':None,'listed_at_phase_4':None,'tokens':0,'token_ranges':[],'note':'No S mechanism used. Threading calls/control alone are external C, not automatically S.'})

# Coverage checks: all tokens, exactly once, and identical texts across paths.
for first,also in manifest:
 spans=result['tokens'][first]; n=len(frozen(first)); cover=[]
 for z in spans:
  assert z['class'] in 'PCRSH' and z['from']<=z['to']; cover.extend(range(z['from'],z['to']+1))
 assert cover==list(range(n)),first
 for other in also:
  assert (BASE/'programs/python'/first).read_bytes()==(BASE/'programs/python'/other).read_bytes(),(first,other)
  assert [x[2] for x in frozen(first)]==[x[2] for x in frozen(other)]
assert len(result['outcomes'])==72
assert not result['mode_differences']
(OUT/'python.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
# Parse our own final output, independent of the in-memory serializable object.
final=json.loads((OUT/'python.json').read_text())
print('Final:',len(final['tokens']),'texts;',len(records),'records;',len(final['outcomes']),'computation/reading stage entries;',len(final['mode_differences']),'mode classification differences')
print('Semantic:',dict(collections.Counter(o['semantic'] for o in final['outcomes'])))
print('Representation:',dict(collections.Counter(str(o['representation']) for o in final['outcomes'])))
print('Execution:',dict(collections.Counter(s for o in final['outcomes'] for s in o['execution_state'])))
print('Custom S:',[(m['configuration'],m['program'],m['mechanism'],m['tokens']) for m in final['s_mechanisms'] if m['mechanism'] and not m['listed_at_phase_4']])
