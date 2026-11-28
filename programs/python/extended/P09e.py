# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P09e, written before any program was run
#   S mechanisms used: suspension queue (S/suspend.py): Var, deref,
#     Queue.wait, bind, run, held.
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - each relation a goal of the suspension queue (a callable object),
#       which decides it by its evaluator or waits on its unbound unknowns:
#       the S mechanism's docstring (harnesses/python/S/suspend.py); the same
#       Relation and evaluators as this configuration's P02 and P07
#       programs; The Python Language Reference (3.13), "Data model"
#       ("Emulating callable objects")
#
# P09e. One computation of two parts: x = y + <k> and y = x - <k>.
# x and y are Vars. Each relation is a goal of the queue: when run, it
# evaluates (+ or -) and decides, or waits on its unbound unknowns, and is
# run again when one is bound. x = y + k is the relation y + k = x, and
# y = x - k the relation x - k = y.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
X_ADDEND = 1
Y_SUBTRAHEND = 1
# CONSTANTS END

q = Queue()
x, y = Var("x"), Var("y")
unknowns = {"x": x, "y": y}
failed = []     # relations found not to hold

cp.bindings(unknowns)
cp.suspended("goals waiting for a binding", q.held)
cp.held("relations found not to hold", failed)


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


def minus(a, b, c):
    """The relation a - b = c over integers, as plus."""
    if a is not None and b is not None:
        if c is None:
            return a, b, a - b
        return (a, b, c) if a - b == c else False
    if a is not None and c is not None:
        return a, a - c, c
    if b is not None and c is not None:
        return b + c, b, c
    return None


cp.relations(plus=plus, minus=minus)


class Relation:
    """One relation of the problem, as a goal of the queue: its name, its
    evaluator, and its places (each a Var or an integer)."""

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
                    q.bind(p, v)

    def __repr__(self):
        return "%s%r" % (self.name, tuple(self.places))


while (s := cp.stage()) is not None:
    if s.k == 1:
        q.wait(Relation("+", plus, (y, s.constants["X_ADDEND"], x)))        # x = y + <k>
        q.wait(Relation("-", minus, (x, s.constants["Y_SUBTRAHEND"], y)))   # and y = x - <k>
    q.run()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        else:
            told = ["%s = %d" % (n, deref(v)) for n, v in unknowns.items() if not isinstance(deref(v), Var)]
            if told:
                cp.answer(", ".join(told))
