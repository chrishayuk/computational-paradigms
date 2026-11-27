# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P05a, written before any program was run
#   S mechanisms used: constraint propagator (S/propagate.py): Store, var,
#     relation (arc consistency), dom; it imports the backtracking search,
#     which this program does not call.
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - a closed world of facts as the finite domain of the unknown it
#       constrains; each constraint, as it arrives, narrowing the domain
#       (all alternatives held at once); the S mechanism's docstring
#       (harnesses/python/S/propagate.py); Mackworth, "Consistency in
#       networks of relations", Artificial Intelligence 8(1), 1977 (arc
#       consistency)
#     - closures for the one-place predicates: The Python Language
#       Reference (3.13), "Function definitions"
#
# P05a. Stage 1: pick(x), a closed world of <facts>; stage 2: x > <k>;
# stage 3: x != <k>.
# x is a variable of the propagator's store. pick, by its facts, gives x its
# domain (as x = k does, if it comes first); each relation is posted as a
# relation of the store on x, which keeps only the values of x for which it
# holds. A comparison that arrives before x has a
# domain (x ranges over all integers then, which no finite domain states)
# is held until a domain arrives, and posted then.

from S.propagate import Store

# CONSTANTS BEGIN
# stage 1
PICK_FACTS = (1, 2, 3)
# stage 2
GREATER_THAN = 1
# stage 3
DIFFERENT_FROM = 2
# CONSTANTS END

store = Store()
facts = []          # pick's closed world, as its stage gives it
X = "x"
values = []         # the values of x still held, in order (read from the store's domain)
held = []           # comparisons waiting for x to have a domain
failed = []         # constraints whose posting emptied a domain

cp.held("domains", store.dom)
cp.held("constraints posted", store.cons)
cp.problem_alternatives("values of x still held", values)
cp.suspended("comparisons waiting for x to have a domain", held)
cp.held("constraints that emptied a domain", failed)


def pick(v):
    """pick(v): v is one of the facts."""
    return v in facts


def greater(v, k):
    """v > k."""
    return v > k


def different(v, k):
    """v != k."""
    return v != k


def equal(v, k):
    """v = k."""
    return v == k


cp.relations(pick=pick, greater=greater, different=different, equal=equal)


def test(name, k, v):
    """Whether the relation (name, k) holds of the value v of x."""
    if name == "pick":
        return pick(v)
    if name == ">":
        return greater(v, k)
    if name == "!=":
        return different(v, k)
    return equal(v, k)


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
    if name == "=":
        return (k,)
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


def report():
    if X in store.dom and not values:
        print("no solution: the domain of x is empty; constraints that emptied it:", failed)
    for v in values:
        cp.answer("x = %s" % v)


while (s := cp.stage()) is not None:
    if s.k == 1:
        facts[:] = s.constants["PICK_FACTS"]
        arrive("pick")
    elif s.k == 2:
        arrive(">", s.constants["GREATER_THAN"])
    elif s.k == 3:
        arrive("!=", s.constants["DIFFERENT_FROM"])
    values[:] = sorted(store.dom[X]) if X in store.dom else []
    if not s.replay:
        report()
