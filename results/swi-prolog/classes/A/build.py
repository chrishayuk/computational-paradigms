# Classifier A, swi-prolog, batch 1A: builds swi-prolog.json.
# Reads only the token files and the raw records. Run with python3 -I.
import csv, json, glob, os, re

REPO = '/Users/christopherhay/cp-roles/classifier-A'
OUT = '/Users/christopherhay/cp-roles/classes-A/swi-prolog'
TOK = REPO + '/results/swi-prolog/tokens'

# ---------------------------------------------------------------- tokens

CONSTANT_FACTS = {'z_value', 'conc_first', 's_value', 'prefix', 'r1_sum', 'r3_addend',
                  'r3_sum', 'conc_second', 'conc_whole', 'rev_first', 'rev_second'}
PROBLEM_DEFS = {'conc': 'conc/3, a case of the problem\'s definition of conc',
                'rev': 'rev/2, a case of the problem\'s definition of rev',
                'r1': 'R1 (u + v = k), the relation the problem names',
                'r2': 'R2 (w * u = v), the relation the problem names',
                'r3': 'R3 (u + k1 = k2), the relation the problem names'}
EVALUATORS = {'sum', 'product', 'sum_known', 'product_known', 'factor'}


def read_tokens(path):
    rows = list(csv.reader(open(path), delimiter='\t', quoting=csv.QUOTE_NONE))[1:]
    return [r[2] for r in rows]


def clauses(toks):
    out, s = [], 0
    for i, t in enumerate(toks):
        if t == '.':
            out.append((s, i)); s = i + 1
    assert s == len(toks), 'trailing tokens'
    return out


def split_top(toks, a, b):
    """split toks[a..b] (inclusive) at depth-0 commas; returns list of (start,end) where
    start is the comma before the goal (except the first)."""
    parts, depth, start = [], 0, a
    for i in range(a, b + 1):
        t = toks[i]
        if t in '([{': depth += 1
        elif t in ')]}': depth -= 1
        elif t == ',' and depth == 0:
            parts.append((start, i - 1)); start = i
    parts.append((start, b))
    return parts


def goal_name(toks, s, e):
    i = s + 1 if toks[s] == ',' else s
    return toks[i], i


def span(a, b, cls, construct, rule):
    return {'from': a, 'to': b, 'class': cls, 'construct': construct, 'rule': rule}


def classify_text(cfg_file, toks):
    spans = []
    for (s, e) in clauses(toks):
        head = toks[s]
        text = ' '.join(toks[s:e + 1])
        if head == ':-':
            d = toks[s + 1]
            if d == 'table':
                spans.append(span(s, e, 'C', 'directive ' + text, 'METRICS class C: a tabling declaration'))
            elif d == 'use_module':
                spans.append(span(s, e, 'P', 'directive ' + text,
                    'rule 12 and rule 1: the library that gives #= its meaning; without it the constraints '
                    'that state R1-R3 do not exist. Listed under external mechanisms (library(clpfd)). See notes'))
            elif d == 'set_prolog_flag':
                spans.append(span(s, e, 'C', 'directive ' + text,
                    'rule 11, by analogy: a flag declaration that chooses the reading (finite, by occurs check) '
                    'of P01c; listed. See notes'))
            else:
                raise ValueError(text)
            continue
        if head in CONSTANT_FACTS:
            spans.append(span(s, e, 'P', 'CONSTANTS block entry ' + text,
                'METRICS class P: the information of a stage (its constant)'))
            continue
        if head == 'unknowns':
            spans.append(span(s, e, 'H', 'unknowns/2 fact', 'class H: harness README section 12 (the whole unknowns/2 fact)'))
            continue
        if head == 'query':
            assert ':-' not in toks[s:e + 1]
            spans.append(span(s, e, 'H', 'query/2 clause (head only, no body)', 'class H: harness README section 12 (head of query/2)'))
            continue
        # clause with possible body
        try:
            neck = toks.index(':-', s, e + 1)
        except ValueError:
            neck = None
        if neck is None:
            assert head in PROBLEM_DEFS, text
            spans.append(span(s, e, 'P', 'fact ' + text + ': ' + PROBLEM_DEFS[head], 'METRICS class P: transcription of the problem\'s definition case (rule 3)'))
            continue
        if head == 'stage':
            spans.append(span(s, neck, 'H', 'stage/3 clause head with its :-', 'class H: harness README section 12 (stage/3 head)'))
            body_cls_default = ('P', 'stage body')
        elif head in PROBLEM_DEFS:
            spans.append(span(s, neck, 'P', 'clause head of ' + PROBLEM_DEFS[head], 'METRICS class P: transcription of the problem\'s definition (rule 3)'))
        elif head in EVALUATORS:
            spans.append(span(s, neck, 'P', 'clause head of %s/3, the primitive relation %s computed by Prolog arithmetic' % (head, '+' if 'sum' in head else '*'),
                'rule 8 and rule 19 (by analogy): computing one place of the primitive relation from the others is P in every direction; the clause head introduces that computation (rule 10)'))
        else:
            raise ValueError(text)
        # body
        parts = split_top(toks, neck + 1, e - 1)
        for (gs, ge) in parts:
            name, gi = goal_name(toks, gs, ge)
            gtext = ' '.join(toks[gi:ge + 1])
            if name == '!':
                spans.append(span(gs, ge, 'C', 'cut in a %s clause' % head, 'rule 2: a cut that commits to the clause is control (METRICS class C: cuts); separator by rule 20'))
            elif name == 'nonvar':
                spans.append(span(gs, ge, 'R', 'mode test %s in a %s clause' % (gtext, head),
                    'rule 19 (by analogy): the tests of which places are known are not the relation; '
                    'the primitive relation has no cases, so rule 2\'s head-test exemption does not apply; separator by rule 20. See notes'))
            elif name == 'when':
                # when ( ( cond ) , goal )
                assert toks[gi + 1] == '(' and toks[gi + 2] == '('
                depth = 0
                for j in range(gi + 1, ge + 1):
                    if toks[j] in '([{': depth += 1
                    elif toks[j] in ')]}': depth -= 1
                    if toks[j] == ',' and depth == 1:
                        comma = j; break
                assert toks[ge] == ')'
                spans.append(span(gs, comma - 1, 'C', 'when/2 call and its condition ' + ' '.join(toks[gi:comma]),
                    'METRICS class C: a coroutine call (when/2) and the condition it waits on; rule 10 for the goal inside it'))
                spans.append(span(comma, ge - 1, 'P', 'goal inside when/2: ' + ' '.join(toks[comma + 1:ge]),
                    'rule 10: the goal inside the coroutine call is classed on its own (the relation computed once known); separator by rule 20'))
                spans.append(span(ge, ge, 'C', 'closing parenthesis of the when/2 call', 'rule 10: the tokens that close a construct take its class'))
            elif name == 'memberchk':
                spans.append(span(gs, ge, 'P', 'goal ' + gtext + ': reads the stage\'s constant from the list the harness passes',
                    'METRICS class P (the information of the stage); rule 9 and rule 12: memberchk/2 of library(lists), listed under external mechanisms; separator by rule 20. See notes'))
            else:
                if head == 'stage':
                    c = 'goal %s: the stage\'s information' % gtext
                    r = 'METRICS class P: the information of the stage; separator by rule 20'
                elif head in PROBLEM_DEFS:
                    c = 'goal %s in the body of %s' % (gtext, PROBLEM_DEFS[head])
                    r = 'METRICS class P: transcription of the problem\'s definition (rule 3); separator by rule 20'
                else:
                    c = 'goal %s in a %s clause' % (gtext, head)
                    if name == 'factor':
                        r = 'rule 19 (by analogy): computing the unknown factor of w * u = v from the other two places is P; separator by rule 20'
                    else:
                        r = 'rule 8 and rule 19 (by analogy): the evaluation or test of the primitive relation is P in every direction; separator by rule 20'
                spans.append(span(gs, ge, 'P', c, r))
        # the clause's full stop
        last = spans[-1]
        if last['class'] == 'P' and last['to'] == e - 1:
            last['to'] = e
        else:
            spans.append(span(e, e, 'P', 'full stop ending the %s clause' % head, 'rule 10: the clause is the definition of the relation (P); its terminator takes that class'))
    return spans


texts = list(csv.reader(open(TOK + '/TEXTS.tsv'), delimiter='\t'))[1:]
tokens_out = {}
coverage = {}
for row in texts:
    first = row[0]
    toks = read_tokens('%s/%s.tokens.tsv' % (TOK, first))
    sp = classify_text(first, toks)
    # coverage check
    cov = [0] * len(toks)
    for x in sp:
        for i in range(x['from'], x['to'] + 1):
            cov[i] += 1
    assert all(c == 1 for c in cov), (first, [i for i, c in enumerate(cov) if c != 1])
    assert [x['from'] for x in sp] == sorted(x['from'] for x in sp)
    tokens_out[first] = sp
    coverage[first] = len(toks)
    # the other paths must have identical token text
    for other in (row[1].split() if len(row) > 1 else []):
        assert read_tokens('%s/%s.tokens.tsv' % (TOK, other)) == toks, other

# totals
totals = {}
for k, sp in tokens_out.items():
    t = {'P': 0, 'C': 0, 'R': 0, 'S': 0, 'H': 0}
    for x in sp:
        t[x['class']] += x['to'] - x['from'] + 1
    totals[k] = t

# ---------------------------------------------------------------- outcomes

ORDERS = {'P02a': ['R1', 'R2', 'R3'], 'P02c': None}
for o in ['R1R2R3', 'R1R3R2', 'R2R1R3', 'R2R3R1', 'R3R1R2', 'R3R2R1']:
    ORDERS['P02b.' + o] = [o[0:2], o[2:4], o[4:6]]

P02_VALID = {
    frozenset(['R1']): 'u + v = 16, w free (infinite)',
    frozenset(['R2']): 'v = w * u (infinite)',
    frozenset(['R3']): 'u = 2; v and w free (infinite)',
    frozenset(['R1', 'R2']): 'the ten triples (1,15,15), (2,14,7), (4,12,3), (8,8,1), (16,0,0), (-1,17,-17), (-2,18,-9), (-4,20,-5), (-8,24,-3), (-16,32,-2)',
    frozenset(['R1', 'R3']): 'u = 2, v = 14; w free (infinite)',
    frozenset(['R2', 'R3']): 'u = 2, v = 2w, for every integer w (infinite)',
    frozenset(['R1', 'R2', 'R3']): 'u = 2, v = 14, w = 7',
}
INPUT_SIZE = {'R1': (1, 2), 'R2': (1, 3), 'R3': (1, 1)}  # relations, occurrences of unknowns


def input_size(rels):
    r = sum(INPUT_SIZE[x][0] for x in rels); o = sum(INPUT_SIZE[x][1] for x in rels)
    return '%d relation(s), %d occurrence(s) of unknowns (%s)' % (r, o, ', '.join(sorted(rels)))


def norm(s):
    return re.sub(r'\s+', ' ', (s or '')).strip()


def rels_so_far(inst, stage):
    if inst == 'P02c':
        return ['R1', 'R2', 'R3']
    return ORDERS[inst][:stage]


def judge_p02(cfg, inst, stage, c, a, obs):
    rels = rels_so_far(inst, stage)
    key = frozenset(rels)
    valid = P02_VALID[key]
    ans = [norm(x['verbatim']) for x in c['queries'][0]['answers']]
    states = c['execution_state']['states']
    o = norm(obs)
    J = dict(semantic=None, representation=None, simplification=None, identical_to_posed=None,
             residual_size=None, residual_equivalence=None)
    base_rule = 'SPECIFICATION Outcomes 1-3; valid outcomes from problems/02-late-information.md (relations so far: %s)' % ', '.join(rels)
    if 'error' in states:
        if o in ('true', ''):
            J.update(semantic='none reported', representation=None,
                     residual_equivalence='nothing is held: observe() read "true" at the exception (no binding, no residual goal); plain Prolog cannot hold the relation, and is/2 raised its instantiation error')
        else:
            J.update(semantic='unsound', representation='solved form',
                     residual_equivalence=('at the exception observe() read the binding %s and no relation is held; by SPECIFICATION 1 ("reported" includes a binding observe() reads at the end of the stage) '
                                           'the report is that binding with the other unknowns free, which admits assignments outside the valid outcomes (%s). '
                                           'Read as an aborted derivation instead, it would be none reported (see notes)') % (o, valid))
        return J, base_rule
    text = ans[-1] if ans else ''
    # final explicit
    if text.rstrip('.').strip() == 'U = 2, V = 14, W = 7':
        J.update(semantic='complete', representation='explicit', residual_equivalence='u = 2, v = 14, w = 7 is the valid outcome exactly')
        return J, base_rule
    if text.rstrip('.').strip() == 'U = 2':
        assert key == frozenset(['R3'])
        J.update(semantic='complete', representation='solved form',
                 residual_equivalence='U = 2 with V and W free (no residual goal, 0 attributed variables) is "u = 2; v and w free"')
        return J, base_rule
    if text.rstrip('.').strip() == 'U = 2, V = 14':
        assert key == frozenset(['R1', 'R3'])
        J.update(semantic='complete', representation='solved form',
                 residual_equivalence='U = 2, V = 14, W free is the valid outcome exactly')
        return J, base_rule
    t = text.rstrip('.').strip()
    if cfg in ('constraints', 'session'):
        if key == frozenset(['R1']):
            assert t == 'U+V#=16', t
            J.update(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=True,
                     residual_size='1 relation, 2 occurrences of unknowns; input ' + input_size(rels),
                     residual_equivalence='the clpfd constraint U+V#=16 over the unbounded integers (no domain imposed) denotes exactly u + v = 16 with w free; an infinite set has no smaller representation')
        elif key == frozenset(['R2']):
            assert t == 'W*U#=V', t
            J.update(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=True,
                     residual_size='1 relation, 3 occurrences of unknowns; input ' + input_size(rels),
                     residual_equivalence='W*U#=V over the unbounded integers denotes exactly v = w * u')
        elif key == frozenset(['R1', 'R2']):
            assert t in ('U+V#=16, W*U#=V', 'W*U#=V, U+V#=16'), t
            J.update(semantic='complete', representation='residual', simplification='reducible', identical_to_posed=True,
                     residual_size='2 relations, 5 occurrences of unknowns; input ' + input_size(rels),
                     residual_equivalence='U+V#=16 and W*U#=V over the integers: u(w+1) = 16, so u divides 16, giving exactly the ten triples (checked by check_p02.py over a box that contains every solution). '
                                          'Equivalent, but the explicit ten triples have no relation left to decide, so the residual is reducible (the solver does not split on the divisors without labeling)')
        elif key == frozenset(['R2', 'R3']):
            assert t == 'U = 2, W*2#=V', t
            J.update(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=False,
                     residual_size='U = 2 bound, 1 relation (w * 2 = v), 2 occurrences of unknowns; input ' + input_size(rels),
                     residual_equivalence='U = 2 and W*2#=V denote u = 2, v = 2w for every integer w: exactly the valid outcome; R3 has been solved and substituted into R2')
        else:
            raise ValueError((cfg, inst, stage, t))
        return J, base_rule
    if cfg == 'coroutines':
        if key == frozenset(['R1']):
            assert t.startswith('when(') and 'sum_known(U, V, 16)' in t and t.count('when(') == 1, t
            J.update(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=True,
                     residual_size='1 relation (a when/2 goal holding sum_known(U, V, 16)), 2 occurrences of unknowns; input ' + input_size(rels),
                     residual_equivalence='the held goal computes u + v = 16 over the integers as soon as one of u, v is known; as a condition it denotes u + v = 16 with w free. Its wait condition is control, not a relation')
        elif key == frozenset(['R2']):
            assert t.startswith('when(') and 'product_known(W, U, V)' in t and t.count('when(') == 1, t
            J.update(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=True,
                     residual_size='1 relation (a when/2 goal holding product_known(W, U, V)), 3 occurrences of unknowns; input ' + input_size(rels),
                     residual_equivalence='the held goal is w * u = v over the integers (factor/3 handles a zero factor), denoting v = w * u')
        elif key == frozenset(['R1', 'R2']):
            assert t.count('when(') == 2 and 'sum_known(U, V, 16)' in t and 'product_known(W, U, V)' in t, t
            J.update(semantic='complete', representation='residual', simplification='reducible', identical_to_posed=True,
                     residual_size='2 relations (two when/2 goals), 5 occurrences of unknowns; input ' + input_size(rels),
                     residual_equivalence='u + v = 16 and w * u = v, both held and neither woken: over the integers exactly the ten triples (check_p02.py). Equivalent; reducible, since the ten explicit triples leave no relation to decide')
        elif key == frozenset(['R2', 'R3']):
            assert t.startswith('U = 2, when(') and 'product_known(W, 2, V)' in t, t
            J.update(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=False,
                     residual_size='U = 2 bound, 1 relation (w * 2 = v, held as a when/2 goal), 2 occurrences of unknowns; input ' + input_size(rels),
                     residual_equivalence='U = 2 and the held w * 2 = v denote u = 2, v = 2w for every integer w, the valid outcome. The wait condition is not simplified (it still tests nonvar(2) or repeats a disjunct), which is control, not a relation left to decide')
        else:
            raise ValueError((cfg, inst, stage, t))
        return J, base_rule
    raise ValueError((cfg, inst, stage, t, states))


def judge(cfg, inst, prog, stage, c, a):
    obs = a['observe'].get('raw')
    ans = [norm(x['verbatim']) for x in c['queries'][0]['answers']]
    states = c['execution_state']['states']
    J = dict(semantic=None, representation=None, simplification=None, identical_to_posed=None,
             residual_size=None, residual_equivalence=None)
    rule = 'SPECIFICATION Outcomes 1-3; valid outcomes from the problem file'
    if inst == 'P01a':
        rule = 'SPECIFICATION Outcomes 1-3; problems/01-unknown-equality.md P01a'
        t = ans[0].rstrip('.').strip()
        if stage == 1:
            assert t == 'X = Y'
            J.update(semantic='complete', representation='solved form', residual_equivalence='X and Y are one shared variable and Z is free: every assignment with x = y, z free')
        elif stage == 2:
            assert t == 'X = Y, Y = Z'
            J.update(semantic='complete', representation='solved form', residual_equivalence='X, Y, Z are one shared variable: every assignment with x = y = z')
        else:
            assert t == 'X = Y, Y = Z, Z = 2'
            J.update(semantic='complete', representation='explicit', residual_equivalence='x = y = z = 2 exactly')
    elif inst == 'P01b':
        rule = 'SPECIFICATION Outcomes 1-3; problems/01-unknown-equality.md P01b'
        t = ans[0].rstrip('.').strip()
        if stage == 1:
            assert t == 'T = [1, 2|S]'
            J.update(semantic='complete', representation='solved form',
                     residual_equivalence='T is bound to [1, 2|S], the term <1,2> ++ s, with S free; no relation remains. The Prolog variable S is not restricted to lists, but <1,2> ++ s is only defined for a sequence s, so the solved form denotes t = <1,2> ++ s for every sequence s (see notes)')
        else:
            assert t == 'S = [3], T = [1, 2, 3]'
            J.update(semantic='complete', representation='explicit', residual_equivalence='s = <3>, t = <1,2,3> exactly')
    elif inst == 'P01c':
        rule = 'SPECIFICATION Outcomes 1-3 and Conventions (two readings); problems/01-unknown-equality.md P01c'
        o = norm(obs)
        if ans and ans[0].rstrip('.').strip() == 'X = [1|X]' or ('error' in states and o == 'X = [1|X]'):
            J.update(semantic='complete (rational reading); unsound (finite reading)', representation='cyclic',
                     semantic_by_reading={'finite': 'unsound', 'rational': 'complete'},
                     residual_equivalence='X = [1|X] is the rational tree <1,1,1,...>, the one rational solution; under the finite reading there is none, so it is an invalid outcome there')
            if 'error' in states:
                J['residual_equivalence'] += ('. Here no answer was delivered: tabling raised a type error (a cyclic answer cannot be tabled), and the cyclic binding is the one observe() read in the exception hook, which SPECIFICATION 1 counts as reported. '
                                              'If bindings read at an exception were not counted, the result would be none reported under both readings (see notes)')
        elif not ans and 'finished' in states:
            J.update(semantic='complete (finite reading); unsound (rational reading)', representation='explicit',
                     semantic_by_reading={'finite': 'complete', 'rational': 'unsound'},
                     residual_equivalence='with occurs_check true the unification fails and the query reports false (no solution): exactly the finite reading\'s empty set, and a report of none where the rational reading has one')
        else:
            raise ValueError((cfg, inst, prog, ans, states, o))
    elif inst.startswith('P02'):
        J2, rule = judge_p02(cfg, inst, stage, c, a, obs)
        J.update(J2)
    elif inst.startswith('P03'):
        rule = 'SPECIFICATION Outcomes 1-3; problems/03-reversible-relations.md'
        expect = {'P03a': ['C = [1, 2, 3]'], 'P03b': ['A = [], B = [1, 2]', 'A = [1], B = [2]', 'A = [1, 2], B = []'],
                  'P03c': ['B = [2, 3]'], 'P03d': ['A = [1, 2]'], 'P03e': ['B = [3, 2, 1]'], 'P03f': ['A = [3, 2, 1]']}[inst]
        got = [x.rstrip('.').strip() for x in ans]
        if got == expect:
            J.update(semantic='complete', representation='explicit',
                     residual_equivalence='every valid outcome is reported (%d of %d), none invalid, in the order %s' % (len(got), len(expect), '; '.join(got)))
            if 'budget' in states:
                J['residual_equivalence'] += ('. After the answer the request for another ran to the budget; at the budget observe() read A bound to a list of fresh variables (the derivation then under way). '
                                              'problems/03-reversible-relations.md says a system that reports the one solution and then runs out of budget is complete with budget, and that is followed here (see notes)')
        elif not got and 'error' in states:
            J.update(semantic='none reported', representation=None,
                     residual_equivalence='no answer; tabling raised a resource error (private_table_space) and observe() read nothing')
        else:
            raise ValueError((cfg, inst, got, states))
    return J, rule


def storage_alts(cfg, inst, prog):
    out = {}
    for f in glob.glob('%s/results/swi-prolog/%s/%s/raw/%s.storage.*.json' % (REPO, cfg, inst[:3], inst)):
        r = json.load(open(f))
        if os.path.basename(r['run']['program']['path']) != prog:
            continue
        for st in r['stages']:
            c = st['attempts'][-1]['computations'][0]
            out[st['stage']] = dict(at_answers=[x.get('alternatives_at') for x in c['queries'][0]['answers']],
                                    at_boundary=c['alternatives'].get('at_boundary'), at_budget=c['alternatives'].get('at_budget'),
                                    by_type=c['alternatives'].get('by_type'), record=os.path.relpath(f, REPO))
    return out


def unknown_repr(cfg, inst, stage, c, a):
    o = norm(a['observe'].get('raw'))
    if inst == 'P01a':
        return {1: 'x and y are one shared Prolog variable (aliasing by unification), z an unbound variable', 2: 'x, y and z are one shared variable', 3: 'none remain unknown: the value 2 reached all three through the one shared variable'}[stage]
    if inst == 'P01b':
        return {1: 's is an unbound variable that is the tail of t\'s list [1, 2|S]: the relation is held as one shared unknown inside a structure, not as a recorded equation', 2: 'none remain unknown: binding S fills the tail of T'}[stage]
    if inst == 'P01c':
        return 'x is bound to a cyclic term (rational tree) X = [1|X]' if 'X = [1|X]' in o else 'no binding: the unification failed (occurs check)'
    if inst.startswith('P03'):
        return 'none remain unknown in the answers'
    if 'when(' in o:
        return 'unknowns still unknown are unbound variables carrying when/2 attributes (the held goals), as shown: ' + o
    if '#=' in o:
        return 'unknowns still unknown are clpfd attributed variables (no finite domain imposed), with the residual constraints shown: ' + o
    if o in ('', 'true'):
        return 'all unknowns unbound plain variables; nothing held'
    return 'bindings ' + o + '; any unknown not shown is an unbound variable'


outcomes = []
records = sorted(glob.glob(REPO + '/results/swi-prolog/*/P0?/raw/*.json'))
log = [l.rstrip('\n').split('\t') for l in open(REPO + '/results/swi-prolog/batch-log.tsv')]
behaviour_index = {}
for f in records:
    r = json.load(open(f))
    run = r['run']
    if run['mode'] != 'behaviour':
        continue
    cfg, inst = run['configuration'], run['instance']
    prog = os.path.basename(run['program']['path'])
    salts = storage_alts(cfg, inst, prog)
    for st in r['stages']:
        assert len(st['attempts']) == 1
        a = st['attempts'][0]
        c = a['computations'][0]
        assert len(a['computations']) == 1
        k = st['stage']
        steps = c['steps']
        rcs = steps.get('restart_cost_source') or ''
        base = dict(configuration=cfg, instance=inst, program=prog, record=os.path.relpath(f, REPO), stage=k)
        if 'before stage %d was posed' % k in rcs:
            # never reached: the replay of an earlier stage raised the error again
            m = re.search(r'during stage (\d+)', rcs)
            stopped = int(m.group(1))
            ent = dict(base, reached=False, semantic='not reached', representation=None, simplification=None,
                       identical_to_posed=None, residual_size=None, execution_state=None,
                       residual_equivalence=None,
                       observations=('not reached (AMENDMENTS 3.2): stage %d was posed by reposing after the error, and the replay of stage %d raised the same error, %s, before stage %d was posed. '
                                     'The record files this under execution_state %s, and its restart_cost_source says the replay was "stopped by budget", which is wrong: budget_exhausted is false and the state is error (a wording fault of the harness). '
                                     'Restart cost %s inferences, read when the replay stopped. Not a failure of stage %d itself.')
                                    % (k, stopped, norm(c['execution_state']['error_verbatim']).split(' % term')[0], k, c['execution_state']['states'], steps.get('restart_cost'), k),
                       rule='AMENDMENTS 3.2: a stage never reached is not reached, with what stopped the run')
            outcomes.append(ent)
            continue
        J, rule = judge(cfg, inst, prog, k, c, a)
        susp = c['suspended']
        es = list(c['execution_state']['states'])
        obsparts = []
        obsparts.append('reported (verbatim answers): %s; ended_by %s, collected on %s' % (
            [x['verbatim'] for x in c['queries'][0]['answers']] or 'none', c['queries'][0]['ended_by'], c['queries'][0]['collected_on']))
        obsparts.append('observe(): %r (%s)' % (norm(a['observe'].get('raw'))[:300], a['observe'].get('taken_on')))
        obsparts.append('unknowns: ' + unknown_repr(cfg, inst, k, c, a))
        sa = salts.get(k)
        if sa:
            obsparts.append('alternatives (storage run %s): retained choicepoints at answers %s, at boundary %s, at budget %s; held for backtracking, not live at once'
                            % (sa['record'], sa['at_answers'], sa['at_boundary'] if sa['at_boundary'] is not None else 'unavailable', sa['at_budget'] if sa['at_budget'] is not None else 'unavailable'))
        else:
            obsparts.append('alternatives: unavailable (no storage reading)')
        if susp.get('at_boundary') is None:
            obsparts.append('suspended work: unavailable')
        else:
            obsparts.append('suspended work: %s attributed variable(s) reachable from the unknowns, %s projected residual goal(s)%s' % (
                susp['at_boundary'], (susp.get('items') or {}).get('residual_goals', 'unavailable'),
                ' (the held when/2 or clpfd goals)' if susp['at_boundary'] else ''))
        if a.get('notes'):
            obsparts.append('incremental computation (session): ' + '; '.join(a['notes']))
        if c['execution_state'].get('error_verbatim'):
            obsparts.append('error verbatim: ' + norm(c['execution_state']['error_verbatim']))
        obsparts.append('steps (behaviour run): to_end %s, restated %s, restart_cost %s' % (steps.get('to_end'), steps.get('restated'), steps.get('restart_cost')))
        obsparts.append('posed: %s (%s)' % (a['posed']['how'], a['posed']['reason']))
        obsparts.append('conclusion withdrawn: none (every earlier report still holds of the information so far)')
        obsparts.append('manual actions: %s' % (a['manual_actions'] or 'none'))
        ent = dict(base, reached=True, semantic=J['semantic'], representation=J['representation'],
                   simplification=J['simplification'], identical_to_posed=J['identical_to_posed'],
                   residual_size=J['residual_size'], execution_state=es,
                   residual_equivalence=J['residual_equivalence'], observations='. '.join(obsparts), rule=rule)
        if 'semantic_by_reading' in J:
            ent['semantic_by_reading'] = J['semantic_by_reading']
        outcomes.append(ent)
        behaviour_index[(cfg, inst, prog, k)] = ent

# every behaviour run in the log has a record
for l in log:
    t, cfg, inst, prog, mode = l[:5]
    if mode != 'behaviour':
        continue
    assert any(o['configuration'] == cfg and o['instance'] == inst and o['program'] == prog for o in outcomes), l

# ---------------------------------------------------------------- mode differences

def norm_err(s):
    return re.sub(r'_\d+', '_G', s or '')

mode_diffs = []
for f in records:
    r = json.load(open(f))
    run = r['run']
    if run['mode'] == 'behaviour':
        continue
    cfg, inst = run['configuration'], run['instance']
    prog = os.path.basename(run['program']['path'])
    bf = [o for o in outcomes if (o['configuration'], o['instance'], o['program']) == (cfg, inst, prog)]
    for st in r['stages']:
        a = st['attempts'][0]; c = a['computations'][0]; k = st['stage']
        b = [o for o in bf if o['stage'] == k][0]
        brec = json.load(open(REPO + '/' + b['record']))
        bc = brec['stages'][k - 1]['attempts'][0]['computations'][0]
        same_answers = [x['verbatim'] for x in c['queries'][0]['answers']] == [x['verbatim'] for x in bc['queries'][0]['answers']]
        same_state = c['execution_state']['states'] == bc['execution_state']['states']
        same_err = norm_err(c['execution_state'].get('error_verbatim')) == norm_err(bc['execution_state'].get('error_verbatim'))
        same_obs = norm_err(a['observe'].get('raw')) == norm_err(brec['stages'][k - 1]['attempts'][0]['observe'].get('raw'))
        if same_answers and same_state and same_err and same_obs:
            continue
        assert same_answers, f
        this = dict(semantic=b['semantic'], representation=b['representation'], execution_state=c['execution_state']['states'],
                    error_verbatim=c['execution_state'].get('error_verbatim'), observe=a['observe'].get('raw'))
        note = ('Same answer as the behaviour run (%s), so the semantic result agrees (complete, explicit). The execution state differs: the storage record says error, '
                'with "HARNESS FAULT: no end event for the computation"; its harness_faults entry shows that the harness could not parse its own at_exception event, '
                'which reads why "budget" at 1000009 steps, so the run did reach the budget as the behaviour run did, and observe() is empty only because the event was lost. '
                'A fault of the instrumentation (PROTOCOL, modes), not a result of the system; the storage figures of this stage (store, choicepoints at budget) are unavailable, not 0 (AMENDMENTS 3.1)') % [x['verbatim'] for x in c['queries'][0]['answers']]
        mode_diffs.append(dict(configuration=cfg, instance=inst, program=prog, mode=run['mode'], record=os.path.relpath(f, REPO), stage=k,
                               behaviour=dict(semantic=b['semantic'], representation=b['representation'], execution_state=b['execution_state'], record=b['record']),
                               this_mode=dict(semantic=b['semantic'], representation=b['representation'], execution_state=c['execution_state']['states'], error_verbatim=c['execution_state'].get('error_verbatim'), my_reading='budget: the recorded error is a harness fault, not the system\'s'),
                               note=note))

# ---------------------------------------------------------------- expressibility

CFGS = ['plain', 'tabling', 'coroutines', 'constraints', 'session']
expr = []
for cfg in CFGS:
    occurs = ' The occurs-check variant sets occurs_check true by a directive (C), choosing the finite reading.'
    expr.append(dict(configuration=cfg, subproblem='P01a', direction=None, expressibility='expressible',
                     reason='each stage is a unification =/2 (P), with the constant read by memberchk/2; no R tokens.'))
    expr.append(dict(configuration=cfg, subproblem='P01b', direction='conc(+, -, -): a known, b and c unknown',
                     reason='conc/3 is transcribed by its two cases (P) and called with the problem\'s arguments; no R tokens.' + (' The table directive is C.' if cfg == 'tabling' else ''),
                     expressibility='expressible'))
    expr.append(dict(configuration=cfg, subproblem='P01c', direction='conc(+, x, x): x = <1> ++ x',
                     expressibility='expressible',
                     reason='x = <1> ++ x is written conc(P, X, X) with the problem\'s conc (P); no R tokens. Unification without occurs check gives the rational reading, with it the finite reading.' + occurs +
                            (' In tabling the transcription runs but tabling cannot store the cyclic answer (type error): an outcome, not a matter of expressibility.' if cfg == 'tabling' else '')))
    for sub in ['P02a', 'P02b', 'P02c']:
        insts = [sub] if sub != 'P02b' else ['P02b.' + o for o in ['R1R2R3', 'R1R3R2', 'R2R1R3', 'R2R3R1', 'R3R1R2', 'R3R2R1']]
        for inst in insts:
            direction = None if sub != 'P02b' else 'order ' + inst.split('.')[1]
            if cfg in ('constraints', 'session'):
                e, why = 'expressible', ('each relation is one clpfd constraint (#=) over the unbounded integers, no domain imposed and no labeling (P); no R tokens. '
                                         'The solver holds what it cannot decide. library(clpfd) is an external mechanism.' + (' The session configuration\'s S mechanism (session-wait.pl) is not used by this program.' if cfg == 'session' else ''))
            elif cfg == 'coroutines':
                e, why = 'expressible with reformulation', ('the primitive relations are written as is/2 evaluations (P) behind mode tests nonvar/1 (R, 26 tokens per text, in sum_known/3 and product_known/3) and cuts (C), '
                                                            'each delayed by when/2 (C) until two places are known. That keeps the relation\'s meaning on every input the stages and other constants give: '
                                                            'it computes the third place, tests a fully known relation, or waits; factor/3 handles a zero factor. No supporting code.')
            else:
                order = ORDERS.get(inst) or ['R1', 'R2', 'R3']
                if inst == 'P02b.R3R1R2':
                    e, why = 'expressible with reformulation', ('in this order every relation arrives with at least two places known (u from R3, then v from R1, then w from R2), so the mode-dispatching evaluation '
                                                                '(is/2 as P, nonvar/1 tests as R, cuts as C) keeps the meaning for any constants (factor/3 handles u = 0). The R tokens are the mode tests.')
                else:
                    e, why = 'not expressible', ('plain Prolog cannot hold a relation with fewer than two known places: the program\'s reformulation (is/2 behind nonvar/1 mode tests, R) raises an instantiation error there, '
                                                 'or, for R2 first, binds u = 0 by factor/3\'s head before erring. In this %s a relation arrives that way, so the only reformulation written changes the meaning (an error in place of the valid outcomes). '
                                                 'Holding the relations would need code that holds them until their values arrive (rule 19: R if written for these relations, S if general); none is written, and I do not judge that such an R layer is impossible, only that these programs show none.'
                                                 % ('order' if sub == 'P02b' else 'sub-problem'))
                    if cfg == 'tabling':
                        why += ' tabling shares plain\'s text; tabling adds nothing here.'
            expr.append(dict(configuration=cfg, subproblem=sub if sub != 'P02b' else 'P02b', direction=direction, expressibility=e, reason=why))
    dirs = {'P03a': 'conc(+, +, -)', 'P03b': 'conc(-, -, +): splitting', 'P03c': 'conc(+, -, +)', 'P03d': 'conc(-, +, +)', 'P03e': 'rev(+, -)', 'P03f': 'rev(-, +)'}
    for sub, d in dirs.items():
        why = 'the one transcription of conc' + (' and rev' if sub in ('P03e', 'P03f') else '') + ' (P), by its cases in the problem\'s order, serves this direction; no R tokens.'
        if cfg == 'tabling':
            why += ' The table directive is C.'
        if sub == 'P03f':
            why += (' It reports the one solution and then runs to the budget looking for more (as the problem file anticipates).' if cfg != 'tabling'
                    else ' Under tabling the same transcription ends in a resource error (private_table_space) before any answer: an outcome of the run, not a matter of expressibility.')
        expr.append(dict(configuration=cfg, subproblem=sub, direction=d, expressibility='expressible', reason=why))

res = dict(tokens=tokens_out, outcomes=outcomes, mode_differences=mode_diffs, expressibility=expr)
json.dump(res, open(OUT + '/swi-prolog.json', 'w'), indent=1, ensure_ascii=False)
json.dump(totals, open(OUT + '/token-totals.json', 'w'), indent=1)
print('texts', len(tokens_out), 'tokens', sum(coverage.values()))
gt = {'P': 0, 'C': 0, 'R': 0, 'S': 0, 'H': 0}
for t in totals.values():
    for k in gt: gt[k] += t[k]
print('totals over distinct texts', gt)
print('outcomes', len(outcomes), 'mode diffs', len(mode_diffs), 'expressibility', len(expr))
