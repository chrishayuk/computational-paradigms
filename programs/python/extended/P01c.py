# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P01c, written before any program was run
#   S mechanism used: suspension queue (S/suspend.py): Var, deref, Queue.bind
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - unknowns as logic variables, an equation as a binding (no occurs
#       check: "binding to anything else gives it that value"):
#       harnesses/python/S/suspend.py, its docstring
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as ():
#       McCarthy, "Recursive functions of symbolic expressions and their
#       computation by machine, Part I", CACM 3(4), 1960 (cons, car, cdr);
#       the same encoding in systems/python/measurement.md, section 2
#     - conc by its two cases, with "if not a:" as the dispatch on case 1:
#       METRICS.md, rule 3 (the example of conc in Python)
#
# P01c. One stage: x = <seq> ++ x, that is conc(<seq>, x, x).
# conc is transcribed forwards, as a function of its own, over cons cells; its
# second place may be an unknown, which case 1 gives back as the tail. So
# conc(<1>, x) is the term <1> ++ x, and the equation binds x to it. Binding
# has no occurs check: x is then a cyclic term, <1, 1, 1, ...>.
# The bindings are registered as their rendering (show below), since repr of
# a cyclic term recurses without end.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
PREFIX = (1,)
# CONSTANTS END

q = Queue()
x = Var("x")
unknowns = {"x": x}
shown = {}      # each unknown's term, as show renders it
failed = []     # relations found not to hold

cp.bindings(shown)
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
    """Output adapter: a term as the problem writes it. A sequence whose
    tail is an unknown is shown as <...> ++ that unknown; one whose tail
    leads back to a cell already shown is cyclic, shown as the part before
    the cycle and the part that repeats for ever."""
    t = deref(t)
    if isinstance(t, Var):
        return t.name
    if not isinstance(t, tuple):
        return str(t)
    items, cells = [], []
    while isinstance(t, tuple) and len(t) == 2 and all(t is not c for c in cells):
        cells.append(t)
        items.append(show(t[0]))
        t = deref(t[1])
    for i, c in enumerate(cells):
        if t is c:
            before = "⟨" + ",".join(items[:i]) + "⟩ ++ " if i else ""
            loop = "⟨" + ",".join(items[i:]) + "⟩"
            return before + loop + " ++ " + loop + " ++ … (cyclic)"
    shown_ = "⟨" + ",".join(items) + "⟩"
    if t == ():
        return shown_
    return shown_ + " ++ " + show(t)


while (s := cp.stage()) is not None:
    if s.k == 1:
        if not q.bind(x, conc(cons(s.constants["PREFIX"]), x)):
            failed.append("x = %s ++ x" % show(cons(s.constants["PREFIX"])))
    for n, v in unknowns.items():
        shown[n] = show(v)
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        else:
            told = ["%s = %s" % (n, show(v)) for n, v in unknowns.items() if deref(v) is not v]
            if told:
                cp.answer(", ".join(told))
