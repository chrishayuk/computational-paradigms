# CP-POSING: reposed
#
# PROVENANCE
#   author: harness-python (an agent), as the README's example; not a study program
#   seen a precursor (absys E01-E09): no
#   idioms: the Python Language Reference (assignment expressions, dict, list)
#
# Made-up problem X01a: s = a + b is stated at stage 1, a arrives at stage 2,
# b at stage 3; the query at each stage is the values of s.

# CONSTANTS BEGIN
# stage 2
A_VALUE = 3
# stage 3
B_VALUE = 4
# CONSTANTS END

known = {}       # the bindings the program holds: unknown name -> value
waiting = []     # relations held until their values arrive

cp.bindings(known)
cp.suspended("waiting relations", waiting)


def plus(x, y):  # the relation s = a + b, evaluated when a and b are known
    return x + y


cp.relations(plus=plus)


def decide():
    for rel in list(waiting):
        if rel == "s = a + b" and "a" in known and "b" in known:
            known["s"] = plus(known["a"], known["b"])
            waiting.remove(rel)


while (s := cp.stage()) is not None:
    if s.k == 1:
        waiting.append("s = a + b")
    elif s.k == 2:
        known["a"] = s.constants["A_VALUE"]
    elif s.k == 3:
        known["b"] = s.constants["B_VALUE"]
    decide()
    if not s.replay and "s" in known:
        cp.answer("s = %d" % known["s"])
