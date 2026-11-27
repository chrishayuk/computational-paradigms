# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P06c, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per held relation, waiting on a condition variable until
#       the information it needs has arrived: The Python Library Reference
#       (3.13), "threading -- Thread-based parallelism": "Thread Objects"
#       (daemon threads), "Condition Objects" (wait_for, notify_all, the
#       with statement on a condition); the same threads as this
#       configuration's P02 programs
#     - negation as Python's "not" on a decided relation: The Python Language
#       Reference (3.13), "Boolean operations"
#     - assignment expressions, while and for statements, dict, list:
#       The Python Language Reference, "Assignment expressions", "The while
#       statement", "The for statement"
#
# P06c. Stage 1: not (x = <k>); stage 2: x = <k>.
# Python has no unknowns: each relation is held, as its places, until
# its evaluator can decide it. x = k gives x its value; not (x = k) holds
# exactly when x = k does not, so it is decided only once x has a value. A
# place is an unknown (an object of the class Unknown, so that any value,
# a string included, can be a constant) or a value.
# Each relation, when it arrives, is given a thread of its own, which decides
# it by its evaluator once it can, and until then waits on the condition
# `changed`, which every new binding notifies. The main thread ends a stage
# when no relation thread is busy: each is waiting or done.

import threading

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

changed = threading.Condition()   # guards everything below; notified at every change
known = {}       # the bindings: unknown -> value
waiting = []     # relations whose threads wait for a value: (name, places)
failed = []      # relations found not to hold
count = {"busy": 0, "news": 0}    # relation threads not waiting; bindings made so far

cp.bindings(known)
cp.suspended("relations waiting in their threads", waiting)
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


def pose(rel):
    """Give a relation that has arrived its own thread."""
    with changed:
        count["busy"] += 1
    threading.Thread(target=hold, args=(rel,), daemon=True).start()


def settle():
    """Wait until no relation thread is busy."""
    with changed:
        changed.wait_for(lambda: count["busy"] == 0)


while (s := cp.stage()) is not None:
    if s.k == 1:
        pose(("not =", (x, s.constants["NOT_EQUAL_TO"])))
    elif s.k == 2:
        pose(("=", (x, s.constants["EQUAL_TO"])))
    settle()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        elif known:
            cp.answer(", ".join("%s = %s" % (n, known[n]) for n in UNKNOWNS if n in known))
