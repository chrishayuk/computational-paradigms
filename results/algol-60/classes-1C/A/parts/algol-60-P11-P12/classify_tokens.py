"""Token classes for ALGOL 60 P11 and P12 (batch 1C), classifier 1C-A.

Reads only the frozen token files (results/algol-60/tokens/...). Each
program's classes are given as a list of construct starts, anchored on a
line of the program and a token text there; a construct runs to the token
before the next start. METRICS.md rule 20 is then applied mechanically: a
separator (';' or ',') just before a construct's first token belongs to
that construct. The script checks that every token is covered exactly once
and writes tokens.json beside it.

Usage: python3 -I classify_tokens.py REPO_ROOT"""
import json, sys, os

ROOT = sys.argv[1]
TOK = os.path.join(ROOT, 'results/algol-60/tokens')


def load_tokens(path):
    rows = [l.rstrip('\n').split('\t') for l in open(path, encoding='utf-8')][1:]
    return [(int(i), int(l), t) for i, l, t in rows]


def find(tokens, anchor):
    line = anchor[0]
    on_line = [t for t in tokens if t[1] == line]
    if not on_line:
        raise SystemExit(f'no tokens on line {line}')
    if len(anchor) == 1:
        return on_line[0][0]
    text, occ = anchor[1], anchor[2] if len(anchor) > 2 else 1
    off = anchor[3] if len(anchor) > 3 else 0
    hits = [t for t in on_line if t[2] == text]
    if len(hits) < occ:
        raise SystemExit(f'anchor {anchor} not found: {[t[2] for t in on_line]}')
    return hits[occ - 1][0] + off


def spans_for(tokens, spec):
    starts = []
    for anchor, cls, construct, rule in spec:
        starts.append([find(tokens, anchor), cls, construct, rule])
    for a, b in zip(starts, starts[1:]):
        if not a[0] < b[0]:
            raise SystemExit(f'anchors out of order: {a} {b}')
    if starts[0][0] != 0:
        raise SystemExit('first construct must start at token 0')
    # rule 20: a separator before a construct belongs to it
    text = {i: t for i, _, t in tokens}
    begins = {s[0] for s in starts}
    for s in starts[1:]:
        p = s[0] - 1
        if text[p] in (';', ',') and p not in begins:
            s[0] = p
    last = tokens[-1][0]
    out = []
    for k, s in enumerate(starts):
        end = starts[k + 1][0] - 1 if k + 1 < len(starts) else last
        if end < s[0]:
            raise SystemExit(f'empty construct {s}')
        out.append({'from': s[0], 'to': end, 'class': s[1], 'construct': s[2], 'rule': s[3]})
    # coverage check
    seen = []
    for sp in out:
        seen.extend(range(sp['from'], sp['to'] + 1))
    assert seen == list(range(0, last + 1)), 'coverage'
    return out

H_READ = 'harness README 2.7.1 (statement that reads a harness word); METRICS.md class H'
H_DECL = 'harness README 2.7.5 (declaration of variables holding only harness words)'
H_LOOP = 'harness README 2.7.2 (message loop and dispatch on the message code and k)'
H_OUT = 'METRICS.md rule 13 (output adapter); harness README 2.7.3'
H_CNT = 'harness README 2.7.4 (counter that only counts); METRICS.md rule 13'
H_EMIT = "harness README 2.7 and harnesses/README.md 11 (the emit stub's binding)"
P_FACTS = 'METRICS.md rule 6 (the facts of pick, stated by the problem, in their order); class P'
P_CONST = 'harness README 2.7 (reading the constants is the stage information); class P'
P_BLOCK = 'METRICS.md rule 10 (the program block that holds the query takes the class of the query)'

# ---------------------------------------------------------------- P11a, P11b
def p11ab(b):
    """b: True for P11b (emit before the test)."""
    spec = [
        ((1,), 'P', 'program block: begin (its end is the last token)', P_BLOCK),
        ((8,), 'H', 'declaration of n, cap, m, i, code, k (instance line and message words, n and cap unused)', H_DECL),
        ((8, 'j'), 'P', 'declaration of j, nf, c, xv, cur (fact loop variable, the facts, the constant c, x, the position in pick)', 'class P (variables of the problem\'s encoding)'),
        ((9,), 'C', 'declaration of ok (the flag that stops the search at the first outcome)', 'METRICS.md rule 2 (it changes both the reported value and the effects); P11 any-one query'),
        ((10,), 'P', 'declaration of the array fv, the facts of pick', 'class P (encoding of pick\'s facts; systems file, Values)'),
        ((10, 'pk'), 'H', 'declaration of the array pk, counters of pick\'s facts', H_CNT),
        ((12,), 'H', 'procedure num: prints an integer', H_OUT),
        ((29,), 'H', 'procedure emit: the effect stub bound as printing [emit]', H_EMIT),
        ((35,), 'H', 'reading the instance line and the message (code, k)', H_READ),
        ((39,), 'P', 'reading pick\'s facts and c (stage 1 constants)', P_CONST),
        ((40, 'pk'), 'H', 'pk[j] := 0, counter initialisation', H_CNT),
        ((40, 'end'), 'P', 'end of the fact-reading loop; reading c', P_CONST),
        ((44,), 'C', 'ok := false', 'METRICS.md rule 2 (stop-at-first flag)'),
        ((44, 'cur'), 'P', 'cur := 0, and the loop over pick\'s facts in order (for j := 0 while ...)', P_FACTS + '; rule 10 (loop header)'),
        ((45, '¬'), 'C', 'not ok and: the loop ends at the first outcome that passes', 'METRICS.md rule 2 (like once/1 or a cut: removing it also emits for later facts, changing the effects); rule 10'),
        ((45, 'cur'), 'P', 'cur < nf do begin cur := cur + 1 (the next fact of pick)', P_FACTS),
        ((47, 'pk'), 'H', 'pk[cur] := pk[cur] + 1, counter of applications of pick\'s facts', H_CNT),
        ((48,), 'P', 'xv := fv[cur]: pick gives x its value', P_FACTS),
    ]
    if not b:
        spec += [
            ((49,), 'P', 'if x >= c then begin emit(x): the test, then the effect, in the order written', 'class P (comparison and emit are problem tokens, P11 Rules); rule 2 (guard on the case\'s own condition)'),
            ((52,), 'C', 'ok := true: marks the first outcome, ending the search', 'METRICS.md rule 2'),
            ((53,), 'P', 'end of the if and of the loop', 'METRICS.md rule 10'),
            ((56,), 'H', 'printing the answer [answer]x[/answer]', H_OUT),
            ((59,), 'H', 'observe block', H_OUT + '; counters 2.7.4'),
            ((66,), 'P', 'program block: end', P_BLOCK),
        ]
    else:
        spec += [
            ((49,), 'P', 'emit(x), then if x >= c then: the effect before the test, in the order written', 'class P (emit and the comparison are problem tokens, P11 Rules)'),
            ((50, 'ok'), 'C', 'ok := true: marks the first outcome, ending the search', 'METRICS.md rule 2'),
            ((51,), 'P', 'end of the loop', 'METRICS.md rule 10'),
            ((53,), 'H', 'printing the answer [answer]x[/answer]', H_OUT),
            ((56,), 'H', 'observe block', H_OUT + '; counters 2.7.4'),
            ((63,), 'P', 'program block: end', P_BLOCK),
        ]
    return spec

# ---------------------------------------------------------------- P11c, P11d
R19 = 'METRICS.md rule 19 (code written for this problem\'s own relations that holds them until later stages and then decides them: R, core configuration)'
R19E = 'METRICS.md rule 19, evaluator split (testing a fully known relation is P)'

def p11cd(d):
    """d: True for P11d (commit at stage 2, x != c at stage 3)."""
    spec = [
        ((1,), 'P', 'program block: begin', P_BLOCK),
        ((8,), 'H', 'declaration of n, cap, m, i, code, k (instance line, message words, message-loop variable)', H_DECL),
        ((8, 'j'), 'P', 'declaration of j, nf, c, xv, cur, cv (fact loop variable, the facts, the constant, x, the position in pick, the committed value v)', 'class P'),
        ((8, 'untried'), 'H', 'declaration of untried (computed only for the observe block)', H_CNT),
        ((9,), 'R', 'declaration of picked, xk, and the flags of the relations posed (r2/r3, committed)', R19 + ': what is known and what is held'),
        ((10,), 'P', 'declaration of the array fv, the facts of pick', 'class P'),
        ((10, 'pk'), 'H', 'declaration of the array pk, counters', H_CNT),
        ((12,), 'R', 'Boolean procedure holds(x): heading, and the holding test of the first relation (if posed then ...)', R19),
    ]
    if not d:
        spec += [
            ((15, 'x', 1), 'P', 'x different from c2: the relation of stage 2, tested', R19E),
            ((15, 'else', 1), 'R', 'else true): the relation not yet posed', R19),
            ((15, '∧'), 'P', 'and: the conjunction of the relations posed', 'class P (connective); rule 10'),
            ((15, '(', 2), 'R', '(if committed then', R19),
            ((15, 'x', 2), 'P', 'x = v: the commitment as information, tested', R19E),
            ((15, 'else', 2), 'R', 'else true)', R19),
        ]
    else:
        spec += [
            ((15, 'x', 1), 'P', 'x = v: the commitment as information, tested', R19E),
            ((15, 'else', 1), 'R', 'else true): the relation not yet posed', R19),
            ((15, '∧'), 'P', 'and: the conjunction of the relations posed', 'class P (connective); rule 10'),
            ((15, '(', 2), 'R', '(if r3 then', R19),
            ((15, 'x', 2), 'P', 'x different from c3: the relation of stage 3, tested', R19E),
            ((15, 'else', 2), 'R', 'else true)', R19),
        ]
    spec += [
        ((17,), 'H', 'procedure num: prints an integer', H_OUT),
        ((34,), 'H', 'procedure emit: the effect stub', H_EMIT),
        ((39,), 'R', 'procedure advance: heading and body block, which resumes pick\'s facts after the one held when a later stage refutes it', R19 + ' (the position reached in pick, held across stages)'),
        ((42,), 'C', 'Boolean ok; ok := false: the stop-at-first flag', 'METRICS.md rule 2'),
        ((44,), 'P', 'for j := 0 while (loop over pick\'s facts, in order)', P_FACTS + '; rule 10'),
        ((44, '¬'), 'C', 'not ok and: the loop ends at the first outcome that passes', 'METRICS.md rule 2'),
        ((44, 'cur'), 'P', 'cur < nf do begin cur := cur + 1', P_FACTS),
        ((46, 'pk'), 'H', 'pk[cur] := pk[cur] + 1', H_CNT),
        ((47,), 'P', 'xv := fv[cur]; emit(xv): pick gives x its value, and the effect, in the order written', 'class P (emit is a problem token, P11 Rules)'),
        ((49,), 'C', 'ok := (the flag set from the test)', 'METRICS.md rule 2; rule 10'),
        ((49, 'holds'), 'P', 'holds(xv): the conjunction of the relations posed after pick, applied to x; end of the loop', 'class P (the problem\'s conjuncts, tested); rule 10'),
        ((51,), 'R', 'xk := ok; end advance: records whether x holds a value', R19),
        ((55,), 'H', 'reading the instance line', H_READ),
        ((57,), 'R', 'initialisation of the holding flags and of the position in pick', R19),
        ((59,), 'H', 'message loop: for i := 1 while true do begin; reading code and k; if code = 3 then begin', H_LOOP + '; 2.7.1'),
        ((66,), 'H', 'reading the replayed value v', H_READ + ' (the statement that reads the replayed value v)'),
        ((66, 'committed'), 'P', 'committed := true: the replayed commitment added as the information x = v', 'harness README 2.7.1 (turning v into x = v is classed by METRICS.md); class P (commit is a problem token, P11 Rules)'),
        ((67,), 'H', 'dispatch: end else if k = 1 then begin', H_LOOP),
        ((71,), 'P', 'reading pick\'s facts (stage 1 constants)', P_CONST),
        ((72, 'pk'), 'H', 'pk[j] := 0', H_CNT),
        ((72, 'end'), 'P', 'end of the fact-reading loop', P_CONST),
        ((73,), 'R', 'picked := true: records that pick has been posed', R19),
        ((73, 'cur'), 'P', 'cur := 0; advance: stage 1, pick(x) and emit(x), the first fact tried', 'class P (the stage-1 conjunction applied)'),
        ((75,), 'H', 'dispatch: end else if k = 2 then begin', H_LOOP),
    ]
    if not d:
        spec += [
            ((76, 'begin', 1, 1), 'P', 'reading c2 (stage 2 constant)', P_CONST),
            ((76, 'r2'), 'R', 'r2 := true: records that x != c2 is held', R19),
            ((76, 'end'), 'H', 'dispatch: end else if k = 3 then begin', H_LOOP),
            ((80,), 'R', 'if xk then: commit only if an outcome is held', R19 + ' (test of what is known)'),
            ((80, 'begin'), 'P', 'begin cv := xv; committed := true end: commit selects the outcome held and adds x = v', 'class P (commit is a problem token, P11 Rules)'),
            ((81,), 'H', 'end of the dispatch', H_LOOP),
        ]
    else:
        spec += [
            ((79,), 'R', 'if xk then: commit only if an outcome is held', R19 + ' (test of what is known)'),
            ((79, 'begin'), 'P', 'begin cv := xv; committed := true end: commit selects the outcome held and adds x = v', 'class P (commit is a problem token, P11 Rules)'),
            ((80,), 'H', 'dispatch: end else if k = 3 then begin', H_LOOP),
            ((81, 'begin', 1, 1), 'P', 'reading c3 (stage 3 constant)', P_CONST),
            ((81, 'r3'), 'R', 'r3 := true: records that x != c3 is held', R19),
            ((81, 'end'), 'H', 'end of the dispatch', H_LOOP),
        ]
    spec += [
        ((84,), 'R', 'if xk then begin if not: re-test of the held outcome after the stage', R19),
        ((84, 'holds'), 'P', 'holds(xv): the relations posed, applied to x', R19E),
        ((84, 'then', 2), 'R', 'then advance end: resumption of pick\'s untried facts when the outcome is refuted', R19),
        ((87,), 'H', 'printing the answer', H_OUT),
        ((90,), 'H', 'untried := ...; observe block; end of the message loop', H_OUT + '; ' + H_CNT),
        ((110,), 'P', 'program block: end', P_BLOCK),
    ]
    return spec

# ---------------------------------------------------------------- P12
R3 = 'METRICS.md rule 3 (an argument the problem does not give: the continuation through which each solution of choice reaches accept)'
P_ENC = 'METRICS.md rule 15 (operations on the systems file\'s encoding of sequences are P)'
P_CH = 'METRICS.md rule 3 (mode-faithful transcription of choice, one branch per case, in the direction the query uses); rule 6 (e = l or e = r, the disjunction the problem states, in its order)'
P12 = [
    ((1,), 'P', 'program block: begin', P_BLOCK),
    ((8,), 'P', 'declaration of n (instance parameter the program uses)', 'harness README 2.7 (not H: instance parameters as the program uses them)'),
    ((8, 'cap'), 'C', 'declaration of cap (used only to choose stopping at the first answer)', 'harness README 2.7 (not H); METRICS.md rule 1/2'),
    ((8, 'm'), 'H', 'declaration of m, i, code, k', H_DECL),
    ((10,), 'H', 'reading the instance line and the message', H_READ),
    ((13,), 'P', 'inner block: begin', P_BLOCK),
    ((14,), 'P', 'declaration of top, lcode, rcode, nfacts, f, len, sv', P_ENC + '; class P'),
    ((14, 'nsol'), 'H', 'declaration of nsol, cand, ch1, ch2, depth, peakdepth, pend, peakpend (counters)', H_CNT),
    ((15,), 'C', 'declaration of anyone', 'METRICS.md rule 1 (stopping early changes only what is computed, not the collected answers)'),
    ((16,), 'P', 'declaration of the arrays hd, tl, fact (the sequence encoding and accept\'s facts)', P_ENC),
    ((18,), 'P', 'procedure cons: construction of a sequence cell', P_ENC),
    ((23,), 'P', 'procedure readseq: reading a fact of accept into the encoding', P_CONST + '; ' + P_ENC),
    ((38,), 'P', 'procedure same: equality of sequences', P_ENC + '; accept tested by equality with its facts'),
    ((43,), 'P', 'procedure choice(n, s', P_CH),
    ((43, 'found'), 'R', ', found', R3),
    ((43, ')'), 'P', '); value n; integer n, s', P_CH),
    ((44, 'procedure'), 'R', 'procedure found (specification of the continuation)', R3),
    ((46,), 'P', 'begin integer c (body of choice)', P_CH),
    ((49,), 'H', 'ch1 := ch1 + 1', H_CNT),
    ((50,), 'P', 'case 1: s := the empty sequence', P_CH),
    ((51,), 'R', 'found: the solution passed on through the continuation', R3),
    ((53,), 'P', 'case 2: if n > 0 then begin c := cons(0, 0); s := c', P_CH + '; rule 2 (the guard of the case itself)'),
    ((57,), 'H', 'depth, peakdepth, pend, peakpend, ch2 counters', H_CNT),
    ((60,), 'P', 'e = l: hd[c] := lcode; choice(n - 1, tl[c]', P_CH),
    ((61, 'found'), 'R', ', found', R3),
    ((61, ')'), 'P', ')', P_CH),
    ((62,), 'H', 'pend, ch2 counters', H_CNT),
    ((64,), 'P', 'e = r: hd[c] := rcode; choice(n - 1, tl[c]', P_CH),
    ((65, 'found'), 'R', ', found', R3),
    ((65, ')'), 'P', ')', P_CH),
    ((66,), 'H', 'depth := depth - 1', H_CNT),
    ((67,), 'C', 'top := top - 1: frees the cell for reuse', 'METRICS.md rule 16 (a reset that only lets store be reused)'),
    ((68,), 'P', 'end of case 2 and of choice', P_CH),
    ((71,), 'H', 'procedure printseq: prints a sequence', H_OUT),
    ((86,), 'P', 'procedure accept: heading, body, loop over its facts in order', 'METRICS.md rule 6 (accept is given by facts in a closed world); rule 10'),
    ((90,), 'H', 'cand := cand + 1', H_CNT),
    ((91,), 'P', 'for f over the facts: if s equals fact f then begin', 'METRICS.md rule 6; rule 15'),
    ((95,), 'H', 'nsol counter, printing the answer and the candidates so far', H_OUT + '; ' + H_CNT),
    ((98,), 'C', 'if anyone then go to done: the search is left at the first solution', 'METRICS.md rule 1 (the harness collects the first cap answers either way; only the work done changes)'),
    ((99,), 'P', 'end of accept', 'METRICS.md rule 10'),
    ((103,), 'P', 'top := 0; lcode := 1; rcode := 2: the encoding and atom codes', P_ENC),
    ((105,), 'C', 'anyone := cap = 1', 'METRICS.md rule 1'),
    ((106,), 'H', 'counter initialisation', H_CNT),
    ((109,), 'P', 'reading the facts of accept (stage 1 constants)', P_CONST),
    ((117,), 'P', 'the query: choice(n, s', 'class P (the query, in the order written)'),
    ((117, 'accept'), 'R', ', accept: accept passed as the continuation', R3),
    ((117, ')'), 'P', ')', 'class P (the query)'),
    ((120,), 'C', 'label done: (the exit of the any-one search)', 'METRICS.md rule 1 (with the go to)'),
    ((121,), 'H', 'observe block', H_OUT),
    ((131,), 'P', 'end of the inner block and of the program', P_BLOCK),
]

TEXTS = [
    ('report/P11a.alg', p11ab(False)), ('report/P11b.alg', p11ab(True)),
    ('report/P11c.alg', p11cd(False)), ('report/P11d.alg', p11cd(True)),
    ('report/P12a.n12.all.alg', P12),
    ('x1/P11a.a60', p11ab(False)), ('x1/P11b.a60', p11ab(True)),
    ('x1/P11c.a60', p11cd(False)), ('x1/P11d.a60', p11cd(True)),
    ('x1/P12a.n12.all.a60', P12),
]

result = {}
totals = {}
for name, spec in TEXTS:
    toks = load_tokens(os.path.join(TOK, name + '.tokens.tsv'))
    spans = spans_for(toks, spec)
    result[name] = spans
    t = {}
    for sp in spans:
        t[sp['class']] = t.get(sp['class'], 0) + sp['to'] - sp['from'] + 1
    totals[name] = (len(toks), t)
    if '-v' in sys.argv:
        text = {i: x for i, _, x in toks}
        for sp in spans:
            print(name, sp['class'], sp['from'], sp['to'], ' '.join(text[i] for i in range(sp['from'], sp['to'] + 1))[:160])
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, 'tokens.json'), 'w') as f:
    json.dump({'tokens': result, 'totals': {k: {'tokens': v[0], 'by_class': v[1]} for k, v in totals.items()}}, f, indent=1, ensure_ascii=False)
for k, v in totals.items():
    print(k, v[0], dict(sorted(v[1].items())))
