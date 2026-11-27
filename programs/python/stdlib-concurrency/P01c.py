# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P01c, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per held relation, waiting on a condition variable until
#       the information it needs has arrived: The Python Library Reference
#       (3.13), "threading -- Thread-based parallelism": "Thread Objects"
#       (daemon threads), "Condition Objects" (wait_for, notify_all, the
#       with statement on a condition)
#     - sequences as tuples, indexing and slicing, + on tuples:
#       The Python Tutorial, "Tuples and Sequences"
#     - conc by its two cases, with "if not a:" as the dispatch on case 1:
#       METRICS.md, rule 3 (the example of conc in Python)
#
# P01c. One stage: x = <seq> ++ x, that is conc(<seq>, x, x).
# conc is transcribed forwards, as a function of its own. Python has no
# unknowns, and its tuples cannot be cyclic: the relation is given a thread of
# its own, which would decide it once the places it needs have values; until
# then it waits on the condition `changed`, which every new binding notifies.
# The main thread ends a stage when no relation thread is busy: each is
# waiting or done. A place is the name of an unknown (a str) or a value.

import threading

# CONSTANTS BEGIN
# stage 1
PREFIX = (1,)
# CONSTANTS END

UNKNOWNS = ("x",)

changed = threading.Condition()   # guards everything below; notified at every change
known = {}       # the bindings: unknown -> value
waiting = []     # relations whose threads wait for a value: (relation, places)
failed = []      # relations found not to hold
count = {"busy": 0, "news": 0}    # relation threads not waiting; bindings made so far

cp.bindings(known)
cp.suspended("relations waiting in their threads", waiting)
cp.held("relations found not to hold", failed)


def conc(a, b):
    """conc(a, b, c), forwards: c from a and b, by the definition's cases."""
    if not a:                               # 1. conc(<>, b, b)
        return b
    return (a[0],) + conc(a[1:], b)         # 2. conc(<h> ++ a, b, <h> ++ c) if conc(a, b, c)


cp.relations(conc=conc)


def conc_places(a, b, c):
    """The relation conc(a, b, c). Each place is a value, or None if
    unknown. Returns the places with every one that can be computed, False
    if it does not hold, or None if it must wait."""
    if a is not None and b is not None:
        r = conc(a, b)
        if c is None:
            return a, b, r
        return (a, b, c) if r == c else False
    return None


RELATION = {"conc": conc_places}


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
        pose(("conc", (s.constants["PREFIX"], "x", "x")))
    settle()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        elif known:
            cp.answer(", ".join("%s = %s" % (n, show(known[n])) for n in UNKNOWNS if n in known))
