"""Read-only evidence checks and independent validation of classifier output.

No study program, harness, or system code is executed or imported.
"""
from pathlib import Path
import ast
import collections
import csv
import gzip
import hashlib
import json

ROOT = Path('/Users/christopherhay/cp-roles/classifier-1C-B')
OUT = Path(__file__).resolve().parent
result = json.loads((OUT / 'python.json').read_text())
assert set(result) == {'tokens', 'outcomes', 'mode_differences', 'expressibility', 'late_definition', 's_mechanisms'}
with (ROOT / 'results/python/tokens/TEXTS-1C-P11-P12.tsv').open() as f:
    texts = list(csv.DictReader(f, delimiter='\t'))
assert set(result['tokens']) == {row['text'] for row in texts}
token_totals = collections.Counter()
span_count = 0
for row in texts:
    key = row['text']
    with (ROOT / 'results/python/tokens' / (key + '.tokens.tsv')).open() as f:
        frozen = list(csv.DictReader(f, delimiter='\t'))
    expected = {int(r['index']) for r in frozen}
    coverage = collections.Counter()
    previous = -1
    for s in result['tokens'][key]:
        assert s['class'] in 'PCRSH'
        assert isinstance(s['from'], int) and isinstance(s['to'], int)
        assert 0 <= s['from'] <= s['to'] < len(frozen)
        assert s['from'] == previous + 1
        assert s['construct'] and s['rule']
        coverage.update(range(s['from'], s['to'] + 1))
        token_totals[s['class']] += s['to'] - s['from'] + 1
        previous = s['to']
        span_count += 1
    assert set(coverage) == expected and set(coverage.values()) == {1}
    for duplicate in filter(None, row['also the text of'].split(',')):
        duplicate = duplicate.strip()
        assert (ROOT / 'programs/python' / key).read_bytes() == (ROOT / 'programs/python' / duplicate).read_bytes()
        assert (ROOT / 'results/python/tokens' / (key + '.tokens.tsv')).read_bytes() == (ROOT / 'results/python/tokens' / (duplicate + '.tokens.tsv')).read_bytes()


def load(p):
    with gzip.open(p, 'rt') if p.suffix == '.gz' else p.open() as f:
        return json.load(f)


records = {}
for conf in ('core', 'stdlib-concurrency', 'extended'):
    for problem in ('P11', 'P12'):
        for dr in ('raw', 'raw-rerun-m2'):
            for p in (ROOT / 'results/python' / conf / problem / dr).glob('*.json*'):
                if p.name.endswith('.jsonl'):
                    continue
                r = load(p)
                records[p.relative_to(ROOT).as_posix()] = r
                pr = r['run']['program']
                assert hashlib.sha256((ROOT / pr['path']).read_bytes()).hexdigest() == pr['sha256']

logged = []
for conf in ('core', 'stdlib-concurrency', 'extended'):
    for problem in ('P11', 'P12'):
        for line in (ROOT / f'results/python/logs/1C-{conf}-{problem}.tsv').read_text().splitlines():
            fields = line.split('\t')
            assert fields[5] == 'exit 0'
            logged.append(tuple(fields[1:5]))
assert collections.Counter(logged) == collections.Counter(
    (r['run']['configuration'], r['run']['instance'], Path(r['run']['program']['path']).name, r['run']['mode'])
    for r in records.values())

expected_stages = {(path, s['stage']) for path, r in records.items() if r['run']['mode'] == 'behaviour' for s in r['stages']}
seen_stages = [(e['record'], e['stage']) for e in result['outcomes']]
assert set(seen_stages) == expected_stages
assert len(seen_stages) == len(set(seen_stages))


def from_answer(text):
    assert text.startswith('s = ⟨') and text.endswith('⟩')
    return tuple(v.strip().removeprefix("'") for v in text[5:-1].split(',') if v.strip())


def valid(sub, n):
    if sub == 'P12a':
        return {('r',), ('l',) * n}
    if sub == 'P12b':
        return {('r',)}
    if sub == 'P12c':
        return {('r',) * n}
    return {('l',) * n}


budget_witnesses = []
comparison_count = 0
for e in result['outcomes']:
    r = records[e['record']]
    run = r['run']
    a = next(s['attempts'][-1] for s in r['stages'] if s['stage'] == e['stage'])
    c = a['computations'][0]
    answers = [x['verbatim'] for q in c['queries'] for x in q['answers']]
    assert e['reached'] and not e['harness_fault']
    assert e['execution_state'] == c['execution_state']['states']
    assert e['observations']['answers_verbatim'] == answers
    assert e['simplification'] is None and e['identical_to_posed'] is None and e['residual_size'] is None
    assert c['suspended']['at_boundary'] == 0
    assert not a['manual_actions'] and not r['manual_actions']
    if run['problem'] == 'P12':
        outcomes = valid(run['subproblem'], run['parameters']['n'])
        got = {from_answer(text) for text in answers}
        assert got <= outcomes
        if 'budget' in e['execution_state']:
            text = a['observe']['bindings']['s']
            term = ast.parse(text, mode='eval').body
            prefix = []
            while isinstance(term, ast.Tuple) and len(term.elts) == 2:
                prefix.append(ast.literal_eval(term.elts[0]))
                term = term.elts[1]
            # Exhibit one concrete denotation of the observed binding. For an
            # unknown tail, choose the empty sequence. Every witness is invalid.
            witness = tuple(prefix)
            assert witness not in outcomes
            assert e['semantic'] == 'unsound'
            if isinstance(term, ast.Name):
                assert e['representation'] == 'solved form'
                assert e['residual_equivalence']['equivalent'] is False
                assert not any(v[:len(prefix)] == tuple(prefix) for v in outcomes)
            else:
                assert ast.literal_eval(term) == ()
                assert e['representation'] == 'explicit'
            budget_witnesses.append((run['instance'], witness))
        else:
            assert got and (run['parameters']['answers'] == 'any-one' or got == outcomes)
            assert e['semantic'] == 'complete'
    else:
        assert e['semantic'] == 'complete'
        sub = run['subproblem']
        if sub in ('P11a', 'P11b'):
            assert answers == ['x = 2']
        elif sub == 'P11c':
            assert answers == (['x = 1'] if e['stage'] == 1 else ['x = 2'])
        else:
            assert answers == ([] if e['stage'] == 3 else ['x = 1'])
            if e['stage'] == 3:
                assert a['print'].startswith('no solution:') and a['observe']['bindings'] == {}
        actual_log = [json.loads(l) for l in (ROOT / r['effects']['log_path']).read_text().splitlines()]
        assert actual_log == r['effects']['log_after_run']
        values = [x['entry'] for x in actual_log]
        assert values == (['2'] if sub == 'P11a' else ['1'] if sub == 'P11d' else ['1', '2'])
        assert e['effects']['final_classification'] == ('exact' if sub in ('P11a', 'P11d') else 'extra')
    assert len(e['observations']['measurement_runs']) == 2
    for m in e['observations']['measurement_runs']:
        mr = records[m['record']]
        ma = next(s['attempts'][-1] for s in mr['stages'] if s['stage'] == e['stage'])
        mc = ma['computations'][0]
        assert [x['verbatim'] for q in mc['queries'] for x in q['answers']] == answers
        assert ma['observe']['bindings'] == a['observe']['bindings']
        assert mc['execution_state']['states'] == c['execution_state']['states']
        assert ma['print'] == a['print']
        assert m['classifications_match']
        comparison_count += 1
assert result['mode_differences'] == []
assert result['late_definition'] == []
assert len(result['expressibility']) == 24
for key, spans in result['tokens'].items():
    if not key.startswith('extended/'):
        continue
    entries = [e for e in result['s_mechanisms'] if key == e['configuration'] + '/' + e['program'] and not e['listed_at_phase_4']]
    assert sum(e['tokens'] for e in entries) == sum(s['to'] - s['from'] + 1 for s in spans if s['class'] == 'S')
print('PASS: exact once-only coverage of', sum(token_totals.values()), 'frozen tokens in', len(texts), 'texts;', span_count, 'construct spans.')
print('PASS:', len(records), 'records match all scoped job-log entries;', len(seen_stages), 'behaviour stages and', comparison_count, 'measurement-stage comparisons.')
print('PASS: program hashes, P11 persistent effects logs, P12 valid answers, and', len(budget_witnesses), 'invalid observable-binding witnesses.')
print('Class totals:', dict(token_totals))
for instance, witness in budget_witnesses:
    print('Budget counterexample:', instance, ''.join(witness), '(unknown tail, if any, instantiated to empty)')
