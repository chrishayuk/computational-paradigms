"""Classifier A's token classes for python P04-P06 (batch 1B).
Classes every token of every text in TEXTS-1B-P04-P06.tsv by construct, from a
table of (group, context, source line) rules, with sub-expression overrides;
INDENT/DEDENT take the class of the compound statement they open/close.
Checks that every token index is covered exactly once. Writes tokens.json."""
import re,json,sys
sys.path.insert(0,'results/python/classes-1B/A/parts/python-P04-P06')
from lines import texts,load

R19='rule 19 (holding code for the problem\'s own relations: known-tests, wait verdict, records)'
R13='rule 13 (output adapter / stand-in for harness answers())'
H7='harness README s.7 (H constructs); rule 13'
def grp(path):
    conf,f=path.split('/'); p=f[:3]
    if p=='P06': p = 'P06abc' if f[3] in 'abc' else 'P06de'
    return conf+':'+p

CONST=re.compile(r'^[A-Z_]+ = ')
def rule_for(g,ctx,line,path):
    """returns (cls, construct, rule, overrides) ; overrides: list of (anchor_pos, cls, construct, rule)"""
    conf,prob=g.split(':')
    ov=[]
    # ---- universal harness constructs
    if line.startswith('while (s := cp.stage())'): return ('H','stage loop header (cp.stage)',H7+' item 1',ov)
    if re.match(r'(el)?if s\.k == \d+:',line): return ('H','stage-number dispatch',H7+' item 2',ov)
    if line=='if not s.replay:': return ('H','replay test',H7+' item 3',ov)
    if line.startswith('cp.') : return ('H','harness call '+line.split('(')[0],H7+' item 4',ov)
    if ctx=='show': return ('H','output adapter show()',R13)+(ov,)
    if line in ('holds = False','holds = True','if not holds and not s.replay:') or line.startswith('print("false:'):
        return ('H','output adapter: "true"/"false" report of a ground query',R13,ov)
    if ctx=='<module>' and CONST.match(line) and line.split(' =')[0] not in ('UNKNOWNS','EVALUATOR','NIL','A','X'):
        return ('P','constants block entry: stage information '+line.split(' =')[0],'harness README s.3.1/s.7 (block entries are stage information); METRICS class P',ov)
    if line=='A = "a"': return ('P','the atom A (vocabulary)','METRICS class P (vocabulary)',ov)
    if re.match(r'for (x|_|value|p) in answers:',line): return ('H','stand-in for answers(): drawing the query generator\'s answers',R13,ov)
    if re.match(r'known\["(x|s|p)"\] = ',line): return ('H','collecting the answer for observe (bindings)',R13,ov)
    if line=='report()': return ('H','report call (output adapter)',R13,ov)
    if ctx=='report': return ('H','output adapter report()',R13,ov)
    # ---- core / stdlib P04
    if prob=='P04' and conf in ('core','stdlib-concurrency'):
        if line=='known = {}': return ('H','bindings dict, only collected for observe',R13,ov)
        if ctx=='loop': return ('P','loop(x), case 1 (generator)','rule 3 (mode-faithful transcription)',ov)
        if ctx=='equal': return ('P','x = k as a generator of x (x unknown) or test','rule 3, rule 8',ov)
        if ctx=='query': return ('P','the disjunction, alternatives in presentation order','rule 6 (stated disjunction); rule 3',ov)
        if ctx=='alist':
            return ('P','alist (%s) by its cases'%('left' if prob=='P04' and path.endswith(('P04c.py','P04d.py')) else 'right'),'rule 3 (mode-faithful transcription; s is None dispatch is case/direction dispatch); rule 15/tuple decomposition',ov)
        if line.startswith('answers = '): return ('P','the query','METRICS class P (the query)',ov)
    # ---- extended P04 / P06de shared resolution layer
    if conf=='extended' and prob in ('P04','P06de'):
        if line.startswith('from S.search'): return ('S','import of S backtracking search','rule 12 (listed S mechanism)',ov)
        if line.startswith('from S.suspend'): return ('S','import of S suspension queue (Var, deref, Queue)','rule 12 (listed S mechanism)',ov)
        if line=='binder = Queue()': return ('S','program S "unify": its binder (Queue used for bind with trail)','rules 12, 15 (general unifier is S)',ov)
        if line=='trail = []': return ('S','trail of the S search / unify','rules 12, 15',ov)
        if line=='stack = []': return ('H','search stack given only so it can be registered as pending',R13,ov)
        if line=='NIL = ()':
            used = path.endswith(('P04c.py','P04d.py','P04e.py','P04f.py','P06d.py'))
            return (('P','<> in the cons-cell encoding','METRICS class P (the problem\'s empty sequence)',ov) if used else
                    ('R','NIL, defined and unused in this program','R: a definition the problem does not give (dead code)',ov))
        if ctx=='unify': return ('S','program S mechanism "unify"','rules 12, 15 (a unifier is S)',ov)
        if ctx in ('children','done'): return ('S','program S mechanism "resolution" (%s)'%ctx,'rules 12, 15 (a search/resolution layer is S)',ov)
        if ctx=='negation': return ('S','program S mechanism "negation" (negation as failure by its own search)','rules 12, 15 (general over goals)',ov)
        if ctx=='cons':
            used = path.endswith(('P04c.py','P04e.py','P06d.py'))
            return ('R','cons(): encoding of a tuple constant as cons cells'+('' if used else ', defined and unused'),'R: a definition the problem does not give (input encoding conversion)',ov)
        if ctx in ('loop','equal','either','alist','mem','setdiff','student','maths','takes','nonmajor'):
            return ('P','%s, by its cases (heads unified, bodies as goals)'%ctx,'rule 3 (transcription by cases); rule 6 for either' if ctx=='either' else 'rule 3 (transcription by cases)',ov)
        if line.startswith('world = '): return ('P','the closed world (facts container)','METRICS class P (closed world facts)',ov)
        if re.match(r'world\["\w+"\] = ',line): return ('P','stage 1: facts of the closed world','METRICS class P (stage information)',ov)
        if line.startswith('for _ in search('):
            return ('H','stand-in for answers(): drawing the search\'s answers',R13,[(3,'C','search directive: search(query, children, done, trail, stack)','S-mechanisms.md (a search directive is C); METRICS class C')])
        if re.match(r'(x|sv|d|p) = Var\(',line): return ('P','the query\'s unknown','METRICS class P (the query)',ov)
        if line.startswith('query = '):
            ov=[]
            if 'cons(' in line: ov=[('cons','R','cons() conversion of a constant','R: input encoding conversion')]
            return ('P','the query (goal list)','METRICS class P (the query)',ov)
    # ---- P05 (all configurations)
    if prob=='P05':
        if line=='values = []':
            return (('H','values read from the store, collected for the harness',R13,ov) if conf=='extended' else ('R','values of x held across stages',R19,ov))
        if line=='x_has_values = []': return ('R','flag: x has been given values',R19,ov)
        if line=='held = []': return ('R','comparisons held until x has values',R19,ov)
        if line=='waiting = []': return ('R','record of the comparisons whose threads wait',R19,ov)
        if line=='facts = []': return ('P','pick\'s closed world (facts container)','METRICS class P',ov)
        if line=='failed = []': return ('H','constraints that emptied a domain, kept only for printing',R13,ov)
        if line=='X = "x"': return ('P','the unknown x (store variable)','METRICS class P',ov)
        if line.startswith('from S.propagate'): return ('S','import of S constraint propagator','rule 12 (listed S mechanism)',ov)
        if line=='store = Store()': return ('S','the propagator\'s store','rule 12 (listed S mechanism, instantiated)',ov)
        if ctx in ('pick','greater','different','equal'): return ('P','relation %s (test of a known value)'%ctx,'rule 19 (testing a fully known relation is P); rule 9 for "in"',ov)
        if ctx in ('holds','test'):
            if line.startswith('return'): return ('P','test of the relation on a value','rule 19 (testing a fully known relation)',ov)
            return ('R','dispatch of a held relation by its name',R19,ov)
        if ctx=='source':
            if line in ('return tuple(facts)','return (k,)'): return ('P','computing x\'s values from the relation','rule 19 (computing a place is P)',ov)
            return ('R','source(): which relation can give x values / must wait',R19,ov)
        if ctx=='keep': return ('P','keep(): the conjunction applied to the values held','rule 7 (comprehension stating the conjunction)',ov)
        if ctx=='on_x':
            if line.startswith('holds.__name__'): return ('H','name for rendering only',R13,ov)
            return ('R','on_x(): the relation as a one-place predicate for the store','R: a definition the problem does not give',ov)
        if ctx=='post':
            if line.startswith('if not store.relation'):
                return ('H','failure note for printing',R13,[(['store','.','relation'],'P','posting the relation on x to the store','METRICS class P (the constraint posted); S-mechanisms.md')])
            if line.startswith('failed.append'): return ('H','failure note for printing',R13,ov)
            return ('P','post(): posting a relation on x','METRICS class P (the constraint posted)',ov)
        if ctx=='arrive':
            if conf=='stdlib-concurrency': return ('C','arrive(): one thread per relation','METRICS class C (thread calls)',ov)
            if line in ('keep(name, k)','post(name, k)'): return ('P','the arriving relation applied','rule 1 (the stage\'s relation)',ov)
            if line=='store.var(X, given)': return ('P','x given its domain by the relation (pick\'s facts / x = k)','METRICS class P (posted relation)',ov)
            return ('R','arrive(): hold a comparison until x has values, release held ones',R19,ov)
        if ctx in ('told','settle') or line in ('import threading','changed = threading.Condition()','count = {"busy": 0, "news": 0}','settle()'):
            return ('C','thread synchronisation (%s)'%(ctx if ctx!='<module>' and ctx!='<main>' else line.split(' ')[0]),'METRICS class C (thread calls, scheduling)',ov)
        if ctx=='hold':
            if line=='keep(name, k)': return ('P','the relation applied once x has values','rule 1',ov)
            if line in ('name, k = rel','while not x_has_values and source(name, k) is None:','waiting.append(rel)','if not x_has_values:','values[:] = source(name, k)','x_has_values.append(True)'):
                return ('R','hold(): wait verdict / record of waiting / x given values',R19,ov)
            return ('C','hold(): thread synchronisation','METRICS class C (thread calls)',ov)
        if ctx=='<main>':
            if line.startswith('facts[:] ='): return ('P','stage 1/2: pick\'s facts','METRICS class P (stage information)',ov)
            if line.startswith('arrive('): return ('P','the stage\'s relation','METRICS class P (stage information)',ov)
            if line.startswith('values[:] = sorted('): return ('H','store domain collected for the harness',R13,ov)
    # ---- P06abc (all configurations)
    if prob=='P06abc':
        if line=='UNKNOWNS = ("x",)': return ('H','names of unknowns, used only to render the answer',R13,ov)
        if ctx=='Unknown':
            if line in ('def __repr__(self):','return self.name'): return ('H','rendering of an unknown',R13,ov)
            return ('R','class Unknown: an unknown as a place of a held relation',R19,ov)
        if line=='x = Unknown("x")' or line=='x = Var("x")': return ('P','the unknown x','METRICS class P',ov)
        if line=='known = {}': return ('R','bindings store used to decide held relations',R19,ov)
        if line in ('held = []','failed = []','waiting = []'): return ('R','held / failed / waiting relations',R19,ov)
        if line.startswith('from S.suspend'): return ('S','import of S suspension queue','rule 12 (listed S mechanism)',ov)
        if line=='q = Queue()': return ('S','the suspension queue','rule 12 (listed S mechanism, instantiated)',ov)
        if line=='unknowns = {"x": x}': return ('H','unknowns dict for registration and rendering',R13,ov)
        if line=='EVALUATOR = {"=": equal, "not =": not_equal}': return ('R','evaluator table of held relations',R19,ov)
        if ctx in ('equal','not_equal'):
            if line.startswith('def '): return ('P','relation %s (evaluator)'%ctx,'rule 19 (evaluator)',ov)
            if line.startswith('return (a, b)'): return ('P','testing the fully known relation (%s)'%ctx,'rule 19 (testing a fully known relation is P); negation connective P',ov)
            if line in ('return a, a','return b, b'): return ('P','computing one place from the other','rule 19 (computing a place is P)',ov)
            return ('R','evaluator: test of which places are known / wait verdict',R19,ov)
        if ctx=='place': return ('R','place(): the value of a place, None while unknown (test of which places are known)',R19,ov)
        if ctx=='decide' or line=='decide()': return ('R','decide(): taking up held relations until none is decided',R19+'; written for this program\'s relations, not listed as S',ov)
        if ctx in ('told','settle','pose') or line in ('import threading','changed = threading.Condition()','count = {"busy": 0, "news": 0}','settle()'):
            return ('C','thread synchronisation / one thread per relation','METRICS class C (thread calls)',ov)
        if ctx=='hold':
            if line in ('name, places = rel','waiting.append(rel)','if outcome is False:','failed.append(rel)','else:','for p, v in zip(places, outcome):','if isinstance(p, Unknown) and v is not None and p.name not in known:','known[p.name] = v') or line.startswith('while (outcome'):
                return ('R','hold(): evaluate, wait verdict, record',R19,ov)
            return ('C','hold(): thread synchronisation','METRICS class C (thread calls)',ov)
        if ctx=='Relation':
            if line in ('def __repr__(self):','return "%s%r" % (self.name, tuple(self.places))'): return ('H','rendering of a goal',R13,ov)
            if line.startswith('q.wait('): return ('C','freeze call: the goal waits on its unbound unknowns','S-mechanisms.md (a freeze call is C)',ov)
            return ('R','class Relation: a problem relation held as a goal (evaluate, wait verdict, record, bind)',R19,ov)
        if ctx=='<main>':
            if line.startswith('held.append('): return ('R','holding the stage\'s relation',R19,[(4,'P','the stage\'s relation (name, places)','METRICS class P (stage information)')])
            if line.startswith('pose('): return ('C','pose(): a thread for the stage\'s relation','METRICS class C (thread calls)',[(2,'P','the stage\'s relation (name, places)','METRICS class P (stage information)')])
            if line.startswith('q.wait(Relation'): return ('C','q.wait(): the goal queued','S-mechanisms.md (freeze call is C)',[(4,'P','the stage\'s relation as a goal','METRICS class P (stage information)')])
            if line=='q.run()': return ('C','q.run(): running ready goals','METRICS class C (explicit scheduling)',ov)
            if line in ('if failed:','elif known:','else:','if told:') or line.startswith(('print(','told = [')): return ('H','output adapter: report',R13,ov)
    # ---- core P06de
    if prob=='P06de' and conf in ('core','stdlib-concurrency'):
        if line=='known = {}': return ('H','bindings dict, only collected for observe',R13,ov)
        if ctx in ('mem','setdiff','student','maths','takes','nonmajor'):
            return ('P','%s by its cases'%ctx,'rule 3 (mode-faithful transcription); rule 2 (case guards); rule 9 for "in"' ,ov)
        if line.startswith('world = '): return ('P','the closed world (facts container)','METRICS class P',ov)
        if re.match(r'world\["\w+"\] = ',line): return ('P','stage 1: facts of the closed world','METRICS class P (stage information)',ov)
        if line.startswith('answers = '): return ('P','the query','METRICS class P (the query)',ov)
        if line.startswith('known["d"] = '): return ('H','collecting the answer for observe',R13,[(5,'P','the query setdiff(...)','METRICS class P (the query)')])
    raise ValueError('no rule: %s %s %r (%s)'%(g,ctx,line,path))

def match_end(toks,i):
    depth=0
    for j in range(i,len(toks)):
        if toks[j] in '([{': depth+=1
        elif toks[j] in ')]}':
            depth-=1
            if depth==0: return j
    raise ValueError

def classify(path):
    src,toks,ctx=load(path); g=grp(path)
    cls=[None]*len(toks)
    bylines={}
    for idx,ln,t in toks:
        if t not in ('<INDENT>','<DEDENT>'): bylines.setdefault(ln,[]).append(idx)
    for ln,idxs in bylines.items():
        raw=src[ln-1]; line=raw.split('  #')[0].strip() if '#' in raw else raw.strip()
        c,con,rule,ov=rule_for(g,ctx[ln],line,path)
        lt=[toks[i][2] for i in idxs]
        lab=[(c,con,rule,0)]*len(idxs)
        inst=0
        for anc,c2,con2,r2 in ov:
            if isinstance(anc,int): starts=[anc]
            else:
                a=[anc] if isinstance(anc,str) else list(anc)
                starts=[k for k in range(len(lt)) if lt[k:k+len(a)]==a]
            for k in starts:
                inst+=1
                b = k if lt[k] in '([{' else next(j for j in range(k,len(lt)) if lt[j]=='(')
                e = match_end(lt,b)
                for q in range(k,e+1): lab[q]=(c2,con2,r2,inst)
                if k>0 and lt[k-1]==',': lab[k-1]=(c2,con2,r2,inst)
        # s.constants reads inside non-H constructs: H (README s.7 item 3), with a preceding comma (rule 20)
        for k in range(len(lt)-5):
            if lt[k:k+3]==['s','.','constants'] and lt[k+3]=='[' and lt[k+5]==']':
                inst+=1
                for q in range(k,k+6): lab[q]=('H','reading s.constants',H7+' item 3; rule 20 for a preceding comma',inst)
                if k>0 and lt[k-1]==',' : lab[k-1]=lab[k]
        seg=0; prevl=None
        for i,l in zip(idxs,lab):
            if l!=prevl: seg+=1; prevl=l
            cls[i]=l[:3]+((ln,seg),ctx[ln])
    # layout: INDENT takes the class of the header it follows; DEDENT the block it closes
    stack=[]; prev=None
    for idx,ln,t in toks:
        if t=='<INDENT>':
            hdr = prev; stack.append(hdr); cls[idx]=(hdr[0],hdr[1],hdr[2],('layout',idx),hdr[4])
        elif t=='<DEDENT>':
            hdr=stack.pop(); cls[idx]=(hdr[0],hdr[1],hdr[2],('layout',idx),hdr[4])
        else: prev=cls[idx]
    assert all(c is not None for c in cls)
    # spans: one per construct instance (a line segment, or a layout token);
    # a whole top-level def/class that is one construct is one span
    whole={}
    for c in cls:
        if c[4] not in ('<module>','<main>'): whole.setdefault(c[4],set()).add((c[0],c[1]))
    spans=[]
    for idx,c in enumerate(cls):
        unit = ('def',c[4]) if c[4] in whole and len(whole[c[4]])==1 else c[3]
        if spans and spans[-1]['_u']==unit and spans[-1]['to']==idx-1:
            spans[-1]['to']=idx
        else: spans.append({'from':idx,'to':idx,'class':c[0],'construct':c[1],'rule':c[2],'_u':unit})
    for sp in spans: del sp['_u']
    # coverage check
    cov=[0]*len(toks)
    for s in spans:
        for i in range(s['from'],s['to']+1): cov[i]+=1
    assert all(x==1 for x in cov) and len(cov)==toks[-1][0]+1
    return spans,cls,toks

if __name__=='__main__':
    out={}; tot={}
    for t in texts():
        spans,cls,toks=classify(t)
        out[t]=spans
        cnt={}
        for c in cls: cnt[c[0]]=cnt.get(c[0],0)+1
        tot[t]=cnt
        print(t,len(toks),cnt)
    json.dump(out,open('results/python/classes-1B/A/parts/python-P04-P06/tokens.json','w'),ensure_ascii=False,indent=0)
    json.dump(tot,open('results/python/classes-1B/A/parts/python-P04-P06/totals.json','w'),indent=1)
