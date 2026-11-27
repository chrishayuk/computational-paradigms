# P11. Irreversible effects

*Added after review 1.*

**Probes:** whether an externally visible operation is tied to an outcome
the computation commits to, or to the exploration of alternatives that may
later be rejected.

## Vocabulary

- **L** is an external log. Only the operation emit(m) writes to it,
  appending m. Nothing the system does can remove an entry. The harness
  provides L and emit, as one identical stub for every system.
- pick is as in P05.
- These are queries for **any one** outcome: the system is asked for one
  answer, not all.

## Commitment

An outcome is **provisional** until the problem commits to it, and
**final** after. Commitment is explicit, so that no system is asked to
anticipate information it has not received:

- In a problem of one stage, the outcome is committed when it is reported.
- In a problem of several stages, a stage marked **commit** commits: the
  system selects one of its current outcomes, v, and the information
  x = v is added to the problem. A system that holds several outcomes at
  that point must select one. A system that cannot select (one that keeps
  every alternative live, for instance) is judged on every entry it
  emitted: *extra* if L holds more than one entry, *missing* if it holds
  none. Its semantic result is then classified against the outcomes before
  the commit. The valid outcomes after commit are computed
  with x = v.

A reposed run replays a commit as the information x = v, with the v first
selected, so the commitment is preserved (`PROTOCOL.md`).

The log L is kept across every run the harness makes, reposed runs
included, as `PROTOCOL.md` says. Entries duplicated only by reposing are
counted separately.

## Effects

This problem adds a fourth classification axis, applied to it alone,
judged on L when the problem ends:

| class | meaning |
|---|---|
| **exact** | L holds exactly the effects of the committed outcome |
| **extra** | L also holds effects performed for outcomes that were never committed |
| **missing** | an effect the committed outcome requires was not performed |

Separately, for every entry of L, record **when** it was performed:
before commitment (on a provisional outcome), at commitment, or after it.
An effect can be both deferred to commitment and exact.

## P11a. The effect after the test

One stage: pick(x) and x ≥ 2 and emit(x), in that order.

Valid: one answer, x = 2 or x = 3, and L holds exactly that one entry.
Answers are collected with `answers(1)`.

## P11b. The effect before the test

One stage: pick(x) and emit(x) and x ≥ 2, in that order.

Valid: as P11a. A log of ⟨1, 2⟩ is *extra*.

## P11c. The effect, a late contradiction, then commitment

| stage | information |
|---|---|
| 1 | pick(x) and emit(x) |
| 2 | x ≠ 1 |
| 3 | commit |

Valid after stage 3: one answer, x = 2 or x = 3, and L holds exactly that
one entry. An entry emitted before stage 3 was emitted on a provisional
outcome. If that outcome was later refuted (x = 1 at stage 2), L is
*extra*.

## P11d. Commitment, then a contradiction

| stage | information |
|---|---|
| 1 | pick(x) and emit(x) |
| 2 | commit |
| 3 | x ≠ 1 |

Valid: the commit at stage 2 adds x = v, for the v the system selected.
- If v = 1, stage 3 contradicts it: the valid outcome after stage 3 is
  none, and L holding ⟨1⟩ is *exact*, since 1 was the committed outcome.
- If v = 2 or v = 3, stage 3 is consistent: the valid outcome is x = v,
  and L holding ⟨v⟩ is *exact*. Record what the
system does with information that contradicts a committed effect.

## Rules

- emit and commit are problem tokens.
- Any deferral the program arranges itself, such as collecting answers
  before emitting, is control.

## Observations

- L, verbatim, with when each entry was performed.
- The effects class.
- Where commitment happens, in the system's own terms (a cut, a commit
  guard, the end of a query).
- The control tokens used to avoid *extra*.
