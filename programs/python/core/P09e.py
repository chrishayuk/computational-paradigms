# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core for P09e, written before any program was run
#   idioms:
#     - the stage loop, cp calls, relations held in a list until their values
#       arrive: harnesses/python/README.md, sections 3 and 8 (x01_total.py);
#       the same holding loop (decide) and evaluators as this
#       configuration's P02 and P07 programs
#     - integer arithmetic: The Python Language Reference (3.13), "Binary
#       arithmetic operations"
#
# P09e. One computation of two parts: x = y + <k> and y = x - <k>.
# Python core has no unknowns: each relation is held, as its three places,
# until two of them have values, and then decided by its evaluator (+ or -),
# which computes the third place or tests it. x = y + k is the relation
# y + k = x, and y = x - k the relation x - k = y. A place is the name of an
# unknown (a str) or an integer.

# CONSTANTS BEGIN
# stage 1
X_ADDEND = 1
Y_SUBTRAHEND = 1
# CONSTANTS END

UNKNOWNS = ("x", "y")

known = {}      # the bindings: unknown -> value
held = []       # relations not yet decided, in the order they arrived: (name, places)
failed = []     # relations found not to hold

cp.bindings(known)
cp.suspended("relations waiting for values", held)
cp.held("relations found not to hold", failed)


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


cp.relations(plus=plus, minus=minus)

EVALUATOR = {"+": plus, "-": minus}


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


while (s := cp.stage()) is not None:
    if s.k == 1:
        held.append(("+", ("y", s.constants["X_ADDEND"], "x")))         # x = y + <k>
        held.append(("-", ("x", s.constants["Y_SUBTRAHEND"], "y")))     # and y = x - <k>
    decide()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        elif known:
            cp.answer(", ".join("%s = %d" % (n, known[n]) for n in UNKNOWNS if n in known))
