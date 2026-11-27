# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P01b, written before any program was run
#   S mechanism used: suspension queue (S/suspend.py): Var, deref, Queue.bind
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - unknowns as logic variables, an equation as a binding:
#       harnesses/python/S/suspend.py, its docstring
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as ():
#       McCarthy, "Recursive functions of symbolic expressions and their
#       computation by machine, Part I", CACM 3(4), 1960 (cons, car, cdr);
#       the same encoding in systems/python/measurement.md, section 2
#     - conc by its two cases, with "if not a:" as the dispatch on case 1:
#       METRICS.md, rule 3 (the example of conc in Python)
#
# P01b. Stage 1: conc(<seq>, s, t); stage 2: s = <seq>.
# conc is transcribed forwards, as a function of its own, over cons cells. Its
# second place may be an unknown: case 1 then gives that unknown itself as the
# tail, so conc(<1,2>, s) is the term <1,2> ++ s, and stage 1 binds t to it.
# Stage 2 binds s; t's tail is then <3>.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
PREFIX = (1, 2)
# stage 2
S_VALUE = (3,)
# CONSTANTS END

q = Queue()
s_, t = Var("s"), Var("t")
unknowns = {"s": s_, "t": t}
failed = []     # relations found not to hold

cp.bindings(unknowns)
cp.held("relations found not to hold", failed)


def cons(seq):
    """The encoding: a sequence given as a tuple, as cons cells ending in ()."""
    t = ()
    for e in reversed(seq):
        t = (cons(e) if isinstance(e, tuple) else e, t)
    return t


def conc(a, b):
    """conc(a, b, c), forwards: c from a and b, by the definition's cases."""
    a = deref(a)
    if not a:                               # 1. conc(<>, b, b)
        return b
    return (a[0], conc(a[1], b))            # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)


cp.relations(conc=conc)


def show(t):
    """Output adapter: a term as the problem writes it, a sequence whose
    tail is an unknown as <...> ++ that unknown."""
    t = deref(t)
    if isinstance(t, Var):
        return t.name
    if not isinstance(t, tuple):
        return str(t)
    items = []
    while isinstance(t, tuple) and len(t) == 2:
        items.append(show(t[0]))
        t = deref(t[1])
    shown = "⟨" + ",".join(items) + "⟩"
    if t == ():
        return shown
    return shown + " ++ " + show(t)


while (s := cp.stage()) is not None:
    if s.k == 1:
        if not q.bind(t, conc(cons(s.constants["PREFIX"]), s_)):
            failed.append("conc(%s, s, t)" % show(cons(s.constants["PREFIX"])))
    elif s.k == 2:
        if not q.bind(s_, cons(s.constants["S_VALUE"])):
            failed.append("s = %s" % show(cons(s.constants["S_VALUE"])))
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        else:
            told = ["%s = %s" % (n, show(v)) for n, v in unknowns.items() if deref(v) is not v]
            if told:
                cp.answer(", ".join(told))
