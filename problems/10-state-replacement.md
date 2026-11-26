# P10. State replacement

*Added after review 1.*

**Probes:** how a system represents a value that changes, a relation that
must keep holding while its inputs change, and the withdrawal of
information already given.

Every other problem only adds information. This one replaces and retracts
it, which imperative systems, PLANNER's erase and Conniver's contexts are
designed to do.

## Vocabulary

- b and d are **named quantities**, not unknowns. A quantity has one value
  at a time.
- "b becomes e" is a **replacing** stage. After it, b's value is e, with
  any b inside e taken at its value before the stage.
- "withdraw R" is a **retracting** stage. After it, the information is
  everything given so far, without R.
- pick is as in P05.

The valid outcomes after a replacing or retracting stage are computed from
the current values and the information not withdrawn (`SPECIFICATION.md`).
A system that reposes replays every stage, replacements and withdrawals
included (`PROTOCOL.md`).

## P10a. Absolute and relative replacement

| stage | information | valid outcomes |
|---|---|---|
| 1 | b becomes 10 | b = 10 |
| 2 | b becomes b + 5 | b = 15 |
| 3 | b becomes 7 | b = 7 |

## P10b. A standing relation

Here d is not given values by replacing stages. It is defined by a relation
that must hold whenever b has a value.

| stage | information | valid outcomes |
|---|---|---|
| 1 | d = 2 · b, at all times | d = 2 · b; neither has a value yet |
| 2–4 | the stages of P10a | d = 20, then 30, then 14 |

## P10c. A snapshot

| stage | information | valid outcomes |
|---|---|---|
| 1 | b becomes 10 | b = 10 |
| 2 | d becomes 2 · b | d = 20 |
| 3 | b becomes b + 5 | b = 15, d = 20 |
| 4 | b becomes 7 | b = 7, d = 20 |

P10b and P10c tell a relation that keeps holding apart from a value
computed once.

## P10d. Retraction of a constraint

| stage | information | valid outcomes |
|---|---|---|
| 1 | pick(x) | x ∈ {1, 2, 3} |
| 2 | x > 1 | x ∈ {2, 3} |
| 3 | withdraw x > 1 | x ∈ {1, 2, 3} |

## Observations

- Whether the system represents replacement natively, or by indexing values
  with time or version. Indexing written for the purpose is reformulation.
- Whether earlier values can still be retrieved after they are replaced.
- P10b: how many dependent values are recomputed after each replacement,
  and in how many steps.
- P10d: whether the alternative that x > 1 removed comes back, and whether
  that needs restating.
