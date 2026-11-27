# P13. Deterministic scale, n = 100. Python 3.12, configuration core.
# From problems/13-deterministic-scale.md.
#
# Prescribed tasks (P13a-P13d): a sequence is a chain of pairs, None for
# <> and (h, t) for <h> ++ t, so that the head and the tail are taken in
# constant time. (A Python list would copy on slicing, which the problem
# rules out.) Each function is recursive, one branch per case. The default
# recursion limit (1000) suffices at n = 100; at n >= 10^3 the recursion of
# range, sum, rev and racc exceeds it, and sys.setrecursionlimit would be a
# configuration flag.
#
# Native tasks (P13e, P13f): a Python list, built by list(range(...)),
# summed by the built-in sum, reversed by slicing.

N = 100


def seq_range(m, n):
    """s with range(m, n, s)."""
    if m > n:
        return None
    return (m, seq_range(m + 1, n))


def seq_sum(s):
    """k with sum(s, k)."""
    if s is None:
        return 0
    h, t = s
    j = seq_sum(t)
    return h + j


def conc(a, b):
    """c with conc(a, b, c)."""
    if a is None:
        return b
    h, t = a
    return (h, conc(t, b))


def rev(a):
    """b with rev(a, b): quadratic, through conc."""
    if a is None:
        return None
    h, l = a
    q = rev(l)
    return conc(q, (h, None))


def revacc(a):
    """b with revacc(a, b)."""
    return racc(a, None)


def racc(a, c):
    """b with racc(a, c, b)."""
    if a is None:
        return c
    h, t = a
    return racc(t, (h, c))


def as_list(s):
    """Harness (H): the chain of pairs written out as a list, to print it."""
    out = []
    while s is not None:
        h, s = s
        out.append(h)
    return out


s = seq_range(1, N)
print("p13a", as_list(s))

s = seq_range(1, N)
k = seq_sum(s)
print("p13b", k)

s = seq_range(1, N)
r = rev(s)
print("p13c", as_list(r))

s = seq_range(1, N)
r = revacc(s)
print("p13d", as_list(r))

s = list(range(1, N + 1))
k = sum(s)
print("p13e", k)

s = list(range(1, N + 1))
r = s[::-1]
print("p13f", r)
