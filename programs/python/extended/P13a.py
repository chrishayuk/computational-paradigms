# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P13a, written before any program was run
#   S mechanisms used: backtracking search (S/search.py): search, undo, the
#     trail; suspension queue (S/suspend.py): Var, deref, Queue.bind with a
#     trail. And two of the program's own, general over relations, so S
#     (METRICS.md, rules 12, 15 and 19), not listed in S-mechanisms.md:
#     "unify" (the same text as this configuration's P03 programs) and
#     "resolution" (children and done), here with the goal list as a linked
#     list, () or (goal, rest), so that putting a case's body before the
#     rest does not copy the rest (programs/python/README.md, batch 1D).
#   idioms:
#     - the stage loop, cp calls, s.params["n"], the search's stack
#       registered as pending: harnesses/python/README.md, sections 3 and 8
#     - a relation as a generator of its cases, each a head unified with the
#       goal's arguments and a body of goals; goals solved left to right,
#       cases tried in order, by chronological backtracking, bindings undone
#       through a trail: Robinson, "A machine-oriented logic based on the
#       resolution principle", JACM 12(1), 1965; the S mechanisms'
#       docstrings (harnesses/python/S/search.py, suspend.py); this
#       configuration's P03 and P12 programs
#     - sequences, and the goal list, as cons cells, <h> ++ t as the pair
#       (h, t) and <> as (): McCarthy, "Recursive functions of symbolic
#       expressions and their computation by machine, Part I", CACM 3(4),
#       1960; systems/python/measurement.md, section 2
#     - an arithmetic guard on known integers inside a case (m > n, m <= n)
#       and an argument computed in the direction used (m + 1): METRICS.md,
#       rules 3 and 8; this configuration's P12a (n > 0, n - 1)
#     - a trailing underscore on a name that would shadow a built-in
#       (range_): PEP 8, "Naming Conventions", "Descriptive: Naming Styles"
#
# P13a. One stage: range(<k>, n, s), n from s.params["n"].
# range is transcribed once, as a relation (a generator of its cases in
# order), and the query is solved by S's search, depth first; every answer
# is reported. The search is iterative, so no recursion limit is reached;
# every resolution step leaves a choice point on the search's stack (the
# relation's generator, suspended after its case 2) until the search
# backtracks after the answer.

from S.search import search, undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
START = 1
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
    relation reduce `goals` to, in the order of the cases. A goal list is a
    linked list, () or (goal, rest); a case's body is put before the rest
    without copying the rest."""
    (relation, args), rest = goals
    for body in relation(*args):
        reduced = rest
        for goal in reversed(body):
            reduced = (goal, reduced)
        yield reduced


def done(goals):
    """A goal list is solved when no goal is left."""
    return not goals


def range_(m, n, s):
    """The relation range(m, n, s), by the definition's cases in order, m
    and n integers (the direction the query uses)."""
    m, n = deref(m), deref(n)
    if m > n and unify(s, NIL):                             # 1. range(m, n, <>) if m > n
        yield ()
    t = Var("t")
    if m <= n and unify(s, (m, t)):                         # 2. range(m, n, <m> ++ t) if m <= n
        yield ((range_, (m + 1, n, t)),)                    #    and range(m + 1, n, t)


cp.relations(range=range_)


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


class Shown:
    """Output adapter: an unknown as observe() renders it, its term as the
    problem writes it (a long sequence is rendered without recursion)."""

    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return show(self.v)


while (st := cp.stage()) is not None:
    if st.k == 1:
        seq = Var("s")
        cp.bindings({"s": Shown(seq)})
        query = ((range_, (st.constants["START"], st.params["n"], seq)), ())    # range(<k>, n, s)
        for _ in search(query, children, done, trail, stack):
            if not st.replay:
                cp.answer("s = %s" % show(seq))
