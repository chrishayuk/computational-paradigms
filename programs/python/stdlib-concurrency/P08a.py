# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P08a, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per held relation, waiting on a condition variable until
#       the information it needs (values, or a definition) has arrived: The
#       Python Library Reference (3.13), "threading -- Thread-based
#       parallelism": "Thread Objects" (daemon threads), "Condition Objects"
#       (wait_for, notify_all, the with statement on a condition; a
#       Condition's default lock is reentrant); the same threads as this
#       configuration's P02 programs
#     - a definition that arrives as a def statement executed when its stage
#       is posed: The Python Language Reference (3.13), "Function
#       definitions"
#     - rev and conc by their cases, with "if not a:" as the dispatch on
#       case 1: METRICS.md, rule 3 (the example of conc in Python)
#     - sequences as tuples, indexing and slicing, + on tuples:
#       The Python Tutorial, "Tuples and Sequences"
#
# P08a. Stage 1: a = <x, y, z>; stage 2: rev(a, b), with rev not yet
# defined; stage 3: x = y; stage 4: the definitions of rev and conc;
# stage 5: y = z; stage 6: b = <seq> ++ c.
# Python has no unknowns: each relation is held, as its places, until
# its evaluator can decide it. A place is an unknown (an object of the class
# Unknown, so that any value, a string included, can be a constant) or a
# value; a sequence is a tuple of places, so a = <x, y, z> gives a the value
# (x, y, z), a tuple of three unknowns. = on two sequences of one length is
# decided place by place, and s = p ++ t, with p and s known, by p's places
# and the rest of s.
# rev and conc are defined, by def, when stage 4 is posed, and not before:
# rev(a, b) is decided, by calling rev forwards, as soon as a has a value,
# once rev has been defined: until then its thread waits.
# Each relation, when it arrives, is given a thread of its own, which decides
# it by its evaluator once it can, and until then waits on the condition
# `changed`, which every new binding, and every definition, notifies. The
# main thread ends a stage when no relation thread is busy.

import threading

# CONSTANTS BEGIN
# stage 6
PREFIX = (42,)
# CONSTANTS END

UNKNOWNS = ("a", "b", "c", "x", "y", "z")

changed = threading.Condition()   # guards everything below; notified at every change

class Unknown:
    """An unknown, as a place of a relation: its name."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


UNKNOWN = {n: Unknown(n) for n in UNKNOWNS}
a, b, c, x, y, z = (UNKNOWN[n] for n in UNKNOWNS)

known = {}       # the bindings: unknown -> value (a sequence's places may be unknowns)
waiting = []     # relations whose threads wait for a value or a definition: (name, places)
failed = []      # relations found not to hold
count = {"busy": 0, "news": 0}    # relation threads not waiting; bindings and definitions so far
defined = {}     # the relations whose definitions have arrived

cp.bindings(known)
cp.suspended("relations waiting in their threads", waiting)
cp.held("relations defined", defined)
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
    """The relation rev(a, b), decided by rev forwards once a has a value
    and rev has been defined; None (wait) until then."""
    if a is not None and "rev" in defined:
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


def told():
    """With `changed` held, after a new binding: wake every waiting
    relation thread, counting it busy from now."""
    count["news"] += 1
    count["busy"] += len(waiting)
    waiting.clear()
    changed.notify_all()


def hold(rel):
    """The thread of one relation: decide it, waiting while it cannot."""
    name, places = rel
    with changed:
        while (outcome := EVALUATOR[name](*[place(p) for p in places])) is None:
            waiting.append(rel)
            count["busy"] -= 1
            changed.notify_all()
            seen = count["news"]
            changed.wait_for(lambda: count["news"] != seen)
        if outcome is False:
            failed.append(rel)
        elif isinstance(outcome, list):
            for decided_in_its_stead in outcome:
                pose(decided_in_its_stead)
        else:
            new = False
            for p, v in zip(places, outcome):
                if isinstance(p, Unknown) and v is not None and p.name not in known:
                    known[p.name] = v
                    new = True
            if new:
                told()
        count["busy"] -= 1
        changed.notify_all()


def arrived(name):
    """A definition has arrived: note it, and wake the waiting threads."""
    with changed:
        defined[name] = True
        told()


def pose(rel):
    """Give a relation that has arrived its own thread."""
    with changed:
        count["busy"] += 1
    threading.Thread(target=hold, args=(rel,), daemon=True).start()


def settle():
    """Wait until no relation thread is busy."""
    with changed:
        changed.wait_for(lambda: count["busy"] == 0)


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
        pose(("=", (a, (x, y, z))))
    elif s.k == 2:
        pose(("rev", (a, b)))
    elif s.k == 3:
        pose(("=", (x, y)))
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
        arrived("rev")
    elif s.k == 5:
        pose(("=", (y, z)))
    elif s.k == 6:
        pose(("++", (b, s.constants["PREFIX"], c)))
    settle()
    if not s.replay:
        report()
