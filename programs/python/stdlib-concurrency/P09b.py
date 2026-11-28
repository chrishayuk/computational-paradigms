# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P09b (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, computations registered for spawn() and the
#       constants kept by main for them: harnesses/python/README.md, sections
#       3 and 8, and its qualification program x03_two.py
#     - an equation on an unknown as an assignment when the unknown has no
#       value, and as a comparison when it has one (the direction each
#       conjunct is reached in: METRICS.md, rules 3 and 8): The Python
#       Language Reference (3.13), "Assignment statements", "Value
#       comparisons", "The if statement"
#
# P09b. Two separate computations, each started with spawn():
#   A: x = <k> and x = <k>        B: y = <k>
# Each computation is a function of its own, with its own bindings. A's
# conjunction is evaluated in its order: the first equation gives x its
# value, the second tests it. A binding is registered only for a solution,
# so a failed conjunction leaves none. In core the harness runs the
# computations one after the other; in stdlib-concurrency side by side: the
# program text is the same.

# CONSTANTS BEGIN
# stage 1
A_FIRST = 1
A_SECOND = 2
B_VALUE = 3
# CONSTANTS END

C = {}          # the constants, as stage 1 delivers them, for the computations


def A():
    """Computation A: x = <k> and x = <k>."""
    known = {}
    cp.bindings(known)
    x = C["A_FIRST"]                        # x = <k>: x has no value, so it is given one
    if x == C["A_SECOND"]:                  # and x = <k>: x has a value, so it is tested
        known["x"] = x
        cp.answer("x = %s" % x)
    else:
        print("no solution: x = %s and x = %s" % (C["A_FIRST"], C["A_SECOND"]))


def B():
    """Computation B: y = <k>."""
    known = {}
    cp.bindings(known)
    known["y"] = C["B_VALUE"]               # y = <k>
    cp.answer("y = %s" % known["y"])


cp.computation("A", A)
cp.computation("B", B)

while (s := cp.stage()) is not None:
    C.update(s.constants)
