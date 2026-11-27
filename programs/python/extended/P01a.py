# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P01a, written before any program was run
#   S mechanism used: suspension queue (S/suspend.py): Var, deref, Queue.bind
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - unknowns as logic variables, an equation between unknowns as a
#       binding of one to the other, a value as a binding to it:
#       harnesses/python/S/suspend.py, its docstring ("Binding a Var to
#       another unbound Var makes them one variable")
#
# P01a. Stage 1: x = y; stage 2: y = z; stage 3: z = <k>.
# Each equation is told to the variables as a binding: x = y makes x and y one
# variable; z = <k> gives that variable its value, which every unknown
# identified with it then has.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 3
Z_VALUE = 2
# CONSTANTS END

q = Queue()
x, y, z = Var("x"), Var("y"), Var("z")
unknowns = {"x": x, "y": y, "z": z}
failed = []     # equations found not to hold

cp.bindings(unknowns)
cp.held("equations found not to hold", failed)


def show(t):
    """Output adapter: a term as the problem writes it."""
    t = deref(t)
    if isinstance(t, Var):
        return t.name
    if isinstance(t, tuple):
        return "⟨" + ",".join(show(e) for e in t) + "⟩"
    return str(t)


while (s := cp.stage()) is not None:
    if s.k == 1:
        if not q.bind(x, y):
            failed.append("x = y")
    elif s.k == 2:
        if not q.bind(y, z):
            failed.append("y = z")
    elif s.k == 3:
        if not q.bind(z, s.constants["Z_VALUE"]):
            failed.append("z = %s" % show(s.constants["Z_VALUE"]))
    if not s.replay:
        if failed:
            print("no solution: these equations do not hold:", failed)
        else:
            told = ["%s = %s" % (n, show(v)) for n, v in unknowns.items() if deref(v) is not v]
            if told:
                cp.answer(", ".join(told))
