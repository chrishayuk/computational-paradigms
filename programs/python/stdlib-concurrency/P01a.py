# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P01a, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per held relation, waiting on a condition variable until
#       the information it needs has arrived: The Python Library Reference
#       (3.13), "threading -- Thread-based parallelism": "Thread Objects"
#       (daemon threads), "Condition Objects" (wait_for, notify_all, the
#       with statement on a condition)
#     - assignment expressions, dict, list: The Python Language Reference,
#       "Assignment expressions"; The Python Tutorial, "Dictionaries"
#
# P01a. Stage 1: x = y; stage 2: y = z; stage 3: z = <k>.
# Python has no unknowns: each equation, when it arrives, is given a thread of
# its own, which decides it once one of its places has a value; until then it
# waits on the condition `changed`, which every new binding notifies. The main
# thread ends a stage when no relation thread is busy: each is waiting or
# done. A place is the name of an unknown (a str) or a value.

import threading

# CONSTANTS BEGIN
# stage 3
Z_VALUE = 2
# CONSTANTS END

UNKNOWNS = ("x", "y", "z")

changed = threading.Condition()   # guards everything below; notified at every change
known = {}       # the bindings: unknown -> value
waiting = []     # relations whose threads wait for a value: (relation, places)
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


cp.relations(equal=equal)

RELATION = {"=": equal}


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
        while (outcome := RELATION[name](*[place(p) for p in places])) is None:
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
                if isinstance(p, str) and p not in known:
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


def show(x):
    """Output adapter: a sequence as the problem writes it, anything else by str()."""
    if isinstance(x, tuple):
        return "⟨" + ",".join(show(e) for e in x) + "⟩"
    return str(x)


while (s := cp.stage()) is not None:
    if s.k == 1:
        pose(("=", ("x", "y")))
    elif s.k == 2:
        pose(("=", ("y", "z")))
    elif s.k == 3:
        pose(("=", ("z", s.constants["Z_VALUE"])))
    settle()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        elif known:
            cp.answer(", ".join("%s = %s" % (n, show(known[n])) for n in UNKNOWNS if n in known))
