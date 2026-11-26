# P04. Unbounded alternative

**Probes:** whether an alternative with no finite derivation stops the
system from finding another alternative that has one, and whether a
left-recursive definition can be used on data that is known.

## Vocabulary

loop(x): defined only by

1. loop(x) if loop(x)

Read as the least relation, loop has no instances.

as(s): s is a finite sequence of the atom a. It is defined, in this order,
by:

1. as(s) if as(m) and s = ⟨a⟩ ++ m, with the two conjuncts in that order
2. as(⟨⟩)

## Queries

Each is one stage.

| | query | valid outcomes |
|---|---|---|
| P04a | loop(x) or x = 1, in that order | x = 1 |
| P04b | x = 1 or loop(x), in that order | x = 1 |
| P04c | as(⟨a,a⟩) | true (one solution, no unknowns) |
| P04d | as(s) | infinitely many: s = ⟨⟩, ⟨a⟩, ⟨a,a⟩, … |

## Observations

- P04a and P04b: whether x = 1 is reported, and whether the computation
  then finishes, suspends or runs to budget.
- P04c: the outcome, and whether the computation finishes.
- P04d: which solutions are reported within the budget, in what order, and
  whether every solution would be reached given enough steps.
