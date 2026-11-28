# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P16b, written before any program was run
#   S mechanisms used: suspension queue (S/suspend.py): Var, deref,
#     Queue.wait, bind, run, held.
#   idioms:
#     - the stage loop, cp calls, s.params["n"]; computations registered
#       with cp.computation for the harness to spawn, the sizes they need
#       kept by main for them: harnesses/python/README.md, sections 3, 3.4
#       and 8, and its qualification program x03_two.py
#     - each relation a goal of S's queue (Relation, a callable object) that
#       evaluates and decides it, or waits on its unbound unknowns and is run
#       again when one of them is bound: this configuration's P02 and P07
#       programs (Relation, equal and plus, as there); the S mechanisms' docstrings
#       (harnesses/python/S/suspend.py: wait, bind, run; "a goal waiting on
#       several vars is woken once")
#     - integer arithmetic: The Python Language Reference (3.13), "Binary
#       arithmetic operations"
#
# P16b. Four contributors, m = n/4. Stage 1: contributor c (c = 1 to 4),
# a separate computation (spawned by the harness: here one after another),
# contributes succ(x_i, x_(i+1)) for i = (c - 1)m + 1, ..., cm, ascending;
# stage 2: total = x_1 + x_(m+1) + x_(2m+1) + x_(3m+1) + x_(4m+1); stage 3:
# x_1 = <k>. Stages 2 and 3 are main's. The contributors share the one queue
# and its Vars (the program's module: one database).
# All unknowns are integers, each a Var. The sum of stage 2 is posed as its
# primitive relations, (((x_1 + x_(m+1)) + x_(2m+1)) + x_(3m+1)) + x_(4m+1)
# = total, with fresh unknowns t1, t2, t3 (SPECIFICATION.md, "Arithmetic and
# comparison"). Each relation is a goal of the queue: when it is run it
# evaluates and computes a place or tests it, or waits on its unbound
# unknowns; a binding wakes only the goals waiting on that Var. Goals are run
# in the order posted, first in, first out. The tests of which places are
# known and the wait are R and C (METRICS.md, rule 19).

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 3
VALUE = 0
# CONSTANTS END

q = Queue()
unknowns = {}   # the unknowns, by name: name -> Var
failed = []     # relations found not to hold
sizes = {}      # n and m, kept by main for the contributors once stage 1 is posed

cp.bindings(unknowns)
cp.suspended("goals waiting for a binding", q.held)
cp.held("relations found not to hold", failed)


def succ(a, b):
    """The relation succ(a, b): b = a + 1, over integers. Each place is an
    integer, or None if unknown. Returns both places with every one that
    can be computed, False if the relation does not hold, or None if it
    must wait."""
    if a is not None and b is not None:
        return (a, b) if b == a + 1 else False
    if a is not None:
        return a, a + 1
    if b is not None:
        return b - 1, b
    return None


def equal(a, b):
    """The relation a = b. Each place is an integer, or None if unknown.
    Returns both places with every one that can be computed, False if the
    relation does not hold, or None if it must wait."""
    if a is not None and b is not None:
        return (a, b) if a == b else False
    if a is not None:
        return a, a
    if b is not None:
        return b, b
    return None


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


cp.relations(succ=succ, equal=equal, plus=plus)


class Relation:
    """One relation of the problem, as a goal of the queue: its name, its
    evaluator, and its places (each a Var or a value)."""

    def __init__(self, name, evaluate, places):
        self.name, self.evaluate, self.places = name, evaluate, places

    def __call__(self):
        values = [deref(p) for p in self.places]
        outcome = self.evaluate(*[None if isinstance(v, Var) else v for v in values])
        if outcome is None:
            q.wait(self, *[v for v in values if isinstance(v, Var)])
        elif outcome is False:
            failed.append(self)
        else:
            for p, v in zip(values, outcome):
                if isinstance(p, Var) and v is not None:
                    if not q.bind(p, v):
                        failed.append(self)

    def __repr__(self):
        return "%s%r" % (self.name, tuple(self.places))


def x(i):
    """The unknown x_i, a Var made when it is first named."""
    name = "x_%d" % i
    if name not in unknowns:
        unknowns[name] = Var(name)
    return unknowns[name]


def unknown(name):
    """A fresh unknown of a decomposition, a Var made when it is first named."""
    if name not in unknowns:
        unknowns[name] = Var(name)
    return unknowns[name]


def report():
    names = ["x_%d" % i for i in range(1, sizes["n"] + 2)] + ["total"]
    if failed:
        print("no solution: these relations do not hold:", failed)
        return
    told = ["%s = %s" % (u, deref(unknowns[u])) for u in names
            if u in unknowns and not isinstance(deref(unknowns[u]), Var)]
    if told:
        cp.answer(", ".join(told))


def contribute(c):
    """Contributor c's part: succ(x_i, x_(i+1)) for its segment, ascending."""
    m = sizes["m"]
    for i in range((c - 1) * m + 1, c * m + 1):
        q.wait(Relation("succ", succ, (x(i), x(i + 1))))              # succ(x_i, x_(i+1))
    q.run()
    report()


def C1():
    contribute(1)


def C2():
    contribute(2)


def C3():
    contribute(3)


def C4():
    contribute(4)


cp.computation("C1", C1)
cp.computation("C2", C2)
cp.computation("C3", C3)
cp.computation("C4", C4)

while (st := cp.stage()) is not None:
    if st.k == 1:
        sizes["n"] = st.params["n"]
        sizes["m"] = st.params["n"] // 4                       # the contributors are spawned after main's part
    elif st.k == 2:
        m = sizes["m"]                                          # total = x_1 + x_(m+1) + x_(2m+1) + x_(3m+1) + x_(4m+1)
        q.wait(Relation("+", plus, (x(1), x(m + 1), unknown("t1"))))
        q.wait(Relation("+", plus, (unknown("t1"), x(2 * m + 1), unknown("t2"))))
        q.wait(Relation("+", plus, (unknown("t2"), x(3 * m + 1), unknown("t3"))))
        q.wait(Relation("+", plus, (unknown("t3"), x(4 * m + 1), unknown("total"))))
    elif st.k == 3:
        q.wait(Relation("=", equal, (x(1), st.constants["VALUE"])))   # x_1 = <k>
    q.run()
    if st.k > 1 and not st.replay:
        report()
