# P06. Negation with unknowns

**Probes:** whether negation gives valid outcomes when the unknowns it
mentions are still unknown, and whether the order of information changes
the outcome.

not R holds of an assignment exactly when R does not hold of it. Definitions
with negation are read under the stratified semantics
(`SPECIFICATION.md`). Relations given by facts are in a closed world.

## P06a. Negation, then a value

| stage | information | valid outcomes |
|---|---|---|
| 1 | not (x = 1) | every value x other than 1 |
| 2 | x = 2 | x = 2 |

## P06b. A value, then negation

| stage | information | valid outcomes |
|---|---|---|
| 1 | x = 2 | x = 2 |
| 2 | not (x = 1) | x = 2 |

## P06c. A contradiction through negation

| stage | information | valid outcomes |
|---|---|---|
| 1 | not (x = 1) | every value x other than 1 |
| 2 | x = 1 | none |

## P06d. Set difference

mem(e, s): e is an element of the sequence s. It is defined, in this order,
by:

1. mem(e, ⟨e⟩ ++ t), for every sequence t
2. mem(e, ⟨h⟩ ++ t) if mem(e, t)

setdiff(s1, s2, d): d is the elements of s1 that are not elements of s2, in
their order in s1. It is defined, in this order, by:

1. setdiff(⟨⟩, s2, ⟨⟩)
2. setdiff(⟨h⟩ ++ t, s2, d) if mem(h, s2) and setdiff(t, s2, d)
3. setdiff(⟨h⟩ ++ t, s2, ⟨h⟩ ++ d) if not mem(h, s2) and setdiff(t, s2, d)

| stage | information | valid outcomes |
|---|---|---|
| 1 | setdiff(⟨1,2,3,4⟩, ⟨2,4,6⟩, d) | d = ⟨1,3⟩ |

A system with a set-forming construct may state the same definition with it.
That counts as problem tokens too (`METRICS.md`, rule 6).

## P06e. Clark's students

A closed world, from Clark (1978) as rendered by Elcock (1990):

- student(ʙʀᴏᴡɴ), student(ꜱᴍɪᴛʜ)
- maths(ᴄ101), maths(ᴄ301)
- takes(ʙʀᴏᴡɴ, ᴄ101), takes(ꜱᴍɪᴛʜ, ᴄ101), takes(ꜱᴍɪᴛʜ, ᴄ301)

nonmajor(p): p is a student who does not take some maths course. It is
defined by one case:

1. nonmajor(p) if student(p) and maths(k) and not takes(p, k), with the
   conjuncts in that order

| | query | valid outcomes |
|---|---|---|
| P06e1 | nonmajor(ʙʀᴏᴡɴ) | true |
| P06e2 | nonmajor(ꜱᴍɪᴛʜ) | false |
| P06e3 | nonmajor(p) | p = ʙʀᴏᴡɴ |

## Observations

- Whether P06a and P06b give the same outcome. A system that reports no
  solution for P06a is *unsound*; record the step at which the negation
  was decided.
- P06a stage 1: whether the negation is held as a condition, decided at
  once, delayed, or an error. A representation that restricts x to integers
  is *partial*.
- P06e3: whether p and k are known before the negation is decided.
