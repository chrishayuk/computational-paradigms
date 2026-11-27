"""propagate.py on made-up constraints."""
from S.propagate import Store
from S.suspend import Var
from S.search import undo


def test_linear_to_fixpoint():
    s = Store()
    s.var("x", range(11))
    s.var("y", range(11))
    assert s.linear([(1, "x"), (1, "y")], "==", 10)
    assert s.linear([(1, "x"), (-1, "y")], "==", 2)
    # bounds alone do not decide it; the residual says what is left
    assert s.value("x") is None and len(s.residual()) == 2
    assert s.dom["x"] == set(range(2, 11)) and s.dom["y"] == set(range(0, 9))
    assert s.fix("y", lambda v: v >= 4)            # one more fact decides it
    assert (s.value("x"), s.value("y")) == (6, 4) and s.residual() == []


def test_exact_coefficients_and_inequalities():
    trail = []
    s = Store(trail)
    s.var("a", range(-50, 51))
    s.var("b", range(-50, 51))
    assert s.linear([(3, "a"), (5, "b")], "==", 1)   # 3a + 5b = 1
    assert s.linear([(1, "a")], ">=", 40)
    assert s.linear([(1, "b")], "<=", -22)
    # bounds consistency: integer bounds, not divisibility
    assert s.dom["a"] == set(range(42, 48)) and s.dom["b"] == set(range(-28, -24)), (s.dom["a"], s.dom["b"])
    mark = len(trail)
    assert not s.fix("b", lambda v: v == -26)         # 3a = 131: no integer a, no rounding
    undo(trail, mark)
    assert s.fix("b", lambda v: v == -25) and s.value("a") == 42   # 3a = 126
    assert repr(s.cons[0]) == "3*'a' + 5*'b' == 1"


def test_failure_on_empty_domain():
    s = Store()
    s.var("x", (1, 2, 3))
    s.var("y", (1, 2, 3))
    assert s.linear([(1, "x"), (1, "y")], ">=", 5)
    assert s.dom["x"] == {2, 3}
    assert not s.linear([(1, "x"), (1, "y")], "<=", 3)
    assert s.queue == [] and not s.queued


def test_relation_arc_consistency_and_residual():
    s = Store()
    for v in "pqr":
        s.var(v, (1, 2, 3))

    def less(a, b):
        return a < b
    assert s.relation("pq", less) and s.relation("qr", less)
    assert s.dom == {"p": {1}, "q": {2}, "r": {3}} and s.residual() == []
    t = Store()
    t.var("u", range(5))
    t.var("w", range(5))
    assert t.relation(["u", "w"], lambda a, b: a * b == 4)
    assert t.dom["u"] == {1, 2, 4} and [repr(c) for c in t.residual()] == ["<lambda>('u', 'w')"]


def test_label_with_trail():
    trail = []
    s = Store(trail)
    xs = ["x1", "x2", "x3"]
    for v in xs:
        s.var(v, range(1, 4))
    for i in range(3):
        for j in range(i + 1, 3):
            s.relation([xs[i], xs[j]], lambda a, b: a != b)
    s.linear([(1, "x1"), (2, "x2")], "<=", 6)
    sols = list(s.label(xs))
    want = [p for p in ([1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]) if p[0] + 2 * p[1] <= 6]
    assert [[d[v] for v in xs] for d in sols] == want, sols
    # exhausted: the domains are those before labelling
    assert [s.dom[v] for v in xs] == [{1, 2, 3}, {1, 2}, {1, 2, 3}], [s.dom[v] for v in xs]


def test_take_one_solution_then_post_under_trail():
    trail = []
    s = Store(trail)
    for v in "ab":
        s.var(v, range(10))
    s.linear([(1, "a"), (1, "b")], "==", 9)
    first = next(s.label(["a", "b"]))
    assert first == {"a": 0, "b": 9}
    undo(trail, 0)
    assert s.dom["a"] == set(range(10)) and s.cons == []   # the post was undone too


def test_suspend_vars_as_variables():
    x, y = Var("x"), Var("y")
    s = Store()
    s.var(x, range(4))
    s.var(y, range(4))
    s.linear([(2, x), (1, y)], "==", 7)
    assert s.dom[x] == {2, 3} and s.dom[y] == {1, 2, 3}
    assert repr(s.residual()[0]) == "2*x + 1*y == 7"
