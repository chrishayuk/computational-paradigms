# P01. Unknown equality

**Probes:** how a system represents a relation between unknowns before
either has a value, and whether a later value reaches all of them.

## Vocabulary

conc(a, b, c): c is a followed by b. It is defined by:

1. conc(⟨⟩, b, b), for every sequence b
2. conc(⟨h⟩ ++ a, b, ⟨h⟩ ++ c) if conc(a, b, c)

So conc relates sequences only.

## P01a. A chain of equations

| stage | information | valid outcomes |
|---|---|---|
| 1 | x = y | every assignment with x = y; z free |
| 2 | y = z | every assignment with x = y = z |
| 3 | z = 2 | x = y = z = 2 |

## P01b. An unknown inside a structure

| stage | information | valid outcomes |
|---|---|---|
| 1 | conc(⟨1,2⟩, s, t) | t = ⟨1,2⟩ ++ s, for every sequence s |
| 2 | s = ⟨3⟩ | s = ⟨3⟩, t = ⟨1,2,3⟩ |

## P01c. A self-referential equation

| stage | information |
|---|---|
| 1 | x = ⟨1⟩ ++ x |

Two readings:

- **finite:** no finite sequence satisfies it. Valid outcome: none.
- **rational:** over rational trees (finite or infinite terms with
  finitely many distinct subterms), it has one solution, the infinite
  sequence ⟨1, 1, 1, …⟩.

A result is classified under each reading. A cyclic value, presented as
such, is *complete* under the rational reading and *unsound* under the
finite one.

## Observations

- After P01a stage 1 and P01b stage 1, how the relation between unknowns is
  held: as one shared unknown, as a recorded equation, or otherwise.
- Whether the value of P01a stage 3, or P01b stage 2, reaches every unknown
  it determines, and in how many steps.
- P01c: the report, and the configuration's occurs-check setting.
