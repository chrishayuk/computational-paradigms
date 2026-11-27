"""search.py on made-up trees."""
from S.search import search, undo


def strings(n):
    """Bit strings of length n with no two adjacent 1s, as tuples."""
    return search((), lambda s: (s + (b,) for b in (0, 1) if not (b and s and s[-1])),
                  lambda s: len(s) == n)


def test_order_and_count():
    got = list(strings(4))
    assert len(got) == 8, got                      # Fibonacci: 8 strings of length 4
    assert got == sorted(got), got                 # depth first, leftmost first
    assert got[0] == (0, 0, 0, 0) and got[-1] == (1, 0, 1, 0)


def test_take_one_is_lazy():
    seen = []

    def children(s):
        seen.append(s)
        return (s + (b,) for b in (0, 1))
    first = next(search((), children, lambda s: len(s) == 30))
    assert first == (0,) * 30 and len(seen) == 30  # only the leftmost path was expanded


def test_root_and_empty():
    assert list(search(5, lambda n: [], lambda n: n == 5)) == [5]
    assert list(search(5, lambda n: [], lambda n: False)) == []


def test_deep_beyond_recursion_limit():
    n = 20000
    assert list(search(0, lambda k: (k + 1,), lambda k: k == n)) == [n]


def test_trail_restores_state():
    # state is shared and mutable; each child is made by changing it, with undo trailed
    state, trail = [], []

    def children(_):
        for b in "ab":
            state.append(b)
            trail.append(state.pop)
            yield None

    sols = [''.join(state) for _ in search(None, children, lambda _: len(state) == 3, trail)]
    assert sols == ["aaa", "aab", "aba", "abb", "baa", "bab", "bba", "bbb"], sols
    assert state == [] and trail == []             # exhausted: back to the start


def test_stop_early_then_undo():
    state, trail = [], []

    def children(_):
        for b in "xy":
            state.append(b)
            trail.append(state.pop)
            yield None
    stack = []
    it = search(None, children, lambda _: len(state) == 2, trail, stack)
    next(it)
    assert state == ["x", "x"] and len(stack) == 3  # root, and two open choice points
    undo(trail, 0)
    assert state == []


def test_pruning_by_children():
    # subsets of {1..6} summing to 7: children skip what would exceed it
    items = (1, 2, 3, 4, 5, 6)

    def children(node):
        i, chosen, total = node
        if i < len(items):
            if total + items[i] <= 7:
                yield (i + 1, chosen + (items[i],), total + items[i])
            yield (i + 1, chosen, total)
    sols = [c for _, c, t in search((0, (), 0), children, lambda n: n[2] == 7)]
    assert sols == [(1, 2, 4), (1, 6), (2, 5), (3, 4)], sols
