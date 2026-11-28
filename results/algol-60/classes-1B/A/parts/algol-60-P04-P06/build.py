import json, sys
sys.path.insert(0, '.')
import run
from collections import Counter

# ---- tokens: one entry per distinct text, under its first path (TEXTS-1B-P04-P06.tsv)
FIRST = {'report': 'alg', 'x1': 'a60'}
tokens = {}
for path, (toks, spans) in run.res.items():
    tokens[path] = spans
# coverage check
for path, (toks, spans) in run.res.items():
    cov = []
    for s in spans: cov.extend(range(s['from'], s['to'] + 1))
    assert cov == list(range(len(toks))), path

comp = json.load(open('compact.json'))
beh = [e for e in comp if e['mode'] == 'behaviour']

S_SPEC = 'SPECIFICATION.md, Outcomes'
A3 = 'AMENDMENTS.md 3'

def J(inst, stage, cfg, e):
    """Classifier A's judgement of one behaviour stage."""
    a = e['answers']; n = len(a)
    x1sim = cfg == 'x1sim'
    out = dict(reached=True, semantic=None, representation=None, simplification=None,
               identical_to_posed=None, residual_size=None, execution_state=list(e['states']),
               residual_equivalence=None, observations='', rule=S_SPEC)
    err = (e['err'] or '').strip()
    if inst == 'P04a':
        out.update(semantic='none reported', observations=(
            'x = 1 not reported: the first alternative, loop(x), recurses without end and the second is never tried. '
            'x is held unknown (Boolean xk false). No alternatives or suspended work reported by the program (the second '
            'alternative is held only implicitly, as the rest of the main program). '
            + ('Stopped by SIGKILL at ' + str(e['wall']) + ' s, below the 60 s safety limit (safety_limit.hit false), with no error text: recorded as error; '
               'unbounded recursion in the simulator is the likely cause, but the record does not say. ' if x1sim else
               'Budget at 10^6 steps; storage run peak call_depth about 333330 (report). ')
            + 'No manual actions.'),
            rule='SPECIFICATION.md Outcomes 1 (none reported) and 3; problems/04 Observations')
    elif inst == 'P04b':
        out.update(semantic='complete', representation='explicit', observations=(
            'x = 1 reported first (' + repr(a[0]) + '), then the second alternative loop(x) runs without end. x held as a value. '
            + ('Then the process was killed (SIGKILL) at ' + str(e['wall']) + ' s, below the safety limit, with no error text: error. ' if x1sim else
               'Then budget at 10^6 steps. ')
            + 'No alternatives or suspended work reported. No manual actions.'),
            rule='SPECIFICATION.md Outcomes 1 (the report denotes exactly the valid outcomes, x = 1) and 3')
    elif inst in ('P04c', 'P04d'):
        out.update(semantic='none reported', observations=(
            ('Valid outcome true; ' if inst == 'P04c' else 'Valid outcomes infinite (s = <>, <a>, ...); no finite representation given, no answer obtained; ')
            + 'alist-left calls alist(m) with m unknown before its second conjunct, so case 1 recurses without end and no answer is ever produced: not every solution would be reached given more steps. '
            + ('x1sim: ' + repr(err) + ' (error). ' if x1sim else 'Budget at 10^6 steps (stopped at line 66/55 in alist case 1); storage peak call_depth about 2*10^5. ')
            + 'Unknowns s, m as Boolean-and-integer pairs. No alternatives or suspended work reported. No manual actions.'),
            rule='SPECIFICATION.md Outcomes 1 and 3; METRICS.md answer completeness; problems/04 Observations')
    elif inst == 'P04e':
        if x1sim:
            out.update(semantic='none reported', observations=(
                'x1sim stopped with ' + repr(err) + ' before any answer (error): the reconstructed X1 run-time does not handle this program\'s procedure parameters; '
                'report and x1 give true and finish. No manual actions.'))
        else:
            out.update(semantic='complete', representation='explicit', observations=(
                'true reported once; the computation finishes (alist/1 applied 1, alist/2 applied 2). Cost run: 113 steps (report), 118 (x1); '
                'name_repeat_evaluations 13. No alternatives or suspended work. No manual actions.'))
    elif inst == 'P04f':
        if x1sim:
            out.update(semantic='partial', representation='explicit', observations=(
                'One answer, s = (), then ' + repr(err) + ' (error), the same fault as P04e in x1sim. The enumeration would reach every solution in report and x1; here it stops at the second. No manual actions.'),
                rule='SPECIFICATION.md Outcomes 1 (a nonempty proper subset of an infinite set) and 3')
        else:
            out.update(semantic='partial', representation='explicit', observations=(
                'Valid outcomes infinite; no finite representation given. 20 answers collected (cap), s = (), (a), (a, a), ... in order of length, and ' + str(e['nans_stdout'])
                + ' printed before the budget. Every solution would be reached given enough steps (alist-right with s unknown, body before head, enumerates by length). '
                'Alternatives are held for backtracking on the ALGOL call stack (continuations), not reported by the program. Budget at 10^6 steps. No manual actions.'),
                rule='SPECIFICATION.md Outcomes 1 (a nonempty proper subset of an infinite set) and 3; METRICS.md answer completeness')
    elif inst in ('P05a', 'P05c'):
        vals = {('P05a', 1): '{1,2,3}', ('P05a', 2): '{2,3}', ('P05a', 3): '{3}',
                ('P05c', 1): '{1,2,3}', ('P05c', 2): 'none', ('P05c', 3): 'none'}[(inst, stage)]
        alive = {'{1,2,3}': 3, '{2,3}': 2, '{3}': 1, 'none': 0}[vals]
        wd = ''
        if inst == 'P05a' and stage == 2: wd = 'x = 1, reported at stage 1, is withdrawn: shown only by its absence from the answers and from the values held. '
        if inst == 'P05a' and stage == 3: wd = 'x = 2, reported at stages 1-2, is withdrawn: shown only by its absence. '
        if inst == 'P05c' and stage == 2: wd = 'x = 1, 2, 3, reported at stage 1, are all withdrawn: shown by no answer and "no solution" in the observe block. '
        if inst == 'P05c' and stage == 3: wd = 'Stage 3 could be posed and was received into the same (re-created) computation; nothing further withdrawn. '
        out.update(semantic='complete', representation='explicit', observations=(
            f'Valid {vals}; answers {a}. ' + ('Empty outcome reported as no answers and "no solution" in observe (answer completeness: reported none, yes). ' if alive == 0 else '')
            + f'Every surviving value of x held at once (problem-defined alternatives x = {alive}); a value that fails a test is dropped, not kept for backtracking. '
            + 'No suspended work. ' + wd + 'No manual actions.'),
            rule='SPECIFICATION.md Outcomes 1-3; problems/05 Observations')
    elif inst == 'P05b':
        if stage == 1:
            out.update(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=True,
                       residual_size='1 relation (x > 1), 1 occurrence of x; the input: 1 relation, 1 occurrence',
                       residual_equivalence='equivalent: the held relation x > 1 (r1, c1 = 1), acted on at stage 2, denotes exactly every integer x > 1, the valid outcome (comparisons other than = and != hold only of integers, so no other value qualifies); checked by hand and by residual_check.py over -1000..1000',
                       observations=('The comparison on the unknown x is held as a residual (' + repr(a[0]) + '), not enumerated and not an error. '
                                     'x unrepresented beyond the held relation. Suspended: 1 held relation (the program\'s held-relations count). No alternatives. No manual actions.'),
                       rule='SPECIFICATION.md Outcomes 1, 2 (residual: state held and acted on later), simplification')
        else:
            out.update(semantic='complete', representation='explicit', observations=(
                'Valid {2,3}; answers ' + str(a) + '. pick gives three values; the held x > 1 is decided on each, 1 dropped. All held at once (x = 2). The stage-1 residual is released (held relations none). No manual actions.'))
    elif inst in ('P06a', 'P06c'):
        if stage == 1:
            out.update(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=True,
                       residual_size='1 relation (not (x = 1)), 1 occurrence of x; the input: 1 relation, 1 occurrence',
                       residual_equivalence='equivalent: the held negation not (x = 1), with x unknown and acted on at stage 2, denotes every value other than 1; it does not restrict x to integers in what it reports (checked by hand, and over -1000..1000 by residual_check.py)',
                       observations=('The negation is held as a condition, not decided at once (' + repr(a[0]) + '); the program never reports no solution while x is unknown. '
                                     'x unknown (xk false). Suspended: 1 held relation. No alternatives. No manual actions.'),
                       rule='SPECIFICATION.md Outcomes 1, 2 (residual), simplification; problems/06 Observations')
        elif inst == 'P06a':
            out.update(semantic='complete', representation='explicit', observations=(
                'x = 2 reported; the held negation decided once x is known (not-eq-examined 3 by the end of stage 2: examined again in each propagation pass). Same outcome as P06b. Nothing withdrawn. No manual actions.'))
        else:
            out.update(semantic='complete', representation='explicit', observations=(
                'Valid none: no answer, and "no solution" in observe (answer completeness: reported none, yes). The observe block still reads [bind x]1, the binding from x = 1, beside "no solution". '
                'The stage-1 residual is withdrawn by the contradiction. No manual actions.'),
                rule='SPECIFICATION.md Outcomes 1 (empty set reported as empty); see notes on the binding read by observe')
    elif inst == 'P06b':
        out.update(semantic='complete', representation='explicit', observations=(
            'x = 2 at both stages; at stage 2 the negation is decided at once, x being known. Same outcome as P06a. No suspended work. No manual actions.'))
    elif inst == 'P06d':
        out.update(semantic='complete', representation='explicit', observations=(
            'd = (1, 3) reported, finished. setdiff/1 1, /2 2, /3 2, mem/1 2, mem/2 13 (case 3 re-tests mem). No manual actions.'))
    elif inst == 'P06e1':
        out.update(semantic='complete', representation='explicit', observations='true reported once; p and k are known when the negation is decided. No manual actions.')
    elif inst == 'P06e2':
        out.update(semantic='complete', representation='explicit', observations='Valid false: no answer and "no solution" in observe (reported none, yes). p and k known when each negation is decided. No manual actions.')
    elif inst == 'P06e3':
        out.update(semantic='complete', representation='explicit', observations='p = brown reported once; student(p) and maths(k) give p and k before not takes(p, k) is decided. No manual actions.')
    if out['semantic'] == 'none reported':
        out['representation'] = None
    if 'error' in e['states'] and err:
        out['observations'] += ' error_verbatim: ' + err
    out['observations'] += f" [record: ended_by {e['ended']}, posed {e['posed']}/{e['reason']}]"
    return out

outcomes = []
for e in beh:
    cfg = e['cfg']
    prog = e['inst'] + ('.alg' if cfg == 'report' else '.a60')
    j = J(e['inst'], e['stage'], cfg, e)
    ent = dict(configuration=cfg, instance=e['inst'], program=prog, record=e['rec'], stage=e['stage'])
    ent.update(j)
    ent['harness_fault'] = False
    outcomes.append(ent)

# expressibility
expr = []
REASONS = {
    'P04a': ('expressible with reformulation', None, 'loop and the disjunction are transcribed (a recursive procedure; the alternatives in the order written), but each relation is a procedure passing each solution to a continuation found: an extra argument (R). Meaning kept on every input.'),
    'P04b': ('expressible with reformulation', None, 'as P04a.'),
    'P04c': ('expressible with reformulation', 'alist-left, s known', 'cases and conjuncts transcribed in the order written, as procedures with a success continuation (R), mode tests (R) and branches for directions not used (R); the infinite left recursion is the problem\'s own order, not a change of meaning.'),
    'P04d': ('expressible with reformulation', 'alist-left, s unknown', 'as P04c.'),
    'P04e': ('expressible with reformulation', 'alist-right, s known', 'as P04c; case 2 decides its head before its body, as written.'),
    'P04f': ('expressible with reformulation', 'alist-right, s unknown', 'as P04c, and case 2 calls its body alist(m) before deciding its head s = <a> ++ m, since a sequence cannot be built before its tail: one move (rule 4).'),
    'P05a': ('expressible with reformulation', None, 'pick\'s facts and the comparisons are P, but the comparisons on an unknown x are held until pick gives values by code written for these relations (rule 19: R, core).'),
    'P05b': ('expressible with reformulation', None, 'as P05a; here x > 1 is held over a whole stage.'),
    'P05c': ('expressible with reformulation', None, 'as P05a, with equations.'),
    'P06a': ('expressible with reformulation', None, 'not (x = c) and x = c are decided by evaluators (P), held and propagated by code for these relations (rule 19: R, core). The language negation is sound only because the holding waits for x.'),
    'P06b': ('expressible with reformulation', None, 'as P06a.'),
    'P06c': ('expressible with reformulation', None, 'as P06a (the same text).'),
    'P06d': ('expressible', 'setdiff(s1, s2, d): d from s1, s2; mem(e, s) both known', 'mode-faithful transcription (rule 3): setdiff as a function in the direction the query uses, mem as a Boolean procedure; no R tokens.'),
    'P06e1': ('expressible', 'nonmajor(p), p known', 'transcription over the closed-world facts, conjuncts in order; no R tokens.'),
    'P06e2': ('expressible', 'nonmajor(p), p known', 'as P06e1 (the same text).'),
    'P06e3': ('expressible', 'nonmajor(p), p unknown', 'transcription; student(p) enumerates its stated facts (rule 6), no R tokens.'),
}
for cfg in ('report', 'x1', 'x1sim'):
    for sp, (cls, d, why) in REASONS.items():
        r = why
        if cfg == 'x1sim' and sp in ('P04e', 'P04f'):
            r += ' (x1sim\'s run-time error "Unknown descriptor of formal argument" is a fault of the reconstructed run-time, not of expressibility.)'
        expr.append(dict(configuration=cfg, subproblem=sp, direction=d, expressibility=cls, reason=r))

s_mech = []
for cfg, ext in (('report', 'alg'), ('x1', 'a60'), ('x1sim', 'a60')):
    for inst in ['P04a','P04b','P04c','P04d','P04e','P04f','P05a','P05b','P05c','P06a','P06b','P06c','P06d','P06e1','P06e2','P06e3']:
        s_mech.append(dict(configuration=cfg, program=f'{inst}.{ext}', mechanism='none', listed_at_phase_4=None, tokens=0,
                           note='no S tokens: harnesses/algol-60/S-mechanisms.md lists none for any configuration, and the program supplies none of its own (its holding code in P05 and P06 is written for the problem\'s relations, R by rule 19; the continuation-passing search in P04 is R and C, not a general mechanism)'))

doc = dict(tokens=tokens, outcomes=outcomes, mode_differences=[], expressibility=expr, late_definition=[], s_mechanisms=s_mech)
json.dump(doc, open('algol-60.json', 'w'), indent=1, ensure_ascii=False)
# totals
tot = Counter(); per = {}
for p, spans in tokens.items():
    c = Counter()
    for s in spans: c[s['class']] += s['to'] - s['from'] + 1
    per[p] = dict(c); tot.update(c)
print(dict(tot), sum(tot.values()))
for p, c in per.items(): print(p, c)
print(Counter((o['semantic']) for o in outcomes), len(outcomes))
print(Counter(tuple(o['execution_state']) for o in outcomes))
