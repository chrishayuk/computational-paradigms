# P09. Concurrent goals

**Probes:** whether a system can run computations that do not depend on
each other without one blocking the other, and whether computations can
work together through information they share. A system may support one
and not the other.

loop is as in P04. rev and conc are as in P03.

## P09a. Independent computations

Two separate computations, posed to the same running system. They are not
conjoined, and share no unknowns:

- A: loop(x)
- B: rev(⟨1, 2, 3⟩, b)

Valid outcomes: none for A; b = ⟨3, 2, 1⟩ for B. Posed in both orders, A
then B and B then A.

## P09b. Isolation from failure

Two separate computations:

- A: x = 1 and x = 2
- B: y = 3

Valid outcomes: none for A; y = 3 for B.

## P09c. Communication through a shared unknown

One computation, the conjunction of two parts sharing the unknown s:

- producer: s = ⟨1, 2, 3, 4, 5⟩, built one element at a time. gen(n, s)
  holds when s = ⟨n, n+1, …, 5⟩. It is defined, in this order, by
  1. gen(n, ⟨⟩) if n > 5
  2. gen(n, ⟨n⟩ ++ t) if n ≤ 5 and gen(n + 1, t)
- consumer: t is the sum of the first three elements of s.

Posed as gen(1, s) and sum3(s, t), in that order. Valid outcome: t = 6.

## P09d. An unbounded producer

As P09c, but with the producer unbounded: genu(n, s) is defined by

1. genu(n, ⟨n⟩ ++ t) if genu(n + 1, t)

Read as the least relation, genu has no finite instances, so the
conjunction has no solution among finite sequences. Record whether the
consumer nonetheless computes t = 6 from the part of s produced. A system
that does so and reports t = 6 as a finished outcome is classified
*unsound*, with the observation recorded. A system that reports it as a
value computed so far, with the producer still running, is recorded as
such.

## P09e. Mutual waiting

One computation of two parts, each waiting for a value only the other can
give: x = y + 1 and y = x − 1. Valid outcomes: every integer pair with
x = y + 1.

## Observations

- P09a: whether B's outcome is reported while A runs. Whether the order in
  which they are posed matters. If the system runs them one after another,
  record that.
- P09b: whether A's failure affects B.
- P09c and P09d: whether the consumer acts on s before the producer has
  finished, from a trace if the system gives one, and in what order the
  two parts take their steps.
- P09e: whether the system reports a residual, suspends, enumerates, or
  reports a deadlock, and whether the state can be told apart from
  completion.
