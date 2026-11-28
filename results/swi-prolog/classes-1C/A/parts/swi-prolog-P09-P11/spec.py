# Classifier 1C-A, swi-prolog P09-P11: token class specification.
# Each text is a list of segments (marker, class, construct, rule). A segment
# runs from its marker's token to the token before the next segment's marker.
# Marker: "L" = first token of line L; "L:text" = first token on line L whose
# text is `text`; "L:text:n" = its n-th occurrence on the line; a suffix
# "-k" moves k tokens back (used for the separator before a construct,
# rule 20).

R_CONST = "P: the stage's information (a constant of the CONSTANTS block, SPECIFICATION 'How a problem is stated' 2)"
R_CONSTREAD = "P: reads the stage's constant into the goal, the stage's information (harness README 2.5); memberchk/2 of library(lists), external mechanism (rule 12)"
R_UNK = "H: harness README 12 (unknowns/2 facts)"
R_HEAD = "H: harness README 12 (stage/3, query/2, spawned/4 head with its :-)"
R_END = "H: terminator of a stage/query/spawned clause, whose head is H (rule 10, the tokens that introduce and close a construct take its class)"
R_QFACT = "H: harness README 12 (query/2 fact)"
R_DEF = "P: a definition case as the problem file gives it"
R_GOAL = "P: a conjunct of the stage's information / query"
R_CLPFD = "P: loads library(clpfd), which supplies the problem's arithmetic connectives (#=, #>, ...); without it the program's meaning is lost (rule 1); listed as external mechanism (rule 12)"
R_TABLE = "C: tabling declaration (METRICS class C)"
R_DYN = "C: rule 11, dynamic/1 makes a relation with no clauses fail instead of raising an existence error (listed)"
R_FREEZE = "C: freeze/2 call (METRICS class C); its goal argument is classed on its own (rule 10)"
R_EMIT = "P: emit is a problem token (problems/11 'Rules'); note: harness README 12 lists emit/1 calls as H, the problem file is taken to decide"
R_HCOMMIT = "H: harness README 12 (h_commitment/1 call)"
R_COMMIT = "P: the commit stage's information (problems/11 'Rules': commit is a problem token): on replay x = v, else nothing added"

def const(line, what):
    return (str(line), "P", "constant " + what, R_CONST)

def unk(line):
    return (str(line), "H", "unknowns/2", R_UNK)

def head(line):
    return (str(line), "H", "clause head", R_HEAD)

def end(line):
    return (str(line) + ":.", "H", "clause terminator", R_END)

def qfact(line):
    return (str(line), "H", "query(_, _) fact", R_QFACT)

SPEC = {}

# ---------------------------------------------------------------- P09a
P09a_common = lambda off: [
    (str(34 + off), "P", "loop/1 case 1", R_DEF),
    (str(37 + off), "P", "conc/3 case 1", R_DEF),
    (str(38 + off), "P", "conc/3 case 2", R_DEF),
    (str(41 + off), "P", "rev/2 case 1", R_DEF),
    (str(42 + off), "P", "rev/2 case 2", R_DEF),
    unk(44 + off),
    head(48 + off),
    (str(48 + off) + ":loop", "P", "computation A: loop(x)", R_GOAL),
    end(48 + off),
    head(50 + off),
    (str(50 + off) + ":memberchk", "P", "read the sequence constant", R_CONSTREAD),
    (str(50 + off) + ":rev:1-1", "P", "computation B: rev(<seq>, b)", R_GOAL),
    end(50 + off),
]
SPEC["constraints/P09a.pl"] = [const(30, "rev_first (stage 1 sequence)")] + P09a_common(0)
SPEC["tabling/P09a.pl"] = [const(30, "rev_first (stage 1 sequence)"),
    ("33", "C", ":- table loop/1, conc/3, rev/2", R_TABLE)] + P09a_common(2)

# ---------------------------------------------------------------- P09b
SPEC["constraints/P09b.pl"] = [
    const(23, "a_first_value"), const(24, "a_second_value"), const(25, "b_value"),
    unk(28),
    head(32),
    ("33:memberchk", "P", "read constant k1", R_CONSTREAD),
    ("33:X-1", "P", "x = k1", R_GOAL),
    ("34:memberchk-1", "P", "read constant k2", R_CONSTREAD),
    ("34:X-1", "P", "x = k2", R_GOAL),
    end(34),
    head(36),
    ("36:memberchk", "P", "read constant k", R_CONSTREAD),
    ("36:Y:2-1", "P", "y = k", R_GOAL),
    end(36),
]

# ---------------------------------------------------------------- P09c
def p09c(constl, defs_line, stage_line, qline, kind, table_line=None, clpfd_line=None, oneline=True):
    segs = []
    if clpfd_line:
        segs.append((str(clpfd_line), "P", ":- use_module(library(clpfd))", R_CLPFD))
    segs.append(const(constl, "gen_start"))
    if table_line:
        segs.append((str(table_line), "C", ":- table gen/2, sum3/2", R_TABLE))
    g1, g2, s3 = defs_line
    segs.append((str(g1), "P", "gen case 1: gen(n, <>) if n > 5", R_DEF))
    if kind == "plain":
        segs.append((str(g2), "P", "gen case 2: gen(n, <n> ++ rest) if n =< 5 and gen(n + 1, rest); n + 1 by is/2 in the direction used (rule 8)", R_DEF))
    else:
        segs += [
            (str(g2), "P", "gen case 2 head and n =< 5, n1 = n + 1" + (" (is/2 in the direction used, rule 8)" if kind == "coroutines" else " (clpfd)"), R_DEF),
            (str(g2) + ":freeze-1", "C", "freeze(Rest, ...) around the recursive gen", R_FREEZE),
            (str(g2) + ":gen:2", "P", "recursive conjunct gen(n + 1, rest)", R_DEF),
            (str(g2) + ":):3", "C", "close of freeze/2", R_FREEZE),
            (str(g2) + ":.", "P", "terminator of gen case 2 (clause head P, rule 10)", R_DEF),
        ]
    segs.append((str(s3), "P", "sum3 case 1" + (" (p + q + r = total by is/2, the direction used, rule 8)" if kind != "constraints" else " (clpfd)"), R_DEF))
    segs.append(unk(s3 + 2))
    segs.append(head(stage_line))
    sl = stage_line if oneline else stage_line + 1
    segs.append((f"{sl}:memberchk", "P", "read constant k", R_CONSTREAD))
    if kind == "plain":
        segs.append((f"{sl}:gen-1", "P", "conjunct gen(k, s)", R_GOAL))
    else:
        segs += [
            (f"{sl}:freeze-1", "C", "freeze(S, ...) around gen(k, s)", R_FREEZE),
            (f"{sl}:gen", "P", "conjunct gen(k, s)", R_GOAL),
            (f"{sl}:):4", "C", "close of freeze/2", R_FREEZE),
        ]
    segs.append((f"{sl}:sum3-1", "P", "conjunct sum3(s, total)", R_GOAL))
    segs.append(end(sl))
    segs.append(qfact(qline))
    return segs

SPEC["constraints/P09c.pl"] = p09c(35, (39, 40, 43), 48, 51, "constraints", clpfd_line=31, oneline=False)
SPEC["coroutines/P09c.pl"] = p09c(34, (38, 39, 42), 47, 50, "coroutines", oneline=False)
SPEC["plain/P09c.pl"] = p09c(28, (32, 33, 36), 41, 43, "plain")
SPEC["tabling/P09c.pl"] = p09c(26, (32, 33, 36), 41, 43, "plain", table_line=29)

# ---------------------------------------------------------------- P09d
def p09d(constl, g, s3, stage_line, qline, kind, table_line=None, clpfd_line=None, oneline=True):
    segs = []
    if clpfd_line:
        segs.append((str(clpfd_line), "P", ":- use_module(library(clpfd))", R_CLPFD))
    segs.append(const(constl, "genu_start"))
    if table_line:
        segs.append((str(table_line), "C", ":- table genu/2, sum3/2", R_TABLE))
    if kind == "plain":
        segs.append((str(g), "P", "genu case 1 (n + 1 by is/2, the direction used, rule 8)", R_DEF))
    else:
        segs += [
            (str(g), "P", "genu case 1 head and n1 = n + 1", R_DEF),
            (f"{g}:freeze-1", "C", "freeze(Rest, ...) around the recursive genu", R_FREEZE),
            (f"{g}:genu:2", "P", "recursive conjunct genu(n + 1, rest)", R_DEF),
            (f"{g}:):3", "C", "close of freeze/2", R_FREEZE),
            (f"{g}:.", "P", "terminator of genu case 1 (rule 10)", R_DEF),
        ]
    segs.append((str(s3), "P", "sum3 case 1", R_DEF))
    segs.append(unk(s3 + 2))
    segs.append(head(stage_line))
    sl = stage_line if oneline else stage_line + 1
    segs.append((f"{sl}:memberchk", "P", "read constant k", R_CONSTREAD))
    if kind == "plain":
        segs.append((f"{sl}:genu-1", "P", "conjunct genu(k, s)", R_GOAL))
    else:
        segs += [
            (f"{sl}:freeze-1", "C", "freeze(S, ...) around genu(k, s)", R_FREEZE),
            (f"{sl}:genu", "P", "conjunct genu(k, s)", R_GOAL),
            (f"{sl}:):4", "C", "close of freeze/2", R_FREEZE),
        ]
    segs.append((f"{sl}:sum3-1", "P", "conjunct sum3(s, total)", R_GOAL))
    segs.append(end(sl))
    segs.append(qfact(qline))
    return segs

SPEC["constraints/P09d.pl"] = p09d(34, 39, 42, 47, 50, "constraints", clpfd_line=30, oneline=False)
SPEC["coroutines/P09d.pl"] = p09d(33, 38, 41, 46, 49, "coroutines", oneline=False)
SPEC["plain/P09d.pl"] = p09d(26, 30, 33, 38, 40, "plain")
SPEC["tabling/P09d.pl"] = p09d(25, 31, 34, 39, 41, "plain", table_line=28)

# ---------------------------------------------------------------- P09e
R_EVAL = "P: computing one place of a + b = c from the other two, in any direction (rule 19, evaluator split, applied by analogy; rule 8)"
R_KNOWN = "R: tests of which places are known (rule 19, by analogy: the holding/dispatch, not the relation)"
R_CUT = "C: cut committing to a mode branch (METRICS class C, rule 2)"
R_HEADR = "R: head of a case the problem does not give (the primitive relation written as one clause per direction; rule 3, rule 4)"

SPEC["constraints/P09e.pl"] = [
    ("26", "P", ":- use_module(library(clpfd))", R_CLPFD),
    const(30, "x_is_y_plus"), const(31, "y_is_x_minus"),
    unk(34),
    head(37),
    ("38:memberchk", "P", "read constant k1", R_CONSTREAD),
    ("38:X-1", "P", "x = y + k1 (clpfd #=)", R_GOAL),
    ("39:memberchk-1", "P", "read constant k2", R_CONSTREAD),
    ("39:Y-1", "P", "y = x - k2 (clpfd #=)", R_GOAL),
    end(39),
    qfact(41),
]

def mode_clauses(l1, name, e1, e2, e3):
    # l1, l1+1, l1+2: name(A,B,C) :- nonvar(A), nonvar(B), !, C is ... ; nonvar(A), !, B is ... ; A is ...
    return [
        (str(l1), "R", f"{name} clause 1 head", R_HEADR),
        (f"{l1}:nonvar", "R", "nonvar(A), nonvar(B)", R_KNOWN),
        (f"{l1}:!-1", "C", "cut", R_CUT),
        (f"{l1}:!:1+1", "P", e1, R_EVAL),
        (f"{l1}:.", "R", "terminator (clause head R)", R_HEADR),
        (str(l1 + 1), "R", f"{name} clause 2 head", R_HEADR),
        (f"{l1+1}:nonvar", "R", "nonvar(A)", R_KNOWN),
        (f"{l1+1}:!-1", "C", "cut", R_CUT),
        (f"{l1+1}:!:1+1", "P", e2, R_EVAL),
        (f"{l1+1}:.", "R", "terminator (clause head R)", R_HEADR),
        (str(l1 + 2), "R", f"{name} clause 3 head", R_HEADR),
        (f"{l1+2}:A:2", "P", e3, R_EVAL),
        (f"{l1+2}:.", "R", "terminator (clause head R)", R_HEADR),
    ]

def stage_p09e(hl):
    return [
        head(hl),
        (f"{hl+1}:memberchk", "P", "read constant k1", R_CONSTREAD),
        (f"{hl+1}:sum-1", "P", "x = y + k1, as sum(y, k1, x)", R_GOAL),
        (f"{hl+2}:memberchk-1", "P", "read constant k2", R_CONSTREAD),
        (f"{hl+2}:diff-1", "P", "y = x - k2, as diff(x, k2, y)", R_GOAL),
        end(hl + 2),
    ]

SPEC["plain/P09e.pl"] = (
    [const(27, "x_is_y_plus"), const(28, "y_is_x_minus")]
    + mode_clauses(32, "sum", "C is A + B", "B is C - A", "A is C - B")
    + mode_clauses(37, "diff", "C is A - B", "B is A - C", "A is B + C")
    + [unk(41)] + stage_p09e(44) + [qfact(48)]
)

R_WHEN = "C: when/2 call with its condition (METRICS class C: coroutine calls, delay); its goal argument classed on its own (rule 10)"
def when_wrapper(l, name, inner):
    return [
        (str(l), "R", f"{name}/3 head (wrapper the problem does not give)", R_HEADR),
        (f"{l+1}:when", "C", "when(( two of three places nonvar ), ...", R_WHEN),
        (f"{l+2}:{inner}-1", "R", f"{inner}(A, B, C), the dispatch called when woken", "R: call of the mode dispatcher, part of the holding code the problem does not give (rule 3; rule 19 by analogy)"),
        (f"{l+2}:):2", "C", "close of when/2", R_WHEN),
        (f"{l+2}:.", "R", "terminator (clause head R)", R_HEADR),
    ]

SPEC["coroutines/P09e.pl"] = (
    [const(32, "x_is_y_plus"), const(33, "y_is_x_minus")]
    + when_wrapper(38, "sum", "sum_known")
    + mode_clauses(42, "sum_known", "C is A + B", "B is C - A", "A is C - B")
    + when_wrapper(48, "diff", "diff_known")
    + mode_clauses(52, "diff_known", "C is A - B", "B is A - C", "A is B + C")
    + [unk(56)] + stage_p09e(59) + [qfact(63)]
)

# ---------------------------------------------------------------- P10
R_REPL = "P: the replacing stage 'b becomes e' carried out natively by replacing the fact (retractall/1, assertz/1, named in the systems file's core for replacing state between stages)"
R_READ = "P: reads a named quantity's current value (the value e uses, or the query)"
R_ABSENT = "R: if-then-else for a quantity that has no value yet, a case the problem does not give (rule 3); its contents classed on their own (rule 10)"

def becomes_const(hl, cl, cname, var="V"):
    # stage(k, _, Cs) :- memberchk(c(k, V), Cs), retractall(q(_)), assertz(q(V)).   (one or two lines)
    return [
        head(hl),
        (f"{cl}:memberchk", "P", f"read constant {cname}", R_CONSTREAD),
        (f"{cl}:retractall-1", "P", "replace the fact: retractall then assertz", R_REPL),
        end(cl),
    ]

def becomes_expr(hl, cname, qty, expr):
    # stage(k,_,Cs) :-\n memberchk(c(k,K),Cs), b(B0), V is ..,\n retractall(q(_)), assertz(q(V)).
    l1, l2 = hl + 1, hl + 2
    return [
        head(hl),
        (f"{l1}:memberchk", "P", f"read constant {cname}", R_CONSTREAD),
        (f"{l1}:b-1", "P", "read b's value before the stage", R_READ),
        (f"{l1}:V-1", "P", f"compute e = {expr} by is/2 (rule 8, the direction used)", "P: rule 8"),
        (f"{l2}:retractall-1", "P", f"replace {qty}'s fact", R_REPL),
        end(l2),
    ]

SPEC["constraints/P10a.pl"] = [
    const(31, "b_becomes (stage 1)"), const(33, "b_becomes_b_plus (stage 2)"), const(35, "b_becomes (stage 3)"),
    ("38", "C", ":- dynamic b/1", "C: rule 11 (dynamic declaration; here it changes nothing a stage reads, since b always has a fact when read, so C by rule 1 as well); listed"),
    unk(40),
] + becomes_const(43, 44, "b_becomes") + becomes_expr(46, "b_becomes_b_plus", "b", "b + k") + becomes_const(50, 51, "b_becomes") + [
    ("54", "H", "query head", R_HEAD),
    ("54:b", "P", "the query: b's current value", R_READ),
    ("54:.", "H", "clause terminator", R_END),
]

def p10b(base, kind):
    # base: line of d_equals_times_b constant
    c1 = base
    segs = []
    if kind == "constraints":
        segs.append(("41", "P", ":- use_module(library(clpfd))", R_CLPFD))
    segs += [const(c1, "d_equals_times_b (stage 1)"), const(c1 + 2, "b_becomes (stage 2)"),
             const(c1 + 4, "b_becomes_b_plus (stage 3)"), const(c1 + 6, "b_becomes (stage 4)")]
    dl = c1 + 9
    segs.append((str(dl), "C", ":- dynamic b/1, d_of/2", R_DYN + " (b/1 is read at stage 1 with no fact)"))
    segs.append(unk(dl + 2))
    s1 = dl + 5
    segs += [head(s1), (f"{s1+1}:memberchk", "P", "read constant k", R_CONSTREAD)]
    if kind == "constraints":
        segs.append((f"{s1+1}:assertz-1", "P", "stage 1: assert the standing relation d = k * b as a rule d_of(b, d) :- d #= k * b", "P: the stage's information, a relation that holds at all times, posed by assertz/1 (systems file: assertz for posing definitions)"))
    elif kind == "plain":
        segs.append((f"{s1+1}:assertz-1", "P", "stage 1: assert the standing relation as d_of(b, d) :- d is k * b", "P: the stage's information posed by assertz/1; d from b by is/2, the direction the stages use (rule 8)"))
    else:
        segs += [
            (f"{s1+1}:assertz-1", "P", "stage 1: assertz((d_of(b, d) :- ...", "P: the stage's information posed by assertz/1"),
            (f"{s1+1}:freeze", "C", "freeze(B, ...) in the asserted rule", R_FREEZE),
            (f"{s1+1}:D:2", "P", "d is k * b (rule 8, the direction used)", "P: rule 8"),
            (f"{s1+1}:):4", "C", "close of freeze/2", R_FREEZE),
            (f"{s1+1}:):5", "P", "close of the rule and of assertz", "P: the stage's information posed by assertz/1"),
        ]
    segs.append(end(s1 + 1))
    s2 = s1 + 3
    segs += becomes_const(s2, s2 + 1, "b_becomes")
    s3 = s2 + 3
    segs += becomes_expr(s3, "b_becomes_b_plus", "b", "b + k")
    s4 = s3 + 4
    segs += becomes_const(s4, s4 + 1, "b_becomes")
    q = s4 + 5
    segs += [
        (str(q), "H", "query head", R_HEAD),
        (f"{q}:(:2", "R", "( ... -> ... ; true ): b may have no value", R_ABSENT),
        (f"{q}:b", "P", "b(V): b's current value", R_READ),
        (f"{q}:->", "R", "->", R_ABSENT),
        (f"{q}:B:2", "P", "B = V", "P: equality"),
        (f"{q}:;", "R", "; true )", R_ABSENT),
        (f"{q}:d_of-1", "P", "d_of(B, D): the standing relation applied (the query of d)", R_GOAL),
        (f"{q}:.", "H", "clause terminator", R_END),
    ]
    return segs

SPEC["constraints/P10b.pl"] = p10b(45, "constraints")
SPEC["coroutines/P10b.pl"] = p10b(43, "coroutines")
SPEC["plain/P10b.pl"] = p10b(41, "plain")

SPEC["constraints/P10c.pl"] = [
    const(35, "b_becomes (stage 1)"), const(37, "d_becomes_times_b (stage 2)"),
    const(39, "b_becomes_b_plus (stage 3)"), const(41, "b_becomes (stage 4)"),
    ("44", "C", ":- dynamic b/1, d/1", R_DYN + " (d/1 is read at stage 1 with no fact)"),
    unk(46),
] + becomes_const(49, 50, "b_becomes") + [
    head(52),
    ("53:memberchk", "P", "read constant k", R_CONSTREAD),
    ("53:b-1", "P", "read b's value before the stage", R_READ),
    ("53:V-1", "P", "compute e = k * b by is/2 (rule 8)", "P: rule 8"),
    ("54:retractall-1", "P", "replace d's fact", R_REPL),
    end(54),
] + becomes_expr(56, "b_becomes_b_plus", "b", "b + k") + becomes_const(60, 61, "b_becomes") + [
    ("65", "H", "query head", R_HEAD),
    ("65:b", "P", "b(B): b's current value", R_READ),
    ("65:(:3-1", "R", "( ... -> ... ; true ): d may have no value (with its separator)", R_ABSENT),
    ("65:d", "P", "d(V): d's current value", R_READ),
    ("65:->", "R", "->", R_ABSENT),
    ("65:D:2", "P", "D = V", "P: equality"),
    ("65:;", "R", "; true )", R_ABSENT),
    ("65:.", "H", "clause terminator", R_END),
]

R_HELD = "R: held(y, relation), a relation the problem does not give, written so that a stage's relation can be withdrawn from the database (rule 3; rule 19 first bullet, by analogy: holding written for the problem's own relation)"
R_POSE = "P: the stage's information posed into the database by assertz/1 or withdrawn by retract/1 (systems file core: 'for posing definitions and replacing state between stages')"

def p10d(kind, pl, gl, dl, ul, s1, s2, s3, q, clpfd=None):
    segs = []
    if clpfd:
        segs.append((str(clpfd), "P", ":- use_module(library(clpfd))", R_CLPFD))
    segs += [const(pl, "pick(1)"), const(pl + 1, "pick(2)"), const(pl + 2, "pick(3)"), const(gl, "greater_than (stage 2)"),
             (str(dl), "C", ":- dynamic pick/1, held/2", R_DYN + " (held/2 is read at stage 1 with no fact)"),
             unk(ul),
             head(s1),
             (f"{s1}:forall", "P", "stage 1: pick's closed world of facts asserted, one per constant (forall/2, member/2: external mechanisms)", "P: rule 6, a set of facts the problem states, posed as clauses (systems file: assertz for posing definitions)"),
             end(s1),
             head(s2),
             (f"{s2}:memberchk", "P", "read constant k", R_CONSTREAD),
             (f"{s2}:assertz-1", "P", "assertz( ... ) posing the relation", R_POSE),
             (f"{s2}:held", "R", "held(Y, ... ) wrapper", R_HELD)]
    if kind == "coroutines":
        segs += [(f"{s2}:freeze", "C", "freeze(Y, ...)", R_FREEZE),
                 (f"{s2}:Y:3", "P", "y > k", "P: comparison"),
                 (f"{s2}:):4", "C", "close of freeze/2", R_FREEZE),
                 (f"{s2}:):5", "R", "close of held/2", R_HELD),
                 (f"{s2}:):6", "P", "close of assertz/1", R_POSE)]
    else:
        segs += [(f"{s2}:Y:2", "P", "y > k" + (" (clpfd #>)" if kind == "constraints" else ""), "P: comparison"),
                 (f"{s2}:):4", "R", "close of held/2", R_HELD),
                 (f"{s2}:):5", "P", "close of assertz/1", R_POSE)]
    segs += [end(s2),
             head(s3),
             (f"{s3}:memberchk", "P", "read constant k", R_CONSTREAD),
             (f"{s3}:retract-1", "P", "retract( ... ): withdraw x > k", R_POSE),
             (f"{s3}:held", "R", "held(_, ... ) wrapper", R_HELD)]
    if kind == "coroutines":
        segs += [(f"{s3}:freeze", "C", "freeze(_, ...) pattern of the held goal", R_FREEZE),
                 (f"{s3}:_:4", "P", "_ > k, the relation withdrawn", "P: the withdrawn relation"),
                 (f"{s3}:):4", "C", "close of freeze pattern", R_FREEZE),
                 (f"{s3}:):5", "R", "close of held/2", R_HELD),
                 (f"{s3}:):6", "P", "close of retract/1", R_POSE)]
    else:
        segs += [(f"{s3}:_:3", "P", "_ > k, the relation withdrawn", "P: the withdrawn relation"),
                 (f"{s3}:):4", "R", "close of held/2", R_HELD),
                 (f"{s3}:):5", "P", "close of retract/1", R_POSE)]
    segs += [end(s3),
             (str(q), "H", "query head", R_HEAD),
             (f"{q}:pick", "P", "pick(x)", R_GOAL),
             (f"{q}:forall-1", "R", "forall(held(X, R), call(R)): every held relation applied to x, an interpreter of the held store", R_HELD),
             (f"{q}:.", "H", "clause terminator", R_END)]
    return segs

SPEC["constraints/P10d.pl"] = p10d("constraints", 45, 49, 52, 54, 57, 59, 61, 64, clpfd=41)
SPEC["coroutines/P10d.pl"] = p10d("coroutines", 43, 47, 50, 52, 55, 57, 59, 62)
SPEC["plain/P10d.pl"] = p10d("plain", 40, 44, 47, 49, 52, 54, 56, 59)

# ---------------------------------------------------------------- P11
R_PICK = "P: pick(x) over its closed world of facts (rule 6), member/2 in place of the relation, equivalent in the direction used (rule 9; library(lists), external)"

def p11ab(kind, order, pl, ul, hl, ql, clpfd=None):
    segs = []
    if clpfd:
        segs.append((str(clpfd), "P", ":- use_module(library(clpfd))", R_CLPFD))
    segs += [const(pl, "pick(1)"), const(pl + 1, "pick(2)"), const(pl + 2, "pick(3)"), const(pl + 3, "at_least"),
             unk(ul), head(hl)]
    b = hl + 1
    segs.append((f"{b}:member", "P", "pick(x)", R_PICK))
    def cmp():
        if kind == "coroutines":
            return [(f"{b}:freeze-1", "C", "freeze(X, ...)", R_FREEZE),
                    (f"{b}:X:3" if order == "a" else f"{b}:X:4", "P", "x >= k", "P: comparison"),
                    (f"{b}:):" + ("5" if order == "a" else "6"), "C", "close of freeze/2", R_FREEZE)]
        return [(f"{b}:X:{2 if order == 'a' else 3}-1", "P", "x >= k" + (" (clpfd #>=)" if kind == "constraints" else ""), "P: comparison")]
    if order == "a":
        segs.append((f"{b}:memberchk-1", "P", "read constant k", R_CONSTREAD))
        segs += cmp()
        segs.append((f"{b}:emit-1", "H" if False else "P", "emit(x)", R_EMIT))
    else:
        segs.append((f"{b}:emit-1", "P", "emit(x)", R_EMIT))
        segs.append((f"{b}:memberchk-1", "P", "read constant k", R_CONSTREAD))
        segs += cmp()
    segs.append(end(b))
    segs.append(qfact(ql))
    return segs

SPEC["constraints/P11a.pl"] = p11ab("constraints", "a", 34, 40, 43, 46, clpfd=30)
SPEC["constraints/P11b.pl"] = p11ab("constraints", "b", 34, 40, 43, 46, clpfd=30)
SPEC["coroutines/P11a.pl"] = p11ab("coroutines", "a", 30, 36, 39, 42)
SPEC["coroutines/P11b.pl"] = p11ab("coroutines", "b", 30, 36, 39, 42)
SPEC["plain/P11a.pl"] = p11ab("plain", "a", 28, 34, 37, 40)
SPEC["plain/P11b.pl"] = p11ab("plain", "b", 28, 34, 37, 40)

def p11cd(kind, which, pl, nl, ul, s1, cv):
    segs = [const(pl, "pick(1)"), const(pl + 1, "pick(2)"), const(pl + 2, "pick(3)"),
            const(nl, "not_equal_to (stage %d)" % (2 if which == "c" else 3)), unk(ul),
            head(s1), (f"{s1}:member", "P", "pick(x)", R_PICK), (f"{s1}:emit-1", "P", "emit(x)", R_EMIT), end(s1)]
    def neq(l):
        return [head(l), (f"{l}:memberchk", "P", "read constant k", R_CONSTREAD),
                (f"{l}:" + ("dif" if kind == "dif" else "X:2") + "-1", "P", "x /= k" + (" by dif/2" if kind == "dif" else " by \\=/2, x bound by pick (rule 9)"), "P: the problem's /= (rule 9)"),
                end(l)]
    def commit(l):
        return [head(l),
                (f"{l}:(:2", "P", "( ... -> ... ; true ): the commit stage", R_COMMIT),
                (f"{l}:h_commitment", "H", "h_commitment(V)", R_HCOMMIT),
                (f"{l}:->", "P", "-> committed_value(V, X) ; true )", R_COMMIT),
                end(l)]
    if which == "c":
        segs += neq(s1 + 2) + commit(s1 + 4)
    else:
        segs += commit(s1 + 2) + neq(s1 + 4)
    segs.append(qfact(s1 + 6))
    segs.append((str(cv), "P", "committed_value/2: reads the harness's verbatim answer v back as the equations x = v and calls them (term_string/3, memberchk/2, call/1)", R_COMMIT + "; not an output adapter (rule 13: it computes what the report depends on)"))
    return segs

SPEC["constraints/P11c.pl"] = p11cd("dif", "c", 40, 44, 47, 50, 63)
SPEC["constraints/P11d.pl"] = p11cd("dif", "d", 40, 44, 47, 50, 63)
SPEC["plain/P11c.pl"] = p11cd("neq", "c", 38, 42, 45, 48, 61)
SPEC["plain/P11d.pl"] = p11cd("neq", "d", 38, 42, 45, 48, 61)
