"""Independent classification; reads only the brief's permitted source paths.

This script reads records, never executes an Absys program. Token boundaries
come exclusively from the frozen TSVs. Semantic arguments are stated below and
in absys.notes.md; finite arithmetic assertions here are cross-checks, not a
replacement for the unbounded proofs.
"""
from pathlib import Path
from collections import Counter
import csv, json, gzip, hashlib, re

ROOT=Path('/Users/christopherhay/cp-roles/classifier-1C-B')
OUT=Path(__file__).parent
CONFIGS=['absys','absys-depth-first','absys-wake-back']
manifest=list(csv.reader((ROOT/'results/absys/tokens/TEXTS-1C-P09-P11.tsv').open(),delimiter='\t'))[1:]
result=dict(tokens={},outcomes=[],mode_differences=[],expressibility=[],late_definition=[],s_mechanisms=[])

def span(a,b,c,construct,rule):
    return dict(from_=a,to=b,**{'class':c},construct=construct,rule=rule)
def specs(rows):
    return [{('from' if k=='from_' else k):v for k,v in span(*row).items()} for row in rows]
def constants(a,b):return (a,b,'P','stage constants table','P: stage information; rule 10')
def p(a,b,what):return (a,b,'P',what,'rules 1, 2, 3, 10; arithmetic decomposition is P')
def r(a,b,what):return (a,b,'R',what,'R definition; rules 4, 5, 10 as applicable')
def hist(a,b,c,d,e):
    return [r(a,b,'version-history append and conjunction opening'),p(c,d,'new scalar value equation'),r(e,e,'version-history conjunction closing')]

revdefs=[p(9,18,'loop definition'),p(19,60,'conc definition, empty then recursive case'),p(61,102,'rev definition, empty then recursive case')]
result['tokens']['absys/P09a.ab1']=specs([constants(0,8),*revdefs,p(103,106,'computation A query'),p(107,112,'computation B query')])
result['tokens']['absys/P09b.ab1']=specs([constants(0,2),constants(3,5),constants(6,8),p(9,16,'computation A contradictory conjunction'),p(17,19,'computation B equality')])
result['tokens']['absys/P09c.ab1']=specs([
 constants(0,2),constants(3,5),r(6,22,'integer greater-than definition through positive difference'),r(23,39,'integer less-or-equal definition through nonnegative difference'),r(40,60,'positive-integer least relation'),r(61,76,'nonnegative-integer definition'),
 p(77,84,'gen definition opening'),p(85,88,'gen empty-sequence head'),r(89,94,'greater-than comparison replacement'),p(95,102,'gen second case and sequence head'),r(103,108,'less-or-equal comparison replacement'),p(109,119,'gen successor and recursive application'),p(120,121,'gen definition closing'),p(122,147,'sum3 head and arithmetic definition'),p(148,161,'producer and consumer conjunction')])
result['tokens']['absys/P09d.ab1']=specs([constants(0,2),p(3,28,'genu head, successor and recursion'),p(29,54,'sum3 head and arithmetic definition'),p(55,68,'unbounded producer and consumer conjunction')])
result['tokens']['absys/P09e.ab1']=specs([constants(0,2),constants(3,5),p(6,17,'two mutually dependent arithmetic relations')])
result['tokens']['absys/P10a.ab1']=specs([constants(0,2),constants(3,5),constants(6,8),*hist(9,16,17,19,20),*hist(21,28,29,33,34),*hist(35,42,43,45,46)])
result['tokens']['absys/P10b.ab1']=specs([constants(0,2),constants(3,5),constants(6,8),constants(9,11),r(12,17,'history-mapping procedure header'),(18,19,'C','key p: await a history cell','C key declaration; rules 1, 10'),r(20,44,'history mapping cases and list-head equations'),p(45,49,'standing multiplication on one history value'),r(50,57,'history mapping recursion and closing'),r(58,63,'replace scalar standing relation by history mapping'),*hist(64,71,72,74,75),*hist(76,83,84,88,89),*hist(90,97,98,100,101)])
result['tokens']['absys/P10c.ab1']=specs([constants(0,2),constants(3,5),constants(6,8),constants(9,11),*hist(12,19,20,22,23),*hist(24,31,32,36,37),*hist(38,45,46,50,51),*hist(52,59,60,62,63)])
result['tokens']['absys/P10d.ab1']=specs([constants(0,2),constants(3,5),constants(6,8),constants(9,11),p(12,30,'pick closed-world facts in order'),r(31,47,'greater-than through positive difference'),r(48,68,'positive-integer least relation'),p(69,72,'pick query'),r(73,78,'greater-than replacement call'),r(79,82,'restate pick on a fresh version in place of withdrawal')])

def effect_spans(start):
    # The leading goal separator is H (20); the comma introducing the
    # problem argument is P (20), despite the harness's five-token shorthand.
    return [(start,start+3,'H','emit adapter opening, including preceding goal separator','rules 10, 13, 20; harness README 3.12'),p(start+4,start+5,'emit problem argument with its preceding separator'),(start+6,start+6,'H','emit adapter closing','rules 10, 13; harness README 3.12')]
for name in ['P11c.abs','P11d.abs']:
    result['tokens']['absys/'+name]=specs([constants(0,2),constants(3,5),constants(6,8),constants(9,11),p(12,32,'pick closed-world facts'),p(33,37,'stage conjunction opening and pick query'),*effect_spans(38),p(45,45,'stage conjunction closing'),p(46,51,'inequality by negated equality on ground pick outcomes')])
for name,split in [('P09a.AB.or.ab1',108),('P09a.BA.or.ab1',110)]:
    result['tokens']['absys/variants/'+name]=specs([constants(0,8),*revdefs,r(103,103,'disjunction wrapper replacing independent spawn'),p(104,split-1,'first computation query'),r(split,split,'disjunction replacing independent spawn'),p(split+1,114,'second computation query'),r(115,115,'disjunction wrapper closing')])
result['tokens']['absys/variants/P09b.or.ab1']=specs([constants(0,2),constants(3,5),constants(6,8),r(9,9,'disjunction wrapper replacing independent spawn'),p(10,17,'contradictory computation A'),r(18,18,'disjunction replacing independent spawn'),p(19,21,'computation B equality'),r(22,22,'disjunction wrapper closing')])
for name in ['P11a.ne.abs','P11b.ne.abs']:
    rows=[constants(0,2),constants(3,5),constants(6,8),r(9,11,'constant for the changed comparison, one excluded value'),p(12,32,'pick closed-world facts'),p(33,37,'stage conjunction opening and pick query')]
    if name.startswith('P11a'):
        rows += [r(38,44,'negated equality replacing greater-or-equal, including separator'),*effect_spans(45)]
    else:
        rows += [*effect_spans(38),r(45,51,'negated equality replacing greater-or-equal, including separator')]
    rows += [p(52,52,'stage conjunction closing')]
    result['tokens']['absys/variants/'+name]=specs(rows)

token_totals=Counter(); per_text={}; shared_checks=[]
for primary,others in manifest:
    rows=list(csv.DictReader((ROOT/'results/absys/tokens'/(primary+'.tokens.tsv')).open(),delimiter='\t'))
    indices=[int(x['index']) for x in rows]
    assert indices==list(range(len(rows)))
    spans=result['tokens'][primary]
    coverage=[i for s in spans for i in range(s['from'],s['to']+1)]
    assert coverage==indices,(primary,coverage,indices)
    counts=Counter()
    for s in spans:counts[s['class']]+=s['to']-s['from']+1
    per_text[primary]=dict(counts);token_totals.update(counts)
    for other in others.split():
        oo=list(csv.DictReader((ROOT/'results/absys/tokens'/(other+'.tokens.tsv')).open(),delimiter='\t'))
        assert [(x['index'],x['token']) for x in rows]==[(x['index'],x['token']) for x in oo]
        # Read only the permitted program files, also checking the source bytes.
        assert (ROOT/'programs/absys'/primary).read_bytes()==(ROOT/'programs/absys'/other).read_bytes()
        shared_checks.append(other)
assert set(result['tokens'])=={m[0] for m in manifest}

# Unbounded semantic arguments: by induction pos denotes exactly positive
# integers; nonneg exactly nonnegative integers. Existential differences then
# give a>b and a<=b over ALL integers, without imposing a finite domain.
# x=y+1 AND y=x-1 reduces algebraically to x=y+1 over Z.
assert all((x==y+1 and y==x-1)==(x==y+1) for x in range(-30,31) for y in range(-30,31))
assert [10,10+5,7]==[10,15,7]
assert [2*x for x in [10,15,7]]==[20,30,14]
assert sum([1,2,3])==6

def read_record(path):
    with (gzip.open(path,'rt') if path.suffix=='.gz' else path.open()) as f:return json.load(f)
def key(rec):
    r=rec['run'];return (r['configuration'],r['instance'],r['program']['path'])
paths=[f for cfg in CONFIGS for pr in ['P09','P10','P11'] for directory in ['raw','raw-rerun-m2'] for f in sorted((ROOT/'results/absys'/cfg/pr/directory).glob('*.json*')) if not f.name.endswith('.jsonl')]

def ref_value(text,pointer,limit=8000):
    if len(text)<=limit:return text
    return {'record_json_pointer':pointer,'characters':len(text),'sha256':hashlib.sha256(text.encode()).hexdigest(),'note':'Verbatim content remains at this pointer in the cited raw record; no long-list truncation is treated as an answer.'}

def classify(rec,path,stage,attempt,comp,reading=None):
    run=rec['run'];cfg=run['configuration'];inst=run['instance'];sub=run['subproblem'];k=stage['stage'];a=attempt;c=comp
    prog=run['program']['path'].removeprefix('programs/absys/'+cfg+'/')
    ci=a['computations'].index(c);ai=stage['attempts'].index(a);si=rec['stages'].index(stage)
    ptr=f'/stages/{si}/attempts/{ai}'
    raw=a['observe']['raw'] or ''
    ans=''.join(v['verbatim'] for q in c['queries'] for v in q['answers'])
    e=dict(configuration=cfg,instance=inst,program=prog,record=str(path.relative_to(ROOT)),stage=k,attempt=a['attempt'],final_attempt=a is stage['attempts'][-1],computation=c['id'],reading=reading,reached=True,semantic='complete',representation='explicit',simplification=None,identical_to_posed=None,residual_size=None,input_size=None,execution_state=c['execution_state']['states'][:],residual_equivalence=None,harness_fault='.INVALID.' in path.name,rule='SPECIFICATION Outcomes 1–3; problem valid outcomes')
    commentary=[];equiv=None
    # Do not turn a replay timeout into a failure of the stage it never reached.
    if sub=='P10d' and k==3:
        e.update(reached=False,semantic=None,representation=None,execution_state=[],rule='AMENDMENTS 3.2: not reached; replay of stage 2 did not return')
        e['stopped_by']={'stage':2,'execution_state':['timeout'],'reason':'Replay of gt(x,1) did not finish within this attempt’s safety limit; no state from stage 3 was observed.'}
        commentary.append('Stage 3 is not reached. The record’s timeout belongs to replay of stage 2. The separate restart-cost run later reporting 1000014 steps is a different process and does not establish that this attempt reached stage 3.')
    elif 'timeout' in e['execution_state'] or 'error' in e['execution_state']:
        assert not ans
        e.update(semantic='none reported',representation=None)
        commentary.append('No current-stage answer or observable state was captured before the stop; prior-stage stdout during replay is not a current-stage answer.')
    elif sub.startswith('P09a'):
        if c['id']=='A':
            finished_blocks=[v['verbatim'] for q in c['queries'] for v in q['answers'] if '(hibernating)' in v['verbatim']]
            if 'variants/' in prog and finished_blocks:
                e.update(semantic='unsound',representation='solved form')
                equiv='Not equivalent: query A receives the same untagged disjunction state as B. Its surviving reverse branch leaves x free, whereas loop(x), read least, has no solutions. A B-only derivation must not be silently removed from A’s returned query.'
                commentary.append('The OR variant does not tag or separate computation answers; a completed B branch is also in query A’s report.')
            else:
                e.update(semantic='none reported',representation=None)
                commentary.append('loop has no finite derivation. Its still-running goal is execution work, not an assertion of a finished free-x answer.')
        else:
            if re.search(r'\bb = \[3;2;1\]',ans):
                equiv='Equivalent on B’s unknown: the completed/observable binding b=[3;2;1] is the unique reverse of [1;2;3]. A pending least-loop branch has no solutions; its absent b is not a free-b completed answer.'
            else:
                e.update(semantic='none reported',representation=None)
                commentary.append('B has no observable binding. In the primary AB order loop is ahead of rev in the same conjunction; in depth-first AB.or the loop alternative prevents the queued reverse branch from running.')
        commentary.append('spawn side_by_side is false. The primary feeds assertions into one conjunction; BA obtains B before adding A, AB does not. OR variants place the computation queries in pre-spawn text; their textual OR order, not the instance’s empty spawn subsections, controls scheduling.')
    elif sub=='P09b':
        if c['id']=='A':
            if 'variants/' in prog:
                e.update(semantic='unsound',representation='solved form')
                equiv='Not equivalent for A: its query returns the surviving y=3 derivation with x absent/free, although x=1 and x=2 has no solution. The raw report has no computation tag that would make it an empty answer set for A.'
            else:
                commentary.append('No derivation survives: A’s empty valid outcome is explicitly detected.')
        elif 'variants/' not in prog:
            e['semantic']='unsound';commentary.append('A destroyed the only derivation. B also reports no derivation, although its independent query requires y=3.')
        else:
            equiv='Equivalent for B: y=3 is the sole surviving solved branch. A’s inconsistent branch has disappeared.'
        commentary.append('Failure isolation is absent in the primary. The disjunction variant isolates derivation failure, but returns one shared untagged state for both named computations.')
    elif sub=='P09c':
        assert 'total = 6' in raw
        equiv='Equivalent: the hibernating derivation has s=[1;2;3;4;5], total=6, exactly the singleton valid outcome. Induction on pos/nonneg makes gt/le exact integer comparisons; each remaining branch requires pos of a nonpositive integer or an impossible ground equality, hence has no solutions. These running branches do not invalidate the valid explicit form.'
        commentary.append('One of 16 derivations is hibernating with the valid explicit answer; 15 still run at budget. Producer gen finishes in the successful branch before sum3 runs. The goal lists of unfinished branches put comparison work and gen ahead of sum3; they are pending work, not suspended processes. No trace establishes consumer progress before producer completion.')
    elif sub=='P09d':
        e.update(semantic='none reported',representation=None,rule='P09d1 finite exception / P09d2 observed total criterion; SPECIFICATION Outcomes reported bindings')
        commentary.append('s has the materialized prefix 1 through 333333 and an open tail. The pending goal starts by constructing element 333334, then recurses into genu, with sum3 still behind it. total does not occur: the consumer has not computed 6. This is neither an infinite value report nor a finished finite answer; both readings are none reported. Running producer work is distinguished from a stopped residual constraint store.')
    elif sub=='P09e':
        e.update(representation='residual',simplification='reducible',identical_to_posed=False,residual_size={'relations':2,'unknown_occurrences':4,'conditions':'y+1=x AND y+1=x'},input_size={'relations':2,'unknown_occurrences':4,'conditions':'x=y+1 AND y=x-1'})
        equiv='Equivalent over all integers: y=x-1 iff x=y+1. The two stored copies of y+1=x therefore denote exactly the required pairs. Removing either duplicate gives one relation (2 unknown occurrences), so the report is reducible. Identical-to-posed is false literally: subtraction was normalized into addition and equality orientation changed, although neither posed constraint was discharged.'
        commentary.append('x and y remain uninstantiated; two arithmetic relations wait for the other integer operand. This is distinguishable from completion by both the suspended-process listing and its count 2; it is not reported as a deadlock.')
    elif sub in ['P10a','P10b','P10c']:
        if sub=='P10b':
            e.update(representation='residual',simplification='reduced' if k==1 else 'reducible',identical_to_posed=False,residual_size={'relations':1 if k==1 else 2,'unknown_occurrences':2 if k==1 else 4,'conditions':'dbl(b,d)' if k==1 else f'bt{k-1}=s AND dbl(s,u)','basis':'one relation per undecided held application/equality; dbl denotes the per-cell primitive multiplication, with history continuation overhead retained'},input_size={'relations':1 if k==1 else 2,'unknown_occurrences':2 if k==1 else 3,'basis':'current problem information: d=2*b, plus b=current scalar after a replacing stage; old versions existentially projected'})
            equiv='Equivalent under the program’s explicit history encoding: dbl pairs each arrived b cell with a d cell satisfying d=2*b. At stage 1 it holds that standing relation for values to arrive; no scalar value is assigned. After replacements the last arrived pairs are (10,20), (15,30), (7,14). The remaining equation identifies history tails and dbl waits for the next cell; existentially projecting future cells leaves precisely the valid current values. Stage 1 needs one undecided multiplication relation. At later stages current values are explicit after decoding and the future-tail constraints can be omitted for this stage, so that raw residual is reducible.'
            commentary.append('One dependent d value is computed for each newly appended b value; old d values persist. key delays recursive mapping until another history cell arrives. Boundary suspension count is 1 initially, then 2 (tail equality plus key-waiting dbl).')
        else:
            e['representation']='solved form'
            equiv='Equivalent under the declared version-history projection: the current quantity is the last cell supplied so far, not an arbitrary future cell of its open tail. P10a gives b=10,15,7. P10c gives b=10 initially with d unconstrained; then d=20, retained when b becomes 15 and 7. The printed histories are finite terms with free tails and no undecided relation, hence solved form rather than raw scalar explicit output.'
        commentary.append('Replacement is reformulated by fresh value/tail names. Earlier values remain retrievable in the histories; no binding is erased. A changed current-value conclusion is superseded by changing the version interpreted as current, with both old and new versions still printed. Free tails are Absys unknowns. No manual restart or edit is required.')
    elif sub=='P10d':
        assert k==1
        equiv='Equivalent: pick’s three facts produce exactly x=1,2,3. No comparison has arrived yet.'
    elif sub.startswith('P11'):
        # These are any-one queries. observe holds more than answers(1).
        equiv='Equivalent for the any-one query: answers(1) returns a valid current x. observe also exposes all surviving ground alternatives. The P11 cannot-select rule judges semantics against the pre-commit outcomes when no v is selected; no binding x=v may be inferred from the first printed answer.'
        commentary.append('The current surviving x values are '+(', '.join(re.findall(r'^    x = (\d+)$',raw,re.M)))+'. All are held derivations, not alternatives pending for a further answers request. answers(1) reads the first but does not stop the machine from performing other branches’ effects.')
        if sub in ['P11c','P11d']:
            commentary.append('No commitment is selected: the commit section is empty, all surviving derivations persist, and replayed_commitments is empty. Negated ground equality removes derivation x=1 at '+('stage 2' if sub=='P11c' else 'stage 3')+'; its previously emitted entry remains in external L. P11d therefore did not commit to v=1 merely because x=1 was printed first, and stage 3 is judged using the stipulated no-selection fallback.')
        e['effects']='extra' if k==({'P11c':3,'P11d':3}.get(sub,1)) else None
        e['effects_at_problem_end']='extra'
        effects=[ef for s in rec['stages'] for at in s['attempts'] for ef in at['effects']]
        e['effect_log_at_problem_end']=[dict(ef,timing='before commitment') for ef in effects if ef['log']==('classification' if run['mode']=='behaviour' else 'observation')]
        e['effects_reason']='L contains 1,2,3, all emitted at stage 1 before any commitment. One-stage any-one problems require one entry for x=2 or 3. Staged problems select none, so P11’s cannot-select rule makes a log with more than one entry extra. Loss of output 1 from a failed derivation’s printer does not erase it from L.'
    else:raise AssertionError(sub)
    if equiv is not None:e['residual_equivalence']={'equivalent':not equiv.startswith('Not equivalent'),'reason':equiv}
    elif e['representation'] in ['solved form','residual']:
        raise AssertionError(('missing equivalence',sub))
    e['observations']={
      'reasoning':' '.join(commentary),
      'reported_verbatim':[{**{qk:qv for qk,qv in q.items() if qk!='answers'},'answers':[{**{vk:vv for vk,vv in v.items() if vk!='verbatim'},'verbatim':ref_value(v['verbatim'],f'{ptr}/computations/{ci}/queries/{qi}/answers/{vi}/verbatim')} for vi,v in enumerate(q['answers'])]} for qi,q in enumerate(c['queries'])],
      'observe_verbatim':ref_value(raw,ptr+'/observe/raw'),
      'unknowns_representation':'uninstantiated identifiers or open list-tail variables; suspended equalities are printed beside aliases' if e['reached'] and raw else 'unavailable: no current-stage observe state',
      'alternatives':c['alternatives'], 'suspended':c['suspended'],
      'manual_actions':a['manual_actions'], 'posing':a['posed'],
      'error_verbatim':c['execution_state']['error_verbatim'],
      'safety_limit':a['safety_limit'],
      'harness_faults':rec.get('harness_faults',[]),
      'measurements':{'steps':c['steps'],'store':a['store'],'problem_operations':c['problem_operations'],'unavailable_policy':'null is unavailable; no missing figure is read as zero'},
    }
    if not e['reached']:
        e['observations']['alternatives']=None;e['observations']['suspended']=None
    return e

def entries(rec,path,final_only=False):
    es=[]
    readings=['finite','stream'] if rec['run']['subproblem']=='P09d' else [None]
    for s in rec['stages']:
        for a in s['attempts'][-1:] if final_only else s['attempts']:
            for c in a['computations']:
                for reading in readings:es.append(classify(rec,path,s,a,c,reading))
    return es

behaviours={}; compared=[]
for path in paths:
    if '.behaviour.' not in path.name:continue
    rec=read_record(path)
    es=entries(rec,path)
    result['outcomes']+=es
    assert key(rec) not in behaviours
    behaviours[key(rec)]=(path,[e for e in es if e['final_attempt']])
def classification(e):
    return {k:e[k] for k in ['reached','semantic','representation','simplification','identical_to_posed','residual_size','input_size','execution_state','residual_equivalence','harness_fault']}
for path in paths:
    if '.behaviour.' in path.name:continue
    rec=read_record(path);bp,bes=behaviours[key(rec)]
    mes=entries(rec,path,True)
    assert len(mes)==len(bes)
    differences=0
    for be,me in zip(bes,mes):
        assert (be['stage'],be['computation'],be['reading'])==(me['stage'],me['computation'],me['reading'])
        if classification(be)!=classification(me):
            differences+=1
            result['mode_differences'].append(dict(configuration=me['configuration'],instance=me['instance'],program=me['program'],mode=rec['run']['mode'],record=str(path.relative_to(ROOT)),stage=me['stage'],computation=me['computation'],reading=me['reading'],harness_fault=me['harness_fault'],behaviour=classification(be),this_mode=classification(me),note='Final stage classification differs; initial safety attempts remain documented separately.'))
    compared.append({'record':str(path.relative_to(ROOT)),'behaviour':str(bp.relative_to(ROOT)),'final_classification_entries_compared':len(mes),'differences':differences})

judgements={
 'P09a':('not expressible','Separate spawn computations cannot be transcribed: all assertions conjoin in one session. Named OR variants instead share an untagged disjunction report, which does not preserve the two computation queries; A even receives B’s solved branch. The reverse direction alone is transcribed (tokens 19–102), but the required independent computation interface is absent.'),
 'P09b':('not expressible','Separate failure-isolated computations are absent. The primary conjoins A and B, so A’s failure destroys B. The OR variant preserves B but gives the same y=3 branch to A’s query, changing the separate-computation meaning.'),
 'P09c':('expressible with reformulation','No primitive comparisons. Integer gt/le are replaced by existential positive/nonnegative differences (R 6–76,89–94,103–108). Induction on their least definitions proves equivalence on all integer constants, without a finite bound. Scheduling/nontermination does not change this denotation.'),
 'P09d1':('expressible','genu and sum3 are direct head/recursive/arithmetic transcriptions in order; the least finite-sequence relation is empty. No R tokens.'),
 'P09d2':('expressible','The same genu and sum3 equations directly transcribe the specified producer/consumer definitions, with no R tokens. In the stream reading the query is for total while production continues, so representing a completed infinite list is not required. Consumer starvation in this program is an execution result, not evidence that the definitions need reformulation.'),
 'P09e':('expressible','Native reversible arithmetic holds both integer equations; lack of duplicate elimination affects simplification, not expressibility.'),
 'P10a':('expressible with reformulation','Named replacement becomes a history of fresh versions (R append constructs); last arrived version gives the required current scalar on every integer input. Equations for the new values are P inside that encoding.'),
 'P10b':('expressible with reformulation','dbl maps the problem-specific standing multiplication across value histories (R 12–17,20–44,50–63 and version append constructs); key 18–19 is C. Induction over arrived cells maintains current d=dk*b for every replacement.'),
 'P10c':('expressible with reformulation','Fresh version histories implement replacement; the snapshot uses the then-current b version once, so later b versions leave d’s current value unchanged. R history constructs; P snapshot arithmetic.'),
 'P10d':('not expressible','The comparison itself has a meaning-preserving R definition, but withdrawal cannot revive discarded derivations. Stage 3 instead conjoins pick(x3) with the old state and changes the reported unknown. It cannot recover after all old alternatives are eliminated, e.g. threshold at least the largest pick fact. Thus it is not a generic implementation of retraction; the observed stage 3 is in any event never reached.'),
 'P11a':('not expressible','The supplied 1990-notation variant replaces x>=k by excluding one chosen value (R 9–11,38–44); that is not equivalent when the facts or threshold change. This notation has emit but no arithmetic to define a generic integer comparison. No generic transcribed or preserving reformulation is supplied.'),
 'P11b':('not expressible','As P11a: R 9–11,45–51 encode one excluded value rather than an integer threshold; emit is present but arithmetic comparisons cannot be defined in that notation. Effects are also extra on the recorded constants.'),
 'P11c':('not expressible','pick, emit and late inequality can be transcribed, but commitment to one current outcome cannot: the commit section is empty and every derivation stays live. P11 specifies how to judge this failure to select; that fallback does not supply a selection construct.'),
 'P11d':('not expressible','Commitment cannot be transcribed or implemented by this program. No v is selected and the later contradiction removes x=1 rather than contradicting an irrevocable selection. The stipulated no-selection fallback is used for outcome classification.'),
}
for cfg in CONFIGS:
    for sub,(judgement,reason) in judgements.items():
        result['expressibility'].append(dict(configuration=cfg,subproblem=sub,direction='forward reverse of known sequence' if sub=='P09a' else ('known starting integer to sequence and total' if sub in ['P09c','P09d1','P09d2'] else None),expressibility=judgement,reason=reason))
    for primary,others in manifest:
        name=primary.split('/',1)[1]
        result['s_mechanisms'].append(dict(configuration=cfg,program=name,mechanism='none',listed_at_phase_4=True,tokens=0,token_ranges=[],reason='Phase-4 list is empty. Native arithmetic, key, lambda, or, not and tout need no S; problem-specific history mapping and arithmetic definitions of comparisons are R, not a general interpreter/scheduler/store.'))

# Independently account for every job in the permitted logs, including names
# whose textual OR order differs from the instance spawn order.
logjobs=Counter()
for cfg in CONFIGS:
    for pr in ['P09','P10','P11']:
        f=ROOT/'results/absys/logs'/f'1C-{cfg}-{pr}.tsv'
        for line in f.read_text().splitlines():
            fields=line.split('\t')
            if len(fields)>=7 and fields[1]==cfg:
                logjobs[(cfg,fields[2],fields[3],fields[4])]+=1
recordjobs=Counter()
for path in paths:
    rec=read_record(path);rr=rec['run'];cfg=rr['configuration']
    recordjobs[(cfg,rr['instance'],rr['program']['path'].removeprefix('programs/absys/'+cfg+'/'),rr['mode'])]+=1
assert logjobs==recordjobs,(logjobs-recordjobs,recordjobs-logjobs)
for logname in ['batch-log.tsv','rerun-m2-log.tsv']:
    assert not any(re.search(r'\bP(?:09|10|11)[a-z]',line) for line in (ROOT/'results/absys'/logname).read_text().splitlines())
assert len(paths)==171 and len(behaviours)==57 and len(compared)==114
assert not any('/raw-rerun-m2/' in str(p) for p in paths)

finals=[e for e in result['outcomes'] if e['final_attempt']]
validation=dict(distinct_texts=len(manifest),shared_configuration_paths_verified=len(shared_checks),tokens=sum(token_totals.values()),token_totals={c:token_totals[c] for c in 'PCRSH'},per_text=per_text,behaviour_records=len(behaviours),all_raw_records=len(paths),logged_jobs=sum(logjobs.values()),behaviour_entries_including_initial_attempts=len(result['outcomes']),final_behaviour_entries=len(finals),final_semantics=dict(Counter(e['semantic'] or 'not reached' for e in finals)),final_representations=dict(Counter(e['representation'] or 'not applicable' for e in finals)),final_execution_states=dict(Counter(st for e in finals for st in e['execution_state'])),unreached_final_entries=sum(not e['reached'] for e in finals),harness_fault_behaviour_entries=sum(e['harness_fault'] for e in result['outcomes']),measurement_comparisons=compared,measurement_reruns=0,mode_differences=len(result['mode_differences']))
(OUT/'absys.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(OUT/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in validation.items() if k not in ['per_text','measurement_comparisons']},indent=2))
