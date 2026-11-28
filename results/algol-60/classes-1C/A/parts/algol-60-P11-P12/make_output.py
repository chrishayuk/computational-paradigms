"""Builds algol-60.json for ALGOL 60 P11 and P12 (batch 1C), classifier 1C-A.
Reads tokens.json (from classify_tokens.py) and the raw records; writes
algol-60.json. Read-only on the repository.
Usage: python3 -I make_output.py REPO_ROOT"""
import json, sys, os, glob, gzip, re

ROOT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, 'results/algol-60')


def load(p):
    if p.endswith('.gz'):
        with gzip.open(p, 'rt') as f:
            return json.load(f)
    with open(p) as f:
        return json.load(f)


def records(conf, prob):
    out = {}
    for p in sorted(glob.glob(f'{RES}/{conf}/{prob}/raw/*.json')) + sorted(glob.glob(f'{RES}/{conf}/{prob}/raw/*.json.gz')):
        d = load(p)
        out.setdefault(d['run']['instance'], {})[d['run']['mode']] = (os.path.relpath(p, ROOT), d)
    return out


def comp(d, st):
    a = d['stages'][st - 1]['attempts'][-1]
    return a, a['computations'][0]


def peak(store, k):
    q = store.get('quantities', {}).get(k)
    if not q:
        return None
    if q.get('peak'):
        return q['peak']['value']
    return q.get('boundary')


tok = json.load(open(os.path.join(HERE, 'tokens.json')))['tokens']
EXT = {'report': '.alg', 'x1': '.a60', 'x1sim': '.a60'}

outcomes = []
modediff = []
checked_modes = []

# ------------------------------------------------------------------ P11
P11_VALID = {
    'P11a': {1: 'one answer, x = 2 or x = 3; L holds exactly that one entry'},
    'P11b': {1: 'one answer, x = 2 or x = 3; L holds exactly that one entry (a log <1, 2> is extra)'},
    'P11c': {1: 'any one of x in {1, 2, 3} (pick(x) and emit(x); emit does not constrain x)',
             2: 'any one of x in {2, 3}',
             3: 'commit: the system selects v from {2, 3}; valid after the commit x = v; L should hold exactly the entry of v'},
    'P11d': {1: 'any one of x in {1, 2, 3}',
             2: 'commit: the system selects v from {1, 2, 3}; valid after the commit x = v',
             3: 'x != 1 with x = v: none if v = 1, else x = v'},
}

for conf in ('report', 'x1', 'x1sim'):
    recs = records(conf, 'P11')
    for inst in ('P11a', 'P11b', 'P11c', 'P11d'):
        path, d = recs[inst]['behaviour']
        cost = recs[inst].get('cost')
        stor = recs[inst].get('storage')
        log = d['effects']['log_after_run']
        K = len(d['stages'])
        committed_v = None
        for st in range(1, K + 1):
            a, c = comp(d, st)
            ans = [x['verbatim'] for x in c['queries'][0]['answers']]
            states_h = c['execution_state']['states']
            obs = a['observe']['raw']
            m = re.search(r'untried and kept for a later stage: (\d+)', obs)
            untried = int(m.group(1)) if m else 0
            em = [e['entry'] for e in (a.get('effects') or [])]
            exec_state = ['alternatives pending'] if untried > 0 else ['finished']
            steps = None
            if cost:
                _, cc = comp(cost[1], st)
                steps = cc['steps']
            store = comp(stor[1], st)[0]['store'] if stor else {}
            e = {'configuration': conf, 'instance': inst, 'program': inst + EXT[conf], 'record': path,
                 'stage': st, 'reached': True, 'harness_fault': bool(d.get('harness_faults'))}
            note_rec = 'harness recorded states ' + json.dumps(states_h) + ' (the program prints no [alternatives] or [suspended] tag)'
            obs_common = []
            if steps:
                obs_common.append(f"cost run {cost[0].split('/')[-1]}: steps stage {steps['stage']}, restated {steps['restated']}, to first answer {steps['to_first_answer']}, repeated work (name_repeat_evaluations) {steps['repeated_work']['name_repeat_evaluations'] if steps['repeated_work'] else None}")
            elif conf == 'x1sim':
                obs_common.append('x1sim: behaviour only, no step count (budget not enforced); steps unavailable, not 0 (AMENDMENTS 3.1)')
            if store:
                pk = {k: peak(store, k) for k in ('frames', 'array_elements', 'call_depth')}
                obs_common.append(f"storage run: peaks {json.dumps(pk)} (null: not above the previous stage's peak, harness README 3.4)")
            if any('recreated_for_budget: true' in n for n in a.get('notes', [])):
                obs_common.append('report/x1 re-created the computation for its budget (harness README 3.1): the earlier stages were run again in a fresh process, their emits not appended to L again (so no duplicate entries are in L), counted under no restart cost')
            if inst in ('P11a', 'P11b'):
                e.update({'semantic': 'complete', 'representation': 'explicit', 'simplification': None,
                          'identical_to_posed': None, 'residual_size': None, 'execution_state': ['finished'],
                          'residual_equivalence': None})
                ent = [x['entry'] for x in log]
                if inst == 'P11a':
                    eff = 'exact'
                    timing = f'L = <{", ".join(ent)}>: the one entry 2 was performed at commitment (in the one stage, after the test passed, on the outcome then reported, which commits it)'
                    ctrl = 'the C tokens of the stop-at-first flag (ok, the condition "not ok and" of the loop over pick) stop the loop after the first x that passes; emit after the test is the problem\'s own order (P)'
                else:
                    eff = 'extra'
                    timing = f'L = <{", ".join(ent)}>: entry 1 performed before commitment on a provisional outcome (x = 1) that the test x >= 2 then refuted in the same stage; entry 2 at commitment'
                    ctrl = 'none that avoids extra: the program keeps the problem\'s order, emit before the test; the C stop-at-first flag only stops after x = 2'
                e['observations'] = '; '.join([
                    f"answer x = {ans[0]}; observe binds x = {a['observe']['bindings'].get('x')}; facts of pick tried 2 of 3 (pick/1 1, pick/2 1, pick/3 0)",
                    'no alternatives held after the stage (the program ends), no suspended work, no conclusion withdrawn, no manual action',
                    'commitment, in the program\'s terms: the end of the query, when the loop over pick stops at the first x that passes and the answer is printed', ctrl] + obs_common)
                e['effects'] = eff
                e['effects_timing'] = timing
                e['rule'] = 'SPECIFICATION.md Outcomes 1 (an any-one query answered with one valid outcome is complete); P11 Effects; committed when reported (one stage)'
                e['note'] = note_rec
            else:
                v = P11_VALID[inst][st]
                commit_stage = 3 if inst == 'P11c' else 2
                if st == commit_stage:
                    committed_v = ans[0] if ans else None
                withdrawn = None
                if inst == 'P11c' and st == 2:
                    withdrawn = 'x = 1, reported at stage 1, is withdrawn: the program replaced it by x = 2 (the [bind x] changes; no explicit withdrawal is printed); the entry 1 already in L cannot be withdrawn'
                if inst == 'P11d' and st == 3:
                    withdrawn = 'x = 1, reported and committed at stage 2, is withdrawn: the program reports no solution; the committed entry 1 stays in L'
                if ans:
                    sem, rep = 'complete', 'explicit'
                    eqv = None
                else:
                    sem, rep = 'complete', 'explicit'
                    eqv = None
                e.update({'semantic': sem, 'representation': rep, 'simplification': None, 'identical_to_posed': None,
                          'residual_size': None, 'execution_state': exec_state, 'residual_equivalence': eqv})
                parts = [f'valid: {v}']
                if ans:
                    parts.append(f'answer x = {ans[0]}, valid')
                else:
                    parts.append('no answer; observe says "no solution": the empty outcome reported as empty (answer completeness: reported none, yes)')
                parts.append('observe: ' + re.sub(r'\s+', ' ', obs.replace('\n', ' | ')).strip())
                parts.append(f'alternatives held: {untried} untried fact(s) of pick kept for backtracking, beside the outcome held ([problem-alternatives x] counts both), resumed only when a later stage refutes the outcome; none live at once')
                parts.append('suspended work: the relations posed after pick are held as flags and re-tested on every later stage (procedure holds), no named suspended structure')
                parts.append(f'entries emitted in this stage: {em if em else "none"}')
                if withdrawn:
                    parts.append(withdrawn)
                parts.append('manual actions: none')
                if st == commit_stage:
                    parts.append(f'commitment, in the program\'s terms: the commit stage sets cv := xv and committed := true, so x = v is held as one more relation in holds; v = {committed_v}')
                e['observations'] = '; '.join(parts + obs_common)
                e['note'] = note_rec + ('' if untried == 0 else '; classed alternatives pending from the program\'s own report (untried facts held as backtracking alternatives, [held-as backtracking]); suspended is also arguable, since only later information resumes them')
                e['rule'] = 'SPECIFICATION.md Outcomes 1 (any-one query) and 3; P11 Commitment'
                if st == K:
                    ent = [x['entry'] for x in log]
                    if inst == 'P11c':
                        e['effects'] = 'extra'
                        e['effects_timing'] = f'L = <{", ".join(ent)}>: entry 1 at stage 1, before commitment, on the provisional outcome x = 1, refuted at stage 2 and never committed (extra); entry 2 at stage 2, before commitment, on the provisional outcome x = 2 that stage 3 then committed; nothing at commitment or after. No entry was duplicated by reposing'
                    else:
                        e['effects'] = 'extra'
                        e['effects_timing'] = f'L = <{", ".join(ent)}>: entry 1 at stage 1, before commitment, on the outcome x = 1 that stage 2 committed (exact so far); entries 2 and 3 at stage 3, after commitment, for outcomes never committed: the late contradiction x != 1 made the program resume pick\'s untried facts, emitting each before testing it against x = 1 and x != 1, so L holds effects of uncommitted outcomes (extra). What the program does with information that contradicts a committed effect: it searches past the commitment, performs new effects, finds none valid and reports no solution; the committed effect 1 is not withdrawn (it cannot be)'
                    e['rule'] += '; P11 Effects (judged on L when the problem ends)'
            outcomes.append(e)

# ------------------------------------------------------------------ P12
ACCEPT = {'P12a': lambda n: ['(r)', '(' + ', '.join(['l'] * n) + ')'],
          'P12b': lambda n: ['(r)'],
          'P12c': lambda n: ['(' + ', '.join(['r'] * n) + ')'],
          'P12d': lambda n: ['(' + ', '.join(['l'] * n) + ')']}
EXPECT_CAND = {  # depth-first, in the order written (problem file, reference positions)
    'P12a': lambda n: n + 1, 'P12b': lambda n: 2 ** n + 1, 'P12c': lambda n: 2 ** (n + 1) - 1, 'P12d': lambda n: n + 1}

for conf in ('report', 'x1', 'x1sim'):
    recs = records(conf, 'P12')
    for inst in sorted(recs):
        sub, nn, mode = inst.split('.')
        n = int(nn[1:])
        path, d = recs[inst]['behaviour']
        a, c = comp(d, 1)
        ans = [x['verbatim'] for x in c['queries'][0]['answers']]
        valid = sorted(ACCEPT[sub](n))
        e = {'configuration': conf, 'instance': inst, 'program': inst + EXT[conf], 'record': path, 'stage': 1,
             'reached': True, 'harness_fault': bool(d.get('harness_faults'))}
        if c['execution_state']['states'] == ['error']:
            e.update({'semantic': 'none reported', 'representation': None, 'simplification': None, 'identical_to_posed': None,
                      'residual_size': None, 'execution_state': ['error'], 'residual_equivalence': None,
                      'observations': 'error verbatim: ' + json.dumps(c['execution_state']['error_verbatim']) + '; stdout empty: no answer, no observe block (harness README 2.4: nothing can be observed after the stop); the stage was reached: the run was started and stage 1 posed, and the error came with no output at all; the only formal procedure in the program is found, the parameter through which choice passes each solution to accept (its first use is the first candidate, the empty sequence), so the error is most likely at the first call of the formal parameters of choice, in the query; the same text runs to completion in x1, so it is a fault of the x1sim compiler or of its reconstructed run-time with a procedure (or name) parameter, not of the problem or the meaning of the program; x1sim has no step count and no store measurement (unavailable, not 0); no manual action',
                      'rule': 'SPECIFICATION.md Outcomes 1 (nothing reported) and 3 (error, verbatim); AMENDMENTS 3.2 (posed and errs: an error of the stage, not not-reached)'})
            outcomes.append(e)
            continue
        got = [x.replace('s = ', '') for x in ans]
        want = ACCEPT[sub](n)
        if mode == 'all':
            ok = sorted(got) == sorted(want)
        else:
            ok = len(got) == 1 and got[0] in want
        assert ok, (conf, inst, got, want)
        cand = c.get('candidates_examined')
        exp = 2 ** (n + 1) - 1 if mode == 'all' else EXPECT_CAND[sub](n)
        assert cand == exp, (conf, inst, cand, exp)
        obs = a['observe']['raw']
        mm = re.search(r'at most\s*\+?\s*(\d+)\s*cells, with at most\s*\+?\s*(\d+)', obs)
        parts = [f"answers, in the order reported: {got}", f"candidates examined {cand} (expected {exp} for depth-first in the order written)"]
        so_far = re.findall(r'candidates examined so far:\s*\+?\s*(\d+)', a['stdout'])
        parts.append(f'candidates examined before each solution: {so_far}')
        if mode == 'all':
            parts.append('finished after the last solution: the strategy covered the whole space (finite, 2^(n+1) - 1 candidates)')
        else:
            parts.append('the search was left at the first solution (go to done), no alternatives kept')
        parts.append(f'partial sequence held, depth first: at most {mm.group(1)} cells, at most {mm.group(2)} alternatives (e = r) kept for backtracking, on ALGOL\'s own recursion; partial sequences held at the stage boundary 0 (the search has ended); none live at once')
        parts.append('unknown s represented as an index into the cell arrays, given its value by choice through the name parameter; no suspended work; no conclusion withdrawn; no manual action')
        cost = recs[inst].get('cost'); stor = recs[inst].get('storage')
        if cost:
            _, cc = comp(cost[1], 1)
            parts.append(f"cost run: steps {cc['steps']['stage']}, to first answer {cc['steps']['to_first_answer']}, between answers {cc['steps']['between_answers']}, repeated work {cc['steps']['repeated_work']}")
        if stor:
            s = comp(stor[1], 1)[0]['store']
            parts.append('storage run: peaks ' + json.dumps({k: peak(s, k) for k in ('frames', 'slots', 'array_elements', 'names', 'call_depth')}) + f", calls {peak(s, 'calls')}")
        if conf == 'x1sim':
            parts.append('x1sim: no step or store figure (unavailable)')
        e.update({'semantic': 'complete', 'representation': 'explicit', 'simplification': None, 'identical_to_posed': None,
                  'residual_size': None, 'execution_state': ['finished'], 'residual_equivalence': None,
                  'observations': '; '.join(parts),
                  'rule': 'SPECIFICATION.md Outcomes 1 (' + ('all valid outcomes reported, answer completeness ' + f'{len(got)}/{len(want)}, 0 invalid' if mode == 'all' else 'any-one query answered with one valid outcome') + ') and 3 (finished)'})
        outcomes.append(e)

# ------------------------------------------------------------------ modes
for prob in ('P11', 'P12'):
    for conf in ('report', 'x1'):
        recs = records(conf, prob)
        for inst, modes in sorted(recs.items()):
            _, b = modes['behaviour']
            for mname in ('cost', 'storage'):
                if mname not in modes:
                    continue
                mp, md = modes[mname]
                for st in range(1, len(b['stages']) + 1):
                    ab, cb = comp(b, st); am, cm = comp(md, st)
                    fb = ([x['verbatim'] for x in cb['queries'][0]['answers']], cb['execution_state']['states'], ab['observe']['raw'], [x['entry'] for x in ab.get('effects') or []])
                    fm = ([x['verbatim'] for x in cm['queries'][0]['answers']], cm['execution_state']['states'], am['observe']['raw'], [x['entry'] for x in am.get('effects') or []])
                    if fb != fm:
                        modediff.append({'configuration': conf, 'instance': inst, 'program': inst + EXT[conf], 'mode': mname,
                                         'record': mp, 'stage': st, 'behaviour': fb, 'this_mode': fm, 'note': 'differs'})
                checked_modes.append(mp)

# ------------------------------------------------------------------ expressibility
expr = []
for conf in ('report', 'x1', 'x1sim'):
    for sub in ('P11a', 'P11b'):
        expr.append({'configuration': conf, 'subproblem': sub, 'direction': None, 'expressibility': 'expressible',
                     'reason': 'one stage, posed by rerunning: pick by its facts in order, the test and emit in the order written, all P; the stop at the first outcome is C (the any-one query), no R token. ' + ('The emit before the test is kept, as the problem states it.' if sub == 'P11b' else '')})
    for sub in ('P11c', 'P11d'):
        expr.append({'configuration': conf, 'subproblem': sub, 'direction': None, 'expressibility': 'expressible with reformulation',
                     'reason': 'ALGOL 60 has no unknowns or alternatives of its own: to receive later stages into the same computation, the program holds the relations posed after pick as flags tested by holds, the position reached in pick\'s facts, and resumes the untried facts when a later stage refutes the outcome (procedure advance, the re-test after each stage): 87 R tokens by METRICS.md rule 19, written for this problem\'s own relations, so core configuration. The reformulation keeps the meaning on these inputs (the semantic results are complete at every stage); the effects are extra, which is a result of the order the problem gives (emit right after pick), not of the reformulation' + (' (P11d: after the commitment, the resumption performs effects for uncommitted outcomes)' if sub == 'P11d' else '')})
    for sub in ('P12a', 'P12b', 'P12c', 'P12d'):
        expr.append({'configuration': conf, 'subproblem': sub, 'direction': 'choice(n, s) with n known and s unknown (the direction the query uses)',
                     'expressibility': 'expressible with reformulation',
                     'reason': 'choice is transcribed by its two cases in order, the disjunction e = l or e = r as two statements in its order, s given its value through a name parameter (rule 3, P); accept by its facts and the equality of sequences (rules 6, 15, P). The conjunction "choice(n, s) and accept(s)" is carried by an argument the problem does not give, the procedure parameter found (accept passed to choice): 13 R tokens (rule 3). The depth-first order is ALGOL\'s own sequential execution and recursion, not a search written by hand, so no S (P12 Rules). C: the any-one exit (go to done), the answer mode and the cell reset (rule 16).' + (' In x1sim the same text errs at run time ("Unknown descriptor of formal procedure"), so the transcription is not demonstrated in that configuration; the judgement is from the program, which x1 runs to completion.' if conf == 'x1sim' else '')})

# ------------------------------------------------------------------ S
smech = []
for conf in ('report', 'x1', 'x1sim'):
    files = sorted(os.path.basename(p) for p in glob.glob(f'{ROOT}/programs/algol-60/{conf}/P1[12]*{EXT[conf]}'))
    for f in files:
        smech.append({'configuration': conf, 'program': f, 'mechanism': 'none', 'listed_at_phase_4': None, 'tokens': 0,
                      'note': 'no S tokens: S-mechanisms.md lists none for ALGOL 60, and the program supplies none (the P12 enumeration is the transcription of choice on the language\'s own recursion; the P11c/d holding is R by rule 19, written for this problem)'})

# ------------------------------------------------------------------ write
tokens = {k: [{kk: sp[kk] for kk in ('from', 'to', 'class', 'construct', 'rule')} for sp in v] for k, v in tok.items()}
out = {'tokens': tokens, 'outcomes': outcomes, 'mode_differences': modediff, 'expressibility': expr,
       'late_definition': [], 's_mechanisms': smech,
       'about': {'classifier': '1C-A', 'system': 'algol-60', 'batch': '1C', 'problems': ['P11', 'P12'],
                 'shared_texts': 'each x1 text is also the text of x1sim (TEXTS-1C-P11-P12.tsv); classed once under x1, since no token\'s class differs between the two (neither has an S mechanism, and the X1 procedures are the system\'s own in both). The 24 P12 files of each configuration are one text, classed under P12a.n12.all',
                 'mode_records_compared': len(checked_modes),
                 'late_definition': 'no P08 program in this batch'}}
with open(os.path.join(HERE, 'algol-60.json'), 'w') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print('outcomes', len(outcomes), 'mode records compared', len(checked_modes), 'differences', len(modediff), 'expr', len(expr), 's', len(smech))
