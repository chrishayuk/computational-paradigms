# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core for P08a, written before any program was run
#   idioms:
#     - the stage loop, cp calls, relations held in a list until their values
#       arrive: harnesses/python/README.md, sections 3 and 8 (x01_total.py)
#     - a definition that arrives as a def statement executed when its stage
#       is posed; a name used before it is bound raises NameError: The Python
#       Language Reference (3.13), "Function definitions", "Naming and
#       binding" ("Resolution of names")
#     - rev and conc by their cases, with "if not a:" as the dispatch on
#       case 1: METRICS.md, rule 3 (the example of conc in Python)
#     - sequences as tuples, indexing and slicing, + on tuples:
#       The Python Tutorial, "Tuples and Sequences"
#
# P08a. Stage 1: a = <x, y, z>; stage 2: rev(a, b), with rev not yet
# defined; stage 3: x = y; stage 4: the definitions of rev and conc;
# stage 5: y = z; stage 6: b = <seq> ++ c.
# Python core has no unknowns: each relation is held, as its places, until
# its evaluator can decide it. A place is an unknown (an object of the class
# Unknown, so that any value, a string included, can be a constant) or a
# value; a sequence is a tuple of places, so a = <x, y, z> gives a the value
# (x, y, z), a tuple of three unknowns. = on two sequences of one length is
# decided place by place, and s = p ++ t, with p and s known, by p's places
# and the rest of s.
# rev and conc are defined, by def, when stage 4 is posed, and not before:
# rev(a, b) is decided, by calling rev forwards, as soon as a has a value,
# whether or not rev has been defined yet. Python's own meaning of a name
# used before it is defined is a NameError.

# CONSTANTS BEGIN
# stage 6
PREFIX = (42,)
# CONSTANTS END

UNKNOWNS = ("a", "b", "c", "x", "y", "z")


class Unknown:
    """An unknown, as a place of a relation: its name."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


UNKNOWN = {n: Unknown(n) for n in UNKNOWNS}
a, b, c, x, y, z = (UNKNOWN[n] for n in UNKNOWNS)

known = {}      # the bindings: unknown -> value (a sequence's places may be unknowns)
held = []       # relations not yet decided, in the order they arrived: (name, places)
failed = []     # relations found not to hold

cp.bindings(known)
cp.suspended("relations waiting for values", held)
cp.held("relations found not to hold", failed)


def equal(a, b):
    """The relation a = b. Each place is a value, or None if unknown.
    Returns both places with every one that can be computed, False if the
    relation does not hold, None if it must wait, or, for two sequences of
    one length, the equations of their places, to be decided in its stead."""
    if a is not None and b is not None:
        if isinstance(a, tuple) and isinstance(b, tuple):
            if len(a) != len(b):
                return False
            return [("=", pair) for pair in zip(a, b)]
        return (a, b) if a == b else False
    if a is not None:
        return a, a
    if b is not None:
        return b, b
    return None


def prefix(s, p, t):
    """The relation s = p ++ t, p a sequence. With s known, the equations of
    p's places with s's first places, and t = the rest of s, decided in its
    stead; with t known, s; with neither, wait (None)."""
    if s is not None and p is not None:
        if not isinstance(s, tuple) or len(s) < len(p):
            return False
        return [("=", pair) for pair in zip(s, p)] + [("=", (t, s[len(p):]))]
    if t is not None and p is not None:
        return (p + t, p, t)
    return None


def reverse(a, b):
    """The relation rev(a, b), decided by rev forwards once a has a value."""
    if a is not None:
        r = rev(a)
        if r is None:                       # no case of rev applies
            return False
        if b is None:
            return a, r
        return [("=", (b, r))]
    return None


cp.relations(equal=equal, prefix=prefix)

EVALUATOR = {"=": equal, "++": prefix, "rev": reverse}


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
            elif isinstance(outcome, list):
                held.extend(outcome)
            else:
                for p, v in zip(places, outcome):
                    if isinstance(p, Unknown) and v is not None:
                        known.setdefault(p.name, v)


def show(t):
    """Output adapter: a place with every known value put in, a sequence as
    the problem writes it."""
    if isinstance(t, Unknown):
        return show(known[t.name]) if t.name in known else t.name
    if isinstance(t, str):
        return "'" + t                    # an atom, with a leading quote
    if isinstance(t, tuple):
        return "⟨" + ",".join(show(e) for e in t) + "⟩"
    return str(t)


def report():
    if failed:
        print("no solution: these relations do not hold:", failed)
    elif any(n in known for n in UNKNOWNS):
        cp.answer(", ".join("%s = %s" % (n, show(known[n])) for n in UNKNOWNS if n in known))


while (s := cp.stage()) is not None:
    if s.k == 1:
        held.append(("=", (a, (x, y, z))))
    elif s.k == 2:
        held.append(("rev", (a, b)))
    elif s.k == 3:
        held.append(("=", (x, y)))
    elif s.k == 4:
        def conc(a, b):
            """conc(a, b, c), forwards: c from a and b, by the definition's cases."""
            if not a:                               # 1. conc(<>, b, b)
                return b
            return (a[0],) + conc(a[1:], b)         # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)

        def rev(a):
            """rev(a, b), forwards: b from a, by the definition's cases."""
            if not a:                               # 1. rev(<>, <>)
                return ()
            return conc(rev(a[1:]), (a[0],))        # 2. rev(<h> ++ l, r) if rev(l, q) and conc(q, <h>, r)

        cp.relations(conc=conc, rev=rev)
    elif s.k == 5:
        held.append(("=", (y, z)))
    elif s.k == 6:
        held.append(("++", (b, s.constants["PREFIX"], c)))
    decide()
    if not s.replay:
        report()
