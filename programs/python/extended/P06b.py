# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P06b, written before any program was run
#   S mechanisms used: suspension queue (S/suspend.py): Var, deref,
#     Queue.wait, bind, run, held
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - a relation as a goal of the suspension queue, which waits on its
#       unbound unknowns and is run again when one is bound: the S
#       mechanism's docstring (harnesses/python/S/suspend.py) and the
#       qualification program x01_extended.py; the same goals as this
#       configuration's P02 programs
#     - negation decided only once its unknowns have values: Naish,
#       Negation and Control in Prolog, LNCS 238, Springer, 1986; negation
#       as Python's "not" on a decided relation: The Python Language
#       Reference (3.13), "Boolean operations"
#     - a callable object: The Python Language Reference, "Data model"
#       ("Emulating callable objects", "Basic customization")
#
# P06b. Stage 1: x = <k>; stage 2: not (x = <k>).
# x is a Var. Each relation is a goal of the queue: when it is run it
# evaluates (=, or not =) and decides, or waits on its unbound unknowns.
# x = k gives x its value; not (x = k) holds exactly when x = k does not,
# so it is decided only once x has a value.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
EQUAL_TO = 2
# stage 2
NOT_EQUAL_TO = 1
# CONSTANTS END

q = Queue()
x = Var("x")
unknowns = {"x": x}
failed = []     # relations found not to hold

cp.bindings(unknowns)
cp.suspended("goals waiting for a binding", q.held)
cp.held("relations found not to hold", failed)


def equal(a, b):
    """The relation a = b. Each place is a value, or None if unknown.
    Returns both places with every one that can be computed, False if the
    relation does not hold, or None if it must wait."""
    if a is not None and b is not None:
        return (a, b) if a == b else False
    if a is not None:
        return a, a
    if b is not None:
        return b, b
    return None


def not_equal(a, b):
    """The relation not (a = b): it holds exactly when a = b does not hold.
    Decided only when both places have values; None (wait) otherwise."""
    if a is not None and b is not None:
        return (a, b) if not equal(a, b) else False
    return None


cp.relations(equal=equal, not_equal=not_equal)


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
        q.wait(Relation("=", equal, (x, s.constants["EQUAL_TO"])))
    elif s.k == 2:
        q.wait(Relation("not =", not_equal, (x, s.constants["NOT_EQUAL_TO"])))
    q.run()
    if not s.replay:
        if failed:
            print("no solution: these relations do not hold:", failed)
        else:
            told = ["%s = %s" % (n, deref(v)) for n, v in unknowns.items() if not isinstance(deref(v), Var)]
            if told:
                cp.answer(", ".join(told))
