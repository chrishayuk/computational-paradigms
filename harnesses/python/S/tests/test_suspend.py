"""suspend.py on made-up goals."""
from S.suspend import Var, deref, Queue
from S.search import search, undo


def test_deref_and_bind():
    q = Queue()
    x, y = Var("x"), Var("y")
    assert deref(x) is x and repr(x) == "x"
    assert q.bind(x, y) and deref(x) is y
    assert q.bind(y, 3) and deref(x) == 3 and repr(x) == "3"
    assert q.bind(x, 3) and not q.bind(x, 4) and deref(y) == 3


def test_wake_in_suspension_order_fifo():
    q, log = Queue(), []
    a, b = Var("a"), Var("b")
    q.wait(lambda: log.append("g1"), a)
    q.wait(lambda: log.append("g2"), b)
    q.wait(lambda: log.append("g3"), a)
    assert q.run() == 0 and log == [] and len(q.held) == 3
    q.bind(a, 1)
    assert list(q.held) == [2]
    q.bind(b, 2)
    assert q.run() == 3 and log == ["g1", "g3", "g2"], log
    assert q.held == {} and q.ready == []


def test_ready_now_and_any_of_several():
    q, log = Queue(), []
    a, b = Var(), Var()
    q.bind(a, 0)
    q.wait(lambda: log.append("bound already"), a, b)
    q.wait(lambda: log.append("no vars"))
    q.wait(lambda: log.append("either"), Var(), b)
    q.run()
    q.bind(b, 1)
    q.run()
    assert log == ["bound already", "no vars", "either"], log   # woken once only


def test_woken_goals_go_behind_ready_ones():
    q, log = Queue(), []
    x = Var("x")
    q.wait(lambda: log.append("on x"), x)

    def first():
        log.append("first")
        q.bind(x, 1)           # wakes "on x" behind "second"
    q.wait(first)
    q.wait(lambda: log.append("second"))
    q.run()
    assert log == ["first", "second", "on x"], log


def test_aliasing_moves_waiters():
    q, log = Queue(), []
    x, y = Var("x"), Var("y")
    q.wait(lambda: log.append("x"), x)
    q.bind(x, y)
    q.run()
    assert log == []
    q.bind(y, "v")
    q.run()
    assert log == ["x"] and deref(x) == "v"


def test_dataflow_chain():
    # z = (a + b) * 2 by goals that wait for what they need
    q = Queue()
    a, b, s, z = Var("a"), Var("b"), Var("s"), Var("z")

    def add():
        if isinstance(deref(a), Var) or isinstance(deref(b), Var):
            q.wait(add, a if isinstance(deref(a), Var) else b)   # wait for the other
        else:
            q.bind(s, deref(a) + deref(b))
    q.wait(add, a, b)
    q.wait(lambda: q.bind(z, deref(s) * 2), s)
    q.bind(b, 4)
    q.run()
    assert isinstance(deref(z), Var) and len(q.held) == 2
    q.bind(a, 3)
    q.run()
    assert deref(s) == 7 and deref(z) == 14 and not q.held


def test_trail_with_search():
    # choose x in 1..3 by search; a goal waiting on x binds y = x * 10;
    # backtracking unbinds both and suspends the goal again
    q, trail = Queue(), []
    x, y = Var("x"), Var("y")
    q.wait(lambda: q.bind(y, deref(x) * 10, trail), x)

    def children(_):
        for v in (1, 2, 3):
            q.bind(x, v, trail)
            q.run()
            yield None
    sols = [(deref(x), deref(y)) for _ in search(None, children, lambda _: not isinstance(deref(x), Var), trail)]
    assert sols == [(1, 10), (2, 20), (3, 30)], sols
    assert isinstance(deref(x), Var) and isinstance(deref(y), Var) and len(q.held) == 1
    mark = len(trail)
    q.bind(x, y, trail)
    undo(trail, mark)
    assert deref(x) is x and x.waiting == [1] and y.waiting == []
