"""Independent classifier B. Reads frozen tokens and records; executes no subject code."""
import csv
import json
import pathlib
import collections
import re

SOURCE = pathlib.Path('/Users/christopherhay/cp-roles/classifier-B')
DEST = pathlib.Path(__file__).parent

def read_tokens(path):
    with (SOURCE / 'results/algol-60/tokens' / (path + '.tokens.tsv')).open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert [int(x['index']) for x in rows] == list(range(len(rows)))
    return rows

class Classifier:
    """Parse the supplied token stream into constructs, without tokenizing source."""
    def __init__(self, path):
        self.path = path
        self.rows = read_tokens(path)
        self.ts = [r['token'].replace('\u0332', '').lower() for r in self.rows]
        self.raw = [r['token'] for r in self.rows]
        # The frozen table prints report-mode string payloads without quotes.
        # Their call position identifies these existing tokens; never re-tokenize.
        for j,t in enumerate(self.ts):
            if t == 'outstring':
                assert self.ts[j+1:j+4] == ['(','1',',']
                self.ts[j+4] = '<string>'
        self.i = 0
        self.annotations = [None] * len(self.ts)
        self.serial = 0
        self.sub = path.split('/')[1].split('.')[0]
        self.proc = None

    def mark(self, a, b, cls, construct, rule):
        if a >= b: return
        self.serial += 1
        for i in range(a, b):
            assert self.annotations[i] is None, (self.path, i)
            self.annotations[i] = (cls, construct, rule, self.serial)

    def eat(self, token):
        assert self.ts[self.i] == token, (self.path, self.i, token, self.ts[self.i:self.i+10])
        self.i += 1

    def scan(self, stops):
        a = self.i
        depth = 0
        while self.i < len(self.ts):
            t = self.ts[self.i]
            if depth == 0 and t in stops: break
            if t in ('(', '['): depth += 1
            if t in (')', ']'): depth -= 1
            self.i += 1
        return a, self.i

    def variable_class(self, name, context):
        if context == 'H': return 'H'
        if context == 'R-direction': return 'R'
        if context == 'encoding': return 'P'
        if name in {'n','cap','i','code','k','held','conc1','conc2','rev1','rev2','x1','x2','x3','answers'}:
            return 'H'
        if name == 'm': return 'P' if self.sub == 'P02b' else 'H'
        if name in {'pass','changed','xk','yk','zk','sk','tk','uk','vk','wk','r1','r2','r3','r','order','path'}:
            return 'R' if name not in {'order','r'} or self.sub != 'P02b' else 'P'
        if name == 'same' and self.sub == 'P03d': return 'R'
        return 'P'

    def declaration(self, context):
        a = self.i
        self.scan({';'})
        b = self.i
        # A declaration's individual declarators are the smallest role-bearing units.
        # Shared bounds belong to their array declaration; arrays here have one role,
        # except path in P03b's combined hd,tl,path declaration.
        ids = []
        depth = 0
        start = a
        for j in range(a,b):
            t = self.ts[j]
            if t in ('[','('): depth += 1
            elif t in (']',')'): depth -= 1
            elif t == ',' and depth == 0:
                ids.append((start,j)); start=j
        ids.append((start,b))
        for l,u in ids:
            names = [t for t in self.ts[l:u] if re.fullmatch('[a-z][a-z0-9]*',t) and t not in {'integer','boolean','array','value','own'}]
            name = names[0]
            cls = self.variable_class(name, context)
            role = {'P':'problem value or sequence encoding declaration', 'R':'held-state or separate-direction declaration', 'H':'harness word or observation counter declaration'}[cls]
            rule = {'P':'1, 3, 15', 'R':'14, 19', 'H':'13; harness 2.7'}[cls]
            self.mark(l,u,cls,role + ': ' + name,rule)
        # A semicolon between declarations/statements is assigned later to the following construct.

    def proc_context(self, name):
        if name in {'uname','place','state','relations','printseq','printpath'}: return 'H'
        if name in {'split','strip','prefix','lastsplit','unrev'}: return 'R-direction'
        if name == 'same' and self.sub == 'P03d': return 'R-direction'
        if name in {'cons','readseq','same','conc','rev'}: return 'encoding'
        return 'holding'

    def procedure(self):
        a = self.i
        if self.ts[self.i] != 'procedure': self.i += 1
        self.eat('procedure')
        name = self.ts[self.i]; self.i += 1
        self.scan({';'}); self.eat(';')
        # Formal specifications are part of the procedure interface.
        while self.ts[self.i] in {'value','integer','boolean'}:
            self.scan({';'}); self.eat(';')
        pc = self.proc_context(name)
        cls = 'H' if pc == 'H' else 'R' if pc in {'holding','R-direction'} else 'P'
        self.mark(a,self.i,cls,'procedure interface: '+name, '13' if cls=='H' else '14, 19' if cls=='R' else '3, 15')
        old = self.proc; self.proc = name
        self.statement(pc)
        # The identifier following an end is an ALGOL end comment but appears in
        # this frozen token stream. Keep it with the procedure's closing construct.
        if self.i < len(self.ts) and self.ts[self.i] == name:
            self.mark(self.i,self.i+1,cls,'procedure end label: '+name,'10; frozen token table')
            self.i += 1
        self.proc = old

    def condition_role(self, a, b, context, kind):
        ts = self.ts[a:b]
        if context == 'H': return 'H','output adapter','13'
        if context == 'R-direction': return 'R','separate direction case dispatch','14, 10'
        if context == 'encoding': return 'P','sequence encoding or definition case','2, 3, 15'
        if self.proc == 'propagate': return 'R','held-relation scan and dispatch','19, 10'
        if self.proc in {'equation','value3','examine1','examine2','examine3'}:
            known = {'ak','bk','xk','yk','zk','sk','tk','uk','vk','wk'}
            if known.intersection(ts): return 'R','test of which relation places are known','19, 10'
            return 'P','test of a fully known equality or arithmetic relation','19 (evaluator), 2'
        if 'k' in ts or (self.sub=='P02b' and ts[:1]==['r']):
            return 'H','stage/message dispatch','13; harness 2.7(2)'
        if kind == 'for' and ('m' in ts or 'true' in ts):
            return 'H','harness message or instance-code loop','13; harness 2.7'
        return 'H','output adapter conditional','13'

    def simple_role(self,a,b,context):
        ts=self.ts[a:b]; first=ts[0]
        if context == 'H': return 'H','output adapter statement','13'
        if first in {'outstring','outinteger','printtext','print','nlcr','uname','place','state','relations','printseq','printpath'}:
            return 'H','print already computed answers or observed state','13; harness 2.7(3)'
        if first in {'ininteger'} or (':=' in ts and ts[-1:] == ['read']):
            target=ts[4] if first=='ininteger' else first
            cls='H' if target in {'n','cap','m','code','k','order'} else 'P'
            return cls, 'read harness input word' if cls=='H' else 'read stage constant', '13; harness 2.7(1)' if cls=='H' else '1; stage information'
        if first in {'conc1','conc2','rev1','rev2','answers','x1','x2','x3','held'}:
            return 'H','observation counter or its computation','13; harness 2.7(4)'
        if context == 'R-direction': return 'R','separate direction computation: '+str(self.proc),'14, 15'
        if context == 'encoding': return 'P','sequence encoding or definition computation','3, 15'
        if self.proc == 'propagate': return 'R','scan or invoke held problem relation','19'
        if self.proc in {'equation','value3','examine1','examine2','examine3'}:
            if first in {'r','r1','r2','r3','changed'}:
                return 'R','update held-relation status','19'
            return 'P','evaluate relation or give a place its value','19 (evaluator); 15'
        if first in {'propagate','examine1'}: return 'R','invoke held-relation evaluator','19'
        if first in {'split','strip','prefix','unrev'}: return 'R','query in separately written direction','3, 14'
        if first in {'r1','r2','r3','xk','yk','zk','sk','tk','uk','vk','wk'}:
            return 'R','initialize or pose a held relation','19'
        if first == 'r' and self.sub=='P02b':
            return 'P','select the relation specified by instance order','1; problem order'
        return 'P','stage information, query, or sequence encoding','1, 3, 15'

    def statement(self,context='top',shell_role=None):
        a=self.i; t=self.ts[a]
        if t=='begin':
            cls='H' if context=='H' else 'R' if context in {'R-direction','holding'} else 'P'
            if shell_role is not None:cls=shell_role
            self.mark(a,a+1,cls,'block scope','10');self.i+=1
            while self.ts[self.i]!='end':
                if self.ts[self.i]==';':
                    # Delay classing the separator until its following construct is known.
                    self.i+=1; continue
                t=self.ts[self.i]
                if t=='procedure' or (t in {'integer','boolean'} and self.ts[self.i+1]=='procedure'):
                    self.procedure()
                elif t in {'integer','boolean','own','value'}:self.declaration(context)
                else:self.statement(context)
            self.mark(self.i,self.i+1,cls,'block closing delimiter','10'); self.i+=1
        elif t=='if':
            self.i+=1;self.scan({'then'});self.eat('then')
            cls,desc,rule=self.condition_role(a,self.i,context,'if')
            self.mark(a,self.i,cls,desc,rule)
            body_context=context
            # Top-level branches that only print are output adapters. Stage-dispatch
            # branches still contain P reads and R poses, independently classed.
            if context=='top' and cls=='H' and desc=='output adapter conditional':body_context='H'
            self.statement(body_context,cls)
            if self.i<len(self.ts) and self.ts[self.i]=='else':
                self.mark(self.i,self.i+1,cls,'else connective of '+desc,rule);self.i+=1
                self.statement(body_context,cls)
        elif t=='for':
            self.i+=1;self.scan({'do'});self.eat('do')
            cls,desc,rule=self.condition_role(a,self.i,context,'for');self.mark(a,self.i,cls,desc,rule)
            # The message loop's body is mixed; its block delimiters are H.
            body=self.i
            self.statement(context,cls)
            if desc=='harness message or instance-code loop' and self.ts[body]=='begin':
                self.relabel(body,body+1,'H','harness message loop block','10; harness 2.7')
                self.relabel(self.i-1,self.i,'H','harness message loop closing delimiter','10; harness 2.7')
        else:
            expression_if = self.ts[a+1:a+3] == [':=','if']
            self.scan({';','end'} if expression_if else {';','end','else'})
            assert self.i>a,(self.path,self.i,self.ts[self.i:self.i+10])
            cls,desc,rule=self.simple_role(a,self.i,context)
            # Chain assignments may initialize both the encoding allocator and H counters.
            if self.ts[a]=='top' and self.ts[a+2] in {'conc1','answers'}:
                self.mark(a,a+2,'P','encoded-cell allocator target in chained initialization','10, 15')
                self.mark(a+2,self.i,'H','initialize observation counters','13')
            else:self.mark(a,self.i,cls,desc,rule)

    def relabel(self,a,b,cls,desc,rule):
        for i in range(a,b):self.annotations[i]=None
        self.mark(a,b,cls,desc,rule)

    def run(self):
        self.statement()
        assert self.i==len(self.ts),(self.path,self.i,self.ts[self.i:])
        # Rule 20: separators go with the following construct, including procedure
        # and statement separators. A final semicolon belongs to its containing block.
        for i in range(len(self.ts)-1,-1,-1):
            if self.annotations[i] is None:
                assert self.ts[i]==';',(self.path,i,self.ts[i])
                cls,desc,rule,serial=self.annotations[i+1]
                self.annotations[i]=(cls,desc,rule+'; 20',serial)
        spans=[]
        for i,(cls,desc,rule,serial) in enumerate(self.annotations):
            if spans and serial==self.annotations[i-1][3] and cls==spans[-1]['class']:
                spans[-1]['to']=i
                if '20' in rule and '20' not in spans[-1]['rule']:spans[-1]['rule']+='; 20'
            else:spans.append({'from':i,'to':i,'class':cls,'construct':desc,'rule':rule})
        return spans

def token_classes():
    texts=list(csv.DictReader((SOURCE/'results/algol-60/tokens/TEXTS.tsv').open(),delimiter='\t'))
    return {r['text']:Classifier(r['text']).run() for r in texts}

def size(relations, occurrences, bindings=0):
    return {'relations_left_to_decide':relations,'unknown_occurrences_in_those_relations':occurrences,'bound_unknowns':bindings}

def p02_relations(run, stage):
    if run['subproblem']=='P02c':return {'R1','R2','R3'}
    order=run['parameters'].get('order',['R1','R2','R3'])
    return set(order[:stage])

def judgement(run,stage,reading=None):
    sub=run['subproblem']
    rep='explicit'; simp=None; identical=None; sizes=None; proof=None
    if sub=='P01a':
        if stage<3:
            rep='residual';simp='reducible';identical=True
            sizes={'input':size(stage,2*stage),'reported':size(stage,2*stage)}
            proof=('Equivalent: the held equality x=y, with z free, is exactly stage 1. Identifying x with y gives a smaller solved form.' if stage==1 else
                   'Equivalent: x=y and y=z is exactly the accumulated information over all values. Identifying all three unknowns gives a smaller solved form.')
        else:proof='Equivalent: z=2 and the two equalities force x=y=z=2, the single explicit answer.'
    elif sub=='P01b':
        if stage==1:
            rep='residual';simp='reducible';identical=True
            sizes={'input':size(1,2),'reported':size(1,2)}
            proof='Equivalent by the two cases of conc: conc(<1,2>,s,t) iff t=<1,2>++s for every finite sequence s. The latter is a solved form with no relation left to decide.'
        else:proof='Equivalent: substituting s=<3> into conc(<1,2>,s,t) gives exactly t=<1,2,3>.'
    elif sub=='P01c':
        rep='residual';simp='inconsistency undetected' if reading=='finite' else 'reducible';identical=True
        sizes={'input':size(1,2),'reported':size(1,2)}
        proof=('Equivalent to the empty valid set: a finite sequence would need length(x)=1+length(x), impossible. The program retains this contradiction and does not report no solutions.' if reading=='finite' else
               'Equivalent over rational trees: repeated unfolding of x=<1>++x forces every element to be 1 and leaves no finite termination; the unique regular infinite sequence is the valid outcome. The program leaves the equation undecided instead of constructing its cyclic solved value.')
    elif sub.startswith('P02'):
        rels=p02_relations(run,stage)
        input_size=size(len(rels),sum({'R1':2,'R2':3,'R3':1}[x] for x in rels))
        if rels=={'R1'}:
            rep='residual';simp='reduced';identical=True
            proof='Equivalent: u+v=16 is held unchanged over integers and w is free. As SPECIFICATION explicitly illustrates, this one arithmetic relation is reduced.'
            report_size=size(1,2)
        elif rels=={'R2'}:
            rep='residual';simp='reduced';identical=True
            proof='Equivalent: the held w*u=v is exactly R2 over all integers. Multiplication cannot be expressed by the permitted solved-form sequence/unknown terms, so one relation remains necessary.'
            report_size=size(1,3)
        elif rels=={'R1','R2'}:
            rep='residual';simp='reducible';identical=True
            proof='Equivalent: substituting v=16-u in w*u=v yields u*(w+1)=16. Thus u is a nonzero integer divisor of 16. The checker derives all ten triples in the problem file without restricting the original domain. Their explicit disjunction has no relation left to decide, so this residual is reducible.'
            report_size=size(2,5)
        elif rels=={'R2','R3'}:
            rep='residual';simp='reduced';identical=False
            proof='Equivalent: R3 forces u=12-10=2; substituting into R2 gives v=2*w, w any integer. The report holds exactly w*2=v plus u=2. One arithmetic relation remains necessary in the specified representation language; there is no finite-domain restriction.'
            report_size=size(1,2,1)
        elif rels=={'R3'}:
            rep='solved form'
            proof='Equivalent: u+10=12 iff u=2; v and w remain free integers.'
        elif rels=={'R1','R3'}:
            rep='solved form'
            proof='Equivalent: R3 gives u=2, and R1 then gives v=14; w remains any integer.'
        else:
            assert rels=={'R1','R2','R3'}
            proof='Equivalent: R3 gives u=2; R1 gives v=14; R2 gives w=14/2=7. These integers satisfy all three relations and are uniquely forced.'
        if rep=='residual':sizes={'input':input_size,'reported':report_size}
    else:
        proof={
            'P03a':'The two conc cases append <1,2> to <3>, giving exactly c=<1,2,3>.',
            'P03b':'Every split of the length-2 result is at position 0, 1 or 2. The three reported prefix/suffix pairs are exactly those splits, in that order.',
            'P03c':'Removing the required matching prefix <1> from <1,2,3> leaves exactly b=<2,3>.',
            'P03d':'The required suffix <3> leaves exactly a=<1,2>. The separate direction checks suffix equality and exhausts its recursion.',
            'P03e':'Induction on the two rev cases gives the unique reversal <3,2,1> of <1,2,3>.',
            'P03f':'Reversal is an involution on finite sequences, so exactly a=<3,2,1> satisfies rev(a,<1,2,3>). The report contains that answer and the recursive direction finishes.'
        }[sub]
        proof='Equivalent: '+proof
    return {'semantic':'complete','representation':rep,'simplification':simp,'identical_to_posed':identical,'residual_size':sizes,
            'residual_equivalence':proof,'rule':'SPECIFICATION Outcomes 1-3; '+('P01c '+reading+' reading; ' if reading else '')+'AMENDMENTS 3.1-3.4'}

def records():
    paths=sorted((SOURCE/'results/algol-60').glob('*/P0?/raw/*.json'))
    # Only read raw run records, never the authored summaries alongside raw/.
    return [(str(p.relative_to(SOURCE)),json.loads(p.read_text())) for p in paths]

def canonical_answer(s):
    # Discard display padding and numeric unary plus only; retain arithmetic plus.
    s=re.sub(r'\+\s*(\d+)',r'\1',s)
    return re.sub(r'\s+','',s)

EXPECTED_EXPLICIT={
    'P03a':['c=(1,2,3)'],
    'P03b':['a=(),b=(1,2)','a=(1),b=(2)','a=(1,2),b=()'],
    'P03c':['b=(2,3)'],'P03d':['a=(1,2)'],
    'P03e':['b=(3,2,1)'],'P03f':['a=(3,2,1)']}

def check_answers(run,stage,answers):
    sub=run['subproblem']; actual=[canonical_answer(a) for a in answers]
    if sub in EXPECTED_EXPLICIT:expected=EXPECTED_EXPLICIT[sub]
    elif sub=='P01a':expected=[['xheld,yheld,zfree,wherex=y','xheld,yheld,zheld,wherex=y,y=z','x=2,y=2,z=2'][stage-1]]
    elif sub=='P01b':expected=[['sheld,theld,whereconc((1,2),s,t)','s=(3),t=(1,2,3)'][stage-1]]
    elif sub=='P01c':expected=['xheld,wherex=(1)++x']
    else:
        rels=p02_relations(run,stage)
        expected=[{
            frozenset(['R1']):'uheld,vheld,wfree,whereu+v=16',
            frozenset(['R2']):'uheld,vheld,wheld,wherew.u=v',
            frozenset(['R3']):'u=2,vfree,wfree',
            frozenset(['R1','R2']):'uheld,vheld,wheld,whereu+v=16,w.u=v',
            frozenset(['R1','R3']):'u=2,v=14,wfree',
            frozenset(['R2','R3']):'u=2,vheld,wheld,wherew.2=v',
            frozenset(['R1','R2','R3']):'u=2,v=14,w=7',
        }[frozenset(rels)]]
    assert actual==expected,(run['configuration'],run['instance'],stage,actual,expected)

def observations(run,attempt,comp,stage):
    sub=run['subproblem']
    unknowns=('Boolean known flags and integer value slots, with separate retained equality flags; an unknown flag does not assert an integer-only domain for the displayed free variable. Unknown equalities are not native shared cells.' if sub=='P01a' else
              'Boolean known flags and sequence-cell indices into head/tail arrays; unbound names in held relations are symbolic sequence places. No unifier or occurs check; no cyclic value is constructed.' if sub.startswith('P01') else
              'Boolean known flags and integer value slots; the retained R1/R2/R3 flags and their stage constants hold the arithmetic relations over the problem\'s integer domain.' if sub.startswith('P02') else
              'The query output is computed directly using finite sequence head/tail arrays. Unknown result arguments are procedure results or entries in a direction-specific path array; no native logical variable remains.')
    waits=[]
    if sub=='P01a' and stage<3:waits=['x=y waits for either endpoint to become known']+(['y=z waits for either endpoint to become known'] if stage==2 else [])
    elif sub=='P01b' and stage==1:waits=['conc(a1,s,t) waits for s; it does not yet construct t=<1,2>++s']
    elif sub=='P01c':waits=['x=a1++x waits for x to be known; no value is supplied by this instance']
    elif sub.startswith('P02'):
        rels=p02_relations(run,stage)
        if rels in ({'R1'},{'R1','R2'}):waits+=['R1 waits for u or v']
        if rels in ({'R2'},{'R1','R2'}):waits+=['R2 waits for two known places (with explicit zero/divisibility cases in its evaluator)']
        if rels=={'R2','R3'}:waits+=['R2 has u=2 and waits for v or w']
    return {
        'answers_verbatim':[x['verbatim'] for q in comp['queries'] for x in q['answers']],
        'observe_verbatim':attempt['observe']['raw'],
        'bindings':attempt['observe']['bindings'],
        'unknowns_representation':unknowns,
        'alternatives':comp['alternatives'],
        'alternatives_note':'No native alternatives and no retained alternatives structure is reported. Null measurements remain unavailable, not measured zero.',
        'suspended':comp['suspended'],
        'waiting_on':waits,
        'suspension_note':'Held problem relations, not a language suspension facility. A missing boundary/peak count is unavailable; finished stages hold no pending work according to the execution observation.',
        'conclusion_withdrawn':False,
        'withdrawal_note':'Later bindings refine earlier conditional outcomes; no conclusion is retracted.',
        'manual_actions':attempt['manual_actions'],
        'run_manual_actions':[],
        'problem_operations_cumulative':comp['problem_operations'],
        'steps_in_this_record':comp['steps'],
        'store_in_this_record':attempt['store'],
        'execution_basis':comp['execution_state']['basis'],
        'error_verbatim':comp['execution_state']['error_verbatim'],
        'posing':attempt['posed'],
        'measurement_note':'x1sim has behaviour only; no step budget, cost or store measurement is available.' if run['configuration']=='x1sim' else 'Behaviour is the classification source. Cost/storage figures belong to their corresponding mode records; nulls here are unavailable.',
        'evaluation_order':'The problem-specific propagate procedure scans held relations in R1,R2,R3 order until no new binding is made; observation counts are cumulative examinations, not applications of definition cases.' if sub.startswith('P02') else None,
    }

def outcome_classes(all_records):
    out=[]
    indexed={(d['run']['configuration'],d['run']['instance'],d['run']['mode']):(p,d) for p,d in all_records}
    for path,d in all_records:
        run=d['run']
        if run['mode']!='behaviour':continue
        assert run['complete'] and not d['harness_faults'] and not d['manual_actions']
        for s in d['stages']:
            assert len(s['attempts'])==1
            a=s['attempts'][0];assert len(a['computations'])==1
            c=a['computations'][0];stage=s['stage']
            assert not a['manual_actions']
            check_answers(run,stage,[x['verbatim'] for q in c['queries'] for x in q['answers']])
            for reading in (['finite','rational'] if run['subproblem']=='P01c' else [None]):
                obs=observations(run,a,c,stage)
                obs['measurement_records']={}
                for mode in ['cost','storage']:
                    other=indexed.get((run['configuration'],run['instance'],mode))
                    if other:
                        mp,md=other; ma=md['stages'][stage-1]['attempts'][0]; mc=ma['computations'][0]
                        obs['measurement_records'][mode]={'record':mp,'steps':mc['steps'] if mode=='cost' else None,
                                                         'store':ma['store'] if mode=='storage' else None}
                    else:obs['measurement_records'][mode]=None
                if run['subproblem'] in {'P01a','P01b'}:
                    obs['binding_propagation_latency']='Individual-binding latency is unavailable; the cost record gives the whole-stage cost, including harness/output work.'
                if run['subproblem'].startswith('P02') and p02_relations(run,stage)=={'R1','R2','R3'}:
                    prior=p02_relations(run,stage-1) if run['subproblem']!='P02c' else set()
                    sequence=['R2'] if prior=={'R1','R3'} else ['R1','R2'] if prior=={'R2','R3'} else ['R1','R2','R3','R1','R2']
                    obs['last_stage_examination_order']={'sequence':sequence,'basis':'Inferred from source flags and the R1,R2,R3 scan; cumulative observation counters agree. No native execution trace was recorded.'}
                if reading=='finite':
                    obs['answer_completeness']={'valid_outcomes':0,'reported_no_solutions':False,'equivalent_empty_residual':True}
                elif run['subproblem'].startswith('P02') and p02_relations(run,stage)=={'R1','R2'}:
                    obs['answer_completeness']={'valid_outcomes':10,'explicit_triples_reported':0,'equivalent_residual':True}
                else:
                    obs['answer_completeness']={'all_valid_outcomes_denoted':True,'invalid_outcomes_denoted':False,'basis':'The literal reports are checked against the problem file; equivalence is explained in residual_equivalence.'}
                out.append({'configuration':run['configuration'],'instance':run['instance'],
                            'program':pathlib.Path(run['program']['path']).name,'record':path,
                            'stage':stage,'reading':reading,'reached':True,
                            **judgement(run,stage,reading),
                            'execution_state':c['execution_state']['states'],
                            'observations':obs})
    return out

def mode_differences(all_records):
    by={(d['run']['configuration'],d['run']['instance'],d['run']['program']['path'],d['run']['mode']):(p,d) for p,d in all_records}
    diffs=[]; comparisons=0
    for path,d in all_records:
        r=d['run']
        if r['mode']=='behaviour':continue
        bp,b=by[(r['configuration'],r['instance'],r['program']['path'],'behaviour')]
        assert r['complete'] and not d['harness_faults']
        assert [s['stage'] for s in d['stages']]==[s['stage'] for s in b['stages']]
        for s,bs in zip(d['stages'],b['stages']):
            comparisons+=1
            assert len(s['attempts'])==len(bs['attempts'])==1
            a,ba=s['attempts'][0],bs['attempts'][0]
            c,bc=a['computations'][0],ba['computations'][0]
            def signature(at,co):
                return (at['observe']['raw'],at['observe']['bindings'],
                        [[v['verbatim'] for v in q['answers']] for q in co['queries']],
                        co['execution_state']['states'],co['execution_state']['error_verbatim'],
                        co['alternatives']['at_boundary'],co['suspended']['at_boundary'])
            # Identical reports imply identical semantic/representation/simplification
            # judgments; do not reclass each mode or confuse measurements with outcomes.
            assert signature(a,c)==signature(ba,bc),(path,s['stage'],'unexpected mode difference')
    assert comparisons==136
    return diffs

def expressibility_classes():
    entries=[]
    for config in ['report','x1','x1sim']:
        for sub in ['P01a','P01b','P01c','P02a','P02b','P02c','P03a','P03b','P03c','P03d','P03e','P03f']:
            direction={'P01b':'conc: known prefix, later known suffix -> result',
                       'P03a':'conc(a,b,c): a,b -> c','P03b':'conc(a,b,c): c -> a,b',
                       'P03c':'conc(a,b,c): a,c -> b','P03d':'conc(a,b,c): b,c -> a',
                       'P03e':'rev(a,b): a -> b','P03f':'rev(a,b): b -> a'}.get(sub)
            plain=sub in {'P03a','P03e'}
            reason={
                'P01a':'ALGOL has no native unknown equality. R known flags, held equation flags and a problem-specific propagation scan retain equalities until a value arrives (rule 19). The arithmetic/value evaluations within this mechanism are P. The displayed unknown equalities impose no finite or integer-only domain.',
                'P01b':'Forward conc and sequence encoding are P (3,15), but retaining conc with two unknown places until stage 2 requires the problem-specific R holding layer (19). Its first residual is equivalent on the full sequence domain.',
                'P01c':'The program retains the particular recursive equation as R state (19). This preserves its conditional meaning under both finite and rational readings without deciding the finite contradiction or constructing the rational cyclic solution. No native unification/occurs check is available.',
                'P02a':'Problem-specific R knownness tests, held relations and repeated scans (19) retain the original integer relations; evaluators in every arithmetic direction are P under rule 19. No finite search domain or general supporting mechanism is used.',
                'P02b':'The same R holding layer (19) is used in all six arrival orders. Instance order dispatch follows the posed problem; the propagation scan itself uses R1,R2,R3 order. All six end with the same unique answer; early equivalent residuals need not be fully simplified.',
                'P02c':'Although all information arrives at once, the program uses the R holding/propagation formulation of R1,R2,R3 (19), rather than a transcription that directly computes the full relation without knownness handling.',
                'P03a':'conc computes the query direction with one branch for each of its two cases, in order. This is mode-faithful P by rule 3; the sequence encoding is P by rule 15.',
                'P03b':'The separate split direction and extra path/depth state are R by rules 3,5,14,15. It preserves conc by visiting every split position of the known finite result; the forward procedure cannot run backwards.',
                'P03c':'The separate strip direction tests matching heads and recurses to derive the suffix. It is R throughout its computational constructs (3,14), preserving conc on finite sequences.',
                'P03d':'The separate prefix direction with path/depth state and suffix equality is R (3,5,14,15). It preserves exactly the prefix that concatenates with the supplied suffix to make the result.',
                'P03e':'rev follows its two cases in order and evaluates recursive rev before conc, as the definition requires. Forward conc likewise transcribes its cases; P under rules 3 and 15.',
                'P03f':'Separate unrev and lastsplit directions plus path/depth state are R (3,5,14,15). lastsplit is evaluated before recursive unrev, reversing the two given conjuncts (one move under 4,8). This preserves the reversal relation on finite sequences.'
            }[sub]
            entries.append({'configuration':config,'subproblem':sub,'direction':direction,
                            'expressibility':'expressible' if plain else 'expressible with reformulation','reason':reason})
    return entries

def verify_final(result,all_records):
    texts=list(csv.DictReader((SOURCE/'results/algol-60/tokens/TEXTS.tsv').open(),delimiter='\t'))
    assert set(result['tokens'])=={r['text'] for r in texts}
    for r in texts:
        path=r['text'];rows=read_tokens(path);spans=result['tokens'][path]
        covered=[i for s in spans for i in range(s['from'],s['to']+1)]
        assert covered==list(range(len(rows))),(path,'coverage')
        assert all(s['class'] in 'PCRSH' and s['construct'] and s['rule'] for s in spans)
        for alias in r['also the text of'].split():
            assert [x['token'] for x in read_tokens(alias)]==[x['token'] for x in rows],alias
    log=[]
    for line in (SOURCE/'results/algol-60/batch-log.tsv').read_text().splitlines():
        t,config,instance,program,mode,*rest=line.split('\t');log.append((config,instance,program,mode))
    keys=[(d['run']['configuration'],d['run']['instance'],pathlib.Path(d['run']['program']['path']).name,d['run']['mode']) for p,d in all_records]
    assert collections.Counter(log)==collections.Counter(keys)
    stages=json.loads((SOURCE/'harnesses/stages.json').read_text())
    expected={}
    for p in stages['problems']:
        if p['problem'] not in {'P01','P02','P03'}:continue
        for sub in p['subproblems']:
            for inst in sub['instances']:expected[inst['id']]=[s['stage'] for s in sub['stages']]
    for path,d in all_records:
        assert [s['stage'] for s in d['stages']]==expected[d['run']['instance']],path
    # Exact integer proof for R1+R2: u divides nonzero 16, so |u| <= 16.
    triples=sorted((u,16-u,16//u-1) for u in range(-16,17) if u and 16%u==0)
    assert triples==sorted([(1,15,15),(2,14,7),(4,12,3),(8,8,1),(16,0,0),(-1,17,-17),(-2,18,-9),(-4,20,-5),(-8,24,-3),(-16,32,-2)])
    assert all(u+v==16 and w*u==v for u,v,w in triples)
    assert len(result['outcomes'])==105 and len(result['expressibility'])==36
    counts=collections.Counter()
    for spans in result['tokens'].values():
        for s in spans:counts[s['class']]+=s['to']-s['from']+1
    return counts

if __name__=='__main__':
    all_records=records()
    result={'tokens':token_classes(),'outcomes':outcome_classes(all_records),
            'mode_differences':mode_differences(all_records),'expressibility':expressibility_classes()}
    counts=verify_final(result,all_records)
    output=DEST/'algol-60.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    json.loads(output.read_text())
    print('Verified token coverage:',dict(counts),'total',sum(counts.values()))
    print('Verified',len(all_records),'run records; 102 behaviour stages / 105 reading-specific judgments; 136 mode-stage comparisons with no differences; 36 expressibility judgments')
