# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P06e3 (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, a generator registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - a closed world of facts as tuples; a relation as a generator of the
#       values that satisfy it, by its cases (here its facts) in order:
#       The Python Language Reference (3.13), "Yield expressions"; PEP 255,
#       "Simple Generators"; The Python Tutorial, "Tuples and Sequences"
#     - negation as Python's "not" on a decided test; "in" for membership of
#       a fact in the closed world: The Python Language Reference, "Boolean
#       operations", "Membership test operations"
#     - atoms as strings; None for a place that has no value: The Python
#       Library Reference, "Text Sequence Type -- str", "Built-in Constants"
#     - the closed world itself: Clark, "Negation as failure", in Gallaire
#       and Minker (eds.), Logic and Data Bases, Plenum, 1978, as the
#       problem file cites it
#
# P06e3. The query nonmajor(p), over the closed world of <facts>.
# student and maths are generators of the values that satisfy them (the
# place given as None while unknown); takes is a test, since the definition
# of nonmajor reaches it with both places known. nonmajor's conjuncts are in
# their order: student(p), then maths(k), then not takes(p, k). Every value
# of p found is reported, once for each way it holds.

# CONSTANTS BEGIN
# stage 1
STUDENT_FACTS = ("brown", "smith")
MATHS_FACTS = ("c101", "c301")
TAKES_FACTS = (("brown", "c101"), ("smith", "c101"), ("smith", "c301"))
# CONSTANTS END

known = {}
cp.bindings(known)

world = {"student": (), "maths": (), "takes": ()}   # the closed world, as stage 1 gives it
cp.held("the closed world", world)


def student(p):
    """student(p): yields each value of p for which it holds."""
    for fact in world["student"]:
        if p is None or p == fact:
            yield fact


def maths(k):
    """maths(k): yields each value of k for which it holds."""
    for fact in world["maths"]:
        if k is None or k == fact:
            yield fact


def takes(p, k):
    """takes(p, k), p and k known: whether it is one of the facts."""
    return (p, k) in world["takes"]


def nonmajor(p):
    """nonmajor(p): yields p once for each way the one case holds."""
    for p1 in student(p):                   # 1. nonmajor(p) if student(p)
        for k in maths(None):               #    and maths(k)
            if not takes(p1, k):            #    and not takes(p, k)
                yield p1


cp.relations(student=student, maths=maths, takes=takes, nonmajor=nonmajor)


while (s := cp.stage()) is not None:
    if s.k == 1:
        world["student"] = s.constants["STUDENT_FACTS"]
        world["maths"] = s.constants["MATHS_FACTS"]
        world["takes"] = s.constants["TAKES_FACTS"]
        answers = nonmajor(None)
        cp.pending("the query, not yet exhausted", answers)
        for p in answers:
            known["p"] = p
            if not s.replay:
                cp.answer("p = '%s" % p)
