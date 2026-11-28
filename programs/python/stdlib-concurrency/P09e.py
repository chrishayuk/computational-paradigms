# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P09e, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per relation, waiting on a condition variable until a
#       value it needs arrives: The Python Library Reference (3.13),
#       "threading -- Thread-based parallelism": "Thread Objects" (daemon
#       threads), "Condition Objects" (wait_for, notify_all, the with
#       statement on a condition); the same threads (told, hold, pose,
#       settle) and evaluators as this configuration's P02 and P07 programs
#     - integer arithmetic: The Python Language Reference (3.13), "Binary
#       arithmetic operations"
#
# P09e. One computation of two parts: x = y + <k> and y = x - <k>.
# Each relation, when it arrives, is given a thread of its own, which
# decides it by its evaluator (+ or -) once two of its places have values
# and, until then, waits on the condition `changed`. x = y + k is the
# relation y + k = x, and y = x - k the relation x - k = y. The main thread
# ends the stage when no relation thread is busy: each is waiting or done.

import threading

# CONSTANTS BEGIN
# stage 1
X_ADDEND = 1
Y_SUBTRAHEND = 1
# CONSTANTS END

UNKNOWNS = ("x", "y")

changed = threading.Condition()   # guards everything below; notified at every change
known = {}       # the bindings: unknown -> value
waiting = []     # relations whose threads wait for a value: (name, places)
failed = []      # relations found not to hold
count = {"busy": 0, "news": 0}    # relation threads not waiting; bindings made so far

cp.bindings(known)
cp.suspended("relations waiting in their threads", waiting)
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
            for p, x in zip(places, outcome):
                if isinstance(p, str) and x is not None and p not in known:
                    known[p] = x
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
        pose(("+", ("y", s.constants["X_ADDEND"], "x")))         # x = y + <k>
        pose(("-", ("x", s.constants["Y_SUBTRAHEND"], "y")))     # and y = x - <k>
    settle()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        elif known:
            cp.answer(", ".join("%s = %d" % (n, known[n]) for n in UNKNOWNS if n in known))
