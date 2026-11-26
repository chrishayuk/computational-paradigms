# P05. Late contradiction

**Probes:** how a system holds several alternatives while constraints that
eliminate some of them arrive, and what happens to answers it has already
given.

## Vocabulary

pick(x): a closed world of three facts, in this order: pick(1), pick(2),
pick(3).

x > 1 and x ≠ 2 are primitive comparisons.

## P05a. Choice first

| stage | information | valid outcomes |
|---|---|---|
| 1 | pick(x) | x ∈ {1, 2, 3} |
| 2 | x > 1 | x ∈ {2, 3} |
| 3 | x ≠ 2 | x = 3 |

## P05b. Constraint first

| stage | information | valid outcomes |
|---|---|---|
| 1 | x > 1 | every integer x > 1 |
| 2 | pick(x) | x ∈ {2, 3} |

## P05c. Contradiction

| stage | information | valid outcomes |
|---|---|---|
| 1 | pick(x) | x ∈ {1, 2, 3} |
| 2 | x = 4 | none |
| 3 | x = 3 | none |

Stage 3 adds to stages that are already inconsistent, so the valid outcome
stays empty.

## Observations

- After each stage: whether every surviving alternative is held at once, or
  one is held and the others kept for backtracking, or the others are lost.
- An answer reported at one stage and invalid at the next: how its
  withdrawal is shown, if at all.
- P05b stage 1: how a comparison on an unknown is treated: held, reported
  as a residual, enumerated, or an error.
- P05c: how the empty outcome is reported, and whether stage 3 can be
  posed at all.
