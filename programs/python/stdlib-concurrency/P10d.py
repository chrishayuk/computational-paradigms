# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P10d, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per relation, waiting on a condition variable until the
#       information it needs has arrived: The Python Library Reference
#       (3.13), "threading -- Thread-based parallelism": "Thread Objects"
#       (daemon threads), "Condition Objects" (wait_for, notify_all, the
#       with statement on a condition); this configuration's P05 programs
#       (told, hold, arrive, settle, keep), unchanged but for the relations
#       P10d does not use
#     - a closed world of facts as a tuple; filtering a list by a
#       comprehension; removing entries from a list: The Python Tutorial
#       (3.13), "Tuples and Sequences", "List Comprehensions", "More on
#       Lists"
#
# P10d. Stage 1: pick(x), a closed world of <facts>; stage 2: x > <k>;
# stage 3: withdraw x > <k> (the relation of stage 2).
# As in P05, the values of x still held are kept in a list, all at once;
# each relation, when it arrives, is given a thread of its own, which keeps
# only the values for which the relation holds (waiting, on the condition
# `changed`, while x has no values and the relation cannot give it any).
# The information given and not withdrawn is kept too, in order, with the
# stage that gave each relation. A withdrawal restates: the values of x are
# cleared, and each relation not withdrawn is given a new thread, in the
# order it was given. The main thread ends a stage when no relation thread
# is busy.

import threading

# CONSTANTS BEGIN
# stage 1
PICK_FACTS = (1, 2, 3)
# stage 2
GREATER_THAN = 1
# CONSTANTS END

changed = threading.Condition()   # guards everything below; notified at every change
values = []         # the values of x still held, in order
x_has_values = []   # [True] once some relation has given x its values
waiting = []        # comparisons whose threads wait for x to have values: (name, k)
information = []    # the relations given and not withdrawn, in order: (stage, name, k)
count = {"busy": 0, "news": 0}    # relation threads not waiting; times x was given values

cp.problem_alternatives("values of x still held", values)
cp.held("x has been given values", x_has_values)
cp.suspended("comparisons waiting in their threads for x to have values", waiting)
cp.held("information given and not withdrawn", information)

facts = []          # pick's closed world, as stage 1 gives it


def pick(v):
    """pick(v): v is one of the facts."""
    return v in facts


def greater(v, k):
    """v > k."""
    return v > k


cp.relations(pick=pick, greater=greater)


def holds(name, k, v):
    """Whether the relation (name, k) holds of the value v of x."""
    if name == "pick":
        return pick(v)
    return greater(v, k)


def source(name, k):
    """The values a relation can give x by itself, or None if it cannot."""
    if name == "pick":
        return tuple(facts)
    return None


def told():
    """With `changed` held, after x is given its values: wake every waiting
    relation thread, counting it busy from now."""
    count["news"] += 1
    count["busy"] += len(waiting)
    waiting.clear()
    changed.notify_all()


def hold(rel):
    """The thread of one relation on x: wait while x has no values and the
    relation cannot give it any; then keep only the values for which it
    holds."""
    name, k = rel
    with changed:
        while not x_has_values and source(name, k) is None:
            waiting.append(rel)
            count["busy"] -= 1
            changed.notify_all()
            seen = count["news"]
            changed.wait_for(lambda: count["news"] != seen)
        if not x_has_values:
            values[:] = source(name, k)
            x_has_values.append(True)
            told()
        keep(name, k)
        count["busy"] -= 1
        changed.notify_all()


def arrive(name, k=None):
    """Give a relation on x that has arrived its own thread."""
    with changed:
        count["busy"] += 1
    threading.Thread(target=hold, args=((name, k),), daemon=True).start()


def settle():
    """Wait until no relation thread is busy."""
    with changed:
        changed.wait_for(lambda: count["busy"] == 0)


def keep(name, k):
    """Keep only the values of x for which the relation holds."""
    values[:] = [v for v in values if holds(name, k, v)]


def tell(stage, name, k=None):
    """A stage adds a relation: it is kept as information, and taken up."""
    with changed:
        information.append((stage, name, k))
    arrive(name, k)


def withdraw(stage):
    """A stage withdraws the relation of an earlier stage: the information
    is everything given so far without it, and the values of x are worked
    out again from that information, each relation in a new thread, in the
    order it was given."""
    with changed:
        information[:] = [rel for rel in information if rel[0] != stage]
        values.clear()
        x_has_values.clear()
        again = list(information)
    for _, name, k in again:
        arrive(name, k)


def report():
    if x_has_values and not values:
        print("no solution: no value of x satisfies the information so far")
    for v in values:
        cp.answer("x = %s" % v)


while (s := cp.stage()) is not None:
    if s.k == 1:
        facts[:] = s.constants["PICK_FACTS"]
        tell(1, "pick")                                 # pick(x)
    elif s.k == 2:
        tell(2, ">", s.constants["GREATER_THAN"])       # x > <k>
    elif s.k == 3:
        withdraw(2)                                     # withdraw x > <k>
    settle()
    if not s.replay:
        report()
