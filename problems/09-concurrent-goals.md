# P09. Concurrent goals

**Probes:** whether a system can run computations that do not depend on
each other without one blocking the other, and whether computations can
work together through information they share. A system may support one and
not the other.

All computations run in one instance of the system (`PROTOCOL.md`). loop
is as in P04. rev and conc are as in P03.

## P09a. Independent computations

Two separate computations, each started with `spawn` (`PROTOCOL.md`) in the
same running system, not conjoined, sharing no unknowns:

- A: loop(x)
- B: rev(⟨1, 2, 3⟩, b)

Valid outcomes: none for A; b = ⟨3, 2, 1⟩ for B. Posed in both orders, A
then B and B then A. Each computation has its own budget.

## P09b. Isolation from failure

Two separate computations:

- A: x = 1 and x = 2
- B: y = 3

Valid outcomes: none for A; y = 3 for B.

## P09c. Communication through a shared unknown

gen(n, s): s = ⟨n, n+1, …, 5⟩. It is defined, in this order, by:

1. gen(n, ⟨⟩) if n > 5
2. gen(n, ⟨n⟩ ++ rest) if n ≤ 5 and gen(n + 1, rest)

sum3(s, total): total is the sum of the first three elements of s. It is
defined by:

1. sum3(⟨p, q, r⟩ ++ m, total) if p + q + r = total, for every sequence m

One computation: gen(1, s) and sum3(s, total), in that order. Valid
outcome: total = 6, s = ⟨1, 2, 3, 4, 5⟩.

## P09d. An unbounded producer

genu(n, s) is defined by one case:

1. genu(n, ⟨n⟩ ++ rest) if genu(n + 1, rest)

One computation: genu(1, s) and sum3(s, total), in that order. It is run
once and classified twice, under each of two readings:

- **P09d1, finite:** sequences are finite, and genu is read as the least
  relation. It has no instances, so the conjunction has no solution. Valid
  outcome: none. A system that reports total = 6 as a finished outcome is
  *unsound*. One that has bound total to 6 while the producer is still
  running, and reports nothing finished, is *none reported* with *budget*,
  and the binding is recorded as an observation.
- **P09d2, stream:** sequences may be infinite, and genu is read as the
  greatest relation, so s = ⟨1, 2, 3, …⟩. Valid outcome: total = 6, while
  the producer goes on. A system that computes total = 6 is *complete* for
  total, whether or not the producer ever stops. The producer's state is
  recorded separately: *budget*, *suspended*, or demand-driven and idle.

## P09e. Mutual waiting

One computation of two parts, each needing a value only the other can give:
x = y + 1 and y = x − 1. Valid outcomes: every integer pair with
x = y + 1.

## Observations

- P09a: whether B's outcome is reported while A runs, and whether the
  order in which they are posed matters. If the system can only run them
  one after another, record that.
- P09b: whether A's failure affects B.
- P09c and P09d: whether the consumer acts on s before the producer has
  finished, from a trace if the system gives one, and in what order the two
  parts take their steps.
- P09e: whether the system reports a residual, suspends, enumerates, or
  reports a deadlock, and whether that state can be told apart from
  completion.
