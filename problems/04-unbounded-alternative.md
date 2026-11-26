# P04. Unbounded alternative

**Probes:** whether an alternative with no finite derivation stops the
system from finding one that has one, and how the order in which a
recursive definition is written affects its use.

## Vocabulary

loop(x): defined only by

1. loop(x) if loop(x)

Read as the least relation, loop has no instances.

alist(s): s is a finite sequence of the atom ᴀ. Two definitions are given.
They have the same meaning and are written differently.

- **alist-left**, in this order:
  1. alist(s) if alist(m) and s = ⟨ᴀ⟩ ++ m, with the two conjuncts in that
     order
  2. alist(⟨⟩)
- **alist-right**, in this order:
  1. alist(⟨⟩)
  2. alist(⟨ᴀ⟩ ++ m) if alist(m)

## Queries

Each is one stage.

| | query | valid outcomes |
|---|---|---|
| P04a | loop(x) or x = 1, in that order | x = 1 |
| P04b | x = 1 or loop(x), in that order | x = 1 |
| P04c | alist(⟨ᴀ,ᴀ⟩), with alist-left | true: one solution, no unknowns |
| P04d | alist(s), with alist-left | infinitely many: s = ⟨⟩, ⟨ᴀ⟩, ⟨ᴀ,ᴀ⟩, … |
| P04e | alist(⟨ᴀ,ᴀ⟩), with alist-right | true |
| P04f | alist(s), with alist-right | infinitely many, as P04d |

## Observations

- P04a and P04b: whether x = 1 is reported, and then whether the
  computation finishes, holds alternatives pending, suspends or runs to
  the budget.
- P04c and P04e: the outcome, and whether the computation finishes.
- P04d and P04f: which solutions are reported, in what order, and whether
  every solution would be reached given enough steps. Compare only this
  property across systems, not the number reported within the budget.
