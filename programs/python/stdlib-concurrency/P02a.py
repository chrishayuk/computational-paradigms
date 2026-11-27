# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P02a, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per held relation, waiting on a condition variable until
#       the information it needs has arrived: The Python Library Reference
#       (3.13), "threading -- Thread-based parallelism": "Thread Objects"
#       (daemon threads), "Condition Objects" (wait_for, notify_all, the
#       with statement on a condition)
#     - integer arithmetic, // and % on integers: The Python Language
#       Reference, "Binary arithmetic operations"
#
# P02a. Stage 1: R1, u + v = <k>; stage 2: R2, w * u = v; stage 3: R3,
# u + <k> = <k>. All unknowns are integers.
# Each relation, when it arrives, is given a thread of its own. The thread
# decides the relation by its evaluator (+ or *) once two of its places have
# values, computing the third or testing it; until then it waits on the
# condition `changed`, which every new binding notifies. The main thread ends
# a stage when no relation thread is busy: each is waiting or done. A place is
# the name of an unknown (a str) or an integer.

import threading

# CONSTANTS BEGIN
# stage 1
R1_SUM = 16
# stage 3
R3_ADDEND = 10
R3_SUM = 12
# CONSTANTS END

UNKNOWNS = ("u", "v", "w")

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


def times(a, b, c):
    """The relation a * b = c over integers, as plus. Where the known
    factor is 0 and c = 0, the relation holds for every value of the other
    factor, which stays unknown (None)."""
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


cp.relations(plus=plus, times=times)

EVALUATOR = {"R1": plus, "R2": times, "R3": plus}


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
        pose(("R1", ("u", "v", s.constants["R1_SUM"])))
    elif s.k == 2:
        pose(("R2", ("w", "u", "v")))
    elif s.k == 3:
        pose(("R3", ("u", s.constants["R3_ADDEND"], s.constants["R3_SUM"])))
    settle()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        elif known:
            cp.answer(", ".join("%s = %d" % (n, known[n]) for n in UNKNOWNS if n in known))
