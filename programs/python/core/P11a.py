# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P11a (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, cp.emit, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - a conjunction as a generator of its solutions, its conjuncts in
#       order (a generator over pick's facts, a test, the effect), and one
#       answer taken with next(): The Python Language Reference (3.13),
#       "Yield expressions"; PEP 255, "Simple Generators"; The Python Library
#       Reference, "Built-in Functions" (next, with a default); this
#       configuration's P04 programs (a relation as a generator of the
#       values that satisfy it, None while x is unknown)
#
# P11a. One stage, an any-one query: pick(x) and x >= <k> and emit(x), in
# that order.
# The conjunction is a generator of its solutions: for each value pick gives
# x, in the facts' order, the test, then the effect, then the solution. One
# answer is taken (next), which commits it as it is reported; the
# generator, with its untried alternatives, is left suspended.

# CONSTANTS BEGIN
# stage 1
PICK_FACTS = (1, 2, 3)
AT_LEAST = 2
# CONSTANTS END

known = {}          # the bindings of the solution reported
cp.bindings(known)

facts = []          # pick's closed world, as stage 1 gives it


def pick(x):
    """pick(x): yields each value of x for which it holds, x None while unknown."""
    for v in facts:
        if x is None or x == v:
            yield v


def at_least(v, k):
    """v >= k."""
    return v >= k


cp.relations(pick=pick, at_least=at_least)


def conjunction(k):
    """pick(x) and x >= k and emit(x), in that order: yields each solution x."""
    for x in pick(None):
        if at_least(x, k):
            cp.emit(x)
            yield x


while (s := cp.stage()) is not None:
    if s.k == 1:
        facts[:] = s.constants["PICK_FACTS"]
        answers = conjunction(s.constants["AT_LEAST"])
        cp.pending("the conjunction's untried alternatives", answers)
        x = next(answers, None)                     # any one
        if x is None:
            if not s.replay:
                print("no solution: no value of x satisfies the conjunction")
        else:
            known["x"] = x
            if not s.replay:
                cp.answer("x = %s" % x)
