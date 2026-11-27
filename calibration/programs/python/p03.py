# P03. Reversible relations. Python 3.12, configuration core (no imports).
# From problems/03-reversible-relations.md (conc from
# problems/01-unknown-equality.md). Sequences are Python lists.
#
# A Python function computes in one direction. conc and rev are transcribed
# by cases in the direction of P03a and P03e. Each other direction is a
# separate function, written by the same cases read in that direction,
# returning the list of every solution (README.md: reformulations).


def conc(a, b):
    """P03a: c with conc(a, b, c), a and b given."""
    if not a:
        return b
    return [a[0]] + conc(a[1:], b)


def conc_split(c):
    """P03b: every (a, b) with conc(a, b, c), c given. Reformulation."""
    solutions = [([], c)]
    if c:
        for a, b in conc_split(c[1:]):
            solutions.append(([c[0]] + a, b))
    return solutions


def conc_suffix(a, c):
    """P03c: every b with conc(a, b, c), a and c given. Reformulation."""
    if not a:
        return [c]
    if c and c[0] == a[0]:
        return conc_suffix(a[1:], c[1:])
    return []


def conc_prefix(b, c):
    """P03d: every a with conc(a, b, c), b and c given. Reformulation."""
    solutions = []
    if b == c:
        solutions.append([])
    if c:
        for a in conc_prefix(b, c[1:]):
            solutions.append([c[0]] + a)
    return solutions


def rev(a):
    """P03e: b with rev(a, b), a given."""
    if not a:
        return []
    return conc(rev(a[1:]), [a[0]])


def rev_inverse(r):
    """P03f: every a with rev(a, r), r given. Reformulation: case 2 read
    backwards, with conc(q, <h>, r) taken before rev(l, q)."""
    solutions = []
    if not r:
        solutions.append([])
    for q, last in conc_split(r):
        if len(last) == 1:
            for l in rev_inverse(q):
                solutions.append([last[0]] + l)
    return solutions


print("p03a", conc([1, 2], [3]))
print("p03b", conc_split([1, 2]))
print("p03c", conc_suffix([1], [1, 2, 3]))
print("p03d", conc_prefix([3], [1, 2, 3]))
print("p03e", rev([1, 2, 3]))
print("p03f", rev_inverse([1, 2, 3]))
