# P06. Negation with unknowns

**Probes:** whether negation gives valid outcomes when the unknowns it
mentions are still unknown, and whether the order of information changes
the outcome.

The negation here is of a relation. not R holds of an assignment exactly
when R does not hold of it. Where relations are given by facts, the world is
closed: only the facts stated are true.

## P06a. Negation, then a value

| stage | information | valid outcomes |
|---|---|---|
| 1 | not (x = 1) | every x ≠ 1 |
| 2 | x = 2 | x = 2 |

## P06b. A value, then negation

| stage | information | valid outcomes |
|---|---|---|
| 1 | x = 2 | x = 2 |
| 2 | not (x = 1) | x = 2 |

## P06c. A contradiction through negation

| stage | information | valid outcomes |
|---|---|---|
| 1 | not (x = 1) | every x ≠ 1 |
| 2 | x = 1 | none |

## P06d. Set difference

mem(x, s): x is an element of s. It is defined, in this order, by:

1. mem(x, ⟨x⟩ ++ t)
2. mem(x, ⟨h⟩ ++ t) if mem(x, t)

setdiff(s1, s2, d): d is the sequence of the elements of s1 that are not
elements of s2, in their order in s1.

| stage | information | valid outcomes |
|---|---|---|
| 1 | setdiff(⟨1,2,3,4⟩, ⟨2,4,6⟩, d) | d = ⟨1,3⟩ |

setdiff is given by its meaning, not by a definition. Each system defines
it in its own idiom, and the definition is counted as P where it states
that meaning directly and as R otherwise.

## P06e. Clark's students

A closed world, from Clark (1978) as rendered by Elcock (1990):

- student(brown), student(smith)
- maths(c101), maths(c301)
- takes(brown, c101), takes(smith, c101), takes(smith, c301)

nonmajor(s): s is a student, and there is a maths course c that s does not
take.

| | query | valid outcomes |
|---|---|---|
| P06e1 | nonmajor(brown) | true |
| P06e2 | nonmajor(smith) | false |
| P06e3 | nonmajor(s) | s = brown |

## Observations

- Whether P06a and P06b give the same outcome. A system that reports no
  solution for P06a is *unsound* by the definition in
  `SPECIFICATION.md`; record the step at which the negation was decided.
- P06a stage 1: whether the negation is held as a condition, decided at
  once, delayed, or an error.
- P06e3: whether the unknown s is decided before the negation is.
