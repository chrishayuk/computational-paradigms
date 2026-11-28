# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P15b2, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one thread per relation, waiting on a condition variable until the
#       information it needs has arrived; the goals of a case's body posed
#       as threads of their own: The Python Library Reference (3.13),
#       "threading -- Thread-based parallelism": "Thread Objects" (daemon
#       threads), "Condition Objects" (wait_for, notify_all, the with
#       statement on a condition; the default lock is an RLock); the same
#       threads (told, hold, pose, settle) as this configuration's P02, P08
#       and P09c programs
#     - <h> ++ t as a cell of a head and a tail, the tail possibly an
#       unknown, so that a sequence may be produced while it is read (the
#       stream reading): McCarthy, "Recursive functions of symbolic
#       expressions and their computation by machine, Part I", CACM 3(4),
#       1960; this configuration's P09c and P09d (Cell, Unknown)
#     - committed choice: a relation application takes the first case, in
#       the definition's order, whose head and guard hold of what is known,
#       and waits while it cannot tell: Clark and Gregory, "PARLOG: parallel
#       programming in logic", ACM TOPLAS 8(1), 1986 (stream merge by
#       committed choice)
#
# P15b2. One stage: zeros(z) and merge(<seq>, z, m) and position(<k>, m, i),
# in that order, any one, under the stream reading: P15b with the arguments
# of merge swapped. The same text as this configuration's P15b, but for that.
# Each application of a relation is given a thread of its own, in the order
# posed. zeros, read as the greatest relation, binds its sequence to the
# cell <0> ++ rest, rest a new unknown, and poses zeros(rest), without end.
# merge waits until it can tell which of its cases applies (every case needs
# to know whether its first sequence is <>), takes the first that does, in
# the definition's order, binds m's head and poses the merge of the case's
# body. position waits for m's next cell, and either binds i or poses its
# body's goals (position of the rest, and i = j + 1). With <9> first, case 3
# takes its head first, and position binds i; zeros goes on without end, so
# the main thread's wait for the threads to settle does not end: expected
# budget, with i's binding in the registered bindings for observe().

import threading

# CONSTANTS BEGIN
# stage 1
OTHER = (9,)
SOUGHT = 9
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
Z, M, I = Unknown("z"), Unknown("m"), Unknown("i")

known = {}       # the bindings: unknown's name -> value
waiting = []     # relations whose threads wait for a value: (name, places)
failed = []      # relations found not to hold
count = {"busy": 0, "news": 0, "fresh": 0}   # relation threads not waiting; bindings made; new unknowns

cp.bindings(known)
cp.suspended("relations waiting in their threads", waiting)
cp.held("relations found not to hold", failed)


def place(p):
    """The value of a place: an unknown's value, None while it has none."""
    return known.get(p.name) if isinstance(p, Unknown) else p


def fresh(name):
    """A new unknown, for the rest of a sequence or a part of a case."""
    count["fresh"] += 1
    return Unknown("%s%d" % (name, count["fresh"]))


def sequence(seq):
    """The encoding of a given finite sequence as cells ending in ()."""
    t = NIL
    for e in reversed(seq):
        t = Cell(e, t)
    return t


def equal(a, b):
    """The relation a = b, on places. Returns (bindings, goals): the
    unknown given a value, and no goal; False if it does not hold; None if
    it must wait."""
    va, vb = place(a), place(b)
    if va is not None and vb is not None:
        return ([], []) if va is vb or va == vb else False
    if va is not None:
        return [(b, va)], []
    if vb is not None:
        return [(a, vb)], []
    return None


def plus(a, b, c):
    """The relation a + b = c over integers, on places, as equal."""
    va, vb, vc = place(a), place(b), place(c)
    if va is not None and vb is not None:
        if vc is None:
            return [(c, va + vb)], []
        return ([], []) if va + vb == vc else False
    if va is not None and vc is not None:
        return [(b, vc - va)], []
    if vb is not None and vc is not None:
        return [(a, vc - vb)], []
    return None


def zeros(s):
    """The relation zeros(s), by its one case, read as the greatest
    relation: its head's equation on s, and the goal of its body."""
    rest = fresh("z")                               # 1. zeros(<0> ++ s) if zeros(s)
    head = equal(s, Cell(0, rest))
    if head is False:
        return False
    return head[0], [("zeros", (rest,))]


def merge(a, b, m):
    """The relation merge(a, b, m), by committed choice: the first case, in
    the definition's order, whose head and guard hold; None while that
    cannot be told."""
    va = place(a)
    if va is None:
        return None
    if va == NIL:                                   # 1. merge(<>, b, b)
        return equal(m, b)
    vb = place(b)
    if vb is None:
        return None
    if vb == NIL:                                   # 2. merge(<h> ++ a, <>, <h> ++ a)
        return equal(m, a)
    if vb != NIL:                                   # 3. merge(<h> ++ a, b, <h> ++ m) if b != <>
        rest = fresh("m")                           #    and merge(a, b, m)
        head = equal(m, Cell(va.head, rest))
        if head is False:
            return False
        return head[0], [("merge", (va.tail, b, rest))]
    rest = fresh("m")                               # 4. merge(a, <h> ++ b, <h> ++ m) if a != <>
    head = equal(m, Cell(vb.head, rest))            #    and merge(a, b, m)
    if head is False:
        return False
    return head[0], [("merge", (a, vb.tail, rest))]


def position(e, m, i):
    """The relation position(e, m, i), by its cases in order: waits for m's
    next cell; False where m ends."""
    vm = place(m)
    if vm is None:
        return None
    if vm == NIL:                                   # no case holds of <>
        return False
    if vm.head == e:                                # 1. position(e, <e> ++ t, 1)
        return equal(i, 1)
    if vm.head != e:                                # 2. position(e, <h> ++ t, i) if h != e
        j = fresh("j")                              #    and position(e, t, j)
        return [], [("position", (e, vm.tail, j)), ("+", (j, 1, i))]   # and i = j + 1


cp.relations(zeros=zeros, merge=merge, position=position, plus=plus, equal=equal)

RELATION = {"zeros": zeros, "merge": merge, "position": position, "+": plus, "=": equal}


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


def report():
    if failed:
        print("no solution: these relations do not hold:", failed)
        return
    i = place(I)
    if i is not None:
        cp.answer("i = %d" % i)


while (st := cp.stage()) is not None:
    if st.k == 1:
        pose(("zeros", (Z,)))                                           # zeros(z)
        pose(("merge", (sequence(st.constants["OTHER"]), Z, M)))        # and merge(<9>, z, m)
        pose(("position", (st.constants["SOUGHT"], M, I)))              # and position(9, m, i)
    settle()
    if not st.replay:
        report()
