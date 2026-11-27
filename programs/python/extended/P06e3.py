# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P06e3, written before any program was run
#   S mechanisms used: backtracking search (S/search.py): search, undo, the
#     trail; suspension queue (S/suspend.py): Var, deref, Queue.bind with a
#     trail. And two of the program's own, general over relations, so S
#     (METRICS.md, rules 12, 15 and 19), not listed in S-mechanisms.md, the
#     same text as in this configuration's P03 programs: "unify"
#     (unification of terms built from values, cons cells and Vars, no
#     occurs check) and "resolution" (children and done: a goal list reduced
#     by the cases of its first goal's relation, depth first); and a third
#     of its own, also S: "negation" (not R, by a search of its own for R:
#     negation as failure).
#   idioms:
#     - the stage loop, cp calls, the search's stack registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - a relation as a generator of its cases, each a head unified with the
#       goal's arguments and a body of goals; goals solved left to right,
#       cases tried in order, by chronological backtracking, bindings undone
#       through a trail: Robinson, "A machine-oriented logic based on the
#       resolution principle", JACM 12(1), 1965 (unification); the S
#       mechanisms' docstrings (harnesses/python/S/search.py, suspend.py)
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as ():
#       McCarthy, "Recursive functions of symbolic expressions and their
#       computation by machine, Part I", CACM 3(4), 1960; the same encoding
#       in systems/python/measurement.md, section 2
#     - negation as failure: Clark, "Negation as failure", in Gallaire and
#       Minker (eds.), Logic and Data Bases, Plenum, 1978
#     - generators and yield: The Python Language Reference (3.13), "Yield
#       expressions"; PEP 255, "Simple Generators"
#
# P06e3. The query nonmajor(p), over the closed world of <facts>.
# The facts and nonmajor are transcribed as relations: generators that, for
# each case (each fact) in order, unify its head with the goal's arguments
# and give its body; nonmajor's conjuncts are in their order: student(p),
# then maths(k), then the goal negation(takes(p, k)). Atoms are strings.
# The query is solved by search, depth first, and every answer is reported.

from S.search import search, undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
STUDENT_FACTS = ("brown", "smith")
MATHS_FACTS = ("c101", "c301")
TAKES_FACTS = (("brown", "c101"), ("smith", "c101"), ("smith", "c301"))
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


def negation(*goals):
    """not R, R a conjunction of goals: holds exactly when R has no
    solution, found by a search of its own (negation as failure). Any
    bindings that search makes are undone."""
    mark = len(trail)
    for _ in search(goals, children, done, trail, []):
        undo(trail, mark)
        return
    yield ()


world = {"student": (), "maths": (), "takes": ()}   # the closed world, as stage 1 gives it
cp.held("the closed world", world)


def student(p):
    """The relation student(p): its facts, in order."""
    for fact in world["student"]:
        if unify(p, fact):
            yield ()


def maths(k):
    """The relation maths(k): its facts, in order."""
    for fact in world["maths"]:
        if unify(k, fact):
            yield ()


def takes(p, k):
    """The relation takes(p, k): its facts, in order."""
    for fact in world["takes"]:
        if unify((p, k), fact):
            yield ()


def nonmajor(p):
    """The relation nonmajor(p), by its one case."""
    k = Var("k")
    yield ((student, (p,)), (maths, (k,)),                  # 1. nonmajor(p) if student(p) and maths(k)
           (negation, ((takes, (p, k)),)))                  #    and not takes(p, k)


cp.relations(student=student, maths=maths, takes=takes, nonmajor=nonmajor, negation=negation)


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


while (s := cp.stage()) is not None:
    if s.k == 1:
        world["student"] = s.constants["STUDENT_FACTS"]
        world["maths"] = s.constants["MATHS_FACTS"]
        world["takes"] = s.constants["TAKES_FACTS"]
        p = Var("p")
        cp.bindings({"p": p})
        query = ((nonmajor, (p,)),)
        for _ in search(query, children, done, trail, stack):
            if not s.replay:
                cp.answer("p = %s" % show(p))
