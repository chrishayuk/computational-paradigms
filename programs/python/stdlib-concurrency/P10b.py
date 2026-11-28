# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P10b, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per relation, waiting on a condition variable and woken at
#       every change: The Python Library Reference (3.13), "threading --
#       Thread-based parallelism": "Thread Objects" (daemon threads),
#       "Condition Objects" (wait_for, notify_all, the with statement on a
#       condition); the same threads (told, pose, settle) as this
#       configuration's P02 programs
#     - a named quantity as an entry of a dict, replaced by assignment: The
#       Python Language Reference (3.13), "Assignment statements"
#     - the relation d = k * b evaluated in the direction it is used (d from
#       b): METRICS.md, rule 8; "Binary arithmetic operations"
#
# P10b. Stage 1: d = <k> * b, at all times; stages 2-4: b becomes <k>, b
# becomes b + <k>, b becomes <k>.
# b is a named quantity, replaced by assignment, and every replacement wakes
# the waiting threads. The standing relation is given a thread of its own,
# which never ends: each time it is woken, it gives its target the value the
# relation defines from its source's current value, where the source has
# one, and waits again on the condition `changed`. The main thread ends the
# stage when no relation thread is busy.

import threading

# CONSTANTS BEGIN
# stage 1
D_FACTOR = 2
# stage 2
B_FIRST = 10
# stage 3
B_ADDEND = 5
# stage 4
B_THIRD = 7
# CONSTANTS END

NAMES = ("b", "d")

changed = threading.Condition()   # guards everything below; notified at every change
quantities = {}     # the named quantities: name -> current value
waiting = []        # standing relations whose threads wait for a change: (factor, source, target)
count = {"busy": 0, "news": 0}    # relation threads not waiting; replacements made so far

cp.bindings(quantities)
cp.suspended("standing relations waiting in their threads for a change", waiting)


def times(a, b):
    """The relation a * b = c, c from a and b."""
    return a * b


cp.relations(times=times)


def told():
    """With `changed` held, after a replacement: wake every waiting
    relation thread, counting it busy from now."""
    count["news"] += 1
    count["busy"] += len(waiting)
    waiting.clear()
    changed.notify_all()


def hold(rel):
    """The thread of one standing relation, target = factor * source, at
    all times: give the target its value whenever the source has one, then
    wait for the next change."""
    factor, source, target = rel
    with changed:
        while True:
            if source in quantities:
                quantities[target] = times(factor, quantities[source])
            waiting.append(rel)
            count["busy"] -= 1
            changed.notify_all()
            seen = count["news"]
            changed.wait_for(lambda: count["news"] != seen)


def pose(rel):
    """Give a relation that has arrived its own thread."""
    with changed:
        count["busy"] += 1
    threading.Thread(target=hold, args=(rel,), daemon=True).start()


def become(name, value):
    """A replacing stage: the named quantity takes a new value, and the
    waiting relation threads are told."""
    with changed:
        quantities[name] = value
        told()


def settle():
    """Wait until no relation thread is busy."""
    with changed:
        changed.wait_for(lambda: count["busy"] == 0)


while (s := cp.stage()) is not None:
    if s.k == 1:
        pose((s.constants["D_FACTOR"], "b", "d"))                      # d = <k> * b, at all times
    elif s.k == 2:
        become("b", s.constants["B_FIRST"])                             # b becomes <k>
    elif s.k == 3:
        become("b", quantities["b"] + s.constants["B_ADDEND"])          # b becomes b + <k>
    elif s.k == 4:
        become("b", s.constants["B_THIRD"])                             # b becomes <k>
    settle()
    if not s.replay and quantities:
        cp.answer(", ".join("%s = %s" % (n, quantities[n]) for n in NAMES if n in quantities))
