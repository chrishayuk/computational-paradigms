"""Independent P12 classification and evidence checks. Never executes Absys.

Reads only the explicitly permitted files in classifier-1C-B; writes here.
Token boundaries come exclusively from the frozen TSVs, never a tokenizer.
"""
from pathlib import Path
import collections
import csv
import gzip
import hashlib
import json
import re

ROOT = Path('.')
OUT = Path(__file__).resolve().parent
CONFIGS = ['absys', 'absys-depth-first', 'absys-wake-back']


def read_json(path):
    with (gzip.open(path, 'rt') if str(path).endswith('.gz') else path.open()) as f:
        return json.load(f)


def tokens(path):
    with path.open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert [int(r['index']) for r in rows] == list(range(len(rows)))
    return [r['token'] for r in rows]


def classify_tokens(ts):
    spans = []
    def add(lo, hi, cls, construct, rule):
        assert lo <= hi
        spans.append(dict(from_=lo, to=hi, **{'class': cls}, construct=construct, rule=rule))
        spans[-1]['from'] = spans[-1].pop('from_')
    g = ts.index("gtz'")
    const_starts = [i for i in range(g) if ts[i] in ['acc1', 'acc2'] and ts[i+1] == '=']
    for j, start in enumerate(const_starts):
        end = const_starts[j+1]-1 if j+1 < len(const_starts) else g-1
        add(start, end, 'P', f'{ts[start]}: stage-1 closed-world accept fact in the constants table',
            'P definition; rules 1, 10; harnesses/absys/README 3.9, 3.12')
    assert ts[g:g+6] == ["gtz'", '=', 'lambda', 'q', 'begin', '{']
    ch = ts.index("choice'")
    assert ts[ch-2:ch] == ['}', 'end']
    add(g, g+4, 'R', 'gtz: declaration and lambda introducing an extra guard relation',
        'R extra definition; rule 10')
    assert [int(ts[g+8+4*i]) for i in range(16)] == list(range(1,17))
    add(g+5, ch-2, 'C', 'gtz body: explicit enumeration of positive values 1 through 16',
        'Rule 6: enumeration not stated by the problem; rule 10 nested body')
    add(ch-1, ch-1, 'R', 'gtz: closing delimiter of the extra definition', 'R extra definition; rule 10')
    assert ts[ch:ch+8] == ["choice'", '=', 'lambda', 'm', ',', 'w', 'begin', '{']
    add(ch, ch+7, 'P', 'choice: relation declaration and ordered case disjunction', 'Rules 1, 3, 6, 10')
    add(ch+8, ch+11, 'P', 'choice case 1: empty sequence', 'Rules 1, 2, 3')
    add(ch+12, ch+19, 'P', 'choice case 2: disjunction separator and nonempty sequence head',
        'Rules 2, 6, 10, 20')
    assert ts[ch+20:ch+24] == ['gtz', '(', 'm', ')']
    add(ch+20, ch+23, 'R', 'replacement of the primitive m > 0 guard by gtz(m)',
        'R rewritten comparison; systems/absys/README Notation; rule 10')
    add(ch+24, ch+32, 'P', "choice case 2: stated alternatives e = L or e = R in order",
        'Rules 1, 2, 6, 10')
    add(ch+33, ch+37, 'P', 'choice case 2: primitive arithmetic decomposition m1 = m - 1',
        'SPECIFICATION Arithmetic and comparison; rules 3, 8')
    add(ch+38, ch+43, 'P', 'choice case 2: recursive choice(m1,t)', 'Rules 1, 3, 10')
    add(ch+44, ch+45, 'P', 'choice: closing case disjunction and lambda delimiters', 'Rules 6, 10')
    ac = ts.index("accept'")
    assert ac == ch+46
    add(ac, ac+4, 'P', 'accept: closed-world fact relation declaration', 'Rules 1, 3, 10')
    if ts[ac+5] == '{':
        assert ts[ac+5:ac+15] == ['{','u','=','acc1','or','u','=','acc2','}','end']
        add(ac+5, ac+5, 'P', 'accept: opening fact disjunction', 'Rules 6, 10')
        add(ac+6, ac+8, 'P', 'accept fact 1', 'Rules 1, 6')
        add(ac+9, ac+12, 'P', 'accept fact 2 with preceding disjunction separator', 'Rules 1, 6, 20')
        add(ac+13, ac+14, 'P', 'accept: closing fact disjunction and lambda', 'Rules 6, 10')
        stage = ac+15
    else:
        assert ts[ac+5:ac+9] == ['u','=','acc1','end']
        add(ac+5, ac+7, 'P', 'accept: sole closed-world fact', 'Rules 1, 6')
        add(ac+8, ac+8, 'P', 'accept: closing lambda delimiter', 'Rule 10')
        stage = ac+9
    assert ts[stage:] == ['begin','choice','(','n',',','s',')','accept','(','s',')','end']
    add(stage, stage, 'P', 'stage 1: opening query conjunction', 'P query; rule 10')
    add(stage+1, stage+6, 'P', 'stage 1: choice(n,s), first conjunct', 'P query; rules 1, 3')
    add(stage+7, stage+10, 'P', 'stage 1: accept(s), second conjunct', 'P query; rules 1, 3')
    add(stage+11, stage+11, 'P', 'stage 1: closing query conjunction', 'P query; rule 10')
    assert [i for s in spans for i in range(s['from'], s['to']+1)] == list(range(len(ts)))
    return spans


def values(raw):
    """Read already printed ground s bindings; do not derive missing bindings."""
    out = []
    for term in re.findall(r'^\s+s = (\[[^\n]*\])$', raw, re.M):
        vs = re.findall(r"'([lr])'", term)
        assert term == '[' + ';'.join("'"+v+"'" for v in vs) + ']'
        out.append(tuple(vs))
    return out


def expected(subproblem, n):
    return {'P12a': {('r',), ('l',)*n}, 'P12b': {('r',)},
            'P12c': {('r',)*n}, 'P12d': {('l',)*n}}[subproblem]


def class_stage(record, stage):
    r = record['run']
    assert len(stage['attempts']) == 1
    a = stage['attempts'][0]
    assert len(a['computations']) == 1
    c = a['computations'][0]
    assert c['id'] == 'main' and len(c['queries']) == 1
    q = c['queries'][0]
    vs = values(a['observe']['raw'])
    valid = expected(r['subproblem'], r['parameters']['n'])
    assert stage['stage'] == 1 and a['posed']['how'] == 'fresh'
    # Every P12 stage in this batch was actually posed, including the timeouts.
    if c['execution_state']['states'] == ['timeout']:
        assert not vs and not q['answers'] and not a['observe']['raw'] and a['print'] is None
        assert a['safety_limit']['hit'] and a['safety_limit']['action'] == 'fixed-limit-timeout'
        assert a['exit']['signal'] == 'SIGKILL'
        assert c['alternatives']['at_boundary'] is None and c['suspended']['at_boundary'] is None
        semantic, representation, equivalence = 'none reported', None, None
    else:
        assert c['execution_state']['states'] == ['finished']
        assert len(vs) == len(valid) and set(vs) == valid
        assert c['suspended']['at_boundary'] == 0
        assert c['alternatives']['at_boundary'] == len(vs)
        qvs = [v for answer in q['answers'] for v in values(answer['verbatim'])]
        assert qvs == vs[:q['cap']]
        assert q['ended_by'] == ('cap' if len(vs)>q['cap'] else 'exhausted')
        semantic, representation = 'complete', 'explicit'
        equivalence = (
            'Equivalent: the observed ground s bindings are exactly the closed-world accept facts, '
            'each a sequence over L/R of length <= n. By induction on n, choice admits precisely '
            'all such sequences: its base admits [], and its guarded recursive case prepends L or R. '
            'Every recursive m is in 0..n, n is 8, 12 or 16, and gtz(m) iff m>0 on 0..16. '
            'Thus the conjunction admits exactly these facts. check_and_classify.py checks every '
            'observed value, set equality, guard domain and query cap. '
            + ('For this any-one query the first valid answer already satisfies the request; observe also reads the full solution set.'
               if r['parameters']['cap']==1 else 'Every valid solution was reported and enumeration exhausted.')
        )
    assert not record['manual_actions'] and not a['manual_actions']
    return dict(reached=True, semantic=semantic, representation=representation,
                simplification=None, identical_to_posed=None, residual_size=None,
                execution_state=c['execution_state']['states'], residual_equivalence=equivalence)


def measurement(record, path):
    a = record['stages'][0]['attempts'][0]
    c = a['computations'][0]
    return {'record': str(path.relative_to(ROOT)), 'steps': c['steps'],
            'alternatives': c['alternatives'], 'store': a['store'],
            'problem_operations': c['problem_operations'],
            'candidates_examined_before_each_solution': None,
            'partial_sequences_held': None,
            'note': ('Missing figures are unavailable, not zero. No problem-defined candidate or partial-sequence counter is provided. '
                     'A sampled maximum is not an exact peak; answer steps are reporting latency after elaboration, not candidate positions.')}


def main():
    result = {k: {} if k=='tokens' else [] for k in
              ['tokens','outcomes','mode_differences','expressibility','late_definition','s_mechanisms']}
    manifest = list(csv.DictReader((ROOT/'results/absys/tokens/TEXTS-1C-P12.tsv').open(), delimiter='\t'))
    assert len(manifest) == 12
    counts = collections.Counter({k:0 for k in 'PCRSH'})
    token_table = []
    for row in manifest:
        key = row['text']
        ts = tokens(ROOT/f'results/absys/tokens/{key}.tokens.tsv')
        spans = classify_tokens(ts)
        result['tokens'][key] = spans
        per_text = collections.Counter()
        source = ROOT/'programs/absys'/key
        for alias in row['also the text of'].split():
            assert source.read_bytes() == (ROOT/'programs/absys'/alias).read_bytes()
            assert ts == tokens(ROOT/f'results/absys/tokens/{alias}.tokens.tsv')
        for s in spans:
            n = s['to']-s['from']+1
            counts[s['class']] += n
            per_text[s['class']] += n
        token_table.append((key, len(ts), per_text['P'], per_text['C'], per_text['R']))
    # This is a check of the mathematical finite guard, not execution of a program.
    assert all((m in range(1,17)) == (m>0) for m in range(17))
    records = []
    for cfg in CONFIGS:
        for directory in ['raw', 'raw-rerun-m2']:
            for path in sorted((ROOT/'results/absys'/cfg/'P12'/directory).glob('*')):
                assert path.name.endswith(('.json','.json.gz'))
                rec = read_json(path)
                assert rec['run']['configuration'] == cfg and rec['run']['problem'] == 'P12'
                assert len(rec['stages']) == 1
                assert not rec['harness_faults'] and '.INVALID.' not in path.name
                src = ROOT/rec['run']['program']['path']
                assert hashlib.sha256(src.read_bytes()).hexdigest() == rec['run']['program']['sha256']
                records.append((path, rec))
    assert len(records) == 216
    behaviour = {}
    for path, rec in records:
        r = rec['run']
        if r['mode'] == 'behaviour':
            key = (r['configuration'],r['instance'],r['program']['path'])
            assert key not in behaviour
            behaviour[key] = (path, rec)
    assert len(behaviour) == 72
    measured = collections.defaultdict(dict)
    for path, rec in records:
        r = rec['run']
        if r['mode'] != 'behaviour':
            key = (r['configuration'],r['instance'],r['program']['path'])
            bp, br = behaviour[key]
            bc = class_stage(br, br['stages'][0])
            mc = class_stage(rec, rec['stages'][0])
            # Equivalence prose depends on the query, so is also identical here.
            if bc != mc:
                result['mode_differences'].append(dict(configuration=r['configuration'],
                    instance=r['instance'], program=Path(r['program']['path']).name,
                    mode=r['mode'],record=str(path.relative_to(ROOT)),stage=1,
                    behaviour=bc,this_mode=mc,note='Compared against '+str(bp.relative_to(ROOT))))
            assert values(rec['stages'][0]['attempts'][0]['observe']['raw']) == values(br['stages'][0]['attempts'][0]['observe']['raw'])
            measured[key][r['mode']] = measurement(rec,path)
    assert len(measured) == 72 and all(set(m)=={'cost','storage'} for m in measured.values())
    # Check every actual run in the batch-1C P12 logs has its record.
    logged = collections.Counter()
    no_program = 0
    for log in sorted((ROOT/'results/absys/logs').glob('*P12*')):
        for line in log.read_text().splitlines():
            cols = line.split('\t')
            if cols[-1] == 'no program':
                no_program += 1
            else:
                assert len(cols)==7 and cols[5]=='exit 0'
                logged[(cols[1],cols[2],cols[3],cols[4])] += 1
    recorded = collections.Counter((r['run']['configuration'],r['run']['instance'],
        Path(r['run']['program']['path']).name,r['run']['mode']) for _,r in records)
    assert logged == recorded and no_program == 72
    for key, (path, rec) in sorted(behaviour.items()):
        r = rec['run']; a = rec['stages'][0]['attempts'][0]; c = a['computations'][0]; q = c['queries'][0]
        classification = class_stage(rec, rec['stages'][0])
        finished = classification['semantic'] == 'complete'
        vs = values(a['observe']['raw'])
        obs = {
            'outcomes_verbatim': [ans['verbatim'] for ans in q['answers']],
            'observe_raw_verbatim': a['observe']['raw'],
            'print_verbatim': a['print'],
            'solutions_in_observed_order': [list(v) for v in vs],
            'unknowns_representation': ('s is a fully ground finite sequence of L/R atoms; no query unknown remains.'
                if finished else 'No query binding/state was observed before the timeout; the captured stdout contains parameter/prelude states only. The representation of s at interruption is unavailable.'),
            'alternatives_held': c['alternatives'],
            'suspended_work': c['suspended'],
            'execution_note': ('Hibernating ground derivations have no suspended work. All search work finished; saved answer derivations do not imply alternatives pending, even when answers(1) ended at its cap (harness README 3.7).'
                if finished else 'Stage 1 was posed and search began. SIGKILL at the fixed 600-second safety limit interrupted elaboration before observe/print could read query state. This is reached/timeout, not not reached or budget.'),
            'answer_completeness': {'query': r['parameters']['answers'],
                'valid_collected': len(q['answers']), 'valid_expected_for_query': 1 if q['cap']==1 else len(expected(r['subproblem'],r['parameters']['n'])),
                'invalid_collected': 0, 'valid_bindings_observed': len(vs),
                'all_valid_solutions': len(expected(r['subproblem'],r['parameters']['n'])), 'ended_by': q['ended_by']},
            'conclusions_withdrawn': [], 'manual_actions': [],
            'candidates_examined_before_each_solution': None, 'partial_sequences_held': None,
            'search_observation': 'The query keeps the specified choice-before-accept presentation order. The records do not count accept evaluations or partial sequences; candidate positions and search avoidance cannot be inferred from final derivations or reporting latency.',
            'measurements': measured[key],
        }
        result['outcomes'].append(dict(configuration=r['configuration'],instance=r['instance'],
            program=Path(r['program']['path']).name,record=str(path.relative_to(ROOT)),stage=1,
            **classification,harness_fault=False,observations=obs,
            rule='SPECIFICATION Outcomes 1-3 and Observations; harnesses/absys/README 3.7-3.8; P12 Limits; AMENDMENTS 3.1-3.2 and 3.4'))
    for cfg in CONFIGS:
        for sub in ['P12a','P12b','P12c','P12d']:
            result['expressibility'].append(dict(configuration=cfg,subproblem=sub,direction=None,
                expressibility='expressible with reformulation',reason=(
                'The native configuration has no > comparison, so choice cannot be transcribed verbatim. '
                'The extra gtz definition and its call replace m>0 by m in {1,...,16}; its body is C under '
                'rule 6 and its definition/call are R under rule 10. Starting with n=8,12,16, every recursive '
                'm is in 0..n, so this preserves the entire choice relation on every sequence at the stated '
                'sizes, not merely the accepted answers. The head equations, L/R disjunction, decrement, '
                'recursion, accept facts and query order are transcriptions. No supporting mechanism is '
                'needed. The finite guard is not a general positive-integer comparison for n>16; hidden '
                'variants were not available or read, so no claim that those pass is made. '
                'Systems/absys Notation and SPECIFICATION expressibility; METRICS rules 3,6,8,10; AMENDMENTS 3.4.')))
        for row in manifest:
            filename = Path(row['text']).name
            result['s_mechanisms'].append(dict(configuration=cfg,program=filename,mechanism=None,
                listed_at_phase_4=None,tokens=0,token_spans=[],
                note='No S mechanism is used or supplied. The phase-4 S-mechanisms.md lists none for this configuration. Search, arithmetic, equality and suspension are native; gtz is a finite guard reformulation/enumeration (R/C), not a general supporting mechanism.'))
    (OUT/'absys.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    # Re-open the delivered JSON and independently check coverage from its spans.
    delivered = read_json(OUT/'absys.json')
    for row in manifest:
        key=row['text']; n=len(tokens(ROOT/f'results/absys/tokens/{key}.tokens.tsv'))
        cover=[0]*n
        for span in delivered['tokens'][key]:
            assert span['class'] in 'PCRSH' and 0 <= span['from'] <= span['to'] < n
            for i in range(span['from'],span['to']+1): cover[i]+=1
        assert cover == [1]*n
    assert len(delivered['outcomes'])==72 and not delivered['mode_differences']
    summary = {'distinct_texts':12,'token_totals':dict(counts),'total_tokens':sum(counts.values()),
        'behaviour_stages':72,'semantic':dict(collections.Counter(o['semantic'] for o in result['outcomes'])),
        'execution':dict(collections.Counter(', '.join(o['execution_state']) for o in result['outcomes'])),
        'measurement_records_compared':144,'mode_differences':len(result['mode_differences']),
        'table':token_table}
    (OUT/'check-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
