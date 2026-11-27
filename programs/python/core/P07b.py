# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core for P07b, written before any program was run
#   idioms:
#     - the stage loop, cp calls, relations held in a list until their values
#       arrive: harnesses/python/README.md, sections 3 and 8 (x01_total.py)
#     - integer arithmetic, // and % on integers: The Python Language
#       Reference (3.13), "Binary arithmetic operations"
#     - assignment expressions, while and for statements, dict, list:
#       The Python Language Reference, "Assignment expressions", "The while
#       statement", "The for statement"
#
# P07b. One stage: x + y = <k>, x - y = <k>, in that order.
# All unknowns are integers. Python core has no unknowns: each relation is
# held, as its places, until its evaluator (=, +, -, *) can compute a place
# or test it, and then decided. A place is the name of an unknown (a str) or
# an integer.

# CONSTANTS BEGIN
# stage 1
SUM = 10
DIFFERENCE = 4
# CONSTANTS END

UNKNOWNS = ("x", "y")

known = {}      # the bindings: unknown -> value
held = []       # relations not yet decided, in the order they arrived: (name, places)
failed = []     # relations found not to hold

cp.bindings(known)
cp.suspended("relations waiting for values", held)
cp.held("relations found not to hold", failed)


def equal(a, b):
    """The relation a = b. Each place is an integer, or None if unknown.
    Returns both places with every one that can be computed, False if the
    relation does not hold, or None if it must wait."""
    if a is not None and b is not None:
        return (a, b) if a == b else False
    if a is not None:
        return a, a
    if b is not None:
        return b, b
    return None


def plus(a, b, c):
    """The relation a + b = c over integers. Each place is an integer, or
    None if unknown. Returns the places with every one that can be
    computed, False if the relation does not hold, or None if it must wait."""
    if a is not None and b is not None:
        if c is None:
            return a, b, a + b
        return (a, b, c) if a + b == c else False
    if a is not None and c is not None:
        return a, c - a, c
    if b is not None and c is not None:
        return c - b, b, c
    return None


def minus(a, b, c):
    """The relation a - b = c over integers, as plus."""
    if a is not None and b is not None:
        if c is None:
            return a, b, a - b
        return (a, b, c) if a - b == c else False
    if a is not None and c is not None:
        return a, a - c, c
    if b is not None and c is not None:
        return b + c, b, c
    return None


def times(a, b, c):
    """The relation a * b = c over integers, as plus. Where the known
    factor is 0 and c = 0, the relation holds for every value of the other
    factor, which stays unknown (None); where c is not a multiple of the
    known factor, no integer satisfies it."""
    if a is not None and b is not None:
        if c is None:
            return a, b, a * b
        return (a, b, c) if a * b == c else False
    if a is not None and c is not None:
        if a != 0:
            return (a, c // a, c) if c % a == 0 else False
        return (a, None, c) if c == 0 else False
    if b is not None and c is not None:
        if b != 0:
            return (c // b, b, c) if c % b == 0 else False
        return (None, b, c) if c == 0 else False
    return None


cp.relations(equal=equal, plus=plus, minus=minus, times=times)

EVALUATOR = {"=": equal, "+": plus, "-": minus, "*": times}


def place(p):
    """The value of a place: an unknown's value, None while it has none."""
    return known.get(p) if isinstance(p, str) else p


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
                for p, x in zip(places, outcome):
                    if isinstance(p, str) and x is not None:
                        known.setdefault(p, x)


def report():
    if failed:
        print("no solution: these relations do not hold:", failed)
    elif any(n in known for n in UNKNOWNS):
        cp.answer(", ".join("%s = %d" % (n, known[n]) for n in UNKNOWNS if n in known))


while (s := cp.stage()) is not None:
    if s.k == 1:
        held.append(("+", ("x", "y", s.constants["SUM"])))
        held.append(("-", ("x", "y", s.constants["DIFFERENCE"])))
    decide()
    if not s.replay:
        report()
