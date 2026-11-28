# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P10d, written before any program was run
#   S mechanisms used: constraint propagator (S/propagate.py): Store with a
#     trail, var, relation (arc consistency), dom; backtracking search
#     (S/search.py): undo and the trail convention only (no search is made).
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - a closed world of facts as the finite domain of the unknown it
#       constrains; each constraint, as it arrives, narrowing the domain:
#       this configuration's P05 programs (arrive, post, source), unchanged
#       but for the relations P10d does not use and the trail; the S
#       mechanism's docstring (harnesses/python/S/propagate.py); Mackworth,
#       "Consistency in networks of relations", Artificial Intelligence
#       8(1), 1977
#     - withdrawal by undoing the store's changes through its trail, back to
#       where the withdrawn relation was posted, and posting again what came
#       after it: the trail convention of harnesses/python/S/search.py
#       ("undo(trail, mark) restores an earlier state")
#
# P10d. Stage 1: pick(x), a closed world of <facts>; stage 2: x > <k>;
# stage 3: withdraw x > <k> (the relation of stage 2).
# x is a variable of the propagator's store, which keeps a trail. pick, by
# its facts, gives x its domain; each relation is posted on x and narrows
# the domain. The information given and not withdrawn is kept, in order,
# with the stage that gave each relation and the trail's length before it
# was taken up. A withdrawal undoes the store back to that length, which
# restores the domain the relation narrowed and removes the relation, and
# posts again every relation given after it (none, here).

from S.propagate import Store
from S.search import undo

# CONSTANTS BEGIN
# stage 1
PICK_FACTS = (1, 2, 3)
# stage 2
GREATER_THAN = 1
# CONSTANTS END

trail = []          # undo entries of the store's changes (S/search.py's convention)
store = Store(trail)
facts = []          # pick's closed world, as its stage gives it
X = "x"
values = []         # the values of x still held, in order (read from the store's domain)
held = []           # comparisons waiting for x to have a domain
failed = []         # constraints whose posting emptied a domain
information = []    # the relations given and not withdrawn, in order: (stage, name, k)
marks = {}          # stage -> the trail's length before its relation was taken up

cp.held("domains", store.dom)
cp.held("constraints posted", store.cons)
cp.problem_alternatives("values of x still held", values)
cp.suspended("comparisons waiting for x to have a domain", held)
cp.held("constraints that emptied a domain", failed)
cp.held("information given and not withdrawn", information)


def pick(v):
    """pick(v): v is one of the facts."""
    return v in facts


def greater(v, k):
    """v > k."""
    return v > k


cp.relations(pick=pick, greater=greater)


def test(name, k, v):
    """Whether the relation (name, k) holds of the value v of x."""
    if name == "pick":
        return pick(v)
    return greater(v, k)


def on_x(name, k):
    """The relation (name, k) as a one-place predicate on x, for the store."""
    def holds(v):
        return test(name, k, v)
    holds.__name__ = "pick" if name == "pick" else "x %s %r" % (name, k)
    return holds


def post(name, k):
    """Post the relation (name, k) on x; note it if it empties x's domain."""
    if not store.relation([X], on_x(name, k)):
        failed.append(on_x(name, k).__name__)


def source(name, k):
    """The finite set of values a relation gives x by itself, or None."""
    if name == "pick":
        return tuple(facts)
    return None


def arrive(name, k=None):
    """Take up one relation on x as it arrives."""
    if X not in store.dom:
        given = source(name, k)
        if given is None:
            held.append((name, k))
            return
        store.var(X, given)
        for rel in list(held):
            held.remove(rel)
            post(*rel)
    post(name, k)


def tell(stage, name, k=None):
    """A stage adds a relation: it is kept as information, and taken up."""
    information.append((stage, name, k))
    marks[stage] = len(trail)
    arrive(name, k)


def withdraw(stage):
    """A stage withdraws the relation of an earlier stage: the store is
    undone back to before that relation was taken up, and every relation
    given after it is taken up again, in order."""
    gone = [rel for rel in information if rel[0] == stage]
    later = [rel for rel in information if rel[0] > stage]
    information[:] = [rel for rel in information if rel[0] != stage]
    for _, name, k in gone:
        if (name, k) in held:
            held.remove((name, k))
            return
        if on_x(name, k).__name__ in failed:
            failed.remove(on_x(name, k).__name__)
    undo(trail, marks[stage])
    for later_stage, name, k in later:
        marks[later_stage] = len(trail)
        arrive(name, k)


def report():
    if X in store.dom and not values:
        print("no solution: the domain of x is empty; constraints that emptied it:", failed)
    for v in values:
        cp.answer("x = %s" % v)


while (s := cp.stage()) is not None:
    if s.k == 1:
        facts[:] = s.constants["PICK_FACTS"]
        tell(1, "pick")                                 # pick(x)
    elif s.k == 2:
        tell(2, ">", s.constants["GREATER_THAN"])       # x > <k>
    elif s.k == 3:
        withdraw(2)                                     # withdraw x > <k>
    values[:] = sorted(store.dom[X]) if X in store.dom else []
    if not s.replay:
        report()
