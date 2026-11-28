# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P11a, written before any program was run
#   S mechanisms used: backtracking search (S/search.py): search, undo, the
#     trail; suspension queue (S/suspend.py): Var, deref, Queue.bind with a
#     trail. And two of the program's own, general over relations, so S
#     (METRICS.md, rules 12, 15 and 19), not listed in S-mechanisms.md, the
#     same text as in this configuration's P03 and P04 programs: "unify"
#     (unification of terms built from values, cons cells and Vars, no
#     occurs check) and "resolution" (children and done: a goal list reduced
#     by the cases of its first goal's relation, depth first).
#   idioms:
#     - the stage loop, cp calls, cp.emit, the search's stack registered as
#       pending: harnesses/python/README.md, sections 3 and 8
#     - a relation as a generator of its cases, each a head unified with the
#       goal's arguments and a body of goals; a closed world of facts as the
#       cases of a relation, in order; goals solved left to right, by
#       chronological backtracking; one solution taken with next(): Robinson,
#       "A machine-oriented logic based on the resolution principle", JACM
#       12(1), 1965; the S mechanisms' docstrings
#       (harnesses/python/S/search.py: "a caller takes one (next) or many")
#     - an external effect as a goal that performs it when it is reached
#       and then succeeds, as a Prolog write/1 goal does: Clocksin and
#       Mellish, Programming in Prolog, Springer, 1981, chapter 5 ("Input
#       and Output")
#
# P11a. One stage, an any-one query: pick(x) and x >= <k> and emit(x), in
# that order.
# pick (its facts), >= and emit are relations; the query is solved by
# search, depth first, its goals left to right, and one solution is taken,
# which commits it as it is reported. The search's untried alternatives are
# left on its stack.

from S.search import search, undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
PICK_FACTS = (1, 2, 3)
AT_LEAST = 2
# CONSTANTS END

binder = Queue()    # used only for its bind, with the trail
trail = []      # undo entries of bindings (S/search.py's convention)
stack = []      # the search's pending choice points
NIL = ()

cp.pending("choice points of the search", stack)

facts = []          # pick's closed world, as stage 1 gives it


def unify(x, y):
    """Unify two terms, binding Vars through the trail. On failure, undo
    what it bound and return False."""
    mark = len(trail)
    pairs = [(x, y)]
    while pairs:
        a, b = pairs.pop()
        a, b = deref(a), deref(b)
        if a is b:
            continue
        if isinstance(a, Var) or isinstance(b, Var):
            binder.bind(a, b, trail)
        elif isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
            pairs.extend(zip(a, b))
        elif isinstance(a, tuple) or isinstance(b, tuple) or a != b:
            undo(trail, mark)
            return False
    return True


def children(goals):
    """Resolution: the goal lists that the cases of the first goal's
    relation reduce `goals` to, in the order of the cases."""
    (relation, args), rest = goals[0], goals[1:]
    for body in relation(*args):
        yield body + rest


def done(goals):
    """A goal list is solved when no goal is left."""
    return not goals


def pick(x):
    """The relation pick(x): its facts, in order, each a case."""
    for v in facts:
        if unify(x, v):
            yield ()


def at_least(x, k):
    """The relation x >= k, a test on integers."""
    if deref(x) >= k:
        yield ()


def emit(x):
    """emit(x): appends x to the log, and holds."""
    cp.emit(deref(x))
    yield ()


cp.relations(pick=pick, at_least=at_least)


while (s := cp.stage()) is not None:
    if s.k == 1:
        facts[:] = s.constants["PICK_FACTS"]
        x = Var("x")
        cp.bindings({"x": x})
        query = ((pick, (x,)), (at_least, (x, s.constants["AT_LEAST"])), (emit, (x,)))
        solutions = search(query, children, done, trail, stack)
        if next(solutions, None) is None:           # any one
            if not s.replay:
                print("no solution: no value of x satisfies the conjunction")
        elif not s.replay:
            cp.answer("x = %s" % deref(x))
