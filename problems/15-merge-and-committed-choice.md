# P15. Merge and committed choice

*Added after review 1.*

**Probes:** how a system arbitrates between computations: interleaving two
sources, fairness to an unbounded one, and granting a single resource.

## P15a. Merge

merge(a, b, m): m is an interleaving of a and b that keeps the order of
each. It is defined, in this order, by:

1. merge(⟨⟩, b, b), for every sequence b
2. merge(⟨h⟩ ++ a, ⟨⟩, ⟨h⟩ ++ a), for every sequence a
3. merge(⟨h⟩ ++ a, b, ⟨h⟩ ++ m) if b ≠ ⟨⟩ and merge(a, b, m)
4. merge(a, ⟨h⟩ ++ b, ⟨h⟩ ++ m) if a ≠ ⟨⟩ and merge(a, b, m)

| | query | valid outcomes |
|---|---|---|
| P15a1 | merge(⟨1,2⟩, ⟨3,4⟩, m), any one | any of the six interleavings |
| P15a2 | merge(⟨1,2⟩, ⟨3,4⟩, m), all | all six: ⟨1,2,3,4⟩, ⟨1,3,2,4⟩, ⟨1,3,4,2⟩, ⟨3,1,2,4⟩, ⟨3,1,4,2⟩, ⟨3,4,1,2⟩ |

## P15b. Fairness to an unbounded source

Under the stream reading of P09d2. z is defined by

1. zeros(⟨0⟩ ++ s) if zeros(s)

read as the greatest relation, so zeros(z) makes z = ⟨0, 0, 0, …⟩. A
consumer asks where 9 is: position(e, m, i) holds when the i-th element of
m is e. It is defined, in this order, by

1. position(e, ⟨e⟩ ++ t, 1)
2. position(e, ⟨h⟩ ++ t, i) if h ≠ e and position(e, t, j) and i = j + 1

The query is zeros(z) and merge(z, ⟨9⟩, m) and position(9, m, i), in that
order, an any-one query (`answers(1)`). The arguments of merge are in the order that disadvantages a
depth-first merge, which takes from z for ever. **P15b2** poses the same
with merge(⟨9⟩, z, m). Read as the greatest relation, merge also
admits the unfair interleaving that takes only from z, so this problem adds
a requirement the definition alone does not give: **fairness**, meaning
every element of both inputs appears at some finite position. Valid: every
fair interleaving, that is, those in which 9 appears at a finite
position.

Valid outcome: i = some positive integer. A system that reports a value of
i is *complete* for i, whatever it has produced of m, and whether or not
the producer of z stops. A merge that takes only from z never binds i:
*none reported* with *budget*.

## P15c. One resource, two requests at once

grant(p, q, g): of two requests, from p and from q, for one resource, g is
the one granted. It is defined by

1. grant(p, q, p)
2. grant(p, q, q)

One stage: grant(ᴀ, ʙ, g), an any-one query (`answers(1)`). Valid outcomes:
g = ᴀ, or g = ʙ. Committed choice means the system selects one and does not
revisit it.

## P15d. One resource, over time

| stage | information | valid outcomes |
|---|---|---|
| 1 | ᴀ requests | holder = ᴀ, queue = ⟨⟩ |
| 2 | ʙ requests | holder = ᴀ, queue = ⟨ʙ⟩ |
| 3 | ᴀ releases | holder = ʙ, queue = ⟨⟩ |

holder and queue are named quantities, as in P10, starting as none and ⟨⟩.
A request and a release are replacing stages, defined by cases:

- p requests: if holder = none, holder becomes p; otherwise queue becomes
  queue ++ ⟨p⟩;
- p releases, where holder = p: if queue = ⟨⟩, holder becomes none;
  otherwise, with queue = ⟨h⟩ ++ t, holder becomes h and queue becomes t.

A program may implement this as a process, or by these replacements.
Either is a transcription (P).

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
