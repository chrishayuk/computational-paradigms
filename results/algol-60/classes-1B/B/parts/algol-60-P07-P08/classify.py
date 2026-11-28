#!/usr/bin/env python3
"""Independent classification from the supplied frozen tokens and permitted records.
Never invokes an ALGOL program. Paths read are explicitly restricted below.
"""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,re
BASE=Path('.')
OUT=Path('results/algol-60/classes-1B/B/parts/algol-60-P07-P08')
TEXTS=list(csv.reader((BASE/'results/algol-60/tokens/TEXTS-1B-P07-P08.tsv').open(),delimiter='\t'))[1:]
RULES={'H':'METRICS 13; ALGOL harness 2.7; nested constructs 10; separators 20',
 'P':'METRICS 2, 3, 8, 15, 19 (relation evaluator); nested constructs 10; separators 20',
 'R':'METRICS 19 (problem-specific holding), 5 (extra state); nested constructs 10; separators 20',
 'C':'METRICS 1, 2, 10 (explicit order/permission); separators 20'}
COUNTERS={'x1','x2','x3','rev1','rev2','conc1','conc2'}
WORDS={'n','cap','m','i','code','k'}
VALUES={'c1','c2','c3','xv','yv','zv','wv','uv','vv','av','bv','cv','sv','pv','rv','hd','tl','ev','top','nel'}
FLAGS={'xk','yk','zk','wk','uk','vk','ak','bk','ck','ek','r1','r2','r3','q1','q2','q3','q5','q6','changed','inconsistent'}
DEFS={'defined','concdef','rev1def','rev2def'}
ADAPTERS={'uname','place','state','relations','digits','printint','printel','printseq','seqplace','seqstate','elstate'}
class Tokens:
 def __init__(self,key):
  self.key=key;self.rows=list(csv.DictReader((BASE/f'results/algol-60/tokens/{key}.tokens.tsv').open(),delimiter='\t'))
  assert [int(r['index']) for r in self.rows]==list(range(len(self.rows)))
  self.t=[r['token'] for r in self.rows];self.lines=[int(r['line']) for r in self.rows];self.sp=[];self.used=set()
 def add(self,a,b,cl,label,rule=None):
  if a>b:return
  assert not self.used.intersection(range(a,b+1)),(self.key,a,b,label)
  self.used.update(range(a,b+1));self.sp.append({'from':a,'to':b,'class':cl,'construct':label,'rule':rule or RULES[cl]})
 def line(self,i):return self.lines[i]
 def label(self,a,b):return ' '.join(self.t[a:b+1])[:170]
 def at(self,line):return self.lines.index(line)
 def before(self,line):return next((i for i,l in enumerate(self.lines) if l>=line),len(self.t))

def decl(x,a,b,ctx):
 # Parameter declarations belong to their procedure; main mixed declarations split by declared name.
 if ctx!='main':x.add(a,b,ctx,'declaration: '+x.label(a,b));return
 ts=x.t; start=a;nest=0;parts=[]
 for j in range(a,b+1):
  if ts[j] in ['[','(']:nest+=1
  if ts[j] in [']',')']:nest-=1
  if ts[j]==',' and nest==0:parts.append((start,j-1));start=j
 parts.append((start,b))
 for l,r in parts:
  ns=[v for v in ts[l:r+1] if re.fullmatch('[A-Za-z][A-Za-z0-9]*',v) and v.lower() not in ['integer','boolean','array']]
  name=ns[0] if ns else ''
  cl='H' if name in WORDS or name in COUNTERS or name=='held' else 'C' if name in DEFS or name=='ord' else 'P' if name in VALUES else 'R'
  x.add(l,r,cl,'declaration of '+name)

def simple_class(x,a,b,proc,base):
 ts=x.t[a:b+1];lhs=ts[0] if ts else ''
 if lhs in COUNTERS:return 'H','operation counter '+lhs
 if proc=='propagate':return 'R','examine a held relation' if lhs.startswith('examine') else 'holding pass state'
 if lhs in DEFS:return 'C','set permission flag '+lhs
 if lhs=='propagate' or (lhs.startswith('examine') and proc=='main'):return 'R','invoke problem-specific holding/evaluation'
 if proc=='main':
  if lhs=='ininteger':
   return ('H' if set(ts)&(WORDS|{'ord'}) else 'P'),'read harness words' if set(ts)&(WORDS|{'ord'}) else 'read stage constants'
  if lhs in COUNTERS:return 'H','initialize operation counters'
  if lhs in WORDS or lhs in ['outstring','outinteger','PRINTTEXT','print','NLCR']:return 'H','harness input/output'
  if lhs in FLAGS or any(v in FLAGS for v in ts[:ts.index(':=')]) if ':=' in ts else False:return 'R','initialize held state'
  return 'P','stage information / encoded value: '+x.label(a,b)
 if proc=='examine1' and 'P07g' in x.key:
  if lhs=='r1':return 'R','retire square relation'
  if lhs=='inconsistent':return 'P','reject candidate violating square equation'
  return 'R','square-root solution algorithm: '+x.label(a,b)
 if lhs in FLAGS:
  if lhs=='inconsistent':return 'P','inconsistent relation verdict'
  return 'R','known/held/changed bookkeeping: '+x.label(a,b)
 if proc in ['rev','conc'] and 'P08c' in x.key:
  if lhs in ['st'] or (lhs in ['rev','conc'] and not any(v in ts for v in ['(', 'cons'])):return 'R','three-state return protocol: '+x.label(a,b)
  if lhs=='t' and not any(v in ts for v in ['rev','conc']):return 'R','three-state return propagation'
 if lhs=='t' and proc=='examine2' and 'P08c' in x.key:return 'P','apply rev to known sequence (status retained separately)'
 return ('P' if proc.startswith('examine') or proc=='equal' else base),'relation/value operation: '+x.label(a,b)

def condition_class(x,a,b,proc,base):
 ts=set(x.t[a:b+1])
 if proc=='propagate':return ('C' if 'ord' in ts else 'R')
 if proc=='main' and 'k' in ts:return 'H'
 if ts & DEFS:return 'C'
 if ts & FLAGS:
  # A semantic failure guard inside the prefix algorithm controls more than case dispatch.
  if ts<= {'if','else','¬','inconsistent','then'}:return 'C'
  return 'R'
 if proc=='examine1' and 'P07g' in x.key:
  return 'P' if '×' in ts and 'c1' in ts else 'R'
 if 'P08c' in x.key and ts & {'st','t'}:return 'R'
 return 'P' if proc.startswith('examine') or proc=='equal' else base

class Parser:
 def __init__(self,x,proc,base):
  self.x=x;self.ts=list(x.t);self.proc=proc;self.base=base
  # The frozen TSV omits quote marks for Report strings. Mask only the already
  # identified string argument of each fixed output call while parsing structure;
  # keep the original tokens, their indices and their classes unchanged.
  for i,v in enumerate(x.t):
   if v=='outstring' and i+5<len(x.t) and x.t[i+1]=='(' and x.t[i+3]==',':self.ts[i+4]='<string>'
   elif v=='PRINTTEXT' and i+3<len(x.t) and x.t[i+1]=='(':self.ts[i+2]='<string>'
 def stmt(self,i,end,override=None,frame=None):
  x=self.x;ts=self.ts;base=override or self.base
  if i>=end:return i
  if ts[i]==';':
   # The separator is reserved for the following construct by the caller.
   return self.stmt(i+1,end,override)
  if ts[i]=='begin':
   blockclass=frame or base
   x.add(i,i,blockclass,self.proc+' block opener');i+=1
   while i<end and ts[i]!='end':
    start=i
    if ts[i]==';':i+=1
    j=self.stmt(i,end,override)
    if start<i:
     # Assign semicolon to the first span of the following construct.
     target=next(s for s in reversed(x.sp) if s['from']==i)
     target['from']=start;x.used.add(start)
    assert j>i,(x.key,i,ts[i:i+15]);i=j
   if i<end:
    j=i+1
    if j<end and ts[j] not in [';', 'else','end']:j+=1
    x.add(i,j-1,blockclass,self.proc+' block closer');return j
   return i
  if ts[i]=='if':
   a=i;depth=0;i+=1
   while i<end:
    if ts[i] in ['(', '[']:depth+=1
    if ts[i] in [')', ']']:depth-=1
    if ts[i]=='then' and depth==0:break
    i+=1
   assert i<end,(x.key,'then',a)
   cl=condition_class(x,a,i,self.proc,base) if override is None else base
   x.add(a,i,cl,self.proc+' conditional header: '+x.label(a,i));i=self.stmt(i+1,end,override,frame=cl)
   if i<end and ts[i]=='else':
    x.add(i,i,cl,self.proc+' else connective');i=self.stmt(i+1,end,override,frame=cl)
   return i
  if ts[i]=='for':
   a=i;depth=0
   while i<end:
    if ts[i] in ['(', '[']:depth+=1
    if ts[i] in [')', ']']:depth-=1
    if ts[i]=='do' and depth==0:break
    i+=1
   assert i<end
   if override:cl=override
   elif self.proc=='main' and ('m' in ts[a:i] or 'true' in ts[a:i]):cl='H'
   elif self.proc=='propagate':cl='C'
   else:cl='C' if 'inconsistent' in ts[a:i] else 'P' if self.proc.startswith('examine') and 'P07g' not in x.key else base
   x.add(a,i,cl,self.proc+' loop header: '+x.label(a,i));return self.stmt(i+1,end,override,frame=cl)
  if ts[i].lower() in ['integer','boolean']:
   j=i
   while j<end and ts[j]!=';':j+=1
   # Do not consume separator: it belongs to following statement.
   decl(x,i,j-1,'main' if self.proc=='main' else base);return j
  a=i;depth=0;conditional=0
  while i<end:
   v=ts[i]
   if v in ['(', '[']:depth+=1
   if v in [')', ']']:depth-=1
   if depth==0 and v in [';','end']:break
   # Conditional expressions have their own elses, unlike statement elses.
   if depth==0 and v=='if':conditional+=1
   if depth==0 and v=='else':
    if conditional:conditional-=1
    else:break
   i+=1
  assert i>a,(x.key,a,ts[a:a+10])
  cl,label=simple_class(x,a,i-1,self.proc,base) if override is None else (base,'output adapter statement')
  x.add(a,i-1,cl,label)
  return i
 def region(self,a,b,override=None):
  i=a;pending=None
  while i<b:
   if self.ts[i]==';':pending=i;i+=1;continue
   j=self.stmt(i,b,override)
   if pending is not None:
    target=next(s for s in reversed(self.x.sp) if s['from']==i);target['from']=pending;self.x.used.add(pending);pending=None
   assert j>i;i=j
  if pending is not None:
   # A terminal declaration/procedure separator introduces the next construct.
   return pending
  return None

MAIN_LINES={'P07a':114,'P07b':80,'P07c':60,'P07d':114,'P07f':80,'P07g':37,'P08a':226,'P08c':141}
# Output sections are a single output adapter each, including the count derived solely for observe().
OUTPUT_LINES={'P07a':126,'P07b':92,'P07c':72,'P07d':126,'P07f':92,'P07g':48,'P08a':261,'P08c':167}

def classify_tokens(key):
 x=Tokens(key);ts=x.t;name=Path(key).stem
 # Outer declaration block has no computational role beyond program framing.
 x.add(0,0,'H','outer program block opener')
 starts=[]
 for i,v in enumerate(ts):
  if v=='procedure':
   start=i-1 if i and ts[i-1].lower() in ['integer','boolean'] else i
   starts.append((start,ts[i+1]))
 main=x.at(MAIN_LINES[name]);first=starts[0][0] if starts else main
 # Main declarations before procedures, with separator ownership rule 20.
 p=Parser(x,'main','R');pend=p.region(1,first)
 if pend is not None:
  # Assign declaration separator to procedure header below.
  firstsep=pend
 else:firstsep=None
 for z,(a,proc) in enumerate(starts):
  b=starts[z+1][0] if z+1<len(starts) else main
  prefix=a
  if a>0 and ts[a-1]==';' and a-1 not in x.used:prefix=a-1
  # Remove the final semicolon, owned by the next procedure/main input construct.
  end=b-1 if ts[b-1]==';' else b
  if proc in ADAPTERS:
   x.add(prefix,end-1,'H','output adapter procedure '+proc)
   continue
  base='P' if proc in ['cons','same','sameel','readseq','conc','rev'] else 'R'
  # P08c status-returning procedures add a three-state protocol; body split below.
  j=a
  while j<end and ts[j]!=';':j+=1
  x.add(prefix,j-1,base,'procedure signature '+proc)
  j+=1
  # value and typed formal specifications until first statement.
  while j<end and (ts[j]=='value' or ts[j].lower() in ['integer','boolean']):
   k=j
   while k<end and ts[k]!=';':k+=1
   x.add(j-1,k-1,base,'formal specification of '+proc+': '+x.label(j,k-1));j=k+1
  body=j
  # Include separator before the body with its first header.
  parser=Parser(x,proc,base);pending=parser.region(body,end)
  if body-1 not in x.used:
   s=next(s for s in x.sp if s['from']==body);s['from']=body-1;x.used.add(body-1)
  if pending is not None:raise AssertionError((key,proc,'unexpected terminal separator',pending))
 # Parse main statement stream up to its final outer end, using H override on output-only region.
 a=main
 if ts[a-1]==';' and a-1 not in x.used:a-=1
 output=x.at(OUTPUT_LINES[name]);last=len(ts)-1
 if name.startswith('P08'):
  # Main input, initialization and message dispatch are handled as a stream. The final
  # two end tokens close the message body and outer program; parse just the body here.
  loopline=233 if name=='P08a' else 147
  lo=x.at(loopline)
  pp=Parser(x,'main','P');pp.region(a,lo)
  loopstart=lo-1 if ts[lo-1]==';' and lo-1 not in x.used else lo
  # Message loop and body wrapper are fixed harness constructs.
  do=ts.index('do',lo);x.add(loopstart,do,'H','fixed harness message loop header')
  x.add(do+1,do+1,'H','message body opener')
  pp.region(do+2,output)
  outstart=output-1 if ts[output-1]==';' and output-1 not in x.used else output
  Parser(x,'output','H').region(outstart,last-1,override='H')
  x.add(last-1,last-1,'H','message body closer');x.add(last,last,'H','outer program block closer')
 else:
  Parser(x,'main','P').region(a,output)
  outstart=output-1 if ts[output-1]==';' and output-1 not in x.used else output
  Parser(x,'output','H').region(outstart,last,override='H')
  x.add(last,last,'H','outer program block closer')
 # Split mixed chained assignment targets by role, as nested constructs (rule 10).
 for sp in list(x.sp):
  a,b=sp['from'],sp['to']; seg=ts[a:b+1]
  if sp['class'] in ['R','P'] and ':=' in seg and (('defined' in seg and len([v for v in seg if v==':='])>1) or ('top' in seg and 'rev1' in seg)):
   x.sp.remove(sp);x.used.difference_update(range(a,b+1))
   cuts=[]
   for j in range(a,b):
    if ts[j] in DEFS and ts[j+1]==':=':cuts.append((j,j+1,'C','permission flag initialization target'))
   if 'top' in seg and 'rev1' in seg:
    j=ts.index('rev1',a,b+1);cuts.append((j,b,'H','initialize operation counters in shared zero assignment'))
   cur=a
   for l,r,cl,lab in sorted(cuts):
    if cur<l:x.add(cur,l-1,sp['class'],sp['construct'])
    x.add(l,r,cl,lab);cur=r+1
   if cur<=b:x.add(cur,b,sp['class'],sp['construct'])
 # The return value of P08c's conc/rev is an added three-state protocol.
 if name=='P08c':
  for sp in list(x.sp):
   a,b=sp['from'],sp['to'];seg=ts[a:b+1]
   if sp['construct'].startswith('declaration:') and set(seg)&{'st','t'}:
    x.sp.remove(sp);x.used.difference_update(range(a,b+1));cur=a
    ends=[i for i in range(a,b+1) if ts[i]==',']+[b+1]
    for end in ends:
     v=next((v for v in ts[cur:end] if v not in [';','integer',',']),None)
     cl='R' if v in ['st','t'] else 'P'
     x.add(cur,end-1,cl,'status protocol local '+str(v) if cl=='R' else 'relation output local '+str(v));cur=end
   elif sp['class']=='P' and ':=' in seg and any(v in seg for v in ['rev','conc']):
    j=a+1 if ts[a]==';' else a
    if ts[j]=='t' and ts[j+1]==':=':
     x.sp.remove(sp);x.used.difference_update(range(a,b+1))
     x.add(a,j+1,'R','added status-return assignment target','METRICS 5, 10, 19; separators 20')
     x.add(j+2,b,'P','application of original relation places','METRICS 3, 10, 15; separators 20')
  for sp in list(x.sp):
   if sp['construct'] in ['procedure signature conc','procedure signature rev']:
    a=sp['from'];j=a+1 if ts[a]==';' else a
    x.sp.remove(sp);x.used.difference_update(range(a,sp['to']+1))
    x.add(a,j+1,'R','added integer status result in procedure signature', 'METRICS 5, 10, 19; separators 20')
    x.add(j+2,sp['to'],'P','relation name and original places', 'METRICS 3, 10; separators 20')

 assert len(x.used)==len(ts),(key,sorted(set(range(len(ts)))-x.used))
 x.sp.sort(key=lambda s:s['from'])
 assert [i for s in x.sp for i in range(s['from'],s['to']+1)]==list(range(len(ts)))
 return x

if __name__=='__main__':
 xs=[classify_tokens(r[0]) for r in TEXTS]
 (OUT/'token-classes.json').write_text(json.dumps({x.key:x.sp for x in xs},indent=2)+'\n')
 print('classified',len(xs),'texts',sum(len(x.t) for x in xs),'tokens')
