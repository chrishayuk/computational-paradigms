# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P02c, written before any program was run
#   S mechanism used: suspension queue (S/suspend.py): Var, deref, Queue
#     (wait, bind, run, held)
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - a relation as a goal held by the queue until one of its unknowns is
#       bound, which then runs again and decides or waits again:
#       harnesses/python/S/suspend.py, its docstring ("to wait for all of
#       several variables, wait on the next unbound one");
#       harnesses/python/qualification/programs/x01_extended.py
#     - a callable object with __call__ and __repr__: The Python Language
#       Reference (3.13), "Data model", "Emulating callable objects" and
#       "Basic customization"
#     - integer arithmetic, // and % on integers: The Python Language
#       Reference, "Binary arithmetic operations"
#
# P02c. One stage: R1, u + v = <k>; R2, w * u = v; R3, u + <k> = <k>, in
# that order. All unknowns are integers.
# Each relation, when it arrives, is a goal of the queue. When it runs, its
# evaluator (+ or *) decides it if two of its places have values, computing
# the third or testing it; otherwise it waits on its unbound unknowns, and is
# run again when one of them is bound.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
R1_SUM = 16
R3_ADDEND = 10
R3_SUM = 12
# CONSTANTS END

q = Queue()
u, v, w = Var("u"), Var("v"), Var("w")
unknowns = {"u": u, "v": v, "w": w}
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


def times(a, b, c):
    """The relation a * b = c over integers, as plus. Where the known
    factor is 0 and c = 0, the relation holds for every value of the other
    factor, which stays unknown (None)."""
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


cp.relations(plus=plus, times=times)


class Relation:
    """One relation of the problem, as a goal of the queue: its name, its
    evaluator, and its places (each a Var or an integer)."""

    def __init__(self, name, evaluate, places):
        self.name, self.evaluate, self.places = name, evaluate, places

    def __call__(self):
        values = [deref(p) for p in self.places]
        outcome = self.evaluate(*[None if isinstance(x, Var) else x for x in values])
        if outcome is None:
            q.wait(self, *[x for x in values if isinstance(x, Var)])
        elif outcome is False:
            failed.append(self)
        else:
            for p, x in zip(values, outcome):
                if isinstance(p, Var) and x is not None:
                    q.bind(p, x)

    def __repr__(self):
        return "%s%r" % (self.name, tuple(self.places))


while (s := cp.stage()) is not None:
    if s.k == 1:
        q.wait(Relation("R1", plus, (u, v, s.constants["R1_SUM"])))
        q.wait(Relation("R2", times, (w, u, v)))
        q.wait(Relation("R3", plus, (u, s.constants["R3_ADDEND"], s.constants["R3_SUM"])))
    q.run()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        else:
            told = ["%s = %d" % (n, deref(x)) for n, x in unknowns.items() if not isinstance(deref(x), Var)]
            if told:
                cp.answer(", ".join(told))
