"""Independent classifier B. Reads only authorized files; never imports programs.

The frozen TSVs are the sole token stream. ASTs locate constructs in source;
matching a frozen token to its source position does not generate new tokens.
"""
from pathlib import Path
import ast
import csv
import json
import re
from collections import Counter, defaultdict

ROOT = Path('.')
OUT = Path('results/python/classes/B')
TEXTS = list(csv.reader((ROOT/'results/python/tokens/TEXTS.tsv').open(), delimiter='\t'))[1:]

def tokens_for(path):
    rows = list(csv.DictReader((ROOT/'results/python/tokens'/(path+'.tokens.tsv')).open(), delimiter='\t'))
    assert [int(t['index']) for t in rows] == list(range(len(rows)))
    return rows

def classify_tokens(path):
    source = (ROOT/'programs/python'/path).read_text()
    lines = source.splitlines()
    tree = ast.parse(source)  # parsing only; no execution and no tokenizer calls
    rows = tokens_for(path)
    conf, filename = path.split('/')
    labels = [None]*len(rows)
    positions = []
    cursors = defaultdict(int)
    for t in rows:
        ln, word = int(t['line']), t['token']
        if word in ('<INDENT>', '<DEDENT>'):
            positions.append(None)
        elif word == '<NEWLINE>':
            positions.append((ln, len(lines[ln-1])))
        else:
            col = lines[ln-1].find(word, cursors[ln])
            assert col >= 0, (path, t)
            positions.append((ln, col))
            cursors[ln] = col+len(word)

    def put(node, cls, construct, rule, header=False):
        label = (cls, construct, rule)
        start = (node.lineno, node.col_offset)
        end = (node.end_lineno, node.end_col_offset)
        # Newline closes its statement, and is part of that construct.
        for i, pos in enumerate(positions):
            if pos is not None and rows[i]['token']!='<NEWLINE>' and start <= pos < end:
                labels[i] = label
            elif isinstance(node,ast.stmt) and pos is not None and rows[i]['token']=='<NEWLINE>' and start[0] <= pos[0] <= end[0]:
                labels[i] = label
        # A comma separating arguments belongs to the argument that follows it.
        if not isinstance(node,ast.stmt):
            inside=[i for i,p in enumerate(positions) if p is not None and rows[i]['token']!='<NEWLINE>' and start<=p<end]
            if inside and inside[0]>0 and rows[inside[0]-1]['token']==',':
                labels[inside[0]-1]=label
        return label

    compound_headers = {}
    evaluator_names = {'equal', 'plus', 'times', 'conc_places'}
    direction_names = {'split', 'rest', 'front', 'unrev'}
    s_names = {'unify', 'children', 'done'}

    def visit(node, inherited=None, function=None):
        text = ast.get_source_segment(source, node) or ''
        head = text.splitlines()[0]
        cls, rule = inherited or ('P', 'METRICS 1, 3')
        construct = head
        if inherited and inherited[0] in {'S','H'}:
            if isinstance(node,ast.FunctionDef) and node.name=='__repr__':
                cls,rule='H','METRICS 13: output adapter for an existing held relation'
            # Entire mechanism/adapter, including nested methods, retains its role.
            if isinstance(node,ast.FunctionDef):function=node.name
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            cls, rule = 'C', 'METRICS 12: enable named control/external mechanism; implementation counted separately as S'
        elif isinstance(node, ast.FunctionDef):
            function = node.name
            if function == 'show':
                cls, rule = 'H', 'METRICS 13: output adapter'
            elif function in s_names:
                cls, rule = 'S', 'METRICS 12, 15, 19: general unifier or goal-list resolution mechanism'
            elif function in direction_names:
                cls, rule = 'R', 'METRICS 3, 14: separately written inverse direction'
            elif function in evaluator_names:
                cls, rule = 'R', 'METRICS 19: evaluator interface and known-place dispatch; body split below'
            elif function in {'conc', 'rev'}:
                cls, rule = 'P', 'METRICS 2, 3: one branch per given case in the direction used'
            elif function == 'cons':
                cls, rule = 'R', 'METRICS 3, 15: additional cons-cell encoding not defined as P by systems/python'
            else:
                cls, rule = 'R', 'METRICS 19: holding and re-examining this problem vocabulary'
        elif isinstance(node, ast.ClassDef):
            cls, rule = 'S', 'METRICS 12, 19: Relation accepts an arbitrary evaluator, generic suspension adapter'
        elif function in direction_names or function == 'cons':
            cls, rule = 'R', 'METRICS 14 (inverse direction) or 3,15 (added encoding)'
        elif function in evaluator_names:
            if isinstance(node, ast.If) and ('is not None' in ast.unparse(node.test) or 'is None' in ast.unparse(node.test)):
                cls, rule = 'R', 'METRICS 19: which places are known'
            elif isinstance(node, ast.Return) and isinstance(node.value, ast.Constant) and node.value.value is None:
                cls, rule = 'R', 'METRICS 19: verdict to wait'
            else:
                cls, rule = 'P', 'METRICS 19: evaluate a place or test the fully known relation, in every direction'
        elif isinstance(node, ast.While) and 'cp.stage' in head:
            cls, rule = 'H', 'Python harness README 7.1: fixed stage loop header; METRICS 10'
        elif isinstance(node, ast.If) and ('s.k' in ast.unparse(node.test) or 's.replay' in ast.unparse(node.test)):
            cls, rule = 'H', 'Python harness README 7.2-3: stage/replay dispatch; METRICS 10'
        elif isinstance(node, ast.If) and ast.unparse(node.test) in {'failed', 'known', 'told'}:
            cls, rule = 'R', 'METRICS 13: test of held state deciding which result to report'
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and ast.unparse(node.value.func).startswith('cp.'):
            cls, rule = 'H', 'Python harness README 7.4: fixed registration/answer call'
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and ast.unparse(node.value.func)=='print':
            cls, rule = 'H', 'METRICS 13: output only'
        elif isinstance(node, (ast.Assign, ast.AnnAssign)) and function is None:
            target = ast.unparse(node.targets[0]) if isinstance(node, ast.Assign) else ast.unparse(node.target)
            if target == 'UNKNOWNS' or target in {'shown','told'} or (target.startswith('shown[')):
                cls, rule = 'H', 'METRICS 13: output names or already-computed rendered bindings'
            elif filename.startswith('P03') and (target=='known' or target.startswith('known[')):
                if isinstance(node,ast.Assign) and isinstance(node.value,ast.Call) and ast.unparse(node.value.func) in {'conc','rev'}:
                    cls,rule='P','METRICS 1,3: compute the posed forward query'
                else:
                    cls,rule='H','METRICS 13: collect already-computed query answers for observe()'
            elif target in {'known','held','waiting','failed','RELATION','EVALUATOR'}:
                cls, rule = 'R', 'METRICS 19: problem-specific binding/undecided-relation bookkeeping'
            elif target in {'changed','count'}:
                cls, rule = 'C', 'METRICS 1, 10: synchronization state for threading external mechanism'
            elif target in {'q','binder','trail','stack'}:
                cls, rule = 'C', 'METRICS 12: instantiate suspension/search control mechanism'
            elif target == 'name' and 's.params' in text:
                cls, rule = 'H', 'Python harness README 7.3: instance arrival order'
            elif target == 'answers':
                cls, rule = 'R', 'METRICS 3,14: query through the separately written direction'
            elif target.startswith('known['):
                cls, rule = 'P', 'METRICS 1,3: query result/binding'
            elif target in {'x','u, v, w','x, y, z','s_, t','unknowns','a','b','a, b','c','NIL','query'}:
                cls, rule = 'P', 'METRICS 1,3: unknowns, query, or empty-sequence value'
        elif isinstance(node, ast.For) and function is None:
            if 'unknowns.items()' in head:
                cls, rule = 'H', 'METRICS 13: render existing bindings'
            elif 'search(' in head:
                cls, rule = 'C', 'METRICS class C,12: search/enumeration directive'
            elif 'answers' in head:
                cls, rule = 'C', 'METRICS class C,10: request successive generator answers'
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            fn = ast.unparse(node.value.func)
            if fn in {'decide'}:
                cls, rule = 'R', 'METRICS 19: run problem-specific holding pass'
            elif fn in {'settle','q.run','q.wait','pose'}:
                cls, rule = 'C', 'METRICS class C,12: explicit scheduling/waiting/thread directive'
            elif fn in {'held.append'}:
                cls, rule = 'R', 'METRICS 19: post an undecided relation to the problem-specific store'
            elif fn=='failed.append':
                cls, rule = 'R', 'METRICS 19: record an inconsistent relation for subsequent reporting'

        # Synchronization calls are control, even inside problem-specific holding code.
        if function in {'told','hold','pose','settle'} and not (inherited and inherited[0] in {'S','H'}):
            if isinstance(node, ast.With) or any(x in head for x in ['notify_all(', '.wait_for(', 'threading.Thread(', 'count[', 'seen =']):
                cls, rule = 'C', 'METRICS 1,10,12: explicit synchronization via threading (external mechanism)'
        label = put(node, cls, construct, rule)
        # Recurse by statements. A function classified throughout retains its class.
        sticky = (cls,rule) if (cls in {'S','H'} and inherited and inherited[0] in {'S','H'}) or (isinstance(node, ast.ClassDef) or function in s_names|direction_names|{'show','cons'}) else None
        for field in ('body','orelse','finalbody'):
            children = getattr(node,field,[])
            if children:
                # elif has no additional INDENT; any unused mapping is harmless.
                compound_headers[children[0].lineno] = label
            for ch in children:
                if isinstance(ch, ast.stmt):
                    if isinstance(ch, ast.Expr) and isinstance(ch.value, ast.Constant) and isinstance(ch.value.value,str):
                        continue # frozen tokenizer excluded docstrings
                    visit(ch, sticky or (('R','METRICS 19: holding the problem relations') if function in {'place','decide','told','hold','pose','settle'} else None), function)

    for stmt in tree.body:
        visit(stmt)

    # Layout belongs to the enclosing header, including through skipped docstrings.
    layout_stack=[]
    for i,t in enumerate(rows):
        if t['token']=='<INDENT>':
            label=compound_headers.get(int(t['line']))
            assert label is not None,(path,t)
            layout_stack.append(label);labels[i]=label
        elif t['token']=='<DEDENT>':
            assert layout_stack,(path,t)
            labels[i]=layout_stack.pop()
    assert not layout_stack

    # The harness reads are nested H constructs, even within problem arguments.
    for node in ast.walk(tree):
        if isinstance(node,ast.Subscript) and isinstance(node.value,ast.Attribute) and ast.unparse(node.value) in {'s.constants','s.params','cp.params'}:
            put(node,'H',ast.unparse(node),'Python harness README 7.3; METRICS 10: fixed input read')
    # Nested relation arguments of posting/scheduling calls express stage information.
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call):continue
        fn=ast.unparse(node.func)
        if any(isinstance(parent,ast.ClassDef) and parent.lineno<=node.lineno<=parent.end_lineno for parent in ast.walk(tree)):
            continue
        if fn in {'held.append','pose','q.wait'} and node.args:
            arg=node.args[0]
            put(arg,'P',ast.unparse(arg),'METRICS P,10: the relation/places posed, nested within holding or control')
        if fn=='search' and node.args:
            put(node.args[0],'P','posed query passed to search','METRICS P,10: query argument inside C search directive')
        if fn=='cons':
            put(node,'R','conversion to the added cons-cell encoding','METRICS 3,15: extra encoding conversion, not specified as P by systems/python')
        if fn=='Relation' and len(node.args)>1:
            put(node.args[1],'R','extra evaluator argument to the generic Relation adapter','METRICS 3,10,20: the problem does not give an evaluator argument')
    # Reapply fixed input reads after the outer argument classification.
    for node in ast.walk(tree):
        if isinstance(node,ast.Subscript) and isinstance(node.value,ast.Attribute) and ast.unparse(node.value) in {'s.constants','s.params','cp.params'}:
            put(node,'H',ast.unparse(node),'Python harness README 7.3; METRICS 10: fixed input read')

    assert all(labels),(path,[(i,rows[i]) for i,x in enumerate(labels) if x is None])
    spans=[]
    for i,label in enumerate(labels):
        if spans and spans[-1]['_label']==label:
            spans[-1]['to']=i
        else:
            spans.append({'from':i,'to':i,'class':label[0],'construct':label[1],'rule':label[2],'_label':label})
    for span in spans:del span['_label']
    return spans

def all_records():
    records={}
    for p in sorted((ROOT/'results/python').glob('*/P0?/raw/*.json')):
        d=json.loads(p.read_text())
        r=d['run'];key=(r['configuration'],r['instance'],r['mode'])
        assert key not in records
        records[key]=(str(p.relative_to(ROOT)),d)
    return records

def classify_stage(record_path,d,st,reading=None):
    r=d['run'];conf=r['configuration'];inst=r['instance'];sub=r['subproblem'];k=st['stage']
    a=st['attempts'][-1];c=a['computations'][0]
    answers=[v['verbatim'] for q in c['queries'] for v in q['answers']]
    states=c['execution_state']['states']
    held=c['suspended']['at_boundary']
    result=dict(configuration=conf,instance=inst,program=Path(r['program']['path']).name,record=record_path,stage=k,
                reached=True,semantic='complete',representation='explicit',simplification=None,
                identical_to_posed=None,residual_size=None,execution_state=states,
                residual_equivalence=None,observations={},rule='SPECIFICATION Outcomes 1–3; classify reported held state as well as printed answers')
    if reading:result['reading']=reading
    obs=dict(answers_verbatim=answers,observe_verbatim=a['observe']['raw'],print_verbatim=a['print'],
             bindings=a['observe']['bindings'],alternatives=c['alternatives'],suspended=c['suspended'],
             withdrawn_conclusions=[],manual_actions=a.get('manual_actions',[])+d.get('manual_actions',[]),
             error_verbatim=c['execution_state'].get('error_verbatim'),
             measurement_note='Null measurements are unavailable, never zero (AMENDMENTS 3.1).',
             metrics_record=record_path,
             unknowns_representation=('S.suspend.Var objects; aliases or references to values/cons cells' if conf=='extended' else 'names absent from known; named places in held relation tuples'))
    result['observations']=obs
    def residual(relations,occ,input_rel,input_occ,simp,ident,why):
        result.update(representation='residual',simplification=simp,identical_to_posed=ident,
                      residual_size={'residual':{'relations':relations,'unknown_occurrences':occ},
                                     'input':{'relations':input_rel,'unknown_occurrences':input_occ},
                                     'convention':'Primitive arithmetic relations; given conc is one undecided relation; constructor ++ is a term. Bound-place substitution applied; bindings/free variables not counted as undecided relations.'},
                      residual_equivalence={'equivalent':True,'reason':why})
    if sub=='P01a':
        if k<3:
            if conf=='extended':
                result['representation']='solved form'
                result['residual_equivalence']={'equivalent':True,'reason':'Stage 1 aliases x to y, leaves z free. Stage 2 aliases x and y to z. This is precisely the equality chain over all problem values.'}
            else:
                residual(k,2*k,k,2*k,'reducible',True,'The registered equations are exactly the arrived equalities, so denote all and only the valid assignments. Aliasing x=y (and y=z) would remove all undecided equality tests.')
        else:obs['value_reaches_all']='x, y, z all read as 2; no earlier binding lost. Exact instruction latency is available in corresponding cost record.'
    elif sub=='P01b':
        if k==1:
            if conf=='extended':
                result['representation']='solved form'
                result['residual_equivalence']={'equivalent':True,'reason':'Read the reported t=⟨1,2⟩++s in the problem sequence domain: the two given conc cases reduce the known prefix to this term, with s free over finite sequences.'}
            else:
                residual(1,2,1,2,'reducible',True,'The held conc(⟨1,2⟩,s,t) is the posed relation, equivalent by two recursive cases and the base case to t=⟨1,2⟩++s. That solved term has no undecided relation.')
        else:obs['value_reaches_all']='s and t are both determined and observed as ⟨3⟩ and ⟨1,2,3⟩.'
    elif sub=='P01c':
        obs['occurs_check']='No occurs check in S.suspend.Queue.bind (extended); core/concurrency retain the relation and perform no cyclic binding or occurs check.'
        if conf=='extended':
            result['representation']='cyclic'
            result['semantic']='unsound' if reading=='finite' else 'complete'
            obs['reading_reason']='The reported explicit cycle denotes the unique all-1 infinite sequence. It is invalid among finite sequences, and exactly the rational-tree solution.'
        else:
            residual(1,2,1,2,'inconsistency undetected' if reading=='finite' else 'reducible',True,
                     'For finite x, |x|=1+|x| is impossible: both posed and held conditions have no solutions, but no inconsistency is reported.' if reading=='finite' else 'Unfolding x=⟨1⟩++x forces every element to 1; its unique rational solution is the all-1 cycle, which is a smaller cyclic term. The retained conc condition has exactly this meaning under the rational reading.')
    elif sub.startswith('P02'):
        order=r['parameters'].get('order',['R1','R2','R3'])
        arrived=set(order[:k]) if sub!='P02c' else {'R1','R2','R3'}
        input_n=len(arrived);input_occ=sum({'R1':2,'R2':3,'R3':1}[x] for x in arrived)
        if arrived=={'R1','R2','R3'}:
            obs['derivation']='R3 gives u=12−10=2; R1 gives v=16−2=14; R2 gives w=14/2=7. All six orders reach this final assignment.'
        elif arrived=={'R3'} or arrived=={'R1','R3'}:
            result['representation']='solved form'
            result['residual_equivalence']={'equivalent':True,'reason':'R3 fixes u=2, with v,w free integers.' if arrived=={'R3'} else 'R3 fixes u=2 and R1 fixes v=14, with w free over all integers.'}
        elif arrived=={'R2','R3'}:
            residual(1,2,input_n,input_occ,'reduced',False,'The observed binding u=2 together with the held multiplication denotes v=2w for every integer w, exactly the valid outcomes. One arithmetic relation is necessary under the specified solved-form term vocabulary.')
        elif arrived=={'R1','R2'}:
            residual(2,5,input_n,input_occ,'reducible',True,'Eliminate v to obtain u(w+1)=16. Thus u is a nonzero signed divisor of 16, v=16−u and w=16/u−1: precisely the ten triples listed in P02. The conjunction is equivalent but the ten explicit triples leave no undecided relations; see check_residuals().')
        elif arrived=={'R1'}:
            residual(1,2,1,2,'reduced',True,'The held u+v=16 is exactly the posed relation over all integers, w free; SPECIFICATION explicitly classes this residual as reduced.')
        elif arrived=={'R2'}:
            residual(1,3,1,3,'reduced',True,'The held w·u=v is exactly the arrived integer relation, including zero factors; no domain restriction or enumeration was imposed.')
        obs['waiting_on']='Each retained relation waits for enough of its named places to become bound for its evaluator; plus/times require two known places. Held R1,R2 do not enumerate their joint solutions.'
        obs['resume_order']='Core scans arrival order to a fixpoint; extended wakes queued goals FIFO through S.suspend; concurrency wakes relation threads via notify_all, with lock acquisition order not fixed by the record.'
    elif sub.startswith('P03'):
        obs['answer_completeness']={'valid_obtained':len(answers),'valid_expected':3 if sub=='P03b' else 1,'invalid_obtained':0}
        obs['answer_order']='The three prefix/suffix splits in increasing prefix length.' if sub=='P03b' else 'The sole valid sequence, as recorded verbatim.'
        if sub=='P03f' and conf=='extended':
            term=ast.parse(a['observe']['bindings']['a'],mode='eval').body
            length=0
            while isinstance(term,ast.Tuple) and len(term.elts)==2:
                length+=1;term=term.elts[1]
            assert isinstance(term,ast.Tuple) and not term.elts and length!=3
            result['semantic']='unsound'
            result['rule']='SPECIFICATION Outcomes 1, reported-binding paragraph: observe-held bindings at budget are reported even if not delivered by the answer mechanism; P03f answer-then-budget example does not remove additional reports.'
            obs['budget_note']=f'One valid printed answer precedes 10^6 instructions, but observe also reports a bound finite cons sequence of length {length}, with fresh h places. Every instantiation of that held term has the wrong length; valid a has length 3. Under the explicit observed-binding rule this additional report is unsound. Under an answer-only reading it would be complete/budget; that is not the adopted reading. The unresolved goal list is not registered as a residual that could qualify this binding.'
            obs['answer_completeness']['additional_invalid_observed_binding']=1
        if conf=='extended':
            obs['search_undo']='Exhausted searches undo bindings, so observe may show free Vars after valid answers were printed; those are restored search roots, not withdrawals of the reported query solutions.'
    return result

def check_residuals():
    # Mathematical reference calculation only, not evaluation of any program.
    expected={(1,15,15),(2,14,7),(4,12,3),(8,8,1),(16,0,0),(-1,17,-17),(-2,18,-9),(-4,20,-5),(-8,24,-3),(-16,32,-2)}
    got={(u,16-u,16//u-1) for u in range(-16,17) if u and 16%u==0}
    assert got==expected
    assert all(u+v==16 and w*u==v for u,v,w in got)
    assert {t for t in got if t[0]+10==12}=={(2,14,7)}
    # Any integer divisor of 16 has absolute value <=16, so this is exhaustive,
    # rather than a finite-domain approximation to the problem's integers.
    return sorted(got)

def expressibility():
    result=[]
    for conf in ['core','extended','stdlib-concurrency']:
        for sub in ['P01a','P01b','P01c','P02a','P02b','P02c','P03a','P03b','P03c','P03d','P03e','P03f']:
            direction=None
            if sub.startswith('P03'):
                direction={'P03a':'conc: a,b → c','P03b':'conc: c → a,b','P03c':'conc: a,c → b','P03d':'conc: b,c → a','P03e':'rev: a → b','P03f':'rev: b → a'}[sub]
            if conf!='extended':
                if sub in {'P03a','P03e'}:
                    cls='expressible';reason='The forward function follows each given case and the given conjunct order (METRICS 3,8).'
                elif sub.startswith('P03'):
                    cls='expressible with reformulation';reason='A separate inverse direction function retains the relation on finite sequence inputs; all its tokens are R under METRICS 3,14. P03f additionally moves conc before recursive rev (one move, METRICS 4).'
                else:
                    cls='expressible with reformulation';reason='Named unknowns and a store for this fixed problem vocabulary hold undecided relations; this is R under METRICS 19. Evaluator mathematics remains P. '+('threading is an external scheduling mechanism, with C call tokens.' if conf=='stdlib-concurrency' else 'No native unknown aliasing or relational suspension is used.')
            elif sub=='P01a':
                cls='expressible';reason='The supplied S.suspend Var/Queue mechanism directly aliases unknowns and binds the final value; stage equality calls are P, mechanism size counted separately.'
            elif sub in {'P01b','P01c'}:
                cls='expressible with reformulation';reason='The forward conc cases are P, but the program adds a cons-cell encoding (cons), not defined by systems/python as a P encoding (METRICS 3,15). S.suspend supplies variable binding. P01c yields the rational cycle; failure to reject it in the finite reading is recorded separately as unsound.'
            elif sub.startswith('P02'):
                cls='expressible with reformulation';reason='Known-place dispatch and wait verdicts are R (METRICS 19); the mathematical evaluator bodies are P. The actual generic Relation adapter is additional S under METRICS 12,19 and must be disclosed separately from phase-4 S.suspend. The problem-specific core adapter also works in this configuration, so the use of S here is not evidence of non-expressibility.'
            else:
                cls='expressible' if sub in {'P03a','P03e'} else 'expressible with reformulation';reason='The core mode-faithful forward definitions remain available.' if sub in {'P03a','P03e'} else 'The meaning-preserving core inverse direction remains available (METRICS 3,14); P03f moves conc before recursive rev, one move.'
                reason+=' The actual relational program instead adds generic unify/children/done S beyond the three phase-4 mechanisms, plus R cons conversion. Its P relation cases do not establish native reversibility in the originally listed configuration; the additional mechanisms must accompany its outcome.'
            result.append(dict(configuration=conf,subproblem=sub,direction=direction,expressibility=cls,reason=reason))
    return result

def main():
    tokens={row[0]:classify_tokens(row[0]) for row in TEXTS}
    records=all_records();outcomes=[];mode_differences=[]
    for (conf,inst,mode),(path,d) in records.items():
        if mode!='behaviour':continue
        for st in d['stages']:
            readings=['finite','rational'] if d['run']['subproblem']=='P01c' else [None]
            for reading in readings:
                outcome=classify_stage(path,d,st,reading)
                for metric_mode in ['cost','storage']:
                    mp,md=records[conf,inst,metric_mode]
                    ma=md['stages'][st['stage']-1]['attempts'][-1]
                    mc=ma['computations'][0]
                    outcome['observations'][metric_mode+'_measurements']=(dict(record=mp,steps=mc['steps'],problem_operations=mc['problem_operations']) if metric_mode=='cost' else dict(record=mp,store=ma['store'],alternatives=mc['alternatives'],suspended=mc['suspended']))
                outcomes.append(outcome)
    axes=['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence']
    for (conf,inst,mode),(path,d) in records.items():
        if mode=='behaviour':continue
        bp,bd=records[conf,inst,'behaviour']
        assert len(d['stages'])==len(bd['stages'])
        for st,bst in zip(d['stages'],bd['stages']):
            readings=['finite','rational'] if d['run']['subproblem']=='P01c' else [None]
            for reading in readings:
                b=classify_stage(bp,bd,bst,reading);m=classify_stage(path,d,st,reading)
                assert b['observations']['answers_verbatim']==m['observations']['answers_verbatim'],(conf,inst,mode)
                if any(b[x]!=m[x] for x in axes):
                    mode_differences.append(dict(configuration=conf,instance=inst,program=m['program'],mode=mode,record=path,stage=st['stage'],reading=reading,behaviour={x:b[x] for x in axes},this_mode={x:m[x] for x in axes},note='Classification differs from behaviour.'))
    obj=dict(tokens=tokens,outcomes=outcomes,mode_differences=mode_differences,expressibility=expressibility())
    (OUT/'python.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    triples=check_residuals()
    totals=Counter()
    byconf=defaultdict(Counter)
    for path,spans in tokens.items():
        expected=0
        for s in spans:
            assert s['from']==expected and s['to']>=s['from']
            expected=s['to']+1
            totals[s['class']]+=s['to']-s['from']+1
            byconf[path.split('/')[0]][s['class']]+=s['to']-s['from']+1
        assert expected==len(tokens_for(path))
    assert len(outcomes)==105
    log=list(csv.reader((ROOT/'results/python/batch-log.tsv').open(),delimiter='\t'))
    assert len(records)==len(log)==153
    assert Counter((row[1],row[2],row[3],row[4]) for row in log)==Counter((c,i,Path(d['run']['program']['path']).name,m) for (c,i,m),(p,d) in records.items())
    for first,*shared in TEXTS:
        for other in shared:
            if not other:continue
            assert (ROOT/'programs/python'/first).read_bytes()==(ROOT/'programs/python'/other).read_bytes()
            assert tokens_for(first)==tokens_for(other)
    summary=dict(distinct_texts=len(tokens),tokens=dict(totals),by_first_path_configuration={k:dict(v) for k,v in byconf.items()},behaviour_records=51,behaviour_stages=102,reading_classifications=len(outcomes),mode_differences=len(mode_differences),semantic=dict(Counter(o['semantic'] for o in outcomes)),representations=dict(Counter(o['representation'] for o in outcomes)),execution=dict(Counter(x for o in outcomes for x in o['execution_state'])),residual_checks=triples)
    (OUT/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
