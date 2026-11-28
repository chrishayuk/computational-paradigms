# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of stdlib-concurrency for P11c (one text, the
#   same file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls, cp.emit, s.commitment for a replayed commit
#       stage, a generator registered as pending: harnesses/python/README.md,
#       sections 3 and 8; its qualification program x02_pick.py (a commit
#       stage taken from s.commitment)
#     - a conjunction as a generator of its solutions, its conjuncts in
#       order, one answer taken with next(), and more asked for when a later
#       relation refutes the one held (chronological backtracking into the
#       generator): The Python Language Reference (3.13), "Yield
#       expressions"; PEP 255, "Simple Generators"; The Python Library
#       Reference, "Built-in Functions" (next, with a default); this
#       configuration's P04 programs
#     - commitment as giving up the alternatives not taken (the generator
#       dropped), as a cut does: Clocksin and Mellish, Programming in
#       Prolog, Springer, 1981, chapter 4 ("Backtracking and the Cut")
#
# P11c. Any-one queries. Stage 1: pick(x) and emit(x); stage 2: x != <k>;
# stage 3: commit.
# Stage 1's conjunction is a generator of its solutions: for each value pick
# gives x, in the facts' order, the effect, then the solution; one answer is
# taken. A relation on x added later is kept, and the solution held must
# satisfy every relation added: if it does not, the generator is asked for
# its next solution (which performs that solution's effect) until one does
# or none is left. A commit stage selects the solution held, v: x = v is
# added as a relation, and the generator is dropped, so that no alternative
# is tried after it. A replayed commit stage takes x = v from s.commitment.

# CONSTANTS BEGIN
# stage 1
PICK_FACTS = (1, 2, 3)
# stage 2
DIFFERENT_FROM = 1
# CONSTANTS END

known = {}          # the bindings of the solution held, while there is one
solutions = []      # stage 1's generator of solutions, until a commit drops it
added = []          # relations on x added after stage 1: (name, k)

cp.bindings(known)
cp.pending("the conjunction's untried alternatives", solutions)
cp.held("relations on x added after stage 1", added)

facts = []          # pick's closed world, as stage 1 gives it


def pick(x):
    """pick(x): yields each value of x for which it holds, x None while unknown."""
    for v in facts:
        if x is None or x == v:
            yield v


def different(v, k):
    """v != k."""
    return v != k


def equal(v, k):
    """v = k."""
    return v == k


cp.relations(pick=pick, different=different, equal=equal)


def holds(name, k, v):
    """Whether the relation (name, k) holds of the value v of x."""
    if name == "!=":
        return different(v, k)
    return equal(v, k)


def conjunction():
    """pick(x) and emit(x), in that order: yields each solution x."""
    for x in pick(None):
        cp.emit(x)
        yield x


def satisfies(v):
    """Whether v satisfies every relation added after stage 1."""
    return all(holds(name, k, v) for name, k in added)


def advance():
    """Keep the solution held if it satisfies every relation added;
    otherwise ask stage 1's generator for its next solution, until one does
    or none is left."""
    v = known.pop("x", None)
    while v is not None and not satisfies(v):
        v = next(solutions[0], None) if solutions else None
    if v is not None:
        known["x"] = v


def add(name, k):
    """A stage adds a relation on x."""
    added.append((name, k))
    advance()


def commit(commitment):
    """A commit stage: the solution held, v (or, in a replay, the v the
    stage first selected), is selected; x = v is added, and the
    alternatives not taken are given up."""
    if commitment is not None:
        chosen = [v for v in facts if "x = %s" % v == commitment]
        v = chosen[0] if chosen else None
    else:
        v = known.get("x")
    if v is not None:
        add("=", v)
    solutions.clear()


def report():
    if "x" in known:
        cp.answer("x = %s" % known["x"])
    else:
        print("no solution: no value of x satisfies the information so far")


while (s := cp.stage()) is not None:
    if s.k == 1:
        facts[:] = s.constants["PICK_FACTS"]
        solutions[:] = [conjunction()]              # pick(x) and emit(x)
        v = next(solutions[0], None)                # any one
        if v is not None:
            known["x"] = v
    elif s.k == 2:
        add("!=", s.constants["DIFFERENT_FROM"])    # x != <k>
    elif s.k == 3:
        commit(s.commitment)                        # commit
    if not s.replay:
        report()
