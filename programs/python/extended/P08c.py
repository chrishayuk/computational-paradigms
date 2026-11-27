# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-27
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P08c, written before any program was run
#   S mechanisms used: backtracking search (S/search.py): search, undo, the
#     trail; suspension queue (S/suspend.py): Var, deref, Queue.bind with a
#     trail. And two of the program's own, general over relations, so S
#     (METRICS.md, rules 12, 15 and 19), not listed in S-mechanisms.md, the
#     same text as in this configuration's P03 programs: "unify"
#     (unification of terms built from values, cons cells and Vars, no
#     occurs check) and "resolution" (children and done: a goal list reduced
#     by the cases of its first goal's relation, depth first).
#     The suspension queue also holds each application of a relation that
#     has no definition yet, waiting on a Var that is bound when the
#     relation's definition (or its first part) arrives.
#   idioms:
#     - the stage loop, cp calls, the search's stack registered as pending:
#       harnesses/python/README.md, sections 3 and 8
#     - a relation as a generator of its cases, each a head unified with the
#       goal's arguments and a body of goals; goals solved left to right,
#       cases tried in order, by chronological backtracking, bindings undone
#       through a trail: Robinson, "A machine-oriented logic based on the
#       resolution principle", JACM 12(1), 1965 (unification); the S
#       mechanisms' docstrings (harnesses/python/S/search.py, suspend.py)
#     - sequences as cons cells, <h> ++ t as the pair (h, t) and <> as ():
#       McCarthy, "Recursive functions of symbolic expressions and their
#       computation by machine, Part I", CACM 3(4), 1960; the same encoding
#       in systems/python/measurement.md, section 2
#     - a definition that arrives as def statements executed when its stage
#       is posed: The Python Language Reference (3.13), "Function
#       definitions"
#     - generators and yield: The Python Language Reference (3.13), "Yield
#       expressions"; PEP 255, "Simple Generators"
#
# P08c. Stage 1: the definition of conc; stage 2: rev(<seq>, b), with rev
# not yet defined; stage 3: rev, case 1 only: rev(<seq>, <seq>), a fact
# whose sequences are the stage's constants; stage 4: rev, case 2.
# The unknowns are Vars; an equation is a unification. A relation is the
# list of its cases that have arrived, each a generator that unifies the
# case's head with the goal's arguments and gives the case's body; the
# relation tries them in order. An application posed while its relation has
# no case is held in the queue, waiting on the Var that the arrival of the
# relation's definition binds; it is then solved by search, depth first, and
# its first solution kept (any choice points left stay registered). A
# relation applied inside a search tries only the cases it has.

from S.search import search, undo
from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 2
FORWARDS = (1, 2)
# stage 3
CASE1_FIRST = ()
CASE1_SECOND = ()
# CONSTANTS END

binder = Queue()    # used only for its bind, with the trail (unify)
trail = []      # undo entries of bindings (S/search.py's convention)
stack = []      # the search's pending choice points
NIL = ()

cp.pending("choice points of the search", stack)


q = Queue()         # holds applications waiting for a definition
cases = {"rev": [], "conc": []}                               # each relation's cases, as they arrive
defined = {"rev": Var("rev is defined"), "conc": Var("conc is defined")}
failed = []         # applications or equations found not to hold

cp.suspended("applications waiting for a definition", q.held)
cp.held("relations found not to hold", failed)


def unify(x, y):
    """Unify two terms, binding Vars through the trail. On failure, undo
    what it bound and return False."""
    mark = len(trail)
    pairs = [(x, y)]
    while pairs:
        a, b = pairs.pop()
        a, b = deref(a), deref(b)
        if a is b:
            continue
        if isinstance(a, Var) or isinstance(b, Var):
            binder.bind(a, b, trail)
        elif isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
            pairs.extend(zip(a, b))
        elif isinstance(a, tuple) or isinstance(b, tuple) or a != b:
            undo(trail, mark)
            return False
    return True


def children(goals):
    """Resolution: the goal lists that the cases of the first goal's
    relation reduce `goals` to, in the order of the cases."""
    (relation, args), rest = goals[0], goals[1:]
    for body in relation(*args):
        yield body + rest


def done(goals):
    """A goal list is solved when no goal is left."""
    return not goals


def rev(a, b):
    """The relation rev(a, b): the cases of its definition that have
    arrived, in order."""
    for case in cases["rev"]:
        yield from case(a, b)


def conc(a, b, c):
    """The relation conc(a, b, c): the cases of its definition that have
    arrived, in order."""
    for case in cases["conc"]:
        yield from case(a, b, c)


cp.relations(rev=rev, conc=conc)

NAME = {rev: "rev", conc: "conc"}


class Application:
    """An application of a relation, posed as information: solved by
    search once its relation has a definition, held until then."""

    def __init__(self, relation, args):
        self.relation, self.args = relation, args

    def __call__(self):
        name = NAME[self.relation]
        if not cases[name]:
            q.wait(self, defined[name])
            return
        if next(search(((self.relation, self.args),), children, done, trail, stack), None) is None:
            failed.append(self)

    def __repr__(self):
        return "%s(%s)" % (NAME[self.relation], ", ".join(show(t) for t in self.args))


def equation(s, t):
    """Pose s = t, as a unification; note it if it does not hold."""
    if not unify(s, t):
        failed.append("%s = %s" % (show(s), show(t)))


def cons(seq):
    """The encoding: a sequence given as a tuple, as cons cells ending in ()."""
    t = ()
    for e in reversed(seq):
        t = (cons(e) if isinstance(e, tuple) else e, t)
    return t


def show(t):
    """Output adapter: a term as the problem writes it, a sequence whose
    tail is an unknown as <...> ++ that unknown."""
    t = deref(t)
    if isinstance(t, Var):
        return t.name
    if isinstance(t, str):
        return "'" + t                    # an atom, with a leading quote
    if not isinstance(t, tuple):
        return str(t)
    items = []
    while isinstance(t, tuple) and len(t) == 2:
        items.append(show(t[0]))
        t = deref(t[1])
    shown = "⟨" + ",".join(items) + "⟩"
    if t == ():
        return shown
    return shown + " ++ " + show(t)


b = Var("b")
unknowns = {"b": b}
cp.bindings(unknowns)


def report():
    if failed:
        print("no solution: these do not hold:", failed)
        return
    told = ["%s = %s" % (n, show(v)) for n, v in unknowns.items() if deref(v) is not v]
    if told:
        cp.answer(", ".join(told))


while (s := cp.stage()) is not None:
    if s.k == 1:
        def conc_1(a, b, c):
            if unify((a, b), (NIL, c)):                         # 1. conc(<>, b, b)
                yield ()

        def conc_2(a, b, c):
            h, a1, c1 = Var("h"), Var("a1"), Var("c1")
            if unify((a, c), ((h, a1), (h, c1))):               # 2. conc(<h> ++ a, b, <h> ++ c)
                yield ((conc, (a1, b, c1)),)                    #    if conc(a, b, c)

        cases["conc"].extend([conc_1, conc_2])
        q.bind(defined["conc"], True)
    elif s.k == 2:
        q.wait(Application(rev, (cons(s.constants["FORWARDS"]), b)))
    elif s.k == 3:
        fact = (cons(s.constants["CASE1_FIRST"]), cons(s.constants["CASE1_SECOND"]))

        def rev_1(a, b):
            if unify((a, b), fact):                             # 1. rev(<>, <>)
                yield ()

        cases["rev"].append(rev_1)
        q.bind(defined["rev"], True)
    elif s.k == 4:
        def rev_2(a, b):
            h, l, q2 = Var("h"), Var("l"), Var("q")
            if unify(a, (h, l)):                                # 2. rev(<h> ++ l, r)
                yield ((rev, (l, q2)), (conc, (q2, (h, NIL), b)))   #    if rev(l, q) and conc(q, <h>, r)

        cases["rev"].append(rev_2)
        q.bind(defined["rev"], True)
    q.run()
    if not s.replay:
        report()
