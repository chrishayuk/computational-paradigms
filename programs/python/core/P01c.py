# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core for P01c, written before any program was run
#   idioms:
#     - the stage loop, cp calls, a relation held in a list until its values
#       arrive: harnesses/python/README.md, sections 3 and 8 (x01_total.py)
#     - sequences as tuples, indexing and slicing, + on tuples:
#       The Python Tutorial (3.13), "Tuples and Sequences"; The Python
#       Library Reference, "Sequence Types -- list, tuple, range"
#     - conc by its two cases, with "if not a:" as the dispatch on case 1:
#       METRICS.md, rule 3 (the example of conc in Python)
#
# P01c. One stage: x = <seq> ++ x, that is conc(<seq>, x, x).
# conc is transcribed forwards, as a function of its own. Python core has no
# unknowns, and its tuples cannot be cyclic: the relation is held, as its
# three places, until the places it needs have values. A place is the name of
# an unknown (a str) or a value.

# CONSTANTS BEGIN
# stage 1
PREFIX = (1,)
# CONSTANTS END

UNKNOWNS = ("x",)

known = {}      # the bindings: unknown -> value
held = []       # relations not yet decided: (a, b, c) of conc(a, b, c)
failed = []     # relations found not to hold

cp.bindings(known)
cp.suspended("relations waiting for a value", held)
cp.held("relations found not to hold", failed)


def conc(a, b):
    """conc(a, b, c), forwards: c from a and b, by the definition's cases."""
    if not a:                               # 1. conc(<>, b, b)
        return b
    return (a[0],) + conc(a[1:], b)         # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)


cp.relations(conc=conc)


def conc_places(a, b, c):
    """The relation conc(a, b, c). Each place is a value, or None if
    unknown. Returns the places with every one that can be computed, False
    if it does not hold, or None if it must wait."""
    if a is not None and b is not None:
        r = conc(a, b)
        if c is None:
            return a, b, r
        return (a, b, c) if r == c else False
    return None


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
            outcome = conc_places(*[place(p) for p in rel])
            if outcome is None:
                continue
            held.remove(rel)
            again = True
            if outcome is False:
                failed.append(rel)
            else:
                for p, x in zip(rel, outcome):
                    if isinstance(p, str):
                        known.setdefault(p, x)


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        held.append((s.constants["PREFIX"], "x", "x"))
    decide()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        elif known:
            cp.answer(", ".join("%s = %s" % (n, show(known[n])) for n in UNKNOWNS if n in known))
