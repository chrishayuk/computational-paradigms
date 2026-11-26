# P07. Simultaneous constraints

**Probes:** which systems of arithmetic relations a system solves, which it
leaves unresolved, and which it gets wrong.

All unknowns are integers. Each system is one stage, its relations in the
order given.

| | relations | valid outcomes |
|---|---|---|
| P07a | x + y + z = 12, y + z = 7, z = 3 | x = 5, y = 4, z = 3 |
| P07b | x + y = 10, x − y = 4 | x = 7, y = 3 |
| P07c | x + y = 10 | every integer pair with x + y = 10 |
| P07d | w · u = v, u = 2, v = 14 | w = 7 |
| P07e | w · u = v, u = 2, v = 15 | none: 15 is not a multiple of 2 |
| P07f | x + y = 10, x + y = 11 | none |
| P07g | x · x = 9 | x = 3 or x = −3 |

P07a also runs in all six orders of its relations.

## Observations

- For each: solved, residual (with the residual recorded), enumerated by
  search, unresolved, reported as failure, or error.
- P07e and P07f: whether the inconsistency is detected. A system that holds
  the relations unresolved does not report an invalid outcome, but it does
  not report the empty outcome either. Record it as *none* with
  *suspended*, and note that the inconsistency was not detected.
- P07g: whether both solutions are found.
- What mechanism solves each case that is solved: elaboration one relation
  at a time, propagation, elimination, or search.
