# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core for P01a, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#       (the README's example x01_total.py holds a relation in a list until
#       its values arrive, as this program does)
#     - assignment expressions, while and for statements, dict, list:
#       The Python Language Reference (3.13), "Assignment expressions",
#       "The while statement", "The for statement"; The Python Tutorial,
#       "Dictionaries", "More on Lists"
#
# P01a. Stage 1: x = y; stage 2: y = z; stage 3: z = <k>.
# Python core has no unknowns: each equation is held, as a pair of places,
# until one of its places has a value, and then decided. A place is the name
# of an unknown (a str) or a value.

# CONSTANTS BEGIN
# stage 3
Z_VALUE = 2
# CONSTANTS END

UNKNOWNS = ("x", "y", "z")

known = {}      # the bindings: unknown -> value
held = []       # equations not yet decided, in the order they arrived
failed = []     # equations found not to hold

cp.bindings(known)
cp.suspended("equations waiting for a value", held)
cp.held("equations found not to hold", failed)


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


cp.relations(equal=equal)


def place(p):
    """The value of a place: an unknown's value, None while it has none."""
    return known.get(p) if isinstance(p, str) else p


def decide():
    """Take up the held equations, in the order they arrived, until a pass
    over them decides none."""
    again = True
    while again:
        again = False
        for eq in list(held):
            outcome = equal(*[place(p) for p in eq])
            if outcome is None:
                continue
            held.remove(eq)
            again = True
            if outcome is False:
                failed.append(eq)
            else:
                for p, x in zip(eq, outcome):
                    if isinstance(p, str):
                        known.setdefault(p, x)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        held.append(("x", "y"))
    elif s.k == 2:
        held.append(("y", "z"))
    elif s.k == 3:
        held.append(("z", s.constants["Z_VALUE"]))
    decide()
    if not s.replay:
        if failed:
            print("no solution: these equations do not hold:", failed)
        elif known:
            cp.answer(", ".join("%s = %s" % (n, show(known[n])) for n in UNKNOWNS if n in known))
