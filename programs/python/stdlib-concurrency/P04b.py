# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P04b (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - a relation as a generator of the values that satisfy it, a
#       disjunction as one generator after another, in order: The Python
#       Language Reference (3.13), "Yield expressions" (yield from); PEP 255,
#       "Simple Generators"; PEP 380, "Syntax for Delegating to a Subgenerator"
#     - None for a place that has no value: The Python Library Reference,
#       "Built-in Constants" (None)
#
# P04b. The query: x = <k> or loop(x), in that order.
# Each relation is a generator of the values of x that satisfy it, x given
# as None while it is unknown, by its cases in order. The disjunction tries
# its first alternative and then its second, as written.

# CONSTANTS BEGIN
# stage 1
X_VALUE = 1
# CONSTANTS END

known = {}
cp.bindings(known)


def loop(x):
    """loop(x): yields each value of x for which loop(x) holds."""
    yield from loop(x)                      # 1. loop(x) if loop(x)


def equal(x, k):
    """x = k: yields each value of x for which it holds."""
    if x is None or x == k:
        yield k


def query(x, k):
    """x = k or loop(x), in that order."""
    yield from equal(x, k)
    yield from loop(x)


cp.relations(loop=loop, equal=equal)


while (s := cp.stage()) is not None:
    if s.k == 1:
        answers = query(None, s.constants["X_VALUE"])
        cp.pending("the disjunction, not yet exhausted", answers)
        for x in answers:
            known["x"] = x
            if not s.replay:
                cp.answer("x = %s" % x)
