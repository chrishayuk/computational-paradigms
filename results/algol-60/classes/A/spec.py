# Classifier A's construct classes for algol-60 batch 1A, as markers (see spans.py).
# Each family is written against the report text; the x1 text has the same lines, and the same markers are
# resolved in it (x1 overrides below where a marker differs). x1sim's texts are identical to x1's (TEXTS.tsv).

PROG = ("P", "the program block (outer begin/end, or an inner block for the encoding)", "rule 10; the block that holds the transcription")
def dec(cls, what, rule): return (cls, "declaration: " + what, rule)

HW = "harness README 2.7.5 (declarations holding only harness words), METRICS rule 13"
INST = ("H", "reading the instance line (n, cap, m and the codes) and, where present, the one message", "harness README 2.7.1; METRICS rule 13")
LOOP = ("H", "the message loop and the dispatch on the message's stage k", "harness README 2.7.2")
ANS = ("H", "printing the answer and the observe block (output adapters, tags, held count, counters' output)", "harness README 2.7.3 and 2.7.4; METRICS rule 13")
ADAPT = ("H", "output adapter procedures (printing names, places, states, held relations, sequences)", "METRICS rule 13; harness README 2.7.3")
CNT = ("H", "a counter that only counts (problem operations or examinations)", "harness README 2.7.4")
CONS = ("P", "cons: construction on the sequence encoding", "METRICS rule 15; systems file, Values")
READSEQ = ("P", "readseq: reading a stage's sequence into the encoding (the stage's information)", "METRICS rule 15; harness README 2.7 (reading constants is the stage information)")
SAME = ("P", "same: equality on the sequence encoding, used to test a fully known relation", "METRICS rule 15, rule 19 (testing a fully known relation)")
CONC = ("P", "conc computing its third place from the first two, by its two cases in order (mode-faithful transcription)", "METRICS rule 3 (case dispatch P), rule 19")
PROP = ("R", "propagate: examines every held relation again until a pass gives no unknown a value (holding, written for this problem's relations)", "METRICS rule 19 (holding code for the problem's own relations is R)")
PROPCALL = ("R", "invoking the propagation of held relations", "METRICS rule 19")
EVR = ("R", "evaluator: the test of which places are known, the release of the held relation, the change flag, and the waiting", "METRICS rule 19 (known-tests, waiting verdict and what is recorded are R)")
EVT = ("P", "evaluator: testing the fully known relation", "METRICS rule 19 (testing a fully known relation is P)")
EVC = ("P", "evaluator: computing one place from the others", "METRICS rule 19 (computing any one place from the others is P)")
POST = ("P", "posing the stage: reading its constants and recording that its relation holds", "the stage's information (METRICS class P); harness README 2.7 (reading constants is P)")
INITR = ("R", "initialising the knownness and held flags", "METRICS rule 19")
INITP = ("P", "initialising the verdict of the relations' tests", "METRICS rule 19 (the verdict of testing a fully known relation)")
INITTOP = ("P", "initialising the cell allocator of the encoding", "METRICS rule 15")
INITCNT = ("H", "initialising counters that only count", "harness README 2.7.4")
LEN = ("P", "reading the stage's constants: the lengths of the known sequences", "harness README 2.7 (reading constants is the stage information); systems file, Values")

def evaluator_P01a():
    return [
        ("11@0", "R", "evaluator heading of equation (a = b by name): formals, known flags and held flag", "METRICS rule 19"),
        ("16:if", *EVT), ("16:r", *EVR), ("18:bv", *EVC), ("18:bk", *EVR), ("20:av", *EVC), ("20:ak", *EVR),
        ("23@0", "R", "evaluator of z = k (value3): heading, known test, release", "METRICS rule 19"),
        ("27:if", *EVT), ("27:end", *EVR), ("29:zv", *EVC), ("29:zk", *EVR),
    ]

SPEC = {}

SPEC["P01a"] = [
    ("1@0", *PROG),
    ("8@0", *dec("H", "n, cap, m, i, code, k (harness words; n, cap, m are read and not used)", HW)),
    ("8:c3", *dec("P", "c3, the constant of stage 3; xv, yv, zv, the values of the unknowns", "stage information and the unknowns' values (METRICS class P)")),
    ("8:held", *dec("H", "held, the count of held equations printed in observe", HW)),
    ("8:pass", *dec("R", "pass, the loop variable of propagate", "METRICS rule 19")),
    ("9@0", *dec("R", "xk, yk, zk (known flags), r1, r2, r3 (held flags), changed", "METRICS rule 19")),
    ("9:inconsistent", *dec("P", "inconsistent, the verdict of the tests of fully known relations", "METRICS rule 19")),
    *evaluator_P01a(),
    ("33@0", *PROP),
    ("46@0", *ADAPT),
    ("75@0", *INST),
    ("77@0", *INITR), ("77:inconsistent", *INITP),
    ("79@0", *LOOP),
    ("83:r1", "P", "posing stage 1: x = y holds", "stage information (METRICS class P)"),
    ("84@0", *LOOP), ("84:r2", "P", "posing stage 2: y = z holds", "stage information"),
    ("85@0", *LOOP), ("85:begin", "P", "posing stage 3: reading k and recording z = k", "stage information; harness README 2.7"),
    ("87@0", *PROPCALL),
    ("90@0", *ANS),
    ("114@0", *PROG),
]

SPEC["P01b"] = [
    ("1@0", *PROG),
    ("8@0", "P", "the capacity of the cell arrays (cells := 1000) and the inner block it sizes", "METRICS rule 15 (the encoding); systems file, Values"),
    ("11@0", *dec("H", "n, cap, m, i, code, k", HW)),
    ("11:len", *dec("P", "len, top, a1, b2, sv, tv: lengths, the allocator, the stage sequences and the unknowns' values", "stage information, unknowns' values, METRICS rule 15")),
    ("11:held", *dec("H", "held, the count printed in observe", HW)),
    ("11:pass", *dec("R", "pass, the loop variable of propagate", "METRICS rule 19")),
    ("11:conc1", *dec("H", "conc1, conc2, counters of conc's cases", "harness README 2.7.4")),
    ("12@0", *dec("R", "sk, tk (known flags), r1, r2 (held flags), changed", "METRICS rule 19")),
    ("12:inconsistent", *dec("P", "inconsistent, the verdict of the tests", "METRICS rule 19")),
    ("13@0", *dec("P", "the cell arrays hd, tl of the sequence encoding", "METRICS rule 15")),
    ("15@0", *CONS), ("20@0", *READSEQ), ("35@0", *SAME),
    ("40@0", *CONC), ("44:conc1", *CNT), ("44:conc", *CONC), ("48@0", *CNT), ("49@0", *CONC),
    ("53@0", "R", "evaluator of conc(a1, s, t) (examine1): heading, the test that s is known, and the waiting", "METRICS rule 19"),
    ("57@0", *EVC), ("59@0", *EVR), ("59:if#2", *EVT), ("59:end", *EVR), ("60:tv", *EVC), ("60:tk", *EVR),
    ("64@0", "R", "evaluator of s = b2 (examine2): heading, known test, release", "METRICS rule 19"),
    ("67:if#2", *EVT), ("67:end", *EVR), ("68:sv", *EVC), ("68:sk", *EVR),
    ("72@0", *PROP),
    ("84@0", *ADAPT),
    ("111@0", *INST),
    ("113@0", *INITR), ("113:inconsistent", *INITP),
    ("114@0", *INITTOP), ("114:conc1", *INITCNT),
    ("116@0", *LOOP),
    ("120:begin", "P", "posing stage 1: reading a and recording conc(a, s, t)", "stage information"),
    ("121@0", *LOOP), ("121:begin", "P", "posing stage 2: reading b and recording s = b", "stage information"),
    ("123@0", *PROPCALL),
    ("126@0", *ANS),
    ("153@0", *PROG),
]

SPEC["P01c"] = [
    ("1@0", *PROG),
    ("8@0", *dec("H", "n, cap, m, i, code, k", HW)),
    ("8:len", *dec("P", "len, the length of a", "stage information")),
    ("10@0", *INST),
    ("14@0", *LEN),
    ("16@0", *dec("P", "top, a1, xv: the allocator, the known sequence a, the value of x", "METRICS rule 15; the unknown's value")),
    ("16:held", *dec("H", "held, conc1, conc2: observe count and counters", "harness README 2.7.4, 2.7.5")),
    ("17@0", *dec("R", "xk (known flag), r1 (held flag)", "METRICS rule 19")),
    ("17:inconsistent", *dec("P", "inconsistent, the verdict of the test", "METRICS rule 19")),
    ("18@0", *dec("P", "the cell arrays hd, tl of the sequence encoding", "METRICS rule 15")),
    ("20@0", *CONS), ("25@0", *READSEQ), ("40@0", *SAME),
    ("45@0", *CONC), ("49:conc1", *CNT), ("49:conc", *CONC), ("53@0", *CNT), ("54@0", *CONC),
    ("58@0", "R", "evaluator of x = a1 ++ x (examine1): heading, the test that x is known, and the waiting", "METRICS rule 19"),
    ("62@0", *EVT), ("63@0", *EVR),
    ("66@0", *ADAPT),
    ("86@0", *INITR), ("86:inconsistent", *INITP),
    ("87@0", *INITTOP), ("87:conc1", *INITCNT),
    ("88@0", "P", "posing the stage: reading a and recording x = a ++ x", "stage information"),
    ("90@0", "R", "invoking the evaluator of the held relation", "METRICS rule 19"),
    ("93@0", *ANS),
    ("115@0", *PROG),
]

def P02_evaluators():
    return [
        ("11@0", "R", "evaluator of R1, u + v = c1 (examine1): heading and the known tests", "METRICS rule 19"),
        ("14@0", *CNT), ("15@0", *EVR),
        ("16:if", *EVT), ("16:r1", *EVR), ("18:vv", *EVC), ("18:vk", *EVR), ("20:uv", *EVC), ("20:uk", *EVR),
        ("23@0", "R", "evaluator of R2, w . u = v (examine2): heading and the known tests", "METRICS rule 19"),
        ("26@0", *CNT), ("27@0", *EVR),
        ("28:if", *EVT), ("28:r2", *EVR), ("30:vv", *EVC), ("30:vk", *EVR),
        ("33@0", "P", "evaluator: computing w from u and v over the integers (u = 0, divisibility)", "METRICS rule 19 (computing one place is P in every direction)"),
        ("36:wk", *EVR), ("36:end", "P", "evaluator: computing w from u and v over the integers (u = 0, divisibility)", "METRICS rule 19"),
        ("38@0", *EVR),
        ("42@0", "P", "evaluator: computing u from w and v over the integers (w = 0, divisibility)", "METRICS rule 19"),
        ("45:uk", *EVR), ("45:end", "P", "evaluator: computing u from w and v over the integers", "METRICS rule 19"),
        ("47@0", *EVR),
        ("51@0", "R", "evaluator of R3, u + a3 = b3 (examine3): heading and the known test", "METRICS rule 19"),
        ("54@0", *CNT), ("55@0", *EVR),
        ("56:if", *EVT), ("56:end", *EVR), ("58:uv", *EVC), ("58:uk", *EVR),
        ("62@0", *PROP),
        ("75@0", *ADAPT),
    ]
P02_DECL = [
    ("1@0", *PROG),
    ("8@0", *dec("H", "n, cap, m, i, code, k", HW)),
    ("8:c1", *dec("P", "c1, a3, b3 (the constants of R1 and R3) and uv, vv, wv (the values of the unknowns)", "stage information and the unknowns' values")),
    ("8:held", *dec("H", "held, the count printed in observe", HW)),
    ("8:pass", *dec("R", "pass, the loop variable of propagate", "METRICS rule 19")),
    ("8:x1", *dec("H", "x1, x2, x3, counters of examinations", "harness README 2.7.4")),
    ("9@0", *dec("R", "uk, vk, wk (known flags), r1, r2, r3 (held flags), changed", "METRICS rule 19")),
    ("9:inconsistent", *dec("P", "inconsistent, the verdict of the tests", "METRICS rule 19")),
]
SPEC["P02a"] = P02_DECL + P02_evaluators() + [
    ("115@0", *INST),
    ("117@0", *INITR), ("117:inconsistent", *INITP),
    ("118@0", *INITCNT),
    ("120@0", *LOOP),
    ("124:begin", "P", "posing stage 1: reading c and recording R1", "stage information"),
    ("125@0", *LOOP), ("125:r2", "P", "posing stage 2: recording R2", "stage information"),
    ("126@0", *LOOP), ("126:begin", "P", "posing stage 3: reading a, b and recording R3", "stage information"),
    ("128@0", *PROPCALL),
    ("131@0", *ANS),
    ("158@0", *PROG),
]
SPEC["P02b"] = P02_DECL + P02_evaluators() + [
    ("115@0", *INST),
    ("116@0", "P", "the inner block that holds the instance's order", "rule 10"),
    ("117@0", *dec("H", "r, the code of the relation the message's stage poses, used only by the dispatch", HW)),
    ("118@0", *dec("P", "order, the instance's presentation order, a parameter the program uses", "harness README 2.7 (not H: an order as the program uses it); SPECIFICATION, presentation order")),
    ("119@0", ("H"), "reading the instance line's codes into order", "harness README 2.7.1"),
    ("120@0", *INITR), ("120:inconsistent", *INITP),
    ("121@0", *INITCNT),
    ("123@0", "H", "the message loop and the dispatch on the stage, through order[k]", "harness README 2.7.2"),
    ("129:begin", "P", "posing R1: reading c and recording R1", "stage information"),
    ("130@0", *LOOP), ("130:r2", "P", "posing R2: recording R2", "stage information"),
    ("131@0", *LOOP), ("131:begin", "P", "posing R3: reading a, b and recording R3", "stage information"),
    ("133@0", *PROPCALL),
    ("136@0", *ANS),
    ("163@0", *PROG),
]
SPEC["P02c"] = P02_DECL + P02_evaluators() + [
    ("115@0", *INST),
    ("117@0", *INITR), ("117:inconsistent", *INITP),
    ("118@0", *INITCNT),
    ("121@0", ("H"), "reading the one message", "harness README 2.7.1"),
    ("123@0", "P", "posing the one stage: R1, R2 and R3 in that order, with their constants", "stage information"),
    ("127@0", *PROPCALL),
    ("130@0", *ANS),
    ("156@0", *PROG),
]

def p03_head(lens_decl_marker, lens_what):
    return [
        ("1@0", *PROG),
        ("8@0", *dec("H", "n, cap, m, i, code, k", HW)),
        (lens_decl_marker, *dec("P", lens_what, "stage information")),
        ("10@0", *INST),
        ("14@0", *LEN),
        ("15@0", *PROG),
    ]
DIRFN = "METRICS rule 14 (a separately written function for a direction is R throughout, head tests included); rule 3"
EXTRA = "METRICS rules 3 and 5 (an extra argument the problem does not give)"

SPEC["P03a"] = p03_head("8:la", "la, lb, the lengths of a and b") + [
    ("16@0", *dec("P", "top, a1, b1, c1: allocator, a, b and the answer c", "METRICS rule 15; the query")),
    ("16:conc1", *dec("H", "conc1, conc2 counters", "harness README 2.7.4")),
    ("17@0", *dec("P", "the cell arrays hd, tl, sized from the lengths", "METRICS rule 15")),
    ("19@0", *CONS), ("24@0", *READSEQ),
    ("39@0", *CONC), ("43:conc1", *CNT), ("43:conc", *CONC), ("47@0", *CNT), ("48@0", *CONC),
    ("52@0", *ADAPT),
    ("63@0", *INITTOP), ("63:conc1", *INITCNT),
    ("64@0", "P", "reading a and b (the query's known places)", "stage information"),
    ("66@0", "P", "the query conc(a, b, c), c computed from a and b", "METRICS rule 3 (the direction the query uses)"),
    ("68@0", *ANS),
    ("73@0", *PROG),
]
SPEC["P03b"] = p03_head("8:lc", "lc, the length of c") + [
    ("16@0", *dec("P", "top, c0: allocator and the known c", "METRICS rule 15")),
    ("16:answers", *dec("H", "answers, conc1, conc2: counters", "harness README 2.7.4")),
    ("17@0", *dec("P", "the cell arrays hd, tl", "METRICS rule 15")),
    ("17:path", *dec("R", "path, the heads taken so far, an extra argument of the search", EXTRA)),
    ("17:[", *dec("P", "the bounds of the cell arrays (shared with path)", "METRICS rule 15")),
    ("19@0", *CONS), ("24@0", *READSEQ),
    ("39@0", *ADAPT),
    ("61@0", "R", "split: conc(a, b, c) with c known, a separately written direction function, with the extra argument d", DIRFN),
    ("65@0", *CNT), ("67@0", "H", "printing each answer split finds (output adapter)", "METRICS rule 13; harness README 2.7.3"),
    ("68@0", "R", "split: case 2, c = h followed by c1, recursion with path extended", DIRFN),
    ("70@0", *CNT), ("71@0", "R", "split: case 2, c = h followed by c1, recursion with path extended", DIRFN),
    ("76@0", *INITTOP), ("76:answers", *INITCNT),
    ("77@0", "P", "reading c (the query's known place)", "stage information"),
    ("79@0", "R", "the query, as a call of the direction function with its extra argument", DIRFN + "; " + EXTRA),
    ("81@0", *ANS),
    ("86@0", *PROG),
]
SPEC["P03c"] = p03_head("8:la", "la, lc, the lengths of a and c") + [
    ("16@0", *dec("P", "top, a0, c0: allocator and the known a and c", "METRICS rule 15")),
    ("16:answers", *dec("H", "answers, conc1, conc2: counters", "harness README 2.7.4")),
    ("17@0", *dec("P", "the cell arrays hd, tl", "METRICS rule 15")),
    ("19@0", *CONS), ("24@0", *READSEQ),
    ("39@0", *ADAPT),
    ("50@0", "R", "strip: conc(a, b, c) with a and c known, a separately written direction function", DIRFN),
    ("56@0", *CNT), ("58@0", "H", "printing the answer strip finds (output adapter)", "METRICS rule 13"),
    ("59@0", "R", "strip: case 2, a and c both begin with h, recursion", DIRFN),
    ("65:conc2", *CNT), ("65:strip", "R", "strip: case 2, recursion", DIRFN),
    ("70@0", *INITTOP), ("70:answers", *INITCNT),
    ("71@0", "P", "reading a and c (the query's known places)", "stage information"),
    ("73@0", "R", "the query, as a call of the direction function", DIRFN),
    ("75@0", *ANS),
    ("80@0", *PROG),
]
SPEC["P03d"] = p03_head("8:lb", "lb, lc, the lengths of b and c") + [
    ("16@0", *dec("P", "top, b0, c0: allocator and the known b and c", "METRICS rule 15")),
    ("16:answers", *dec("H", "answers, conc1, conc2: counters", "harness README 2.7.4")),
    ("17@0", *dec("P", "the cell arrays hd, tl", "METRICS rule 15")),
    ("18@0", *dec("R", "path, the heads taken so far, an extra argument of the search", EXTRA)),
    ("20@0", *CONS), ("25@0", *READSEQ),
    ("40@0", "R", "same: equality on the encoding, used only inside the direction function prefix", "METRICS rule 15, last sentence (rule 14 wins)"),
    ("45@0", *ADAPT),
    ("56@0", "R", "prefix: conc(a, b, c) with b and c known, a separately written direction function, with the extra argument d", DIRFN),
    ("62@0", *CNT), ("64@0", "H", "printing each answer prefix finds (output adapter)", "METRICS rule 13"),
    ("65@0", "R", "prefix: case 2, c = h followed by c1, recursion with path extended", DIRFN),
    ("68@0", *CNT), ("69@0", "R", "prefix: case 2, recursion", DIRFN),
    ("74@0", *INITTOP), ("74:answers", *INITCNT),
    ("75@0", "P", "reading b and c (the query's known places)", "stage information"),
    ("77@0", "R", "the query, as a call of the direction function with its extra argument", DIRFN + "; " + EXTRA),
    ("79@0", *ANS),
    ("84@0", *PROG),
]
SPEC["P03e"] = p03_head("8:la", "la, the length of a") + [
    ("16@0", *dec("P", "top, a0, b0: allocator, a and the answer b", "METRICS rule 15; the query")),
    ("16:conc1", *dec("H", "conc1, conc2, rev1, rev2 counters", "harness README 2.7.4")),
    ("17@0", *dec("P", "the cell arrays hd, tl, sized for rev", "METRICS rule 15")),
    ("19@0", *CONS), ("24@0", *READSEQ),
    ("39@0", *CONC), ("43:conc1", *CNT), ("43:conc", *CONC), ("47@0", *CNT), ("48@0", *CONC),
    ("52@0", "P", "rev computing b from a by its two cases in order, conjuncts in order (mode-faithful transcription)", "METRICS rule 3"),
    ("56:rev1", *CNT), ("56:rev", "P", "rev, case 1", "METRICS rule 3"), ("60@0", *CNT),
    ("61@0", "P", "rev, case 2: rev(l, q) and then conc(q, <h>, r)", "METRICS rule 3"),
    ("65@0", *ADAPT),
    ("76@0", *INITTOP), ("76:conc1", *INITCNT),
    ("77@0", "P", "reading a (the query's known place)", "stage information"),
    ("79@0", "P", "the query rev(a, b), b computed from a", "METRICS rule 3 (the direction the query uses)"),
    ("81@0", *ANS),
    ("88@0", *PROG),
]
SPEC["P03f"] = p03_head("8:lb", "lb, the length of b") + [
    ("16@0", *dec("P", "top, b0: allocator and the known b", "METRICS rule 15")),
    ("16:answers", *dec("H", "answers, conc1, conc2, rev1, rev2: counters", "harness README 2.7.4")),
    ("17@0", *dec("P", "the cell arrays hd, tl (sized for lastsplit's cells too)", "METRICS rule 15")),
    ("18@0", *dec("R", "path, the heads taken so far, an extra argument of the search", EXTRA)),
    ("20@0", *CONS), ("25@0", *READSEQ),
    ("40@0", "R", "lastsplit: conc(q, <h>, r) with r known, a separately written direction function for conc", DIRFN),
    ("49:conc1", *CNT), ("49:q", "R", "lastsplit: case 1", DIRFN),
    ("51:conc2", *CNT), ("51:q", "R", "lastsplit: case 2", DIRFN),
    ("55@0", *ADAPT),
    ("66@0", "R", "unrev: rev(a, r) with r known, a separately written direction function, conjuncts of case 2 moved, extra argument d", DIRFN + "; rule 4 (a move)"),
    ("73@0", *CNT), ("75@0", "H", "printing each answer unrev finds (output adapter)", "METRICS rule 13"),
    ("76@0", "R", "unrev: case 2, lastsplit then recursion with path extended", DIRFN),
    ("79@0", *CNT), ("80@0", "R", "unrev: case 2, recursion", DIRFN),
    ("85@0", *INITTOP), ("85:answers", *INITCNT),
    ("86@0", "P", "reading b (the query's known place)", "stage information"),
    ("88@0", "R", "the query, as a call of the direction function with its extra argument", DIRFN + "; " + EXTRA),
    ("90@0", *ANS),
    ("97@0", *PROG),
]

# x1 overrides: family -> {marker_in_report: marker_in_x1}
X1_MARKERS = {}
