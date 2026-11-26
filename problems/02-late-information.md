# P02. Late information

**Probes:** whether relations that cannot yet be decided are kept and
resumed when information arrives, and at what cost.

From Elcock (1982, p. 123), who gives the three relations in this order.

## Vocabulary

Integer arithmetic: a + b = c and a · b = c, as relations.

## Stages

| stage | information |
|---|---|
| 1 | u + v = 16 |
| 2 | w · u = v |
| 3 | u + 10 = 12 |

Valid outcomes:

- after 1: every integer pair with u + v = 16; w free.
- after 2: every integer triple with u + v = 16 and w · u = v.
- after 3: u = 2, v = 14, w = 7, the only solution.

## P02b. Every order

The same three relations, each in a stage of its own, in all six orders.
The valid outcome after the third stage is always u = 2, v = 14, w = 7.

## P02c. All at once

The three relations as one stage, in the order above. Valid outcome:
u = 2, v = 14, w = 7.

## Observations

- After stages 1 and 2: what is held for each relation that cannot yet be
  decided, and what each is waiting for, in the system's terms.
- At stage 3: in what order the held relations are taken up, and how many
  times each is examined, from a trace if the system gives one.
- P02b: whether all six orders give the same final outcome, and the steps
  of each.
- The incremental and restated costs of each stage (`METRICS.md`).
