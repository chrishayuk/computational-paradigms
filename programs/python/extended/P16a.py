# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P16a, written before any program was run
#   S mechanisms used: suspension queue (S/suspend.py): Var, deref,
#     Queue.wait, bind, run, held.
#   idioms:
#     - the stage loop, cp calls, s.params["n"] and s.params["order"]:
#       harnesses/python/README.md, sections 3 and 8
#     - each relation a goal of S's queue (Relation, a callable object) that
#       evaluates and decides it, or waits on its unbound unknowns and is run
#       again when one of them is bound: this configuration's P02 and P07
#       programs (Relation, equal, as there); the S mechanisms' docstrings
#       (harnesses/python/S/suspend.py: wait, bind, run; "a goal waiting on
#       several vars is woken once")
#     - integer arithmetic: The Python Language Reference (3.13), "Binary
#       arithmetic operations"
#
# P16a. Stage 1: succ(x_i, x_(i+1)) for i = 1, ..., n - 1, in the instance's
# arrival order (s.params["order"]); stage 2: x_j = <k>, j = ceil(n/2).
# All unknowns are integers, each a Var. Each relation is a goal of the
# queue: when it is run it evaluates and computes a place or tests it, or
# waits on its unbound unknowns; a binding wakes only the goals waiting on
# that Var. Goals are run in the order posted, first in, first out. The
# tests of which places are known and the wait are R and C (METRICS.md,
# rule 19).

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 2
VALUE = 0
# CONSTANTS END

q = Queue()
unknowns = {}   # the unknowns, by name: name -> Var
failed = []     # relations found not to hold

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


cp.relations(succ=succ, equal=equal)


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


def arrival(order, n):
    """The i of the relations succ(x_i, x_(i+1)), i = 1, ..., n - 1, in the
    arrival order the problem fixes."""
    if order == "ascending":
        return list(range(1, n))
    if order == "descending":
        return list(range(n - 1, 0, -1))
    if order == "interleaved":
        return list(range(1, n, 2)) + list(range(2, n, 2))


def report(names):
    if failed:
        print("no solution: these relations do not hold:", failed)
        return
    told = ["%s = %s" % (u, deref(unknowns[u])) for u in names
            if u in unknowns and not isinstance(deref(unknowns[u]), Var)]
    if told:
        cp.answer(", ".join(told))


while (st := cp.stage()) is not None:
    n = st.params["n"]
    names = ["x_%d" % i for i in range(1, n + 1)]
    if st.k == 1:
        for i in arrival(st.params["order"][0], n):
            q.wait(Relation("succ", succ, (x(i), x(i + 1))))          # succ(x_i, x_(i+1))
    elif st.k == 2:
        q.wait(Relation("=", equal, (x((n + 1) // 2), st.constants["VALUE"])))   # x_j = <k>, j = ceil(n/2)
    q.run()
    if not st.replay:
        report(names)
