"""Read permitted P12 evidence, classify it, and validate the resulting JSON.

This script never executes Prolog or reads another classifier's output.
Token boundaries come exclusively from the frozen TSV files.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import re

SOURCE = Path('.')
OUTPUT = Path('results/swi-prolog/classes-1C/B/parts/swi-prolog-P12')
CONFIGURATIONS = ['constraints', 'coroutines', 'plain', 'session', 'tabling']


def read_json(path):
    return json.loads(path.read_text())


def frozen_tokens(key):
    path = SOURCE / 'results/swi-prolog/tokens' / (key + '.tokens.tsv')
    with path.open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert [int(row['index']) for row in rows] == list(range(len(rows)))
    return rows


def token_classes(key):
    rows = frozen_tokens(key)
    ts = [row['token'] for row in rows]
    spans = []

    def add(start, end, cls, construct, rule):
        assert start == (spans[-1]['to'] + 1 if spans else 0)
        assert start <= end
        spans.append(dict(from_=start, to=end, **{'class': cls},
                          construct=construct, rule=rule))
        spans[-1]['from'] = spans[-1].pop('from_')

    i = 0
    while ts[i] == 'accept_fact':
        end = ts.index('.', i)
        add(i, end, 'P', 'Closed-world accept fact for n=' + ts[i+2],
            'P definition; rules 1 and 3. The n field selects the problem instance, not an efficiency argument.')
        i = end + 1
    if ts[i] == ':-':
        end = ts.index('.', i)
        assert ts[i:end+1] == [':-', 'table', 'choice', '/', '2', '.']
        add(i, end, 'C', 'Table choice/2',
            'C tabling declaration; rule 1: operational strategy on the same finite least relation.')
        i = end + 1
    end = ts.index('.', i)
    assert ts[i:end+1] == ['choice', '(', '_', ',', '[', ']', ')', '.']
    add(i, end, 'P', 'choice case 1: empty sequence', 'P definition case; rules 1 and 3.')
    i = end + 1
    end = ts.index('.', i)
    assert ts[i:end+1] == ['choice', '(', 'N', ',', '[', 'E', '|', 'T', ']', ')', ':-',
                          'N', '>', '0', ',', '(', 'E', '=', 'l', ';', 'E', '=', 'r', ')',
                          ',', 'N1', 'is', 'N', '-', '1', ',', 'choice', '(', 'N1', ',', 'T', ')', '.']
    add(i, end, 'P', 'choice case 2, including guard, stated l/r disjunction, decrement and recursion',
        'Rules 2, 3, 6 and 8: the guard belongs to the stated case, the two choices are stated, and n is known in every query. No move or extra algorithm.')
    i = end + 1
    end = ts.index('.', i)
    assert ts[i] == 'unknowns'
    add(i, end, 'H', 'unknowns(main, [S]) declaration',
        'Fixed harness contract, section 12: whole unknowns/2 fact is H.')
    i = end + 1
    end = ts.index(':-', i)
    assert ts[i] == 'stage'
    add(i, end, 'H', 'Stage 1 interface head and clause introducer',
        'Fixed harness contract, sections 2.1 and 12; rule 10: body goals are classified independently.')
    i = end + 1
    assert ts[i:i+6] == ['h_param', '(', 'n', ',', 'N', ')']
    add(i, i+5, 'H', 'Read instance size with h_param/2', 'Fixed harness call; harness contract section 12.')
    i += 6
    assert ts[i:i+7] == [',', 'choice', '(', 'N', ',', 'S', ')']
    add(i, i+6, 'P', 'Query choice(n, s), with preceding conjunction separator',
        'P query in stated order; rules 1 and 20.')
    i += 7
    assert ts[i:i+2] == [',', 'h_candidate']
    add(i, i+1, 'H', 'Count this accept evaluation, with preceding separator',
        'Fixed h_candidate/0 measurement call (harness section 12); rule 20.')
    i += 2
    assert ts[i:i+12] == [',', 'member', '(', 'accept_fact', '(', 'N', ',', 'S', ')', ',', 'Cs', ')']
    add(i, i+11, 'P', 'Query accept(s) by membership among this instance\'s closed-world facts',
        'Rules 1, 3, 9 and 20: equivalent finite fact lookup. member/2 is an external library call, not S.')
    i += 12
    assert ts[i] == '.'
    add(i, i, 'H', 'Terminator of the stage interface clause',
        'Construct punctuation of the H stage clause shell; rule 10 and harness section 12. This is not a separator between goals under rule 20.')
    i += 1
    assert ts[i:] == ['query', '(', '_', ',', '_', ')', '.']
    add(i, len(ts)-1, 'H', 'Trivial query/2 harness interface fact', 'Fixed harness interface; section 12.')
    assert [j for s in spans for j in range(s['from'], s['to']+1)] == list(range(len(ts)))
    return spans


def answer_value(text):
    match = re.fullmatch(r'\s*S\s*=\s*\[([lr,\s]*)\]\s*\.?\s*', text)
    assert match, repr(text)
    result = tuple(x.strip() for x in match.group(1).split(',') if x.strip())
    assert all(x in ('l', 'r') for x in result)
    return result


def valid_values(subproblem, n):
    return {
        'P12a': {('r',), ('l',)*n},
        'P12b': {('r',)},
        'P12c': {('r',)*n},
        'P12d': {('l',)*n},
    }[subproblem]


def classify(record, path):
    run = record['run']
    assert len(record['stages']) == 1
    stage = record['stages'][0]
    assert stage['stage'] == 1 and len(stage['attempts']) == 1
    attempt = stage['attempts'][0]
    assert attempt['posed']['how'] == 'fresh' and not attempt['posed']['replayed']
    assert len(attempt['computations']) == 1
    comp = attempt['computations'][0]
    assert comp['id'] == 'main' and len(comp['queries']) == 1
    query = comp['queries'][0]
    n = run['parameters']['n']
    values = [answer_value(a['verbatim']) for a in query['answers']]
    valid = valid_values(run['subproblem'], n)
    assert values and len(set(values)) == len(values)
    assert set(values) <= valid
    if run['parameters']['answers'] == 'all':
        assert set(values) == valid and query['ended_by'] == 'exhausted'
        expected_order = [('l',)*n, ('r',)] if run['subproblem'] == 'P12a' else list(valid)
        assert values == expected_order
    else:
        assert len(values) == 1
        if run['subproblem'] == 'P12a':
            assert values == [('l',)*n]
    states = comp['execution_state']['states']
    assert states in [['finished'], ['alternatives pending']]
    assert (states == ['finished']) == (query['ended_by'] == 'exhausted')
    assert comp['suspended']['at_boundary'] == 0
    assert not attempt['manual_actions'] and not record['manual_actions']
    assert not attempt['safety_limit']['hit'] and not comp['steps']['budget_exhausted']
    assert not record['harness_faults'] and '.INVALID.' not in path.name
    assert not attempt['stdout'] and not attempt['stderr']
    assert run['complete'] and run['constants']['variant'] is None
    assert run['program']['sha256'] == hashlib.sha256((SOURCE/run['program']['path']).read_bytes()).hexdigest()
    expected_candidates = (2**(n+1)-1 if run['parameters']['answers'] == 'all'
                           or run['subproblem'] == 'P12c' else
                           2**n+1 if run['subproblem'] == 'P12b' else n+1)
    assert comp['candidates_examined'] == expected_candidates
    return dict(reached=True, semantic='complete', representation='explicit',
                simplification=None, identical_to_posed=None, residual_size=None,
                execution_state=states, residual_equivalence=None), attempt, comp, query, values


def main():
    manifest_path = SOURCE/'results/swi-prolog/tokens/TEXTS-1C-P12.tsv'
    with manifest_path.open() as f:
        manifest = list(csv.reader(f, delimiter='\t'))[1:]
    tokens = {}
    aliases = {}
    for row in manifest:
        key = row[0]
        tokens[key] = token_classes(key)
        aliases[key] = [key] + (row[1].split() if len(row) > 1 else [])
        for other in aliases[key]:
            assert (SOURCE/'programs/swi-prolog'/key).read_bytes() == (SOURCE/'programs/swi-prolog'/other).read_bytes()
            assert [r['token'] for r in frozen_tokens(key)] == [r['token'] for r in frozen_tokens(other)]
    assert len(tokens) == 8

    data = {}
    records = []
    for config in CONFIGURATIONS:
        for folder in ['raw', 'raw-rerun-m2']:
            for path in sorted((SOURCE/f'results/swi-prolog/{config}/P12/{folder}').glob('*.json*')):
                assert path.suffix == '.json', 'Unexpected compression requires gzip reader'
                record = read_json(path)
                run = record['run']
                assert run['configuration'] == config and run['problem'] == 'P12'
                result, attempt, comp, query, values = classify(record, path)
                key = (config, run['instance'], Path(run['program']['path']).name, run['mode'])
                assert key not in data
                item = (record, path.relative_to(SOURCE).as_posix(), result, attempt, comp, query, values)
                data[key] = item
                records.append(item)
    assert len(records) == 360
    # Every line of each batch-1C P12 job log corresponds to exactly one record.
    log_keys = []
    for config in CONFIGURATIONS:
        path = SOURCE/f'results/swi-prolog/logs/1C-{config}-P12.tsv'
        for line in path.read_text().splitlines():
            _, c, instance, program, mode, status, _ = line.split('\t')
            assert c == config and status == 'exit 0'
            log_keys.append((c, instance, program, mode))
    assert Counter(log_keys) == Counter(data.keys())

    outcomes = []
    differences = []
    for key in sorted(data):
        config, instance, program, mode = key
        if mode != 'behaviour':
            continue
        record, path, result, attempt, comp, query, values = data[key]
        run = record['run']
        n = run['parameters']['n']
        measurements = {}
        for other_mode in ['cost', 'storage']:
            other = data[(config, instance, program, other_mode)]
            if other[2] != result:
                differences.append(dict(configuration=config, instance=instance, program=program,
                                        mode=other_mode, record=other[1], stage=1,
                                        behaviour=result, this_mode=other[2], note='Classification differs from behaviour.'))
            assert other[6] == values
            assert other[5]['ended_by'] == query['ended_by']
            assert other[4]['candidates_examined'] == comp['candidates_examined']
            measurements[other_mode] = other
        cost = measurements['cost']
        storage = measurements['storage']
        acceptable = valid_values(run['subproblem'], n)
        evidence = ('All reported lists match exactly the closed-world accept set at this n; '
                    'each has only l/r atoms and length at most n, so satisfies choice.'
                    if run['parameters']['answers'] == 'all' else
                    'The one reported list is in the closed-world accept set, uses only l/r atoms, '
                    'and has length at most n. The any-one query is complete with one valid answer '
                    '(SPECIFICATION.md, Outcomes 1).')
        observations = dict(
            answers_verbatim=[a['verbatim'] for a in query['answers']],
            answer_order=[list(v) for v in values],
            valid_outcomes=[list(v) for v in sorted(acceptable)],
            answer_completeness=dict(valid_obtained=len(values), valid_expected=len(acceptable),
                                     invalid_obtained=0, requirement=run['parameters']['answers']),
            semantic_check=evidence + ' Verified by check_classification.py against the P12 table, independently of program output.',
            unknowns='S is a ground finite Prolog list in every answer; no unknown remains in an answer.',
            observe_raw=attempt['observe']['raw'],
            observe_note=('After exhausted backtracking the held bindings may be empty; the collected answers remain reported.'
                          if not attempt['observe']['raw'] else 'The last answer is still held and is readable by observe().'),
            ended_by=query['ended_by'],
            execution_basis=comp['execution_state']['basis'],
            alternatives=comp['alternatives'],
            alternatives_note=('Retained choicepoints are for backtracking, not simultaneously live solution branches. '
                               'Behaviour-mode null counts are unavailable; storage counts follow below. '
                               'A pending choicepoint can produce only failure; pending does not imply another valid answer.'),
            suspended=comp['suspended'],
            suspended_note='No attributed variable or waiting engine is held; suspended-work boundary count is 0. An unavailable peak is null.',
            conclusions_withdrawn=[], manual_actions=[],
            candidates_examined=comp['candidates_examined'],
            candidates_before_each_answer_measured=None,
            candidates_note=('h_candidate counts accept evaluations and the record provides the final total only, '
                             'not an at-each-answer count. For the stated depth-first order the reference ranks '
                             'are n+1 for l^n, 2^n+1 for [r], and 2^(n+1)-1 for r^n; these are not per-answer measurements.'),
            partial_sequences_held=None,
            partial_sequences_note='No h_held count is supplied; problem-defined partial-sequence counts are unavailable and are not inferred from choicepoints.',
            cost_measurements=dict(record=cost[1], steps=cost[4]['steps'],
                                   answer_steps=[a['steps_at'] for a in cost[5]['answers']]),
            storage_measurements=dict(record=storage[1], alternatives=storage[4]['alternatives'],
                                      alternatives_at_answers=[a['alternatives_at'] for a in storage[5]['answers']],
                                      store=storage[3]['store']),
            measurement_note=('Null measurements are unavailable, never zero (AMENDMENTS.md 3.1). '
                              'Heartbeat maxima are sampled with their recorded interval and GC setting; '
                              'tabling has no in-stage sampling (AMENDMENTS.md 2). A true stack/choicepoint peak is unavailable.'),
            external_mechanisms=(['library(lists): member/2', 'table/1 (SLG tabling)'] if config == 'tabling'
                                 else ['library(lists): member/2', 'session engines used by the fixed harness'] if config == 'session'
                                 else ['library(lists): member/2']),
        )
        outcomes.append(dict(configuration=config, instance=instance, program=program, record=path,
                             stage=1, **result, observations=observations, harness_fault=False,
                             rule='SPECIFICATION.md Outcomes 1-3; P12 Queries and valid-outcome table; AMENDMENTS.md 3.1-3.2. Explicit lists need no residual simplification or equivalence field.'))

    expressibility = []
    support = []
    for config in CONFIGURATIONS:
        for letter in 'abcd':
            subproblem = 'P12' + letter
            expressibility.append(dict(configuration=config, subproblem=subproblem, direction=None,
                expressibility='expressible',
                reason='The two choice clauses transcribe both stated cases, guard and l-before-r disjunction; '
                       'n is known, so N1 is N-1 is mode-faithful (rules 3 and 8). '
                       'member/2 exactly matches the given closed-world accept facts (rule 9). '
                       'The query keeps choice before accept. All sizes and both answer modes use this transcription; '
                       'there are no R tokens, moves, omissions or imposed domains.' +
                       (' The table directive is C and changes evaluation, not the relation.' if config == 'tabling' else '')))
            support.append(dict(configuration=config, program=subproblem+'.pl', mechanism=None,
                                listed_at_phase_4=None, tokens=0, token_spans=[],
                                note='No supporting mechanism is used by this program.' +
                                (' The phase-4 wait-for-undefined-procedure layer is preloaded in session, '
                                 'but P12 makes no undefined application and does not invoke that layer. '
                                 'Engine calls belong to the fixed harness; no S tokens are added to this text.'
                                 if config == 'session' else ' member/2 is an external library call, not S.')))
    output = dict(tokens=tokens, outcomes=outcomes, mode_differences=differences,
                  expressibility=expressibility, late_definition=[], s_mechanisms=support)
    assert len(outcomes) == 120 and len(expressibility) == 20 and not differences
    (OUTPUT/'swi-prolog.json').write_text(json.dumps(output, indent=2, ensure_ascii=False)+'\n')
    # Validate serialized output rather than just the in-memory structures.
    saved = read_json(OUTPUT/'swi-prolog.json')
    totals = Counter({c: 0 for c in 'PCRSH'})
    per_text = {}
    expanded = Counter({c: 0 for c in 'PCRSH'})
    for key, spans in saved['tokens'].items():
        count = len(frozen_tokens(key))
        coverage = [0]*count
        local = Counter({c: 0 for c in 'PCRSH'})
        for span in spans:
            assert span['class'] in 'PCRSH' and 0 <= span['from'] <= span['to'] < count
            for i in range(span['from'], span['to']+1):
                coverage[i] += 1
            local[span['class']] += span['to']-span['from']+1
        assert coverage == [1]*count
        totals.update(local)
        per_text[key] = dict(local)
        for _ in aliases[key]:
            expanded.update(local)
    report = dict(distinct_texts=len(tokens), physical_programs=sum(map(len, aliases.values())),
                  tokens_distinct=dict(totals), tokens_expanded=dict(expanded), per_text=per_text,
                  records_checked=len(records), behaviour_stages=len(outcomes),
                  measured_comparisons=240, mode_differences=len(differences),
                  execution_states=dict(Counter(', '.join(o['execution_state']) for o in outcomes)),
                  aliases=aliases)
    (OUTPUT/'validation-summary.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
