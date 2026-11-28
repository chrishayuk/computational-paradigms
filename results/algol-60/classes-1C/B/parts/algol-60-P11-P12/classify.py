"""Independent classification. Reads only the paths authorized in the brief.
Never executes an ALGOL program or a repository tool; uses frozen token rows.
"""
from pathlib import Path
from collections import defaultdict, Counter
import csv, json, re, gzip, hashlib

ROOT = Path('.')
OUT = Path('results/algol-60/classes-1C/B/parts/algol-60-P11-P12')
RULE = {
 'P':'METRICS rules 1, 3, 6, 15; systems/algol-60 Values',
 'C':'METRICS rules 1, 2, 10 (explicit traversal/termination control)',
 'R':'METRICS rule 19 (problem-specific holding); rule 10',
 'S':'P12 Rules: a search written by hand is supporting code; METRICS rules 10, 12',
 'H':'METRICS rule 13; harnesses/algol-60/README 2.7',
}

manifest = list(csv.DictReader((ROOT/'results/algol-60/tokens/TEXTS-1C-P11-P12.tsv').open(),delimiter='\t'))
aliases = {}
for row in manifest:
    aliases[row['text']] = [row['text']] + row['also the text of'].split()

class Text:
    def __init__(self, key):
        self.key=key
        self.rows=list(csv.DictReader((ROOT/'results/algol-60/tokens'/(key+'.tokens.tsv')).open(),delimiter='\t'))
        assert [int(x['index']) for x in self.rows] == list(range(len(self.rows)))
        self.lines=defaultdict(list)
        for i,r in enumerate(self.rows): self.lines[int(r['line'])].append(i)
        self.a=[None]*len(self.rows)
    def put(self, ids, cls, name, rule=None):
        for i in ids:self.a[i]=(cls,name,rule or RULE[cls])
    def line(self, n, cls, name, rule=None):self.put(self.lines[n],cls,name,rule)
    def lineset(self, lo, hi, cls, name, rule=None):
        self.put([i for n in range(lo,hi+1) for i in self.lines[n]],cls,name,rule)
    def part(self,n,lo,hi,cls,name,rule=None):self.put(self.lines[n][lo:hi],cls,name,rule)
    def declaration(self,n,roles):
        ids=self.lines[n]; toks=[self.rows[i]['token'] for i in ids]
        # Split the frozen declaration at its existing commas, never tokenize source.
        starts=[0]+[i for i,t in enumerate(toks) if t==',']
        for a,b in zip(starts,starts[1:]+[len(ids)]):
            names=[t for t in toks[a:b] if t in roles]
            assert names,(self.key,n,toks[a:b])
            cls=roles[names[0]]
            self.put(ids[a:b],cls,'declaration of '+', '.join(names))
    def finish(self):
        assert all(x is not None for x in self.a),(self.key,[i for i,x in enumerate(self.a) if x is None])
        # Separators between constructs belong to the following construct.
        for i in range(len(self.a)-2,-1,-1):
            if self.rows[i]['token'] in [';',','] and self.a[i][:2]!=self.a[i+1][:2]:
                c,n,r=self.a[i+1];self.a[i]=(c,n,r+'; METRICS rule 20')
        spans=[]
        for i,x in enumerate(self.a):
            if spans and spans[-1]['class']==x[0] and spans[-1]['construct']==x[1] and spans[-1]['rule']==x[2]:
                spans[-1]['to']=i
            else:spans.append({'from':i,'to':i,'class':x[0],'construct':x[1],'rule':x[2]})
        return spans

def p11(t, letter):
    staged=letter in 'cd'
    t.line(1,'P','program block')
    roles={x:'H' for x in ['n','cap','m','i','code','k','untried']}
    roles.update({x:'P' for x in ['nf','c','c2','c3','xv','cv']})
    roles.update(j='C',cur='R' if staged else 'C')
    t.declaration(8,roles)
    t.declaration(9, {x:('R' if staged else 'C') for x in ['ok','picked','xk','r2','r3','committed']})
    t.declaration(10,{'fv':'P','pk':'H'})
    if not staged:
        t.lineset(12,27,'H','num: decimal output adapter')
        t.lineset(28,32,'H','emit: fixed effect-stub binding')
        for n in [35,36,37]:t.line(n,'H',f'harness input, line {n}')
        t.line(39,'P','read pick fact count')
        t.line(40,'P','read the stated pick facts in order')
        ids=t.lines[40];start=next(i for i in ids if t.rows[i]['token']=='pk')
        end=next(i for i in ids if i>start and t.rows[i]['token']=='end')
        t.put(range(start,end),'H','initialize pick operation counter')
        t.line(41,'P','read comparison constant')
        t.line(44,'C','initialize traversal and success flag')
        t.line(45,'C','try facts until first successful conjunction')
        t.line(46,'C','fact traversal block')
        t.line(47,'C','advance fact cursor')
        t.part(47,6,None,'H','increment pick operation counter')
        t.line(48,'P','pick fact binds x')
        if letter=='a':
            t.line(49,'P','test x >= c: stated conjunct','METRICS rule 2: test is exactly the problem condition; rule 10')
            t.line(50,'P','successful stated test branch')
            t.line(51,'P','emit(x): problem effect','P11 Rules: emit is P; METRICS rule 10')
            t.line(52,'C','stop after a successful any-one conjunction')
            t.line(53,'P','close stated test branch')
            t.line(54,'C','close fact traversal')
            t.line(56,'H','answer output adapter')
            t.lineset(59,65,'H','observation output adapter')
            t.line(66,'P','close program block')
        else:
            t.line(49,'P','emit(x): problem effect','P11 Rules: emit is P; METRICS rule 10')
            t.line(50,'P','test x >= c: stated conjunct','METRICS rule 2; rule 10')
            t.part(50,5,None,'C','stop after a successful any-one conjunction')
            t.line(51,'C','close fact traversal')
            t.line(53,'H','answer output adapter')
            t.lineset(56,62,'H','observation output adapter')
            t.line(63,'P','close program block')
        return
    t.lineset(12,15,'R','holds: problem-specific relation holding and readiness')
    # Nested fully-known evaluators are P in every direction (rule 19).
    ids=t.lines[15];tokens=[t.rows[i]['token'] for i in ids]
    for op in ['≠','=']:
        pos=tokens.index(op)
        t.put(ids[pos-1:pos+2],'P','evaluate '+('late disequality' if op=='≠' else 'committed equality'),
              'METRICS rule 19: fully known relation evaluator is P; rule 10')
    t.lineset(17,32,'H','num: decimal output adapter')
    t.lineset(33,37,'H','emit: fixed effect-stub binding')
    t.lineset(39,43,'R','advance: problem-specific retained pick state')
    t.line(44,'C','try remaining facts until one passes held relations')
    t.line(45,'C','remaining-facts traversal block')
    t.line(46,'R','advance retained fact cursor')
    t.part(46,6,None,'H','increment pick operation counter')
    t.line(47,'P','pick fact binds x')
    t.line(48,'P','emit(x): problem effect','P11 Rules: emit is P; METRICS rule 10')
    t.line(49,'R','test candidate against problem-specific held relations')
    t.line(50,'C','close remaining-facts traversal')
    t.line(51,'R','retain whether x has a surviving value')
    t.line(52,'R','close advance procedure')
    t.line(55,'H','read harness instance line')
    t.line(56,'H','read harness order words')
    t.line(57,'R','initialize held relation and fact state')
    t.line(59,'H','harness message loop')
    t.line(60,'H','harness message block')
    t.line(62,'H','read harness message')
    for n in [63,64,67,68,69,75]:t.line(n,'H','harness stage/message dispatch')
    t.line(66,'R','retain replayed commitment flag')
    ids=t.lines[66];semi=next(i for i in ids if t.rows[i]['token']==';')
    t.put(range(ids[0],semi),'H','read replayed committed value')
    t.line(71,'P','read pick fact count')
    t.line(72,'P','read stated pick facts in order')
    ids=t.lines[72];start=next(i for i in ids if t.rows[i]['token']=='pk');end=next(i for i in ids if i>start and t.rows[i]['token']=='end')
    t.put(range(start,end),'H','initialize pick operation counter')
    t.line(73,'R','retain pick readiness and initial cursor')
    t.line(74,'R','advance problem-specific retained pick')
    if letter=='c':
        t.line(76,'H','dispatch late disequality stage')
        ids=t.lines[76]
        start=next(i for i in ids if t.rows[i]['token'] in ['ininteger','c2'])
        flag=next(i for i in ids if t.rows[i]['token']=='r2')
        t.put(range(start,flag-1),'P','read late disequality constant')
        t.put(range(flag,ids[-1]),'R','retain late disequality readiness')
        for n in [77,78,81]:t.line(n,'H','dispatch commit stage')
        commitline=80
    else:
        for n in [76,77,80]:t.line(n,'H','dispatch commit stage')
        commitline=79
        t.line(81,'H','dispatch late disequality stage')
        ids=t.lines[81]
        start=next(i for i in ids if t.rows[i]['token'] in ['ininteger','c3'])
        flag=next(i for i in ids if t.rows[i]['token']=='r3')
        t.put(range(start,flag-1),'P','read late disequality constant')
        end=next(i for i in ids if i>flag and t.rows[i]['token']=='end')
        t.put(range(flag,end),'R','retain late disequality readiness')
    t.line(commitline,'P','commit selected x as cv','P11 Rules: commit is P; METRICS rule 10')
    t.part(commitline,0,4,'R','test whether a commit candidate is held')
    t.part(commitline,8,11,'R','retain commitment readiness')
    t.line(84,'R','revalidate retained candidate and advance after refutation')
    t.line(87,'H','answer output adapter')
    t.lineset(90,108,'H','observation output adapter and its counter')
    t.line(109,'H','close harness message loop')
    t.line(110,'P','close program block')

def p12(t):
    t.line(1,'P','program block')
    t.declaration(8,{'n':'P','cap':'C','m':'H','i':'H','code':'H','k':'H'})
    for n in [10,11,12]:t.line(n,'H',f'harness input, line {n}')
    t.line(13,'P','query data block')
    roles={x:'P' for x in ['top','lcode','rcode','nfacts','f','len','sv']}
    roles.update({x:'H' for x in ['nsol','cand','ch1','ch2','depth','peakdepth','pend','peakpend']})
    t.declaration(14,roles)
    t.line(15,'C','any-one termination mode declaration')
    t.line(16,'P','sequence and accept-fact encoding arrays')
    t.lineset(18,21,'P','cons: encoded sequence construction','METRICS rule 15; systems/algol-60 Values')
    t.lineset(23,36,'P','readseq: read and encode a stated accept fact','METRICS rule 15; stage information is P (harness 2.7)')
    t.lineset(38,41,'P','same: equality of encoded sequences','METRICS rule 15; systems/algol-60 Values')
    t.lineset(43,47,'S','continuation-based depth-first search procedure')
    t.part(43,6,8,'R','additional continuation argument found','METRICS rules 3, 5, 10: extra argument')
    t.part(44,8,None,'R','additional continuation formal declaration','METRICS rules 3, 5, 10: extra argument')
    t.line(47,'P','sequence cell local declaration')
    t.line(49,'H','count choice base case')
    t.line(50,'P','choice case 1: empty sequence')
    t.line(51,'S','invoke continuation on each search candidate')
    t.line(53,'P','choice case 2: n > 0 head test','METRICS rules 2, 3, 10')
    t.line(54,'P','choice case 2 block')
    t.line(55,'P','construct head-tail cell for choice case 2')
    t.line(56,'P','bind encoded sequence cell')
    for n in [57,58,59,62,63,66]:t.line(n,'H',f'search measurement counter, line {n}')
    t.line(60,'P','choice case 2: e = l')
    t.line(64,'P','choice case 2: e = r')
    for n in [61,65]:
        t.line(n,'S','recursive traversal of '+('left' if n==61 else 'right')+' subtree with continuation')
        t.part(n,10,12,'R','additional continuation actual argument','METRICS rules 3, 5, 10: extra argument')
    t.line(67,'C','release sequence cell for store reuse','METRICS rule 16')
    t.line(68,'P','close choice case 2')
    t.line(69,'S','close depth-first search procedure')
    t.lineset(71,84,'H','printseq: encoded sequence output adapter')
    t.lineset(86,89,'P','accept: closed-world fact matching definition')
    t.line(90,'H','count candidate examined')
    t.line(91,'P','match against the stated accept facts','METRICS rule 6: enumeration of stated facts')
    t.line(92,'P','accept fact matching block')
    t.line(93,'P','accept fact equality head test','METRICS rules 2, 15')
    t.line(94,'P','matching accept fact branch')
    t.line(95,'H','count answers already computed')
    t.line(96,'H','answer output adapter')
    t.line(97,'H','candidate count output adapter')
    t.line(98,'C','escape recursive search for any-one query')
    for n in [99,100,101]:t.line(n,'P','close accept definition branch/block')
    t.line(103,'P','initialize sequence encoding store')
    t.line(104,'P','atom encoding l = 1, r = 2')
    t.line(105,'C','choose any-one termination from query cap')
    t.line(106,'H','initialize measurement counters')
    t.line(109,'P','read number of accept facts')
    t.line(110,'P','read stated accept fact set')
    t.line(111,'P','accept fact input block')
    t.line(112,'P','read accept fact length')
    t.line(113,'P','retain encoded accept fact')
    t.line(114,'P','close accept fact input block')
    t.line(117,'S','invoke hand-written search for query')
    t.part(117,5,7,'R','additional query continuation argument','METRICS rules 3, 5, 10: extra argument')
    t.line(120,'C','any-one search escape target')
    t.lineset(121,130,'H','observation output adapter')
    t.line(131,'P','close query data block')
    t.line(132,'P','close program block')

texts={}
token_objects={}
for key in aliases:
    t=Text(key)
    if '/P11' in key:p11(t,Path(key).stem[-1])
    else:p12(t)
    texts[key]=t.finish();token_objects[key]=t

def read_record(p):
    with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:return json.load(f)

records=[]
for config in ['report','x1','x1sim']:
    for prob in ['P11','P12']:
        for raw in ['raw','raw-rerun-m2']:
            for p in sorted((ROOT/'results/algol-60'/config/prob/raw).glob('*.json*')):
                if p.name.endswith(('.json','.json.gz')):records.append((p,read_record(p)))

logged=[]
for config in ['report','x1','x1sim']:
    for problem in ['P11','P12']:
        for line in (ROOT/f'results/algol-60/logs/1C-{config}-{problem}.tsv').read_text().splitlines():
            fields=line.split('\t')
            assert fields[5]=='exit 0',fields
            logged.append(tuple(fields[1:5]))
record_jobs=[]
for p,d in records:
    r=d['run'];program=Path(r['program']['path'])
    assert hashlib.sha256((ROOT/program).read_bytes()).hexdigest()==r['program']['sha256']
    assert hashlib.sha256((ROOT/r['constants']['input_path']).read_bytes()).hexdigest()==r['constants']['input_sha256']
    record_jobs.append((r['configuration'],r['instance'],program.name,r['mode']))
assert Counter(logged)==Counter(record_jobs)

# Check the posed constant facts directly against the permitted problem files.
for paths in aliases.values():
    for path in paths:
        config,program=path.split('/')
        constantpath=(ROOT/'programs/algol-60'/path).with_suffix('.constants')
        lines=[line.split(':',1) for line in constantpath.read_text().splitlines() if line.strip()]
        data={int(k):list(map(int,v.split())) for k,v in lines}
        if program.startswith('P11'):
            assert data[1][:4]==[3,1,2,3]
            if program.startswith(('P11a','P11b')):assert data[1][4:]==[2]
            else:assert data[2 if program.startswith('P11c') else 3]==[1]
        else:
            sub,n,mode=program.rsplit('.',1)[0].split('.')
            n=int(n[1:]);values=data[1];nf=values[0];values=values[1:];facts=[]
            for _ in range(nf):
                size=values[0];facts.append(tuple(values[1:size+1]));values=values[size+1:]
            assert not values
            assert set(facts)==set({'P12a':[(2,),(1,)*n],'P12b':[(2,)],'P12c':[(2,)*n],'P12d':[(1,)*n]}[sub])

def answer_values(a):
    return [b['verbatim'] for c in a['computations'] for q in c['queries'] for b in q['answers']]

def expected_p12(instance):
    sub,n,mode=instance.split('.');n=int(n[1:])
    vals={'P12a':[('l',)*n,('r',)],'P12b':[('r',)],'P12c':[('r',)*n],'P12d':[('l',)*n]}[sub]
    return vals,n,mode

def classify_record(p,d):
    r=d['run'];sub=r['subproblem'];config=r['configuration'];out=[]
    for stage in d['stages']:
        # These jobs each have exactly one attempt and one main computation.
        assert len(stage['attempts'])==1
        a=stage['attempts'][0];assert len(a['computations'])==1
        comp=a['computations'][0];k=stage['stage'];ans=answer_values(a)
        raw=a['observe']['raw'];states=comp['execution_state']['states']
        reached=not any('not reach' in n.lower() or 'never reach' in n.lower() for n in a.get('notes',[]))
        entry=dict(configuration=config,instance=r['instance'],program=Path(r['program']['path']).name,
          record=str(p.relative_to(ROOT)),stage=k,reached=reached,semantic=None,representation=None,
          simplification=None,identical_to_posed=None,residual_size=None,execution_state=[],
          residual_equivalence=None,observations={},rule=None,harness_fault=('.INVALID.' in p.name or bool(d['harness_faults'])))
        obs=dict(answers_verbatim=ans,observe_verbatim=raw,bindings=a['observe']['bindings'],
            unknowns_representation='No native unknowns; program uses integer values and Boolean flags.' if sub.startswith('P11') else 'Unknown s is filled as an index into parallel head/tail arrays; empty sequence is index 0.',
            alternatives_recorded=comp['alternatives'],suspended_recorded=comp['suspended'],
            manual_actions=a['manual_actions']+d['manual_actions'],posing=a['posed'],notes=a.get('notes',[]),
            problem_operations=comp['problem_operations'],
            measurements={'steps':comp['steps'],'store':a['store'],'note':'Null fields are unavailable, not zero (AMENDMENTS 3.1). Behaviour mode supplies only incidental measurements; cost/storage comparisons are summarized in the notes.'})
        if not reached:
            raise AssertionError('Unexpected not-reached stage requires manual review')
        entry['execution_state']=states[:]
        if sub.startswith('P12'):
            valid,n,mode=expected_p12(r['instance'])
            got=[tuple(re.findall(r'\b[lr]\b',v)) for v in ans]
            if ans:
                assert all(x in valid for x in got),(p,got,valid)
                assert mode=='any' or set(got)==set(valid),(p,got,valid)
                entry.update(semantic='complete',representation='explicit',
                    residual_equivalence='Equivalent for this query: '+('any one returned sequence belongs to the valid set.' if mode=='any' else 'the returned sequence set equals the accept facts, each of length <= n over {l,r}.'))
                obs['answer_completeness']={'valid_answers_obtained':len(got),'valid_answers_expected':1 if mode=='any' else len(valid),'invalid_answers':0}
                expected_candidates=(n+1 if sub in ['P12a','P12d'] else 2**n+1 if sub=='P12b' else 2**(n+1)-1) if mode=='any' else 2**(n+1)-1
                assert comp['candidates_examined']==expected_candidates
                obs['candidates_examined']=comp['candidates_examined']
                obs['candidate_positions_before_answers']=[int(x) for x in re.findall(r'candidates examined so far:\s*\+?\s*(\d+)',a['print'])]
                obs['alternatives_interpretation']='Recursive depth-first traversal holds right branches while traversing left branches. On any-one return, goto done discards the recursion; no alternatives remain resumable at the stage boundary. All-mode exhausts the finite tree.'
                obs['suspended_work']={'kind':'none','count':0}
                obs['conclusion_withdrawn']=None
            else:
                assert states==['error']
                entry.update(semantic='none reported',representation=None,residual_equivalence=None)
                obs['error_verbatim']=comp['execution_state']['error_verbatim']
                obs['answer_completeness']={'valid_answers_obtained':0,'valid_answers_expected':1 if mode=='any' else len(valid),'invalid_answers':0}
                obs['alternatives_interpretation']='No observation block reached; alternatives and suspended item counts are unavailable.'
                obs['unknowns_representation']='No final unknown state is observable. Source encodes s as a head/tail-array cell index, with 0 for the empty sequence.'
                obs['suspended_work']=None
                obs['conclusion_withdrawn']=None
            entry['rule']='SPECIFICATION Outcomes 1-3; P12 query/all versus any-one; AMENDMENTS 3.1 (unavailable measurements).'
        else:
            valid = [2,3] if sub in ['P11a','P11b'] or (sub=='P11c' and k==2) else [2] if sub=='P11c' and k==3 else [] if sub=='P11d' and k==3 else [1] if sub=='P11d' and k==2 else [1,2,3]
            got=[int(v) for v in ans]
            assert all(v in valid for v in got)
            assert got or (valid==[] and 'no solution' in raw)
            entry.update(semantic='complete',representation='explicit',residual_equivalence='Equivalent for the any-one query: returned x is valid.' if got else 'Equivalent empty answer set: committed x = 1 and late x != 1 contradict; program explicitly reports no solution.')
            if sub in ['P11c','P11d']:
                untried=int(re.search(r'untried and kept for a later stage:\s*(\d+)',raw).group(1))
                obs['alternatives_interpretation']=f'{untried} untried pick facts retained via fv and cur, for later-stage revalidation; one current value if bound. These are problem-specific retained data, not a resumable answers() enumerator. After commit, untried facts are incompatible with the committed equality.'
                # Each any-one query is already answered. Retaining data for a
                # subsequent query does not leave work undecided for this stage.
                obs['suspended_work']={'kind':'none needing further information for this stage query','count':0}
                obs['conclusion_withdrawn']='x = 1 is replaced by x = 2; the emitted 1 remains in L.' if sub=='P11c' and k==2 else 'x = 1 is withdrawn as an answer and no solution is reported; committed cv = 1 and its effect remain.' if sub=='P11d' and k==3 else None
                obs['execution_state_reason']='Finished: this stage\'s any-one query has been answered (or its empty outcome decided). fv and cur retain untried fact data for subsequent stage revalidation, but no current relation is waiting on an unknown. No more-answer request exists (harness QUESTIONS A10), so alternatives pending is not used. Retention is recorded separately, including the prose counts missed by the mechanical [alternatives] tag parser.'
            else:
                obs['alternatives_interpretation']='Loop stops at first successful fact; the procedure has no mechanism for resuming further answers.'
                obs['suspended_work']={'kind':'none','count':0}
                obs['conclusion_withdrawn']=None
            obs['answer_completeness']={'valid_answers_obtained':len(got),'valid_answers_expected':1 if valid else 0,'invalid_answers':0,'empty_set_reported':True if not valid else None}
            log=d['effects']['log_after_run']
            # Measurement attempts append to the observation log, not classification L.
            if r['mode']!='behaviour':
                log=[e for st in d['stages'] for at in st['attempts'] for e in at['effects']]
            commitstage=1 if sub in ['P11a','P11b'] else 3 if sub=='P11c' else 2
            commitvalue=2 if sub in ['P11a','P11b','P11c'] else 1
            finalclass='exact' if sub=='P11a' else 'extra'
            timed=[]
            for e in log:
                when='before commitment' if e['stage']<commitstage or sub in ['P11a','P11b'] else 'at commitment' if e['stage']==commitstage else 'after commitment'
                timed.append({**e,'when':when})
            entry['effects']={'class_at_problem_end':finalclass,'committed_value':commitvalue,'commit_stage':commitstage,'L_at_stage':[e['entry'] for e in log if e['stage']<=k],'L_at_problem_end':[e['entry'] for e in log],'entries_with_timing':timed,'reason':{'P11a':'Only 2 is emitted, before its report commits it.','P11b':'1 is emitted before its test fails, then 2 is emitted and reported.','P11c':'1 emitted provisionally at stage 1 is refuted; 2 emitted at stage 2 is committed at stage 3.','P11d':'1 is committed at stage 2; trying refuted alternatives after the late contradiction emits uncommitted 2 and 3.'}[sub]}
            entry['rule']='SPECIFICATION Outcomes 1-4 (any-one complete; semantic and effects axes separate); P11 Commitment/Effects; METRICS rule 19.'
        entry['observations']=obs
        out.append(entry)
    return out

classified={(str(p),d['run']['mode']):classify_record(p,d) for p,d in records}
outcomes=[e for p,d in records if d['run']['mode']=='behaviour' for e in classified[(str(p),'behaviour')]]
base={(d['run']['configuration'],d['run']['instance'],Path(d['run']['program']['path']).name):classified[(str(p),'behaviour')] for p,d in records if d['run']['mode']=='behaviour'}
diffs=[]
compared=0
for p,d in records:
    r=d['run']
    if r['mode']=='behaviour':continue
    compared+=1
    b=base[(r['configuration'],r['instance'],Path(r['program']['path']).name)]
    m=classified[(str(p),r['mode'])]
    axes=['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence']
    for x,y in zip(b,m):
        same=all(x[k]==y[k] for k in axes)
        assert x['observations']['answers_verbatim']==y['observations']['answers_verbatim']
        assert x['observations']['observe_verbatim']==y['observations']['observe_verbatim']
        if x.get('effects'):
            assert x['effects']['L_at_stage']==y['effects']['L_at_stage']
            assert x['effects']['L_at_problem_end']==y['effects']['L_at_problem_end']
            assert x['effects']['class_at_problem_end']==y['effects']['class_at_problem_end']
        if not same:diffs.append(dict(configuration=r['configuration'],instance=r['instance'],program=y['program'],mode=r['mode'],record=y['record'],stage=y['stage'],behaviour={k:x[k] for k in axes},this_mode={k:y[k] for k in axes},note='Classification differs.'))

express=[]
for config in ['report','x1','x1sim']:
    for sub in ['P11a','P11b','P11c','P11d','P12a','P12b','P12c','P12d']:
        kind='not expressible' if sub.startswith('P12') else 'expressible with reformulation' if sub in ['P11c','P11d'] else 'expressible'
        reason=('P12 requires enumerating unknown s. The program supplies continuation-based depth-first search, S under P12 Rules and METRICS 12; none was listed at phase 4, so this is a supporting-search named variant of the core configuration (harnesses/algol-60/S-mechanisms.md). Encoding arrays and equality are P, not evidence of native search.' if sub.startswith('P12') else 'Staged candidate revalidation uses the problem-specific fv/cur/xk store and holds readiness flags, R under METRICS 19; known comparisons and commitment remain P. No general relation store or search engine is supplied.' if sub in ['P11c','P11d'] else 'The finite stated pick facts, comparison and emit in the required order are a mode-faithful transcription (METRICS 3, 6); explicit first-answer loop control is C. Semantic expressibility does not imply exact effects.')
        if config=='x1sim' and sub.startswith('P12'):reason+=' Every recorded attempt reaches the query and errors at a formal-procedure descriptor; this is separate from the core expressibility judgement.'
        express.append(dict(configuration=config,subproblem=sub,direction=None,expressibility=kind,reason=reason))

mechanisms=[]
for key,paths in aliases.items():
    spans=texts[key];ss=[s for s in spans if s['class']=='S']
    for path in paths:
        config,program=path.split('/')
        mechanisms.append(dict(configuration=config,program=program,mechanism='continuation-based depth-first search' if ss else 'none',listed_at_phase_4=False if ss else True,tokens=sum(s['to']-s['from']+1 for s in ss),token_text=key,token_ranges=[{'from':s['from'],'to':s['to']} for s in ss],note='Program-supplied search; count once per configuration across identical P12 programs.' if ss else 'No supporting mechanism used; phase-4 inventory provides none.'))

result=dict(tokens=texts,outcomes=outcomes,mode_differences=diffs,expressibility=express,late_definition=[],s_mechanisms=mechanisms)
(OUT/'algol-60.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')

# Validate exact coverage against every frozen shared text and alias, including hashes.
totals=Counter();pertext={}
for key,spans in texts.items():
    expected=list(range(len(token_objects[key].rows)))
    actual=[i for s in spans for i in range(s['from'],s['to']+1)]
    assert actual==expected,key
    pertext[key]=dict(Counter({c:sum(s['to']-s['from']+1 for s in spans if s['class']==c) for c in 'PCRSH'}))
    totals.update(pertext[key])
    original=[r['token'] for r in token_objects[key].rows]
    for path in aliases[key]:
        rr=list(csv.DictReader((ROOT/'results/algol-60/tokens'/(path+'.tokens.tsv')).open(),delimiter='\t'))
        assert [x['token'] for x in rr]==original,(key,path)
        assert hashlib.sha256((ROOT/'programs/algol-60'/path).read_bytes()).digest()==hashlib.sha256((ROOT/'programs/algol-60'/key).read_bytes()).digest(),(key,path)
assert len(outcomes)==96
assert len(base)==84
assert compared==112
assert len(mechanisms)==84
summary=dict(distinct_texts=len(texts),program_paths=sum(map(len,aliases.values())),tokens=dict(totals),per_text=pertext,behaviour_records=len(base),behaviour_stages=len(outcomes),semantics=dict(Counter(x['semantic'] for x in outcomes)),execution=dict(Counter(tuple(x['execution_state']) for x in outcomes)),measurement_records_compared=compared,mode_differences=len(diffs),harness_fault_entries=sum(x['harness_fault'] for x in outcomes))
summary['execution']={','.join(k):v for k,v in summary['execution'].items()}
(OUT/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
