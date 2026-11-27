# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core for P05b, written before any program was run
#   idioms:
#     - the stage loop, cp calls, relations held in a list until the
#       information they need arrives: harnesses/python/README.md, sections
#       3 and 8 (x01_total.py)
#     - a closed world of facts as a tuple; filtering a list by a
#       comprehension: The Python Tutorial (3.13), "Tuples and Sequences",
#       "List Comprehensions"
#     - comparisons on integers: The Python Language Reference, "Value
#       comparisons"
#
# P05b. Stage 1: x > <k>; stage 2: pick(x), a closed world of <facts>.
# The values of x still held are kept in a list, all at once. A relation
# that can give x its values (pick, by its facts; x = k, by k) gives them
# when x has none yet; every relation then keeps only the values for which
# it holds. A comparison that arrives while x has no values yet is held
# until values arrive.

# CONSTANTS BEGIN
# stage 1
GREATER_THAN = 1
# stage 2
PICK_FACTS = (1, 2, 3)
# CONSTANTS END

values = []         # the values of x still held, in order
x_has_values = []   # [True] once some relation has given x its values
held = []           # comparisons waiting for x to have values: (name, k)

cp.problem_alternatives("values of x still held", values)
cp.held("x has been given values", x_has_values)
cp.suspended("comparisons waiting for x to have values", held)

facts = []          # pick's closed world, as stage 2 gives it


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


def holds(name, k, v):
    """Whether the relation (name, k) holds of the value v of x."""
    if name == "pick":
        return pick(v)
    if name == ">":
        return greater(v, k)
    if name == "!=":
        return different(v, k)
    return equal(v, k)


def source(name, k):
    """The values a relation can give x by itself, or None if it cannot."""
    if name == "pick":
        return tuple(facts)
    if name == "=":
        return (k,)
    return None


def arrive(name, k=None):
    """Take up one relation on x as it arrives."""
    if not x_has_values:
        given = source(name, k)
        if given is None:
            held.append((name, k))
            return
        values[:] = given
        x_has_values.append(True)
        for rel in list(held):
            held.remove(rel)
            keep(*rel)
    keep(name, k)


def keep(name, k):
    """Keep only the values of x for which the relation holds."""
    values[:] = [v for v in values if holds(name, k, v)]


def report():
    if x_has_values and not values:
        print("no solution: no value of x satisfies the information so far")
    for v in values:
        cp.answer("x = %s" % v)


while (s := cp.stage()) is not None:
    if s.k == 1:
        arrive(">", s.constants["GREATER_THAN"])
    elif s.k == 2:
        facts[:] = s.constants["PICK_FACTS"]
        arrive("pick")
    if not s.replay:
        report()
