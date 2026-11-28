"""Independent classifier B; reads only the specified public inputs; executes no ALGOL."""
from pathlib import Path
import csv, json, collections, difflib, re
ROOT=Path('.')
OUT=Path('results/algol-60/classes-1B/B/parts/algol-60-P04-P06')
TR=ROOT/'results/algol-60/tokens'
RULES={
 'p':('P','problem transcription / encoded value operation','METRICS 1, 2, 3, 6, 10, 15'),
 'h':('H','fixed harness interface or output adapter','METRICS 13; harnesses/algol-60/README 2.7'),
 'r':('R','problem-specific representation and holding machinery','METRICS 5, 10, 19'),
 'c':('C','restore temporary binding or release reusable cell store','METRICS 1, 2, 16'),
 'arg':('R','extra knownness or success-continuation argument','METRICS 3, 5, 10'),
 'eval':('P','fully known relation test or computation of a place','METRICS 19 (evaluator), 2, 10, 15'),
 'enc':('P','sequence encoding, construction, decomposition or equality','systems/algol-60/README Values; METRICS 15'),
 'facts':('P','closed-world facts or iteration over the stated facts','METRICS 3, 6, 15'),
 'decl':('R','problem-specific relation evaluator / continuation declaration','METRICS 3, 5, 19'),
}
def rows(name):
 rs=list(csv.DictReader((TR/(name+'.tokens.tsv')).read_text().splitlines(),delimiter='\t'))
 assert [int(x['index']) for x in rs]==list(range(len(rs)))
 return rs
class Annot:
 def __init__(self,name):
  self.name=name;self.rs=rows(name);self.ts=[x['token'].replace('\u0332','') for x in self.rs]
  self.a=[('p',f'problem construct, source line {x["line"]}') for x in self.rs]
 def set(self,l,h,code,label=None):
  assert 0<=l<=h<len(self.a),(self.name,l,h)
  for i in range(l,h+1):self.a[i]=(code,label or RULES[code][1])
 def lines(self,l,h,code,label=None):
  for i,r in enumerate(self.rs):
   if l<=int(r['line'])<=h:self.a[i]=(code,label or RULES[code][1])
 def ranges(self,ranges,code,label=None):
  for l,h in ranges:self.set(l,h,code,label)

def p04ab(name):
 a=Annot(name)
 a.ranges([(1,12),(17,19),(115,211),(223,226),(247,280)],'h')
 a.ranges([(20,22),(33,35),(75,77),(86,88),(97,98),(104,107),(219,222)],'r')
 # Each extra argument and its own leading separator; procedure formals match calls.
 a.ranges([(26,27),(29,30),(40,41),(51,52),(54,55),(63,64),(68,69),(83,85),(230,231),(234,234),(239,240),(244,244)],'arg')
 # P04b reverses its two query calls; replace the query labels below.
 if 'P04b' in name:
  a.set(227,246,'p','query disjunction, branches in presentation order')
  a.ranges([(230,231),(236,237),(241,242),(245,245)],'arg')
 a.set(94,94,'arg','invoke success continuation after equality test')
 a.set(108,108,'arg','invoke success continuation after binding')
 a.set(109,112,'c','undo temporary knownness after success continuation')
 return a

def p04seq(name,known,right):
 a=Annot(name)
 a.lines(8,12,'h')
 # Stable procedure bodies are located in the frozen token stream, not re-tokenized source.
 def find(seq,start=0):
  for i in range(start,len(a.ts)-len(seq)+1):
   if a.ts[i:i+len(seq)]==seq:return i
  raise ValueError((name,seq))
 def region(startseq,endseq,code,label):
  s=find(startseq);e=find(endseq,s)+len(endseq)-1;a.set(s,e,code,label);return s,e
 # Declaration of len is problem information; everything else on the first declaration is harness-only.
 if known:
  a.set(13,14,'p','query sequence length declaration')
 # Sequence encoding primitives: whole definitions are P, rule 15.
 for seq,end in [(['integer','procedure','cons'],['end','cons']),(['Boolean','procedure','same'],['false',';'])]:
  region(seq,end,'enc','sequence encoding operation: '+seq[-1])
 if known:region(['integer','procedure','readseq'],['end','readseq'],'enc','read and encode the posed finite sequence')
 # Locate the central definitions, then split nested evaluators and extra arguments.
 s,e=region(['procedure','conseq'],['end','conseq'],'r','problem-specific equation evaluator and its knownness bookkeeping')
 # Declaration's equation values are P; knownness and continuation formals are R.
 # Full header structure is reformulation, because conseq is an introduced helper.
 for seq in [ ['if','s','≠','0','then'],['if','hd','[','s',']','=','acode','then'],
             ['if','same','(','tl','[','s',']',',','m',')','then'],
             ['m',':=','tl','[','s',']'],['s',':=','cons','(','acode',',','m',')'] ]:
  x=find(seq,s);a.set(x,x+len(seq)-1,'eval')
 for var in ['mk','sk']:
  seq=[var,':=','false']
  x=s
  while True:
   try:x=find(seq,x)
   except ValueError:break
   if x>e:break
   a.set(x,x+2,'c','undo a temporary binding after the continuation');x+=3
 x=find(['top',':=','top','-','1'],s);a.set(x,x+4,'c','release the temporary encoded sequence cell')
 s,e=region(['procedure','alist'],['end','alist'],'p','alist definition by its stated cases')
 # All knownness tests and flags in alist implement the representation, not a case head.
 for i in range(s,e+1):
  if a.ts[i] in ['sk','mk','found','second','body','head']:
   a.set(i,i,'arg')
 # All added continuation declarations, bodies and callbacks are R at their shell.
 for seq in [['procedure','second'],['procedure','body'],['procedure','head']]:
  try:x=find(seq,s)
  except ValueError:continue
  if x<=e:a.set(x,x+len(seq),'decl')
 for i in range(s,e+1):
  if a.ts[i:i+3] in [['if','sk','then'],['if','mk','then']]:a.set(i,i+2,'r','knownness dispatch')
  if a.ts[i:i+2] in [['sk',':='],['mk',':=']]:
   a.set(i,i+2,'r','record knownness of a problem-specific unknown')
   if a.ts[i+2]=='false' and i>s and a.ts[i-2]=='found':a.set(i,i+2,'c','undo temporary knownness after a solution')
 # Pairs of flags in parameter declarations and extra call arguments include their leading comma.
 for i in range(s,e+1):
  if a.ts[i] in ['sk','mk','found','second','body','head'] and i>s and a.ts[i-1]==',':a.set(i-1,i,'arg')
  if a.ts[i:i+3] in [['Boolean','sk',';'],['Boolean','mk',';']]:a.set(i,i+1,'r','knownness flag declaration')
 # Switching order of head and body for known/unknown s is introduced operational dispatch.
 if right:
  seq=['if','sk','then','conseq'];x=find(seq,s);a.set(x,x+2,'r','choose head-first or body-first evaluation from knownness')
  # The else connective belongs to that dispatch.
  x=find(['else','begin','al2'],x);a.set(x,x,'r','knownness dispatch alternative')
 # Counters, outputs and helper printers.
 for seq,end in [(['procedure','printseq'],['end','printseq']),(['procedure','answer'],['end','answer'])]:
  try:region(seq,end,'h','output adapter: '+seq[-1])
  except ValueError:
   if seq[-1]=='answer':
    x=find(seq);z=find(['outstring'],x);a.set(x,z+6,'h','output adapter: true for the ground query')
 # Final observe block.
 last=find(['outstring','(','1',',','[observe]']);a.set(last,len(a.ts)-3,'h','inline observation output adapter')
 # Declarations in inner block: values and encoding P, flags R, counters H.
 for i in range(len(a.ts)):
  if a.ts[i] in ['al1','al2']:
   # Counter declaration names and all assignments are harness instrumentation.
   if i>0 and a.ts[i-1]==',':a.set(i-1,i,'h','operation counter declaration')
   if a.ts[i+1:i+2]==[':=']:
    z=i+1
    while z<len(a.ts) and a.ts[z] not in [';','end']:z+=1
    a.set(i,z-1,'h','operation counter increment or initialization')
  if a.ts[i:i+3]==['Boolean','sk',';']:a.set(i,i+1,'r','query unknown knownness flag')
 # Chained initialization combines encoding allocation cursor and harness counters.
 x=find(['top',':=','al1',':=','al2',':=','0']);a.set(x,x+1,'enc','initialize sequence allocation cursor');a.set(x+2,x+6,'h','initialize operation counters')
 # Final query call and knownness initialization.
 q=find(['alist','(','sk',',','sv',',','answer',')'],e)
 a.set(q,q+7,'p','query alist on the posed sequence or unknown')
 a.set(q+2,q+3,'arg');a.set(q+5,q+6,'arg')
 for i in range(e+1,len(a.ts)):
  if a.ts[i:i+2]==['sk',':=']:a.set(i,i+2,'r','initialize query knownness')
 return a

def p05(name,b=False):
 a=Annot(name);a.set(0,len(a.ts)-1,'r','problem-specific retained alternatives and relation holding')
 a.set(1,12,'h','declarations of harness-only words')
 # Values of pick, relation constants and flags belong to separate constructs.
 if b:
  a.ranges([(15,18)],'p','fact count and comparison constant declarations')
  a.ranges([(39,44)],'h','operation counter array declaration')
  a.set(105,319,'h','output adapters and fixed input interface')
  a.set(330,351,'h','fixed message loop and message reads')
  a.set(352,356,'h','stage dispatch header');a.set(357,357,'h','stage dispatch block')
  a.set(358,364,'p','read comparison constant as stage information')
  a.set(369,375,'h','stage dispatch header and block')
  a.set(376,400,'facts','read and enumerate the stated pick facts')
  a.set(401,407,'r','mark a candidate as live')
  a.set(408,413,'h','count the application of a pick fact')
  a.set(421,422,'h','close stage dispatch')
  a.set(425,len(a.ts)-1,'h','inline output adapter over already computed values and held conditions')
  a.set(82,98,'eval','test the fully known comparison and reject a failing value')
 else:
  a.set(15,20,'p','fact count and relation constant declarations')
  a.set(43,48,'h','operation counter array declaration')
  a.set(132,396,'h','output adapters and fixed input interface')
  a.set(409,436,'h','fixed message loop, message reads and stage dispatch')
  a.set(437,461,'facts','read and enumerate the stated pick facts')
  a.set(462,468,'r','mark a candidate as live')
  a.set(469,474,'h','count the application of a pick fact')
  a.set(482,489,'h','stage dispatch connective and header')
  a.set(490,496,'p','read stage 2 relation constant')
  a.set(501,508,'h','stage dispatch connective and header')
  a.set(509,515,'p','read stage 3 relation constant')
  a.set(518,519,'h','close stage dispatch')
  a.set(522,len(a.ts)-1,'h','inline output adapter over already computed values and held conditions')
  a.set(86,103,'eval','test the fully known stage 2 relation and reject a failing value')
  a.set(110,125,'eval','test the fully known stage 3 relation and reject a failing value')
 return a

def p06ab(name,b=False):
 a=Annot(name);a.set(0,len(a.ts)-1,'r','problem-specific negation/equality evaluator and relation holding')
 a.set(1,12,'h','declarations of harness-only words')
 a.set(13,18,'p','relation constants and represented value declarations')
 a.set(19,20,'h','observation-only held count declaration')
 a.set(23,27,'h','relation examination counter declarations')
 a.set(36,37,'p','inconsistency verdict declaration')
 a.ranges([(43,48),(82,87)] if not b else [(43,48),(90,95)],'h','count relation examinations')
 if not b:
  a.set(53,60,'eval','fully known negated equality test')
  a.set(66,68,'eval','record contradiction from the negation')
  a.set(92,102,'eval','test fully known equality and record contradiction')
  a.set(106,108,'eval','bind x from the given equality')
 else:
  a.set(53,63,'eval','test fully known equality and record contradiction')
  a.set(67,69,'eval','bind x from the given equality')
  a.set(100,107,'eval','fully known negated equality test')
  a.set(113,115,'eval','record contradiction from the negation')
 a.set(158,255,'h','held-relation output adapter and fixed instance input')
 a.set(266,293,'h','counter initialization, fixed message loop and message reads')
 a.set(294,299,'h','stage 1 dispatch header and block')
 a.set(300,306,'p','read stage 1 relation constant')
 a.set(311,317,'h','stage 2 dispatch connective, header and block')
 a.set(318,324,'p','read stage 2 relation constant')
 a.set(328,329,'h','close stage dispatch')
 a.set(332,len(a.ts)-1,'h','inline output adapter for the computed solution set and diagnostic state')
 # The no-inconsistency branch only prints the already computed representation; no solver inside.
 return a

def p06d(name):
 a=Annot(name)
 a.set(1,12,'h','declarations of harness-only words');a.set(18,68,'h','fixed instance and message input')
 a.set(92,102,'h','problem-operation counter declarations')
 a.set(120,249,'enc','sequence construction and reading in the prescribed encoding')
 a.ranges([(287,292),(299,304),(344,349),(367,372),(402,407)],'h','problem-operation counter increment')
 a.set(434,505,'h','sequence output adapter')
 a.set(506,507,'enc','initialize encoded sequence allocation cursor');a.set(508,519,'h','initialize operation counters')
 a.set(543,679,'h','answer and observation output adapter')
 return a

def p06e(name,unknown=False):
 a=Annot(name)
 if not unknown:
  a.set(1,12,'h','declarations of harness-only words');a.set(22,72,'h','fixed instance and message input')
  a.set(160,172,'h','answer and relation-operation counter declarations')
  a.set(239,244,'h','count matching takes facts')
  a.ranges([(278,283),(303,308),(326,331),(332,337),(348,353)],'h','count derivations or relation operations')
  a.set(354,359,'h','print a computed true answer')
  a.set(398,411,'h','initialize harness counters')
  a.set(417,553,'h','inline observation output adapter')
 else:
  a.set(1,12,'h','declarations of harness-only words');a.set(20,70,'h','fixed instance and message input')
  a.set(151,163,'h','answer and relation-operation counter declarations')
  a.set(230,235,'h','count matching takes facts')
  a.set(249,315,'h','atom output adapter')
  a.ranges([(329,334),(352,357),(376,381),(382,387),(398,403)],'h','count derivations or relation operations')
  a.set(404,421,'h','print a computed nonmajor answer')
  a.set(460,473,'h','initialize harness counters');a.set(476,612,'h','inline observation output adapter')
 return a

def refine(a,name):
 # Read names and index structure from the supplied frozen token list only.
 ts=a.ts
 if name.startswith('P04'):
  # Class each formal/actual argument as a construct. Parentheses are the call shell.
  legitimate={'loop':{'x','xv'},'equals':{'x','xv','c','c1'},
              'conseq':{'s','sv','m'},'alist':{'s','sv','m'}}
  for i,t in enumerate(ts):
   if t in legitimate and i+1<len(ts) and ts[i+1]=='(':
    j=i+2;start=j;depth=0;args=[]
    while j<len(ts):
     if ts[j]=='(' :depth+=1
     if ts[j]==')':
      if depth==0:args.append((start,j-1));break
      depth-=1
     if ts[j]==',' and depth==0:args.append((start,j-1));start=j+1
     j+=1
    for l,h in args:
     code='p' if ts[l] in legitimate[t] else 'arg'
     a.set(l,h,code,'relation value argument' if code=='p' else 'extra knownness or success-continuation argument')
     if l>i+2:a.set(l-1,l-1,code)
    a.set(i,i+1,'p','relation application or definition shell')
    a.set(j,j,'p','close relation application or formal parameter list')
  # A success callback passes on an already obtained solution; it is the introduced continuation.
  for i,t in enumerate(ts):
   if t=='found' and RULES[a.a[i][0]][0]!='H':a.set(i,i,'arg','success-continuation parameter or invocation')
   if t in ['xk','sk','mk'] and RULES[a.a[i][0]][0]!='H':
    if i>0 and ts[i-1]=='Boolean':a.set(i-1,i,'r','knownness flag declaration')
    if ts[i+1:i+2]==[':=']:
     a.set(i,i+2,'r','record knownness')
     if ts[i+2]=='false' and any(x=='found' for x in ts[max(0,i-3):i]):a.set(i,i+2,'c','undo temporary knownness after a solution')
    if i>0 and ts[i-1]=='if':a.set(i-1,i+1,'r','test which places are known')
  # Explicit flag-parameter declarations (the two-flag conseq header included).
  for i,t in enumerate(ts):
   if t=='Boolean' and ts[i+1:i+2] in [['xk'],['sk'],['mk']]:
    j=i
    while ts[j]!=';':j+=1
    if RULES[a.a[i][0]][0]!='H':a.set(i,j-1,'r','knownness flag declaration')
  # Additional callback formal declarations are R.
  for i,t in enumerate(ts[:-1]):
   if t=='procedure' and ts[i+1]=='found':a.set(i,i+1,'arg','success-continuation formal declaration')
 if name.startswith('P05'):
  # Fully known comparison tests and their verdicts are P; holding flags remain R.
  for i,t in enumerate(ts):
   if ts[i:i+3]==['if','¬','(']:
    j=i
    while ts[j]!='then':j+=1
    a.set(i,j,'eval','fully known problem relation test')
    if ts[j+1:j+3]==['xa','[']:
     z=j+1
     while ts[z] not in [';','end']:z+=1
     a.set(j+1,z-1,'eval','reject a value violating the problem relation')
  # pk is instrumentation, including its whole indexed assignment/declaration.
  for i,t in enumerate(ts):
   if t=='pk' and ts[i+1:i+2]==['[']:
    j=i+1
    while ts[j]!=']':j+=1
    if ts[j+1:j+2]==[':=']:a.set(i,j+2,'h','count application of the current pick fact')
    else:a.set(i-1,j,'h','pick-operation counter array declaration')
 if name in ['P06a','P06b']:
  # Else branch belongs to the known negation's own truth test, not knownness dispatch.
  for i in range(len(ts)-2):
   if ts[i:i+3]==['else','begin','inconsistent']:a.set(i,i+1,'eval','negated equality false: contradiction branch')
 # Counter assignments are H even when nested in an otherwise P case.
 counter_names=({'loop1','al1','al2'} if name.startswith('P04') else
                {'x1','x2'} if name in ['P06a','P06b'] else
                {'mem1','mem2','sd1','sd2','sd3'} if name=='P06d' else
                {'nm1','stud','math','tak','negs','found'} if name.startswith('P06e') else set())
 for i,t in enumerate(ts[:-1]):
  if t in counter_names and ts[i+1]==':=':
   j=i+2
   while j<len(ts) and ts[j] not in [';','end']:j+=1
   a.set(i,j-1,'h','harness counter assignment')
 return a

def tidy(a,name):
 ts=a.ts
 # Read calls are whole constructs: stage constants P, protocol words H.
 for i,t in enumerate(ts):
  if t=='ininteger' and ts[i+1:i+2]==['(']:
   j=i+2
   while ts[j]!=')':j+=1
   dest=ts[i+4]
   a.set(i,j,'h' if dest in ['n','cap','m','code','k'] else 'p',
         'read fixed harness word' if dest in ['n','cap','m','code','k'] else 'read stage information in the problem encoding')
 if name.startswith('P04'):
  for i,t in enumerate(ts[:-2]):
   if t=='procedure' and ts[i+1] in ['conseq','alist','equals','loop']:
    a.set(i,i+1,'p','problem relation evaluator declaration shell')
   if ts[i:i+4]==['procedure','body',';','begin']:
    a.set(i+3,i+3,'decl','introduced continuation block shell')
  for i,t in enumerate(ts[:-2]):
   if ts[i:i+5]==['if','x','=','c','then']:a.set(i,i+4,'eval','fully known equality test')
   if t in ['xk','sk','mk'] and ts[i+1]==':=':
    a.set(i,i+2,'r','record problem-specific knownness')
    if ts[i+2]=='false' and ts[max(0,i-2):i]==['found',';']:
     a.set(i,i+2,'c','undo temporary knownness after passing a solution onward')
   if t=='else' and ts[i+1:i+3]==['begin','al1']:a.set(i,i,'r','knownness dispatch alternative')
   if t=='else' and ts[i+1:i+3]==['begin','al2']:
    # This is either alist-left's empty case or alist-right's recursive knownness branch.
    a.set(i,i,'r','knownness dispatch alternative')
  # The ordinary value parameters of the equation evaluator are problem places.
  for i,t in enumerate(ts):
   if ts[i:i+4]==['integer','s',',','m']:a.set(i,i+3,'p','equation value parameter declarations')
 if name.startswith('P05'):
  # Observation counts only count; xa and relation-arrival flags implement retained state.
  for i,t in enumerate(ts):
   if i<60 and t in ['held','alive']:
    a.set(i,i,'h','observation-only counter declaration')
   if t in ['picked','r1','r2','r3'] and ts[i+1:i+2]==[':=']:
    j=i+2
    while ts[j] not in [';','end']:j+=1
    a.set(i,j-1,'r','record arrived information in problem-specific holding state')
   if t=='xa' and ts[i+1:i+2]==['[']:
    j=i+1
    while ts[j]!=']':j+=1
    if ts[j+1:j+3]==[':=','true']:a.set(i,j+2,'r','mark the arrived pick value as live')
   if ts[i:i+2]==['if','k']:
    j=i+2
    while ts[j]!='then':j+=1
    a.set(i,j,'h','fixed stage-number dispatch')
  # Remove a leftover P end from an R holding branch, handled systematically below.
 if name.startswith('P06e'):
  # i also indexes the input fact arrays; it is not a harness-only variable.
  a.set(8,8,'p','fact-input index declaration')
 # Block delimiters have the introducing construct's class (rule 10), not the first child's.
 stack=[]
 for i,t in enumerate(ts):
  if t=='begin':
   if i and ts[i-1] in ['then','do','else']:
    a.a[i]=a.a[i-1]
   stack.append(i)
  elif t=='end':
   assert stack,(name,i)
   op=stack.pop();a.a[i]=a.a[op]
   if i+1<len(ts) and re.fullmatch('[A-Za-z][A-Za-z0-9]*',ts[i+1]) and ts[i+1] not in ['else','end']:
    # Optional closing procedure identifier; it belongs to that definition's block.
    a.a[i+1]=a.a[op]
 assert not stack,(name,stack)
 return a

def transfer(a,key2):
 b=Annot(key2)
 bg=collections.defaultdict(list);ag=collections.defaultdict(list)
 for i,r in enumerate(a.rs):ag[int(r['line'])].append(i)
 for i,r in enumerate(b.rs):bg[int(r['line'])].append(i)
 assert set(ag)==set(bg),(a.name,key2)
 for line,ai in ag.items():
  bi=bg[line];ats=[a.ts[i] for i in ai];bts=[b.ts[i] for i in bi]
  sm=difflib.SequenceMatcher(None,ats,bts,autojunk=False)
  for tag,l,h,u,v in sm.get_opcodes():
   if tag=='equal':
    for x,y in zip(ai[l:h],bi[u:v]):b.a[y]=a.a[x]
   elif u<v:
    old=[a.a[x] for x in ai[l:h]]
    if old:
     classes={RULES[z[0]][0] for z in old}
     assert len(classes)==1,(a.name,key2,line,tag,old,ats,bts)
     label=old[0]
    else:
     nearby=[a.a[ai[z]] for z in [max(0,l-1),min(len(ai)-1,l)]]
     if any(RULES[z[0]][0]=='H' for z in nearby):label=('h','X1 output adapter formatting')
     else:
      assert nearby[0][0]==nearby[1][0],(a.name,line,ats,bts,nearby)
      label=nearby[0]
    for x in bi[u:v]:b.a[x]=label
 return b

def make_annotations():
 out={}
 for name in ['P04a','P04b','P04c','P04d','P04e','P04f','P05a','P05b','P05c','P06a','P06b','P06d','P06e1','P06e3']:
  key='report/'+name+'.alg'
  if name in ['P04a','P04b']:a=p04ab(key)
  elif name.startswith('P04'):a=p04seq(key,name in ['P04c','P04e'],name in ['P04e','P04f'])
  elif name.startswith('P05'):a=p05(key,name=='P05b')
  elif name in ['P06a','P06b']:a=p06ab(key,name=='P06b')
  elif name=='P06d':a=p06d(key)
  else:a=p06e(key,name=='P06e3')
  if name=='P05c':a=transfer(out['report/P05a.alg'],key)
  else:a=tidy(refine(a,name),name)
  out[key]=a
  # Dialects have exactly corresponding source lines; align their frozen tokens per line.
  key2='x1/'+name+'.a60'
  out[key2]=transfer(a,key2)
 return out

def finalize(a):
 # Separators take the following construct's class. Do not move a separator into an expression.
 for i,t in enumerate(a.ts[:-1]):
  if t==';':a.a[i]=a.a[i+1]
 # Leading argument separators follow the argument; declarations/calls retain their shell.
 for i,t in enumerate(a.ts[:-1]):
  if t==',':a.a[i]=a.a[i+1]
 # Split at construct boundaries, including nested statements (rule 10).
 breaks={0,len(a.a)}
 for i in range(1,len(a.a)):
  if a.a[i]!=a.a[i-1] or a.rs[i]['line']!=a.rs[i-1]['line']:breaks.add(i)
  if a.ts[i] in [';','begin','end','else']:breaks.add(i)
  if a.ts[i-1] in ['then','do']:breaks.add(i)
 # Keep semicolon with the following construct, as rule 20 specifies.
 for i,t in enumerate(a.ts[:-1]):
  if t==';' and i+1 in breaks and a.a[i]==a.a[i+1]:breaks.discard(i+1)
 spans=[]
 bs=sorted(breaks)
 for l,h in zip(bs,bs[1:]):
  code,label=a.a[l];cl,_,rule=RULES[code]
  excerpt=' '.join(a.ts[l:h])
  if len(excerpt)>140:excerpt=excerpt[:137]+'...'
  spans.append({'from':l,'to':h-1,'class':cl,'construct':label+': '+excerpt,'rule':rule+('; METRICS 20 for leading separators' if a.ts[l] in [';',','] else '')})
 return spans

if __name__=='__main__':
 annotations=make_annotations()
 tokens={key:finalize(a) for key,a in annotations.items()}
 (OUT/'tokens-working.json').write_text(json.dumps(tokens,indent=2,ensure_ascii=False)+'\n')
 for k,v in tokens.items():
  counts=collections.Counter()
  for s in v:counts[s['class']]+=s['to']-s['from']+1
  print(k,len(annotations[k].rs),dict(counts))
