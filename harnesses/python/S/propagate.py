"""S mechanism: a constraint propagator over finite integer domains, with
exact linear relations.

Variables: any hashable key, for instance a name or a suspend.Var (which
owns the variables of the S mechanisms; this module defines none). Uses
search.py for labelling and its trail convention for undoing.

Store(trail=None) holds a domain (a set of integers) per variable and the
constraints posted on them:
  var(v, values)           -- declare v with domain `values` (any iterable);
  linear(terms, op, c)     -- post sum(a * v for a, v in terms) op c, with op
                              '==', '<=' or '>=' and integer a, c (exact: ints);
  relation(vars, pred)     -- post pred(*values) over vars, any arity;
  fix(v=None, keep=None)   -- optionally narrow v to the values satisfying keep,
                              then propagate to a fixpoint; False on failure;
  value(v)                 -- v's value if its domain is one value, else None;
  residual()               -- the constraints not yet decided: those with a
                              variable whose domain has more than one value;
  label(vars)              -- generator of solutions {v: value}, by search.
linear() and relation() propagate at once and return what fix() returns.

Propagation. A constraint is revised when posted and whenever a domain of
one of its variables shrinks; revisions are queued first in, first out, a
constraint at most once in the queue, until none is queued: the fixpoint.
A linear constraint removes each value outside the bounds the other terms
allow (bounds consistency, exact integer arithmetic). A relation keeps the
values that appear in some tuple of the current domains satisfying pred
(arc consistency; its cost is the product of its domains' sizes). A domain
that becomes empty is failure: fix() returns False, with the queue cleared
and the domains as they were at the failure (undo them with the trail).
At the fixpoint, residual() is what remains to decide; each constraint
prints as its relation (repr).

With a trail (a list), every narrowing and every post appends its undo, so
that search.undo restores the store; label() requires one. label(vars)
picks the first variable of vars with more than one value, tries its values
in increasing order (each by fix), and yields when every variable of vars
has one value.
"""
from .search import search


class Fail(Exception):
    pass


class Linear:
    def __init__(self, terms, op, c):
        self.terms, self.op, self.c = list(terms), op, c
        self.vars = [v for _, v in self.terms]

    def revise(self, s):
        if not all(s.dom[v] for v in self.vars):
            raise Fail(self)
        sign = -1 if self.op == ">=" else 1
        terms, c = [(sign * a, v) for a, v in self.terms], sign * self.c
        lo = [min(a * x for x in s.dom[v]) for a, v in terms]
        hi = [max(a * x for x in s.dom[v]) for a, v in terms]
        for i, (a, v) in enumerate(terms):
            top = c - (sum(lo) - lo[i])
            bot = c - (sum(hi) - hi[i]) if self.op == "==" else None
            s.narrow(v, lambda x: a * x <= top and (bot is None or a * x >= bot))

    def __repr__(self):
        return "%s %s %r" % (" + ".join("%r*%r" % t for t in self.terms), self.op, self.c)


class Relation:
    def __init__(self, vars, pred):
        self.vars, self.pred = list(vars), pred

    def revise(self, s):
        tuples = [()]
        for v in self.vars:
            tuples = [t + (x,) for t in tuples for x in s.dom[v]]
        ok = [t for t in tuples if self.pred(*t)]
        for i, v in enumerate(self.vars):
            s.narrow(v, {t[i] for t in ok}.__contains__)

    def __repr__(self):
        return "%s%r" % (getattr(self.pred, "__name__", "relation"), tuple(self.vars))


class Store:
    def __init__(self, trail=None):
        self.dom, self.watch, self.cons = {}, {}, []
        self.queue, self.queued, self.trail = [], set(), trail

    def var(self, v, values):
        self.dom[v] = set(values)
        self.watch.setdefault(v, [])

    def narrow(self, v, keep):
        old = self.dom[v]
        new = {x for x in old if keep(x)}
        if len(new) == len(old):
            return
        self.dom[v] = new
        if self.trail is not None:
            self.trail.append(lambda: self.dom.__setitem__(v, old))
        if not new:
            raise Fail(v)
        for c in self.watch[v]:
            if c not in self.queued:
                self.queued.add(c)
                self.queue.append(c)

    def fix(self, v=None, keep=None):
        try:
            if v is not None:
                self.narrow(v, keep)
            while self.queue:
                c = self.queue.pop(0)
                self.queued.discard(c)
                c.revise(self)
            return True
        except Fail:
            self.queue.clear()
            self.queued.clear()
            return False

    def post(self, c):
        self.cons.append(c)
        for v in c.vars:
            self.watch[v].append(c)
        if self.trail is not None:
            self.trail.append(lambda: [self.cons.pop()] + [self.watch[v].pop() for v in c.vars])
        self.queued.add(c)
        self.queue.append(c)
        return self.fix()

    def linear(self, terms, op, c):
        return self.post(Linear(terms, op, c))

    def relation(self, vars, pred):
        return self.post(Relation(vars, pred))

    def value(self, v):
        d = self.dom[v]
        return next(iter(d)) if len(d) == 1 else None

    def residual(self):
        return [c for c in self.cons if any(len(self.dom[v]) > 1 for v in c.vars)]

    def label(self, vars):
        def children(store):
            v = next(v for v in vars if len(self.dom[v]) != 1)
            for x in sorted(self.dom[v]):
                if self.fix(v, x.__eq__):
                    yield store

        def done(store):
            return all(len(self.dom[v]) == 1 for v in vars)

        assert self.trail is not None, "label() needs a Store with a trail"
        if self.fix():
            for _ in search(self, children, done, self.trail):
                yield {v: self.value(v) for v in vars}
