# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P15c, written before any program was run
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
#     - a relation given by facts as a generator of its cases, each a head
#       unified with the goal's arguments; cases tried in order, by
#       chronological backtracking; one solution taken (break after the
#       first), the search's choice points left on its stack: Robinson, "A
#       machine-oriented logic based on the resolution principle", JACM
#       12(1), 1965; the S mechanisms' docstrings
#       (harnesses/python/S/search.py: "a caller takes one (next) or many");
#       this configuration's P11 and P12 programs
#     - atoms as strings, shown with a leading quote: this configuration's
#       P12 programs
#
# P15c. One stage: grant(<atom>, <atom>, g), any one.
# grant is transcribed once, as a relation (a generator of its two facts, in
# order). The query is solved by S's search, depth first: the first fact
# gives the first solution, which is reported, and the search is stopped,
# its untried choice point (the second fact) left on its stack (registered
# as pending). Nothing in the program asks the search again.

from S.search import search, undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
FIRST = "a"
SECOND = "b"
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


def grant(p, q, g):
    """The relation grant(p, q, g), by the definition's facts in order."""
    if unify(g, p):                                         # 1. grant(p, q, p)
        yield ()
    if unify(g, q):                                         # 2. grant(p, q, q)
        yield ()


cp.relations(grant=grant)


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
        g = Var("g")
        cp.bindings({"g": g})
        query = ((grant, (st.constants["FIRST"], st.constants["SECOND"], g)),)
        for _ in search(query, children, done, trail, stack):
            if not st.replay:
                cp.answer("g = %s" % show(g))
            break                                           # any one
