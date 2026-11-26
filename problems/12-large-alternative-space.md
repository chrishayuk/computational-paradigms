# P12. Large alternative space

*Proposed in review of draft 0.1. Whether it is kept is decided before the
freeze.*

**Probes:** what it costs, in steps and in retained alternatives, to search
one finite space by each system's own strategy, with solutions placed at
chosen depths and positions.

## Vocabulary

choice(n, s): s is a sequence over the atoms ʟ and ʀ, of length at most n.
It is defined, in this order, by:

1. choice(n, ⟨⟩)
2. choice(n, ⟨e⟩ ++ t) if n > 0 and (e = ʟ or e = ʀ, in that order) and
   choice(n − 1, t)

choice(12, s) has 2¹³ − 1 = 8,191 solutions. accept is given by facts, in
a closed world, and differs by sub-problem.

## Queries

Each is one stage: choice(12, s) and accept(s), in that order. Each is
posed twice: for **all** solutions, and for **any one**.

| | accept | all solutions | where they lie |
|---|---|---|---|
| P12a | ⟨ʀ⟩, and ʟ repeated 12 times | both | depth 1 on the right; depth 12 on the far left |
| P12b | ⟨ʀ⟩ only | ⟨ʀ⟩ | depth 1, right of the whole ʟ subtree |
| P12c | ʀ repeated 12 times only | that one | the last sequence in both depth-first and breadth-first order |

For reference only, and not as valid outcomes, here are the positions of
the solutions among the candidates:

| | depth-first, in the order written | breadth-first |
|---|---|---|
| ⟨ʀ⟩ | 4,097th | 3rd |
| ʟ repeated 12 times | 13th | 4,096th |
| ʀ repeated 12 times | 8,191st | 8,191st |

Depth-first holds about 12 alternatives at a time. Breadth-first holds a
frontier of up to 4,096.

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
