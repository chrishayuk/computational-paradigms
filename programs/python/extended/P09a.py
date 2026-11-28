# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P09a, written before any program was run
#   S mechanisms used: backtracking search (S/search.py): search, undo, the
#     trail; suspension queue (S/suspend.py): Var, deref, Queue.bind with a
#     trail. And two of the program's own, general over relations, so S
#     (METRICS.md, rules 12, 15 and 19), not listed in S-mechanisms.md, the
#     same text as in this configuration's P03 and P04 programs: "unify"
#     (unification of terms built from values, cons cells and Vars, no
#     occurs check) and "resolution" (children and done: a goal list reduced
#     by the cases of its first goal's relation, depth first).
#   idioms:
#     - the stage loop, cp calls, computations registered for spawn(), each
#       registering its own search stack as pending: harnesses/python/README.md,
#       sections 3 and 8, and its qualification program x03_two.py
#     - a relation as a generator of its cases, each a head unified with the
#       goal's arguments and a body of goals; goals solved left to right,
#       cases tried in order, by chronological backtracking, bindings undone
#       through a trail: Robinson, "A machine-oriented logic based on the
#       resolution principle", JACM 12(1), 1965; the S mechanisms'
#       docstrings (harnesses/python/S/search.py, suspend.py)
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as ():
#       McCarthy, "Recursive functions of symbolic expressions and their
#       computation by machine, Part I", CACM 3(4), 1960;
#       systems/python/measurement.md, section 2
#
# P09a. Two separate computations, each started with spawn():
#   A: loop(x)            B: rev(<seq>, b)
# loop is as in P04, rev and conc as in P03: relations, transcribed once
# each, solved by search. Each computation has its own unknowns and its own
# search (its stack registered as its pending structure); they share the
# relations and the trail, the one database of the instance. The harness
# runs them one after the other in extended (harnesses/python/README.md, 3.4).

from S.search import search, undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
REV_INPUT = (1, 2, 3)
# CONSTANTS END

C = {}          # the constants, as stage 1 delivers them, for the computations
binder = Queue()    # used only for its bind, with the trail
trail = []      # undo entries of bindings (S/search.py's convention)
NIL = ()


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


def loop(x):
    """The relation loop(x), by its one case."""
    yield ((loop, (x,)),)                                   # 1. loop(x) if loop(x)


def conc(a, b, c):
    """The relation conc(a, b, c), by the definition's cases in order: each
    case whose head unifies gives its body, a tuple of goals."""
    if unify((a, b), (NIL, c)):                             # 1. conc(<>, b, b)
        yield ()
    h, a1, c1 = Var("h"), Var("a1"), Var("c1")
    if unify((a, c), ((h, a1), (h, c1))):                   # 2. conc(<h> ++ a, b, <h> ++ c)
        yield ((conc, (a1, b, c1)),)                        #    if conc(a, b, c)


def rev(a, b):
    """The relation rev(a, b), by the definition's cases in order; the body
    of case 2 keeps its two conjuncts in their order."""
    if unify((a, b), (NIL, NIL)):                           # 1. rev(<>, <>)
        yield ()
    h, l, q = Var("h"), Var("l"), Var("q")
    if unify(a, (h, l)):                                    # 2. rev(<h> ++ l, r)
        yield ((rev, (l, q)), (conc, (q, (h, NIL), b)))     #    if rev(l, q) and conc(q, <h>, r)


cp.relations(loop=loop, conc=conc, rev=rev)


def cons(seq):
    """The encoding: a sequence given as a tuple, as cons cells ending in ()."""
    t = ()
    for e in reversed(seq):
        t = (cons(e) if isinstance(e, tuple) else e, t)
    return t


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


def A():
    """Computation A: loop(x)."""
    x = Var("x")
    cp.bindings({"x": x})
    stack = []
    cp.pending("choice points of the search", stack)
    for _ in search(((loop, (x,)),), children, done, trail, stack):
        cp.answer("x = %s" % show(x))


def B():
    """Computation B: rev(<seq>, b)."""
    b = Var("b")
    cp.bindings({"b": b})
    stack = []
    cp.pending("choice points of the search", stack)
    for _ in search(((rev, (cons(C["REV_INPUT"]), b)),), children, done, trail, stack):
        cp.answer("b = %s" % show(b))


cp.computation("A", A)
cp.computation("B", B)

while (s := cp.stage()) is not None:
    C.update(s.constants)
