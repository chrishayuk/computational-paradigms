# Builds absys.json for classifier A, absys batch 1B (P04, P06, P07, P08).
# Run: python3 -I build.py REPO OUTDIR
import json, glob, os, sys, csv

REPO, OUT = sys.argv[1], sys.argv[2]
CONFIGS = ['absys', 'absys-depth-first', 'absys-wake-back']
TOK = os.path.join(REPO, 'results/absys/tokens')

def ntok(rel):
    with open(os.path.join(TOK, 'absys', rel + '.tokens.tsv')) as f:
        return sum(1 for _ in f) - 1

def P(a, b, c, rule='rule 1 (reference semantics): part of the problem as given'):
    return {'from': a, 'to': b, 'class': 'P', 'construct': c, 'rule': rule}
def R(a, b, c, rule):
    return {'from': a, 'to': b, 'class': 'R', 'construct': c, 'rule': rule}

CONST = 'rule 1: a constant of the stage information, in the constants block (harness README 3.9); removing it changes the posed information'
SEP = 'rule 20: the separator takes the class of the construct that follows'

spans = {}
# ---------------- P04
for f, q in [('P04a.ab1', 'query: loop(x) or x = 1, in that order (P04a), a disjunction the problem states (rule 6)'),
             ('P04b.ab1', 'query: x = 1 or loop(x), in that order (P04b), a disjunction the problem states (rule 6)')]:
    spans[f] = [P(0, 3, "loop's definition: its head, loop'=lambda p"),
                P(4, 9, "loop, case 1: loop(x) if loop(x), the body begin loop(p) end"),
                P(10, 12, 'constant xval = 1 (stage 1)', CONST),
                P(13, 22, q)]
for f, query in [('P04c.ab1', True), ('P04d.ab1', False)]:
    s = [P(0, 3, "alist-left: definition head alist'=lambda p"),
         P(4, 5, 'alist-left: begin { opening the disjunction of its cases'),
         P(6, 16, "alist-left, case 1: alist(m') and p = ['a'&m], conjuncts in the order written (head as an equation on the parameter)"),
         P(17, 21, 'alist-left, case 2: or p = [] (alist(<>))', 'rule 1; ' + SEP),
         P(22, 23, 'alist-left: } end closing the definition')]
    if query:
        s += [P(24, 30, "constant sq = ['a';'a'] (stage 1)", CONST), P(31, 34, 'query: alist(sq), P04c')]
    else:
        s += [P(24, 27, 'query: alist(s), P04d')]
    spans[f] = s
for f, query in [('P04e.ab1', True), ('P04f.ab1', False)]:
    s = [P(0, 3, "alist-right: definition head alist'=lambda p"),
         P(4, 5, 'alist-right: begin { opening the disjunction of its cases'),
         P(6, 9, 'alist-right, case 1: p = [] (alist(<>))'),
         P(10, 21, "alist-right, case 2: or p = ['a'&m'] alist(m) (head as an equation, then alist(m))", 'rule 1; ' + SEP),
         P(22, 23, 'alist-right: } end closing the definition')]
    if query:
        s += [P(24, 30, "constant sq = ['a';'a'] (stage 1)", CONST), P(31, 34, 'query: alist(sq), P04e')]
    else:
        s += [P(24, 27, 'query: alist(s), P04f')]
    spans[f] = s
# ---------------- P06a-c
spans['P06a.abs'] = [P(0, 2, 'constant nk1 = 1 (stage 1)', CONST), P(3, 5, 'constant xk2 = 2 (stage 2)', CONST),
                     P(6, 11, 'stage 1: not(x = nk1), negation the problem states'), P(12, 14, 'stage 2: x = xk2')]
spans['P06b.abs'] = [P(0, 2, 'constant xk1 = 2 (stage 1)', CONST), P(3, 5, 'constant nk2 = 1 (stage 2)', CONST),
                     P(6, 8, 'stage 1: x = xk1'), P(9, 14, 'stage 2: not(x = nk2), negation the problem states')]
spans['P06c.abs'] = [P(0, 2, 'constant nk1 = 1 (stage 1)', CONST), P(3, 5, 'constant xk2 = 1 (stage 2)', CONST),
                     P(6, 11, 'stage 1: not(x = nk1), negation the problem states'), P(12, 14, 'stage 2: x = xk2')]
mem = [P(20, 25, 'mem: definition head mem = lambda E, S'),
       P(26, 34, 'mem, case 1: {S = [E|T]} (mem(e, <e> ++ t)), head as an equation on the parameter'),
       P(35, 51, 'mem, case 2: or {S = [H|T], mem(E, T)}', 'rule 1; ' + SEP)]
consts_d = [P(0, 10, 'constant s1v = [1, 2, 3, 4] (stage 1)', CONST), P(11, 19, 'constant s2v = [2, 4, 6] (stage 1)', CONST)]
spans['P06d.abs'] = consts_d + mem + [
    P(52, 59, 'setdiff: definition head setdiff = lambda S1, S2, D'),
    P(60, 70, 'setdiff, case 1: {S1 = [], D = []}'),
    P(71, 96, 'setdiff, case 2: or {S1 = [H|T], mem(H, S2), setdiff(T, S2, D)}', 'rule 1; ' + SEP),
    P(97, 133, 'setdiff, case 3: or {S1 = [H|T], D = [H|R], not(mem(H, S2)), setdiff(T, S2, R)}', 'rule 1; ' + SEP),
    P(134, 141, 'stage 1 query: setdiff(s1v, s2v, d)')]
spans['variants/P06d.set.abs'] = consts_d + mem + [
    P(52, 59, 'setdiff: definition head setdiff = lambda S1, S2, D'),
    P(60, 86, 'setdiff as a set former: {set(X), {mem(X, S1), not(mem(X, S2))}, D}', 'rule 7: a set-forming construct stating the definition the problem gives is P (P06d says so)'),
    P(87, 94, 'stage 1 query: setdiff(s1v, s2v, d)')]
def students(off_who):
    names = [('st1', "student fact 1"), ('st2', 'student fact 2'), ('mc1', 'maths fact 1'), ('mc2', 'maths fact 2'),
             ('tp1', 'takes fact 1, person'), ('tc1', 'takes fact 1, course'), ('tp2', 'takes fact 2, person'),
             ('tc2', 'takes fact 2, course'), ('tp3', 'takes fact 3, person'), ('tc3', 'takes fact 3, course')]
    s = []
    i = 0
    for n, d in names:
        s.append(P(i, i + 2, 'constant %s (%s)' % (n, d), CONST)); i += 3
    if off_who:
        s.append(P(i, i + 2, "constant who (the query's atom)", CONST)); i += 3
    b = i
    F = 'rule 6: a set of facts the problem states, in a closed world, as a procedure whose alternatives are the facts'
    s += [P(b, b + 3, 'student: definition head student = lambda P', F),
          P(b + 4, b + 8, 'student fact 1: {P = st1}', F),
          P(b + 9, b + 14, 'student fact 2: or {P = st2}', F + '; ' + SEP),
          P(b + 15, b + 18, 'maths: definition head maths = lambda K', F),
          P(b + 19, b + 23, 'maths fact 1: {K = mc1}', F),
          P(b + 24, b + 29, 'maths fact 2: or {K = mc2}', F + '; ' + SEP),
          P(b + 30, b + 35, 'takes: definition head takes = lambda P, K', F),
          P(b + 36, b + 44, 'takes fact 1: {P = tp1, K = tc1}', F),
          P(b + 45, b + 54, 'takes fact 2: or {P = tp2, K = tc2}', F + '; ' + SEP),
          P(b + 55, b + 64, 'takes fact 3: or {P = tp3, K = tc3}', F + '; ' + SEP),
          P(b + 65, b + 68, 'nonmajor: definition head nonmajor = lambda P'),
          P(b + 69, b + 89, 'nonmajor, case 1: {student(P), maths(K), not(takes(P, K))}, conjuncts in the order written')]
    q = b + 90
    return s, q
for f, who in [('P06e1.abs', True), ('P06e2.abs', True), ('P06e3.abs', False)]:
    s, q = students(who)
    s.append(P(q, q + 3, 'stage 1 query: nonmajor(%s)' % ('who' if who else 'p')))
    spans[f] = s
# ---------------- P07
def p07(f, consts, cnames):
    toks = [l.rstrip('\n').split('\t') for l in open(os.path.join(TOK, 'absys', f + '.tokens.tsv'))][1:]
    s = []
    for i, (a, b, c) in enumerate(consts):
        s.append(P(a, b, 'constant ' + c, CONST))
    start = consts[-1][1] + 1
    texts = [t[2] for t in toks]
    n = len(texts)
    grouped = texts[start] == 'begin'
    i = start
    if grouped:
        s.append(P(start, start, 'begin: the stage\'s relations as one conjunction (opening)', 'rule 1: the conjunction connective of the stage'))
        i = start + 1
    end = n - 2 if grouped else n - 1
    r0 = i
    for j in range(i, end + 1):
        if texts[j] in cnames:
            s.append(P(r0, j, 'relation: ' + ' '.join(texts[r0:j + 1]) + ' (a compound expression is a transcription, SPECIFICATION Conventions)'))
            r0 = j + 1
    if grouped:
        s.append(P(n - 1, n - 1, 'end: closing the conjunction', 'rule 1: the conjunction connective of the stage'))
    return s
a_consts = [(0, 2, 'r1sum = 12 (relation 1)'), (3, 5, 'r2sum = 7 (relation 2)'), (6, 8, 'r3val = 3 (relation 3)')]
for f in ['P07a.ab1', 'P07a.132.ab1', 'P07a.213.ab1', 'P07a.231.ab1', 'P07a.312.ab1', 'P07a.321.ab1']:
    spans[f] = p07(f, a_consts, {'r1sum', 'r2sum', 'r3val'})
spans['P07b.ab1'] = p07('P07b.ab1', [(0, 2, 'bsum = 10'), (3, 5, 'bdiff = 4')], {'bsum', 'bdiff'})
spans['P07c.ab1'] = p07('P07c.ab1', [(0, 2, 'csum = 10')], {'csum'})
spans['P07d.ab1'] = [P(0, 2, 'constant uval = 2', CONST), P(3, 5, 'constant vval = 14', CONST), P(6, 6, 'begin: the stage\'s relations as one conjunction (opening)', 'rule 1: the conjunction connective of the stage'), P(7, 11, 'relation: w * u = v'), P(12, 14, 'relation: u = uval'), P(15, 17, 'relation: v = vval'), P(18, 18, 'end: closing the conjunction', 'rule 1: the conjunction connective of the stage')]
spans['P07e.ab1'] = [P(0, 2, 'constant uval = 2', CONST), P(3, 5, 'constant vval = 15', CONST), P(6, 6, 'begin: the stage\'s relations as one conjunction (opening)', 'rule 1: the conjunction connective of the stage'), P(7, 11, 'relation: w * u = v'), P(12, 14, 'relation: u = uval'), P(15, 17, 'relation: v = vval'), P(18, 18, 'end: closing the conjunction', 'rule 1: the conjunction connective of the stage')]
spans['P07f.ab1'] = p07('P07f.ab1', [(0, 2, 'fsum1 = 10'), (3, 5, 'fsum2 = 11')], {'fsum1', 'fsum2'})
spans['P07g.ab1'] = p07('P07g.ab1', [(0, 2, 'gsq = 9')], {'gsq'})
# ---------------- P08
concdef = lambda b: [P(b, b + 7, 'conc: definition head conc=lambda p, q, r (no prime: an equation on the name, Absys idiom)'),
                     P(b + 8, b + 9, 'conc: begin { opening its cases'),
                     P(b + 10, b + 16, 'conc, case 1: p = [] q = r'),
                     P(b + 17, b + 39, "conc, case 2: or p = [h'&k'] r = [h&m'] conc(k, q, m)", 'rule 1; ' + SEP),
                     P(b + 40, b + 41, 'conc: } end')]
spans['P08a.ab1'] = [P(0, 2, 'constant pfx = 42 (stage 6)', CONST),
                     P(3, 11, 'stage 1: a = [x;y;z]'),
                     P(12, 17, 'stage 2: rev(a, b), the application before any definition'),
                     P(18, 20, 'stage 3: x = y'),
                     P(21, 26, 'stage 4: rev definition head rev=lambda p, r (no prime: the definition is information equated with the name already applied)'),
                     P(27, 28, 'rev: begin {'),
                     P(29, 36, 'rev, case 1: p = [] r = []'),
                     P(37, 60, "rev, case 2: or p = [h'&k'] rev(k, n') conc(n, [h], r), conjuncts in the order written", 'rule 1; ' + SEP),
                     P(61, 62, 'rev: } end')] + concdef(63) + [
                     P(105, 107, 'stage 5: y = z'),
                     P(108, 114, 'stage 6: b = [pfx&c]')]
spans['P08b.ab1'] = [P(0, 8, 'stage 1: a = [x;y;z]'), P(9, 14, 'stage 2: rev(a, b)'), P(15, 17, 'stage 3: x = y')]
c_consts = [P(0, 6, 'constant rs = [1;2] (stage 2)', CONST), P(7, 10, 'constant r1p = [] (stage 3, case 1)', CONST),
            P(11, 14, 'constant r1r = [] (stage 3, case 1)', CONST)]
spans['P08c.ab1'] = c_consts + concdef(15) + [
    P(57, 62, 'stage 2: rev(rs, b), before rev has a definition'),
    P(63, 68, 'stage 3: rev definition head rev=lambda p, r'),
    P(69, 70, 'rev: begin {'),
    P(71, 76, 'rev, case 1: p = r1p r = r1r (rev(<>, <>))'),
    R(77, 83, 'or revmore(p, r): an alternative standing for the cases of rev not yet given, which waits for its definition',
      'R: a case the problem file does not give (METRICS class R; rule 4 for the tokens that introduce it); ' + SEP),
    P(84, 85, "rev: } end, closing rev's definition"),
    R(86, 92, 'stage 4: revmore=lambda p, r begin, the head of a definition the problem does not give (revmore)',
      'rule 4: the tokens that introduce the case moved into a new procedure are R; the contents are classed on their own (rule 10)'),
    P(93, 115, "rev, case 2 contents: p = [h'&k'] rev(k, n') conc(n, [h], r), as the problem's case 2", 'rule 10: nested construct classed on its own; the case is the problem\'s'),
    R(116, 116, "end closing revmore's definition", 'rule 4: the tokens that close the reformulated case are R')]
spans['variants/P08c.redefine.ab1'] = c_consts + concdef(15) + [
    P(57, 62, 'stage 2: rev(rs, b), before rev has a definition'),
    P(63, 68, 'stage 3: rev definition head rev=lambda p, r (case 1 alone)'),
    P(69, 76, 'rev, case 1: begin p = r1p r = r1r end'),
    P(77, 82, 'stage 4: a second equation on rev, rev=lambda p, r (case 2 alone)', 'rule 1: the stage information transcribed literally (its meaning in Absys is a second equation on rev: see notes)'),
    P(83, 107, "rev, case 2: begin p = [h'&k'] rev(k, n') conc(n, [h], r) end")]

# ---------- check coverage
texts = [l.rstrip('\n').split('\t') for l in open(os.path.join(TOK, 'TEXTS-1B-P04-P06-P08.tsv'))][1:]
tokens_out = {}
for t, also in texts:
    rel = t.split('/', 1)[1]
    n = ntok(rel)
    sp = sorted(spans[rel], key=lambda s: s['from'])
    cov = []
    for s in sp:
        cov += list(range(s['from'], s['to'] + 1))
    assert cov == list(range(n)), (rel, n, [(s['from'], s['to']) for s in sp])
    tokens_out[t] = sp
assert len(tokens_out) == len(spans)

# ---------- records
def recs(conf, prob):
    out = {}
    for f in sorted(glob.glob(os.path.join(REPO, 'results/absys', conf, prob, 'raw', '*.json'))):
        d = json.load(open(f))
        prog = d['run']['program']['path'].split('/', 3)[3]
        out[(d['run']['instance'], prog, d['run']['mode'])] = os.path.relpath(f, REPO)
    for f in sorted(glob.glob(os.path.join(REPO, 'results/absys', conf, prob, 'raw-rerun-m2', '*.json'))):
        d = json.load(open(f))
        prog = d['run']['program']['path'].split('/', 3)[3]
        out[(d['run']['instance'], prog, d['run']['mode'] + '-m2')] = os.path.relpath(f, REPO)
    return out

def O(sem, rep, simp=None, ident=None, size=None, ex=('finished',), eq=None, obs='', rule=None, **kw):
    d = {'reached': True, 'semantic': sem, 'representation': rep, 'simplification': simp,
         'identical_to_posed': ident, 'residual_size': size, 'execution_state': list(ex),
         'residual_equivalence': eq, 'observations': obs, 'rule': rule}
    d.update(kw)
    return d

NOMAN = ' Manual actions: none. No earlier conclusion withdrawn.'
B = {}  # (instance, program) -> list of stage dicts, for the configuration absys (others differ only where stated)
B[('P04a', 'P04a.ab1')] = [O('complete', 'explicit', ex=('budget',),
    eq='Derivation #2 binds x = 1. Derivation #1 still holds loop(x) to do; loop, read as the least relation, has no instances, so the two derivations together denote exactly x = 1.',
    obs='x = 1 is reported (derivation #2, hibernating), beside derivation #1, still elaborating loop(x) when the budget ran out (x uninstantiated). Alternatives: 2 derivations, all live, at the boundary and at the budget. Suspended work: none (0). The endless alternative did not hide the finite one. Steps (cost run): 1000002.' + NOMAN,
    rule='SPECIFICATION Outcomes 2: classified on the more explicit valid form (x = 1); the still-elaborating derivation is recorded as an observation. Execution state budget: the system reports a derivation still elaborating when the budget ran out.')]
B[('P04b', 'P04b.ab1')] = [O('complete', 'explicit', ex=('budget',),
    eq='Derivation #1 binds x = 1; derivation #2 holds loop(x) to do, which has no instances under the least relation, so the report denotes exactly x = 1.',
    obs='x = 1 is reported first (derivation #1, hibernating); derivation #2 still elaborating loop(x) at the budget. Alternatives: 2 derivations, all live. Suspended work: none. Steps (cost run): 1000002.' + NOMAN,
    rule='SPECIFICATION Outcomes 2 (more explicit valid form); budget as reported.')]
for inst, prog, defn in [('P04c', 'P04c.ab1', 'alist-left'), ('P04e', 'P04e.ab1', 'alist-right')]:
    B[(inst, prog)] = [O('complete', 'explicit',
        eq=None,
        obs='One derivation survives, hibernating, with no unknowns (true). The computation finishes. Alternatives: 1 derivation at the boundary (peak 2 in the storage run; peak 4 under absys-depth-first for P04c). Suspended work: none. Steps (cost run): 15. Definition: %s.' % defn + NOMAN,
        rule='SPECIFICATION Outcomes 1, 2: true with no unknowns, one solution given (the empty assignment).')]
for inst, prog, defn in [('P04d', 'P04d.ab1', 'alist-left'), ('P04f', 'P04f.ab1', 'alist-right')]:
    B[(inst, prog)] = [O('none reported', None, ex=('error',),
        eq=None,
        obs='The system process was ended by SIGKILL (exit -9), which the harness did not send: the record attributes it to the container\'s memory, the system keeping every event of its run (about 85 bytes a step). No state was printed, so no solution of the infinitely many is reported, and whether every solution would be reached given enough steps cannot be read from the record. Alternatives and suspended work: unavailable (not 0, AMENDMENTS 3.1). Definition: %s. Answer completeness (infinite outcomes): no finite equivalent representation; no answers obtained.' % defn + NOMAN,
        rule='SPECIFICATION Outcomes 3, error, verbatim in the record; nothing reported, so none reported.')]
B[('P06a', 'P06a.abs')] = [
    O('unsound', 'explicit',
      obs='The system reports that no derivation survives ("the assertions are unsatisfiable") where every x other than 1 is valid. The negation was decided at once, in stage 1, at step 5 (cost run): not(x = 1) started an independent computation (#1), which bound its own x to 1 and hibernated without contradiction, so the not failed. It was not held as a condition, not delayed, not an error. Unknown x: no derivation, so no representation. Alternatives: 0 derivations (peak 1; sub_derivations peak 1). Suspended work: none (susp_negations 0).' + NOMAN,
      rule='SPECIFICATION Outcomes 1, unsound: reports there are none where valid outcomes exist (P06 Observations: a system that reports no solution for P06a is unsound).'),
    O('unsound', 'explicit',
      obs='No derivation survives from stage 1; x = 2 has nothing to act on (0 steps at stage 2). Valid outcome x = 2 is not reported. P06a and P06b do not give the same outcome. Alternatives: 0. Suspended work: none.' + NOMAN,
      rule='SPECIFICATION Outcomes 1, unsound: reports none where x = 2 is valid.')]
B[('P06b', 'P06b.abs')] = [
    O('complete', 'explicit', obs='x = 2, one derivation, hibernating. Alternatives: 1. Suspended work: none.' + NOMAN, rule='SPECIFICATION Outcomes 1, 2.'),
    O('complete', 'explicit', obs='x = 2. The negation was decided at stage 2, at once, with x known: its independent computation failed on 2 = 1, so not(x = 1) holds (sub_derivations peak 1, 4 steps). Alternatives: 1. Suspended work: none.' + NOMAN, rule='SPECIFICATION Outcomes 1, 2.')]
B[('P06c', 'P06c.abs')] = [
    O('unsound', 'explicit', obs='As P06a stage 1: not(x = 1) decided at once at step 5, failing because its independent computation could bind x to 1; the system reports that no derivation survives where every x other than 1 is valid. Alternatives: 0. Suspended work: none.' + NOMAN,
      rule='SPECIFICATION Outcomes 1, unsound.'),
    O('complete', 'explicit', obs='No derivation survives, which matches the valid outcome (none), but only because the computation had already failed at stage 1 (0 steps at stage 2); the inconsistency of x = 1 with not(x = 1) was never itself detected. Answer completeness: the system reported that there are none (yes). Alternatives: 0. Suspended work: none.' + NOMAN,
      rule='SPECIFICATION Outcomes 1, complete: the report (none) equals the valid outcomes (none).')]
B[('P06d', 'P06d.abs')] = [O('complete', 'explicit',
    obs='d = [1,3], one derivation surviving (derivation #94 under absys and absys-wake-back, #43 under absys-depth-first). Each not(mem(H, S2)) is decided with H and S2 known. Alternatives: 1 at the boundary; peak 12 derivations and 34 sub-derivations (absys, absys-wake-back), 7 and 16 (absys-depth-first). Suspended work: none. Steps (cost): 405 (399 depth-first). Answer completeness 1/1, 0 invalid.' + NOMAN,
    rule='SPECIFICATION Outcomes 1, 2.')]
B[('P06d', 'variants/P06d.set.abs')] = [O('complete', 'explicit',
    obs='Named variant (set former). d = [1,3], one derivation. Alternatives: 1 (peak 1; sub_derivations peak 9, 6 depth-first). Suspended work: none. Steps (cost): 198 (192 depth-first). Answer completeness 1/1.' + NOMAN,
    rule='SPECIFICATION Outcomes 1, 2.')]
B[('P06e1', 'P06e1.abs')] = [O('complete', 'explicit',
    obs='True: one derivation survives with no unknowns. Ground negations only (p and k known before each not). Alternatives: 1 (peak 2; 3 depth-first). Suspended work: none.' + NOMAN, rule='SPECIFICATION Outcomes 1, 2.')]
B[('P06e2', 'P06e2.abs')] = [O('complete', 'explicit',
    obs='False: no derivation survives, the valid outcome. Answer completeness: reported that there are none (yes). Alternatives: 0 (peak 2). Suspended work: none.' + NOMAN, rule='SPECIFICATION Outcomes 1: the report (none) equals the valid outcome (false).')]
B[('P06e3', 'P06e3.abs')] = [O('complete', 'explicit',
    obs="p = 'BROWN', one derivation. The trace (cost run) shows student(p) and maths(K) distributed into four derivations, each binding p and k before its not(takes(p, k)) began: p and k are known before the negation is decided. Alternatives: 1 at the boundary (peak 4; 3 depth-first). Suspended work: none. Answer completeness 1/1." + NOMAN,
    rule='SPECIFICATION Outcomes 1, 2.')]
for inst in ['P07a', 'P07a.132', 'P07a.213', 'P07a.231', 'P07a.312', 'P07a.321']:
    B[(inst, inst + '.ab1')] = [O('complete', 'explicit',
        obs='x = 5, y = 4, z = 3, one derivation, finished. Solved one relation at a time as its values became known: the arithmetic relations suspend ("waits for two of its numbers") and are reactivated as z, then the others, are bound (propagation through suspension, not elimination or search). Alternatives: 1. Suspended work at the boundary: none printed (storage susp_relations boundary counts relations still associated with bound variables, harness README 4).' + NOMAN,
        rule='SPECIFICATION Outcomes 1, 2.')]
B[('P07b', 'P07b.ab1')] = [O('complete', 'residual', 'reducible', True,
    'residual: 2 relations (x + y = 10; 4 + y = x), 4 occurrences of unknowns; input: 2 relations (x + y = 10; x - y = 4), 4 occurrences',
    ex=('suspended',),
    eq='The residual x + y = 10, 4 + y = x is x + y = 10, x - y = 4 rewritten (x - y = 4 iff 4 + y = x over the integers), so it denotes exactly x = 7, y = 3. Reducible: x = 7, y = 3 has no relation left to decide.',
    obs='x and y uninstantiated; 2 suspended relations, each "waits for two of its numbers". The system does not eliminate between relations. Alternatives: 1 derivation.' + NOMAN,
    rule='SPECIFICATION Outcomes, simplification (P07b is the specification\'s own example: complete / residual / reducible). identical_to_posed true: no relation was decided or combined; x - y = 4 is only held in the system\'s additive form.')]
B[('P07c', 'P07c.ab1')] = [O('complete', 'residual', 'reduced', True,
    'residual: 1 relation (x + y = 10), 2 occurrences; input: the same',
    ex=('suspended',), eq='The held relation is the posed relation, and denotes every integer pair with x + y = 10.',
    obs='x, y uninstantiated; 1 suspended relation. Answer completeness (infinite): a finite representation equivalent to them was given (yes). Alternatives: 1.' + NOMAN,
    rule='SPECIFICATION Outcomes, simplification (P07c is the specification\'s example: complete / residual / reduced).')]
B[('P07d', 'P07d.ab1')] = [O('complete', 'explicit',
    obs='w = 7, u = 2, v = 14, finished: w * u = v suspended until u and v were known, then gave w (one relation at a time). Alternatives: 1.' + NOMAN, rule='SPECIFICATION Outcomes 1, 2.')]
B[('P07e', 'P07e.ab1')] = [O('complete', 'explicit',
    obs='No derivation survives: w * 2 = 15 fails ("15 is not a whole multiple of 2"). The inconsistency is detected, with no rational answer w = 15/2. Answer completeness: reported that there are none (yes). Alternatives: 0. Suspended work: none.' + NOMAN,
    rule='SPECIFICATION Outcomes 1: the report (none) equals the valid outcome (none).')]
B[('P07f', 'P07f.ab1')] = [O('complete', 'residual', 'inconsistency undetected', True,
    'residual: 2 relations (x + y = 10; x + y = 11), 4 occurrences; input: the same',
    ex=('suspended',), eq='The held relations are the posed ones, which have no common solution: they denote the empty set, which the system has not reported.',
    obs='x, y uninstantiated; 2 suspended relations. The inconsistency is not detected. Answer completeness: reported that there are none: no. Alternatives: 1.' + NOMAN,
    rule='SPECIFICATION Outcomes (P07f is the specification\'s example: complete / residual / inconsistency undetected; P07 Observations: with suspended).')]
B[('P07g', 'P07g.ab1')] = [O('complete', 'residual', 'reducible', True,
    'residual: 1 relation (x * x = 9), 2 occurrences; input: the same',
    ex=('suspended',), eq='x * x = 9 over the integers denotes exactly x = 3 or x = -3; a smaller equivalent (the two values, no relation left) exists.',
    obs='x uninstantiated; x * x = 9 suspended, "waits for two of its numbers: x" (only one distinct unknown, never two known). Neither solution is found. Answer completeness: 0/2 explicit answers, the residual denoting both. Alternatives: 1.' + NOMAN,
    rule='SPECIFICATION Outcomes, simplification: reducible, since the explicit solutions leave no relation to decide.')]

def P8(sem_o, sem_c, rep, simp=None, ident=None, size=None, ex=('finished',), eq=None, obs='', rule=None):
    d = O('open: %s; closed: %s' % (sem_o, sem_c), rep, simp, ident, size, ex, eq, obs, rule)
    d['semantic_open'] = sem_o
    d['semantic_closed'] = sem_c
    return d

P8R = 'P08: classified under both readings. '
st1 = P8('complete', 'complete', 'solved form', obs='a = [x;y;z], x, y, z uninstantiated (free), b not yet occurring. Alternatives: 1. Suspended work: none.' + NOMAN,
         rule=P8R + 'Solved form: a bound to a term of unknowns, no relation to decide.')
st2 = P8('complete', 'unsound', 'residual', 'reduced', True,
         'residual: 1 relation (rev([x;y;z], b)), 4 occurrences; input (stages 1-2): a = [x;y;z], rev(a, b)',
         ex=('suspended',), eq='Open reading: a = [x;y;z], b free, rev(a, b) pending, which is what the system holds. Closed reading: the valid outcome is none, but a derivation survives.',
         obs='State 4 of P08 (a computation awaiting its definition): "suspended rev([x;y;z], b) (waits for a definition: rev)", rev shown as an uninstantiated identifier. Suspended work: 1 (susp_applications 1). Alternatives: 1. Distinguishable from failure: yes.' + NOMAN,
         rule=P8R + 'P08a, open reading: a system that holds rev(a, b) as a pending application and reports the equations is complete / residual.')
st3 = P8('complete', 'unsound', 'residual', 'reduced', True,
         'residual: rev([x;y;z], b) held, x identified with y; 1 relation to decide, 4 occurrences; input (stages 1-3): a = [x;y;z], rev(a, b), x = y',
         ex=('suspended',), eq='Open reading: x = y, a = [y;y;z], b free, rev pending, which is what the system holds (x = y as a suspended equation between unknowns, an identification). Closed: valid none; a derivation survives.',
         obs='Suspended: rev([x;y;z], b) waiting for its definition, and x = y (susp_applications 1, susp_equations 1): 2 items. Alternatives: 1.' + NOMAN,
         rule=P8R + 'As stage 2.')
B[('P08a', 'P08a.ab1')] = [st1, st2, st3,
    P8('complete', 'complete', 'solved form', ex=('suspended',),
       eq='b = [h5;h6;h1] with suspended equations x = y, x = h1, y = h2, z = h3, h3 = h4, h4 = h5, h2 = h6: closing the equations (check_p08a.py, union-find) gives a = [y;y;z], b = [z;y;y], x = y, the valid outcome of both readings. Equivalent: yes.',
       obs='The pending application was resumed at stage 4 without reposing ("rev = lambda p, r ...; reactivated rev([x;y;z], b)"); conc, defined after rev in the same stage, was itself awaited by up to 3 applications (susp_applications peak 3). Unknowns left as identifications through auxiliary unknowns h1..h6 (7 suspended equations). Alternatives: 1 at the boundary (peak 2; 4 under absys-depth-first). Closed reading: the valid conclusion of stages 2-3 (none) is withdrawn by stage 4; the system had never reported none, so it withdrew nothing of its own. Steps (cost): 54. Manual actions: none.',
       rule=P8R + 'Solved form: every unknown bound, free, or identified with another; no relation left to decide.'),
    P8('complete', 'complete', 'solved form', ex=('suspended',),
       eq='Adding y = z to the stage-4 closure gives x = y = z, a = b = [z;z;z] (check_p08a.py). Equivalent: yes.',
       obs='8 suspended equations between unknowns (x = y = z shown). Alternatives: 1.' + NOMAN,
       rule=P8R + 'Solved form.'),
    P8('complete', 'complete', 'explicit',
       obs='a = b = [42;42;42], c = [42;42], x = y = z = 42, finished; no printed suspended process (storage susp_equations boundary 8 counts equations still associated with bound variables, harness README 4).' + NOMAN,
       rule=P8R + 'Every unknown given a value.')]
B[('P08b', 'P08b.ab1')] = [st1, st2, dict(st3, observations=st3['observations'] + ' P08b ends here: the application stays held, waiting for a definition, distinguishable from failure (a derivation survives with its suspended application). State 4 of P08.')]
B[('P08c', 'P08c.ab1')] = [
    P8('complete', 'complete', 'explicit', obs='conc defined; no unknowns (b does not occur). Alternatives: 1.' + NOMAN, rule=P8R),
    P8('complete', 'unsound', 'residual', 'reduced', True, 'residual: 1 relation (rev([1;2], b)), 1 occurrence; input: the same application',
       ex=('suspended',), eq='Open: b free, rev pending: what the system holds. Closed: valid none; a derivation survives.',
       obs='"suspended rev([1;2], b) (waits for a definition: rev)": state 4. Suspended work: 1 application. Alternatives: 1.' + NOMAN, rule=P8R),
    P8('complete', 'unsound', 'residual', 'reduced', False, 'residual: 1 relation (revmore([1;2], b)), 1 occurrence; input: rev([1;2], b) and case 1 of rev',
       ex=('suspended',), eq='Open: b free, pending, since case 2 may yet arrive. The system resumed rev([1;2], b) with case 1 (derivation #1 failed on [1;2] = []) and holds the rest as revmore([1;2], b) waiting for revmore\'s definition, which is rev(<1,2>, b) restricted to the cases not yet given: equivalent. Closed: valid none; a derivation survives.',
       obs='At stage 3 the application is resumed with the partial definition, not failed: the case-1 alternative fails, the remainder is held ("waits for a definition: revmore"). Suspended work: 1 application. Alternatives: 1 (peak 2). The holding of the remainder is by the program\'s reformulation (revmore, R).' + NOMAN,
       rule=P8R + 'identical_to_posed false: the system transformed the application (case 1 tried and dropped).'),
    P8('complete', 'complete', 'explicit',
       obs='b = [2;1], finished: stage 4 resumed the pending revmore application without reposing ("reactivated revmore([1;2], b)"). Alternatives: 1 (peak 2; 4 depth-first). Steps (cost): 30. Closed reading: the valid conclusion of stages 2-3 (none) is withdrawn; the system had not reported it.' + ' Manual actions: none.',
       rule=P8R)]
B[('P08c', 'variants/P08c.redefine.ab1')] = [
    P8('complete', 'complete', 'explicit', obs='Named variant. conc defined; no unknowns.' + NOMAN, rule=P8R),
    P8('complete', 'unsound', 'residual', 'reduced', True, 'residual: 1 relation (rev([1;2], b)), 1 occurrence; input: the same',
       ex=('suspended',), eq='As the primary at stage 2.', obs='rev([1;2], b) waits for a definition (state 4). Suspended: 1.' + NOMAN, rule=P8R),
    P8('unsound', 'complete', 'explicit',
       obs='The equation rev = lambda (case 1 alone) resumed rev([1;2], b), which failed on [1;2] = []: no derivation survives. Under the open reading the application should still be pending; under the closed reading none is valid. The application is failed at stage 3, not held. Alternatives: 0 (peak 1). Suspended work: none.' + NOMAN,
       rule=P8R + 'Open: reports none where b free / pending is valid, so unsound; closed: none is valid.'),
    P8('unsound', 'unsound', 'explicit',
       obs='No derivation survives (0 steps at stage 4): stage 4 cannot reach the application, which failed at stage 3. The second equation on rev, which in Absys would equate rev with a second lambda, is never elaborated. Valid b = [2;1] under both readings is not reported. Alternatives: 0.' + NOMAN,
       rule=P8R + 'Reports none where b = <2,1> is valid.')]

# configuration-specific overrides
OVR = {('absys-depth-first', 'P04a', 'P04a.ab1'): [O('complete', 'residual', 'reducible', True,
    'residual: 2 derivations, loop(x) to do and x = 1 to do (2 relations, 2 occurrences); input: loop(x) or x = 1 (2 relations, 2 occurrences)',
    ex=('budget',),
    eq='Derivation #1 holds loop(x), which has no instances; derivation #2 holds x = 1 still to do ("x does not occur" in it). Their union denotes exactly x = 1, so equivalent; x = 1 alone is smaller (reducible).',
    obs='Both derivations still elaborating at the budget: depth-first elaborated derivation #1 (loop) only, so x = 1 was never taken up and never bound. The endless alternative hides the finite one in the binding sense. Alternatives: 2 derivations held, 1 live (mixed). Suspended work: none. Steps (cost run): 1000002.' + NOMAN,
    rule='SPECIFICATION Outcomes 2, residual: the held, unelaborated x = 1 is state the system would act on, read by observe(); identical to the posed disjunction. Disputable: an alternative reading is none reported, since no binding of x is held (notes).')]}

outcomes = []
for conf in CONFIGS:
    for prob in ['P04', 'P06', 'P07', 'P08']:
        rr = recs(conf, prob)
        for (inst, prog, mode), path in sorted(rr.items()):
            if mode != 'behaviour':
                continue
            stages = OVR.get((conf, inst, prog), B[(inst, prog)])
            d = json.load(open(os.path.join(REPO, path)))
            assert len(d['stages']) == len(stages), (path, len(d['stages']), len(stages))
            for s, cls in zip(d['stages'], stages):
                states = s['attempts'][-1]['computations'][0]['execution_state']['states']
                assert states == cls['execution_state'], (path, s['stage'], states, cls['execution_state'])
                e = {'configuration': conf, 'instance': inst, 'program': prog, 'record': path, 'stage': s['stage']}
                e.update(cls)
                if (inst, prog) in [('P04d', 'P04d.ab1'), ('P04f', 'P04f.ab1')]:
                    e['error_verbatim'] = s['attempts'][-1]['computations'][0]['execution_state']['error_verbatim']
                outcomes.append(e)

# ---------- mode differences
mode_diff = []
for conf in CONFIGS:
    rr = recs(conf, 'P04')
    for inst, prog in [('P04d', 'P04d.ab1'), ('P04f', 'P04f.ab1')]:
        for mode in ['cost', 'storage']:
            path = rr[(inst, prog, mode)]
            mode_diff.append({'configuration': conf, 'instance': inst, 'program': prog, 'mode': mode, 'record': path, 'stage': 1,
                'behaviour': {'semantic': 'none reported', 'representation': None, 'execution_state': ['error'], 'record': rr[(inst, prog, 'behaviour')]},
                'this_mode': {'semantic': 'none reported', 'representation': None, 'execution_state': ['timeout']},
                'note': 'Both attempts (60 s, then the rerun at 600 s) were stopped by the safety limit (SIGKILL by the harness), where the behaviour run was killed by the kernel for memory after about 3 s. The semantic results agree (nothing reported). The cost/storage run is instrumented (--measure, and --trace in cost), so its timeout is a limit of the measurement (PROTOCOL, Modes), not evidence about the model. No step count or store is available (unavailable, not 0).'})
            m2 = rr[(inst, prog, mode + '-m2')]
            mode_diff.append({'configuration': conf, 'instance': inst, 'program': prog, 'mode': mode + ' (measurement rerun m2)', 'record': m2, 'stage': 1,
                'behaviour': {'semantic': 'none reported', 'representation': None, 'execution_state': ['error']},
                'this_mode': {'semantic': 'none reported', 'representation': None, 'execution_state': ['error']},
                'note': 'No difference from the behaviour run: the m2 rerun (absys-measure 8a0eefd, --peak-every) ended by SIGKILL from the kernel, as the behaviour run did, which differs from the original %s record beside it (timeout). Listed for the comparison the brief asks for; the original record stands.' % mode})

# ---------- expressibility
expr = []
subs = {'P04': ['P04a', 'P04b', 'P04c', 'P04d', 'P04e', 'P04f'],
        'P06': ['P06a', 'P06b', 'P06c', 'P06d', 'P06e1', 'P06e2', 'P06e3'],
        'P07': ['P07a', 'P07b', 'P07c', 'P07d', 'P07e', 'P07f', 'P07g'],
        'P08': ['P08a', 'P08b', 'P08c']}
reasons = {
    'P04': 'Every definition (loop, alist-left, alist-right) and query is transcribed case by case in the order given: no R token.',
    'P06': 'not, the facts (as procedures whose alternatives are the facts, a closed world) and the definitions by cases are transcribed in the order given: no R token. Transcribed is not sound: P06a and P06c stage 1 are unsound (outcomes).',
    'P07': 'Each set of relations is transcribed as arithmetic assertions in the order given (P07a in each of its six orders): no R token. Whether the system solves them is an outcome, not expressibility.',
    'P08a': 'rev and conc transcribed as in P03; the application is posed before the definitions, which arrive as equations on the names at stage 4: no R token.',
    'P08b': 'Stages 1-3 transcribed: no R token.',
    'P08c': 'An Absys procedure is one value, given by one equation, with no way to receive a further case. The program of record gives rev at stage 3 as case 1 or revmore(p, r), and defines revmore as case 2 at stage 4: 15 R tokens (77-83, 86-92, 116). On the inputs used, rev keeps its meaning (case 1 union the cases still to come), and stage 4 completes it. The literal transcription (variants/P08c.redefine.ab1, two equations on rev) changes the meaning: it fails the application at stage 3 and is reported as a named variant. Concern: writing revmore at stage 3 presumes that more cases may arrive (notes).',
}
for conf in CONFIGS:
    for prob, ss in subs.items():
        for sp in ss:
            if prob == 'P08':
                ex = 'expressible with reformulation' if sp == 'P08c' else 'expressible'
                rs = reasons[sp]
            else:
                ex = 'expressible'; rs = reasons[prob]
            if sp == 'P07a':
                rs += ' The six orders (P07a, .132, .213, .231, .312, .321) are one sub-problem; each order is an instance of the problem, so none is a move.'
            if sp == 'P06d':
                rs += ' The named variant (set former) is also P (rule 7), but it is not the problem\'s setdiff for an s1 with repeated elements.'
            expr.append({'configuration': conf, 'subproblem': sp, 'direction': 'rev(a, b), a given (as a list of unknowns or of values), b unknown' if prob == 'P08' else None,
                         'expressibility': ex, 'reason': rs})

# ---------- late definition
late = []
for conf in CONFIGS:
    late += [
        {'configuration': conf, 'program': 'P08a.ab1', 'kind': 'code awaited',
         'evidence': 'The application rev(a, b) (tokens 12-17, stage 2) is posed with no definition of rev in the program; Absys suspends it, "rev has no value yet; the application waits" (susp_applications 1 at stages 2 and 3, rev printed as an uninstantiated identifier). The definitions (tokens 21-62 rev, 63-104 conc) are information of stage 4, equations on the names; the trace shows "rev = lambda p, r ...; reactivated rev([x;y;z], b)", and conc applications, defined after rev, wait in turn for conc (susp_applications peak 3). No flag or test: the wait is on the value of the identifier itself (docs/decisions.md rule 6, as the systems file says).'},
        {'configuration': conf, 'program': 'P08b.ab1', 'kind': 'code awaited',
         'evidence': 'rev(a, b) (tokens 9-14) waits for rev\'s value through stage 3, the last; the record ends with "suspended rev([x;y;z], b) (waits for a definition: rev)", a surviving derivation, told apart from failure. The definition never arrives.'},
        {'configuration': conf, 'program': 'P08c.ab1', 'kind': 'code awaited',
         'evidence': 'rev(rs, b) (tokens 57-62, stage 2) waits for rev; stage 3\'s equation rev=lambda (63-85) reactivates it; case 1 fails in one derivation and the remainder revmore([1;2], b) (R tokens 77-83) waits for revmore\'s value; stage 4\'s revmore=lambda (86-116; R head 86-92 and 116, problem contents 93-115) reactivates it and gives b = [2;1]. Both waits are on a definition arriving as information; the waiting on the remainder depends on the reformulation.'},
        {'configuration': conf, 'program': 'variants/P08c.redefine.ab1', 'kind': 'code awaited',
         'evidence': 'At stage 2 rev(rs, b) (57-62) waits for rev, as in the primary (code awaited). But the stage-3 equation (63-76) gives rev a value that is case 1 alone, the application is resumed with it and fails ([1;2] = []); no derivation survives, so the stage-4 equation (77-107) reaches nothing. Held until the first (partial) definition, then failed: not held across a definition that arrives in parts.'}]

# ---------- S mechanisms
smech = []
for conf in CONFIGS:
    for t, also in texts:
        prog = t.split('/', 1)[1]
        smech.append({'configuration': conf, 'program': prog, 'mechanism': 'none', 'listed_at_phase_4': True, 'tokens': 0,
                      'note': 'harnesses/absys/S-mechanisms.md lists none for this configuration; the program supplies none (no S token). The waiting for a definition in P08 is the core\'s (rule 6), not program code.' if prog.startswith('P08') or 'P08' in prog else 'harnesses/absys/S-mechanisms.md lists none for this configuration; the program supplies none (no S token).'})

doc = {'classifier': 'A (Claude agent, claude-opus-5-5)', 'repo_commit': 'b73d59a', 'batch': '1B: absys P04, P06, P07, P08',
       'tokens': tokens_out, 'outcomes': outcomes, 'mode_differences': mode_diff, 'expressibility': expr,
       'late_definition': late, 's_mechanisms': smech}
json.dump(doc, open(os.path.join(OUT, 'absys.json'), 'w'), indent=1, ensure_ascii=False)
# totals
tot = {}
for t, sp in tokens_out.items():
    for s in sp:
        tot[s['class']] = tot.get(s['class'], 0) + s['to'] - s['from'] + 1
print('texts', len(tokens_out), 'tokens by class', tot, 'outcomes', len(outcomes), 'mode_diffs', len(mode_diff))
from collections import Counter
print(Counter((o['semantic']) for o in outcomes))
print(Counter(tuple(o['execution_state']) for o in outcomes))
