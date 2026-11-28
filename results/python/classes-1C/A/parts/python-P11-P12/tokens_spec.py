"""Token classes for python P11/P12 (batch 1C), classifier A.

Each text has a list of markers. A marker starts a span at a token and the
span runs to the next marker. A marker is
    (anchor, occurrence, col, class, construct, rule)
anchor: a substring of the source line (stripped) that the marker's line
  starts with; occurrence: which matching line (0-based);
col: None = the first token of the line that is not INDENT/DEDENT;
  an int = that token of the line (negative from the end);
  "tok:X" = the first token X on the line; "tok:X:n" its n-th occurrence.
Layout: an INDENT takes the class of the span active when it appears (the
header that opens the block); a DEDENT takes the class of the header whose
block it closes (METRICS rule 10), computed with a stack.
"""

R19 = "METRICS rule 19 (problem-specific code that holds relations across stages: R in core; and in extended, since it is not general)"
R13 = "METRICS rule 13 (output adapter: renders or collects for the harness an answer already computed)"
HSTAGE = "harnesses/python/README.md section 7, items 1-2 (stage loop and stage dispatch)"
HREAD = "harnesses/python/README.md section 7, item 3 (reading s.constants / s.params / s.replay / s.commitment)"
HCALL = "harnesses/python/README.md section 7, item 4 (cp.* calls with arguments that only name or render objects)"
PCONST = "METRICS class P (the information of a stage); harnesses/python/README.md section 7 (constants block entries are the stages' information, classed by the rules, not H)"
PQUERY = "METRICS class P (the query); SPECIFICATION 'any one' queries; harnesses/README.md answers(cap)"
PEMIT = "P11 'Rules': emit and commit are problem tokens (this overrides harnesses/python/README.md section 7 item 4, which lists cp.emit as H)"
SCALL = "METRICS rule 12 (code written for the experiment is S); rule 15 (a general mechanism such as a unifier or a search is S)"
CSEARCH = "METRICS class C (search directive); harnesses/python/S-mechanisms.md (code around S: a search directive is C)"

# --------------------------------------------------------------- core P11a/b
def core_p11ab(order):
    conj = [
        ("def conjunction", 0, None, "P", "conjunction(k): the query pick(x) and %s, in the order written, as a generator of its solutions" % order,
         "METRICS class P (the query's conjunction, in presentation order); rules 1, 3; " + PEMIT),
    ]
    return [
        ("PICK_FACTS", 0, None, "P", "constants block: pick's three facts (stage 1)", PCONST),
        ("AT_LEAST", 0, None, "P", "constants block: k of x >= k (stage 1)", PCONST),
        ("known = {}", 0, None, "H", "known: a dict only exposed to observe() (the answer already computed)", R13),
        ("cp.bindings", 0, None, "H", "cp.bindings(known)", HCALL),
        ("facts = []", 0, None, "P", "facts: pick's closed world, the store stage 1 gives its facts to", "METRICS rule 6 (a set of facts the problem states is P)"),
        ("def pick", 0, None, "P", "pick(x): its facts in order, each matched against x (head test)", "METRICS rules 2, 3, 6 (the facts as cases; the head match is P)"),
        ("def at_least", 0, None, "P", "at_least(v, k): the comparison v >= k evaluated in the direction the query uses", "METRICS rule 8"),
        ("cp.relations", 0, None, "H", "cp.relations(...)", HCALL),
    ] + conj + [
        ("while (s := cp.stage())", 0, None, "H", "stage loop header", HSTAGE),
        ("if s.k == 1", 0, None, "H", "stage dispatch s.k == 1", HSTAGE),
        ("facts[:] = s.constants", 0, None, "P", "stage 1: pick's facts given to the relation", PCONST),
        ("facts[:] = s.constants", 0, "tok:s", "H", "s.constants[...] read", HREAD),
        ("facts[:] = s.constants", 0, -1, "P", "stage 1: pick's facts given to the relation", PCONST),
        ("answers = conjunction(", 0, None, "P", "the query posed: conjunction(k)", PQUERY),
        ("answers = conjunction(", 0, "tok:s", "H", "s.constants[...] read", HREAD),
        ("answers = conjunction(", 0, -2, "P", "the query posed: conjunction(k)", PQUERY),
        ("cp.pending", 0, None, "H", "cp.pending(...)", HCALL),
        ("x = next(answers, None)", 0, None, "P", "the any-one query: one solution taken (next)", PQUERY),
        ("if x is None", 0, None, "H", "report of the stage: 'no solution' or the answer; known['x'] for observe()", R13 + "; " + HREAD + "; " + HCALL),
    ]


# ---------------------------------------------------------- shared P11c/d
def p11cd_common_core():
    return [
        ("known = {}", 0, None, "R", "known: the solution held across stages, which later stages test and replace", R19),
        ("solutions = []", 0, None, "R", "solutions: holder of stage 1's generator across stages", R19),
        ("added = []", 0, None, "R", "added: the relations on x added after stage 1, held", R19),
        ("cp.bindings", 0, None, "H", "cp.bindings / cp.pending / cp.held", HCALL),
        ("facts = []", 0, None, "P", "facts: pick's closed world", "METRICS rule 6"),
        ("def pick", 0, None, "P", "pick(x): its facts in order, each matched against x", "METRICS rules 2, 3, 6"),
        ("def different", 0, None, "P", "different(v, k): evaluator of x != k on a known x", "METRICS rule 19, evaluator (testing a fully known relation is P); rule 8"),
        ("def equal", 0, None, "P", "equal(v, k): evaluator of x = v (the commitment) on a known x", "METRICS rule 19, evaluator; rule 8"),
        ("cp.relations", 0, None, "H", "cp.relations(...)", HCALL),
        ("def holds", 0, None, "R", "holds: dispatch of a held relation by its name", R19 + " (the holding, not the relation)"),
        ("return different(v, k)", 0, None, "P", "holds: the evaluator of x != k applied", "METRICS rule 19 (evaluator: testing a fully known relation is P)"),
        ("return equal(v, k)", 0, None, "P", "holds: the evaluator of x = v applied", "METRICS rule 19 (evaluator)"),
    ]


def p11cd_tail(stage_add, stage_commit, extended):
    m = [
        ("def satisfies", 0, None, "R", "satisfies(v): every held relation tested against the candidate", R19),
    ]
    if extended:
        m += [("def next_solution", 0, None, "R", "next_solution(): the next solution of the held search, x's value in it", R19)]
    m += [
        ("def advance", 0, None, "R", "advance(): keep the held solution, or retry stage 1's alternatives until one satisfies the held relations", R19 + "; removing it changes the values reported (rule 1), so it is not C"),
        ("def add", 0, None, "R", "add(name, k): record a relation and re-decide the held solution", R19),
        ("def commit", 0, None, "P", "commit: the problem's commit stage (select the held v, add x = v)", PEMIT),
        ("if commitment is not None", 0, None, "H", "commit: a replayed commit taken from s.commitment as x = v (decoding the verbatim answer)", HREAD + " (taking s.commitment as x = v)"),
        ("v = known.get(\"x\")", 0, None, "P", "commit: the held solution v selected", PEMIT),
    ]
    if extended:
        m += [("stack.clear()", 0, None, "C", "commit: the search's choice points and the search itself given up (a cut)",
               "METRICS class C (cuts) and rule 2 (commitment beyond the problem's x = v: removing it changes only what is held and, in P11d, which effects later stages would perform); P11 'Rules' (control used to avoid extra)")]
    else:
        m += [("solutions.clear()", 0, None, "C", "commit: stage 1's generator given up (a cut)",
               "METRICS class C (cuts) and rule 2 (commitment beyond the problem's x = v: removing it changes only what is held and, in P11d, which effects later stages would perform); P11 'Rules' (control used to avoid extra)")]
    m += [
        ("def report", 0, None, "H", "report(): the answer, or 'no solution'", R13),
        ("while (s := cp.stage())", 0, None, "H", "stage loop header", HSTAGE),
        ("if s.k == 1", 0, None, "H", "stage dispatch", HSTAGE),
        ("facts[:] = s.constants", 0, None, "P", "stage 1: pick's facts given to the relation", PCONST),
        ("facts[:] = s.constants", 0, "tok:s", "H", "s.constants[...] read", HREAD),
        ("facts[:] = s.constants", 0, -1, "P", "stage 1: pick's facts given to the relation", PCONST),
    ]
    if extended:
        m += [
            ("solutions[:] = [search(", 0, None, "R", "stage 1: the search held across stages", R19),
            ("solutions[:] = [search(", 0, "tok:search", "C", "search(...) directive", CSEARCH),
            ("solutions[:] = [search(", 0, 8, "P", "the query's goals: pick(x) and emit(x), in order", "METRICS class P (the query); " + PEMIT),
            ("solutions[:] = [search(", 0, 27, "C", "search(...) directive: resolution, trail, stack", CSEARCH),
            ("solutions[:] = [search(", 0, -2, "R", "stage 1: the search held across stages", R19),
            ("v = next_solution()", 1, None, "P", "the any-one query: one solution taken", PQUERY),
        ]
    else:
        m += [
            ("solutions[:] = [conjunction()]", 0, None, "R", "stage 1: the generator held across stages", R19),
            ("solutions[:] = [conjunction()]", 0, "tok:conjunction", "P", "the query posed: conjunction() = pick(x) and emit(x)", PQUERY),
            ("solutions[:] = [conjunction()]", 0, -2, "R", "stage 1: the generator held across stages", R19),
            ("v = next(solutions[0], None)", 1, None, "P", "the any-one query: one solution taken (next)", PQUERY),
        ]
    m += [
        ("if v is not None", 2, None, "R", "stage 1: the solution held for later stages", R19),
    ]
    # stage 2 and 3 in the instance's order
    for (anchor, kind) in ((stage_add, "add"), (stage_commit, "commit")):
        pass
    m += [
        ("elif s.k == 2", 0, None, "H", "stage dispatch", HSTAGE),
        ("elif s.k == 3", 0, None, "H", "stage dispatch", HSTAGE),
        ("add(\"!=\", s.constants", 0, None, "P", "the stage's information x != k", "METRICS class P (stage information)"),
        ("add(\"!=\", s.constants", 0, "tok:s", "H", "s.constants[...] read", HREAD),
        ("add(\"!=\", s.constants", 0, -2, "P", "the stage's information x != k", "METRICS class P (stage information)"),
        ("commit(s.commitment)", 0, None, "P", "the commit stage", PEMIT),
        ("commit(s.commitment)", 0, "tok:s", "H", "s.commitment read", HREAD),
        ("commit(s.commitment)", 0, -2, "P", "the commit stage", PEMIT),
        ("if not s.replay", -1, None, "H", "print nothing during a replay; report()", HREAD + "; " + R13),
    ]
    return m


def core_p11cd(which):
    consts = [("PICK_FACTS", 0, None, "P", "constants block: pick's three facts (stage 1)", PCONST),
              ("DIFFERENT_FROM", 0, None, "P", "constants block: k of x != k (stage %s)" % ("2" if which == "c" else "3"), PCONST)]
    return consts + p11cd_common_core() + [
        ("def conjunction", 0, None, "P", "conjunction(): the query pick(x) and emit(x), in order, as a generator of its solutions", "METRICS class P (the query); " + PEMIT),
    ] + p11cd_tail(None, None, extended=False)


# ------------------------------------------------------------- extended S
def ext_mech_head():
    return [
        ("from S.search", 0, None, "S", "import of the listed S mechanism backtracking search (search, undo)", "METRICS rule 12 (S mechanisms used by the program); harnesses/python/S-mechanisms.md"),
        ("from S.suspend", 0, None, "S", "import of the listed S mechanism suspension queue (Var, Queue, deref)", "METRICS rule 12; harnesses/python/S-mechanisms.md"),
    ]


def ext_unify_res():
    return [
        ("def unify", 0, None, "S", "unify(x, y): the program's own unifier (mechanism 'unify')", SCALL),
        ("def children", 0, None, "S", "children(goals): resolution step over any relation (mechanism 'resolution')", SCALL + "; rule 19 (general over relations)"),
        ("def done", 0, None, "S", "done(goals): resolution's solution test (mechanism 'resolution')", SCALL),
    ]


def ext_p11ab(order_goals):
    return ext_mech_head() + [
        ("PICK_FACTS", 0, None, "P", "constants block: pick's three facts (stage 1)", PCONST),
        ("AT_LEAST", 0, None, "P", "constants block: k of x >= k (stage 1)", PCONST),
        ("binder = Queue()", 0, None, "S", "binder: a suspension Queue used only for its bind (part of 'unify')", SCALL),
        ("trail = []", 0, None, "S", "trail: the search's undo trail shared with unify", SCALL),
        ("stack = []", 0, None, "H", "stack: a list made only so that the search's choice points can be registered for observe()", HCALL + "; " + R13),
        ("NIL = ()", 0, None, "S", "NIL: the empty sequence of the shared unify/resolution text; unused in P11", SCALL + " (dead here: copied with the mechanism text)"),
        ("cp.pending", 0, None, "H", "cp.pending(...)", HCALL),
        ("facts = []", 0, None, "P", "facts: pick's closed world", "METRICS rule 6"),
    ] + ext_unify_res() + [
        ("def pick", 0, None, "P", "pick(x): its facts in order as cases, x unified with each (head test)", "METRICS rules 2, 6; the call of S unify is the head match"),
        ("def at_least", 0, None, "P", "at_least(x, k): the comparison x >= k as a relation", "METRICS rule 8"),
        ("def emit", 0, None, "P", "emit(x): the effect as a goal", PEMIT),
        ("cp.relations", 0, None, "H", "cp.relations(...)", HCALL),
        ("while (s := cp.stage())", 0, None, "H", "stage loop header", HSTAGE),
        ("if s.k == 1", 0, None, "H", "stage dispatch", HSTAGE),
        ("facts[:] = s.constants", 0, None, "P", "stage 1: pick's facts", PCONST),
        ("facts[:] = s.constants", 0, "tok:s", "H", "s.constants[...] read", HREAD),
        ("facts[:] = s.constants", 0, -1, "P", "stage 1: pick's facts", PCONST),
        ("x = Var(\"x\")", 0, None, "P", "the query's unknown x", "METRICS class P (the query)"),
        ("cp.bindings", 0, None, "H", "cp.bindings({...})", HCALL),
        ("query = ", 0, None, "P", "the query's goals: pick(x) and %s, in the order written" % order_goals, "METRICS class P (the query, in presentation order); " + PEMIT),
        ("query = ", 0, "tok:s", "H", "s.constants[...] read", HREAD),
        ("query = ", 0, "after:]", "P", "the query's goals (cont.)", "METRICS class P (the query)"),
        ("solutions = search(", 0, None, "C", "search(query, children, done, trail, stack): the search directive", CSEARCH),
        ("if next(solutions, None) is None", 0, None, "H", "report test", R13),
        ("if next(solutions, None) is None", 0, "tok:next", "P", "the any-one query: one solution taken (next)", PQUERY),
        ("if next(solutions, None) is None", 0, "tok:is", "H", "report: 'no solution' or the answer", R13 + "; " + HREAD + "; " + HCALL),
    ]


def ext_p11cd(which):
    return ext_mech_head() + [
        ("PICK_FACTS", 0, None, "P", "constants block: pick's three facts (stage 1)", PCONST),
        ("DIFFERENT_FROM", 0, None, "P", "constants block: k of x != k (stage %s)" % ("2" if which == "c" else "3"), PCONST),
        ("binder = Queue()", 0, None, "S", "binder: a suspension Queue used only for its bind (part of 'unify')", SCALL),
        ("trail = []", 0, None, "S", "trail: the search's undo trail shared with unify", SCALL),
        ("stack = []", 0, None, "H", "stack: a list made so that the search's choice points can be registered for observe()", HCALL + "; " + R13),
        ("NIL = ()", 0, None, "S", "NIL: the empty sequence of the shared unify/resolution text; unused in P11", SCALL + " (dead here)"),
        ("x = Var(\"x\")", 0, None, "P", "the query's unknown x", "METRICS class P (the query)"),
    ] + p11cd_common_core()[:3] + [
        ("cp.bindings", 0, None, "H", "cp.bindings / cp.pending / cp.held", HCALL),
        ("facts = []", 0, None, "P", "facts: pick's closed world", "METRICS rule 6"),
    ] + ext_unify_res() + [
        ("def pick", 0, None, "P", "pick(x): its facts in order as cases, x unified with each", "METRICS rules 2, 6"),
        ("def emit", 0, None, "P", "emit(x): the effect as a goal", PEMIT),
    ] + p11cd_common_core()[6:] + p11cd_tail(None, None, extended=True)


# ------------------------------------------------------------- P12
def core_p12():
    return [
        ("ACCEPT_FACTS", 0, None, "P", "constants block: accept's facts for each n posed (stage 1)", PCONST + "; METRICS rule 6"),
        ("facts = []", 0, None, "P", "facts: accept's closed world", "METRICS rule 6"),
        ("def choice", 0, None, "P", "choice(n): its two cases in order, case 2's disjunction e = 'l or e = 'r in order, s unknown (the direction the query uses)", "METRICS rules 3 (mode-faithful transcription, one branch per case), 2 (n > 0 is case 2's own guard), 6 (the stated disjunction)"),
        ("def accept", 0, None, "P", "accept(s): membership in the closed world's facts with `in`", "METRICS rule 9 (built-in in place of the facts, equivalent in the direction used; listed)"),
        ("cp.relations", 0, None, "H", "cp.relations(...)", HCALL),
        ("def conjunction", 0, None, "P", "conjunction(n): the query choice(n, s) and accept(s), in order", "METRICS class P (the query, in presentation order)"),
        ("def show", 0, None, "H", "show(x): printer of a sequence", R13),
        ("while (st := cp.stage())", 0, None, "H", "stage loop header", HSTAGE),
        ("if st.k == 1", 0, None, "H", "stage dispatch", HSTAGE),
        ("n = st.params", 0, None, "H", "n read from s.params", HREAD),
        ("facts[:] = st.constants", 0, None, "P", "stage 1: accept's facts for this n", PCONST),
        ("facts[:] = st.constants", 0, "tok:st", "H", "st.constants[...][n] read", HREAD),
        ("facts[:] = st.constants", 0, -1, "P", "stage 1: accept's facts for this n", PCONST),
        ("answers = conjunction(n)", 0, None, "P", "the query posed", PQUERY),
        ("cp.pending", 0, None, "H", "cp.pending(...)", HCALL),
        ("if st.params[\"answers\"]", 0, None, "H", "dispatch on the instance's answer mode", HREAD),
        ("found = next(answers, None)", 0, None, "P", "the any-one query: one solution taken (next)", PQUERY),
        ("if found is not None and not st.replay", 0, None, "H", "answer, rendered", R13 + "; " + HREAD + "; " + HCALL),
        ("found = None", 0, None, "H", "else branch of the answer-mode dispatch; found reset for the 'no solution' message", R13 + "; " + HREAD),
        ("for found in answers", 0, None, "P", "the all query: every solution taken in order", PQUERY),
        ("if not st.replay", 0, None, "H", "answer, rendered; 'no solution' message", R13 + "; " + HREAD + "; " + HCALL),
    ]


def ext_p12():
    return ext_mech_head() + [
        ("ACCEPT_FACTS", 0, None, "P", "constants block: accept's facts for each n posed (stage 1)", PCONST + "; METRICS rule 6"),
        ("binder = Queue()", 0, None, "S", "binder: a suspension Queue used only for its bind (part of 'unify')", SCALL),
        ("trail = []", 0, None, "S", "trail: the search's undo trail shared with unify", SCALL),
        ("stack = []", 0, None, "H", "stack: a list made only so that the search's choice points can be registered for observe()", HCALL + "; " + R13),
        ("NIL = ()", 0, None, "P", "NIL: the encoding of <> (cons cells)", "METRICS rule 15 (operations and values of an encoding the systems file defines are P; measurement.md section 2)"),
        ("cp.pending", 0, None, "H", "cp.pending(...)", HCALL),
        ("facts = []", 0, None, "P", "facts: accept's closed world", "METRICS rule 6"),
    ] + ext_unify_res() + [
        ("def equal", 0, None, "P", "equal(a, b): the equality e = 'l / e = 'r as a relation (unify called for it)", "METRICS class P (equality connective); rule 15"),
        ("def either", 0, None, "P", "either(...): the stated disjunction, its alternatives in the order written", "METRICS rule 6 (a disjunction the problem states is P); class P connectives"),
        ("def choice", 0, None, "P", "choice(n, s): its two cases in order, case 2's head <e> ++ t, guard n > 0, the disjunction and the recursive goal", "METRICS rules 2, 3, 6, 15"),
        ("def accept", 0, None, "P", "accept(s): its facts in order as cases, s unified with each", "METRICS rules 6, 15"),
        ("cp.relations", 0, None, "H", "cp.relations(...)", HCALL),
        ("def cons", 0, None, "P", "cons(seq): the encoding of the stage's facts as cons cells", "METRICS rule 15 (construction on the encoding)"),
        ("def show", 0, None, "H", "show(t): printer of a term", R13),
        ("while (st := cp.stage())", 0, None, "H", "stage loop header", HSTAGE),
        ("if st.k == 1", 0, None, "H", "stage dispatch", HSTAGE),
        ("n = st.params", 0, None, "H", "n read from s.params", HREAD),
        ("facts[:] = [cons(f)", 0, None, "P", "stage 1: accept's facts for this n, encoded", PCONST + "; rule 15"),
        ("facts[:] = [cons(f)", 0, "tok:st", "H", "st.constants[...][n] read", HREAD),
        ("facts[:] = [cons(f)", 0, -2, "P", "stage 1: accept's facts for this n, encoded", PCONST),
        ("seq = Var(\"s\")", 0, None, "P", "the query's unknown s", "METRICS class P (the query)"),
        ("cp.bindings", 0, None, "H", "cp.bindings({...})", HCALL),
        ("solutions = search(", 0, None, "C", "search(...) directive", CSEARCH),
        ("solutions = search(", 0, 4, "P", "the query's goals: choice(n, s) and accept(s), in order", "METRICS class P (the query, in presentation order)"),
        ("solutions = search(", 0, 24, "C", "search(...) directive: resolution, trail, stack", CSEARCH),
        ("found = 0", 0, None, "H", "found: a count only for the 'no solution' message", R13),
        ("for _ in solutions", 0, None, "P", "the query: solutions taken one at a time, in order", PQUERY),
        ("found += 1", 0, None, "H", "count; answer rendered", R13 + "; " + HREAD + "; " + HCALL),
        ("if st.params[\"answers\"]", 0, None, "H", "dispatch on the instance's answer mode", HREAD),
        ("break", 0, None, "P", "the any-one query: no further solution asked for", PQUERY),
        ("if found == 0", 0, None, "H", "'no solution' message", R13 + "; " + HREAD),
    ]


SPECS = {
    "core/P11a.py": core_p11ab("x >= k and emit(x)"),
    "core/P11b.py": core_p11ab("emit(x) and x >= k"),
    "core/P11c.py": core_p11cd("c"),
    "core/P11d.py": core_p11cd("d"),
    "core/P12a.py": core_p12(),
    "core/P12b.py": core_p12(),
    "core/P12c.py": core_p12(),
    "core/P12d.py": core_p12(),
    "extended/P11a.py": ext_p11ab("x >= k and emit(x)"),
    "extended/P11b.py": ext_p11ab("emit(x) and x >= k"),
    "extended/P11c.py": ext_p11cd("c"),
    "extended/P11d.py": ext_p11cd("d"),
    "extended/P12a.py": ext_p12(),
    "extended/P12b.py": ext_p12(),
    "extended/P12c.py": ext_p12(),
    "extended/P12d.py": ext_p12(),
}
