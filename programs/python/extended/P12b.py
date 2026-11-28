# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P12b, written before any program was run
#   S mechanisms used: backtracking search (S/search.py): search, undo, the
#     trail; suspension queue (S/suspend.py): Var, deref, Queue.bind with a
#     trail. And two of the program's own, general over relations, so S
#     (METRICS.md, rules 12, 15 and 19), not listed in S-mechanisms.md, the
#     same text as in this configuration's P03 and P04 programs: "unify"
#     (unification of terms built from values, cons cells and Vars, no
#     occurs check) and "resolution" (children and done: a goal list reduced
#     by the cases of its first goal's relation, depth first).
#   idioms:
#     - the stage loop, cp calls, s.params (n, answers), the search's stack
#       registered as pending, accept registered as the relation whose
#       applications are the candidates examined: harnesses/python/README.md,
#       sections 3 and 8
#     - a relation as a generator of its cases, each a head unified with the
#       goal's arguments and a body of goals; a disjunction as a relation
#       whose cases are its alternatives, in order; a closed world of facts
#       as the cases of a relation; goals solved left to right, cases tried
#       in order, by chronological backtracking: Robinson, "A
#       machine-oriented logic based on the resolution principle", JACM
#       12(1), 1965; the S mechanisms' docstrings
#       (harnesses/python/S/search.py, suspend.py); this configuration's P04
#       programs (either, equal)
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as ();
#       atoms as strings: McCarthy, "Recursive functions of symbolic
#       expressions and their computation by machine, Part I", CACM 3(4),
#       1960; systems/python/measurement.md, section 2
#
# P12b. One stage: choice(n, s) and accept(s), in that order, for all
# solutions or for any one (s.params["answers"]), n from s.params["n"].
# accept: <R> only (a closed world).
# The same text as this configuration's P12a, with P12b's facts.
# choice, its disjunction e = 'l or e = 'r, and accept (its facts) are
# relations, by their cases in order; the query is solved by S's search,
# depth first, goals left to right. Every solution is reported, or only the
# first. The closed world depends on n, so the constants block gives the
# facts for each n the problem poses.

from S.search import search, undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
ACCEPT_FACTS = {
    8: (("r",),),
    12: (("r",),),
    16: (("r",),),
}
# CONSTANTS END

binder = Queue()    # used only for its bind, with the trail
trail = []      # undo entries of bindings (S/search.py's convention)
stack = []      # the search's pending choice points
NIL = ()

cp.pending("choice points of the search", stack)

facts = []          # accept's closed world, as stage 1 gives it for this n, as cons cells


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


def equal(a, b):
    """The relation a = b: its two places unified."""
    if unify(a, b):
        yield ()


def either(*alternatives):
    """A disjunction: its alternatives, each a tuple of goals, in the order
    written."""
    for goals in alternatives:
        yield goals


def choice(n, s):
    """The relation choice(n, s), by the definition's cases in order, n an
    integer."""
    if unify(s, NIL):                                       # 1. choice(n, <>)
        yield ()
    e, t = Var("e"), Var("t")
    if n > 0 and unify(s, (e, t)):                          # 2. choice(n, <e> ++ t) if n > 0 and
        yield ((either, (((equal, (e, "l")),),              #    (e = 'l or
                         ((equal, (e, "r")),))),            #     e = 'r, in that order) and
               (choice, (n - 1, t)))                        #    choice(n - 1, t)


def accept(s):
    """The relation accept(s): its facts, in order, each a case."""
    for fact in facts:
        if unify(s, fact):
            yield ()


cp.relations(choice=choice, accept=accept)


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
        n = st.params["n"]
        facts[:] = [cons(f) for f in st.constants["ACCEPT_FACTS"][n]]
        seq = Var("s")
        cp.bindings({"s": seq})
        solutions = search(((choice, (n, seq)), (accept, (seq,))), children, done, trail, stack)
        found = 0
        for _ in solutions:
            found += 1
            if not st.replay:
                cp.answer("s = %s" % show(seq))
            if st.params["answers"] == "any-one":
                break                                       # any one
        if found == 0 and not st.replay:
            print("no solution: no s of choice(%d, s) is accepted" % n)
