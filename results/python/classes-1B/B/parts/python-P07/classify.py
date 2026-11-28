"""Independent P07 classification. Reads only brief-authorized study files.
Uses the frozen TSV token indices; does not tokenize or execute study code.
"""
from pathlib import Path
import collections
import csv
import json

SRC = Path('.')
OUT = Path('results/python/classes-1B/B/parts/python-P07')
CONFIGS = ('core', 'extended', 'stdlib-concurrency')

def meta(cls, construct, rule):
    return (cls, construct, rule)

P_REL = 'METRICS rules 1, 19 (relation evaluator), 10'
R_HOLD = 'METRICS rule 19 (known-place tests and problem-specific holding), 10'
C_ORDER = 'METRICS rules 1, 2, 10 (explicit scheduling/synchronisation)'
H_RULE = 'METRICS rules 10, 13; harnesses/python/README.md section 7'
S_RULE = 'METRICS rules 12, 19 (generic reusable relation adapter), 10'


def classify_text(key):
    conf, filename = key.split('/')
    lines = (SRC / 'programs/python' / key).read_text().splitlines()
    with (SRC/'results/python/tokens'/f'{key}.tokens.tsv').open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    for i, row in enumerate(rows):
        assert int(row['index']) == i
    # The evaluator's mathematical signature is P. Dispatch on which of
    # its places are known, and return-None wait verdicts, are R (rule 19).
    function = None
    in_relation = False
    in_report = False
    stage = False
    line_meta = {}
    for n, line in enumerate(lines, 1):
        t = line.strip()
        if not t or t.startswith('#'):
            continue
        if t.startswith('def '):
            function = t[4:t.index('(')]
            if function == 'report': in_report = True
        if t == 'class Relation:':
            in_relation = True
        if t.startswith('while (s := cp.stage()):') or t.startswith('while (s := cp.stage()) is not None:'):
            function = None
            in_relation = False
            in_report = False
            stage = True
        # Defaults below are overridden construct by construct.
        m = None
        if function in ('equal','plus','minus','times') and not stage:
            if t.startswith('cp.relations(') or t.startswith('EVALUATOR ='):
                function = None
            elif t.startswith('def '):
                m = meta('P', f'{function}: arithmetic relation signature', P_REL)
            elif t.startswith('if ') and 'None' in t:
                m = meta('R', f'{function}: dispatch on known places: {t}', R_HOLD)
            elif t == 'return None':
                m = meta('R', f'{function}: relation must wait', R_HOLD)
            elif t.startswith('if ') or t.startswith('return '):
                m = meta('P', f'{function}: integer relation case: {t}', P_REL)
        if m is None:
            if t.startswith('cp.'):
                m = meta('H', f'harness call: {t}', H_RULE)
            elif t.startswith('while (s := cp.stage())') or t.startswith('if s.k ==') or t == 'if not s.replay:':
                m = meta('H', f'stage/replay dispatch: {t}', H_RULE)
            elif in_report or (stage and (t.startswith('if failed:') or t.startswith('print(') or t == 'else:' or t.startswith('told =') or t == 'if told:' or t == 'report()')):
                m = meta('H', f'output adapter for computed bindings/failure: {t}', H_RULE)
            elif in_relation:
                if function == '__repr__':
                    m = meta('H', f'residual output adapter: {t}', H_RULE)
                else:
                    m = meta('S', f'generic Relation adapter: {t}', S_RULE)
            elif t.startswith('import threading'):
                m = meta('C', 'enable external threading mechanism', C_ORDER)
            elif t.startswith('from S.suspend import'):
                m = meta('C', 'enable suspension-queue mechanism and its variables', 'METRICS rules 10, 12; S-mechanisms.md (call sites counted separately)')
            elif t.startswith(('SUM','Z_VALUE','DIFFERENCE','U_VALUE','V_VALUE','FIRST_SUM','SECOND_SUM','SQUARE')) and '=' in t:
                m = meta('P', f'stage constant: {t}', 'METRICS class P: stage information; rule 1')
            elif t.startswith('UNKNOWNS =') or t.startswith('unknowns ='):
                m = meta('H', f'output unknown-name view: {t}', H_RULE)
            elif conf == 'extended' and '= Var(' in t:
                m = meta('P', f'unknown declaration: {t}', 'METRICS class P: problem vocabulary; rule 12 (mechanism call, implementation counted separately)')
            elif t == 'q = Queue()' or t == 'q.run()':
                m = meta('C', f'queue scheduling: {t}', C_ORDER)
            elif conf == 'extended' and t.startswith('failed = []'):
                m = meta('S', 'generic Relation adapter failure store', S_RULE)
            elif t.startswith(('known =','held =','waiting =','failed =','EVALUATOR =')):
                m = meta('R', f'fixed arithmetic holding store: {t}', R_HOLD)
            elif t.startswith('changed =') or t.startswith('count ='):
                m = meta('C', f'thread synchronisation state: {t}', C_ORDER)
            elif function == 'place':
                m = meta('R', f'fixed arithmetic name/value lookup: {t}', R_HOLD)
            elif function == 'decide':
                if t.startswith(('while ','for rel ')) or t.startswith('again =') or t == 'continue':
                    m = meta('C', f'rescan scheduling: {t}', C_ORDER)
                else:
                    m = meta('R', f'fixed arithmetic relation holding/decision: {t}', R_HOLD)
            elif function in ('told','pose','settle'):
                m = meta('C', f'thread scheduling {function}: {t}', C_ORDER)
            elif function == 'hold':
                if t.startswith(('def ','with ','while ','count[','changed.','seen =','new =','if new:')) or t == 'told()':
                    m = meta('C', f'relation thread scheduling: {t}', C_ORDER)
                else:
                    m = meta('R', f'fixed arithmetic thread-held relation: {t}', R_HOLD)
            elif stage:
                if t.startswith(('relations =','"1":','"2":','"3":')) or t == '}':
                    m = meta('P', f'stage conjunction declaration: {t}', 'METRICS class P: posed primitive relations; rule 10; SPECIFICATION arithmetic decomposition')
                elif t.startswith('for position') or t.startswith('for goal') or t.startswith('for rel'):
                    m = meta('P', f'traverse problem-specified relation order: {t}', 'METRICS rules 1, 10; P07 presentation order')
                elif t.startswith('held.'):
                    m = meta('R', f'hold posed arithmetic relation: {t}', R_HOLD)
                elif t.startswith('q.wait') or t.startswith('pose(') or t == 'settle()':
                    m = meta('C', f'schedule posed relation: {t}', C_ORDER)
                elif t == 'decide()':
                    m = meta('R', 'decide held arithmetic relations', R_HOLD)
        if m is None:
            # Docstring lines have no tokens and are intentionally ignored.
            continue
        line_meta[n] = m

    annotations = [None] * len(rows)
    # Assign a distinct construct identity per statement/header; the same
    # identity is used again for that header's INDENT and closing DEDENT.
    line_ids = {n: (n,) + m for n,m in line_meta.items()}
    stack = []
    last_header = None
    for i,row in enumerate(rows):
        tok = row['token']; n = int(row['line'])
        if tok == '<INDENT>':
            assert last_header is not None, (key, i)
            annotations[i] = last_header
            stack.append(last_header)
        elif tok == '<DEDENT>':
            assert stack, (key,i)
            annotations[i] = stack.pop()
        else:
            assert n in line_ids, (key,i,n,lines[n-1])
            annotations[i] = line_ids[n]
            if tok == ':' and lines[n-1].rstrip().endswith(':'):
                last_header = line_ids[n]
    assert not stack

    def override(start, end, m, identity):
        for i in range(start,end+1): annotations[i] = (identity,)+m

    # Required fixed harness reads are H even when embedded in a P/R/C
    # construct (the frozen harness contract section 7.3; rule 10).
    for i in range(len(rows)-3):
        ts = [r['token'] for r in rows[i:i+4]]
        if ts[:3] == ['s','.','constants'] or ts[:3] == ['s','.','params']:
            assert ts[3] == '['
            j = i+4
            while rows[j]['token'] != ']': j += 1
            override(i,j,meta('H',f'fixed harness read: s.{ts[2]}[...]',H_RULE),f'read-{i}')

    # Nested primitive relation declarations: the tuple/Relation itself is
    # P, while append, queue wait or thread creation retains its outer class.
    for i in range(len(rows)-3):
        ts=[r['token'] for r in rows[i:i+4]]
        if (ts[0]=='(' and ts[1] in ('+','-','*','=') and ts[2:]==[',','(']) or ts[:2]==['Relation','(']:
            # Exclude the class declaration (whose '(' does not exist).
            start=i; op=i if ts[0]=='(' else i+1
            depth=0; end=None
            for j in range(op,len(rows)):
                t=rows[j]['token']
                if t=='(': depth+=1
                elif t==')':
                    depth-=1
                    if depth==0: end=j;break
            assert end is not None
            m=meta('P','posed primitive arithmetic relation','METRICS class P; rules 1, 10; SPECIFICATION arithmetic decomposition')
            for j in range(start,end+1):
                if annotations[j][1]!='H': annotations[j]=(f'posed-{i}',)+m

    # The threaded loop embeds an evaluator invocation in its scheduling
    # condition. The known-place evaluation is holding code, not the wait.
    if conf == 'stdlib-concurrency':
        for i,row in enumerate(rows):
            if row['token']=='EVALUATOR' and i and rows[i-1]['token']==':=':
                j=i
                while rows[j]['token']!='<NEWLINE>': j+=1
                # Final tokens are ') is None : NEWLINE'; close the call
                # before the assignment expression's outer ')'.
                end=j-5
                override(i,end,meta('R','evaluate the thread-held arithmetic relation',R_HOLD),f'eval-{i}')

    # Commas separating different constructs belong to the following one.
    for i,row in enumerate(rows[:-1]):
        if row['token']==',' and annotations[i] != annotations[i+1]:
            annotations[i]=annotations[i+1]

    spans=[]
    for i,a in enumerate(annotations):
        assert a is not None
        if i==0 or a!=annotations[i-1]:
            spans.append({'from':i,'to':i,'class':a[1],'construct':a[2],'rule':a[3]})
        else: spans[-1]['to']=i
    return spans, rows


def classify_record(path):
    d=json.loads(path.read_text()); run=d['run']; sub=run['subproblem']; letter=sub[-1]
    assert len(d['stages'])==1 and len(d['stages'][0]['attempts'])==1
    stage=d['stages'][0]; a=stage['attempts'][0]; c=a['computations'][0]
    assert a['posed']['how']=='fresh'
    assert run['complete'] and not a['safety_limit']['hit']
    residual = letter in 'bcfg'
    simpl = {'b':'reducible','c':'reduced','f':'inconsistency undetected','g':'reducible'}.get(letter)
    proofs={
        'a':'With t=x+y, z=3 gives y=7-3=4, t=12-3=9, and x=9-4=5. Conversely these values satisfy all four primitive relations. Relation order does not change this equivalence.',
        'b':'The held relations are precisely x+y=10 and x-y=4 over integers. Adding gives 2*x=14, hence x=7 and y=3; conversely (7,3) satisfies both. No elimination was performed, so the equivalent residual is reducible.',
        'c':'The held relation is exactly x+y=10 with x,y ranging over all integers. It denotes {(n,10-n): n in Z}. It has one relation and two unknown occurrences; the specification explicitly identifies this residual as reduced.',
        'd':'The report w=7,u=2,v=14 is exactly equivalent to w*u=v,u=2,v=14: integer cancellation gives w=14/2=7. The stored failure and waiting structures are empty.',
        'e':'The failure report denotes the empty set. Substituting u=2,v=15 requires 2*w=15, impossible for integer w since 15%2=1. The times evaluator checks divisibility and does not report a rational or truncated solution.',
        'f':'The held conjunction x+y=10 and x+y=11 is identical to the posed information. Subtracting its equations gives 0=1, so its denotation is the valid empty set. The inconsistency is not detected.',
        'g':'The held relation is x*x=9 with the same x in both factor places, not independent factors. Over integers (x-3)*(x+3)=0 iff x=3 or x=-3. It therefore denotes exactly both valid solutions, but has not been reduced to either explicit alternative.'
    }
    conf=run['configuration']
    if conf=='extended':
        unknowns='Unbound unknowns are S.suspend.Var objects, self-referential until bound; deref returns their value. The same Var is used at repeated occurrences.'
        mechanism='S suspension queue runs relation goals FIFO and wakes them on bindings; each evaluator decides one primitive relation. No elimination, finite-domain propagator, or search is used.'
    elif conf=='core':
        unknowns='Unknowns are string place names absent from the known mapping; place returns None until the name has a binding. Repeated names share a mapping entry.'
        mechanism='Repeated passes over the held list decide one primitive relation at a time as values become known; no elimination or search.'
    else:
        unknowns='Unknowns are string place names absent from the shared known mapping; place returns None until bound. Repeated names share the entry.'
        mechanism='One daemon threading.Thread per primitive relation; a threading.Condition protects the store and wakes workers on new bindings. settle waits until every worker is waiting or done. Each evaluator decides one relation at a time; no elimination or search.'
    nrel,nocc={'a':(4,8),'b':(2,4),'c':(1,2),'d':(3,5),'e':(3,5),'f':(2,4),'g':(1,2)}[letter]
    answers=[v['verbatim'] for q in c['queries'] for v in q['answers']]
    expected={'a':1,'b':1,'c':None,'d':1,'e':0,'f':0,'g':2}[letter]
    result={
        'configuration':conf,'instance':run['instance'],'program':Path(run['program']['path']).name,
        'record':str(path.relative_to(SRC)),'stage':stage['stage'],'reached':True,
        'semantic':'complete','representation':'residual' if residual else 'explicit',
        'simplification':simpl,'identical_to_posed':True if residual else None,
        'residual_size':({'relations':nrel,'unknown_occurrences':nocc,'input_relations':nrel,'input_unknown_occurrences':nocc,'unit':'primitive decomposition; repeated occurrences counted separately'} if residual else None),
        'execution_state':c['execution_state']['states'],
        'residual_equivalence':{'equivalent':True,'reason':proofs[letter]},
        'observations':{
            'reported_verbatim':{'answers':answers,'stdout':a['stdout'],'observe':a['observe']['raw']},
            'unknowns_representation':unknowns,
            'bindings_verbatim':a['observe']['bindings'],
            'alternatives':{'count':c['alternatives']['at_boundary'],'held_as':'none; solutions remain implicit in relations' if residual else 'none','peak':None,'peak_note':'unavailable'},
            'suspended_work':{'count':c['suspended']['at_boundary'],'items':c['suspended']['items'],'unit':c['suspended']['unit'],'peak':None,'peak_note':'unavailable'},
            'withdrawn_conclusions':[], 'manual_actions':d['manual_actions']+a['manual_actions'],
            'mechanism':mechanism,
            'inconsistency_detected':(letter=='e') if letter in 'ef' else None,
            'both_square_solutions_found':False if letter=='g' else None,
            'square_solution_note':'Both are represented implicitly by the equivalent residual; neither is enumerated.' if letter=='g' else None,
            'answer_completeness':{'explicit_valid_answers':len(answers),'expected_finite_answers':expected,'invalid_answers':0,'empty_set_reported':(letter=='e') if letter in 'ef' else None,'equivalent_finite_representation':True},
            'steps':c['steps'], 'store':a['store'],
            'problem_operations':c['problem_operations'],
            'measurement_note':'null measurements are unavailable, not zero (AMENDMENTS 3.1).',
            'stage_input_size':{'relations':nrel,'unknown_occurrences':nocc},
            'error_verbatim':c['execution_state']['error_verbatim'],
        },
        'rule':'SPECIFICATION Outcomes 1-3 (equivalence and simplification separate; state read by observe); P07 valid outcomes; METRICS rule 19; AMENDMENTS 3',
        'harness_fault':bool('.INVALID.' in path.name or d['harness_faults']),
    }
    return result,d,a,c


def main():
    with (SRC/'results/python/tokens/TEXTS-1B-P07.tsv').open() as f:
        texts=list(csv.DictReader(f,delimiter='\t'))
    data={'tokens':{},'outcomes':[],'mode_differences':[],'expressibility':[],'late_definition':[],'s_mechanisms':[]}
    token_rows={}
    for row in texts:
        key=row['text']; assert not row['also the text of']
        spans,rows=classify_text(key); data['tokens'][key]=spans; token_rows[key]=rows
        conf,file=key.split('/')
        if conf=='extended':
            data['s_mechanisms'].append({'configuration':conf,'program':file,'mechanism':'suspension queue, including Var and deref (harnesses/python/S/suspend.py)','listed_at_phase_4':True,'tokens':537,'counting':'537 implementation tokens once per configuration; listed for every using program; call sites separately classed','token_ranges':None})
            local=[{'from':s['from'],'to':s['to']} for s in spans if s['class']=='S']
            data['s_mechanisms'].append({'configuration':conf,'program':file,'mechanism':'program-supplied generic Relation goal adapter and failure store','listed_at_phase_4':False,'tokens':sum(s['to']-s['from']+1 for s in spans if s['class']=='S'),'token_ranges':local,'counting':'identical generic mechanism copied into seven texts; count once per configuration, not seven times'})
        reason=('The arithmetic relations are encoded as held places and dispatched on which places are known. Rule 19 gives the holding/known-place tests R while every mathematical evaluator direction is P. This preserves the integer relation, including unresolved conjunctions; inability to simplify b/f/g does not change expressibility. ')
        if conf=='extended': reason+=('For this extended configuration the declared suspension queue supplies variables and waiting; the reusable Relation adapter is additional S, explicitly recorded separately. This is expressibility with those supporting mechanisms available, not native core expressibility.')
        elif conf=='stdlib-concurrency': reason+=('threading is an external mechanism within this configuration: Condition/Thread/wake/settle constructs are C. The arithmetic store is fixed to the problem vocabulary, not a generic user-supplied relation interface.')
        else: reason+=('The fixed dispatch table contains only the problem arithmetic vocabulary (=,+,-,*); its holding code is treated as problem-specific R under rule 19, rather than a general constraint-store S mechanism.')
        data['expressibility'].append({'configuration':conf,'subproblem':file[:-3],'direction':None,'expressibility':'expressible with reformulation','reason':reason})
    groups={}
    for conf in CONFIGS:
        for path in sorted((SRC/'results/python'/conf/'P07/raw').glob('*.json')):
            result,d,a,c=classify_record(path)
            run=d['run']; k=(conf,run['instance'],run['program']['path'])
            groups.setdefault(k,{})[run['mode']]=(result,d,a,c)
            if run['mode']=='behaviour': data['outcomes'].append(result)
        assert not (SRC/'results/python'/conf/'P07/raw-rerun-m2').exists()
    # Verify each logged P07 run is represented, without reading other
    # problems' records. The log itself is authorized in its entirety.
    logrows=[line.split('\t') for line in (SRC/'results/python/batch-log.tsv').read_text().splitlines() if '\tP07' in line]
    assert len(logrows)==108 and len(groups)==36
    assert len(data['outcomes'])==36
    compared=0
    for key,modes in groups.items():
        assert set(modes)=={'behaviour','cost','storage'}
        b=modes['behaviour'][0]
        # Compare all classification-bearing outputs/state, excluding costs,
        # allocation measurements and dictionary insertion order.
        for mode in ('cost','storage'):
            r,d,a,c=modes[mode]; compared+=1
            fields=('reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence','harness_fault')
            changed=any(r[f]!=b[f] for f in fields)
            bo=b['observations']; ro=r['observations']
            assert bo['reported_verbatim']['answers']==ro['reported_verbatim']['answers']
            assert bo['reported_verbatim']['stdout']==ro['reported_verbatim']['stdout']
            assert bo['bindings_verbatim']==ro['bindings_verbatim']
            assert bo['alternatives']['count']==ro['alternatives']['count']
            assert bo['suspended_work']['count']==ro['suspended_work']['count']
            for name,count in bo['suspended_work']['items'].items():
                assert ro['suspended_work']['items'][name]==count
            for name,count in ro['suspended_work']['items'].items():
                if name not in bo['suspended_work']['items']:
                    assert count==0 and '(gc, process-wide)' in name
            if changed:
                data['mode_differences'].append({'configuration':r['configuration'],'instance':r['instance'],'program':r['program'],'mode':mode,'record':r['record'],'stage':r['stage'],'behaviour':{f:b[f] for f in fields},'this_mode':{f:r[f] for f in fields},'note':'Classification differs from matched behaviour record.'})
    assert compared==72 and not data['mode_differences']
    totals=collections.Counter(); perconf=collections.defaultdict(collections.Counter)
    for key,spans in data['tokens'].items():
        indices=[]
        for span in spans:
            assert span['class'] in 'PCRSH'
            assert span['to']>=span['from']
            indices.extend(range(span['from'],span['to']+1))
            n=span['to']-span['from']+1
            totals[span['class']]+=n;perconf[key.split('/')[0]][span['class']]+=n
        assert indices==list(range(len(token_rows[key]))),key
    (OUT/'python.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    summary={'texts':len(texts),'tokens':dict(totals),'by_configuration':{k:dict(v) for k,v in perconf.items()},'behaviour_stages':len(data['outcomes']),'mode_comparisons':compared,'mode_differences':len(data['mode_differences']),'local_S_per_program':{e['program']:e['tokens'] for e in data['s_mechanisms'] if not e['listed_at_phase_4']}}
    (OUT/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
