"""Independent classification/checks. Reads source, frozen tokens and records only.

Never imports or executes a study program, harness, or S implementation.
The AST is used to locate constructs, never to generate lexical tokens.
"""
import ast
import collections
import copy
import json
import re
from pathlib import Path

ROOT = Path('.')
OUT = Path('results/python/classes-1B/B/parts/python-P08')
CONFIGS = ['core', 'extended', 'stdlib-concurrency']
PROGRAMS = ['P08a.py', 'P08b.py', 'P08c.py']
RULES = {
    'P': 'METRICS class P; rules 2, 3, 10 and 15: problem information, case transcription or its value encoding',
    'C': 'METRICS class C; rules 1, 2, 10 and 12: explicit scheduling, suspension or search call',
    'R': 'METRICS rule 19: known-place test or wait verdict in a relation evaluator; rule 10',
    'S': 'METRICS rules 12, 15 and 19: experiment-written mechanism general over relations; rule 10',
    'H': 'METRICS rule 13; Python harness README section 7: fixed harness operation or output-only adapter; rule 10',
}

def frozen(cfg, program):
    p = ROOT / 'results/python/tokens' / cfg / (program + '.tokens.tsv')
    rows = [l.split('\t', 2) for l in p.read_text().splitlines()[1:]]
    return [{'index': int(i), 'line': int(l), 'token': t} for i, l, t in rows]

def token_classes(cfg, program):
    source = (ROOT / 'programs/python' / cfg / program).read_text()
    lines = source.splitlines()
    tree = ast.parse(source)
    labels = {}

    def mark(first, last, cl, desc, mechanism=None):
        for line in range(first, last + 1):
            labels[line] = (cl, desc, mechanism)

    # Each statement and compound header gets its own construct. Function-wide
    # classifications below implement rule 12/13, rather than calling every
    # internal loop of an S implementation an additional C mechanism.
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt):
            end = node.lineno if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.If, ast.For, ast.While, ast.With)) else node.end_lineno
            mark(node.lineno, end, 'P', lines[node.lineno - 1].strip().split('#')[0].rstrip())
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            name = n.name
            if name in ['show', 'report', '__repr__']:
                mark(n.lineno, n.end_lineno, 'H', 'output adapter ' + name)
            elif name in ['Unknown', '__init__', 'place', 'decide', 'told', 'hold', 'arrived', 'pose', 'settle',
                          'unify', 'children', 'done', 'Application', '__call__', 'equation']:
                if cfg == 'extended':
                    mech = 'term unification' if name == 'unify' else ('goal-list resolution' if name in ['children', 'done'] else 'late-definition application store')
                else:
                    mech = 'generic named-place relation store' if name in ['Unknown', '__init__', 'place', 'decide'] else 'generic threaded relation and definition scheduler'
                mark(n.lineno, n.end_lineno, 'S', 'supporting mechanism: ' + name, mech)
            elif cfg == 'extended' and name in ['rev', 'conc']:
                mark(n.lineno, n.end_lineno, 'S', 'dispatch through the arriving case table: ' + name, 'late-definition application store')
    # Nested output methods inside an S class remain H (rule 10/13).
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == '__repr__':
            mark(n.lineno, n.end_lineno, 'H', 'output adapter __repr__')
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name in ['equal', 'prefix', 'reverse']:
            for c in ast.walk(n):
                if isinstance(c, ast.If) and ('is None' in ast.unparse(c.test) or 'is not None' in ast.unparse(c.test)):
                    # r is None is a case-failure test, not a known-place test.
                    if ast.unparse(c.test) != 'r is None':
                        mark(c.lineno, c.lineno, 'R', 'known-place dispatch in ' + n.name)
                elif isinstance(c, ast.Return) and isinstance(c.value, ast.Constant) and c.value.value is None:
                    mark(c.lineno, c.end_lineno, 'R', 'wait verdict in ' + n.name)
        elif isinstance(n, ast.FunctionDef) and n.name == 'equation':
            mark(n.lineno, n.lineno, 'P', 'equality evaluator declaration (rule 19)')
            for c in ast.walk(n):
                if isinstance(c, ast.If):
                    mark(c.lineno, c.lineno, 'P', 'test equality by the S unifier (rules 12, 15, 19)')

    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        if s.startswith(('cp.', 'while (s := cp.stage())', 'if s.k ==', 'elif s.k ==', 'if not s.replay:')):
            mark(i, i, 'H', s.split('#')[0].rstrip())
        if cfg != 'extended' and s.startswith(('known =', 'held =', 'waiting =', 'failed =', 'EVALUATOR =', 'count =', 'defined =')):
            mech = 'generic named-place relation store' if cfg == 'core' else 'generic threaded relation and definition scheduler'
            mark(i, i, 'S', s.split('#')[0].rstrip(), mech)
        if cfg == 'extended':
            if s.startswith('from S.'):
                mech = 'backtracking search' if 'S.search' in s else 'suspension queue'
                mark(i, i, 'S', 'import supporting mechanism: ' + mech, mech)
            elif s.startswith(('binder =', 'trail =', 'stack =')):
                mark(i, i, 'S', s.split('#')[0].rstrip(), 'term unification' if not s.startswith('stack') else 'goal-list resolution')
            elif s.startswith(('cases =', 'defined =', 'failed =', 'NAME =')):
                mark(i, i, 'S', s.split('#')[0].rstrip(), 'late-definition application store')
            elif s.startswith(('q = Queue()', 'q.bind(', 'q.run()')):
                mark(i, i, 'C', s.split('#')[0].rstrip())
            elif s.startswith('unknowns ='):
                mark(i, i, 'H', 'mapping used only by bindings observation and output')
        else:
            if s in ['decide()', 'settle()'] or s.startswith('arrived('):
                mark(i, i, 'C', s)
            elif s == 'import threading' or s.startswith('changed = threading.Condition()'):
                mark(i, i, 'C', 'external threading mechanism: ' + s.split('#')[0].rstrip())

    rows = frozen(cfg, program)
    assigned = []
    indent_stack = []
    last_nonlayout = None
    for r in rows:
        t = r['token']
        if t == '<DEDENT>':
            assert indent_stack
            label = indent_stack.pop()
        elif t == '<INDENT>':
            assert last_nonlayout is not None
            label = last_nonlayout
            indent_stack.append(label)
        else:
            label = labels.get(r['line'])
            assert label is not None, (cfg, program, r)
            if t != '<NEWLINE>':
                last_nonlayout = label
        assigned.append(label)

    def replace_range(first, last, cl, desc, mech=None):
        for i in range(first, last + 1):
            assigned[i] = (cl, desc, mech)

    # Mixed-role arguments are split on the frozen indices, never retokenized.
    # Harness constant access is H even inside P information.
    for i in range(len(rows) - 3):
        if [r['token'] for r in rows[i:i+3]] == ['s', '.', 'constants']:
            end = i + 3
            while rows[end]['token'] != ']':
                end += 1
            first = i - 1 if i and rows[i-1]['token'] == ',' else i
            replace_range(first, end, 'H', 'stage constants read (preceding comma follows its argument, rule 20)')
    for line in set(r['line'] for r in rows):
        ids = [r['index'] for r in rows if r['line'] == line and r['token'] not in ['<INDENT>', '<DEDENT>']]
        if line > len(lines) or not ids:
            continue
        s = lines[line-1].strip()
        if s.startswith('q.wait(Application('):
            # q.wait schedules, Application(rev,args) is the posed query.
            first = next(i for i in ids if rows[i]['token'] == 'Application')
            end = max(i for i in ids if rows[i]['token'] == ')') - 1
            for j in range(first, end + 1):
                if assigned[j][0] != 'H':
                    assigned[j] = ('P', 'posed rev application inside a suspension call', None)
            for j in ids:
                if j < first or j > end:
                    assigned[j] = ('C', 'suspension queue wait directive', None)
        if cfg == 'stdlib-concurrency' and s.startswith('pose(('):
            # Separate scheduling call from the relation it posts.
            first = next(i for i in ids if rows[i]['token'] == '(') + 1
            last = max(i for i in ids if rows[i]['token'] == ')') - 1
            for j in ids:
                if j < first or j > last:
                    assigned[j] = ('C', 'start a relation thread', None)
        if cfg == 'stdlib-concurrency' and s.startswith('if a is not None and "rev" in defined:'):
            first = next(i for i in ids if rows[i]['token'] == 'and')
            replace_range(first, max(ids), 'C', 'definition-availability synchronization beyond the case head (rules 1, 2, 10)')

    spans = []
    for i, label in enumerate(assigned):
        cl, desc, mechanism = label
        # Do not merge independent constructs that happen to share a class.
        key = (cl, desc, mechanism)
        if spans and key == spans[-1]['_key']:
            spans[-1]['to'] = i
        else:
            spans.append({'from': i, 'to': i, 'class': cl, 'construct': desc, 'rule': RULES[cl], '_key': key})
    mechanisms = collections.defaultdict(list)
    for span in spans:
        if span['class'] == 'S':
            mechanisms[span['_key'][2]].append([span['from'], span['to']])
        del span['_key']
    assert not indent_stack
    return spans, mechanisms, rows

def load_records():
    all_records = []
    for cfg in CONFIGS:
        for folder in ['raw', 'raw-rerun-m2']:
            for p in sorted((ROOT / 'results/python' / cfg / 'P08' / folder).glob('*.json')):
                all_records.append((str(p.relative_to(ROOT)), json.loads(p.read_text())))
    return all_records

def size(relations, occurrences, input_relations, input_occurrences, detail):
    return {'unit': 'primitive undecided relations and unknown occurrences',
            'residual': {'relations': relations, 'unknown_occurrences': occurrences},
            'input': {'relations': input_relations, 'unknown_occurrences': input_occurrences},
            'convention': 'Solved bindings are listed in observations, not counted as undecided relations. Input counts the staged query equations before solving; definition clauses are vocabulary, not query constraints. A sequence literal is a term, not extra relations. The stage-6 ++ equation is one primitive concatenation relation. Residual unknown occurrences are counted after substituting solved bindings into its arguments.',
            'detail': detail}

def classify_stage(path, j, st, reading):
    cfg = j['run']['configuration']; inst = j['run']['instance']; k = st['stage']
    a = st['attempts'][-1]; c = a['computations'][0]
    reached = not any('was never posed' in n for n in a['notes'])
    raw = a['observe']['raw']
    entry = {'configuration': cfg, 'instance': inst, 'program': Path(j['run']['program']['path']).name,
             'record': path, 'stage': k, 'reading': reading, 'reached': reached,
             'semantic': None, 'representation': None, 'simplification': None,
             'identical_to_posed': None, 'residual_size': None,
             'execution_state': c['execution_state']['states'] if reached else ['not reached'],
             'residual_equivalence': None, 'harness_fault': '.INVALID.json' in path or bool(j['harness_faults']),
             'observations': {
                 'answers_verbatim': [v['verbatim'] for q in c['queries'] for v in q['answers']],
                 'print_verbatim': a['print'], 'observe_verbatim': raw,
                 'unknowns': 'S.suspend.Var objects with identity and dereference; sequences are cons cells.' if cfg == 'extended' else 'Unknown objects named by .name; bindings held in a dictionary; sequences are tuples of places.',
                 'alternatives': c['alternatives'], 'suspended': c['suspended'],
                 'conclusion_withdrawn': None, 'manual_actions': j['manual_actions'] + a['manual_actions'],
                 'posing': a['posed'], 'record_notes': a['notes'],
                 'error_verbatim': c['execution_state']['error_verbatim'],
                 'measurements': {'steps': c['steps'], 'store': a['store'], 'problem_operations': c['problem_operations']},
             },
             'rule': 'SPECIFICATION Outcomes 1–3 and reported bindings; P08 valid outcomes under the named reading; AMENDMENTS 3.1–3.2'}
    o = entry['observations']
    if not reached:
        entry['semantic'] = 'none reported'
        o['stopped_by'] = "Replay of stage 2 raises NameError: name 'rev' is not defined, before this stage is posed. Copied fields belong to that earlier failure."
        o['measurements']['steps']['to_end'] = None
        o['measurements']['availability_note'] = 'No stage cost or stage-boundary store is available for this unposed stage; restart/restated counts describe the failed replay.'
        return entry

    if inst == 'P08c' and k == 1:
        entry.update(semantic='complete', representation='solved form', residual_equivalence='Equivalent: the stage only introduces conc; there is no query constraint and the empty binding environment represents the one empty substitution. The absence of printed answers does not assert failure.')
        return entry

    if cfg == 'core' and k == 2:
        o['undefined_relation_state'] = 3
        o['suspension_note'] = 'One registered list item survives the exception, but it is dead work: no continuation waits for code, and later replay fails before reaching a later stage. It is not counted as a live reported residual under SPECIFICATION Outcomes 2.'
        if inst == 'P08c':
            entry['semantic'] = 'none reported'
            entry['residual_equivalence'] = None
            o['answer_completeness'] = 'No binding or live residual was reported; an exception is not a report of the empty solution set.'
        else:
            entry.update(semantic='complete' if reading == 'open' else 'unsound', representation='solved form',
                         residual_equivalence='The observed binding a=<x,y,z>, with b free, is exactly the open-reading solution set. The error abandons the application, rather than reporting it as resumable. It is not equivalent under closed semantics, where there are no solutions.')
        return entry

    # The live pending application is a residual condition. Under the closed
    # interpretation the condition is false; correctness and simplification
    # are separate, rather than treating waiting as a report of success.
    if k in [2, 3] and inst in ['P08a', 'P08b'] or (inst == 'P08c' and k == 2):
        entry.update(semantic='complete', representation='residual')
        entry['simplification'] = 'inconsistency undetected' if reading == 'closed' else ('reducible' if cfg == 'stdlib-concurrency' and k == 3 else 'reduced')
        entry['identical_to_posed'] = not (cfg == 'extended' and k == 3)
        if inst == 'P08c':
            entry['residual_size'] = size(1, 1, 1, 1, 'rev(<1,2>,b) pending; b free. The given ground sequence has no unknowns and is a value.')
        else:
            extra = 1 if cfg == 'stdlib-concurrency' and k == 3 else 0
            entry['residual_size'] = size(1 + extra, 4 + 2*extra, 2 + (k == 3), 6 + (2 if k == 3 else 0),
                                         'Pending rev(a,b), plus x=y only when the tuple-place evaluator has not aliased them. a=<x,y,z> is a held solved binding. At extended stage 3 substitute x=y into the binding and the pending application.')
        entry['residual_equivalence'] = ('Equivalent under the open reading: the observed bindings and held equality (if any) give exactly the stated equations; the live rev application is awaiting its missing definition and imposes no further current binding.' if reading == 'open' else 'Equivalent under the closed reading: the held application rev has no cases, so its conjunction with the equations denotes the empty set. The program has not detected/reported that inconsistency; it operationally uses an open wait, recorded separately from semantic equivalence.')
        o['undefined_relation_state'] = 4
        o['normalized_conditions'] = ('b free; rev(<1,2>,b) pending' if inst == 'P08c' else ('a=<y,y,z>; x=y; b free; rev(a,b) pending' if cfg == 'extended' and k == 3 else 'a=<x,y,z>; b free; rev(a,b) pending' + ('; x=y held' if k == 3 else '')))
        return entry

    if inst in ['P08a', 'P08b'] and k == 1:
        entry.update(semantic='complete', representation='solved form', residual_equivalence='Equivalent: a=<x,y,z>; all other query unknowns are free. No relation remains to decide.')
        return entry

    if inst == 'P08c' and k >= 3:
        entry.update(semantic='complete' if reading == 'closed' and k == 3 else 'unsound', representation='explicit',
                     residual_equivalence=('Equivalent empty solution set: the only arrived rev fact has an empty first argument, which cannot match <1,2>.' if reading == 'closed' and k == 3 else 'Not equivalent: an explicit no-solution conclusion is retained. The open reading at stage 3 leaves b free and the application pending; at stage 4 both readings require b=<2,1>.'))
        o['undefined_relation_state'] = 1
        o['partial_definition'] = 'The first rev case wakes the application, which fails and is removed from waiting work. Adding the recursive case never reposes it. Stage 4 retains the prior no-solution conclusion; no withdrawal is shown.'
        o['answer_completeness'] = {'empty_set_reported': True, 'valid_expected': 1 if k == 4 else 'all values for b (open) / empty (closed)', 'valid_obtained': 0}
        return entry

    if cfg == 'extended':
        entry.update(semantic='complete', representation='explicit' if k == 6 else 'solved form')
        normal = {4: 'x=y=u, z=v, a=<u,u,v>, b=<v,u,u>, c free',
                  5: 'x=y=z=u, a=b=<u,u,u>, c free',
                  6: 'x=y=z=42, a=b=<42,42,42>, c=<42,42>'}[k]
        entry['residual_equivalence'] = 'Equivalent, by symbolic substitution through the two rev cases and the two conc cases: ' + normal + '. Fresh Var objects are distinguished by identity, not by .name. The printed name h is reused by distinct fresh variables; it does not imply that all printed h occurrences denote one unknown.'
        o['normalized_conditions'] = normal
        o['output_name_collision'] = 'At stage 4 the printed h for z is a different Var identity from the h for x=y. Source inspection establishes this despite identical repr strings. Class the valid held bindings per SPECIFICATION reported/multiple forms, and retain the ambiguous printed answer verbatim.'
        o['definition_arrival'] = 'At stage 4 actual case functions are installed, defined Vars are bound, and q.run resumes the held application without reposing.' if k == 4 else None
        o['alternatives_note'] = '11 registered iterator/mark entries, held for depth-first continuation. These are mechanism choice points, not 11 distinct valid problem outcomes. The first answer is retained; further search is never requested.'
        return entry

    assert cfg == 'stdlib-concurrency' and inst == 'P08a'
    if k in [4, 5]:
        entry.update(semantic='complete', representation='residual', simplification='reducible', identical_to_posed=False,
                     residual_size=size(k-3, 2*(k-3), 3 + (k == 5), 8 + (2 if k == 5 else 0),
                                        'Residual x=y' + (' and y=z' if k == 5 else '') + '; solved bindings a=<x,y,z>, b=<z,y,x>. Full rev/conc definitions are vocabulary. Input consists of the sequence equation, rev, x=y, and y=z when present.'),
                     residual_equivalence='Equivalent: the held equalities, together with a=<x,y,z> and b=<z,y,x>, give exactly the valid outcomes. The equalities can be eliminated by aliasing, so the residual is reducible.')
        o['normalized_conditions'] = 'a=<x,y,z>; b=<z,y,x>; x=y' + ('; y=z' if k == 5 else '')
        o['definition_arrival'] = 'The def statements execute at stage 4; arrived("rev") wakes the same waiting relation thread. No reposing.' if k == 4 else None
    else:
        assert k == 6
        entry.update(semantic='unsound', representation='solved form',
                     residual_equivalence='Not equivalent: x=y=z=42 and a=b=<42,42,42> are obtained, but c is free. The required c=<42,42> is neither bound nor retained as a relation. For example c=<> is admitted by the reported state and violates the stage-6 equation.')
        o['lost_equation'] = 'prefix receives place(c)=None and returns the replacement equality (None, (y,x)); hold ignores the None place and discharges that equality without binding c. All waiting work is then empty. This is loss of a constraint, not partial enumeration of valid answers.'
        o['normalized_conditions'] = 'x=y=z=42; a=b=<42,42,42>; c free'
    return entry

def normalized_mode_signature(j):
    values = []
    for s in j['stages']:
        a = s['attempts'][-1]
        values.append((s['stage'], a['notes'], a['print'], re.sub(r'0x[0-9a-f]+', '<address>', a['observe']['raw']),
                       [(c['execution_state'], c['alternatives']['at_boundary'], c['suspended']['at_boundary']) for c in a['computations']]))
    return values

def complete_observations(e):
    """Answer-completeness observations, distinct from semantic class."""
    o = e['observations']
    if not e['reached']:
        o['answer_completeness'] = None
        return
    inst, k, reading = e['instance'], e['stage'], e['reading']
    expected_empty = reading == 'closed' and ((inst in ['P08a','P08b'] and k in [2,3]) or (inst=='P08c' and k in [2,3]))
    if expected_empty:
        o['answer_completeness'] = {'valid_outcomes': 'empty', 'empty_set_explicitly_reported': o['print_verbatim'].startswith('no solution:'),
                                    'equivalent_residual': e['semantic']=='complete' and e['representation']=='residual'}
    elif inst=='P08c' and k==1:
        o['answer_completeness'] = {'valid_outcomes': 'one empty substitution, no query unknown introduced', 'valid_obtained':1, 'invalid_obtained':0, 'reported_by':'empty observed environment'}
    elif (inst=='P08a' and k==6) or (inst=='P08c' and k==4):
        o['answer_completeness'] = {'valid_expected':1, 'valid_obtained':int(e['semantic']=='complete'),
                                    'invalid_report': None if e['semantic']=='complete' else ('no-solutions assertion' if inst=='P08c' else 'solved template leaves c free and therefore admits invalid completions')}
    else:
        o['answer_completeness'] = {'valid_outcomes':'infinite', 'finite_equivalent_representation':e['semantic']=='complete',
                                    'enumeration':'symbolic representation; no ground enumeration requested or performed'}

def main():
    data = {'tokens': {}, 'outcomes': [], 'mode_differences': [], 'expressibility': [], 'late_definition': [], 's_mechanisms': []}
    totals = collections.Counter()
    token_rows = {}
    for cfg in CONFIGS:
        for program in PROGRAMS:
            key = cfg + '/' + program
            spans, mechs, rows = token_classes(cfg, program)
            data['tokens'][key] = spans
            token_rows[key] = rows
            for s in spans:
                totals[s['class']] += s['to'] - s['from'] + 1
            for name, ranges in mechs.items():
                data['s_mechanisms'].append({'configuration': cfg, 'program': program, 'mechanism': name,
                    'listed_at_phase_4': name in ['backtracking search', 'suspension queue'],
                    'tokens': sum(b-a+1 for a,b in ranges), 'token_ranges': ranges,
                    'counting': 'Frozen program tokens. Shared implementation counted once per configuration; these per-program references/ranges are not additive mechanism implementations.'})
            if cfg == 'extended':
                for name, num, file in [('backtracking search',176,'search.py'),('suspension queue',537,'suspend.py')]:
                    record = next(x for x in data['s_mechanisms'] if x['configuration']==cfg and x['program']==program and x['mechanism']==name)
                    record.update(implementation_tokens=num, implementation='harnesses/python/S/'+file,
                                  phase_4_source='harnesses/python/S-mechanisms.md')
            def ranges_for(fragment):
                return [[x['from'],x['to']] for x in spans if fragment in x['construct']]
            if cfg == 'core':
                kind = 'neither'
                evidence = 'reverse calls rev(a) without a definition-availability guard; stage 2 raises NameError. Stages after 2 are not reached, including the stages containing the actual def statements. The registered held-list item is not a continuation awaiting code.'
            else:
                kind = 'code awaited'
                evidence = ('The relation wrapper exists early but its cases table is empty; Application waits on defined[name]. Actual conc/rev case functions are defined and appended at their information stages. This awaits relation code, rather than permission for an already-installed relation definition.' if cfg == 'extended' else 'reverse checks defined["rev"]; the actual rev/conc def statements execute only at their definition stages. arrived records that arrival and wakes the waiting thread. The flag tracks missing code, rather than granting permission to code already defined.')
                evidence += ' P08b leaves the application visibly suspended. P08c wakes on case 1, fails, and cannot recover when case 2 arrives.'
            selected = []
            for x in spans:
                if any(v in x['construct'] for v in ['rev(', 'rev_', 'case', 'reverse', 'Application', 'arrived', 'q.bind', 'q.wait', 'defined', 'r = rev']):
                    selected.append({'from':x['from'],'to':x['to'],'construct':x['construct']})
            data['late_definition'].append({'configuration':cfg,'program':program,'kind':kind,'evidence':evidence,'constructs':selected})
            for reading in ['open','closed']:
                if cfg == 'extended':
                    exp = 'expressible'
                    why = 'The admitted extended configuration supplies search and logic variables, and the supplied additional S application layer permits staged case definitions. Both relations are stated by their original cases in their original order. Operational premature failure in P08c is reported separately from the expressibility of the definitions. This capability is credited to the named S mechanisms, not Python core.'
                else:
                    exp = 'not expressible'
                    why = 'The full staged symbolic problem, including retention and later resolution of undecided relations, uses a general EVALUATOR/name-place store and dispatcher supplied by the program (S under rules 12/19), rather than a transcription or meaning-preserving R-only program within the nominal configuration. The forward rev/conc case functions themselves are mode-faithful P under rule 3; that local transcription does not make the whole staged problem expressible without S.'
                    if cfg == 'stdlib-concurrency':
                        why += ' threading is an allowed external mechanism, but the relation/definition store and generic evaluator protocol built around it are additional S. Its effective mechanism configuration is extended with threading.'
                data['expressibility'].append({'configuration':cfg,'subproblem':program[:-3],'direction':None,'reading':reading,'expressibility':exp,'reason':why,
                                               'directions_covered':['rev: given sequence structure to reversed output','conc: forward within rev'] + (['prefix: given prefix and whole sequence to tail','equality: all known/unknown-place combinations'] if program=='P08a.py' else [])})

    records = load_records()
    behaviour = {(j['run']['configuration'],j['run']['instance'],j['run']['program']['path']):(p,j) for p,j in records if j['run']['mode']=='behaviour'}
    comparisons = []
    for path,j in records:
        if j['run']['mode']=='behaviour':
            for st in j['stages']:
                for reading in ['open','closed']:
                    entry = classify_stage(path,j,st,reading)
                    complete_observations(entry)
                    data['outcomes'].append(entry)
        else:
            bp,b = behaviour[j['run']['configuration'],j['run']['instance'],j['run']['program']['path']]
            same = normalized_mode_signature(j) == normalized_mode_signature(b)
            comparisons.append({'record':path,'behaviour':bp,'same':same})
            if not same:
                for st, bst in zip(j['stages'],b['stages']):
                    for reading in ['open','closed']:
                        m = classify_stage(path,j,st,reading); old=classify_stage(bp,b,bst,reading)
                        fields=['reached','semantic','representation','simplification','identical_to_posed','execution_state','residual_equivalence']
                        if any(m[k]!=old[k] for k in fields):
                            data['mode_differences'].append({'configuration':j['run']['configuration'],'instance':j['run']['instance'],'program':Path(j['run']['program']['path']).name,'mode':j['run']['mode'],'record':path,'stage':st['stage'],'reading':reading,'behaviour':{k:old[k] for k in fields},'this_mode':{k:m[k] for k in fields},'note':'Difference from the matching behaviour record.'})
    # Exact coverage, using frozen indices and the supplied distinct-text list.
    texts = (ROOT/'results/python/tokens/TEXTS-1B-P08.tsv').read_text().splitlines()[1:]
    expected = [x.split('\t')[0] for x in texts if x.strip()]
    assert set(data['tokens']) == set(expected)
    for key, spans in data['tokens'].items():
        indices = [i for s in spans for i in range(s['from'],s['to']+1)]
        assert indices == [r['index'] for r in token_rows[key]], key
        assert all(s['class'] in 'PCRSH' for s in spans)
    assert len(behaviour)==9 and len(records)==27
    assert len(data['outcomes'])==78
    assert all(x['same'] for x in comparisons)
    (OUT/'python.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (OUT/'checks.json').write_text(json.dumps({'token_totals':dict(totals),'texts':len(expected),'behaviour_runs':len(behaviour),'behaviour_stages':len(data['outcomes'])//2,'classified_reading_stages':len(data['outcomes']),'mode_comparisons':comparisons,'semantic_totals':dict(collections.Counter(x['semantic'] for x in data['outcomes'])),'representation_totals':dict(collections.Counter(str(x['representation']) for x in data['outcomes']))},indent=2)+'\n')
    print(json.dumps({'tokens':dict(totals),'outcomes':len(data['outcomes']),'mode_differences':len(data['mode_differences']),'semantics':dict(collections.Counter(x['semantic'] for x in data['outcomes']))}))

if __name__=='__main__':
    main()
