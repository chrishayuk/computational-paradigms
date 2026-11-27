#!/usr/bin/env python3
"""Independent classifier B. Reads only allowed source, frozen tokens and raw records.
No Prolog execution, imports of repository code, or tokenization.
"""
from pathlib import Path
import csv, json, re, collections, hashlib

ROOT=Path('/Users/christopherhay/cp-roles/classifier-B')
OUT=Path('/Users/christopherhay/cp-roles/classes-B/swi-prolog')
TOK=ROOT/'results/swi-prolog/tokens'
CONFIGS=['constraints','coroutines','plain','session','tabling']
TEXTS=list(csv.reader((TOK/'TEXTS.tsv').open(),delimiter='\t'))[1:]


def token_rows(path):
    rows=list(csv.DictReader((TOK/(path+'.tokens.tsv')).open(),delimiter='\t'))
    assert [int(x['index']) for x in rows]==list(range(len(rows)))
    return rows


def classify_tokens(path):
    rows=token_rows(path);t=[r['token'] for r in rows]; spans=[]
    def add(a,b,cl,construct,rule):
        if a<=b:spans.append(dict(from_=a,to=b,**{'class':cl},construct=construct,rule=rule))
    def body(a,b,functor):
        # Split goals using the frozen token indices, never by re-lexing source.
        groups=[];d=0;start=a
        for i in range(a,b+1):
            if t[i] in ('(', '['):d+=1
            elif t[i] in (')', ']'):d-=1
            elif t[i]==',' and d==0:
                groups.append((start,i-1));start=i  # rule 20: comma follows next construct
        groups.append((start,b))
        for lo,hi in groups:
            pos=lo+int(t[lo]==',');name=t[pos]
            if name=='when':
                # when(condition, nested evaluator): wrapper and condition C, evaluator P.
                depth=0;split=None
                for j in range(pos+2,hi+1):
                    if t[j] in ('(', '['):depth+=1
                    elif t[j] in (')', ']'):depth-=1
                    elif t[j]==',' and depth==0:split=j;break
                assert split is not None and t[hi]==')'
                add(lo,split-1,'C','when/2 delay wrapper and two-known-places wake condition','METRICS 1, 2, 10; C definition (coroutine call)')
                add(split,hi-1,'P','delayed arithmetic evaluator call','METRICS 3, 8, 10, 20; evaluator reading of 19')
                add(hi,hi,'C','closing delimiter of when/2','METRICS 10')
            elif name=='nonvar':
                add(lo,hi,'C','mode dispatch: test whether an arithmetic place is instantiated','METRICS 1, 2, 10, 20; tests instantiation, not a mathematical case-head condition')
            elif name=='!':
                add(lo,hi,'C','cut committing to the selected arithmetic mode or zero-divisor case','METRICS 1, 2, 10, 20; includes the factor/3 red cut')
            else:
                if name=='memberchk':
                    desc='read the current stage constant from the delivered constants list'
                    rule='METRICS 1, 9, 20; deterministic constant lookup is equivalent here; library(lists) external'
                elif name in ('r1','r2','r3'):
                    desc='pose '+name.upper()+' in the specified presentation order';rule='METRICS P definition, 1, 20'
                elif name in ('conc','rev'):
                    desc='application of the problem-defined '+name+' relation';rule='METRICS 1, 3, 20; unchanged cases and conjunct order'
                elif name in ('sum','sum_known','product','product_known','factor'):
                    desc='arithmetic evaluator application (including inverse integer multiplication)';rule='METRICS 3, 8, 20; evaluator reading of 19'
                else:
                    desc='arithmetic equation, exact divisibility test, or stage equality'
                    rule='METRICS 1, 3, 8, 20; evaluator reading of 19 for arithmetic directions'
                add(lo,hi,'P',desc,rule)
    start=0
    for end,v in enumerate(t):
        if v!='.':continue
        a=start;start=end+1;chunk=t[a:end]
        assert chunk
        if t[a]==':-':
            if t[a+1]=='table':add(a,end,'C','SLG tabling declaration for the problem relations','METRICS C definition, 1, 2, 12; external mechanism table/1')
            elif t[a+1]=='set_prolog_flag':add(a,end,'C','occurs_check=true named variant declaration','METRICS 2; changes operational unification and can change the solution set')
            else:
                assert t[a+1]=='use_module'
                add(a,end,'P','load library(clpfd) to express the integer arithmetic relations','METRICS 1, 12; external library, not experiment-written S')
        elif t[a] in ('unknowns','query') and ':-' not in chunk:
            add(a,end,'H','harness '+t[a]+' declaration','harnesses/swi-prolog/README.md 2.1 and 12; METRICS H definition, 13')
        elif ':-' not in chunk:
            add(a,end,'P','problem constant fact or base case of '+t[a],'METRICS 1, 3; sequence construction is the direct list encoding')
        else:
            mid=a+chunk.index(':-');fn=t[a]
            if fn=='stage':
                add(a,mid,'H','stage/3 interface head, including constants and unknowns arguments','harnesses/swi-prolog/README.md 2.1 and 12; METRICS 10')
            else:
                add(a,mid,'P',fn+' relation/evaluator clause head','METRICS 1, 3, 8, 10; arithmetic evaluator reading of 19; no added state argument')
            body(mid+1,end-1,fn)
            # A clause's full stop closes its last goal unless it is a nested control wrapper.
            cl='C' if fn in ('sum','product') and t[mid+1]=='when' else 'P'
            assert spans[-1]['class']==cl
            spans[-1]['to']=end  # keep terminating punctuation with its construct
    assert start==len(t)
    fixed=[]
    for s in spans:
        s['from']=s.pop('from_');fixed.append({k:s[k] for k in ['from','to','class','construct','rule']})
    assert [i for s in fixed for i in range(s['from'],s['to']+1)]==list(range(len(rows))),path
    return fixed

TOKENS={p:classify_tokens(p) for p,_ in TEXTS}
for primary,also in TEXTS:
    base=[x['token'] for x in token_rows(primary)]
    for alias in also.split():assert [x['token'] for x in token_rows(alias)]==base,(primary,alias)

RECORDS={}
for p in sorted((ROOT/'results/swi-prolog').glob('*/P0?/raw/*.json')):
    x=json.loads(p.read_text());run=x['run'];k=(run['configuration'],run['instance'],Path(run['program']['path']).name,run['mode'])
    assert k not in RECORDS
    RECORDS[k]=(p,x)
log=list(csv.reader((ROOT/'results/swi-prolog/batch-log.tsv').open(),delimiter='\t'))
assert len(log)==len(RECORDS)==270
assert {(r[1],r[2],r[3],r[4]) for r in log}==set(RECORDS)

REL_OCC={'R1':2,'R2':3,'R3':1}
TRIPLES=[(1,15,15),(2,14,7),(4,12,3),(8,8,1),(16,0,0),(-1,17,-17),(-2,18,-9),(-4,20,-5),(-8,24,-3),(-16,32,-2)]
# Exact finite check, not bounded enumeration of an unbounded problem.
DIVISORS=[u for u in range(-16,17) if u and 16%u==0]
assert set(TRIPLES)=={(u,16-u,16//u-1) for u in DIVISORS}
assert [q for q in TRIPLES if q[0]+10==12]==[(2,14,7)]


def information(inst,k):
    order=['R1','R2','R3'] if '.' not in inst else re.findall('R[123]',inst.split('.',1)[1])
    return order if inst=='P02c' else order[:k]


def assess(run,stage,attempt,reading=None,faults=None):
    cfg=run['configuration'];inst=run['instance'];prog=Path(run['program']['path']).name
    k=stage['stage'];c=attempt['computations'][0];q=c['queries'][0]
    answers=[z['verbatim'] for z in q['answers']];obs=attempt['observe'];raw=obs['raw'];bindings=obs['bindings'] or {}
    states=c['execution_state']['states'];err=c['execution_state']['error_verbatim'];restart=c['steps']['restart_cost_source'] or ''
    reached='before stage '+str(k)+' was posed' not in restart
    cl=dict(reached=reached,semantic=None,representation=None,simplification=None,identical_to_posed=None,residual_size=None,execution_state=None,residual_equivalence=None)
    reason=[];size=None;equiv=None
    if not reached:
        stopping=int(re.search(r'during stage (\d+)',restart).group(1))
        cl['status']='not reached';cl['stopped_by']={'stage':stopping,'execution_state':states,'error_verbatim':err,'source':restart}
        reason.append(f'Stage {k} was never entered: replay stopped in stage {stopping}. The restart-cost source says "budget", but the actual exception is an instantiation error; use the recorded exception, not that generic source wording.')
        rule='AMENDMENTS 3.2; SPECIFICATION Outcomes (axes do not apply to a stage never entered)'
    else:
        cl['execution_state']=states if c['execution_state']['determined'] else None
        if not c['execution_state']['determined']:
            reason.append('Execution state unavailable: the exception event is unreadable. The record\'s synthetic [error] is not evidence of a system error.')
        if inst=='P01a':
            cl.update(semantic='complete',representation='explicit' if k==3 else 'solved form')
            equiv={'equivalent':True,'reason':{1:'X and Y are the same logical variable; Z is free. This is exactly X=Y.',2:'X, Y and Z share one logical variable, exactly the two posed equations.',3:'Unification binds the shared variable to 2; all three values are 2.'}[k]}
            reason.append('Unknown equality is represented by variable sharing, not a suspended equation. '+equiv['reason'])
        elif inst=='P01b':
            cl.update(semantic='complete',representation='solved form' if k==1 else 'explicit')
            equiv={'equivalent':True,'reason':'The open list T=[1,2|S] decodes as T=<1,2>++S, for every finite sequence S. Substitution of S=<3> gives T=<1,2,3>.'}
            reason.append('List tails are interpreted in the problem\'s finite-sequence value encoding; an improper host term is not a new value of the mathematical sequence vocabulary. Stage 1 is a solved form without a pending conc call.')
        elif inst=='P01c':
            occurs='occurs-check' in prog
            if occurs:
                cl.update(semantic='complete' if reading=='finite' else 'unsound',representation='explicit')
                equiv={'equivalent':reading=='finite','reason':'occurs_check=true makes the self-unification fail and reports the empty set. This is exactly the finite reading, but omits the one rational solution.'}
                reason.append('No answers, query exhausted: this is an explicit report of no solutions, not none reported. occurs_check=true.')
            else:
                assert bindings.get('X')=='[1|X]'
                cl.update(semantic='unsound' if reading=='finite' else 'complete',representation='cyclic')
                equiv={'equivalent':reading=='rational','reason':'X=[1|X] is the unique rational stream 1,1,1,...; it is not finite. The bound cyclic value is read by observe(), including in the table-reset error case.'}
                reason.append('occurs_check=false. '+equiv['reason'])
                if cfg=='tabling':reason.append('No answer was delivered through answers(); the cyclic binding was nonetheless observed before the acyclic_term error unwound the stacks and counts as reported under SPECIFICATION Outcomes 1.')
        elif inst.startswith('P02'):
            rels=information(inst,k);s=set(rels)
            if 'error' in states:
                if not bindings:
                    cl['semantic']='none reported'
                    reason.append('Instantiation error before any answer or nontrivial observed binding. observe() prints true, which contains no held relation or binding and is not a report of the posed arithmetic relation.')
                else:
                    cl.update(semantic='unsound',representation='solved form')
                    u=int(bindings['U'])
                    witness={'U':u,'V':1 if u==0 else 0,'W':0 if u==0 else 1}
                    equiv={'equivalent':False,'reason':f'Only U={u} is observable; V and W are free and no arithmetic residual survives in the report. For example {witness} is admitted by that solved form but violates R2. A held binding counts as reported even at an error.'}
                    reason.append(equiv['reason'])
            elif s=={'R1','R2','R3'}:
                cl.update(semantic='complete',representation='explicit')
                equiv={'equivalent':True,'reason':'R3 gives U=12-10=2; R1 then gives V=16-2=14; R2 gives W=14/2=7. The recorded triple is exactly this unique solution.'}
                reason.append(equiv['reason'])
            elif s in ({'R3'},{'R1','R3'}):
                cl.update(semantic='complete',representation='solved form')
                equiv={'equivalent':True,'reason':'R3 gives U=2; '+('V=14 by R1 and W remains free.' if 'R1' in s else 'V and W remain free. Free unknowns range over the problem\'s declared integer domain.')}
                reason.append(equiv['reason'])
            else:
                assert s in ({'R1'},{'R2'},{'R1','R2'},{'R2','R3'}),s
                pending=[r for r in rels if r!='R3'];nocc=sum(REL_OCC[r] for r in pending)-(1 if 'R3' in s else 0)
                reducible=s=={'R1','R2'}
                cl.update(semantic='complete',representation='residual',simplification='reducible' if reducible else 'reduced',identical_to_posed='R3' not in s)
                cl['residual_size']={'unit':'primitive relations left to decide, then occurrences of unknowns in them; decided bindings counted separately','input':{'relations':len(rels),'unknown_occurrences':sum(REL_OCC[r] for r in rels)},'residual':{'relations':len(pending),'unknown_occurrences':nocc,'decided_bindings':1 if 'R3' in s else 0}}
                if s=={'R1'}:proof='U+V=16 is exactly R1. One primitive relation with two unknown occurrences is irreducible in the permitted solved-form grammar (which has no arithmetic expression terms); W is free.'
                elif s=={'R2'}:proof='W*U=V is exactly R2 over integers. It is one irreducible primitive relation with three unknown occurrences.'
                elif reducible:proof='The two held arithmetic relations are exactly R1 and R2. Eliminating V gives U*(W+1)=16; U is one of the ten nonzero signed divisors of 16, V=16-U, W=16/U-1. The exact divisor check in classify.py reproduces all ten specified triples. Ten explicit alternatives have zero relations left to decide, so this residual is reducible.'
                else:proof='R3 gives U=2. Substituting into R2 leaves 2*W=V, for every integer W. There is one undecided relation with two unknown occurrences; the solved-form grammar cannot express multiplication as a term. The held representation is reduced and differs from the originally posed two equations.'
                equiv={'equivalent':True,'reason':proof}
                reason.append(proof)
                if cfg=='coroutines':reason.append('Each when/2 payload is read as its held integer relation: sum_known computes a missing sum place or tests the sum; product_known/factor computes a missing product place, handles zero, and tests exact integer divisibility. Its wake condition affects when it runs. It imposes no finite domain. The size and identical flag compare decoded primitive mathematics, not the when/2 syntax.')
                else:reason.append('CLPFD #= holds an integer constraint, with no program-imposed finite bounds and no labeling. The size and identical flag compare primitive mathematics, not rendering punctuation.')
        elif inst.startswith('P03'):
            if inst=='P03f' and cfg=='tabling':
                cl['semantic']='none reported';reason.append('Table computation raises resource_error(private_table_space) before delivering an answer. observe() has no binding. The missing step, suspended-state, and retained-alternative figures are unavailable.')
            elif inst=='P03f' and bindings:
                candidate=bindings['A'];n=candidate.count('_')
                assert candidate.startswith('[') and candidate.endswith(']') and n>3
                cl.update(semantic='unsound',representation='explicit')
                equiv={'equivalent':False,'reason':f'The collected A=<3,2,1> is exactly the sole valid solution. But observe() also reports a proper list skeleton of length {n}, every element free, at budget exhaustion; no such list can reverse to a length-3 list. Under SPECIFICATION Outcomes 1 this binding counts as reported, so the total report includes invalid outcomes. Representation uses the more explicit valid collected answer; the invalid held solved form is recorded separately.'}
                reason.append(equiv['reason'])
            else:
                cl.update(semantic='complete',representation='explicit')
                proof={'P03a':'Concatenating <1,2> and <3> gives exactly <1,2,3>.','P03b':'The prefix lengths 0, 1 and 2 exhaust the splits of <1,2>; the three recorded pairs are exactly those splits, in that order.','P03c':'Removing prefix <1> from <1,2,3> gives exactly suffix <2,3>.','P03d':'Removing suffix <3> gives exactly prefix <1,2>.','P03e':'The given rev cases reverse <1,2,3> to exactly <3,2,1>.','P03f':'The sole collected answer A=<3,2,1> is exactly the valid result. The storage record loses the exception/boundary event, so no additional binding is readable; its execution state and boundary measurements are unavailable.'}[inst]
                equiv={'equivalent':True,'reason':proof};reason.append(proof)
        else:raise AssertionError(inst)
        cl['residual_equivalence']=equiv
        rule='SPECIFICATION Outcomes 1, 2, 3; '+('P01 two readings; ' if inst=='P01c' else '')+('SPECIFICATION Outcomes 1 (observe-readable bindings count as reported); ' if bindings and ('budget' in states or 'error' in states) else '')+'AMENDMENTS 3.1; '+inst[:3]+' valid outcomes'
    # Common observations: retain evidence without treating missing metrics as zeros.
    unknowns='Logical Prolog variables; aliases are shared variables and unbound places are free within the problem\'s declared value domains.'
    if cl['representation']=='cyclic':unknowns='Rational cyclic list X=[1|X], rendered explicitly as a self-reference.'
    elif cl['representation']=='residual':unknowns='Attributed logical variables carrying CLPFD constraints.' if cfg in ('constraints','session') else 'Logical variables linked to attributed when/2 suspension conditions; some shared when state can account for several watched variables.'
    if not reached:unknowns='No new stage state exists; observe() describes the aborted replay only.'
    at=c['alternatives'];su=c['suspended'];steps=dict(c['steps'])
    if not c['execution_state']['determined']:
        # A retained last-answer count cannot measure the missing stage end.
        steps.update(restated=None, to_end=None, budget_exhausted=None)
    observations={
        'classification_reason':' '.join(reason),
        'answers_verbatim':answers,
        'observe_raw':raw,
        'observe_bindings':obs['bindings'],
        'observe_method':obs['method'],
        'unknowns_representation':unknowns,
        'alternatives':at,
        'suspended':su,
        'steps':steps,
        'manual_actions':attempt['manual_actions'],
        'conclusions_withdrawn':[],
        'posing':attempt['posed'],
        'answers_collected_on':q['collected_on'],
        'answer_collection_ended_by':q['ended_by'],
        'error_verbatim':err,
        'metrics_note':'null is unavailable, never zero. Steps here are behaviour evidence; cost-mode counts are the measurement of record. Peak store and exact alternatives are unavailable in behaviour unless explicitly measured. Repeated work and problem-operation counts are not supplied by these programs.',
        'problem_operations':c['problem_operations'],
        'store':attempt['store'],
        'raw_execution_state':c['execution_state']
    }
    if reached:
        if inst=='P01a':expected='infinite' if k<3 else 1
        elif inst=='P01b':expected='infinite' if k==1 else 1
        elif inst=='P01c':expected=0 if reading=='finite' else 1
        elif inst.startswith('P02'):
            info=set(information(inst,k))
            expected=1 if info=={'R1','R2','R3'} else 10 if info=={'R1','R2'} else 'infinite'
        else:expected=3 if inst=='P03b' else 1
        observations['answer_completeness']={
            'expected_solution_cardinality':expected,
            'collected_answer_forms':len(answers),
            'equivalent_finite_representation':cl['semantic']=='complete',
            'no_solutions_reported':not answers and q['ended_by']=='exhausted' if expected==0 else None,
            'invalid_observed_binding_forms':1 if cl['semantic']=='unsound' and bindings else 0,
            'note':'A residual answer can denote many or infinitely many solutions. Collected answer-form counts are not counts of individual solutions; observe-readable bindings are also reports under Outcomes 1.'
        }
    else:observations['answer_completeness']=None
    if inst=='P03f' and bindings:observations['invalid_observed_list_length']=bindings['A'].count('_')
    if cfg=='session' and k<max_stage(run):observations['session_note']='Answers are collected on a separate prefix run; observe() reads this incremental engine. Waiting for the next stage in the harness is not problem-level suspended work.'
    if inst.startswith('P02') and cl['representation']=='explicit' and cfg=='coroutines':observations['resumption_note']='Binding U from R3 wakes the held sum; deriving V permits the product/factor to derive W. No trace of examination counts is supplied; do not infer repeated-work counts from this dependency reasoning.'
    cl['observations']=observations
    cl['rule']=rule
    return cl


def max_stage(run):
    return 3 if run['instance']=='P01a' or run['instance']=='P02a' or run['instance'].startswith('P02b') else 2 if run['instance']=='P01b' else 1

OUTCOMES=[];DIFFS=[]
AXES=['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence']
for key,(p,x) in RECORDS.items():
    if key[-1]!='behaviour':continue
    run=x['run'];assert len(x['stages'])==max_stage(run)
    for s in x['stages']:
        assert len(s['attempts'])==1
        for reading in (['finite','rational'] if run['instance']=='P01c' else [None]):
            cl=assess(run,s,s['attempts'][-1],reading,x['harness_faults'])
            item=dict(configuration=key[0],instance=key[1],program=key[2],record=str(p.relative_to(ROOT)),stage=s['stage'],reading=reading,**cl)
            OUTCOMES.append(item)
            for mode in ['cost','storage']:
                pm,xm=RECORDS[key[:-1]+(mode,)];sm=next(z for z in xm['stages'] if z['stage']==s['stage']);am=sm['attempts'][-1]
                other=assess(xm['run'],sm,am,reading,xm['harness_faults'])
                # Proof wording is not itself a difference in a classification.
                compared=[a for a in AXES if a!='residual_equivalence']
                if any(cl[a]!=other[a] for a in compared) or ((cl['residual_equivalence'] or {}).get('equivalent') != (other['residual_equivalence'] or {}).get('equivalent')):
                    DIFFS.append(dict(configuration=key[0],instance=key[1],program=key[2],mode=mode,record=str(pm.relative_to(ROOT)),stage=s['stage'],reading=reading,behaviour={a:cl[a] for a in AXES},this_mode={a:other[a] for a in AXES},note='Storage instrumentation fault: unreadable/interleaved at_exception event; the synthetic error is not a measured system execution state. The sole collected answer is valid, but the invalid speculative budget binding visible in behaviour/cost is unavailable here. Record-level fault and unavailable measurements are preserved; no inference that the model completes or errors is drawn.',harness_faults=xm['harness_faults'],raw_execution_state=am['computations'][0]['execution_state'],observations=other['observations']))

EXPRESS=[]
for cfg in CONFIGS:
    for sub in ['P01a','P01b','P01c','P02a','P02b','P02c','P03a','P03b','P03c','P03d','P03e','P03f']:
        direction={'P03a':'conc: known first and second, unknown whole','P03b':'conc: unknown first and second, known whole','P03c':'conc: known first and whole, unknown second','P03d':'conc: unknown first, known second and whole','P03e':'rev: known first, unknown second','P03f':'rev: unknown first, known second'}.get(sub)
        if sub.startswith('P01'):
            why='Equality and list construction are transcribed by unification; conc uses exactly the two cases in order. '+('The finite and rational readings are separately representable using the recorded occurs-check settings; the tabling cyclic error concerns execution, not a missing transcription.' if sub=='P01c' else 'An open tail is the problem\'s symbolic finite-sequence suffix, with no changed algorithm.')
        elif sub.startswith('P02'):
            if cfg in ('constraints','session'):why='CLPFD #= directly states the primitive integer sum and product relations, without finite domain bounds or labeling. No R tokens. Session changes the posing mechanism, not expressibility.'
            else:why='The sum/product evaluator expresses the primitive arithmetic relation in all known-place directions; arithmetic computations and exact-divisibility/zero cases are P, instantiation tests and cuts are C (METRICS 3, 8 and evaluator reading of 19). '+('when/2 supplies C suspension around the unchanged evaluators. No new mathematical relation, state argument or reordered equation is introduced.' if cfg=='coroutines' else 'The insufficiently instantiated calls error in several presentation orders; expressibility is kept separate from success/termination. This judges a transcription of arithmetic, not availability of a native relational arithmetic solver. No R tokens. Rule 19 explicitly discusses imperative holding code; here its evaluator principle agrees with rules 3 and 8, while native Prolog mode tests are C under rules 1 and 2.')
        else:why='The same conc/rev clauses transcribe every stated case and conjunct in presentation order, with no extra argument or separately written direction function (METRICS 3, 14). '+('SLG declarations are C; table-space exhaustion does not remove the transcription.' if cfg=='tabling' and sub=='P03f' else 'Backwards reverse may exhaust the budget while seeking another answer; this is an operational result.')
        EXPRESS.append(dict(configuration=cfg,subproblem=sub,direction=direction,expressibility='expressible',reason=why))
    # All six posed order instances are independently identified as well as the P02b umbrella.
    for order in ['R1R2R3','R1R3R2','R2R1R3','R2R3R1','R3R1R2','R3R2R1']:
        base=next(v for v in EXPRESS if v['configuration']==cfg and v['subproblem']=='P02b')
        EXPRESS.append(dict(base,subproblem='P02b.'+order,reason=base['reason']+' The stage order is exactly '+order+'.'))

RESULT=dict(tokens=TOKENS,outcomes=OUTCOMES,mode_differences=DIFFS,expressibility=EXPRESS)
(OUT/'swi-prolog.json').write_text(json.dumps(RESULT,indent=2,ensure_ascii=False)+'\n')
counts=collections.Counter()
for spans in TOKENS.values():
    for sp in spans:counts[sp['class']]+=sp['to']-sp['from']+1
print(json.dumps({'distinct_texts':len(TOKENS),'token_totals':dict(counts),'outcomes':len(OUTCOMES),'reached':collections.Counter(o['reached'] for o in OUTCOMES),'semantic':dict(collections.Counter(o['semantic'] for o in OUTCOMES)),'representations':dict(collections.Counter(o['representation'] for o in OUTCOMES)),'execution':dict(collections.Counter(str(o['execution_state']) for o in OUTCOMES)),'simplification':dict(collections.Counter(o['simplification'] for o in OUTCOMES)),'mode_differences':len(DIFFS),'expressibility':len(EXPRESS)},indent=2))
