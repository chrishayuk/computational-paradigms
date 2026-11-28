"""Validate requested coverage without running any study program."""
from collections import Counter
import hashlib
import json
from classify import ALIASES, TEXTS, ROOT, OUT, frozen, record_files, read_record

d = json.loads((OUT / 'swi-prolog.json').read_text())
assert set(d) == {'tokens','outcomes','mode_differences','expressibility','late_definition','s_mechanisms'}
assert set(d['tokens']) == set(TEXTS)
totals = Counter()
per_text = {}
for path, spans in d['tokens'].items():
    n = len(frozen(path))
    coverage = Counter()
    for s in spans:
        assert s['class'] in 'PCRSH'
        assert isinstance(s['from'], int) and isinstance(s['to'], int)
        assert 0 <= s['from'] <= s['to'] < n
        assert s['construct'] and s['rule']
        coverage.update(range(s['from'], s['to'] + 1))
        totals[s['class']] += s['to'] - s['from'] + 1
    assert coverage == Counter(range(n)), path
    per_text[path] = Counter({c:sum(s['to']-s['from']+1 for s in spans if s['class']==c) for c in 'PCRSH'})

observed = Counter((o['record'],o['stage'],o['attempt'],o['computation'],o['reading']) for o in d['outcomes'])
expected = Counter()
job_keys = Counter()
record_count = 0
faults = []
missing_boundaries = []
for f in record_files():
    rec = read_record(f)
    r = rec['run']
    record_count += 1
    job_keys[(r['configuration'],r['instance'],r['mode'],r['program']['path'].split('/')[-1])] += 1
    assert hashlib.sha256((ROOT / r['program']['path']).read_bytes()).hexdigest() == r['program']['sha256']
    if rec.get('harness_faults'):
        faults.append(str(f.relative_to(ROOT)))
    if r['mode'] == 'behaviour':
        for stage in rec['stages']:
            for attempt in stage['attempts']:
                for comp in attempt['computations']:
                    for reading in (['finite','stream'] if r['subproblem']=='P09d' else [None]):
                        expected[(str(f.relative_to(ROOT)),stage['stage'],attempt['attempt'],comp['id'],reading)] += 1
    else:
        for stage in rec['stages']:
            for attempt in stage['attempts']:
                for comp in attempt['computations']:
                    if comp['suspended']['at_boundary'] is None:
                        missing_boundaries.append((r['configuration'],r['instance'],r['mode'],comp['id']))
assert observed == expected
assert all(v == 1 for v in observed.values())
logs = 0
for cfg in ['plain','tabling','coroutines','constraints','session']:
    for problem in ['P09','P10','P11']:
        for line in (ROOT/'results/swi-prolog/logs'/f'1C-{cfg}-{problem}.tsv').read_text().splitlines():
            cols = line.split('\t')
            assert job_keys[(cols[1],cols[2],cols[4],cols[3])] == 1
            logs += 1
assert logs == record_count == 210
assert len(d['expressibility']) == 70
assert len(d['s_mechanisms']) == 65
assert d['late_definition'] == []
assert all(x['harness_fault'] for x in d['mode_differences'])
per_config = {}
for cfg in ['plain','tabling','coroutines','constraints','session']:
    ct = Counter()
    for alias, first in ALIASES.items():
        if alias.startswith(cfg+'/'):
            ct.update(per_text[first])
    per_config[cfg] = dict(ct)
summary = dict(unique_texts=len(TEXTS),program_paths=len(ALIASES),record_count=record_count,
               behaviour_entries=len(d['outcomes']), unique_text_token_totals=dict(totals),per_configuration_token_totals=per_config,
               semantics=dict(Counter(o['semantic'] for o in d['outcomes'])),
               representations=dict(Counter(str(o['representation']) for o in d['outcomes'])),
               simplification=dict(Counter(str(o['simplification']) for o in d['outcomes'])),
               effects_at_problem_end=dict(Counter(o['effects']['class_at_problem_end'] for o in d['outcomes'] if 'effects' in o and o['stage']==({'P11a':1,'P11b':1,'P11c':3,'P11d':3}[o['instance']]))),
               mode_differences=len(d['mode_differences']),fault_records=faults,unavailable_suspended_boundaries=missing_boundaries)
(OUT/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
