# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P09d, written before any program was run
#   S mechanisms used: suspension queue (S/suspend.py): Var, deref,
#     Queue.wait, bind, run, held.
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - each relation a goal of the suspension queue (a callable object),
#       which decides it or waits on an unbound Var and is run again when it
#       is bound; the goals of a case's body posted to the queue: the S
#       mechanism's docstring (harnesses/python/S/suspend.py); this
#       configuration's P02 programs (Relation); The Python Language
#       Reference (3.13), "Data model" ("Emulating callable objects")
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as (),
#       the tail possibly an unbound Var: McCarthy, "Recursive functions of
#       symbolic expressions and their computation by machine, Part I",
#       CACM 3(4), 1960; systems/python/measurement.md, section 2
#
# P09d. One computation: genu(<k>, s) and sum3(s, total), in that order.
# The same text as this configuration's P09c, with genu in place of gen.
# s and total are Vars. Each relation is a goal of the queue, posted in the
# order written. genu, by its one case, binds s to its first cell, <n> ++
# rest with rest a new Var, and posts its body's goal genu(n + 1, rest),
# without end. sum3 walks s; where it meets an unbound Var it waits on it,
# and it binds total once three elements are known, while the producer goes
# on. The queue runs ready goals first in, first out, so it is never empty
# while genu goes on; the conjunction's solution would be reported only once
# no goal is ready and s is known to its end.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
GENU_FROM = 1
# CONSTANTS END

q = Queue()
NIL = ()
seq, total = Var("s"), Var("total")
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


cp.bindings({"s": Shown(seq), "total": Shown(total)})
cp.suspended("goals waiting for a binding", q.held)
cp.held("relations found not to hold", failed)


def genu(n, s):
    """The relation genu(n, s), by its one case, n known: binds s by the
    case's head and posts the goal of its body."""
    rest = Var("rest")                              # 1. genu(n, <n> ++ rest) if genu(n + 1, rest)
    if not q.bind(s, (n, rest)):
        return False
    q.wait(Goal("genu", genu, (n + 1, rest)))
    return True


def sum3(s, total):
    """The relation sum3(s, total), by its one case: the unbound Var it must
    wait on, while s is not known as far as three elements; False if s ends
    before them."""
    firsts = []
    t = deref(s)
    while len(firsts) < 3:
        if isinstance(t, Var):
            return t
        if not (isinstance(t, tuple) and len(t) == 2):
            return False
        firsts.append(deref(t[0]))
        t = deref(t[1])
    p, q_, r = firsts                               # 1. sum3(<p, q, r> ++ m, total)
    return q.bind(total, p + q_ + r)                #    if p + q + r = total


cp.relations(genu=genu, sum3=sum3)


class Goal:
    """One application of a relation, as a goal of the queue: run, it
    decides the relation, or waits on the Var the relation names."""

    def __init__(self, name, relation, args):
        self.name, self.relation, self.args = name, relation, args

    def __call__(self):
        outcome = self.relation(*self.args)
        if outcome is False:
            failed.append(self)
        elif isinstance(outcome, Var):
            q.wait(self, outcome)

    def __repr__(self):
        return "%s(%s)" % (self.name, ", ".join(show(a) for a in self.args))


def report():
    if failed:
        print("no solution: these relations do not hold:", failed)
        return
    t = deref(seq)
    while isinstance(t, tuple) and len(t) == 2:
        t = deref(t[1])
    if t == NIL and not isinstance(deref(total), Var):
        cp.answer("s = %s, total = %s" % (show(seq), show(total)))


while (s := cp.stage()) is not None:
    if s.k == 1:
        q.wait(Goal("genu", genu, (s.constants["GENU_FROM"], seq)))  # genu(<k>, s)
        q.wait(Goal("sum3", sum3, (seq, total)))                    # and sum3(s, total)
    q.run()
    if not s.replay:
        report()
