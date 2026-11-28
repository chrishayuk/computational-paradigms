# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P09a (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, computations registered for spawn() and the
#       constants kept by main for them: harnesses/python/README.md, sections
#       3 and 8, and its qualification program x03_two.py
#     - loop as a generator of the values of x that satisfy it, as in this
#       configuration's P04 programs: The Python Language Reference (3.13),
#       "Yield expressions" (yield from); PEP 255; PEP 380
#     - rev and conc forwards by their cases, as in this configuration's P03e:
#       METRICS.md, rule 3; The Python Tutorial, "Tuples and Sequences"
#
# P09a. Two separate computations, each started with spawn():
#   A: loop(x)            B: rev(<seq>, b)
# loop is as in P04 (x given as None while unknown); rev and conc as in P03,
# forwards. Each computation is a function of its own, with its own
# bindings; they share no unknowns. In core the harness runs them one after
# the other; in stdlib-concurrency side by side (harnesses/python/README.md,
# 3.4): the program text is the same.

# CONSTANTS BEGIN
# stage 1
REV_INPUT = (1, 2, 3)
# CONSTANTS END

C = {}          # the constants, as stage 1 delivers them, for the computations


def loop(x):
    """loop(x): yields each value of x for which loop(x) holds."""
    yield from loop(x)                      # 1. loop(x) if loop(x)


def conc(a, b):
    """conc(a, b, c), forwards: c from a and b, by the definition's cases."""
    if not a:                               # 1. conc(<>, b, b)
        return b
    return (a[0],) + conc(a[1:], b)         # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)


def rev(a):
    """rev(a, b), forwards: b from a, by the definition's cases."""
    if not a:                               # 1. rev(<>, <>)
        return ()
    return conc(rev(a[1:]), (a[0],))        # 2. rev(<h> ++ l, r) if rev(l, q) and conc(q, <h>, r)


cp.relations(loop=loop, conc=conc, rev=rev)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


def A():
    """Computation A: loop(x)."""
    known = {}
    cp.bindings(known)
    answers = loop(None)
    cp.pending("loop(x), not yet exhausted", answers)
    for x in answers:
        known["x"] = x
        cp.answer("x = %s" % show(x))


def B():
    """Computation B: rev(<seq>, b)."""
    known = {}
    cp.bindings(known)
    known["b"] = rev(C["REV_INPUT"])
    cp.answer("b = %s" % show(known["b"]))


cp.computation("A", A)
cp.computation("B", B)

while (s := cp.stage()) is not None:
    C.update(s.constants)
