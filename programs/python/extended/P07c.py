# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P07c, written before any program was run
#   S mechanisms used: suspension queue (S/suspend.py): Var, deref,
#     Queue.wait, bind, run, held
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - a relation as a goal of the suspension queue, which waits on its
#       unbound unknowns and is run again when one is bound: the S
#       mechanism's docstring (harnesses/python/S/suspend.py) and the
#       qualification program x01_extended.py; the same goals as this
#       configuration's P02 programs
#     - integer arithmetic, // and % on integers: The Python Language
#       Reference (3.13), "Binary arithmetic operations"
#     - a callable object: The Python Language Reference, "Data model"
#       ("Emulating callable objects", "Basic customization")
#
# P07c. One stage: x + y = <k>.
# All unknowns are integers, each a Var. Each relation is a goal of the
# queue: when it is run it evaluates (=, +, -, *) and computes a place or
# tests it, or waits on its unbound unknowns, and is run again when one of
# them is bound. Goals are run in the order posted.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
SUM = 10
# CONSTANTS END

q = Queue()
x = Var("x")
y = Var("y")
unknowns = {"x": x, "y": y}
failed = []     # relations found not to hold

cp.bindings(unknowns)
cp.suspended("goals waiting for a binding", q.held)
cp.held("relations found not to hold", failed)


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


def times(a, b, c):
    """The relation a * b = c over integers, as plus. Where the known
    factor is 0 and c = 0, the relation holds for every value of the other
    factor, which stays unknown (None); where c is not a multiple of the
    known factor, no integer satisfies it."""
    if a is not None and b is not None:
        if c is None:
            return a, b, a * b
        return (a, b, c) if a * b == c else False
    if a is not None and c is not None:
        if a != 0:
            return (a, c // a, c) if c % a == 0 else False
        return (a, None, c) if c == 0 else False
    if b is not None and c is not None:
        if b != 0:
            return (c // b, b, c) if c % b == 0 else False
        return (None, b, c) if c == 0 else False
    return None


cp.relations(equal=equal, plus=plus, minus=minus, times=times)



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


while (s := cp.stage()) is not None:
    if s.k == 1:
        q.wait(Relation("+", plus, (x, y, s.constants["SUM"])))
    q.run()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        else:
            told = ["%s = %s" % (n, deref(v)) for n, v in unknowns.items() if not isinstance(deref(v), Var)]
            if told:
                cp.answer(", ".join(told))
