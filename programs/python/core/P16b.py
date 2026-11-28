# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core for P16b, written before any program was run
#   idioms:
#     - the stage loop, cp calls, s.params["n"]; computations registered
#       with cp.computation for the harness to spawn, the sizes they need
#       kept by main for them: harnesses/python/README.md, sections 3, 3.4
#       and 8, and its qualification program x03_two.py; this
#       configuration's P09a and P09b
#     - relations held until their values arrive, each with an evaluator
#       that computes any one place from the others or tests them: this
#       configuration's P02 and P07 programs (equal and plus, as there)
#     - each held relation indexed under the unknowns it waits for, and a
#       list of the unknowns newly given a value, so that a value takes up
#       only the relations it is a place of (propagation by need): Waltz,
#       "Understanding line drawings of scenes with shadows", in Winston
#       (ed.), The Psychology of Computer Vision, McGraw-Hill, 1975;
#       Mackworth, "Consistency in networks of relations", Artificial
#       Intelligence 8(1), 1977 (the queue of arcs to revise); in Python, a
#       dict of lists: The Python Library Reference (3.13), "Mapping Types
#       -- dict" (setdefault, pop with a default)
#     - integer arithmetic, // on integers: The Python Language Reference,
#       "Binary arithmetic operations"
#
# P16b. Four contributors, m = n/4. Stage 1: contributor c (c = 1 to 4),
# a separate computation (spawned by the harness: here one after another),
# contributes succ(x_i, x_(i+1)) for i = (c - 1)m + 1, ..., cm, ascending;
# stage 2: total = x_1 + x_(m+1) + x_(2m+1) + x_(3m+1) + x_(4m+1); stage 3:
# x_1 = <k>. Stages 2 and 3 are main's. The contributors share the one store
# of relations and bindings (the program's module: one database).
# All unknowns are integers. The sum of stage 2 is posed as its primitive
# relations, (((x_1 + x_(m+1)) + x_(2m+1)) + x_(3m+1)) + x_(4m+1) = total,
# with fresh unknowns t1, t2, t3 (SPECIFICATION.md, "Arithmetic and
# comparison"). Each relation, when it arrives, is examined by its
# evaluator: decided if its places allow, otherwise held, under each unknown
# it waits for. An unknown that gets a value takes up the held relations it
# is a place of, and those that are decided give values in turn, until no
# unknown is newly valued. The holding, the index and the list of new values
# are written for the problem's relations (R by METRICS.md, rule 19).

# CONSTANTS BEGIN
# stage 3
VALUE = 0
# CONSTANTS END

known = {}       # the bindings: unknown -> value
held = {}        # relations not yet decided, by number: (name, places)
watching = {}    # unknown -> numbers of the held relations it is a place of
failed = []      # relations found not to hold
news = []        # unknowns newly given a value, whose relations are not yet taken up
numbered = [0]   # the number of the last relation held
sizes = {}       # n and m, kept by main for the contributors once stage 1 is posed

cp.bindings(known)
cp.suspended("relations waiting for values", held)
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

EVALUATOR = {"succ": succ, "=": equal, "+": plus}


def place(p):
    """The value of a place: an unknown's value, None while it has none."""
    return known.get(p) if isinstance(p, str) else p


def examine(rel):
    """Evaluate one relation on what is known: True if it is decided (the
    unknowns it computes are given their values), False if it does not
    hold, None if it must wait."""
    name, places = rel
    outcome = EVALUATOR[name](*[place(p) for p in places])
    if outcome is None:
        return None
    if outcome is False:
        failed.append(rel)
        return False
    for p, x in zip(places, outcome):
        if isinstance(p, str) and x is not None and p not in known:
            known[p] = x
            news.append(p)
    return True


def propagate():
    """Take up, for each unknown newly given a value, the held relations it
    is a place of, until no unknown is newly valued."""
    while news:
        u = news.pop()
        for number in watching.pop(u, []):
            if number in held and examine(held[number]) is not None:
                del held[number]


def post(rel):
    """A relation arrives: decided if its places allow, otherwise held under
    each unknown it waits for; then what it decided is propagated."""
    if examine(rel) is None:
        numbered[0] += 1
        held[numbered[0]] = rel
        for p in rel[1]:
            if isinstance(p, str):
                watching.setdefault(p, []).append(numbered[0])
    propagate()


def x(i):
    """The name of the unknown x_i."""
    return "x_%d" % i


def report():
    unknowns = [x(i) for i in range(1, sizes["n"] + 2)] + ["total"]
    if failed:
        print("no solution: these relations do not hold:", failed)
    elif any(u in known for u in unknowns):
        cp.answer(", ".join("%s = %d" % (u, known[u]) for u in unknowns if u in known))


def contribute(c):
    """Contributor c's part: succ(x_i, x_(i+1)) for its segment, ascending."""
    m = sizes["m"]
    for i in range((c - 1) * m + 1, c * m + 1):
        post(("succ", (x(i), x(i + 1))))                        # succ(x_i, x_(i+1))
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
        post(("+", (x(1), x(m + 1), "t1")))
        post(("+", ("t1", x(2 * m + 1), "t2")))
        post(("+", ("t2", x(3 * m + 1), "t3")))
        post(("+", ("t3", x(4 * m + 1), "total")))
    elif st.k == 3:
        post(("=", (x(1), st.constants["VALUE"])))             # x_1 = <k>
    if st.k > 1 and not st.replay:
        report()
