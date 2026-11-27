# P13. Deterministic scale

*Added after review 1.*

**Probes:** how steps and store grow with the size of a computation that has
no unknowns and no alternatives, so that the bookkeeping cost of each model
can be seen apart from search and suspension.

The workload depends on the algorithm. Reversing a sequence by repeated
concatenation is quadratic, and with an accumulator it is linear. So each
task is posed twice:

- **prescribed:** with the definitions below, which every system
  transcribes. Differences are then the model's, not the algorithm's;
- **native:** by whatever means is the system's own idiom. The algorithm
  used is recorded, and it is not reformulation. The sequence ⟨1, …, n⟩
  must be built and held until the answer is given; a closed form, or an
  iteration that never builds it, does not answer P13e or P13f.

## Three sources of cost

The costs observed have three sources, which cannot always be separated:

- **algorithmic:** the work intrinsic to the algorithm, the same in every
  system for a prescribed task, and counted as problem operations
  (`METRICS.md`);
- **computational model:** work added by search, suspension, scheduling or
  retained alternatives, although the task has none of them;
- **implementation:** the interpreter, the run-time, the representation of
  data, and measurement.

The prescribed tasks hold the first fixed. Comparing their problem
operations with the system's own steps shows how much the second and third
add.

## Representation

In the prescribed tasks, a sequence must decompose as ⟨h⟩ ++ t in constant
time, as a pair of a head and a tail does. A representation in which
taking the tail copies the sequence (slicing an array, for instance) makes
linear definitions quadratic, and is not a transcription. The
representation used is recorded. A system with no dynamic structures
(ALGOL 60) uses arrays with an index for the tail, and records it.

Recursive definitions at n = 10⁵ exceed some systems' default recursion
depth. Raising the limit is a configuration flag, listed in the systems
file. Where it is not raised, the error is the result.

## Vocabulary

range(m, n, s): s = ⟨m, m+1, …, n⟩, or ⟨⟩ if m > n. It is defined, in this
order, by:

1. range(m, n, ⟨⟩) if m > n
2. range(m, n, ⟨m⟩ ++ t) if m ≤ n and range(m + 1, n, t)

sum(s, k): k is the sum of the elements of s. It is defined, in this order,
by:

1. sum(⟨⟩, 0)
2. sum(⟨h⟩ ++ t, k) if sum(t, j) and k = h + j

rev is as in P03, which is quadratic. revacc(a, b) is the linear one:

1. revacc(a, b) if racc(a, ⟨⟩, b)
2. racc(⟨⟩, b, b), for every sequence b
3. racc(⟨h⟩ ++ t, c, b) if racc(t, ⟨h⟩ ++ c, b)

## Queries

Each is one stage. n takes the values 10², 10³, 10⁴ and 10⁵.

| | query | valid outcome |
|---|---|---|
| P13a | range(1, n, s) | s = ⟨1, …, n⟩ |
| P13b | range(1, n, s) and sum(s, k) | s = ⟨1, …, n⟩, k = n(n+1)/2 |
| P13c | range(1, n, s) and rev(s, r) | s = ⟨1, …, n⟩, r = ⟨n, …, 1⟩ |
| P13d | range(1, n, s) and revacc(s, r) | s = ⟨1, …, n⟩, r = ⟨n, …, 1⟩ |
| P13e | native: build ⟨1, …, n⟩ and sum it | k = n(n+1)/2 |
| P13f | native: build ⟨1, …, n⟩ and reverse it | r = ⟨n, …, 1⟩ |

P13a is measured alone so that the cost of building the input can be taken
out of the others.

## Budget

This problem's budget is 10⁸ steps per stage and its safety limit 600
seconds. The other problems' limits would stop most systems at n = 10⁴ on
P13c, which is the expected result for a quadratic algorithm, not a
finding. These limits are fixed. They are not raised to let any system
finish: a quadratic algorithm is expected to stop scaling, and where it
stops is a result. A run stopped by either limit is recorded as such, and
the larger values of n are not run after it.

Steps, problem operations, process CPU time and maximum resident set size
are recorded for each n. The growth exponents of each are compared across
systems (`METRICS.md`).

## Observations

- Steps and peak store for each n, and how each grows with n, within the
  system. The growth is compared across systems; the counts are not.
- The algorithm used in P13e and P13f.
- Store retained after the answer: for instance suspended relations or
  bindings that are kept although the computation is determinate.
