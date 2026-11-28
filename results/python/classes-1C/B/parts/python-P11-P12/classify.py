"""Independent classifier B: reads only the brief's permitted inputs.

Uses the frozen token TSVs, never tokenize, and never imports/runs study code.
ASTs identify constructs and literal constants only. All writes stay beside this file.
"""
from pathlib import Path
import ast
import collections
import csv
import gzip
import hashlib
import json
import re

ROOT = Path('.')
OUT = Path(__file__).resolve().parent
CONFIGS = ('core', 'stdlib-concurrency', 'extended')
PROBLEMS = ('P11', 'P12')


def read_json(p):
    with gzip.open(p, 'rt') if p.suffix == '.gz' else p.open() as f:
        return json.load(f)


def token_rows(key):
    p = ROOT / 'results/python/tokens' / (key + '.tokens.tsv')
    with p.open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    return [(int(r['index']), int(r['line']), r['token']) for r in rows]


def role(c, name, rule):
    return c, name, rule


def classes_for(key):
    conf, file = key.split('/')
    ext = conf == 'extended'
    staged = file in ('P11c.py', 'P11d.py')
    p12 = file.startswith('P12')
    source = (ROOT / 'programs/python' / key).read_text()
    tree = ast.parse(source)
    line_roles = {}

    def classify(n, context):
        txt = ast.get_source_segment(source, n) or ''
        txt = txt.splitlines()[0]
        label = f'{context + ": " if context else ""}{txt} [line {n.lineno}]'
        if isinstance(n, ast.ImportFrom):
            return role('C', 'select supplied S mechanism: ' + txt, '12; search/suspension declarations are control')
        if isinstance(n, ast.FunctionDef):
            name = n.name
            if name in ('unify', 'children', 'done', 'either'):
                return role('S', 'general ' + ('unification' if name == 'unify' else 'goal-list resolution') + ': ' + name,
                            '12, 15, 19; reusable mechanism, not a problem relation')
            if name in ('show', 'report'):
                return role('H', 'output adapter: ' + name, '13; only renders/collects already computed results')
            if name in ('holds', 'satisfies', 'advance', 'add'):
                return role('R', 'problem-specific staged relation holding: ' + name, '19; holding specific to this staged problem')
            if name == 'next_solution':
                return role('C', 'request next search outcome', '1; explicit search directive')
            if name == 'commit':
                return role('P', 'explicit commit and x = selected value', 'P11 Rules and Commitment; 10')
            if name == 'cons':
                return role('P', 'sequence encoding conversion', '15; construction/decomposition of cons-cell encoding')
            return role('P', 'definition/query: ' + name, '2, 3, 6, 8, 10; mode-faithful cases and connectives')

        if context in ('unify', 'children', 'done', 'either', 'show', 'report', 'cons'):
            return None  # one function construct, all with the same role
        if isinstance(n, ast.While) and ':= cp.stage()' in txt:
            return role('H', 'fixed stage receive loop', '13; harnesses/python/README.md section 7.1')
        if isinstance(n, ast.If) and re.match(r'(?:if|elif) (?:s|st)\.k ==', txt):
            return role('H', label, '10, 13; fixed stage-number dispatch')
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call):
            call = n.value
            if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) and call.func.value.id == 'cp':
                if call.func.attr == 'emit':
                    return role('P', 'irreversible emit', 'P11 Rules: emit and commit are problem tokens; overrides harness H listing')
                return role('H', label, '13; fixed harness call/registration')
            if isinstance(call.func, ast.Name) and call.func.id in ('print', 'report'):
                return role('H', label, '13; output adapter')
        if context == 'holds':
            if isinstance(n, ast.Return):
                return role('P', label, '19; fully known relation evaluator, distinct from holding dispatch')
            return role('R', label, '19; dispatch on encoded held relation')
        if context in ('satisfies', 'advance', 'add'):
            # next() changes operational search progress, within R holding code.
            if isinstance(n, ast.Assign) and ('next(solutions' in txt or 'next_solution()' in txt):
                return role('C', label, '1, 10; advance existing search, nested within problem-specific holding')
            return role('R', label, '19; store, retest and update specific staged relations')
        if context == 'next_solution':
            if isinstance(n, ast.Return) and 'deref(x)' in txt:
                return role('P', label, '10, 15; read the problem unknown from its encoding after search has produced it')
            return role('C', label, '1; ask retained search for its next result')
        if context == 'commit':
            if '.clear()' in txt:
                return role('C', label, '1, 16; discard unchosen alternatives at explicit commitment')
            if isinstance(n, ast.Assign) and ('chosen' in txt):
                return role('R', label, '3; decode a rendered replay commitment by scanning facts')
            return role('P', label, 'P11 Commitment; select v and add x = v')
        if context in ('pick', 'choice', 'equal', 'different', 'at_least', 'emit', 'accept', 'conjunction'):
            rule = '2, 3, 6, 8, 10; problem cases, tests and conjunction in presentation order'
            if context == 'accept' and not ext:
                rule = '6, 7, 9; built-in membership implements the stated closed world of accept facts'
            return role('P', label, rule)

        if isinstance(n, ast.Assign):
            names = {x.id for t in n.targets for x in ast.walk(t) if isinstance(x, ast.Name)}
            if names == {'NIL'} and not p12:
                return role('S', 'general unification: unused empty-sequence prelude',
                            '12, 15; unused generic term-runtime declaration, not P11 vocabulary')
            if names & {'PICK_FACTS', 'AT_LEAST', 'DIFFERENT_FROM', 'ACCEPT_FACTS', 'facts', 'NIL'}:
                return role('P', label, '3, 6, 15; problem facts, stage information, sequence encoding')
            if names & {'binder', 'trail', 'stack'}:
                return role('C', label, '1, 12; configure supplied search and binding machinery')
            if names & {'known'}:
                return role('R' if staged else 'H', label,
                            '19; bindings used to retain/retest staged outcomes' if staged else '13; collect an already computed answer for observe()')
            if names & {'added'}:
                return role('R', label, '19; retained problem-specific staged relations')
            if names & {'solutions'}:
                return role('C', label, '1, 12; retained search and search directive')
            if names & {'x', 'seq'} and 'Var(' in txt:
                return role('P', label, '15; represent problem unknown')
            if names & {'n'}:
                return role('H', label, '13; fixed size parameter supplied by harness')
            if 'next(' in txt or 'next_solution(' in txt:
                return role('C', label, '1; request any-one result from retained enumeration')
            if names & {'answers', 'query'}:
                return role('P', label, '3; pose the problem conjunction in its stated order')
            if names & {'found'}:
                return role('H', label, '13; count/remember whether an answer was already computed, for output')
        if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) and n.target.id == 'found':
            return role('H', label, '13; output completeness sentinel, computes no solution')
        if isinstance(n, ast.If):
            if 'next(solutions' in txt or 'params["answers"]' in txt:
                return role('C', label, '1, 10; explicitly select or stop answer enumeration')
            if 'replay' in txt or 'found' in txt or (not staged and 'x is None' in txt):
                return role('H', label, '13; print only already computed outcomes, suppress replay output')
            if staged and 'v is not None' in txt:
                return role('R', label, '19; retain the known provisional staged outcome')
        if isinstance(n, (ast.For, ast.Break)):
            return role('C', label, '1, 10; enumerate/stop requested search results')
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call):
            fn = n.value.func
            if isinstance(fn, ast.Name) and fn.id == 'commit':
                return role('P', label, 'P11 Rules: explicit commit is P')
            if isinstance(fn, ast.Name) and fn.id == 'add':
                return role('R', label, '19; apply new information through problem-specific holding code')
        raise AssertionError((key, context, ast.dump(n), txt))

    def walk(n, context='', inherited=None):
        selected = classify(n, context)
        if selected is None:
            return
        for line in range(n.lineno, n.end_lineno + 1):
            line_roles[line] = selected
        if isinstance(n, ast.FunctionDef):
            if n.name in ('unify', 'children', 'done', 'either', 'show', 'report', 'cons'):
                return
            context = n.name
        for field in ('body', 'orelse', 'finalbody'):
            for child in getattr(n, field, []):
                if isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                    continue  # docstrings have no frozen tokens
                if isinstance(child, ast.stmt):
                    walk(child, context, selected)

    for n in tree.body:
        walk(n)
    rows = token_rows(key)
    assert [r[0] for r in rows] == list(range(len(rows)))
    classified = []
    suites = []
    previous = None
    for i, line, token in rows:
        if token == '<INDENT>':
            assert previous is not None
            suites.append(previous)
            selected = previous
        elif token == '<DEDENT>':
            selected = suites.pop()
        else:
            assert line in line_roles, (key, i, line, token)
            selected = line_roles[line]
            previous = selected
        classified.append(selected)
    assert not suites

    # The harness fixes access to supplied constants, parameters and replay data
    # as H. Use frozen token text to identify those nested constructs. No lexing.
    i = 0
    while i < len(rows) - 2:
        tok = [r[2] for r in rows[i:i+3]]
        if tok[0] in ('s', 'st', 'cp') and tok[1] == '.' and tok[2] in ('constants', 'params', 'commitment', 'replay'):
            end = i + 3
            while end < len(rows) and rows[end][2] == '[':
                depth = 0
                while end < len(rows):
                    t = rows[end][2]
                    depth += (t == '[') - (t == ']')
                    end += 1
                    if depth == 0:
                        break
            tag = role('H', 'fixed harness input: ' + ''.join(r[2] for r in rows[i:end]),
                       '13; harnesses/python/README.md section 7.3; separator rule 20')
            start = i - 1 if i and rows[i-1][2] == ',' else i
            for j in range(start, end):
                classified[j] = tag
            i = end
        else:
            i += 1

    # Nested problem query inside the search directive: relation arguments P,
    # scheduling parameters and the search call itself C (rule 10).
    if ext:
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'search':
                ids = [i for i, line, token in rows if n.lineno <= line <= n.end_lineno]
                start = next(i for i in ids if rows[i][2] == 'search') + 2
                end = start
                if isinstance(n.args[0], ast.Tuple):
                    assert rows[start][2] == '('
                    depth = 0
                    while end < len(rows):
                        t = rows[end][2]
                        depth += (t == '(') - (t == ')')
                        end += 1
                        if depth == 0:
                            break
                else:
                    assert isinstance(n.args[0], ast.Name) and rows[start][2] == 'query'
                    end = start + 1
                for j in range(start, end):
                    classified[j] = role('P', 'problem conjunction passed as the search root', '3, 10; nested query distinct from the search directive')
    elif staged:
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'conjunction':
                ids = [i for i, line, token in rows if n.lineno <= line <= n.end_lineno]
                start = next(i for i in ids if rows[i][2] == 'conjunction')
                assert [rows[j][2] for j in range(start, start + 3)] == ['conjunction', '(', ')']
                for j in range(start, start + 3):
                    classified[j] = role('P', 'pose pick(x) and emit(x)', '3, 10; problem query nested in the retained-generator setup')

    spans = []
    for i, selected in enumerate(classified):
        c, construct, rule = selected
        if spans and all(spans[-1][k] == v for k, v in [('class', c), ('construct', construct), ('rule', rule)]):
            spans[-1]['to'] = i
        else:
            spans.append({'from': i, 'to': i, 'class': c, 'construct': construct, 'rule': rule})
    assert sum(s['to'] - s['from'] + 1 for s in spans) == len(rows)
    return spans


def records():
    result = []
    for conf in CONFIGS:
        for problem in PROBLEMS:
            for raw in ('raw', 'raw-rerun-m2'):
                for p in sorted((ROOT / 'results/python' / conf / problem / raw).glob('*.json*')):
                    if p.name.endswith('.jsonl'):
                        continue
                    r = read_json(p)
                    assert r['run']['configuration'] == conf
                    assert r['run']['problem'] == problem
                    result.append((p.relative_to(ROOT).as_posix(), r))
    return result


def answer_sequence(s):
    assert s.startswith('s = ⟨') and s.endswith('⟩'), s
    return tuple(x.strip().lstrip("'") for x in s[5:-1].split(',') if x.strip())


def cons_binding(text):
    """Decode a repr of cons cells; Name at a tail denotes an unbound Var."""
    n = ast.parse(text, mode='eval').body
    prefix = []
    while isinstance(n, ast.Tuple) and len(n.elts) == 2:
        prefix.append(ast.literal_eval(n.elts[0]))
        n = n.elts[1]
    if isinstance(n, ast.Name):
        return tuple(prefix), n.id
    assert ast.literal_eval(n) == ()
    return tuple(prefix), None


def valid_sequences(sub, n):
    return {'P12a': {('r',), ('l',) * n}, 'P12b': {('r',)},
            'P12c': {('r',) * n}, 'P12d': {('l',) * n}}[sub]


def stage_classification(path, r, stage):
    run = r['run']
    a = stage['attempts'][-1]
    assert len(a['computations']) == 1
    c = a['computations'][0]
    k = stage['stage']
    answers = [ans['verbatim'] for q in c['queries'] for ans in q['answers']]
    out = {'configuration': run['configuration'], 'instance': run['instance'],
           'program': Path(run['program']['path']).name, 'record': path,
           'stage': k, 'reached': True, 'semantic': None, 'representation': 'explicit',
           'simplification': None, 'identical_to_posed': None, 'residual_size': None,
           'execution_state': c['execution_state']['states'], 'residual_equivalence': None,
           'harness_fault': '.INVALID.' in path or bool(r['harness_faults']),
           'rule': 'SPECIFICATION.md Outcomes 1–3; valid outcomes of ' + run['subproblem']}
    assert not any('did not reach' in x.lower() or 'never posed' in x.lower() for x in a['notes']), a['notes']
    assert a['posed']['how'] in ('fresh', 'incremental'), a['posed']
    assert len(stage['attempts']) == 1
    sub = run['subproblem']
    binding = a['observe']['bindings']
    budget = 'budget' in out['execution_state']
    equivalence = None
    any_query = run['parameters'].get('answers') == 'any-one' or run['problem'] == 'P11'
    if sub.startswith('P12'):
        n = run['parameters']['n']
        valid = valid_sequences(sub, n)
        got = {answer_sequence(x) for x in answers}
        bad = got - valid
        speculative = None
        if budget and binding and binding.get('s') != 's':
            prefix, tail = cons_binding(binding['s'])
            speculative = {'prefix': prefix, 'tail_unknown': tail,
                           'valid': tail is None and prefix in valid}
            if not speculative['valid']:
                bad.add(prefix)
            if tail is not None:
                out['representation'] = 'solved form'
                equivalence = {'equivalent': False,
                               'reason': 'The observed cons term is a fixed prefix followed by the free tail ' + tail +
                               '. Its first element is l, whereas P12c admits only r repeated n times. It is not an equivalent solution form. The opaque pending iterators are unfinished search, not a reported residual condition.',
                               'counterexample': 'Set the free tail to (); the resulting l-prefixed sequence is invalid.'}
        if bad:
            out['semantic'] = 'unsound'
        elif got and (any_query or got == valid):
            out['semantic'] = 'complete'
        elif got:
            out['semantic'] = 'partial'
        else:
            out['semantic'] = 'none reported'
        reason = ('Closed-world accept gives exactly the listed valid sequences; each also satisfies choice because its length is at most n and every element is l or r. ')
        if speculative:
            reason += ('At budget, observe() also reads the speculative binding ' + binding['s'] +
                       '. It is reported by SPECIFICATION.md Outcomes 1, even though accept has not certified it. This invalid bound outcome makes the stage unsound. ')
            out['rule'] += '; observable bindings are reported even at budget; P09d1 exception does not apply'
        else:
            reason += 'All delivered answers are members of that set. '
        if any_query and got:
            reason += 'One valid delivered answer meets the any-one query.'
        elif got == valid:
            reason += 'Both/sole valid answers were delivered; search exhaustion and semantic completeness are separate.'
        elif got:
            reason += 'The delivered answers alone omit at least one valid sequence.'
        else:
            reason += 'No answer was delivered by cp.answer().'
        answer_completeness = {'valid_answers_delivered': len(got & valid), 'expected_all': len(valid),
                               'invalid_answers_delivered': len(got - valid), 'any_one': any_query,
                               'query_satisfied_by_delivered_answers': bool(got & valid) if any_query else got == valid,
                               'speculative_observed_binding': speculative,
                               'reason': reason}
        # A free Var after exhaustion is the restored search workspace, not a
        # binding: use the more explicit valid answers, per Outcomes 2.
        unknowns = ('Restored, unbound Var s after exhaustive trail undo; the valid explicit answers are retained in the answer record.'
                    if binding == {'s': 's'} else
                    'Unknown tail is an S.suspend.Var rendered as t; the other cons cells are bound.'
                    if budget and out['representation'] == 'solved form' else
                    'No unknown in the reported explicit answer(s); core registers no bindings.'
                    if not binding else 'The reported s is a finite cons-cell tuple of atom strings ending in ().')
        withdrawn = []
    else:
        valid = {2, 3} if sub in ('P11a', 'P11b') else ({1, 2, 3} if k == 1 else {2, 3} if sub == 'P11c' and k == 2 else {2} if sub == 'P11c' else {1} if k == 2 else set())
        got = {int(x.split(' = ')[1]) for x in answers}
        if not valid:
            assert not got and 'no solution:' in a['print'] and binding == {}
            out['semantic'] = 'complete'
        else:
            assert got and got <= valid
            out['semantic'] = 'complete'  # P11 is any-one, including provisional stages
        answer_completeness = {'valid_answers_delivered': len(got & valid), 'expected_all': len(valid),
                               'invalid_answers_delivered': len(got - valid), 'any_one': True,
                               'empty_reported': not valid and 'no solution:' in a['print'],
                               'reason': 'One valid outcome suffices for P11. ' +
                               ('Commit selects x = 2, so the last stage has that single solution.' if sub == 'P11c' and k == 3 else
                                'Commit selected x = 1; the subsequent x != 1 makes the solution set empty and the program explicitly reports no solution.' if sub == 'P11d' and k == 3 else
                                'The explicit reported x belongs to the outcomes admitted at this stage.')}
        unknowns = 'No remaining unknown in the selected explicit outcome; a dictionary holds known x.' if binding else 'Known x is removed after contradiction; no solved outcome remains.'
        withdrawn = ([{'conclusion': 'x = 1', 'how': 'known[x] replaced by 2; stage prints x = 2; emitted 1 remains irreversible'}]
                     if sub == 'P11c' and k == 2 else
                     [{'conclusion': 'x = 1', 'how': 'known[x] removed; prints no solution; committed effect 1 remains in L'}]
                     if sub == 'P11d' and k == 3 else [])
        final_log = [e['entry'] for e in r['effects']['log_after_run']]
        expected_log = ['2'] if sub != 'P11d' else ['1']
        final_class = 'exact' if final_log == expected_log else 'extra'
        assert final_log in (['2'], ['1', '2'], ['1'])
        final_stage = 3 if staged_subproblem(sub) else 1
        out['effects'] = {'classification': final_class if k == final_stage else None,
                          'judged_at_stage': final_stage, 'final_classification': final_class,
                          'log_at_boundary': [e['entry'] for e in r['effects']['log_after_run'] if e['stage'] <= k],
                          'final_log': final_log,
                          'committed_x': None if (sub == 'P11c' and k < 3 or sub == 'P11d' and k < 2) else int(expected_log[0]),
                          'entries_this_stage': [dict(e, timing='before commitment (provisional outcome)') for e in a['effects']],
                          'commitment': 'Reporting the one-stage answer commits it.' if final_stage == 1 else
                                        'Explicit commit selects the currently held outcome and adds x = v; alternatives are cleared.',
                          'reason': 'L exactly matches the committed outcome; P11d keeps that effect exact even when later information contradicts x = 1.' if final_class == 'exact' else
                                    'L includes 1, which was explored but never committed; 2 is committed. There are no replay duplicates.'}
    out['residual_equivalence'] = equivalence
    alt = c['alternatives']
    out['observations'] = {
        'answers_verbatim': answers, 'stdout_verbatim': a['stdout'], 'observe_verbatim': a['observe']['raw'],
        'bindings_verbatim': binding, 'unknowns': unknowns,
        'answer_completeness': answer_completeness,
        'alternatives': dict(alt, held_as='backtracking' if alt['at_boundary'] else 'none',
                             explanation='Lazy native generators retain untried facts/recursive cases.' if run['configuration'] != 'extended' else
                                         'Depth-first chronological search holds iterators and trail marks, not all solutions live.',
                             problem_defined_count='unavailable: no cp.problem_alternatives registration'),
        'suspended': c['suspended'],
        'suspension_explanation': '0 waiting-for-information items; paused search generators are alternatives, not suspension on unknown information.',
        'withdrawn_conclusions': withdrawn,
        'manual_actions': r['manual_actions'] + a['manual_actions'],
        'posing': a['posed'], 'steps': c['steps'],
        'problem_operations': c['problem_operations'],
        'candidates_examined': c.get('candidates_examined'),
        'store': a['store'],
        'measurement_note': 'Null measurements are unavailable, not zero. Behaviour has no store or relation-operation instrumentation; use the linked cost/storage records.',
        'harness_notes': a['notes'],
    }
    if run['problem'] == 'P12':
        n = run['parameters']['n']
        positions = {('l',) * n: n + 1, ('r',): 2**n + 1,
                     ('r',) * n: 2**(n + 1) - 1}
        out['observations']['p12_search'] = {
            'strategy': 'depth first, empty case first, l before r; accept follows choice',
            'answer_order': answers,
            'candidates_at_each_delivered_answer': [
                {'answer': text, 'candidate_number': positions[answer_sequence(text)]} for text in answers],
            'candidate_position_basis': 'Derived from the definition and the program cases, not an extra measurement or execution: l^n is n+1st, r is 2^n+1st, r^n is 2^(n+1)-1st.',
            'finite_space_candidates': 2**(n + 1) - 1,
            'search_finished': 'finished' in out['execution_state'],
            'all_query_finishes_after_last_answer': ('finished' in out['execution_state']) if run['parameters']['answers'] == 'all' else None,
            'peak_retained_alternatives': None,
            'peak_note': 'Unavailable: no alternative peak is recorded. Storage traced-allocation peaks are in the linked storage run, and are different quantities.'}
    return out


def staged_subproblem(sub):
    return sub in ('P11c', 'P11d')


def axes(entry):
    return {k: entry[k] for k in ('reached', 'semantic', 'representation', 'simplification',
                                 'identical_to_posed', 'residual_size', 'execution_state', 'residual_equivalence')}


def main():
    with (ROOT / 'results/python/tokens/TEXTS-1C-P11-P12.tsv').open() as f:
        manifest = list(csv.DictReader(f, delimiter='\t'))
    tokens = {}
    for row in manifest:
        key = row['text']
        tokens[key] = classes_for(key)
        for duplicate in filter(None, row['also the text of'].split(',')):
            duplicate = duplicate.strip()
            assert (ROOT / 'programs/python' / key).read_bytes() == (ROOT / 'programs/python' / duplicate).read_bytes()
            assert token_rows(key) == token_rows(duplicate)

    raw_records = records()
    by_key = {}
    for path, r in raw_records:
        run = r['run']
        key = run['configuration'], run['instance'], Path(run['program']['path']).name
        by_key.setdefault(key, {}).setdefault(run['mode'], []).append((path, r))
    outcomes = []
    differences = []
    compared = []
    for key, modes in sorted(by_key.items()):
        assert len(modes['behaviour']) == 1
        path, r = modes['behaviour'][0]
        entries = {s['stage']: stage_classification(path, r, s) for s in r['stages']}
        for entry in entries.values():
            entry['observations']['measurement_runs'] = []
        for mode in ('cost', 'storage'):
            for mpath, mr in modes[mode]:
                for s in mr['stages']:
                    me = stage_classification(mpath, mr, s)
                    be = entries[s['stage']]
                    compared.append((mpath, s['stage']))
                    if axes(be) != axes(me):
                        differences.append({'configuration': key[0], 'instance': key[1], 'program': key[2],
                                            'mode': mode, 'record': mpath, 'stage': s['stage'],
                                            'behaviour': axes(be), 'this_mode': axes(me),
                                            'note': 'A difference on a classified axis.'})
                    a = s['attempts'][-1]
                    c = a['computations'][0]
                    be['observations']['measurement_runs'].append({
                        'mode': mode, 'record': mpath, 'classifications_match': axes(be) == axes(me),
                        'steps': c['steps'], 'problem_operations': c['problem_operations'],
                        'candidates_examined': c.get('candidates_examined'),
                        'answer_measurements': c['queries'], 'alternatives': c['alternatives'],
                        'suspended': c['suspended'], 'store': a['store'], 'harness_faults': mr['harness_faults'],
                        'missing_measurements': 'null and absent fields are unavailable, not zero'})
        outcomes.extend(entries.values())

    expressibility = []
    for conf in CONFIGS:
        for sub in ('P11a', 'P11b', 'P11c', 'P11d', 'P12a', 'P12b', 'P12c', 'P12d'):
            staged = staged_subproblem(sub)
            reason = ('pick, comparison, and the effect in the stated order are mode-faithful transcriptions. Extra effects are an effects result, not a different answer relation.' if sub.startswith('P11') else
                      'The native generator transcribes both choice cases and the ordered l/r disjunction, followed by the closed-world accept test. Both all and any-one use this one direction (n known, s produced).')
            if staged:
                reason = ('The definition of pick is P, but retaining a provisional solution, a list of later relations and retesting/advancing the generator is problem-specific holding (R, rule 19). Commit adds x = v without changing the mathematical relation. This finite closed world requires no imposed domain.')
            if conf == 'extended':
                reason += (' The selected extended implementation additionally uses the supplied search and Var/binding layer plus program-supplied generic unification and resolution (S, listed separately). These are not native Python capabilities. Since extended includes core, the permitted core transcription/holding reformulation establishes this expressibility judgement; using optional S in the selected program does not prove that only supporting code can express the problem.')
            expressibility.append({'configuration': conf, 'subproblem': sub,
                                   'direction': 'n known -> s; all and any-one' if sub.startswith('P12') else 'x unknown -> a provisional/committed value',
                                   'expressibility': 'expressible with reformulation' if staged else 'expressible',
                                   'reason': reason})

    mechanisms = []
    for conf in CONFIGS:
        for file in ('P11a.py', 'P11b.py', 'P11c.py', 'P11d.py', 'P12a.py', 'P12b.py', 'P12c.py', 'P12d.py'):
            if conf != 'extended':
                continue
            for name, size, src, use in (
                ('backtracking search', 176, 'harnesses/python/S/search.py', 'search and undo; chronological depth-first search and trail'),
                ('suspension queue / variables and binding', 537, 'harnesses/python/S/suspend.py', 'Var, deref and Queue.bind only; no Queue.wait/run or waiting goals')):
                mechanisms.append({'configuration': conf, 'program': file, 'mechanism': name,
                                   'listed_at_phase_4': True, 'tokens': size, 'token_ranges': None,
                                   'source': src, 'use': use,
                                   'counting': 'Full phase-4 module size, counted once per configuration, not added anew per importing program. No frozen TSV for this module was supplied.'})
            spans = tokens[conf + '/' + file]
            for name, needle in [('unification without occurs check', 'general unification:'),
                                 ('goal-list resolution', 'general goal-list resolution:')]:
                selected = [s for s in spans if s['class'] == 'S' and s['construct'].startswith(needle)]
                assert selected
                mechanisms.append({'configuration': conf, 'program': file, 'mechanism': name,
                                   'listed_at_phase_4': False,
                                   'tokens': sum(s['to'] - s['from'] + 1 for s in selected),
                                   'token_ranges': [{'from': s['from'], 'to': s['to']} for s in selected],
                                   'source': 'programs/python/' + conf + '/' + file,
                                   'counting': 'Program-local S implementation. Repeated identical mechanism code is counted once per configuration; resolution in P12 additionally contains the generic either disjunction.'})
    result = {'tokens': tokens, 'outcomes': outcomes, 'mode_differences': differences,
              'expressibility': expressibility, 'late_definition': [], 's_mechanisms': mechanisms}
    (OUT / 'python.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    totals = collections.Counter()
    per_text = {}
    for key, spans in tokens.items():
        counts = collections.Counter()
        for s in spans:
            counts[s['class']] += s['to'] - s['from'] + 1
        totals.update(counts)
        per_text[key] = dict(counts)
    audit = {'distinct_texts': len(tokens), 'token_totals': dict(totals), 'per_text': per_text,
             'raw_records': len(raw_records), 'behaviour_records': len(by_key),
             'behaviour_stages': len(outcomes), 'measurement_stage_comparisons': len(compared),
             'mode_differences': len(differences),
             'semantic': dict(collections.Counter(e['semantic'] for e in outcomes)),
             'representation': dict(collections.Counter(e['representation'] for e in outcomes)),
             'execution': dict(collections.Counter(x for e in outcomes for x in e['execution_state'])),
             'final_effects': dict(collections.Counter(e['effects']['classification'] for e in outcomes if e.get('effects', {}).get('classification')))}
    (OUT / 'validation-summary.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
