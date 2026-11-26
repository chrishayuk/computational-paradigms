# P11. Irreversible effects

*Proposed in review of draft 0.1. Whether it is kept is decided before the
freeze.*

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

## Effects

This problem adds a fourth classification axis, applied to it alone:

| class | meaning |
|---|---|
| **exact** | L holds exactly the effects of the outcome committed to |
| **extra** | L also holds effects performed for alternatives later rejected |
| **missing** | an effect the committed outcome requires was not performed |
| **deferred** | effects were held back until commitment, with the point of commitment recorded |

## P11a. The effect after the test

One stage: pick(x) and x ≥ 2 and emit(x), in that order.

Valid: one answer, x = 2 or x = 3, and L holds exactly that one entry.

## P11b. The effect before the test

One stage: pick(x) and emit(x) and x ≥ 2, in that order.

Valid: as P11a. A log of ⟨1, 2⟩ is *extra*.

## P11c. The effect, then a late contradiction

| stage | information |
|---|---|
| 1 | pick(x) and emit(x) |
| 2 | x ≠ 1 |

Valid after stage 2: one answer, x = 2 or x = 3, and L holds exactly that
one entry. A system that emitted 1 at stage 1 is *extra*, unless it deferred
the effect.

## Rules

- emit is a problem token.
- Any deferral the program arranges itself, such as collecting answers
  before emitting, is control.

## Observations

- L, verbatim.
- The effects class.
- Where commitment happens, in the system's own terms.
- The control tokens used to avoid *extra*.
