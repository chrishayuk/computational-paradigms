# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P15a2, written before any program was run
#   S mechanisms used: backtracking search (S/search.py): search, undo, the
#     trail; suspension queue (S/suspend.py): Var, deref, Queue.bind with a
#     trail. And two of the program's own, general over relations, so S
#     (METRICS.md, rules 12, 15 and 19), not listed in S-mechanisms.md, the
#     same text as in this configuration's P03, P04 and P12 programs:
#     "unify" (unification of terms built from values, cons cells and Vars,
#     no occurs check) and "resolution" (children and done: a goal list
#     reduced by the cases of its first goal's relation, depth first).
#   idioms:
#     - the stage loop, cp calls, the search's stack registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - a relation as a generator of its cases, each a head unified with the
#       goal's arguments and a body of goals; goals solved left to right,
#       cases tried in order, by chronological backtracking; every solution
#       taken, until the search is exhausted:
#       Robinson, "A machine-oriented logic based on the
#       resolution principle", JACM 12(1), 1965; the S mechanisms'
#       docstrings (harnesses/python/S/search.py: "a caller takes one (next)
#       or many"); this configuration's P03 and P12 programs
#     - a != b on known terms as a goal that holds when they do not unify,
#       undoing what the attempt bound: Clark, "Negation as failure", in
#       Gallaire and Minker (eds.), Logic and Data Bases, Plenum, 1978; this
#       configuration's P06d (negation, run on ground terms)
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as ():
#       McCarthy, "Recursive functions of symbolic expressions and their
#       computation by machine, Part I", CACM 3(4), 1960;
#       systems/python/measurement.md, section 2
#
# P15a2. One stage: merge(<seq>, <seq>, m), all.
# merge is transcribed once, as a relation (a generator of its four cases in
# order, the guards b != <> and a != <> as goals before the recursive goal,
# in the order written). The query is solved by S's search, depth first;
# every solution is reported, in the order the search finds them.

from S.search import search, undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
FIRST = (1, 2)
SECOND = (3, 4)
# CONSTANTS END

binder = Queue()    # used only for its bind, with the trail
trail = []      # undo entries of bindings (S/search.py's convention)
stack = []      # the search's pending choice points
NIL = ()

cp.pending("choice points of the search", stack)


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


def differ(a, b):
    """The relation a != b, on terms known when it is reached: it holds if
    they do not unify; what the attempt bound is undone."""
    mark = len(trail)
    if unify(a, b):
        undo(trail, mark)
        return
    yield ()


def merge(a, b, m):
    """The relation merge(a, b, m), by the definition's cases in order: each
    case whose head unifies gives its body, a tuple of goals."""
    if unify((a, m), (NIL, b)):                             # 1. merge(<>, b, b)
        yield ()
    h, a1 = Var("h"), Var("a1")
    if unify((a, b, m), ((h, a1), NIL, (h, a1))):           # 2. merge(<h> ++ a, <>, <h> ++ a)
        yield ()
    h, a1, m1 = Var("h"), Var("a1"), Var("m1")
    if unify((a, m), ((h, a1), (h, m1))):                   # 3. merge(<h> ++ a, b, <h> ++ m)
        yield ((differ, (b, NIL)), (merge, (a1, b, m1)))    #    if b != <> and merge(a, b, m)
    h, b1, m1 = Var("h"), Var("b1"), Var("m1")
    if unify((b, m), ((h, b1), (h, m1))):                   # 4. merge(a, <h> ++ b, <h> ++ m)
        yield ((differ, (a, NIL)), (merge, (a, b1, m1)))    #    if a != <> and merge(a, b, m)


cp.relations(merge=merge, differ=differ)


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
    if isinstance(t, str):
        return "'" + t                    # an atom, with a leading quote
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


while (st := cp.stage()) is not None:
    if st.k == 1:
        m = Var("m")
        cp.bindings({"m": m})
        query = ((merge, (cons(st.constants["FIRST"]), cons(st.constants["SECOND"]), m)),)
        found = False
        for _ in search(query, children, done, trail, stack):    # all
            found = True
            if not st.replay:
                cp.answer("m = %s" % show(m))
        if not found and not st.replay:
            print("no solution: merge has no solution for these sequences")
