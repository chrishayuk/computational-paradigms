"""S mechanism: logic variables and a suspension queue.

Owns: Var, deref() (the variables of the S mechanisms; propagate.py accepts
them as its variables, search.py has none). Uses search.py's trail
convention (a list of undo callables) when a trail is given.

A Var is unbound until it is bound once. Binding a Var to another unbound Var
makes them one variable; binding to anything else gives it that value.
deref(t) follows bindings to an unbound Var or a value. Values are compared
with ==; terms are not unified inside (a value that contains Vars is just a
value).

Queue holds goals (zero-argument callables) waiting on unknowns:
  wait(goal, *vars) -- goal is held until any one of vars is bound to a value
                       (if one already is, or none is given, it is ready now);
                       a goal waiting on several vars is woken once;
  bind(v, x, trail) -- bind v to x and wake the goals waiting on v; True if
                       consistent, False if both are values and differ
                       (nothing is changed then);
  run()             -- run ready goals until none is ready; returns how many ran.
Order (fairness): ready goals run first in, first out. A binding appends the
goals it wakes at the back of the ready queue, in the order they suspended.
So a goal, once woken, runs after every goal ready before it and before every
goal woken after it: none waits for ever while each goal returns. A goal may
wait again (to wait for all of several variables, wait on the next unbound
one) and may bind, which wakes others behind it. Binding two unbound Vars
together wakes nothing: the goals of the first wait on the merged variable.

`held` (key -> goal; keys increase in suspension order) is the suspended goals, `ready` the
goals woken and not yet run; a caller may register either. With a trail, a
binding is undone by search.undo: the variable is unbound again and the goals
it woke are held again. Undo only with the ready queue empty (call run()
first): a goal that has run is not un-run, though its trailed bindings are
undone.
"""


class Var:
    __slots__ = ("ref", "waiting", "name")

    def __init__(self, name="_"):
        self.ref = self     # itself while unbound
        self.waiting = []   # keys of goals in Queue.held
        self.name = name

    def __repr__(self):
        t = deref(self)
        return t.name if isinstance(t, Var) else repr(t)


def deref(t):
    while isinstance(t, Var) and t.ref is not t:
        t = t.ref
    return t


class Queue:
    def __init__(self):
        self.held = {}
        self.ready = []
        self.key = 0

    def wait(self, goal, *vars):
        vs = [deref(v) for v in vars]
        if not vs or not all(isinstance(v, Var) for v in vs):
            self.ready.append(goal)
            return
        self.key += 1
        self.held[self.key] = goal
        for v in vs:
            v.waiting.append(self.key)

    def bind(self, v, x, trail=None):
        a, b = deref(v), deref(x)
        if a is b:
            return True
        if not isinstance(a, Var):
            a, b = b, a
        if not isinstance(a, Var):
            return a == b
        a.ref = b
        if isinstance(b, Var):
            n = len(b.waiting)
            b.waiting += a.waiting

            def back():
                a.ref = a
                del b.waiting[n:]
        else:
            woken = [(k, self.held.pop(k)) for k in a.waiting if k in self.held]
            self.ready += [g for _, g in woken]

            def back():
                a.ref = a
                self.held.update(woken)
        if trail is not None:
            trail.append(back)
        return True

    def run(self):
        n = 0
        try:
            while n < len(self.ready):
                n += 1
                self.ready[n - 1]()
        finally:
            del self.ready[:n]
        return n
