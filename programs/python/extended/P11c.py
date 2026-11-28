# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P11c, written before any program was run
#   S mechanisms used: backtracking search (S/search.py): search, undo, the
#     trail; suspension queue (S/suspend.py): Var, deref, Queue.bind with a
#     trail. And two of the program's own, general over relations, so S
#     (METRICS.md, rules 12, 15 and 19), not listed in S-mechanisms.md, the
#     same text as in this configuration's P03 and P04 programs: "unify"
#     (unification of terms built from values, cons cells and Vars, no
#     occurs check) and "resolution" (children and done: a goal list reduced
#     by the cases of its first goal's relation, depth first).
#   idioms:
#     - the stage loop, cp calls, cp.emit, s.commitment for a replayed commit
#       stage, the search's stack registered as pending:
#       harnesses/python/README.md, sections 3 and 8; its qualification
#       program x02_pick.py (a commit stage taken from s.commitment)
#     - a relation as a generator of its cases, each a head unified with the
#       goal's arguments and a body of goals; a closed world of facts as the
#       cases of a relation, in order; one solution taken with next(), and
#       the next asked for when a later relation refutes the one held:
#       Robinson, "A machine-oriented logic based on the resolution
#       principle", JACM 12(1), 1965; the S mechanisms' docstrings
#       (harnesses/python/S/search.py: "a caller takes one (next) or many")
#     - an external effect as a goal that performs it when it is reached and
#       then succeeds: Clocksin and Mellish, Programming in Prolog,
#       Springer, 1981, chapter 5 ("Input and Output"); commitment as giving
#       up the choice points not taken, as a cut does: the same, chapter 4
#       ("Backtracking and the Cut")
#
# P11c. Any-one queries. Stage 1: pick(x) and emit(x); stage 2: x != <k>;
# stage 3: commit.
# Stage 1's query is solved by search, depth first, its goals left to
# right, and one solution is taken. A relation on x added later is kept, and
# the solution held must satisfy every relation added: if it does not, the
# search is asked for its next solution (backtracking into pick, and
# performing that solution's effect) until one does or none is left. A
# commit stage selects the solution held, v: x = v is added as a relation,
# and the search's choice points are given up. A replayed commit stage
# takes x = v from s.commitment.

from S.search import search, undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
PICK_FACTS = (1, 2, 3)
# stage 2
DIFFERENT_FROM = 1
# CONSTANTS END

binder = Queue()    # used only for its bind, with the trail
trail = []      # undo entries of bindings (S/search.py's convention)
stack = []      # the search's pending choice points
NIL = ()

x = Var("x")
known = {}          # the bindings of the solution held, while there is one
solutions = []      # stage 1's search, until a commit gives up its choice points
added = []          # relations on x added after stage 1: (name, k)

cp.bindings(known)
cp.pending("choice points of the search", stack)
cp.held("relations on x added after stage 1", added)

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


def emit(x):
    """emit(x): appends x to the log, and holds."""
    cp.emit(deref(x))
    yield ()


def different(v, k):
    """v != k."""
    return v != k


def equal(v, k):
    """v = k."""
    return v == k


cp.relations(pick=pick, different=different, equal=equal)


def holds(name, k, v):
    """Whether the relation (name, k) holds of the value v of x."""
    if name == "!=":
        return different(v, k)
    return equal(v, k)


def satisfies(v):
    """Whether v satisfies every relation added after stage 1."""
    return all(holds(name, k, v) for name, k in added)


def next_solution():
    """The search's next solution: x's value in it, or None if none is left
    (or the search has been given up)."""
    if solutions and next(solutions[0], None) is not None:
        return deref(x)
    return None


def advance():
    """Keep the solution held if it satisfies every relation added;
    otherwise ask the search for its next solution, until one does or none
    is left."""
    v = known.pop("x", None)
    while v is not None and not satisfies(v):
        v = next_solution()
    if v is not None:
        known["x"] = v


def add(name, k):
    """A stage adds a relation on x."""
    added.append((name, k))
    advance()


def commit(commitment):
    """A commit stage: the solution held, v (or, in a replay, the v the
    stage first selected), is selected; x = v is added, and the search's
    choice points are given up."""
    if commitment is not None:
        chosen = [v for v in facts if "x = %s" % v == commitment]
        v = chosen[0] if chosen else None
    else:
        v = known.get("x")
    if v is not None:
        add("=", v)
    stack.clear()
    solutions.clear()


def report():
    if "x" in known:
        cp.answer("x = %s" % known["x"])
    else:
        print("no solution: no value of x satisfies the information so far")


while (s := cp.stage()) is not None:
    if s.k == 1:
        facts[:] = s.constants["PICK_FACTS"]
        solutions[:] = [search(((pick, (x,)), (emit, (x,))), children, done, trail, stack)]
        v = next_solution()                         # pick(x) and emit(x): any one
        if v is not None:
            known["x"] = v
    elif s.k == 2:
        add("!=", s.constants["DIFFERENT_FROM"])    # x != <k>
    elif s.k == 3:
        commit(s.commitment)                        # commit
    if not s.replay:
        report()
