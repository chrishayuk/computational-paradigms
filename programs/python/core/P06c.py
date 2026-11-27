# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core for P06c, written before any program was run
#   idioms:
#     - the stage loop, cp calls, relations held in a list until their values
#       arrive: harnesses/python/README.md, sections 3 and 8 (x01_total.py)
#     - negation as Python's "not" on a decided relation: The Python Language
#       Reference (3.13), "Boolean operations"
#     - assignment expressions, while and for statements, dict, list:
#       The Python Language Reference, "Assignment expressions", "The while
#       statement", "The for statement"
#
# P06c. Stage 1: not (x = <k>); stage 2: x = <k>.
# Python core has no unknowns: each relation is held, as its places, until
# its evaluator can decide it. x = k gives x its value; not (x = k) holds
# exactly when x = k does not, so it is decided only once x has a value. A
# place is an unknown (an object of the class Unknown, so that any value,
# a string included, can be a constant) or a value.

# CONSTANTS BEGIN
# stage 1
NOT_EQUAL_TO = 1
# stage 2
EQUAL_TO = 1
# CONSTANTS END

UNKNOWNS = ("x",)


class Unknown:
    """An unknown, as a place of a relation: its name."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


x = Unknown("x")

known = {}      # the bindings: unknown -> value
held = []       # relations not yet decided, in the order they arrived: (name, places)
failed = []     # relations found not to hold

cp.bindings(known)
cp.suspended("relations waiting for values", held)
cp.held("relations found not to hold", failed)


def equal(a, b):
    """The relation a = b. Each place is a value, or None if unknown.
    Returns both places with every one that can be computed, False if the
    relation does not hold, or None if it must wait."""
    if a is not None and b is not None:
        return (a, b) if a == b else False
    if a is not None:
        return a, a
    if b is not None:
        return b, b
    return None


def not_equal(a, b):
    """The relation not (a = b): it holds exactly when a = b does not hold.
    Decided only when both places have values; None (wait) otherwise."""
    if a is not None and b is not None:
        return (a, b) if not equal(a, b) else False
    return None


cp.relations(equal=equal, not_equal=not_equal)

EVALUATOR = {"=": equal, "not =": not_equal}


def place(p):
    """The value of a place: an unknown's value, None while it has none."""
    return known.get(p.name) if isinstance(p, Unknown) else p


def decide():
    """Take up the held relations, in the order they arrived, until a pass
    over them decides none."""
    again = True
    while again:
        again = False
        for rel in list(held):
            name, places = rel
            outcome = EVALUATOR[name](*[place(p) for p in places])
            if outcome is None:
                continue
            held.remove(rel)
            again = True
            if outcome is False:
                failed.append(rel)
            else:
                for p, v in zip(places, outcome):
                    if isinstance(p, Unknown) and v is not None:
                        known.setdefault(p.name, v)


while (s := cp.stage()) is not None:
    if s.k == 1:
        held.append(("not =", (x, s.constants["NOT_EQUAL_TO"])))
    elif s.k == 2:
        held.append(("=", (x, s.constants["EQUAL_TO"])))
    decide()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        elif known:
            cp.answer(", ".join("%s = %s" % (n, known[n]) for n in UNKNOWNS if n in known))
