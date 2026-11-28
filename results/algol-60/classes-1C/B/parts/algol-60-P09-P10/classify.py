"""Independent classifier B. Reads only the explicitly permitted evidence.

Uses frozen token rows, never lexes source or executes an ALGOL program.
Run from this output directory with python3 classify.py.
"""
from pathlib import Path
from collections import Counter
import csv
import json
import hashlib
import re

ROOT = Path('.')
OUT = Path(__file__).resolve().parent
TEXTS = []
ALIASES = {}
for line in (ROOT/'results/algol-60/tokens/TEXTS-1C-P09-P10.tsv').read_text().splitlines()[1:]:
    first, other = line.split('\t')
    TEXTS.append(first)
    ALIASES[first] = other.split()

def norm(s):
    return s.replace('\u0332', '').lower()

class Classifier:
    def __init__(self, path):
        self.path = path
        self.rows = list(csv.DictReader((ROOT/'results/algol-60/tokens'/f'{path}.tokens.tsv').open(), delimiter='\t'))
        assert [int(r['index']) for r in self.rows] == list(range(len(self.rows)))
        self.labels = [None]*len(self.rows)
        self.byline = {}
        self.serial = 0
        for r in self.rows:
            self.byline.setdefault(int(r['line']), []).append(int(r['index']))
        for line, ids in self.byline.items():
            self.put(ids[0], ids[-1], 'H', f'Harness message handling or output adapter at source line {line}', 'METRICS 10, 13; harness README 2.7')

    def put(self, a, b, cls, desc, rule):
        self.serial += 1
        label = (cls, desc, rule, self.serial)
        for i in range(a, b+1):
            self.labels[i] = label

    def lines(self, a, b, cls, desc, rule):
        # A procedure can be one construct; its nested statements are overridden.
        ids = [i for l, ix in self.byline.items() if a <= l <= b for i in ix]
        assert ids, (self.path, a, b)
        self.put(min(ids), max(ids), cls, desc, rule)

    def phrase(self, line, phrase, cls, desc, rule):
        # phrase is a list of existing token texts, not a new tokenization.
        ix = self.byline[line]
        vals = [norm(self.rows[i]['token']) for i in ix]
        seq = [norm(t) for t in phrase]
        hits = [j for j in range(len(vals)-len(seq)+1) if vals[j:j+len(seq)] == seq]
        assert len(hits)==1, (self.path,line,phrase,hits)
        j = hits[0]
        self.put(ix[j], ix[j+len(seq)-1], cls, desc, rule)

    def declaration(self, line, mapping):
        # Split a shared declaration into its declared arguments, keeping commas
        # with the following argument (rule 20). Type introducer follows first.
        ix = self.byline[line]
        vals = [norm(self.rows[i]['token']) for i in ix]
        starts = [0]+[j for j,v in enumerate(vals) if v==',']
        for k,start in enumerate(starts):
            end = starts[k+1]-1 if k+1<len(starts) else len(ix)-1
            names = [v for v in vals[start:end+1] if v in mapping]
            assert len(names)==1, (self.path,line,names)
            name=names[0]; cls=mapping[name]
            rule = {'P':'METRICS 3, 15; systems Values', 'R':'METRICS 3, 19', 'H':'METRICS 13; harness README 2.7', 'C':'METRICS 1, 10'}[cls]
            self.put(ix[start],ix[end],cls,f'Declaration of {name}',rule)

    def finish(self):
        # A semicolon separating different constructs belongs to the next one.
        for i in range(len(self.rows)-2,-1,-1):
            if self.rows[i]['token']==';' and self.labels[i]!=self.labels[i+1]:
                self.labels[i]=self.labels[i+1]
        spans=[]
        start=0
        for end in range(1,len(self.rows)+1):
            if end==len(self.rows) or self.labels[end]!=self.labels[start]:
                cls,desc,rule,_=self.labels[start]
                spans.append({'from':start,'to':end-1,'class':cls,'construct':desc,'rule':rule})
                start=end
        return spans

P='METRICS 2, 3, 8, 10, 15'
R='METRICS 3, 5, 10, 19'
H='METRICS 13; harness README 2.7'
C='METRICS 1, 10'

def classify(path):
    c=Classifier(path)
    key=Path(path).name.split('.')[0]
    def L(a,b,cl,d,rule=None):
        c.lines(a,b,cl,d,rule or {'P':P,'R':R,'H':H,'C':C}[cl])
    def T(line,phrase,cl,d,rule=None):
        c.phrase(line,phrase,cl,d,rule or {'P':P,'R':R,'H':H,'C':C}[cl])
    def D(line,**mapping): c.declaration(line,mapping)
    def counter(line,name):
        T(line,[name,':=',name,'+','1'],'H',f'Instrumentation counter {name}')
    if key=='P09a':
        D(8,n='H',cap='H',m='H',i='H',code='H',k='H',c='H',la='P',xv='P',loop1='H',conc1='H',conc2='H',rev1='H',rev2='H')
        D(9,xk='R')
        L(14,14,'R','Initialize explicit knownness of loop argument')
        L(21,21,'P','Read length of posed sequence')
        L(22,24,'P','Block and declarations for local cell encoding storage')
        L(26,29,'P','cons: construct an encoded sequence cell', 'METRICS 15; systems Values')
        L(31,44,'P','readseq: receive the posed sequence in cell encoding','METRICS 15; harness README 2.7: constants are P')
        L(46,57,'P','conc: forward transcription of its two cases')
        counter(50,'conc1');counter(54,'conc2')
        L(59,70,'P','rev: forward transcription with rev then conc')
        counter(63,'rev1');counter(67,'rev2')
        L(72,75,'P','loop: recursive self-call of its sole case')
        T(72,['xk'],'R','Extra knownness argument of loop')
        T(72,[',','found'],'R','Extra continuation argument of loop')
        T(73,['Boolean','xk',';'],'R','Extra knownness formal parameter')
        T(73,['procedure','found'],'R','Extra continuation formal parameter')
        counter(75,'loop1')
        T(75,['xk'],'R','Pass explicit knownness through recursion')
        T(75,[',','found'],'R','Pass continuation through recursion')
        L(77,92,'H','num: integer output adapter')
        L(94,103,'H','printseq: encoded sequence output adapter')
        L(105,111,'H','answera: loop answer output adapter')
        L(113,113,'P','Initialize the newly allocated cell encoding pointer','METRICS 15')
        L(114,114,'P','Pose encoded input sequence')
        L(119,119,'P','Query loop with unknown x')
        T(119,['xk'],'R','Extra knownness argument in loop query')
        T(119,[',','answera'],'R','Extra answer continuation in loop query')
        L(127,127,'P','Query rev in the forward direction')
        L(137,137,'P','Close block holding the local sequence encoding')
    elif key=='P09b':
        D(8,n='H',cap='H',m='H',i='H',code='H',k='H',c='H',c1='P',c2='P',c3='P',xv='P',yv='P',na='H',nb='H')
        D(9,xk='R',yk='R')
        L(11,17,'R','Procedural equality wrapper with knownness and continuation')
        T(15,['if','u','=','cv','then'],'P','Test fully known equality')
        T(15,['found'],'C','Invoke the next conjunct or answer after equality succeeds')
        T(17,['u',':=','cv'],'P','Evaluate unknown place of equality')
        T(17,['found'],'C','Invoke the next conjunct or answer after binding')
        T(17,['uk',':=','false'],'C','Restore knownness after the continuation','METRICS 1, 16')
        L(19,21,'H','answera: count and print an already computed solution')
        L(23,25,'R','seconda: continuation implementing the second conjunct')
        T(25,['xv',',','c2'],'P','Second equality operands')
        L(27,29,'H','answerb: count and print an already computed solution')
        L(34,34,'R','Initialize knownness of the two independent unknowns')
        L(41,41,'P','Read constants of the two computations')
        L(45,45,'R','Equality invocation with explicit knownness and continuation')
        T(45,['xv',',','c1'],'P','First equality operands')
        L(53,53,'R','Equality invocation with explicit knownness and continuation')
        T(53,['yv',',','c3'],'P','Independent B equality operands')
    elif key in ['P09c','P09d']:
        if key=='P09c':
            D(8,n='H',cap='H',m='H',i='H',code='H',k='H',g='P',cells='P')
            L(14,15,'P','Read gen input and allocate its finite sequence encoding')
            L(16,16,'P','Open block for the input-sized sequence encoding')
            D(17,top='P',s0='P',total='P',gen1='H',gen2='H',sum31='H')
            L(18,19,'P','Result of sum3 and encoded sequence storage')
            L(21,24,'P','cons: sequence cell construction','METRICS 15; systems Values')
            L(26,37,'P','gen: transcription of its two ordered cases')
            counter(30,'gen1'); counter(34,'gen2')
            L(39,50,'P','sum3: case head tests and sum of three elements')
            counter(47,'sum31')
            L(52,67,'H','num: integer output adapter')
            L(69,78,'H','printseq: sequence output adapter')
            T(80,['top',':='],'P','Initialize cell construction pointer')
            L(83,83,'P','Query first conjunct gen')
            L(84,84,'P','Query second conjunct sum3 after gen returns')
            L(101,101,'P','Close block for the sequence encoding')
        else:
            D(8,n='H',cap='H',m='H',i='H',code='H',k='H',g='P',top='P',s0='P',total='P',genu1='H',sum31='H')
            L(9,10,'P','sum3 result and finite cell encoding storage')
            L(12,15,'P','cons: sequence cell construction','METRICS 15; systems Values')
            L(17,25,'P','genu: recursive transcription of its sole case')
            counter(22,'genu1')
            L(27,38,'P','sum3: case head tests and sum of three elements')
            counter(35,'sum31')
            L(45,45,'P','Read genu input')
            T(46,['top',':='],'P','Initialize cell construction pointer')
            L(49,49,'P','Query first conjunct genu')
            L(50,50,'P','Query sum3 after genu returns')
    elif key=='P09e':
        c.declaration(8,dict(n='H',cap='H',m='H',i='H',code='H',k='H',c1='P',c2='P',xv='P',yv='P',held='H',x1='H',x2='H', **{'pass':'C'}))
        D(9,xk='R',yk='R',r1='R',r2='R',changed='C',inconsistent='R')
        for a,b,ct,case,full,fwd,back in [
            (11,21,'x1','R1',16,18,20), (23,33,'x2','R2',28,30,32)]:
            L(a,b,'R',f'{case}: hold relation and dispatch on known places')
            counter(a+3,ct)
            # The arithmetic verdict and each solved place are P even in
            # directions not exercised by this particular run (rule 19).
            if case=='R1':
                T(full,['if','xv','≠','yv','+','c1','then','inconsistent',':=','true'],'P','Test fully known R1')
                T(fwd,['yv',':=','xv','-','c1'],'P','Compute y from x in R1')
                T(back,['xv',':=','yv','+','c1'],'P','Compute x from y in R1')
            else:
                T(full,['if','yv','≠','xv','-','c2','then','inconsistent',':=','true'],'P','Test fully known R2')
                T(fwd,['yv',':=','xv','-','c2'],'P','Compute y from x in R2')
                T(back,['xv',':=','yv','+','c2'],'P','Compute x from y in R2')
            T(fwd,['changed',':=','true'],'C','Mark that another propagation pass may be needed')
            T(back,['changed',':=','true'],'C','Mark that another propagation pass may be needed')
        L(35,45,'R','Problem-specific propagation over R1 and R2 only','METRICS 19')
        L(38,41,'C','Repeat propagation passes until no binding changes')
        L(44,44,'C','End repeated propagation pass')
        L(47,50,'H','uname: unknown name output adapter')
        L(52,55,'H','place: relation place output adapter')
        L(57,65,'H','state: known or held place output adapter')
        L(67,77,'H','relations: print held conditions without evaluating them')
        L(84,84,'P','Read the two arithmetic constants')
        L(85,85,'R','Initialize explicit knownness and consistency state')
        L(87,87,'R','Retain both posed arithmetic relations')
        L(89,89,'R','Apply problem-specific relation holding/evaluation')
        L(92,92,'C','Suppress an answer if evaluation found inconsistency','METRICS 2, 10')
    elif key in ['P10a','P10c']:
        if key=='P10a':
            D(8,n='H',cap='H',m='H',i='H',code='H',k='H',e='P',b='P')
            D(9,bk='H')
            stage_lines=[22,25,28]
        else:
            D(8,n='H',cap='H',m='H',i='H',code='H',k='H',e='P',f='P',b='P',d='P')
            D(9,bk='H',dk='H')
            stage_lines=[22,25,28,31]
        for line in stage_lines:
            L(line,line,'P','Read stage constant and replace the named quantity natively')
            # These flags affect only rendering of the state, never computation.
            vals=[norm(c.rows[i]['token']) for i in c.byline[line]]
            for flag in ['bk','dk']:
                if flag in vals: T(line,[flag,':=','true'],'H','Output availability flag')
            # begin/end belong to message dispatch, not to the assignment.
            T(line,['end'],'H','Close stage message dispatch branch') if vals.count('end')==1 else None
    elif key=='P10b':
        D(8,n='H',cap='H',m='H',i='H',code='H',k='H',e='P',f='P',b='P',d='P',recomputed='H')
        D(9,bk='R',dk='R',r1='R')
        L(11,14,'R','Standing relation evaluator: wait for b to have a value')
        T(14,['d',':=','f','×','b'],'P','Evaluate d = f times b','METRICS 8, 19')
        counter(14,'recomputed')
        L(19,19,'R','Initialize knownness and retained standing relation')
        T(19,['recomputed',':=','0'],'H','Initialize recomputation counter')
        L(27,27,'R','Retain the standing relation when posed')
        # Input calls differ in syntax but their source lines are identical.
        if path.startswith('report/'):
            T(27,['ininteger','(','0',',','f',')'],'P','Read standing relation coefficient')
        else: T(27,['f',':=','read'],'P','Read standing relation coefficient')
        T(27,['end'],'H','Close stage message dispatch branch')
        for line in [30,33,36]:
            L(line,line,'P','Read constant and replace b natively')
            vals=[norm(c.rows[i]['token']) for i in c.byline[line]]
            if 'bk' in vals: T(line,['bk',':=','true'],'R','Record that b is known for standing relation evaluation')
            T(line,['end'],'H','Close stage message dispatch branch')
        L(38,38,'R','Re-evaluate the standing relation after each replacement')
    elif key=='P10d':
        D(8,n='H',cap='H',m='H',i='H',code='H',k='H',j='P',nf='P',c2='P',alive='H',tested='H')
        D(9,picked='R',r2='R',w2='H')
        # Array declaration: xv holds the stated facts, pk only counts them.
        L(10,10,'P','Array holding the facts of pick')
        T(10,[',','pk','[','1',':','1000',']'],'H','Per-fact operation counters')
        L(11,11,'R','Live-value flags for the problem-specific alternative store')
        L(13,22,'R','test: re-evaluate held alternatives against active comparison')
        L(17,17,'P','Visit each stated fact of pick','METRICS 6, 10')
        counter(20,'tested')
        T(20,['if','¬','(','xv','[','j',']','>','c2',')','then','xa','[','j',']',':=','false'],'P','Evaluate fully known comparison for a pick value','METRICS 19')
        L(24,35,'H','digits: output adapter for numbered case names')
        L(40,40,'R','Initialize active relation and fact-store flags')
        T(40,['w2',':='],'H','Initialize withdrawal display flag')
        T(40,['nf',':=','0'],'P','Initialize number of stated facts')
        T(40,['tested',':=','0'],'H','Initialize comparison operation counter')
        L(49,51,'P','Receive stated pick facts in order','METRICS 6, 15')
        T(51,['pk','[','j',']',':=','1'],'H','Count application of a stated pick fact')
        T(51,['end'],'H','Close input loop block')
        L(52,52,'R','Record that the pick facts have arrived')
        # Message-dispatch tokens stay H; only stage input and retained flag vary.
        if path.startswith('report/'):
            T(54,['ininteger','(','0',',','c2',')'],'P','Read comparison constant')
        else:T(54,['c2',':=','read'],'P','Read comparison constant')
        T(54,['r2',':=','true'],'R','Hold the comparison as active')
        T(56,['r2',':=','false'],'R','Withdraw comparison from problem-specific held store')
        L(58,58,'R','Recompute live values from retained facts and comparisons')
    else: raise AssertionError(key)
    return c.finish(),c.rows

TOKENS={}
ROWS={}
for path in TEXTS:
    TOKENS[path],ROWS[path]=classify(path)
    for alias in ALIASES[path]:
        assert (ROOT/'programs/algol-60'/alias).read_bytes()==(ROOT/'programs/algol-60'/path).read_bytes()
        other=list(csv.DictReader((ROOT/'results/algol-60/tokens'/f'{alias}.tokens.tsv').open(),delimiter='\t'))
        assert other==ROWS[path], (path,alias)

def records():
    for conf in ['report','x1','x1sim']:
        for prob in ['P09','P10']:
            for folder in ['raw','raw-rerun-m2']:
                for p in sorted((ROOT/'results/algol-60'/conf/prob/folder).glob('*.json*')):
                    import gzip
                    with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:
                        yield str(p.relative_to(ROOT)),json.load(f)

RECORDS=list(records())

def classify_stage(path,r,s,a,c,reading=None):
    run=r['run']; sub=run['subproblem']; k=s['stage']; comp=c['id']
    state=c['execution_state']; reached='not started' not in state['basis'].lower()
    replay_notes=' '.join(a.get('notes',[]))
    if 'did not reach' in replay_notes.lower() or 'not reached' in replay_notes.lower(): reached=False
    answers=[v['verbatim'] for q in c['queries'] for v in q['answers']]
    raw=a['observe']['raw']
    semantic='complete' if answers else 'none reported'
    representation='explicit' if answers else None
    equivalence=None
    simplification=identical=size=None
    comment=''
    unknowns='No unknown remains in the reported values.'
    if sub=='P09a':
        comment='Spawns are serial (side_by_side=false). B completes only when started before A; no B outcome while A runs. Order therefore matters.'
        if comp=='A':
            unknowns='x is represented by integer xv plus Boolean xk=false; no binding is reported before the stop.'
        elif reached:
            equivalence='The sole reported b=(3,2,1) is exactly the reversal of the posed (1,2,3).'
    elif sub=='P09b':
        comment='A finishes with no solution; its logical failure does not prevent B from starting and reporting y=3. Knownness is restored after each continuation.'
        if comp=='A':
            semantic='complete';representation='explicit'
            equivalence='The explicitly observed no-solution result is exact: x=1 and x=2 have no common value.'
        else: equivalence='The sole equality y=3 has exactly the reported solution.'
        unknowns='Unknowns use integer value slots and Boolean knownness flags; temporary values are passed to answer continuations.'
    elif sub=='P09c':
        equivalence='By induction gen(1) constructs (1,2,3,4,5); sum3 tests three cells and computes 1+2+3=6. These are exactly the valid outcomes.'
        comment='The observation explicitly states gen ran to its end, then sum3 began. There is no consumer progress before producer completion.'
    elif sub=='P09d':
        semantic='none reported';representation=None
        unknowns='No s or total binding is observable. Eager recursion calls genu(n+1) before allocating a cell and never reaches sum3 in the transcription.'
        comment=('Finite least-relation reading: no finite sequence satisfies genu. Nothing was reported, so no claim of successful failure or completion is inferred.' if reading=='finite' else 'Greatest-relation stream reading requires total=6 while the producer runs. No total binding was reported, so the result is none reported, rather than unsound or partial.')
    elif sub=='P09e':
        semantic='complete';representation='residual';simplification='reducible';identical=True
        size={'input':{'primitive_relations':2,'unknown_occurrences':4},'residual':{'primitive_relations':2,'unknown_occurrences':4},'smaller_equivalent':{'primitive_relations':1,'unknown_occurrences':2}}
        equivalence='Over the problem integer domain, y=x-1 iff x=y+1. Their conjunction is exactly {(t+1,t): t is an integer}. One redundant relation can be deleted; no enumeration or finite bound is imposed.'
        unknowns='xv/yv integer slots with xk=yk=false; r1/r2 retain both equations, not placeholder values.'
        comment='Both relations wait for a known place; each is examined once. The reported suspended count is 2, distinguishable from completion. It is problem-specific holding, not a native ALGOL suspension. Although the process ends, these are the relation records evaluated by propagate and printed by observe.'
    elif sub=='P10a':
        equivalence=f'Native replacement gives b={[10,15,7][k-1]}, exactly the current named quantity.'
        comment='b is overwritten in one variable. Earlier values are not retained; no version indexing is used.'
    elif sub=='P10b':
        if k==1:
            semantic='complete';representation='residual';simplification='reduced';identical=True
            size={'input':{'primitive_relations':1,'unknown_occurrences':2},'residual':{'primitive_relations':1,'unknown_occurrences':2}}
            equivalence='The retained coefficient f=2 and active relation r1 denote precisely d=2*b with neither quantity valued. Neither an equation nor an unknown occurrence can be removed while preserving that arithmetic dependency.'
            unknowns='b and d have integer slots with bk=dk=false; r1 holds the standing dependency, not arbitrary initial values.'
            comment='One held relation is suspended awaiting b. d has been recomputed zero times, as an actual observed operation count.'
        else:
            equivalence=f'Current b={[10,15,7][k-2]} and d={[20,30,14][k-2]} satisfy the standing equation and the current replacement exactly.'
            comment=f'One dependent quantity d is recomputed after this replacement; cumulative recomputations={k-1}. The standing relation is still held although its current values are explicit. Earlier b/d values are overwritten.'
    elif sub=='P10c':
        equivalence='b is 10,15,7 at the relevant replacing stages. d has no value at stage 1; stage 2 computes d=2*10=20 once, and subsequent stages preserve d=20.'
        comment='A native assignment snapshot, with no standing relation. Earlier overwritten values are not retained.'
        if k==1: unknowns='d is a named quantity not yet assigned, represented by dk=false; it is not a free logical unknown or a pending arithmetic relation.'
    elif sub=='P10d':
        vals=[1,2,3] if k!=2 else [2,3]
        equivalence=f'The retained pick facts are exactly 1,2,3; testing active x>1 yields 2,3 and disabling that test restores all three. Stage {k} therefore denotes exactly {vals}.'
        comment='All surviving values are held simultaneously as xv[j] with xa[j]=true, not as a backtracking continuation. The query has printed all of them and finishes; retained data is not alternatives pending.'
        unknowns='x is represented by the finite facts stated by the problem, not an imposed finite integer domain.'
        if k==2: comment+=' The earlier x=1 outcome is absent from the new answer set; no separate withdrawal event is printed.'
        if k==3: comment+=' x=1 returns without re-input of pick: r2=false disables the retained comparison; observe explicitly prints it as withdrawn.'
    if not reached:
        semantic=representation=simplification=identical=size=equivalence=None
        unknowns='This computation never started; its state is unavailable.'
    withdrawal=None
    if sub=='P10a' and k>1: withdrawal=f'b={[10,15][k-2]} is replaced by b={[15,7][k-2]}; the new answer and bind overwrite the old value.'
    if sub=='P10b' and k>2: withdrawal='Earlier b and its derived d are replaced; new explicit answers/bindings show the replacement.'
    if sub=='P10c' and k>2: withdrawal='Earlier b is replaced; snapshot d=20 is preserved.'
    if sub=='P10d' and k==2: withdrawal='x=1 is removed from the reported current set.'
    if sub=='P10d' and k==3: withdrawal='Constraint x>1 is explicitly marked withdrawn; x=1 is restored.'
    obs={
        'answers_verbatim':answers,'observe_verbatim':raw,
        'observe_scope':'The raw observe block and parsed bindings are attempt-wide. For spawned computations they can include the other computation; only answers_verbatim and this entry execution_state classify the named computation.',
        'bindings':a['observe']['bindings'], 'unknowns_representation':unknowns,
        'alternatives':c['alternatives'], 'suspended':c['suspended'],
        'conclusion_withdrawn':withdrawal, 'manual_actions':a['manual_actions']+r['manual_actions'],
        'coordination_or_state':comment, 'posed':a['posed'],
        'metrics':{'steps':c['steps'],'problem_operations':c['problem_operations'],'store':a['store']},
        'measurement_note':'Null figures are unavailable, never zero. Boundary live store is unavailable after interpreter unwinding; only recorded peaks/totals are evidence. x1sim has no cost or storage mode.',
        'execution_basis':state['basis'], 'error_verbatim':state['error_verbatim'],
        'safety_limit':a['safety_limit'], 'exit':a['exit'], 'attempt_notes':a.get('notes',[])
    }
    if sub=='P09a' and run['configuration']=='x1sim' and a['attempt']==2:
        obs['retry_note']='Raised-limit retry ended with SIGKILL after about 69 seconds; safety_limit.hit=false and record classifies error with no stderr. Cause of the kill is not established by the record; do not reinterpret it as an exhausted 600-second limit.'
    result={'configuration':run['configuration'],'instance':run['instance'],'program':Path(run['program']['path']).name,'record':path,'stage':k,'attempt':a['attempt'],'final_attempt':a is s['attempts'][-1], 'computation':comp,'reading':reading,'reached':reached,'semantic':semantic,'representation':representation,'simplification':simplification,'identical_to_posed':identical,'residual_size':size,'execution_state':state['states'] if reached else [],'residual_equivalence':equivalence,'observations':obs,'rule':'SPECIFICATION Outcomes 1–3; problem valid outcomes; AMENDMENTS 3.1–3.4','harness_fault':'.INVALID.' in path or bool(r['harness_faults'])}
    if not reached:
        result['not_reached_because']=state['basis']
        result['rule']='AMENDMENTS 3.2; harness ALGOL 60 A3: earlier spawned computation stopped the instance'
    return result

def classified(path,r):
    result=[]
    for s in r['stages']:
        for a in s['attempts']:
            for c in a['computations']:
                for reading in (['finite','stream'] if r['run']['subproblem']=='P09d' else [None]):
                    result.append(classify_stage(path,r,s,a,c,reading))
    return result

OUTCOMES=[]
BEHAVIOUR={}
for path,r in RECORDS:
    if r['run']['mode']=='behaviour':
        items=classified(path,r)
        OUTCOMES.extend(items)
        BEHAVIOUR[(r['run']['configuration'],r['run']['instance'],r['run']['program']['path'])]=items

DIFFERENCES=[]
axes=['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence']
for path,r in RECORDS:
    if r['run']['mode']=='behaviour': continue
    base=BEHAVIOUR[(r['run']['configuration'],r['run']['instance'],r['run']['program']['path'])]
    current=classified(path,r)
    assert len(base)==len(current)
    for b,x in zip(base,current):
        assert (b['stage'],b['computation'],b['reading'])==(x['stage'],x['computation'],x['reading'])
        # The generated semantic reasoning is independent of measurement mode.
        if any(b[f]!=x[f] for f in axes):
            DIFFERENCES.append({'configuration':x['configuration'],'instance':x['instance'],'program':x['program'],'mode':r['run']['mode'],'record':path,'stage':x['stage'],'computation':x['computation'],'reading':x['reading'],'behaviour':{f:b[f] for f in axes},'this_mode':{f:x[f] for f in axes},'note':'Mode classification disagrees with behaviour; instrumentation fault.'})
        # Also compare underlying reported values, observe and states so a
        # reasoning template cannot hide a changed answer.
        assert b['observations']['answers_verbatim']==x['observations']['answers_verbatim'],path
        assert b['observations']['observe_verbatim']==x['observations']['observe_verbatim'],path

EXPRESS=[]
for conf in ['report','x1','x1sim']:
    judgements=[
        ('P09a','loop(x), x unknown','expressible','The sole recursive self-call is a transcription. Extra knownness/continuation arguments are incidental R constructs; they do not provide concurrency or produce an answer. Failure to reach B in AB is operational, not failure to state the relation.'),
        ('P09a','rev(a,b), known a to b','expressible','The two ordered rev cases and forward conc cases are transcribed using the systems-file cell encoding (P, rules 3 and 15). Serial spawn is the fixed harness contract; no concurrency is credited.'),
        ('P09a','conc(a,b,c), known a,b to c','expressible','Forward recursion preserves each conc case and presentation order, rules 3 and 15.'),
        ('P09b',None,'expressible with reformulation','The supplied equality wrapper represents knownness and passes a continuation for the next conjunct, with R arguments and dispatch. It tests/binds the two primitive equalities and reports the independent equality without a general unifier or search mechanism.'),
        ('P09c','gen(n,s), n to s; sum3(s,total), s to total','expressible','Each function follows the problem cases in the queried direction (rules 2,3,15), in gen-then-sum3 order. Producer completion before consumption limits coordination but does not change the finite relation.'),
        ('P09d1','genu(n,s), finite least relation; sum3 forward','expressible','The eager recursive transcription has no finite successful derivation, as does genu in the finite reading. Its budget/error is an execution result and does not assert that total=6 is valid.'),
        ('P09d2','genu(n,s), greatest-relation stream; sum3 prefix','not expressible','The supplied eager finite-cell transcription cannot expose the infinite stream or let sum3 compute total before genu returns. No equivalent stream reformulation is supplied; a lazy/demand or scheduling mechanism would be needed for this program. This judgement is about the provided definitions/representations, not a claim of computational impossibility for ALGOL.'),
        ('P09e',None,'expressible with reformulation','Two problem-specific retained arithmetic equations and knownness bits preserve the integer relation; evaluators are split P/R by rule 19. The hard-wired propagation loop is not general over relations, hence R/C rather than S.'),
        ('P10a',None,'expressible','Native assignment directly transcribes absolute/relative replacement, preserving pre-stage evaluation of the right side.'),
        ('P10b','standing d from current b','expressible with reformulation','An active relation flag, knownness and an evaluator called after every replacement maintain the dependency. Holding and tests are R (19); multiplication is P (8,19).'),
        ('P10c',None,'expressible','Native assignments implement a single snapshot and later replacements. Availability flags affect only output.'),
        ('P10d',None,'expressible with reformulation','The facts are stored unchanged (P,6), with active-comparison and live-value flags and rescanning (R,19). Disabling the held comparison restores the retained facts without restating them. The finite set is the stated pick domain, not an imposed search interval.')]
    for sub,direction,ex,reason in judgements:
        EXPRESS.append({'configuration':conf,'subproblem':sub,'direction':direction,'expressibility':ex,'reason':reason})

S_MECHANISMS=[]
for conf in ['report','x1','x1sim']:
    for path in TEXTS:
        if not path.startswith(('report/' if conf=='report' else 'x1/')):continue
        names=[Path(path).name]+[Path(a).name for a in ALIASES[path] if a.startswith(conf+'/')]
        for name in sorted(set(names)):
            S_MECHANISMS.append({'configuration':conf,'program':name,'mechanism':'none','listed_at_phase_4':True,'tokens':0,'token_ranges':[],'reason':'Phase-4 S-mechanisms.md lists none. Problem-specific knownness, relation holding and rescanning are R under rule 19; output adapters are H under 13. No general scheduler, search, unifier or propagator is supplied.'})

DATA={'tokens':TOKENS,'outcomes':OUTCOMES,'mode_differences':DIFFERENCES,'expressibility':EXPRESS,'late_definition':[],'s_mechanisms':S_MECHANISMS}

def validate():
    totals=Counter()
    stages=json.loads((ROOT/'harnesses/stages.json').read_text())
    expected_structure={}
    for problem in stages['problems']:
        if problem['problem'] not in ['P09','P10']:continue
        for sub in problem['subproblems']:
            for instance in sub['instances']:
                expected_structure[instance['id']]=sub['stages']
    for path,spans in TOKENS.items():
        covered=[]
        for span in spans:
            assert span['class'] in 'PCRSH'
            assert span['from']<=span['to']
            covered.extend(range(span['from'],span['to']+1))
            totals[span['class']]+=span['to']-span['from']+1
        assert covered==list(range(len(ROWS[path]))),path
    # Reconcile all log job tuples against the actual raw records.
    logged=[]
    for conf in ['report','x1','x1sim']:
        for prob in ['P09','P10']:
            for line in (ROOT/'results/algol-60/logs'/f'1C-{conf}-{prob}.tsv').read_text().splitlines():
                fields=line.split('\t'); logged.append(tuple(fields[1:5]))
    actual=[(r['run']['configuration'],r['run']['instance'],Path(r['run']['program']['path']).name,r['run']['mode']) for _,r in RECORDS]
    assert Counter(logged)==Counter(actual),(logged,actual)
    assert len(TEXTS)==18 and len(BEHAVIOUR)==30 and len(RECORDS)==70
    # Independently check actual outputs, not merely agreement between modes.
    # This parses answer formatting only; it never tokenizes an ALGOL program.
    def canonical(s):
        s=re.sub(r'\s+','',s)
        return s.replace('=+','=').replace('++','+').replace('-+','-')
    for path,r in RECORDS:
        run=r['run']; program=ROOT/run['program']['path']
        structure=expected_structure[run['instance']]
        assert [s['stage'] for s in r['stages']]==[s['stage'] for s in structure],path
        for actual_stage,expected_stage in zip(r['stages'],structure):
            for attempt in actual_stage['attempts']:
                expected_computations={q['computation'] for q in expected_stage['queries']}
                assert {c['id'] for c in attempt['computations']}==expected_computations,path
        assert hashlib.sha256(program.read_bytes()).hexdigest()==run['program']['sha256'],path
        constants=ROOT/run['constants']['input_path']
        assert hashlib.sha256(constants.read_bytes()).hexdigest()==run['constants']['input_sha256'],path
        stage_constants={}
        for line in constants.read_text().splitlines():
            if not line.strip():continue
            stage,values=line.split(':',1)
            stage_constants.setdefault(int(stage),[]).extend(map(int,values.split()))
        sub=run['subproblem']
        for s in r['stages']:
            k=s['stage']
            for a in s['attempts']:
                for c in a['computations']:
                    got=[canonical(v['verbatim']) for q in c['queries'] for v in q['answers']]
                    reached='not started' not in c['execution_state']['basis'].lower()
                    expected=[]
                    if reached:
                        if sub=='P09a' and c['id']=='B':
                            seq=stage_constants[1][1:]
                            expected=['b=('+','.join(map(str,reversed(seq)))+')']
                        elif sub=='P09b':
                            first,second,independent=stage_constants[1]
                            if c['id']=='A':
                                expected=[f'x={first}'] if first==second else []
                                if first!=second:assert 'no solution' in a['observe']['raw']
                            else:expected=[f'y={independent}']
                        elif sub=='P09c':
                            seq=list(range(stage_constants[1][0],6))
                            if len(seq)>=3: expected=['total='+str(sum(seq[:3]))+',s=('+','.join(map(str,seq))+')']
                        elif sub=='P09e':
                            c1,c2=stage_constants[1]
                            expected=[f'xheld,yheld,wherex=y+{c1},y=x-{c2}']
                        elif sub=='P10a':
                            b=stage_constants[1][0]
                            if k>=2:b+=stage_constants[2][0]
                            if k>=3:b=stage_constants[3][0]
                            expected=[f'b={b}']
                        elif sub=='P10b':
                            f=stage_constants[1][0]
                            if k==1:expected=[f'bheld,dheld,whered={f}.b']
                            else:
                                b=stage_constants[2][0]
                                if k>=3:b+=stage_constants[3][0]
                                if k>=4:b=stage_constants[4][0]
                                expected=[f'b={b},d={f*b}']
                        elif sub=='P10c':
                            initial=stage_constants[1][0];b=initial
                            if k>=3:b+=stage_constants[3][0]
                            if k>=4:b=stage_constants[4][0]
                            expected=[f'b={b},dhasnovalue' if k==1 else f'b={b},d={stage_constants[2][0]*initial}']
                        elif sub=='P10d':
                            values=stage_constants[1][1:]
                            assert len(values)==stage_constants[1][0]
                            if k==2:values=[x for x in values if x>stage_constants[2][0]]
                            expected=[f'x={x}' for x in values]
                    assert got==expected,(path,k,c['id'],got,expected)
    return totals

TOTALS=validate()
(OUT/'algol-60.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2)+'\n')
final=[o for o in OUTCOMES if o['final_attempt']]
table=['| Frozen text (first path) | P | C | R | S | H | Total |','|---|---:|---:|---:|---:|---:|---:|']
for path,spans in TOKENS.items():
    count=Counter()
    for span in spans:count[span['class']]+=span['to']-span['from']+1
    table.append('| '+path+' | '+' | '.join(str(count[cl]) for cl in 'PCRSH')+' | '+str(sum(count.values()))+' |')
notes='''# Independent classifier B: ALGOL 60, batch 1C, P09/P10

I did not write these programs and did not consult another classifier's work.
The source clone was read only. Only this output directory was written. No
ALGOL program, interpreter, compiler, harness, qualification, or system was run.
The Python checking script reads the frozen token tables and the permitted
evidence; it never re-tokenizes a program.

## Evidence and coverage

The first paths in `TEXTS-1C-P09-P10.tsv` identify 18 distinct texts.
The script checks that every alias has identical program bytes and identical
frozen token rows. The report AB/BA texts share one classification. The X1
texts also cover x1sim, and its AB/BA aliases. No class changes with the
configuration: X1 output/input calls are its own procedures; the report
IFIP procedures are external mechanisms, but their token classes still
follow their role (constant input P, harness words and output adapters H).

There are 30 behaviour records and 40 measurement records: 20 cost and
20 storage. The six permitted batch-1C job logs reconcile exactly with
those 70 record jobs. The older batch log and measurement-rerun log contain
no P09/P10 jobs, and the permitted P09/P10 measurement-rerun directories
contain no records. There are no INVALID records, harness_faults entries,
named variants, or P08 programs in this assignment. `late_definition` is
therefore empty. Every program has an explicit zero-S entry.

The JSON uses the logged instance `P09d` plus a `reading` field for its
two judgements, rather than inventing two runs. Spawned computations have
separate entries. Both safety attempts are preserved with `attempt` and
`final_attempt`; use the latter for final outcomes. There are 76 entries
including retries and both readings, or 72 final entries. An unreached
computation has `reached:false`, null outcome axes, no execution state of
its own, and the stopping explanation. It is not counted as its own error.
Observe blocks are attempt-wide; a B binding in P09a.BA is not an A answer.

## Difficult token decisions

* Sequence cell construction, decomposition, input assembly and its storage
  are P (systems Values; rules 3 and 15). Forward conc/rev/gen and sum3
  follow the given cases. The recursive call before the constructor in
  genu is P; it is not an added fairness directive or an omitted base case:
  the problem itself gives no base case. The initial top=0 in a newly
  allocated local encoding is P, not a store-reuse reset (16).
* The unused knownness and continuation arguments of loop are still extra
  arguments (R, 3/5), although they do not explain its nontermination.
  This incidental R does not make the recursive relation itself
  inexpressible. Argument punctuation follows the following argument (20).
* P09b's scalar `equals` wrapper is the hardest boundary. I class the
  extra knownness/continuation wrapper R; binding a place and comparing
  fully known equality are P; invoking the selected continuation is C;
  restoring its temporary knownness is C. It implements this problem's
  scalar equality/conjunction, not a general structured-value unifier,
  relation store, or search engine. I therefore find no S mechanism.
  I record the supplied equality implementation as expressible with
  reformulation; a more direct native assignment/test transcription would
  make a defensible expressibility disagreement here.
* P09e has hard-coded evaluators for two equations. All arithmetic
  evaluations and the fully known tests are P in BOTH directions (19),
  even though this run reaches none of them. Known-place dispatch and
  relation retention are R. Convergence flags and the repeated-pass loop
  are C. `propagate` is R/C rather than S: it cannot accept an arbitrary
  relation or evaluator. Its procedure name does not decide its class.
* P10b's active standing relation, knownness and re-evaluation call are R;
  the multiplication is P. Its recomputation counter is H. P10a/P10c
  availability flags are H because only output reads them: no evaluator
  waits on them. This differs from P10b's bk flag, which gates computation.
* P10d's fact input and traversal of facts are P (6), not a generator of
  unstated integers. Live-value and comparison-activity storage is R (19).
  Testing the fully known comparison is P. Disabling its activity is R,
  and the withdrawal-display flag is H. Traversal purely for output, case
  numbering and operation counters is H (13 and harness 2.7).
* Pure printers, including branches and decimal-digit arithmetic wholly
  inside num/digits/printseq, are H (13). Tests that suppress an inconsistent
  computed outcome are separately C under rule 2. Semicolon separators
  follow the next construct (20), including at changes of class. Introducers
  and nested statements follow rule 10 rather than inheriting a surrounding
  relation-holder's class without examination.

The phase-4 S list supplies no mechanisms in any configuration. I found no
program-supplied mechanism general over relations. The R/C mechanisms are
still charged in full; they are not credited as native suspension,
propagation, retraction of logical facts, or concurrency.

## Outcomes and equivalence

* P09a: in report/x1, A reaches budget. In AB, B never starts; in BA,
  B explicitly reports (3,2,1) before A starts. B does not progress while
  A runs. The X1 simulator has no enforced step budget. Its first attempts
  time out at 60 seconds. The 600-second retries actually end after about
  69 seconds with SIGKILL, no error text and `safety_limit.hit:false`.
  I preserve the recorded error, not a conjectured second timeout, and
  cannot determine the kill's cause from these records. Both retries
  retain the same order-sensitive B result.
* P09b: A explicitly observes no solution, so this is complete/explicit
  for the empty set, not none reported. B independently reports y=3.
  Logical failure is isolated; a process-ending stop in P09a is not.
* P09c: the observation states that gen finished before sum3 began.
  Induction on gen's cases gives (1,2,3,4,5); the sole sum3 case gives 6.
  The explicit outcome is exact, with no producer/consumer overlap.
* P09d: no s or total is observed in any configuration. Report/x1 exhaust
  budget; x1sim reports `Error: Wrong result type in TIRD\\n`.
  Under the finite reading genu has no finite instances, but the run does
  not report successful exhaustion or no solution: none reported. Under
  the stream reading no total=6 is exposed either: also none reported.
  No finite-domain partial-result inference is warranted: no cell is
  constructed before the recursive call returns, and no answer is given.
* P09e: a genuine problem-specific pair of executable held equations is
  read by observe, not just a literal echo. Its residual is exactly the
  posed information, complete and reducible, with two primitive relations
  and four occurrences of unknowns. Algebraically y=x-1 iff x=y+1 over
  the integer domain. Thus its solutions are exactly (t+1,t), and one
  equation can be removed, reducing the size to one relation/two
  occurrences. No finite interval or enumeration is used. The suspended
  count is two held equations; each was examined once. ALGOL's process
  ending does not turn the reported waiting relation state into a solved
  form or a native suspension facility.
* P10a: b=10,15,7. P10b first holds d=2*b, then reports (b,d)=(10,20),
  (15,30),(7,14). The first stage is complete/reduced/residual, identical
  to the posed one primitive relation with two unknown occurrences.
  Arithmetic expressions are not solved-form term constructors under
  the specification. Later stages have explicit valid values and keep
  the standing relation as an observation. Exactly one dependent value
  is recomputed per replacement; cumulative counts are 0,1,2,3.
* P10c: b=10 with d unassigned, then (10,20),(15,20),(7,20). d is a
  named quantity with no value at stage 1, not a free logical variable
  or an unsolved multiplication. Assignments preserve its snapshot.
* P10d: all 1,2,3 are held, then 2,3, then 1,2,3. The facts remain
  stored when their live flags change; withdrawing the comparison does
  not require re-input of pick. The comparison withdrawal is printed.
  The new answer set omits x=1 at stage 2; there is no separate explicit
  cancellation event for that prior answer. Retained live data after
  printing every answer is not `alternatives pending`: asking for more
  answers does not resume an unfinished enumeration. The explicit set
  is the problem's stated finite set, not an imposed finite domain.

All P10 replacements overwrite ordinary variables; no older value can be
retrieved from a version history. The records contain no manual actions.
The report/x1 harness recreates prefixes for budgets and validates identical
prefix output; x1sim receives the stages in one live process. I preserve
those confounds rather than attributing recreation to the program.

For every cost/storage run the checker compares actual answer strings,
observe blocks, execution classifications and semantic/representation axes
with behaviour, as well as independently computing expected reported values
from the permitted constants. All agree. `mode_differences` is empty.
Null measurements remain unavailable. No unmeasured suspended/alternative
count is silently changed to zero; exact held-relation counts are used only
where printed. After a stop, missing bindings are not inferred from source.

## Ambiguities and limits of these judgements

Rules 1/2, 3 and 19 leave a narrow boundary between imperative continuation
scaffolding and a transcription of equality/conjunction. My split above is
explicit, so another classifier can disagree without losing the P evaluator
inside R code. The special H treatment of output adapters also makes their
fairly large decimal-printer bodies H; I apply that frozen rule consistently.

The definition of a residual says the program holds and acts on its state
"at a later stage". Read literally as requiring an actually occurring later
stage, it would reject the specification's own single-stage residual examples
as well as P09e. I read it as requiring genuine held/evaluable state, rather
than a printed copy of the question. P09e has knownness bits, relation flags,
evaluators, a propagation pass and observe access to those same flags and
constants. Its one-stage execution is reported as such; no later resumption
is claimed. P10b also demonstrates actual evaluation at subsequent stages.

Expressibility is kept separate from producing an answer within a limit.
In particular, eager recursion can transcribe a finite least relation even
when it gives no answer. My P09d2 `not expressible` judgement is relative to
the provided eager finite-sequence transcription: it does not express the
greatest-relation stream or expose its total. This is the most contestable
expressibility judgement. A problem-specific prefix/stream representation
could instead be proposed as reformulation; no such program or R tokens
are present here. I do not infer a theorem that ALGOL cannot implement it.
No inaccessible hidden variants were consulted, so expressibility claims
about generic constants are based on the supplied algorithms and input
contract, not on any claimed hidden-variant pass.

I identify no frozen rule that should be silently replaced or changed. The
points above are readings that should remain visible in a disagreement.

## Files read and access discipline

No file outside the user's permitted list was read, accidentally or
otherwise. In particular, no calibration, reviews, variants, transcripts,
earlier classifications, result summaries, author README/audits, other
system folders, private directories, skills, or web sources were opened.
Permitted README/specification text contains links naming some excluded
locations; none was followed.

Evidence read: README.md, SPECIFICATION.md, METRICS.md, PROTOCOL.md,
AMENDMENTS.md; the six permitted problems files; systems/algol-60/README.md;
harnesses/README.md, stages.json and record.schema.json; the ALGOL harness
README, S-mechanisms and QUESTIONS; the P09/P10 program and constants files
in report/x1/x1sim; their frozen token tables and TEXTS manifest; all 70
permitted P09/P10 raw records; the six corresponding batch-1C log files,
and the two permitted older/measurement-rerun logs filtered to these
problems. Listing the permitted systems/harness subtree revealed filenames
only; no qualification programs or records were executed. Files created
and subsequently read here are classify.py, algol-60.json and these notes.

## Totals

'''
notes+='\n'.join(table)+'\n\n'
notes+=f"Unique-text tokens: P={TOTALS['P']}, C={TOTALS['C']}, R={TOTALS['R']}, S={TOTALS['S']}, H={TOTALS['H']}; total={sum(TOTALS.values())}. Every index is covered exactly once.\n\n"
notes+='Final outcomes (72 entries, separate computations and both P09d readings): 57 complete, 12 none reported, 3 not reached; 51 finished, 8 budget, 6 suspended, 4 error, plus the 3 unreached computations. Six residuals are equivalent: three reducible P09e residuals and three reduced P10b stage-1 residuals. The four additional first-attempt entries preserve two timeouts, one complete B outcome and one unreached B. There are no mode differences, no S tokens, and no manual actions.\n'
(OUT/'algol-60.notes.md').write_text(notes)
print(json.dumps({'texts':len(TOKENS),'token_totals':dict(TOTALS),'records':len(RECORDS),'behaviour_runs':len(BEHAVIOUR),'outcome_entries':len(OUTCOMES),'mode_differences':len(DIFFERENCES),'s_mechanisms':len(S_MECHANISMS),'semantic_all_attempts':dict(Counter(x['semantic'] or 'not reached' for x in OUTCOMES))},indent=2))
