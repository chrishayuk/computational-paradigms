"""Read permitted frozen tokens and P04 records; build and check this classifier's output.

This does not import or execute any study program, harness, or tokenizer.
"""
import collections
import csv
import hashlib
import json
import pathlib
import re

SOURCE = pathlib.Path('.')
OUT = pathlib.Path(__file__).resolve().parent
CONFIGS = ['constraints', 'coroutines', 'plain', 'session', 'tabling']
CLASSES = 'PCRSH'


def read_tokens(path):
    with (SOURCE / 'results/swi-prolog/tokens' / (path + '.tokens.tsv')).open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert [int(r['index']) for r in rows] == list(range(len(rows)))
    return rows


def span(start, end, cls, construct, rule):
    return {'from': start, 'to': end, 'class': cls, 'construct': construct, 'rule': rule}


def token_classes(path):
    rows = read_tokens(path)
    # Group the frozen indices by source line, without re-tokenizing the source.
    lines = collections.defaultdict(list)
    for r in rows:
        lines[r['line']].append(r)
    spans = []
    for line in lines.values():
        ts = [r['token'] for r in line]
        lo, hi = int(line[0]['index']), int(line[-1]['index'])
        if ts[:2] == [':-', 'table']:
            spans.append(span(lo, hi, 'C', 'Tabling declaration for the problem relation',
                              'METRICS class C; rules 1 and 12: changes resolution/termination, not the least relation; external mechanism table/1.'))
        elif ts[0] in ('alternative_value', 'alist_argument'):
            spans.append(span(lo, hi, 'P', 'Stage 1 input constant in the replaceable CONSTANTS block',
                              'METRICS class P: information of the stage; rules 3 and 15 for the finite-list transcription.'))
        elif ts[0] in ('loop', 'alist'):
            spans.append(span(lo, hi, 'P', 'Definition case: ' + ' '.join(ts),
                              'METRICS rules 1 and 3: literal transcription in the stated case/conjunct order; rule 15 for list construction/equality.'))
        elif ts[0] in ('unknowns', 'query'):
            spans.append(span(lo, hi, 'H', 'Harness ' + ts[0] + '/2 interface fact',
                              'harnesses/swi-prolog/README.md sections 2.1 and 12; METRICS class H.'))
        elif ts[0] == 'stage':
            body = ts.index(':-') + 1
            spans.append(span(lo, lo + body - 1, 'H', 'Harness stage/3 head and clause introducer',
                              'harnesses/swi-prolog/README.md section 12; METRICS rule 10: body constructs classed separately.'))
            if ts[body] == 'memberchk':
                # Every such call in these frozen texts is exactly these nine tokens.
                assert ts[body + 8] == ')'
                spans.append(span(lo + body, lo + body + 8, 'P', 'Read this stage\'s given constant from its input list (memberchk/2)',
                                  'METRICS rules 1 and 3: input transcription, no generated alternatives or changed algorithm; rule 12: external memberchk/2, not an H predicate.'))
                body += 9
            spans.append(span(lo + body, hi - 1, 'P', 'Ordered stage query (including its preceding conjunction separator, if any)',
                              'METRICS class P and rules 1, 3, 6, 10 and 20: stated query/connectives; no move or omission.'))
            spans.append(span(hi, hi, 'H', 'Terminator of the enclosing stage/3 interface clause',
                              'METRICS classing by construct and rule 10; enclosing interface clause is H, body goals are classed separately.'))
        else:
            raise AssertionError((path, ts))
    validate_spans(path, spans)
    return spans


def validate_spans(path, spans):
    rows = read_tokens(path)
    indices = []
    for s in spans:
        assert s['class'] in CLASSES and s['construct'] and s['rule']
        assert 0 <= s['from'] <= s['to'] < len(rows)
        indices.extend(range(s['from'], s['to'] + 1))
    assert indices == list(range(len(rows))), path


texts = {}
for r in csv.DictReader((SOURCE / 'results/swi-prolog/tokens/TEXTS-1B-P04.tsv').open(), delimiter='\t'):
    texts[r['text']] = r['also the text of'].split()
tokens = {p: token_classes(p) for p in texts}
for p, aliases in texts.items():
    for alias in aliases:
        assert [r['token'] for r in read_tokens(p)] == [r['token'] for r in read_tokens(alias)]
        assert (SOURCE / 'programs/swi-prolog' / p).read_bytes() == (SOURCE / 'programs/swi-prolog' / alias).read_bytes()
        validate_spans(alias, tokens[p])

records = []
for c in CONFIGS:
    for folder in ['raw', 'raw-rerun-m2']:
        for f in sorted((SOURCE / 'results/swi-prolog' / c / 'P04' / folder).glob('*.json')):
            d = json.loads(f.read_text())
            assert d['run']['problem'] == 'P04'
            assert d['run']['configuration'] == c
            assert len(d['stages']) == 1 and d['stages'][0]['stage'] == 1
            program_bytes = (SOURCE / d['run']['program']['path']).read_bytes()
            assert hashlib.sha256(program_bytes).hexdigest() == d['run']['program']['sha256']
            records.append((str(f.relative_to(SOURCE)), d))


def classify(record, d):
    run = d['run']
    instance = run['instance']
    stage = d['stages'][0]
    a = stage['attempts'][-1]
    m = a['computations'][0]
    assert len(a['computations']) == 1
    q = m['queries'][0]
    answers = [v['verbatim'] for v in q['answers']]
    fault = bool(d['harness_faults']) or 'INVALID' in record
    assert a['posed']['replayed'] == []  # Every P04 query is a single fresh stage.
    assert not d['manual_actions'] and not a['manual_actions']
    assert a['separate_run'] is None
    semantic = 'none reported'
    representation = None
    reason = 'No answer was delivered and observe() contains no binding or retained residual denoting an outcome. An empty answer stream at a resource stop is not a report of logical false.'
    if answers:
        representation = 'explicit'
        if instance in ('P04a', 'P04b'):
            assert [s.strip().rstrip('.').strip() for s in answers] == ['X = 1']
            semantic = 'complete'
            reason = 'The least relation defined only by loop(X) :- loop(X) is empty; the disjunction therefore denotes exactly X=1. The reported singleton is exactly that set, irrespective of subsequent search.'
        elif instance in ('P04c', 'P04e'):
            assert len(answers) == 1 and answers[0].strip() == 'true.'
            semantic = 'complete'
            reason = 'The ground finite list [a,a] satisfies alist. With no unknowns the valid solution set is the singleton empty substitution, reported as true.'
        elif instance in ('P04d', 'P04f'):
            lengths = []
            for answer in answers:
                match = re.fullmatch(r'S = \[(.*?)\]\s*\.?\s*', answer)
                assert match, answer
                entries = [] if not match.group(1) else match.group(1).split(', ')
                assert all(x == 'a' for x in entries)
                lengths.append(len(entries))
            assert lengths == list(range(20))
            semantic = 'partial'
            reason = 'The explicit answers are precisely the 20 lists a^n for 0<=n<=19, in increasing length. They form a nonempty proper subset of all finite a-lists; no finite residual representation of the whole infinite set was reported.'
    states = m['execution_state']['states']
    if states == ['timeout']:
        assert len(stage['attempts']) == 2
        assert [x['limit_s'] for x in stage['attempts']] == [60, 600]
    if not fault:
        assert states in (['budget'], ['finished'], ['alternatives pending'], ['timeout'])
    else:
        assert states == ['error'] and not m['execution_state']['determined']
    unknowns = {'P04a': 'X', 'P04b': 'X', 'P04c': None, 'P04d': 'S', 'P04e': None, 'P04f': 'S'}[instance]
    if unknowns is None:
        unknown_repr = 'No query unknowns (ground membership query).'
    elif answers and instance == 'P04f':
        unknown_repr = 'S is an ordinary Prolog logic variable, explicitly bound to a finite ground list in each answer; at the cap it is bound to the 19-element a-list.'
    elif answers:
        unknown_repr = 'X is an ordinary Prolog logic variable, bound to 1 in the answer. In the later non-tabled loop branch the binding is undone by backtracking; this is not a retraction of the already reported answer.'
        if states == ['finished']:
            unknown_repr = 'X is an ordinary Prolog logic variable, explicitly bound to integer 1 in the answer.'
    else:
        unknown_repr = unknowns + ' remains an ordinary unbound Prolog logic variable; no solved form or symbolic answer was reported.'
    obs_text = unknown_repr + ' '
    if not answers:
        obs_text += 'The raw observation "true " with no binding is an empty display of current bindings, not successful completion of the still-running query. '
    if states == ['budget']:
        obs_text += 'The inference budget stopped search; the exception aborts the computation, which cannot be resumed. Choicepoint counts are unavailable in behaviour/cost mode. '
    elif states == ['timeout']:
        obs_text += 'Both the 60-second attempt and its 600-second rerun timed out without answers. Tabled computation is still generating internal answers; their count is not a delivered query answer or a finite residual. No fair enumeration of query answers is established; local table completion on an infinite answer set prevents delivery in these runs. '
    elif states == ['alternatives pending']:
        obs_text += 'The cap is 20. Textual depth-first alist-right enumeration visits exactly one list of each successive length, so every finite a-list would be reached with continued requests and sufficient steps. The corresponding successful storage run holds one clause choicepoint at the boundary; alternatives are held for backtracking. '
    elif states == ['finished']:
        obs_text += 'No further alternatives or suspended goals remain; the successful storage run measures zero retained choicepoints. '
    if fault:
        obs_text += 'The record\'s error is a HARNESS FAULT placeholder for a missing end event (determined=false), not evidence of a Prolog program error. Malformed event fragments refer to inference_limit_exceeded/budget, but the complete computational termination state and boundary measurements are unavailable. '
    obs_text += 'There is only one problem stage, so no earlier-stage conclusion was withdrawn. No manual actions are recorded; the timeout rerun, where present, is automatic.'
    # Do not credit timeout placeholders or fault-associated zeros as measurements.
    suspended = m['suspended']['at_boundary'] if not fault and states != ['timeout'] else None
    obs = {
        'description': obs_text,
        'answers_verbatim': answers,
        'answer_completeness': {
            'valid_obtained': len(answers),
            'invalid_obtained': 0,
            'expected': 'infinite' if instance in ('P04d', 'P04f') else 1,
            'finite_representation_of_all_infinite_outcomes': False if instance in ('P04d', 'P04f') else None,
        },
        'unknowns_representation': unknown_repr,
        'observe_raw': a['observe']['raw'],
        'observe_method': a['observe']['method'],
        'observe_bindings': a['observe']['bindings'],
        'alternatives': m['alternatives'],
        'suspended_count': suspended,
        'suspended_items': m['suspended']['items'] if suspended is not None else None,
        'suspension_note': 'No source construct requests attributed-variable suspension or h_wait. SLG internal waiting consumers are not enumerated by the record; they are not inferred from the attributed-variable count.' if run['configuration'] == 'tabling' else 'No source construct requests suspension; an infinite recursive call is running work, not suspension.',
        'conclusions_withdrawn': [],
        'manual_actions': [],
        'steps_as_recorded': m['steps'],
        'measurements_note': 'Nulls are unavailable, not zero. With a harness fault, missing or placeholder boundary/store readings are unavailable. Steps are the cost mode\'s metric; storage samples, if present, are not true peaks.',
        'attempts': [
            {'attempt': x['attempt'], 'limit_s': x['limit_s'],
             'answers_verbatim': [v['verbatim'] for v in x['computations'][0]['queries'][0]['answers']],
             'execution_state': x['computations'][0]['execution_state']['states'],
             'safety_limit': x['safety_limit'], 'posed': x['posed']}
            for x in stage['attempts']
        ],
    }
    return {
        'configuration': run['configuration'], 'instance': instance,
        'program': pathlib.Path(run['program']['path']).name,
        'record': record, 'stage': 1, 'reached': True,
        'semantic': semantic, 'representation': representation,
        'simplification': None, 'identical_to_posed': None, 'residual_size': None,
        'execution_state': states,
        'execution_state_scope': 'harness reporting failure; computational final state unavailable' if fault else 'computation',
        'residual_equivalence': None,
        'equivalence_reasoning': reason,
        'observations': obs,
        'harness_fault': fault,
        'harness_fault_details': d['harness_faults'],
        'rule': 'SPECIFICATION Outcomes 1-3 and common observations; P04 valid outcomes; METRICS answer completeness; AMENDMENTS 3.1-3.2. ' + ('Harness placeholder error is explicitly scoped to the reporting fault, not attributed to the model.' if fault else 'Semantic result and execution state are independent.'),
    }


classified = [(record, d, classify(record, d)) for record, d in records]
outcomes = [entry for _, d, entry in classified if d['run']['mode'] == 'behaviour']
assert len(outcomes) == 30
behaviour = {(x['configuration'], x['instance'], x['program']): x for x in outcomes}
classification_keys = ['reached', 'semantic', 'representation', 'simplification', 'identical_to_posed',
                       'residual_size', 'execution_state', 'execution_state_scope', 'residual_equivalence']
mode_differences = []
for record, d, entry in classified:
    if d['run']['mode'] == 'behaviour':
        continue
    b = behaviour[(entry['configuration'], entry['instance'], entry['program'])]
    if any(entry[k] != b[k] for k in classification_keys):
        mode_differences.append({
            'configuration': entry['configuration'], 'instance': entry['instance'],
            'program': entry['program'], 'mode': d['run']['mode'], 'record': record,
            'stage': 1, 'behaviour': {k: b[k] for k in classification_keys},
            'behaviour_record': b['record'],
            'this_mode': {k: entry[k] for k in classification_keys},
            'harness_fault': entry['harness_fault'],
            'note': 'Answers and their semantic class agree. Storage instrumentation corrupted a harness event; the synthetic error is a reporting fault, with the final computational state unavailable. It does not establish a model-level error or a semantic disagreement. No measurement rerun exists in this checkout.',
            'harness_fault_details': entry['harness_fault_details'],
            'observations': entry['observations'],
        })

expressibility = []
for c in CONFIGS:
    for sub in ['P04a', 'P04b', 'P04c', 'P04d', 'P04e', 'P04f']:
        direction = 'ground membership' if sub in ['P04c', 'P04e'] else 'enumeration' if sub in ['P04d', 'P04f'] else None
        reason = 'Clauses, equality and ordered disjunction/list patterns transcribe the stated least relations and queries without moves, omissions, extra arguments, algorithm changes, or imposed domains. No R tokens or problem-supplied S code are needed. Failure to terminate/report answers is operational, not failure to express the definitions.'
        if c == 'tabling':
            reason += ' table/1 is the configuration\'s external SLG mechanism; its six declaration tokens per file are C under rules 1 and 12, not reformulation.'
        expressibility.append({'configuration': c, 'subproblem': sub, 'direction': direction,
                               'expressibility': 'expressible', 'reason': reason})

s_mechanisms = []
for sub in ['P04a', 'P04b', 'P04c', 'P04d', 'P04e', 'P04f']:
    s_mechanisms.append({
        'configuration': 'session', 'program': sub + '.pl',
        'mechanism': 'wait for an undefined procedure (configuration-wide session layer; loaded but not invoked by this P04 program)',
        'listed_at_phase_4': True, 'tokens': 0, 'token_ranges': [],
        'token_scope': 'S tokens in this program\'s frozen token text; no call uses the wait layer.',
        'source': 'harnesses/swi-prolog/S/session-wait.pl',
        'phase_4_reported_source_tokens': 158,
        'independent_frozen_source_token_count': None,
        'note': 'S-mechanisms.md says this layer is loaded for every session run and counted once per configuration. No frozen TSV for its source is supplied under results/swi-prolog/tokens. The declared 158 is attributed to that listing, not independently re-tokenized or counted six times. All P04 predicates called here are defined; no wait hook runs.',
    })

result = {'tokens': tokens, 'outcomes': outcomes, 'mode_differences': mode_differences,
          'expressibility': expressibility, 'late_definition': [], 's_mechanisms': s_mechanisms}
(OUT / 'swi-prolog.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')

# Independent structural coverage/inventory checks on the written artifact.
written = json.loads((OUT / 'swi-prolog.json').read_text())
assert set(written['tokens']) == set(texts)
for p, spans in written['tokens'].items():
    validate_spans(p, spans)
assert len(records) == 90
assert len(mode_differences) == 16
assert all(x['mode'] == 'storage' for x in mode_differences)
log_rows = [line.split('\t') for line in (SOURCE / 'results/swi-prolog/batch-log.tsv').read_text().splitlines()
            if len(line.split('\t')) > 4 and line.split('\t')[2].startswith('P04')]
log_keys = collections.Counter((r[1], r[2], r[3], r[4]) for r in log_rows)
record_keys = collections.Counter((d['run']['configuration'], d['run']['instance'], pathlib.Path(d['run']['program']['path']).name, d['run']['mode']) for _, d in records)
# A final storage record was completed after the batch log's last P04 entry.
assert not (log_keys - record_keys), log_keys - record_keys
unlogged = record_keys - log_keys
assert len({(x['configuration'], x['instance'], x['program'], x['stage']) for x in outcomes}) == 30
assert len(written['expressibility']) == 30

def totals(paths):
    counts = collections.Counter({c: 0 for c in CLASSES})
    for p in paths:
        for s in tokens[p]:
            counts[s['class']] += s['to'] - s['from'] + 1
    return dict(counts)

distinct_totals = totals(texts)
per_config = {}
for c in CONFIGS:
    canonical_paths = [p for p, aliases in texts.items() if any(x.startswith(c + '/') for x in [p] + aliases)]
    per_config[c] = totals(canonical_paths)
expanded = {k: sum(v[k] for v in per_config.values()) for k in CLASSES}
semantic_totals = dict(collections.Counter(x['semantic'] for x in outcomes))
exec_totals = dict(collections.Counter(s for x in outcomes for s in x['execution_state']))
summary = {'distinct_texts': len(texts), 'distinct_token_totals': distinct_totals,
           'per_configuration': per_config, 'expanded_totals': expanded,
           'behaviour_semantic': semantic_totals, 'behaviour_execution': exec_totals,
           'records': len(records), 'logged_P04_runs': len(log_rows),
           'unlogged_records': [list(k) + [v] for k, v in unlogged.items()],
           'mode_differences': len(mode_differences)}
print(json.dumps(summary, indent=2))

notes = '''# Independent classification notes: SWI-Prolog, batch 1B, P04

Classified from the permitted clone in classifier-1B-B2. I did not write the programs, consult another classifier's work, run SWI-Prolog, execute a study program or harness, or access the web. All writes are in this output directory. `classify.py` reads the permitted evidence, generates the JSON, checks recorded program SHA-256 values, verifies shared texts, validates coverage against the frozen TSV indices, and checks answer values. It does not tokenize source code.

## Scope and evidence

The inventory contains 12 distinct texts, representing 30 programs: six shared across constraints, coroutines, plain and session, plus six tabling texts. The shared texts have identical token classes in all four configurations. No configuration-specific reclassification of a shared text is needed: session's globally loaded wait layer changes none of the constructs in these programs. There are 30 single-stage behaviour records and 60 cost/storage records, all inspected through bounded extraction. The three tabling timeout behaviour records each contain both the 60-second and 600-second attempts; both are preserved in each outcome's observations. There are no P08 programs, named variants, INVALID records, or raw-rerun-m2 directories for P04 in this checkout. `rerun-m2-log.tsv` is absent. No P04 stage is unreached and no setup/replay failure is recorded.

The P04 batch log contains 89 runs. The tabling/P04f storage record also exists, so I inspected and compared it despite its missing batch-log row. Every logged behaviour run is covered exactly once. All 60 measurement records were compared; only the 16 classification differences are listed. No cost record differs in classification. Measurement values can differ without changing these classes.

## Token judgments and external mechanisms

Definition cases, constants and queries are P. The alist-left body retains its recursive call before the equality, and its recursive case before the base case. The right version retains the stated opposite case order and head pattern. No case/conjunct is moved or omitted. Prolog's [a|M] is construction of the stated finite sequence, not an accumulator or a changed algorithm. There are no R tokens. The table/1 directive in each tabling file is C (six tokens), because it changes resolution and termination while preserving the least relation (rules 1 and 12); it is an external mechanism supplied by that configuration, not S.

The input lookup `memberchk(alternative_value(K), Cs)` or `memberchk(alist_argument(S), Cs)` is P. It retrieves this stage's information from the harness-defined input encoding. It is not a search generator, extra problem case, or answer adapter. The contract explicitly leaves stage bodies to the metric rules and does not list memberchk as H. I apply rules 1 and 3, with ordinary input transcription. This is a judgment call: a more expansive notion of harness plumbing could call these H, but section 12's fixed H list and rule 13 do not authorize that expansion. Each such lookup has nine frozen tokens. The stage head including `:-`, the unknowns fact, and the query interface fact are H under the contract. The stage clause's final period is H as the terminator of the enclosing interface construct; body goals/connectives are P under rules 10 and 20. The latter punctuation boundary is not explicitly resolved by rule 10 and is disclosed rather than silently absorbed into the final P goal.

External mechanisms used by programs: memberchk/2 (outside plain's enumerated ISO core, also inherited by the other configurations) in P04a, P04b, P04c and P04e for each of the five configurations; table/1/SLG in all six tabling programs. No built-in replaces loop or alist, and no constraint solver, coroutine, domain bound or hand-written scheduler is used. Engine operations belong to the fixed session harness, not program C tokens.

No P04 frozen program text contains any S tokens or defines its own supporting mechanism. The phase-4 session wait-for-undefined-procedure layer is nevertheless loaded as part of every session run. I list it for each session program as loaded but uninvoked, with zero *program* S tokens and no ranges. All called procedures in these P04 programs already have definitions. The phase-4 file advertises 158 source tokens once per session configuration; there is no frozen TSV for that source in the permitted tokens tree, and the instruction forbids re-tokenizing. Thus 158 is explicitly attributed to the listing and the independent frozen source count is unavailable, not invented or multiplied by six. The distinct/expanded totals below count only the requested frozen program texts. The other four configurations use no S mechanism.

## Outcome judgments

I distinguish a delivered answer from an empty rendering of bindings while work is running. `observe.raw = "true "` and `{}` bindings at a budget or timeout are not an answer that the disjunction or ground alist query succeeded. They expose no residual relation or solved form. In particular a free X in the in-flight loop is not an unconstrained answer. Empty answer streams here are **none reported**, not logical false and not an unsound empty-set claim. Representation and residual-only fields are null. There are no reported residual or solved-form answers whose equivalence requires a separate constraint solver; explicit answers are checked directly against the valid sets by `classify.py` and by the least-relation argument below.

Under the least-relation semantics loop has no instances. P04a/P04b therefore have exactly X=1. The four non-tabled P04a runs never reach this alternative and hit budget. Their P04b counterparts report X=1 and then hit budget seeking another answer. The P04b semantic result is **complete** despite budget execution, and X becoming free on backtracking does not retract the answer already found. Tabling detects the empty recursive loop and finishes both orders with exactly X=1. In the tabled P04b record no binding remains in observe() after exhaustive backtracking; the earlier delivered answer still counts.

The two alist definitions denote exactly a^n for all nonnegative n, by induction on finite derivations (base n=0, recursive construction adds one a). Ground [a,a] is therefore true in both. Non-tabled alist-left descends forever before its equality or base case can return; P04c and P04d hit budget with no answers. Non-tabled alist-right's P04e returns true and finishes. Its P04f produces lengths 0 through 19, in that order, and stops at the cap with alternatives pending: the representation is explicit and the semantic class is **partial**, since those twenty substitutions are a proper subset of infinitely many. Continued requests would visit every finite length, so fairness/eventual enumeration is positive even though the capped report is partial. This separates answer-set completeness from eventual reachability.

Tabling P04c, P04d and P04f time out without delivered answers in both attempts. For P04c, alist-left calls alist(M) with M free before checking the ground list equality, exposing the same unbounded tabled generator as the open queries. The internal tables can hold many answers (the storage record counts them), but no query-variable values or equivalent finite residual are delivered or projected by observe(). Table-answer counts do not themselves denote a query answer set. These runs are **none reported / timeout**, not suspension or budget. The local table completion of an infinite answer set explains the observed failure to deliver; a claim that the query enumerates every finite answer is not established by these records. No count of internal SLG waiting consumers is available. Attributed-variable zeros must not be mistaken for such a count. The timeout records also contain a contradictory observation method saying nothing could be read although some step/store counters are present; I do not treat their empty-binding display or zero suspension placeholder as a successful observation of a residual.

The successful storage readings give zero retained choicepoints for finished P04e (all configurations) and for tabling P04a/P04b; one clause choicepoint at the P04f cap in each non-tabled configuration. These are backtracking frames, not counts of remaining solutions. No program uses attributed-variable suspension or h_wait; successfully observed non-timeout behaviour boundaries show zero suspended attributed variables/residual goals. Unmeasured counts are null. Every stage has no manual intervention and no earlier-stage withdrawal; automated timeout retries are recorded separately.

## Harness faults and ambiguities

All sixteen non-tabled storage records for P04a-P04d contain malformed harness events and lack a readable completion event. Their execution field is `error` with `determined=false` and the explicit basis "not the system's error". I preserve that error label solely as a **harness reporting failure**, mark every corresponding mode-difference entry `harness_fault: true`, and state that the final computational state is unavailable. This is not evidence that a correctly measured model run errs. Fragmentary events refer to budget/inference_limit_exceeded, but I do not repair incomplete JSON into an asserted valid end event. Their answers agree with behaviour: P04b retains X=1, the others report nothing. Hence there is a reporting/execution difference, without a demonstrated semantic disagreement. Missing step/store/suspension readings are unavailable, not zero, and cannot substantiate a performance comparison. None of these filenames has INVALID, but their own harness_faults array is sufficient to flag the fault.

The specification's execution classes are worded for the computation and supply no unavailable class. The schema forces an `error` placeholder for a missing event (run's make_comp code, around lines 620 and 690). That creates a classification ambiguity: copying the label without qualification would wrongly attribute a harness failure to the system. The added execution_state_scope and notes make that limitation explicit. A dedicated unavailable execution-state value would be clearer. I have not changed the frozen rules.

Budget behaviour records report 1,000,009 inferences for a 1,000,000 budget. That exceeds the amendment's stated maximum slack of eight by one; I retain the recorded budget classification and do not silently normalize the count. This is a step-accounting question, not evidence of a different semantic outcome. No labelled measurement rerun is present to resolve it.

All 30 configuration/subproblem pairs are **expressible**. Transcription is possible independently of termination. C declarations improve some outcomes and fail to deliver others; neither result changes expressibility or introduces R. Directions are distinguished as ground membership (c/e) and enumeration (d/f). Late-definition classification does not apply.

## Reading restrictions

No file outside the permitted list was read. Commands read the named root documents, the P04 problem file and problems README; systems/swi-prolog README and measurement; the common and SWI harness contracts, schema/stages, SWI S listing/source and selected run-driver lines; the P04 program texts (including comparisons of permitted shared texts), frozen token TSVs and TEXTS-1B-P04 inventory; P04 raw records; and P04 rows of batch-log.tsv. Directory/file-name inventories were confined to permitted directories. The absent rerun-m2 log was attempted, and absent P04 raw-rerun-m2 paths checked. Program comments that refer to the prohibited author's README were encountered as part of allowed program source; that README was not opened. Links/names of other prohibited material in allowed root documents were not followed. There was no accidental read of another classifier's work, author notes files, another system, private material, or the web. This checking script reads its own output files only inside the allowed output directory.

## Totals and outcome summary

'''
notes += 'Frozen distinct texts: **' + str(sum(distinct_totals.values())) + '** tokens over 12 texts: ' + ', '.join(f'{k}={distinct_totals[k]}' for k in CLASSES) + '. Every frozen index is covered exactly once; aliases were checked against those same spans.\n\n'
notes += '| configuration | P | C | R | S | H | total |\n|---|---:|---:|---:|---:|---:|---:|\n'
for c, v in per_config.items():
    notes += '| ' + c + ' | ' + ' | '.join(str(v[k]) for k in CLASSES) + ' | ' + str(sum(v.values())) + ' |\n'
notes += '| expanded total | ' + ' | '.join(str(expanded[k]) for k in CLASSES) + ' | ' + str(sum(expanded.values())) + ' |\n\n'
notes += 'Behaviour stages: **30**; semantic totals: ' + ', '.join(f'{k}={v}' for k, v in semantic_totals.items()) + '; execution totals: ' + ', '.join(f'{k}={v}' for k, v in exec_totals.items()) + '. No unsound, undetermined, residual, solved-form, cyclic, unreached, or suspended behaviour results. Compared **60** measurement records: **16** storage reporting-fault differences, **0** cost classification differences, no labelled measurement reruns. All **30** expressibility judgments are expressible; no P08 late-definition entries.\n'
(OUT / 'swi-prolog.notes.md').write_text(notes)
