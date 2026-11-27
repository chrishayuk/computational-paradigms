# P12. Large alternative space

*Added after review 1.*

**Probes:** what it costs, in steps and in retained alternatives, to search
one finite space by each system's own strategy, with solutions placed at
chosen depths and positions.

## Vocabulary

choice(n, s): s is a sequence over the atoms ʟ and ʀ, of length at most n.
It is defined, in this order, by:

1. choice(n, ⟨⟩)
2. choice(n, ⟨e⟩ ++ t) if n > 0 and (e = ʟ or e = ʀ, in that order) and
   choice(n − 1, t)

choice(n, s) has 2ⁿ⁺¹ − 1 solutions: 8,191 for n = 12. accept is given by
facts, in a closed world, and differs by sub-problem. Each sub-problem is
posed at n = 8, 12 and 16, with "12" below read as n, so that the growth of
retained alternatives can be compared across systems.

## Queries

Each is one stage: choice(n, s) and accept(s), in that order. Each is
posed twice: for **all** solutions (`answers(20)`), and for **any one**
(`answers(1)`).

**Limits.** As in P13: a budget of 10⁸ steps per stage and a safety limit
of 600 seconds, fixed and not raised. A strategy that examines every
candidate does about 2ⁿ⁺¹ of them, and needs these limits to reach
n = 16.

| | accept | all solutions | where they lie |
|---|---|---|---|
| P12a | ⟨ʀ⟩, and ʟ repeated 12 times | both | depth 1 on the right; depth 12 on the far left |
| P12b | ⟨ʀ⟩ only | ⟨ʀ⟩ | depth 1, right of the whole ʟ subtree |
| P12c | ʀ repeated 12 times only | that one | the last sequence in both depth-first and breadth-first order |
| P12d | ʟ repeated 12 times only | that one | depth 12 on the far left: early for depth-first, late for breadth-first |

For reference only, and not as valid outcomes, here are the positions of
the solutions among the candidates:

| | depth-first, in the order written | breadth-first |
|---|---|---|
| ⟨ʀ⟩ | 4,097th | 3rd |
| ʟ repeated 12 times | 13th | 4,096th |
| ʀ repeated 12 times | 8,191st | 8,191st |

For general n: ⟨ʀ⟩ is 2ⁿ + 1st depth-first and 3rd breadth-first; ʟ
repeated n times is n + 1st depth-first and 2ⁿth breadth-first; ʀ repeated
n times is last, 2ⁿ⁺¹ − 1st, in both. Depth-first holds about n
alternatives at a time, and breadth-first a frontier of up to 2ⁿ. So for
the first solution, breadth-first is earlier on P12a and P12b, depth-first
on P12d, and they tie on P12c. Depth-first holds less on all four.

**Candidates examined** is the number of sequences s for which accept(s)
is evaluated, counted by the program or the instrumentation. It is a
problem-defined quantity, comparable across systems (`METRICS.md`), as are
the partial sequences held.

## Rules

- The search strategy is the configuration's own. A search written by hand
  is supporting code.
- Placing accept before choice is a move, counted as reformulation.
- A system that avoids search altogether, for instance by holding choice
  until accept constrains s, is recorded as doing so. That is one of the
  results the problem exists to show.

## Observations

- Candidates examined before each solution.
- Peak retained alternatives and peak store, in the units of the systems
  file.
- The order in which solutions are reported.
- For "all": whether the system finishes after the last solution. The space
  is finite, so a strategy that covers it finishes, and *budget* means the
  strategy did not cover it.
- Steps are compared within a system, across its configurations (absys
  against absys-depth-first, for instance).
