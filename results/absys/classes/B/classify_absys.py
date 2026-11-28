#!/usr/bin/env python3
"""Independent classifier B. Reads frozen tokens and recorded data only.

No program, harness or system is imported or executed. Semantic decisions
are documented below and in absys.notes.md; assertions check the evidence.
"""
import collections
import csv
import hashlib
import json
import pathlib
import re

SOURCE = pathlib.Path('.')
DEST = pathlib.Path('results/absys/classes/B')
CONFIGS = ['absys', 'absys-depth-first', 'absys-wake-back']


def read_json(path):
    return json.loads(path.read_text())


def frozen(path):
    with path.open() as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    assert [int(r['index']) for r in rows] == list(range(len(rows)))
    return rows


def span(a, b, construct, rule='METRICS rules 1, 3 and 10: transcription of the problem'):
    return {'from': a, 'to': b, 'class': 'P', 'construct': construct, 'rule': rule}


def class_tokens():
    tokens = {}
    texts = list(csv.reader((SOURCE/'results/absys/tokens/TEXTS.tsv').open(), delimiter='\t'))[1:]
    for first, shared in texts:
        rows = frozen(SOURCE/f'results/absys/tokens/{first}.tokens.tsv')
        # Compare the supplied token streams, never tokenize source.
        for other in shared.split():
            other_rows = frozen(SOURCE/f'results/absys/tokens/{other}.tokens.tsv')
            assert rows == other_rows
        source = (SOURCE/f'programs/absys/{first}').read_text().splitlines()
        ss = []
        # Each constants-table entry is the program's stage information.
        in_constants = False
        constant_lines = []
        for n, line in enumerate(source, 1):
            if 'CONSTANTS BEGIN' in line:
                in_constants = True
            elif 'CONSTANTS END' in line:
                in_constants = False
            elif in_constants and line.strip() and not line.lstrip().startswith('%'):
                constant_lines.append(n)
        for n in constant_lines:
            rr = [r for r in rows if int(r['line']) == n]
            ss.append(span(int(rr[0]['index']), int(rr[-1]['index']),
                           'Stage constant table entry: '+source[n-1].split('%')[0].strip(),
                           'METRICS class P and rule 1; Absys harness 3.9 and 3.12: constants are problem information, not H'))
        words = [r['token'] for r in rows]
        if "conc'" in words:
            k = words.index("conc'")
            parts = [(0,7,'conc lambda definition and three formal places'),
                     (8,9,'conc definition case grouping: begin {'),
                     (10,13,'conc case 1: first sequence is empty'),
                     (14,16,'conc case 1: second and third sequences are equal'),
                     (17,17,'conc definition: disjunction of its two cases'),
                     (18,24,'conc case 2 head: decompose the first sequence'),
                     (25,31,'conc case 2 head: construct the third sequence'),
                     (32,39,'conc case 2 body: recursive conc(k,q,m)'),
                     (40,41,'conc definition case grouping: } end')]
            for a,b,label in parts:
                ss.append(span(k+a,k+b,label,'METRICS rules 1, 2, 3 and 10: original cases, head equations and recursion, in presentation order'))
        if "rev'" in words:
            k = words.index("rev'")
            parts = [(0,5,'rev lambda definition and two formal places'),
                     (6,7,'rev definition case grouping: begin {'),
                     (8,11,'rev case 1: first sequence is empty'),
                     (12,15,'rev case 1: reversed sequence is empty'),
                     (16,16,'rev definition: disjunction of its two cases'),
                     (17,23,'rev case 2 head: decompose first sequence'),
                     (24,29,'rev case 2 first conjunct: rev(k,n)'),
                     (30,39,'rev case 2 second conjunct: conc(n,[h],r)'),
                     (40,41,'rev definition case grouping: } end')]
            for a,b,label in parts:
                ss.append(span(k+a,k+b,label,'METRICS rules 1, 2, 3 and 10: original rev cases and conjunct order; fresh local n is the problem\'s q, not an extra argument'))
        covered = {i for s in ss for i in range(s['from'],s['to']+1)}
        # Stage goals occupy a line each; P02c has one grouped conjunction.
        unclassified = [i for i in range(len(rows)) if i not in covered]
        by_line = collections.defaultdict(list)
        for i in unclassified:
            by_line[int(rows[i]['line'])].append(i)
        for line, indices in by_line.items():
            a,b = min(indices),max(indices)
            if words[a] == 'begin':
                assert words[b] == 'end' and b-a == 16
                ss.append(span(a,a,'P02c single conjunction: begin', 'METRICS class P: conjunction; rule 10'))
                for j, name in enumerate(['R1: u+v=16','R2: w*u=v','R3: u+10=12']):
                    ss.append(span(a+1+j*5,a+5+j*5,name,'METRICS class P and rule 8: primitive arithmetic relation, with no imposed evaluation direction'))
                ss.append(span(b,b,'P02c single conjunction: end', 'METRICS class P: conjunction; rule 10'))
            else:
                ss.append(span(a,b,'Stage information/query: '+source[line-1].strip(),
                               'METRICS class P and rules 1, 3, 8, 10: the stated equality, arithmetic relation or query'))
        ss.sort(key=lambda s:s['from'])
        assert [i for s in ss for i in range(s['from'],s['to']+1)] == list(range(len(rows))), first
        tokens[first] = ss
    return tokens, texts


def data_inventory():
    records = {}
    structure=read_json(SOURCE/'harnesses/stages.json')
    expected_stages={}
    for problem in structure['problems']:
        if problem['problem'] not in ['P01','P02','P03']:
            continue
        for sub in problem['subproblems']:
            for instance in sub['instances']:
                expected_stages[instance['id']]=[stage['stage'] for stage in sub['stages']]
    for cfg in CONFIGS:
        for path in sorted((SOURCE/f'results/absys/{cfg}').glob('P0?/raw/*.json')):
            d = read_json(path)
            r = d['run']
            key = cfg, r['instance'], r['mode']
            assert key not in records, key
            assert r['configuration'] == cfg and r['purpose'] == 'primary'
            assert [s['stage'] for s in d['stages']]==expected_stages[r['instance']]
            program=pathlib.PurePosixPath(r['program']['path'])
            assert program.parts[:2]==('programs','absys') and program.suffix=='.ab1'
            assert hashlib.sha256((SOURCE/program).read_bytes()).hexdigest()==r['program']['sha256']
            records[key] = (str(path.relative_to(SOURCE)), d)
    log = list(csv.reader((SOURCE/'results/absys/batch-log.tsv').open(), delimiter='\t'))
    expected = [(r[1],r[2],r[4]) for r in log]
    assert len(expected) == len(set(expected)) == len(records) == 153
    assert set(expected) == set(records)
    for row in log:
        r = records[row[1],row[2],row[4]][1]['run']
        assert pathlib.Path(r['program']['path']).name == row[3]
    return records


def blocks(raw):
    """Read only the system's printed derivation blocks, excluding ? NAME repeats."""
    return [(m.group(1),m.group(2),m.group(3)) for m in re.finditer(
        r'^  derivation #(\d+) \(([^\n]+)\)\n(.*?)(?=^  derivation #|^#\d+:|\Z)',raw,re.M|re.S)]


def bound_in(block):
    return dict(re.findall(r'^    ([a-z]+) = (.+)$',block,re.M))


def scalar_report_check(sub, stage, raw, cfg):
    bb = blocks(raw)
    if sub == 'P01a':
        assert len(bb)==1
        if stage == 1:
            assert 'suspended   x = y' in raw and not re.search(r'^    z =',raw,re.M)
        elif stage == 2:
            assert 'suspended   x = y;  y = z' in raw
        else:
            assert bound_in(bb[0][2]) == {'x':'2','y':'2','z':'2'}
    if sub == 'P01b':
        assert len(bb)==1
        if stage == 1:
            assert 's = m₂' in raw and 't = [1;2&m₂]' in raw and 'suspended   s = m₂' in raw
        else:
            assert bound_in(bb[0][2]) == {'s':'[3]','t':'[1;2;3]'}
    if sub == 'P01c':
        assert len(bb)==1 and bound_in(bb[0][2]) == {'x':'[1&↻]'}
    expected = {
        'P03a':[{'c':'[1;2;3]'}],
        'P03b':[{'a':'[]','b':'[1;2]'},{'a':'[1]','b':'[2]'},{'a':'[1;2]','b':'[]'}],
        'P03c':[{'b':'[2;3]'}], 'P03d':[{'a':'[1;2]'}],
        'P03e':[{'b':'[3;2;1]'}], 'P03f':[{'a':'[3;2;1]'}]}
    if sub in expected:
        done = [bound_in(b) for _,status,b in bb if status=='hibernating']
        assert done == expected[sub], (cfg,sub,done)
        if sub != 'P03f':
            assert len(bb)==len(done)
        else:
            assert len(bb)==(19 if cfg=='absys-depth-first' else 900)
    return bb


def p02_prefix(d,k):
    r=d['run']
    if r['subproblem']=='P02c':return ['R1','R2','R3']
    return r['parameters'].get('order',['R1','R2','R3'])[:k]


def equivalence(reason):
    return {'equivalent':True,'method':'by hand, with record assertions in classify_absys.py','reason':reason}


def measure_observation(records,cfg,instance,k):
    found={}
    for mode in ['cost','storage']:
        path,d=records[cfg,instance,mode]
        s=next(s for s in d['stages'] if s['stage']==k)
        a=s['attempts'][-1];c=a['computations'][0]
        found[mode]={'record':path,'attempt':a['attempt'],'execution_state':c['execution_state']['states']}
        if mode=='cost':
            found[mode]['steps']=c['steps']
            # Trace is evidence, not an additional execution or a reinterpreted counter.
            lines=a['stdout'].splitlines()
            last_assertion=max((i for i,l in enumerate(lines) if l.startswith('» ')),default=-1)
            trace=lines[last_assertion+1:] if last_assertion>=0 else []
            if instance.startswith('P02'):
                found[mode]['last_assertion_equation_events']=[l for l in trace if re.search(r'#\d+\s+equation\s',l)]
                found[mode]['last_assertion_reactivation_events']=[l for l in trace if 'reactivated' in l]
                order=[]
                for line in trace:
                    match=re.search(r'#\d+\s+(?:equation|suspend)\s+(.+?):',line)
                    if not match:
                        continue
                    relation=match.group(1)
                    if ' * ' in relation:
                        order.append('R2')
                    elif ' + 10 = 12' in relation:
                        order.append('R3')
                    elif ' + ' in relation and ' = 16' in relation:
                        order.append('R1')
                found[mode]['last_assertion_arithmetic_examination_order']=order
                found[mode]['last_assertion_arithmetic_examination_counts']=dict(collections.Counter(order))
                found[mode]['trace_count_convention']='One printed arithmetic equation/suspend event is one examination; binding equations, reactivated-list mentions and hibernations are not added. These event counts are not machine step counts.'
        else:
            found[mode]['store']=a['store']
            found[mode]['alternatives']=c['alternatives']
            found[mode]['suspended']=c['suspended']
        found[mode]['availability']='unavailable after final timeout' if 'timeout' in c['execution_state']['states'] else 'as recorded; null means unavailable'
    return found


def stage_class(path,d,s,reading=None):
    r=d['run'];cfg=r['configuration'];sub=r['subproblem'];k=s['stage']
    a=s['attempts'][-1];c=a['computations'][0];raw=a['observe']['raw']
    o={'configuration':cfg,'instance':r['instance'],'program':pathlib.Path(r['program']['path']).name,
       'record':path,'stage':k,'reading':reading,'reached':True,'semantic':'complete',
       'representation':'explicit','simplification':None,'identical_to_posed':None,
       'residual_size':None,'execution_state':c['execution_state']['states'],
       'residual_equivalence':None,'observations':{},'rule':'SPECIFICATION Outcomes 1–3; problem valid outcomes; AMENDMENTS 3'}
    obs=o['observations']
    obs.update({'record_attempt':a['attempt'], 'posing':a['posed'],
                'unknowns':a['observe']['bindings'],
                'alternatives':c['alternatives'],'suspended':c['suspended'],
                'conclusions_withdrawn':[],
                'manual_actions':a['manual_actions']+d['manual_actions'],
                'harness_faults':d['harness_faults'],
                'unavailable_measurements':'null is unavailable, never zero; behaviour has no step counts or store vector',
                'attempt_history':[{'attempt':aa['attempt'],'limit_s':aa['limit_s'],
                    'reached':True,'semantic':('none reported' if not aa['observe']['raw'] else 'see final stage classification'),
                    'execution_state':aa['computations'][0]['execution_state']['states'],
                    'safety_limit':aa['safety_limit'],'posing':aa['posed']}
                    for aa in s['attempts']]})
    if not raw:
        assert c['execution_state']['states']==['timeout']
        o.update(semantic='none reported',representation=None)
        obs['verbatim']=''
        obs['unknowns_representation']='unavailable: no state was read before either timeout'
        obs['answer_completeness']={'valid_observed':0,'expected':1,'invalid_observed':0,'note':'0 observed answers; unknown retained/suspended counts remain null'}
        return o
    bb=scalar_report_check(sub,k,raw,cfg)
    if sub=='P03f':
        obs['verbatim_completed_derivations']=['  derivation #'+i+' ('+status+')\n'+b for i,status,b in bb if status=='hibernating']
        obs['all_verbatim_state']={'record':path,'json_pointer':f'/stages/{k-1}/attempts/{len(s["attempts"])-1}/observe/raw',
                                   'characters':len(raw),'sha256_utf8':hashlib.sha256(raw.encode()).hexdigest()}
        # Avoid copying megabytes of unfinished bindings into the classification.
        obs['unknowns']={'a':'[3;2;1] in the sole completed derivation; unfinished branch bindings are verbatim at all_verbatim_state'}
        obs['unknowns_representation']='fresh h/k/n unknowns in unfinished branches, with suspended equality processes and queued rev/conc applications'
        obs['unfinished_derivations']=len(bb)-1
        obs['unfinished_work_is_not_an_answer']='The still-elaborating blocks are conditional search state, not extra completed solutions. P03 explicitly makes the sole valid answer plus budget complete. The explicit valid form is the selected representation (SPECIFICATION Outcomes 2).'
        obs['answer_completeness']={'valid_observed':1,'expected':1,'invalid_observed':0}
        obs['equivalence_check']='The only hibernating branch binds a=[3;2;1]. By induction on finite sequences, rev relates exactly a sequence and its reversal, so this is the unique solution. Other branches have undecided goals; their displayed prefixes are not unconditional answers.'
    else:
        obs['verbatim']=raw
        obs['unknowns_representation']='uninstantiated names, suspended equality links, or open list tails as printed; a name that does not occur is free, not an error'
    if sub=='P01a' and k<3:
        o['representation']='solved form'
        o['residual_equivalence']=equivalence(
            'The displayed equality identification is x=y with z free.' if k==1 else
            'The displayed equality chain identifies x=y=z; existential choice of their common value gives exactly all assignments admitted at stage 2.')
        obs['representation_decision']='Equality identification is expressly a solved form in Outcomes 2. Operationally these are recorded equations, not one shared machine variable: the system keeps '+str(k)+' suspended equality process(es). Representation and execution state are separate axes.'
        obs['held_equation_size']={'relations':k,'unknown_occurrences':2*k,'posed_relations':k,'posed_unknown_occurrences':2*k}
        obs['answer_completeness']={'infinite':True,'equivalent_finite_representation':True}
    elif sub=='P01b' and k==1:
        o['representation']='solved form'
        o['residual_equivalence']=equivalence('The report has s=m₂ and t=[1;2&m₂]. Eliminating the fresh local m₂ gives t=⟨1,2⟩++s, with s any finite sequence, exactly P01b stage 1. This is an open sequence construction, not an outstanding conc application.')
        obs['representation_decision']='A term made from values and an unknown tail, together with an identification of unknowns, is a solved form under Outcomes 2. The one suspended s=m₂ equation remains operational work, recorded separately.'
        obs['sequence_domain_reading']='The list-tail notation is read as the problem\'s sequence concatenation (defined on sequences only); the symbolic tail denotes a sequence. No finite numeric or length bound is imposed. The permitted records do not test binding the tail to a nonsequence; no claim about that unrun operational case is inferred.'
        obs['answer_completeness']={'infinite':True,'equivalent_finite_representation':True}
    elif sub=='P01c':
        o['representation']='cyclic'
        o['semantic']='complete' if reading=='rational' else 'unsound'
        obs['occurs_check']='off in all three configurations (systems file and program comment); ↻ is an explicitly printed tail cycle'
        obs['equivalence_check']='[1&↻] is the infinite all-1 sequence. It is the unique rational solution; it is not a finite sequence, whereas the finite reading admits no solution.'
        obs['answer_completeness']=({'valid_observed':1,'expected':1,'invalid_observed':0} if reading=='rational' else {'valid_observed':0,'expected':0,'invalid_observed':1,'reported_no_solutions':False})
    elif sub.startswith('P02'):
        prefix=p02_prefix(d,k);have=frozenset(prefix)
        obs['relations_arrived']=prefix
        relation_numbers={'R1':(1,2),'R2':(1,3),'R3':(1,1)}
        nr=sum(relation_numbers[x][0] for x in prefix);nu=sum(relation_numbers[x][1] for x in prefix)
        if have=={'R1'} or have=={'R2'} or have=={'R1','R2'} or have=={'R2','R3'}:
            o['representation']='residual'
            o['simplification']='reducible' if have=={'R1','R2'} else 'reduced'
            o['identical_to_posed']=have!={'R2','R3'}
            rr,ru=(1,2) if have=={'R2','R3'} else (nr,nu)
            o['residual_size']={'unit':'primitive relations left to decide and occurrences of unknowns in those relations',
                                'input':{'relations':nr,'unknown_occurrences':nu},
                                'residual':{'relations':rr,'unknown_occurrences':ru},
                                'note':'Input is cumulative stage information before solving; solved bindings and free unknowns are listed separately, not counted as undecided relations.'}
            reasons={frozenset({'R1'}):'The stored u+v=16 is exactly R1, over integers; w is free. No arithmetic expression is an allowed solved-form term, so this one relation cannot be eliminated without an infinite enumeration.',
                     frozenset({'R2'}):'The stored w*u=v is exactly R2 over integers. It has infinitely many solutions and cannot be replaced by an allowed non-arithmetic solved-form term.',
                     frozenset({'R1','R2'}):'Both posed relations are held unchanged. Eliminating v gives u*(w+1)=16; hence u is one of ±1, ±2, ±4, ±8, ±16, v=16-u and w=16/u-1. These are exactly the ten triples in P02. It is complete but reducible: explicitly enumerating those ten triples leaves zero relations to decide.',
                     frozenset({'R2','R3'}):'R3 fixes u=12-10=2, and the held relation is w*2=v. Conversely every integer w, with u=2 and v=2*w, satisfies R2 and R3. This is smaller than the posed conjunction and reduced in the permitted representation language.'}
            o['residual_equivalence']=equivalence(reasons[have])
            wanted_susp=2 if have=={'R1','R2'} else 1
            assert c['suspended']['at_boundary']==wanted_susp
            assert ('u + v = 16' in raw)==('R1' in have)
            if have=={'R2','R3'}:assert 'u = 2' in raw and 'w * 2 = v' in raw
            elif 'R2' in have:assert 'w * u = v' in raw
            obs['answer_completeness']=({'valid_explicit_observed':0,'expected_finite':10,'equivalent_finite_representation':True} if have=={'R1','R2'} else {'infinite':True,'equivalent_finite_representation':True})
            obs['waiting_for']='R1 waits for another known number among u,v; R2 waits until two of w,u,v are known. At u=2 it waits for w or v. The held constraints are read state, not an echo: subsequent stages resume them.'
        elif have=={'R3'} or have=={'R1','R3'}:
            o['representation']='solved form'
            want={'u':'2'} if have=={'R3'} else {'u':'2','v':'14'}
            assert bound_in(bb[0][2])==want
            o['residual_equivalence']=equivalence('R3 gives u=2; '+('v and w remain free integers.' if have=={'R3'} else 'R1 then gives v=14 and w remains a free integer. The printed solved form is exactly this infinite set.'))
            obs['answer_completeness']={'infinite':True,'equivalent_finite_representation':True}
        else:
            assert have=={'R1','R2','R3'}
            assert bound_in(bb[0][2])=={'u':'2','v':'14','w':'7'}
            obs['equivalence_check']='R3 fixes u=2, R1 fixes v=14, and R2 fixes w=7; the printed binding is the unique integer solution.'
            obs['answer_completeness']={'valid_observed':1,'expected':1,'invalid_observed':0}
        obs['domain']='All integers, as P02 specifies; no imposed finite domain or finite search bound.'
    elif sub!='P03f':
        obs['answer_completeness']={'valid_observed':len(bb),'expected':3 if sub=='P03b' else 1,'invalid_observed':0}
        obs['equivalence_check']='Bindings asserted against the problem\'s exact stated finite outcome(s) by classify_absys.py.'
    return o


def main():
    tokens,texts=class_tokens()
    records=data_inventory()
    outcomes=[];differences=[];by_key={}
    for (cfg,instance,mode),(path,d) in sorted(records.items()):
        if mode!='behaviour':continue
        for s in d['stages']:
            readings=['finite','rational'] if d['run']['subproblem']=='P01c' else [None]
            for reading in readings:
                o=stage_class(path,d,s,reading)
                o['observations']['measurements']=measure_observation(records,cfg,instance,s['stage'])
                outcomes.append(o)
                by_key[cfg,instance,s['stage'],reading]=o
    # Independently examine every cost/storage stage; only differing classes are output.
    axes=['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence']
    compared=0
    for (cfg,instance,mode),(path,d) in sorted(records.items()):
        if mode=='behaviour':continue
        bp,bd=records[cfg,instance,'behaviour']
        assert [s['stage'] for s in d['stages']]==[s['stage'] for s in bd['stages']]
        for s,bs in zip(d['stages'],bd['stages']):
            readings=['finite','rational'] if d['run']['subproblem']=='P01c' else [None]
            for reading in readings:
                compared+=1
                o=stage_class(path,d,s,reading);b=by_key[cfg,instance,s['stage'],reading]
                if any(o[x]!=b[x] for x in axes):
                    differences.append({'configuration':cfg,'instance':instance,'program':o['program'],'mode':mode,
                        'record':path,'stage':s['stage'],'reading':reading,
                        'behaviour':{**{x:b[x] for x in axes},'record':bp,
                                     'valid_answers_observed':1,'retained_derivations':b['observations']['alternatives']['at_boundary'],
                                     'suspended_count':b['observations']['suspended']['at_boundary']},
                        'this_mode':{**{x:o[x] for x in axes},'attempts':o['observations']['attempt_history'],
                                     'valid_answers_observed':0,'retained_derivations':None,'suspended_count':None,
                                     'steps':None,'store':None},
                        'note':'Both measured attempts (60 s and 600 s) time out with no observable state. Behaviour reports the unique valid answer and reaches budget. This is a measurement/instrumentation limit, not a model-level inability or evidence of a different answer. Missing measurements and counts are unavailable, not zero (AMENDMENTS 3.1). No later stage exists here.'})
                else:
                    # Check that absence of a classification difference is not hiding
                    # a changed observed answer, suspended count, or retained count.
                    a=s['attempts'][-1];ba=bs['attempts'][-1]
                    assert a['print']==ba['print'],(path,s['stage'])
                    for key in ['suspended','alternatives']:
                        assert a['computations'][0][key]['at_boundary']==ba['computations'][0][key]['at_boundary']
    exp=[]
    directions={'P01b':'conc(+,-,-), with the second argument supplied at stage 2',
                'P03a':'conc(+,+,-)','P03b':'conc(-,-,+)','P03c':'conc(+,-,+)',
                'P03d':'conc(-,+,+)','P03e':'rev(+,-)','P03f':'rev(-,+)'}
    for cfg in CONFIGS:
        for first,_ in texts:
            sub=pathlib.Path(first).stem
            reason='The staged equations transcribe the stated information directly using native equality, with no R or S constructs.'
            if sub=='P01b':reason='The two conc cases retain the problem\'s order; the stage uses the same native relational procedure and an open sequence tail. No separate direction algorithm, finite domain or S mechanism is supplied. Sequence-domain interpretation is documented in the outcome and notes.'
            if sub=='P01c':reason='The self-referential equation is directly transcribed. Native equality has no occurs check: operationally the rational result is complete and the finite result unsound. This runtime distinction does not prevent transcribing the stated equation; no reformulation is used.'
            if sub.startswith('P02'):reason='Native integer arithmetic is relational in every place and can hold undecided relations incrementally. The program transcribes all three relations with no R tokens; P02b PART delivery is the fixed harness contract for all six orders.'
            if sub.startswith('P03'):reason='The original conc/rev cases and conjunct order are transcribed once, using native relational lambdas in this direction. No added argument, changed algorithm, reordering or separately written direction function appears. '+('Finding the unique answer and then reaching budget is an execution result, not failure of expressibility.' if sub=='P03f' else 'The behaviour run produces every expected answer.')
            exp.append({'configuration':cfg,'subproblem':sub,'direction':directions.get(sub),'expressibility':'expressible','reason':reason})
    # Integer equivalence proof for the ten finite P02 solutions: derive divisors,
    # rather than enumerating an arbitrary finite domain.
    triples=sorted((u,16-u,16//u-1) for u in [1,2,4,8,16,-1,-2,-4,-8,-16])
    assert len(triples)==10 and all(u+v==16 and w*u==v for u,v,w in triples)
    assert [t for t in triples if t[0]+10==12]==[(2,14,7)]
    result={'tokens':tokens,'outcomes':outcomes,'mode_differences':differences,'expressibility':exp}
    assert len(tokens)==12 and len(outcomes)==105 and len(differences)==6 and len(exp)==36
    (DEST/'absys.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    totals=collections.Counter()
    per_text={}
    for key,spans in tokens.items():
        t=collections.Counter()
        for ss in spans:t[ss['class']]+=ss['to']-ss['from']+1
        totals.update(t);per_text[key]=dict(t)
    summary={'records_checked':len(records),'behaviour_records':51,'behaviour_stages':102,
             'outcome_rows_including_two_P01c_readings':len(outcomes),'mode_stage_reading_comparisons':compared,
             'unique_texts':12,'token_totals':{x:totals[x] for x in 'PCRSH'},'per_text':per_text,
             'semantic':dict(collections.Counter(o['semantic'] for o in outcomes)),
             'representation':dict(collections.Counter(o['representation'] for o in outcomes)),
             'execution_state_combinations':dict(collections.Counter(', '.join(o['execution_state']) for o in outcomes)),
             'residual_simplification':dict(collections.Counter(o['simplification'] for o in outcomes if o['representation']=='residual')),
             'mode_differences':len(differences),'expressibility_rows':len(exp),
             'P02_R1_R2_ten_triples':triples}
    (DEST/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
