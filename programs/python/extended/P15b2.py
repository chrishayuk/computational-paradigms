# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P15b2, written before any program was run
#   S mechanisms used: suspension queue (S/suspend.py): Var, deref,
#     Queue.wait, bind, run, held.
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - each relation application a goal of S's queue (a callable object)
#       that decides its relation or waits on the Vars it needs; a sequence
#       produced while it is read, as cons cells whose tail is a Var (the
#       stream reading): the S mechanisms' docstrings
#       (harnesses/python/S/suspend.py); this configuration's P09c and P09d
#       (Goal, genu as a producer without end)
#     - committed choice: a goal takes the first case, in the definition's
#       order, whose head and guard hold of what is bound, and waits while it
#       cannot tell: Clark and Gregory, "PARLOG: parallel programming in
#       logic", ACM TOPLAS 8(1), 1986 (stream merge by committed choice)
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as ():
#       McCarthy, "Recursive functions of symbolic expressions and their
#       computation by machine, Part I", CACM 3(4), 1960
#
# P15b2. One stage: zeros(z) and merge(<seq>, z, m) and position(<k>, m, i),
# in that order, any one, under the stream reading: P15b with the arguments
# of merge swapped. The same text as this configuration's P15b, but for that.
# z, m and i are Vars, and each relation application is a goal of the
# queue, posted in the order written. zeros, read as the greatest relation,
# binds its sequence to the cell <0> ++ rest, rest a new Var, and posts
# zeros(rest), without end. merge waits until it can tell which of its cases
# applies (every case needs to know whether its first sequence is <>), takes
# the first that does, in the definition's order, binds m's head and posts
# the merge of the case's body. position waits for m's next cell, and either
# binds i or posts its body's goals (position of the rest, then i = j + 1).
# The queue runs ready goals first in, first out, so it is never empty while
# zeros goes on, and q.run() does not return. With <9> first, case 3 takes
# its head first, and position binds i = 1; zeros goes on: expected budget,
# with i's binding in the registered bindings for observe(), rendered by the
# output adapter Shown.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
OTHER = (9,)
SOUGHT = 9
# CONSTANTS END

q = Queue()
NIL = ()
z, m, i = Var("z"), Var("m"), Var("i")
failed = []         # relations found not to hold


def show(t):
    """Output adapter: a term as the problem writes it, a sequence whose
    tail is an unknown as <...> ++ that unknown."""
    t = deref(t)
    if isinstance(t, Var):
        return t.name
    if not isinstance(t, tuple):
        return str(t)
    items = []
    while isinstance(t, tuple) and len(t) == 2:
        items.append(show(t[0]))
        t = deref(t[1])
    shown = "⟨" + ",".join(items) + "⟩"
    if t == ():
        return shown
    return shown + " ++ " + show(t)


class Shown:
    """Output adapter: an unknown as observe() renders it, its term as the
    problem writes it (a long sequence is rendered without recursion)."""

    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return show(self.v)


cp.bindings({"i": Shown(i), "m": Shown(m), "z": Shown(z)})
cp.suspended("goals waiting for a binding", q.held)
cp.held("relations found not to hold", failed)


def cons(seq):
    """The encoding: a sequence given as a tuple, as cons cells ending in ()."""
    t = ()
    for e in reversed(seq):
        t = (cons(e) if isinstance(e, tuple) else e, t)
    return t


def zeros(s):
    """The relation zeros(s), by its one case, read as the greatest
    relation: binds s by the case's head and posts the goal of its body."""
    rest = Var("z")                                 # 1. zeros(<0> ++ s) if zeros(s)
    if not q.bind(s, (0, rest)):
        return False
    q.wait(Goal("zeros", zeros, (rest,)))
    return True


def merge(a, b, m):
    """The relation merge(a, b, m), by committed choice: the first case, in
    the definition's order, whose head and guard hold; the unbound Var it
    must wait on while that cannot be told."""
    ta = deref(a)
    if isinstance(ta, Var):
        return ta
    if ta == NIL:                                   # 1. merge(<>, b, b)
        return q.bind(m, b)
    tb = deref(b)
    if isinstance(tb, Var):
        return tb
    if tb == NIL:                                   # 2. merge(<h> ++ a, <>, <h> ++ a)
        return q.bind(m, ta)
    if tb != NIL:                                   # 3. merge(<h> ++ a, b, <h> ++ m) if b != <>
        rest = Var("m")                             #    and merge(a, b, m)
        if not q.bind(m, (ta[0], rest)):
            return False
        q.wait(Goal("merge", merge, (ta[1], tb, rest)))
        return True
    rest = Var("m")                                 # 4. merge(a, <h> ++ b, <h> ++ m) if a != <>
    if not q.bind(m, (tb[0], rest)):                #    and merge(a, b, m)
        return False
    q.wait(Goal("merge", merge, (ta, tb[1], rest)))
    return True


def position(e, m, i):
    """The relation position(e, m, i), by its cases in order: the unbound
    Var it must wait on while m's next cell is not known; False where m
    ends."""
    tm = deref(m)
    if isinstance(tm, Var):
        return tm
    if tm == NIL:                                   # no case holds of <>
        return False
    h = deref(tm[0])
    if h == e:                                      # 1. position(e, <e> ++ t, 1)
        return q.bind(i, 1)
    if h != e:                                      # 2. position(e, <h> ++ t, i) if h != e
        j = Var("j")                                #    and position(e, t, j)
        q.wait(Goal("position", position, (e, tm[1], j)))
        q.wait(Goal("+", plus, (j, 1, i)))          #    and i = j + 1
        return True


def plus(a, b, c):
    """The relation a + b = c over integers: computes any one place from the
    other two, or tests them; the unbound Vars it must wait on while two
    places are unknown."""
    ta, tb, tc = deref(a), deref(b), deref(c)
    unbound = [t for t in (ta, tb, tc) if isinstance(t, Var)]
    if not unbound:
        return ta + tb == tc
    if len(unbound) > 1:
        return unbound
    if isinstance(tc, Var):
        return q.bind(tc, ta + tb)
    if isinstance(tb, Var):
        return q.bind(tb, tc - ta)
    return q.bind(ta, tc - tb)


cp.relations(zeros=zeros, merge=merge, position=position, plus=plus)


class Goal:
    """One application of a relation, as a goal of the queue: run, it
    decides the relation, or waits on the Vars the relation names."""

    def __init__(self, name, relation, args):
        self.name, self.relation, self.args = name, relation, args

    def __call__(self):
        outcome = self.relation(*self.args)
        if outcome is False:
            failed.append(self)
        elif isinstance(outcome, Var):
            q.wait(self, outcome)
        elif isinstance(outcome, list):
            q.wait(self, *outcome)

    def __repr__(self):
        return "%s(%s)" % (self.name, ", ".join(show(a) for a in self.args))


def report():
    if failed:
        print("no solution: these relations do not hold:", failed)
        return
    if not isinstance(deref(i), Var):
        cp.answer("i = %s" % show(i))


while (st := cp.stage()) is not None:
    if st.k == 1:
        q.wait(Goal("zeros", zeros, (z,)))                                      # zeros(z)
        q.wait(Goal("merge", merge, (cons(st.constants["OTHER"]), z, m)))       # and merge(<9>, z, m)
        q.wait(Goal("position", position, (st.constants["SOUGHT"], m, i)))      # and position(9, m, i)
    q.run()
    if not st.replay:
        report()
