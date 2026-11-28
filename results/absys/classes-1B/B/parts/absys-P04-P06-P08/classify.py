"""Independent classifier B. Reads frozen tokens and raw records; executes no Absys.

All classification decisions below are hand judgements. Automation expands shared
texts, attaches evidence and checks coverage; it does not infer classes from logs.
"""
import json
import re
from collections import Counter
from pathlib import Path
from inspect_records import ROOT, CONFIGS, records

OUT = Path(__file__).resolve().parent
DATA = {k: [] if k != 'tokens' else {} for k in
        ['tokens','outcomes','mode_differences','expressibility','late_definition','s_mechanisms']}
TEXTS = [line.split('\t') for line in
         (ROOT/'results/absys/tokens/TEXTS-1B-P04-P06-P08.tsv').read_text().splitlines()[1:]]
P_RULE = 'METRICS, P; rules 1, 3 and 10 (native transcription; nested constructs)'

def span(a,b,label,cls='P',rule=None):
    return {'from':a,'to':b,'class':cls,'construct':label,'rule':rule or P_RULE}

def make(name, parts):
    DATA['tokens']['absys/'+name] = [span(*p) for p in parts]

for n in ['a','b']:
    make('P04'+n+'.ab1',[(0,4,'loop definition header'),(5,8,'loop case: recursive application'),
        (9,9,'loop definition end'),(10,12,'query constant xval = 1'),
        (13,13,'query disjunction opening'),
        (14,17 if n=='a' else 16,'first query disjunct: '+('loop(x)' if n=='a' else 'x = xval')),
        (18 if n=='a' else 17,21,'or and second query disjunct'),(22,22,'query disjunction close')])
for n in ['c','d','e','f']:
    left=n in 'cd'
    parts=[(0,5,'alist definition header and disjunction opening')]
    if left:
        parts += [(6,9,'alist-left recursive case: alist(m)'),(10,16,'alist-left recursive case: p = <a> ++ m'),
                  (17,21,'or and alist-left empty case')]
    else:
        parts += [(6,9,'alist-right empty case'),(10,17,'or and alist-right recursive head'),
                  (18,21,'alist-right recursive case: alist(m)')]
    parts += [(22,23,'alist definition close')]
    parts += ([(24,30,'query sequence constant'),(31,34,'ground alist query')] if n in 'ce'
              else [(24,27,'alist sequence generation query')])
    make('P04'+n+'.ab1',parts)
for n in 'abc':
    parts=[(0,2,'first stage constant'),(3,5,'second stage constant')]
    parts += ([(6,8,'stage 1: x = 2'),(9,14,'stage 2: not(x = 1)')]
              if n=='b' else [(6,11,'stage 1: not(x = 1)'),(12,14,'stage 2: value of x')])
    make('P06'+n+'.abs',parts)

MEM=[(20,25,'mem definition header'),(26,34,'mem case 1: sequence begins with E'),
     (35,43,'or and mem case 2 head'),(44,50,'mem case 2 recursive application (leading separator rule 20)'),
     (51,51,'mem case 2 close')]
make('P06d.abs',[(0,10,'first input sequence constant'),(11,19,'second input sequence constant')]+MEM+[
    (52,59,'setdiff definition header'),(60,70,'setdiff case 1: empty input and output'),
    (71,79,'or and setdiff case 2 head'),(80,86,'setdiff case 2 membership test'),
    (87,95,'setdiff case 2 recursive application'),(96,96,'setdiff case 2 close'),
    (97,113,'or and setdiff case 3 head (retain H)'),(114,123,'setdiff case 3 negated membership'),
    (124,132,'setdiff case 3 recursive application'),(133,133,'setdiff case 3 close'),
    (134,141,'setdiff query')])
for n in ['1','2','3']:
    offset=3 if n!='3' else 0
    parts=[(3*i,3*i+2,'closed-world fact constant '+str(i+1)) for i in range(10)]
    if offset:parts += [(30,32,'ground query atom constant')]
    chunks=[(30,33,'student definition header'),(34,38,'student fact 1'),(39,44,'or and student fact 2'),
            (45,48,'maths definition header'),(49,53,'maths fact 1'),(54,59,'or and maths fact 2'),
            (60,65,'takes definition header'),(66,74,'takes fact 1'),(75,84,'or and takes fact 2'),
            (85,94,'or and takes fact 3'),(95,99,'nonmajor definition header'),
            (100,103,'nonmajor: student(P)'),(104,108,'nonmajor: maths(K)'),
            (109,118,'nonmajor: not(takes(P,K))'),(119,119,'nonmajor definition close'),
            (120,123,'nonmajor query')]
    parts += [(a+offset,b+offset,l) for a,b,l in chunks]
    make('P06e'+n+'.abs',parts)

orders={'':[(10,16,'R1: x + y + z = 12'),(17,21,'R2: y + z = 7'),(22,24,'R3: z = 3')],
        '.132':[(10,16,'R1: x + y + z = 12'),(17,19,'R3: z = 3'),(20,24,'R2: y + z = 7')],
        '.213':[(10,14,'R2: y + z = 7'),(15,21,'R1: x + y + z = 12'),(22,24,'R3: z = 3')],
        '.231':[(10,14,'R2: y + z = 7'),(15,17,'R3: z = 3'),(18,24,'R1: x + y + z = 12')],
        '.312':[(10,12,'R3: z = 3'),(13,19,'R1: x + y + z = 12'),(20,24,'R2: y + z = 7')],
        '.321':[(10,12,'R3: z = 3'),(13,17,'R2: y + z = 7'),(18,24,'R1: x + y + z = 12')]}
for order,goals in orders.items():
    make('P07a'+order+'.ab1',[(0,2,'R1 constant'),(3,5,'R2 constant'),(6,8,'R3 constant'),
         (9,9,'one-stage conjunction opening')]+goals+[(25,25,'one-stage conjunction close')])
for n in 'bf':
    make('P07'+n+'.ab1',[(0,2,'first equation constant'),(3,5,'second equation constant'),
         (6,6,'conjunction opening'),(7,11,'first arithmetic relation'),
         (12,16,'second arithmetic relation'),(17,17,'conjunction close')])
for n in 'cg':
    make('P07'+n+'.ab1',[(0,2,'arithmetic constant'),(3,7,'arithmetic relation')])
for n in 'de':
    make('P07'+n+'.ab1',[(0,2,'u constant'),(3,5,'v constant'),(6,6,'conjunction opening'),
         (7,11,'w * u = v'),(12,14,'u = uval'),(15,17,'v = vval'),(18,18,'conjunction close')])

CONC=[(15,24,'conc definition header and disjunction opening'),(25,31,'conc empty case'),
      (32,46,'or and conc recursive case head equations'),(47,54,'conc recursive application'),
      (55,56,'conc definition close')]
make('P08a.ab1',[(0,2,'stage 6 prefix constant'),(3,11,'stage 1: a = <x,y,z>'),
    (12,17,'stage 2: application of undefined rev'),(18,20,'stage 3: x = y'),
    (21,28,'stage 4: rev definition header'),(29,36,'rev empty case'),
    (37,44,'or and rev recursive case head'),(45,50,'rev recursive application'),
    (51,60,'rev recursive case: conc(q,<h>,r)'),(61,62,'rev definition close')]+
    [(a+48,b+48,l) for a,b,l in CONC]+[
    (105,107,'stage 5: y = z'),(108,114,'stage 6: b = <42> ++ c')])
make('P08b.ab1',[(0,8,'stage 1: a = <x,y,z>'),(9,14,'stage 2: application of undefined rev'),
    (15,17,'stage 3: x = y')])
R_RULE='METRICS R; extra definition/case, rule 10 separates unchanged case contents'
make('P08c.ab1',[(0,6,'stage 2 query sequence constant'),(7,10,'stage 3 empty input constant'),
    (11,14,'stage 3 empty output constant')]+CONC+[
    (57,62,'stage 2: application of undefined rev'),(63,70,'stage 3: rev definition header'),
    (71,76,'rev empty case'),(77,83,'extra alternative delegates unknown future cases to revmore','R',R_RULE),
    (84,85,'rev definition close'),(86,92,'stage 4: extra procedure revmore header','R',R_RULE),
    (93,99,'original rev recursive case head'),(100,105,'original rev recursive application'),
    (106,115,'original rev recursive case conc application'),
    (116,116,'extra procedure revmore close','R',R_RULE)])
# P06 explicitly permits a set-forming presentation, and rule 7 explicitly
# assigns the comprehension construct P. Its multiplicity limitation is noted.
make('variants/P06d.set.abs',[(0,10,'first input sequence constant'),(11,19,'second input sequence constant')]+MEM+[
    (52,60,'setdiff set-form definition header'),
    (61,64,'set comprehension binder (P06d permission; rule 7)','P','METRICS rule 7; P06d allows a set former'),
    (65,72,'set comprehension: mem(X,S1)'),(73,82,'set comprehension: not(mem(X,S2))'),
    (83,83,'comprehension predicate close'),(84,85,'comprehension result D'),
    (86,86,'setdiff definition close'),(87,94,'setdiff query')])
make('variants/P08c.redefine.ab1',[(0,6,'stage 2 query sequence constant'),
    (7,10,'stage 3 empty input constant'),(11,14,'stage 3 empty output constant')]+CONC+[
    (57,62,'stage 2: application of undefined rev'),
    (63,69,'stage 3: equation defining rev by the arriving case'),(70,75,'rev empty case contents'),
    (76,76,'stage 3 definition close'),
    (77,83,'stage 4: equation defining rev by the arriving case'),(84,90,'rev recursive case head'),
    (91,96,'rev recursive application'),(97,106,'rev recursive case conc application'),
    (107,107,'stage 4 definition close')])

ALL_RECORDS=list(records())
BEHAVIOUR={}

def size(ni,ui,nr,ur,bindings=None):
    return {'input':{'primitive_relations':ni,'unknown_occurrences':ui},
            'residual':{'relations_left_to_decide':nr,'unknown_occurrences_in_those_relations':ur},
            'retained_term_bindings':bindings,
            'convention':'Input counts posed data assertions on primitive arithmetic decomposition; procedure definitions excluded. Residual counts undecided processes, with solved term bindings shown separately; repeated occurrences counted, including fresh local unknowns.'}

def classify(r,s,a):
    p=r['subproblem']; k=s['stage']; c=a['computations'][0]
    states=c['execution_state']['states']
    e={'reached':True,'semantic':'complete','representation':'explicit',
       'simplification':None,'identical_to_posed':None,'residual_size':None,
       'execution_state':states,'residual_equivalence':None,
       'rule':'SPECIFICATION Outcomes 1–3; judged against '+p+' valid outcomes'}
    extra=''
    if p in ['P04d','P04f']:
        assert not a['observe']['raw']
        e.update(semantic='none reported',representation=None)
        extra='No state or answers were reported. Infinite answer completeness and enumeration order cannot be established from this record. No finite representation of all outcomes was reported.'
    elif p in ['P04a','P04b']:
        if p=='P04a' and r['configuration']=='absys-depth-first':
            e.update(representation='residual',simplification='reducible',identical_to_posed=True,
                     residual_size=size(2,2,2,2),
                     residual_equivalence='Equivalent: the printed to-do branches are loop(x) OR x=1. Under the specified least relation loop has no instances; their union is exactly x=1. The x=1 equation has not executed. A singleton explicit answer would be smaller.')
            extra='No executed x=1 binding: the finite branch is still queued. This is a complete conditional residual, not an obtained explicit answer; valid explicit answers obtained 0/1.'
        else:
            extra='x=1 is held and readable (1/1 valid explicit answers). The other branch still has loop(x) to do and denotes the empty set under the least relation. Class on the more explicit valid report, per Outcomes 2; retain the looping branch as an observation.'
    elif p in ['P04c','P04e']:
        extra='One successful derivation, no query unknowns: true (1/1). Ground recognition finishes in either case order.'
    elif p in ['P06a','P06c']:
        if k==1 or p=='P06a': e['semantic']='unsound'
        extra=('No solutions reported. Negation is decided at stage 1, before x is supplied: the subcomputation binds its own x to 1 and hibernates, and the parent fails. The matching cost trace has four printed events (not, equation, hibernate, fail), with five measured machine steps for the stage; it does not number the fail event by machine step. '
               'Stage 2 is delivered to the empty computation, not skipped. P06a and P06b therefore differ. No earlier conclusion is withdrawn.')
    elif p=='P06b':
        extra='x=2 (1/1). In stage 2 x is already ground when not(x=1) is decided; unlike P06a, no valid assignment was eliminated.'
    elif p=='P06d':
        extra='d=<1,3> (1/1), exactly the ordered difference for these constants.'
        if 'variants/' in r['program']['path']:
            extra+=' The named set variant deduplicates in general; this record contains no duplicate input elements and establishes no general sequence-multiplicity correctness.'
    elif p=='P06e1': extra='One successful derivation, no unknowns: true (1/1); BROWN lacks C301.'
    elif p=='P06e2': extra='No derivation: false, correctly detects that SMITH takes both maths courses.'
    elif p=='P06e3':
        extra="p='BROWN' (1/1). The matching cost trace starts each negation with both p and k ground (BROWN/SMITH and C101/C301); no unknown negation is used on this query."
    elif p.startswith('P07a'):
        extra='x=5, y=4, z=3 (1/1). The machine solves relations one at a time as values arrive and reactivates waiting arithmetic; no simultaneous elimination or value search is supplied. Compound x+y+z=12 has two primitive additions, including its fresh intermediate.'
    elif p=='P07b':
        e.update(representation='residual',simplification='reducible',identical_to_posed=False,
                 residual_size=size(2,4,2,4),residual_equivalence='Equivalent over integers: x+y=10 and 4+y=x are the original equations, the latter is a reorientation of x-y=4. Substitution gives 2y=6, y=3, x=7. The residual is reducible to that explicit pair.')
        extra='Two arithmetic processes wait; no elimination occurs. Identical flag is false because subtraction is stored as 4+y=x, although the size and denotation are unchanged.'
    elif p=='P07c':
        e.update(representation='residual',simplification='reduced',identical_to_posed=True,
                 residual_size=size(1,2,1,2),residual_equivalence='Equivalent: the held integer addition x+y=10 is exactly the posed relation. At least one relation on the two unknowns is required in the specified term vocabulary; this is reduced (the specification gives this example).')
        extra='One arithmetic process waits. All integer pairs are retained; no finite domain has been imposed.'
    elif p=='P07d':extra='w=7, u=2, v=14 (1/1), obtained by the native multiplication relation when the other two values become known.'
    elif p=='P07e':extra='No derivation survives: integer inconsistency is detected. 2w=15 has no integer solution; no rational or truncated answer is reported.'
    elif p=='P07f':
        e.update(representation='residual',simplification='inconsistency undetected',identical_to_posed=True,
                 residual_size=size(2,4,2,4),residual_equivalence='Equivalent to the empty valid outcome set: x+y cannot equal both 10 and 11. Subtracting the two equations gives 0=1. Both original equations are genuinely held arithmetic processes, so semantic completeness is separate from the undetected inconsistency.')
        extra='Two arithmetic processes wait; emptiness is not reported as no solutions.'
    elif p=='P07g':
        e.update(representation='residual',simplification='reducible',identical_to_posed=True,
                 residual_size=size(1,2,1,2),residual_equivalence='Equivalent over integers: x*x=9 iff (x-3)(x+3)=0 iff x=3 or x=-3. Both roots remain denoted, but neither is enumerated. The two explicit roots have zero relations left to decide, so this is reducible.')
        extra='One arithmetic process waits. The repeated operand x is one unknown in two operand places, not two known inputs; no root search occurs.'
    elif p.startswith('P08'):
        # Reading-specific semantics attached below.
        if p in ['P08a','P08b']:
            if k==1:
                e.update(representation='solved form',residual_equivalence='Equivalent under both readings: a=<x,y,z>; the element unknowns are free. No rev application has been posed.')
            elif k==2:
                e.update(representation='residual',simplification='reduced',identical_to_posed=False,
                         residual_size=size(2,6,1,4,'a=<x,y,z>'),
                         residual_equivalence='Open: equivalent; a=<x,y,z>, b free, and rev([x,y,z],b) is an explicitly pending application, not a decided relation. Closed: not equivalent; the held nonempty open state does not report the empty closed outcome set. The list equation is already a term binding; its substitution into the pending application makes the state nonidentical to the posed assertions.')
                extra='Undefined-state 4: computation awaiting its definition. It is visibly distinct from failure; no rev code or permission flag has arrived.'
            elif k==3:
                e.update(representation='residual',simplification='reducible',identical_to_posed=False,
                         residual_size=size(3,8,2,6,'a=<x,y,z>'),
                         residual_equivalence='Open: equivalent after identifying x=y; this yields a=<y,y,z>, b free, rev pending. Closed: not equivalent to no solutions. Reducible because the machine still holds x=y as an undecided equality process instead of replacing x by y in the term and application.')
                extra='Undefined-state 4 persists. One application and one equation between unknowns wait. Neither fails or is silently dropped.'
            elif k in [4,5]:
                nr=7 if k==4 else 8
                e.update(representation='residual',simplification='reducible',identical_to_posed=False,
                         residual_size=size(3 if k==4 else 4,8 if k==4 else 10,nr,2*nr,'a=<x,y,z>; b=<h5,h6,h1>'),
                         residual_equivalence=('Equivalent under both readings. Existentially eliminate local h1,...,h6 from the equality graph: '+
                             ('{x,y,h1,h2,h6} and {z,h3,h4,h5} are its two components, giving x=y and b=<z,y,y> with a=<y,y,z>.' if k==4 else
                              'all nine variables x,y,z,h1,...,h6 form one component, giving x=y=z and a=b=<z,z,z>.')+
                             ' These solved term forms are smaller than the held equality processes. See check_equivalence.py for the graph check against every such record.'))
                extra='The definition itself arrives at stage 4 and resumes rev, with conc also supplied at that stage. No procedure application remains; only equality processes between still-unknown elements remain suspended. No earlier no-solutions conclusion was reported or withdrawn.'
            else:
                extra='a=b=<42,42,42>, x=y=z=42, c=<42,42> (1/1), after the stage 6 prefix binds the equality component and wakes all waiting equations.'
        else:
            variant='variants/' in r['program']['path']
            if k==1:
                e.update(representation='solved form',residual_equivalence='Equivalent under both readings: conc is defined, no query application has been posed and b is free/absent.')
            elif k==2 or (k==3 and not variant):
                e.update(representation='residual',simplification='reduced',identical_to_posed=k==2,
                         residual_size=size(1,1,1,1),
                         residual_equivalence=('Open: equivalent to b free with the missing definition pending. '+
                            ('rev([1,2],b) is held directly.' if k==2 else 'The empty case cannot match [1,2]; the pending revmore([1,2],b) represents the missing recursive case.')+
                            ' Closed: not equivalent to the empty valid outcome set; the system treats the absent definition as unknown.'))
                extra=('Undefined-state 4: waits for rev itself.' if k==2 else 'The primary program resumes rev with its base case at stage 3, rejects that branch and retains one application of still-undefined revmore. Stage 4 supplies that code and reaches b=<2,1>.')
            elif variant:
                extra=('The arriving empty case resumes and fails the application on [1,2]. Under closed this correctly reports none; under open it wrongly loses the pending application.' if k==3 else
                       'No solutions remain after the second equation on rev. The application failed at stage 3; stage 4 is delivered, but cannot restore the failed derivation. No withdrawal of the earlier no-solutions conclusion occurs.')
            else:extra='b=<2,1> (1/1). The stage 3 revmore application resumes when its definition arrives at stage 4, without reposing or manual action.'

    raw=a['observe']['raw']
    unknown_lines=[z.strip() for z in (a['print'] or '').splitlines() if 'uninstantiated' in z or '(suspended:' in z]
    e['observations']={
        'reported_verbatim':a['print'],
        'answers_verbatim':[v['verbatim'] for q in c['queries'] for v in q['answers']],
        'unknowns':{'printed_uninstantiated_or_suspended_alias_lines':unknown_lines,
                    'explanation':('Unavailable: no state was printed.' if not raw else
                        'No surviving derivation; no unknown bindings survive.' if 'No derivation survives' in raw else
                        'Native named variables and finite list terms; equations between unknowns are held processes, not destructive aliases. A name reported as does not occur is free/unintroduced; see bindings_observed. Bound values and any pending arguments are preserved verbatim above.')},
        'bindings_observed':a['observe'].get('bindings'),
        'alternatives':c['alternatives'], 'suspended':c['suspended'],
        'conclusion_withdrawn':False,'manual_actions':a['manual_actions'],
        'steps':c['steps'],'store':a['store'],'error_verbatim':c['execution_state']['error_verbatim'],
        'detail':extra,
    }
    return e

def read_entries(f,x):
    r=x['run']; entries=[]
    for s in x['stages']:
        a=s['attempts'][-1]
        e=classify(r,s,a)
        base={'configuration':r['configuration'],'instance':r['instance'],
              'program':r['program']['path'].split('/'+r['configuration']+'/',1)[1],
              'record':str(f.relative_to(ROOT)),'stage':s['stage'],
              'harness_fault':f.name.endswith('.INVALID.json') or bool(x.get('harness_faults'))}
        if r['problem']!='P08':
            entries.append(base|e)
            continue
        for reading in ['open','closed']:
            er=base|e|{'reading':reading}
            p=r['subproblem'];k=s['stage'];variant='variants/' in r['program']['path']
            undefined=(p in ['P08a','P08b'] and k in [2,3]) or (p=='P08c' and (k==2 or k==3 and not variant))
            failed_partial=p=='P08c' and variant and k==3
            failed_final=p=='P08c' and variant and k==4
            er['semantic']='unsound' if (undefined and reading=='closed') or (failed_partial and reading=='open') or failed_final else 'complete'
            entries.append(er)
    return entries

for f,x in ALL_RECORDS:
    r=x['run']
    if r['mode']=='behaviour':
        entries=read_entries(f,x)
        DATA['outcomes']+=entries
        BEHAVIOUR[(r['configuration'],r['instance'],r['program']['path'])]=entries

AXES=['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence']
for f,x in ALL_RECORDS:
    r=x['run']
    if r['mode']=='behaviour':continue
    baseline=BEHAVIOUR[(r['configuration'],r['instance'],r['program']['path'])]
    for e,b in zip(read_entries(f,x),baseline):
        if any(e[k]!=b[k] for k in AXES):
            DATA['mode_differences'].append({
                'configuration':r['configuration'],'instance':r['instance'],'program':e['program'],
                'mode':r['mode'],'record':e['record'],'stage':e['stage'],
                'behaviour':{'record':b['record']}|{k:b[k] for k in AXES},
                'this_mode':{k:e[k] for k in AXES},
                'note':'Both safety-limit attempts (60s then 600s) time out in the original measurement build; behaviour is an unrequested SIGKILL error. Neither reports state or outcomes. The m2 rerun matches behaviour (none reported/error), so is not another mode-difference entry; its measurements are unavailable, not zero.'})

for conf in CONFIGS:
    for p in ['P04'+z for z in 'abcdef']+['P06'+z for z in ['a','b','c','d','e1','e2','e3']]+['P07'+z for z in 'abcdefg']+['P08a','P08b','P08c']:
        reason='The native equations, lambdas, disjunction and/or negation transcribe the given vocabulary and query without an added mechanism.'
        judgement='expressible'; direction=None
        if p in ['P04c','P04e']:direction='alist: recognise a supplied finite sequence'
        if p in ['P04d','P04f']:direction='alist: generate sequences'
        if p in ['P06a','P06c']:reason='Native not and equality transcribe the staged assertions (P tokens); the early operational decision is unsound on an unknown, as reported in outcomes. Expressibility does not assert successful solving or sound operational execution.'
        if p=='P06d':
            direction='setdiff: two ground sequences to difference'
            reason='The primary lambda has the three stated cases, in order, and uses native mem/not. The optional set variant is allowed syntactically by P06d and rule 7; its deduplication is not a faithful replacement for arbitrary repeated sequences.'
        if p.startswith('P06e'):direction='nonmajor: enumerate p' if p=='P06e3' else 'nonmajor: check supplied person'
        if p.startswith('P07'):
            reason='The integer arithmetic relations are native and directly transcribed. Inability to eliminate P07b/P07f or enumerate P07g is a solving limitation, not a missing means of stating the relations. All six P07a orders are explicitly requested instances, not reformulation moves.'
        if p=='P08a':
            reason='Native application of an unbound procedure name waits for the lambda value delivered at stage 4; the one rev/conc transcription also propagates later output information back to input elements.'
        if p=='P08b':reason='The undefined native procedure application remains held without an error, failure or added layer; code need never arrive.'
        if p=='P08c':
            judgement='expressible with reformulation'
            reason='A procedure is a single lambda value, so two later equations do not append its cases. The primary factors unknown future cases into revmore, an extra problem-specific relation (R 77–83, 86–92, 116), preserving the missing-code application and both specified cases on all inputs. The literal redefine variant loses the query at stage 3 and does not recover at stage 4. This factoring uses the native wait mechanism and adds no S layer.'
        directions=['rev: input spine to output','rev: later output information constrains input'] if p=='P08a' else [direction]
        for d in directions:
            DATA['expressibility'].append({'configuration':conf,'subproblem':p,'direction':d,'expressibility':judgement,'reason':reason})
    for program in ['P08a.ab1','P08b.ab1','P08c.ab1','variants/P08c.redefine.ab1']:
        evidence={
            'P08a.ab1':'Application 12–17 is delivered at stage 2; rev is uninstantiated and the printed application waits for a definition. Its code, tokens 21–62 (rev) and 63–104 (conc), is first delivered at stage 4 and resumes the application. Tokens 18–20 can add x=y in between. No flag or permission test exists.',
            'P08b.ab1':'Application 9–14 arrives at stage 2 and remains printed as waiting for a definition through stage 3 (15–17). There is no definition anywhere in this program. It is code awaited that never arrives.',
            'P08c.ab1':'Application 57–62 waits for rev at stage 2. Stage 3 gives rev (63–85); its empty case fails on [1,2] and its added application revmore (77–83) waits for that undefined name. Stage 4 delivers the revmore lambda (86–116), resumes it and yields b=[2;1]. The missing code itself is supplied in the stage, without a permission flag.',
            'variants/P08c.redefine.ab1':'Application 57–62 initially waits for the undefined rev, so kind is code awaited at stage 2. Definition 63–76 arrives at stage 3; its only case fails on [1,2], leaving no pending application. Stage 4 equation 77–107 supplies a different lambda and cannot recover the failed computation. Thus after the partial definition the application is neither held nor permission-gated.'}[program]
        DATA['late_definition'].append({'configuration':conf,'program':program,'kind':'code awaited','evidence':evidence})
    for first,others in TEXTS:
        program=first.split('/',1)[1]
        DATA['s_mechanisms'].append({'configuration':conf,'program':program,'mechanism':'none',
            'listed_at_phase_4':True,'tokens':0,
            'token_ranges':[],
            'reason':'harnesses/absys/S-mechanisms.md lists none. Uses only configuration core; P08c revmore is problem-specific factoring (R), not a general wait layer. No program supplies S.'})

def validate():
    assert set(DATA['tokens'])=={a for a,b in TEXTS}
    counts=Counter()
    for first,others in TEXTS:
        fn=ROOT/'results/absys/tokens'/(first+'.tokens.tsv')
        lines=fn.read_text().splitlines()[1:]
        indices=[int(z.split('\t')[0]) for z in lines]
        actual=[]
        for s in DATA['tokens'][first]:
            assert s['from']<=s['to'],(first,s)
            actual+=list(range(s['from'],s['to']+1))
            counts[s['class']]+=s['to']-s['from']+1
        assert actual==indices,(first,actual,indices)
        # Read permitted copies, check frozen index/line/token tables identical.
        for copy in others.split():
            assert (ROOT/'results/absys/tokens'/(copy+'.tokens.tsv')).read_bytes()==fn.read_bytes(),copy
            assert (ROOT/'programs/absys'/copy).read_bytes()==(ROOT/'programs/absys'/first).read_bytes(),copy
    assert len(DATA['outcomes'])==189
    assert len(DATA['mode_differences'])==12
    assert len(DATA['late_definition'])==12
    assert len(DATA['s_mechanisms'])==90
    assert len(ALL_RECORDS)==282
    return counts

if __name__=='__main__':
    counts=validate()
    (OUT/'absys.json').write_text(json.dumps(DATA,indent=2,ensure_ascii=False)+'\n')
    print('Frozen texts:',len(TEXTS),'classes:',dict(counts),'total:',sum(counts.values()))
    print('Behaviour records:',len(BEHAVIOUR),'outcome entries:',len(DATA['outcomes']))
    print('Semantics:',dict(Counter(e['semantic'] for e in DATA['outcomes'])))
    print('Representation:',dict(Counter(str(e['representation']) for e in DATA['outcomes'])))
    print('Execution:',dict(Counter(tuple(e['execution_state']) for e in DATA['outcomes'])))
    print('Mode differences:',len(DATA['mode_differences']))
