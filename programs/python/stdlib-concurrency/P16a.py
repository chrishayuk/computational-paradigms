# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P16a (one text,
#   the same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, s.params["n"] and s.params["order"]:
#       harnesses/python/README.md, sections 3 and 8
#     - relations held until their values arrive, each with an evaluator
#       that computes any one place from the others or tests them: this
#       configuration's P02 and P07 programs (equal, as there)
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
# P16a. Stage 1: succ(x_i, x_(i+1)) for i = 1, ..., n - 1, in the instance's
# arrival order (s.params["order"]); stage 2: x_j = <k>, j = ceil(n/2).
# All unknowns are integers. Each relation, when it arrives, is examined by
# its evaluator: decided if its places allow, otherwise held, under each
# unknown it waits for. An unknown that gets a value takes up the held
# relations it is a place of, and those that are decided give values in
# turn, until no unknown is newly valued. The holding, the index and the
# list of new values are written for the problem's relations (R by
# METRICS.md, rule 19).

# CONSTANTS BEGIN
# stage 2
VALUE = 0
# CONSTANTS END

known = {}       # the bindings: unknown -> value
held = {}        # relations not yet decided, by number: (name, places)
watching = {}    # unknown -> numbers of the held relations it is a place of
failed = []      # relations found not to hold
news = []        # unknowns newly given a value, whose relations are not yet taken up
numbered = [0]   # the number of the last relation held

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


cp.relations(succ=succ, equal=equal)

EVALUATOR = {"succ": succ, "=": equal}


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


def arrival(order, n):
    """The i of the relations succ(x_i, x_(i+1)), i = 1, ..., n - 1, in the
    arrival order the problem fixes."""
    if order == "ascending":
        return list(range(1, n))
    if order == "descending":
        return list(range(n - 1, 0, -1))
    if order == "interleaved":
        return list(range(1, n, 2)) + list(range(2, n, 2))


def report(unknowns):
    if failed:
        print("no solution: these relations do not hold:", failed)
    elif any(u in known for u in unknowns):
        cp.answer(", ".join("%s = %d" % (u, known[u]) for u in unknowns if u in known))


while (st := cp.stage()) is not None:
    n = st.params["n"]
    unknowns = [x(i) for i in range(1, n + 1)]
    if st.k == 1:
        for i in arrival(st.params["order"][0], n):
            post(("succ", (x(i), x(i + 1))))                    # succ(x_i, x_(i+1))
    elif st.k == 2:
        post(("=", (x((n + 1) // 2), st.constants["VALUE"])))  # x_j = <k>, j = ceil(n/2)
    if not st.replay:
        report(unknowns)
