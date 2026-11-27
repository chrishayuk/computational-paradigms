# CP-POSING: incremental
#
# PROVENANCE
#   author: s-python-extended (an agent), as the qualification of extended's S import; not a study program
#   seen a precursor (absys E01-E09): no
#   idioms: the Python Language Reference; harnesses/python/S/suspend.py
#
# Made-up problem X01a, as x01_total.py, with the relation held by the S
# mechanism suspend.py (a goal waiting on a and b) instead of by hand.

# CONSTANTS BEGIN
# stage 2
A_VALUE = 3
# stage 3
B_VALUE = 4
# CONSTANTS END

from S.suspend import Var, Queue, deref

q = Queue()
a, b, s_ = Var("a"), Var("b"), Var("s")
cp.bindings({"a": a, "b": b, "s": s_})
cp.suspended("waiting goals", q.held)


def plus(x, y):  # the relation s = a + b, evaluated when a and b are known
    return x + y


cp.relations(plus=plus)


def sum_goal():
    x, y = deref(a), deref(b)
    if isinstance(x, Var) or isinstance(y, Var):
        q.wait(sum_goal, x if isinstance(x, Var) else y)
    else:
        q.bind(s_, plus(x, y))


while (s := cp.stage()) is not None:
    if s.k == 1:
        q.wait(sum_goal, a, b)
    elif s.k == 2:
        q.bind(a, s.constants["A_VALUE"])
    elif s.k == 3:
        q.bind(b, s.constants["B_VALUE"])
    q.run()
    if not s.replay and not isinstance(deref(s_), Var):
        cp.answer("s = %d" % deref(s_))
