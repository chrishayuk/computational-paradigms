# P01. Unknown equality

**Probes:** how a system represents a relation between unknowns before
either has a value, and whether a later value reaches all of them.

## Vocabulary

conc(a, b, c): c = a ++ b. It is defined by:

1. conc(⟨⟩, b, b)
2. conc(⟨h⟩ ++ a, b, ⟨h⟩ ++ c) if conc(a, b, c)

## P01a. A chain of equations

| stage | information |
|---|---|
| 1 | x = y |
| 2 | y = z |
| 3 | z = 2 |

Valid outcomes:

- after 1: every assignment with x = y; z free.
- after 2: every assignment with x = y = z.
- after 3: x = y = z = 2.

## P01b. An unknown inside a structure

| stage | information |
|---|---|
| 1 | conc(⟨1,2⟩, s, t) |
| 2 | s = ⟨3⟩ |

Valid outcomes:

- after 1: t = ⟨1,2⟩ ++ s, for every sequence s.
- after 2: s = ⟨3⟩, t = ⟨1,2,3⟩.

## P01c. A self-referential equation

| stage | information |
|---|---|
| 1 | x = ⟨1⟩ ++ x |

Valid outcome: no finite sequence satisfies it, so there are no solutions
among the values of this study.

## Observations

- After P01a stage 1 and P01b stage 1, how is the relation between unknowns
  held? For example: as one shared unknown, as a recorded equation, or
  otherwise.
- Whether the value of stage 3 (P01a) or stage 2 (P01b) reaches every
  unknown it determines, and in how many steps.
- For P01c: reported failure, a cyclic or infinite value, a suspension,
  budget, or error. A cyclic value is recorded as what it is. It is
  classified *unsound* only if the system presents it as a finite sequence.
