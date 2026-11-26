# P15. Merge and committed choice

**Probes:** how a system arbitrates between computations: interleaving two
sources, fairness to an unbounded one, and granting a single resource.

## P15a. Merge

merge(a, b, m): m is an interleaving of a and b that keeps the order of
each. It is defined, in this order, by:

1. merge(⟨⟩, b, b), for every sequence b
2. merge(⟨h⟩ ++ a, ⟨⟩, ⟨h⟩ ++ a), for every sequence a
3. merge(⟨h⟩ ++ a, b, ⟨h⟩ ++ m) if merge(a, b, m), b not empty
4. merge(a, ⟨h⟩ ++ b, ⟨h⟩ ++ m) if merge(a, b, m), a not empty

| | query | valid outcomes |
|---|---|---|
| P15a1 | merge(⟨1,2⟩, ⟨3,4⟩, m), any one | any of the six interleavings |
| P15a2 | merge(⟨1,2⟩, ⟨3,4⟩, m), all | all six: ⟨1,2,3,4⟩, ⟨1,3,2,4⟩, ⟨1,3,4,2⟩, ⟨3,1,2,4⟩, ⟨3,1,4,2⟩, ⟨3,4,1,2⟩ |

## P15b. Fairness to an unbounded source

Under the stream reading of P09d2: z is the unbounded sequence ⟨0, 0, 0, …⟩,
and the merge is of z and ⟨9⟩. Read as the greatest relation, merge also
admits the unfair interleaving that takes only from z, so this problem adds
a requirement the definition alone does not give: **fairness**, meaning
every element of both inputs appears at some finite position. Valid: every
fair interleaving, that is, those in which 9 appears at a finite
position.

Record the position at which 9 appears in what the system produces within
the budget, or that it does not appear. A merge that takes only from z
produces a valid prefix but never a valid outcome.

## P15c. One resource, two requests at once

One stage: requests from ᴀ and from ʙ for one resource arrive together.
Exactly one is granted. Valid outcomes: ᴀ granted and ʙ not, or ʙ granted
and ᴀ not. An "any one" query.

## P15d. One resource, over time

| stage | information | valid outcomes |
|---|---|---|
| 1 | ᴀ requests | ᴀ holds the resource |
| 2 | ʙ requests | ᴀ holds it; ʙ waits |
| 3 | ᴀ releases | ʙ holds it |

A grant, once made, is not withdrawn when a later request arrives. That is
committed choice.

## Observations

- P15a: the order in which interleavings are reported, and whether the
  choice in P15a1 is deterministic from run to run.
- P15b: the position of 9, or its absence.
- P15c: how the choice between ᴀ and ʙ is made, and whether it is
  committed (not revisited on backtracking).
- P15d: how ʙ's waiting is held, and whether stage 3 resumes it or ʙ's
  request has to be posed again.
