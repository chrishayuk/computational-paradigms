# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P09b, written before any program was run
#   S mechanisms used: suspension queue (S/suspend.py): Var, deref,
#     Queue.bind with a trail; backtracking search (S/search.py): undo and
#     the trail convention only (no search is made).
#   idioms:
#     - the stage loop, cp calls, computations registered for spawn() and the
#       constants kept by main for them: harnesses/python/README.md, sections
#       3 and 8, and its qualification program x03_two.py
#     - equations as bindings of logic variables, a failed conjunction
#       undoing the bindings it made through the trail: the S mechanisms'
#       docstrings (harnesses/python/S/suspend.py, search.py); Robinson, "A
#       machine-oriented logic based on the resolution principle", JACM
#       12(1), 1965
#
# P09b. Two separate computations, each started with spawn():
#   A: x = <k> and x = <k>        B: y = <k>
# Each computation has its own Var. An equation is a binding (Queue.bind),
# which fails if the Var already has another value; the conjunction's
# bindings are undone when it fails. The harness runs the computations one
# after the other in extended.

from S.search import undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
A_FIRST = 1
A_SECOND = 2
B_VALUE = 3
# CONSTANTS END

C = {}          # the constants, as stage 1 delivers them, for the computations
binder = Queue()    # used only for its bind


def A():
    """Computation A: x = <k> and x = <k>."""
    x = Var("x")
    cp.bindings({"x": x})
    trail = []
    if binder.bind(x, C["A_FIRST"], trail) and binder.bind(x, C["A_SECOND"], trail):
        cp.answer("x = %s" % deref(x))
    else:
        undo(trail, 0)
        print("no solution: x = %s and x = %s" % (C["A_FIRST"], C["A_SECOND"]))


def B():
    """Computation B: y = <k>."""
    y = Var("y")
    cp.bindings({"y": y})
    if binder.bind(y, C["B_VALUE"]):
        cp.answer("y = %s" % deref(y))


cp.computation("A", A)
cp.computation("B", B)

while (s := cp.stage()) is not None:
    C.update(s.constants)
