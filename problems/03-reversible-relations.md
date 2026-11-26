# P03. Reversible relations

**Probes:** whether one definition of a relation serves for every
combination of known and unknown arguments, and whether the system knows
when it has found every answer.

## Vocabulary

conc, as in P01, with its cases in that order.

rev(a, b): b is a in reverse order. It is defined, in this order, by:

1. rev(⟨⟩, ⟨⟩)
2. rev(⟨h⟩ ++ l, r) if rev(l, q) and conc(q, ⟨h⟩, r), with the two
   conjuncts in that order

## Queries

Each is one stage.

| | query | valid outcomes |
|---|---|---|
| P03a | conc(⟨1,2⟩, ⟨3⟩, c) | c = ⟨1,2,3⟩ |
| P03b | conc(a, b, ⟨1,2⟩) | three: (⟨⟩, ⟨1,2⟩), (⟨1⟩, ⟨2⟩), (⟨1,2⟩, ⟨⟩) |
| P03c | conc(⟨1⟩, b, ⟨1,2,3⟩) | b = ⟨2,3⟩ |
| P03d | conc(a, ⟨3⟩, ⟨1,2,3⟩) | a = ⟨1,2⟩ |
| P03e | rev(⟨1,2,3⟩, b) | b = ⟨3,2,1⟩ |
| P03f | rev(a, ⟨1,2,3⟩) | a = ⟨3,2,1⟩, exactly one |

## Observations

- Whether every valid outcome is reported, and in what order.
- After the last valid outcome: whether the computation finishes, holds
  alternatives pending, or goes on to the budget. P03f has exactly one
  solution, so a system that reports it and then runs out of budget is
  *complete* with *budget*.
- Whether any direction needed reformulation, and how.
