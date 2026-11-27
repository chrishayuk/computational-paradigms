# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core for P08c, written before any program was run
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
# P08c. Stage 1: the definition of conc; stage 2: rev(<seq>, b), with rev
# not yet defined; stage 3: rev, case 1 only: rev(<seq>, <seq>); stage 4:
# rev, case 2.
# Python core has no unknowns: each relation is held, as its places, until
# its evaluator can decide it. A place is an unknown (an object of the class
# Unknown, so that any value, a string included, can be a constant) or a
# value; a sequence is a tuple. conc is defined, by def, when stage 1 is
# posed; rev, by def, when stage 3 is posed, with its one case (a fact, from
# the stage's constants), and again when stage 4 is posed, with both cases:
# a function falls through to None where no case applies, which the
# evaluator takes as rev not holding. rev(<seq>, b) is decided, by calling
# rev forwards, as soon as its first place has a value, whether or not rev
# has been defined yet. Python's own meaning of a name used before it is
# defined is a NameError.

# CONSTANTS BEGIN
# stage 2
FORWARDS = (1, 2)
# stage 3
CASE1_FIRST = ()
CASE1_SECOND = ()
# CONSTANTS END

UNKNOWNS = ("b",)


class Unknown:
    """An unknown, as a place of a relation: its name."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


UNKNOWN = {n: Unknown(n) for n in UNKNOWNS}
b = UNKNOWN["b"]

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


cp.relations(equal=equal)

EVALUATOR = {"=": equal, "rev": reverse}

case1 = {}      # rev's case 1, a fact, as stage 3 gives it


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
        def conc(a, b):
            """conc(a, b, c), forwards: c from a and b, by the definition's cases."""
            if not a:                               # 1. conc(<>, b, b)
                return b
            return (a[0],) + conc(a[1:], b)         # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)

        cp.relations(conc=conc)
    elif s.k == 2:
        held.append(("rev", (s.constants["FORWARDS"], b)))
    elif s.k == 3:
        case1["first"], case1["second"] = s.constants["CASE1_FIRST"], s.constants["CASE1_SECOND"]

        def rev(a):
            """rev(a, b), forwards: b from a, by the cases that have arrived."""
            if a == case1["first"]:                 # 1. rev(<>, <>)
                return case1["second"]

        cp.relations(rev=rev)
    elif s.k == 4:
        def rev(a):
            """rev(a, b), forwards: b from a, by the cases that have arrived."""
            if a == case1["first"]:                 # 1. rev(<>, <>)
                return case1["second"]
            if a:                                   # 2. rev(<h> ++ l, r) if rev(l, q) and conc(q, <h>, r)
                q = rev(a[1:])
                return None if q is None else conc(q, (a[0],))

        cp.relations(rev=rev)
    decide()
    if not s.replay:
        report()
