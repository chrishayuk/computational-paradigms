# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P09c, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per relation, waiting on a condition variable until the
#       information it needs has arrived; the goals of a case's body posed
#       as threads of their own: The Python Library Reference (3.13),
#       "threading -- Thread-based parallelism": "Thread Objects" (daemon
#       threads), "Condition Objects" (wait_for, notify_all, the with
#       statement on a condition; the default lock is an RLock); the same
#       threads (told, hold, pose, settle) as this configuration's P02 and
#       P08 programs
#     - <h> ++ t as a cell of a head and a tail, the tail possibly an
#       unknown: McCarthy, "Recursive functions of symbolic expressions and
#       their computation by machine, Part I", CACM 3(4), 1960; The Python
#       Language Reference, "Data model" ("Basic customization", __repr__)
#
# P09c. One computation: gen(<k>, s) and sum3(s, total), in that order.
# Each application of a relation is given a thread of its own, in the order
# posed: gen(<k>, s), then sum3(s, total). gen, by its cases, gives s its
# first cell, <n> ++ rest with rest a new unknown, and poses its body's goal
# gen(n + 1, rest) as a new thread. sum3 waits until s is known as far as
# three elements, then gives total. So the consumer may act on s before the
# producer has finished, as the threads are scheduled. The main thread ends
# the stage when no relation thread is busy, and reports the conjunction's
# solution once s and total have values.

import threading

# CONSTANTS BEGIN
# stage 1
GEN_FROM = 1
GEN_LAST = 5
# CONSTANTS END

changed = threading.Condition()   # guards everything below; notified at every change


class Unknown:
    """An unknown, as a place of a relation: its name."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Cell:
    """The sequence <head> ++ tail, its tail a sequence or an unknown."""

    def __init__(self, head, tail):
        self.head, self.tail = head, tail

    def __repr__(self):
        return "⟨%r⟩ ++ %r" % (self.head, self.tail)


NIL = ()
S, TOTAL = Unknown("s"), Unknown("total")

known = {}       # the bindings: unknown's name -> value
waiting = []     # relations whose threads wait for a value: (name, places)
failed = []      # relations found not to hold
count = {"busy": 0, "news": 0, "fresh": 0}   # relation threads not waiting; bindings made; new unknowns
definition = {}  # gen's last element, as stage 1 gives the definition

cp.bindings(known)
cp.suspended("relations waiting in their threads", waiting)
cp.held("relations found not to hold", failed)


def place(p):
    """The value of a place: an unknown's value, None while it has none."""
    return known.get(p.name) if isinstance(p, Unknown) else p


def fresh():
    """A new unknown, for the rest of a sequence."""
    count["fresh"] += 1
    return Unknown("rest%d" % count["fresh"])


def equal(a, b):
    """The relation a = b, on places. Returns (bindings, goals): the
    unknown given a value, and no goal; False if it does not hold; None if
    it must wait."""
    va, vb = place(a), place(b)
    if va is not None and vb is not None:
        return ([], []) if va == vb else False
    if va is not None:
        return [(b, va)], []
    if vb is not None:
        return [(a, vb)], []
    return None


def gen(n, s):
    """The relation gen(n, s), by its cases in order, n known: its head's
    equation on s, and the goal of its body."""
    n = place(n)
    if n is None:
        return None
    if n > definition["last"]:              # 1. gen(n, <>) if n > 5
        return equal(s, NIL)
    if n <= definition["last"]:             # 2. gen(n, <n> ++ rest) if n <= 5 and gen(n + 1, rest)
        rest = fresh()
        head = equal(s, Cell(n, rest))
        if head is False:
            return False
        return head[0], [("gen", (n + 1, rest))]


def sum3(s, total):
    """The relation sum3(s, total), by its one case: waits until s is known
    as far as its first three elements; fails if s ends before them."""
    firsts = []
    t = place(s)
    while len(firsts) < 3:
        if t is None:
            return None
        if not isinstance(t, Cell):
            return False
        firsts.append(t.head)
        t = place(t.tail)
    p, q, r = firsts                        # 1. sum3(<p, q, r> ++ m, total)
    return equal(total, p + q + r)          #    if p + q + r = total


cp.relations(gen=gen, sum3=sum3, equal=equal)

RELATION = {"gen": gen, "sum3": sum3, "=": equal}


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
        while (outcome := RELATION[name](*places)) is None:
            waiting.append(rel)
            count["busy"] -= 1
            changed.notify_all()
            seen = count["news"]
            changed.wait_for(lambda: count["news"] != seen)
        if outcome is False:
            failed.append(rel)
        else:
            bindings, goals = outcome
            new = False
            for u, v in bindings:
                if u.name not in known:
                    known[u.name] = v
                    new = True
            for goal in goals:
                pose(goal)
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


def elements(p):
    """Output adapter: the elements of a sequence that is known to its end,
    or None if it is not."""
    items = []
    t = place(p)
    while isinstance(t, Cell):
        items.append(t.head)
        t = place(t.tail)
    return items if t == NIL else None


def report():
    if failed:
        print("no solution: these relations do not hold:", failed)
        return
    seq, total = elements(S), place(TOTAL)
    if seq is not None and total is not None:
        cp.answer("s = ⟨%s⟩, total = %s" % (",".join(str(e) for e in seq), total))


while (s := cp.stage()) is not None:
    if s.k == 1:
        definition["last"] = s.constants["GEN_LAST"]
        pose(("gen", (s.constants["GEN_FROM"], S)))     # gen(<k>, s)
        pose(("sum3", (S, TOTAL)))                      # and sum3(s, total)
    settle()
    if not s.replay:
        report()
