# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core for P10d, written before any program was run
#   idioms:
#     - the stage loop, cp calls, relations held in a list until the
#       information they need arrives: harnesses/python/README.md, sections
#       3 and 8 (x01_total.py); this configuration's P05 programs (pick, the
#       values of x still held, arrive, keep), unchanged but for the
#       relations P10d does not use
#     - a closed world of facts as a tuple; filtering a list by a
#       comprehension; removing entries from a list: The Python Tutorial
#       (3.13), "Tuples and Sequences", "List Comprehensions", "More on
#       Lists"
#     - comparisons on integers: The Python Language Reference, "Value
#       comparisons"
#
# P10d. Stage 1: pick(x), a closed world of <facts>; stage 2: x > <k>;
# stage 3: withdraw x > <k> (the relation of stage 2).
# As in P05, the values of x still held are kept in a list, all at once, and
# each relation, as it arrives, keeps only the values for which it holds.
# The information given and not withdrawn is kept too, in order, with the
# stage that gave each relation. Narrowing the list loses the values a
# relation removed, so a withdrawal restates: the values of x are worked
# out again from the information not withdrawn, in the order it was given.

# CONSTANTS BEGIN
# stage 1
PICK_FACTS = (1, 2, 3)
# stage 2
GREATER_THAN = 1
# CONSTANTS END

values = []         # the values of x still held, in order
x_has_values = []   # [True] once some relation has given x its values
held = []           # comparisons waiting for x to have values: (name, k)
information = []    # the relations given and not withdrawn, in order: (stage, name, k)

cp.problem_alternatives("values of x still held", values)
cp.held("x has been given values", x_has_values)
cp.suspended("comparisons waiting for x to have values", held)
cp.held("information given and not withdrawn", information)

facts = []          # pick's closed world, as stage 1 gives it


def pick(v):
    """pick(v): v is one of the facts."""
    return v in facts


def greater(v, k):
    """v > k."""
    return v > k


cp.relations(pick=pick, greater=greater)


def holds(name, k, v):
    """Whether the relation (name, k) holds of the value v of x."""
    if name == "pick":
        return pick(v)
    return greater(v, k)


def source(name, k):
    """The values a relation can give x by itself, or None if it cannot."""
    if name == "pick":
        return tuple(facts)
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


def tell(stage, name, k=None):
    """A stage adds a relation: it is kept as information, and taken up."""
    information.append((stage, name, k))
    arrive(name, k)


def withdraw(stage):
    """A stage withdraws the relation of an earlier stage: the information
    is everything given so far without it, and the values of x are worked
    out again from that information, in the order it was given."""
    information[:] = [rel for rel in information if rel[0] != stage]
    values.clear()
    x_has_values.clear()
    held.clear()
    for _, name, k in information:
        arrive(name, k)


def report():
    if x_has_values and not values:
        print("no solution: no value of x satisfies the information so far")
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
    if not s.replay:
        report()
