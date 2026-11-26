# P02. Late information

**Probes:** whether relations that cannot yet be decided are kept and
resumed when information arrives, and at what cost.

From Elcock (1982, p. 123), who gives the three relations in this order.
All unknowns are integers.

## The relations

- R1: u + v = 16
- R2: w · u = v
- R3: u + 10 = 12

## P02a. In Elcock's order

| stage | information | valid outcomes |
|---|---|---|
| 1 | R1 | every integer pair with u + v = 16; w free (infinite) |
| 2 | R2 | exactly ten triples (u, v, w), below |
| 3 | R3 | u = 2, v = 14, w = 7 |

After stage 2, u · (w + 1) = 16, so u divides 16. The ten triples are
(1, 15, 15), (2, 14, 7), (4, 12, 3), (8, 8, 1), (16, 0, 0), (−1, 17, −17),
(−2, 18, −9), (−4, 20, −5), (−8, 24, −3) and (−16, 32, −2).

## P02b. Every order

The three relations, one per stage, in all six orders. After each stage,
the valid outcomes depend only on which relations have arrived:

| relations so far | valid outcomes |
|---|---|
| R1 | u + v = 16, w free (infinite) |
| R2 | v = w · u (infinite) |
| R3 | u = 2; v and w free (infinite) |
| R1, R2 | the ten triples above |
| R1, R3 | u = 2, v = 14; w free (infinite) |
| R2, R3 | u = 2, v = 2w, for every integer w (infinite) |
| R1, R2, R3 | u = 2, v = 14, w = 7 |

## P02c. All at once

R1, R2 and R3 as one stage, in that order. Valid outcome: u = 2, v = 14,
w = 7.

## Observations

- After each stage that does not decide everything: what is held for each
  relation not yet decided, and what each is waiting for, in the system's
  terms.
- When the last relation arrives: in what order the held relations are
  taken up, and how many times each is examined, from a trace if the
  system gives one.
- P02b: whether all six orders give the same final outcome, and the steps
  of each.
- Incremental cost, restated cost, restart cost and repeated work for each
  stage (`METRICS.md`).
