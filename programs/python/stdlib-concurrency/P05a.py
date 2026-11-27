# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P05a, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per relation, waiting on a condition variable until the
#       information it needs has arrived: The Python Library Reference
#       (3.13), "threading -- Thread-based parallelism": "Thread Objects"
#       (daemon threads), "Condition Objects" (wait_for, notify_all, the
#       with statement on a condition); the same threads as this
#       configuration's P02 programs
#     - a closed world of facts as a tuple; filtering a list by a
#       comprehension: The Python Tutorial (3.13), "Tuples and Sequences",
#       "List Comprehensions"
#     - comparisons on integers: The Python Language Reference, "Value
#       comparisons"
#
# P05a. Stage 1: pick(x), a closed world of <facts>; stage 2: x > <k>;
# stage 3: x != <k>.
# The values of x still held are kept in a list, all at once. A relation
# that can give x its values (pick, by its facts; x = k, by k) gives them
# when x has none yet; every relation then keeps only the values for which
# it holds. Each relation, when it arrives, is given a thread of its own;
# a comparison that arrives while x has no values yet waits, on the
# condition `changed`, until values arrive. The main thread ends a stage
# when no relation thread is busy: each is waiting or done.

import threading

# CONSTANTS BEGIN
# stage 1
PICK_FACTS = (1, 2, 3)
# stage 2
GREATER_THAN = 1
# stage 3
DIFFERENT_FROM = 2
# CONSTANTS END

changed = threading.Condition()   # guards everything below; notified at every change
values = []         # the values of x still held, in order
x_has_values = []   # [True] once some relation has given x its values
waiting = []        # comparisons whose threads wait for x to have values: (name, k)
count = {"busy": 0, "news": 0}    # relation threads not waiting; times x was given values

cp.problem_alternatives("values of x still held", values)
cp.held("x has been given values", x_has_values)
cp.suspended("comparisons waiting in their threads for x to have values", waiting)

facts = []          # pick's closed world, as stage 1 gives it


def pick(v):
    """pick(v): v is one of the facts."""
    return v in facts


def greater(v, k):
    """v > k."""
    return v > k


def different(v, k):
    """v != k."""
    return v != k


def equal(v, k):
    """v = k."""
    return v == k


cp.relations(pick=pick, greater=greater, different=different, equal=equal)


def holds(name, k, v):
    """Whether the relation (name, k) holds of the value v of x."""
    if name == "pick":
        return pick(v)
    if name == ">":
        return greater(v, k)
    if name == "!=":
        return different(v, k)
    return equal(v, k)


def source(name, k):
    """The values a relation can give x by itself, or None if it cannot."""
    if name == "pick":
        return tuple(facts)
    if name == "=":
        return (k,)
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


def report():
    if x_has_values and not values:
        print("no solution: no value of x satisfies the information so far")
    for v in values:
        cp.answer("x = %s" % v)


while (s := cp.stage()) is not None:
    if s.k == 1:
        facts[:] = s.constants["PICK_FACTS"]
        arrive("pick")
    elif s.k == 2:
        arrive(">", s.constants["GREATER_THAN"])
    elif s.k == 3:
        arrive("!=", s.constants["DIFFERENT_FROM"])
    settle()
    if not s.replay:
        report()
