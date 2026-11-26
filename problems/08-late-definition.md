# P08. Late definition

**Probes:** what an application of a relation that has no definition yet
means to a system, and what happens when the definition arrives.

rev and conc are as in P03.

## What an undefined relation can mean

A relation applied before its definition has arrived can be treated as:

1. a relation that is false (it has no instances);
2. a relation whose truth is unknown;
3. a reference to a definition that is unavailable, which is an error;
4. a computation awaiting its definition.

These are different states, and a system may take any of them. Two readings
fix the valid outcomes:

- **closed:** an undefined relation has no instances (state 1);
- **open:** the definition may yet arrive, so an application of it neither
  holds nor fails, and the valid outcomes are those of the other
  information alone.

Neither reading is the valid one. A result records which of the four states
the system takes, and is classified under both readings.

Under the closed reading, a definition's arrival can withdraw an earlier
valid conclusion (no solutions) although the information only grows.
That is the non-monotonicity of conclusions that `SPECIFICATION.md`
describes, and the withdrawal is recorded.

## P08a. A definition that arrives

| stage | information | closed reading | open reading |
|---|---|---|---|
| 1 | a = ⟨x, y, z⟩ | a = ⟨x, y, z⟩ | the same |
| 2 | rev(a, b) | none | a = ⟨x, y, z⟩; b free; rev(a, b) pending |
| 3 | x = y | none | a = ⟨y, y, z⟩; b free; pending |
| 4 | the definitions of rev and conc | a = ⟨y, y, z⟩, b = ⟨z, y, y⟩ | the same |
| 5 | y = z | x = y = z, a = b = ⟨z, z, z⟩ | the same |
| 6 | b = ⟨42⟩ ++ c | x = y = z = 42, a = b = ⟨42, 42, 42⟩, c = ⟨42, 42⟩ | the same |

## P08b. A definition that never arrives

Stages 1 to 3 of P08a, and no more. Record whether the system's report can
be told apart from failure, and which of the four states it shows.

## P08c. A definition that arrives in parts

| stage | information | closed reading | open reading |
|---|---|---|---|
| 1 | the definition of conc | no unknowns | the same |
| 2 | rev(⟨1, 2⟩, b) | none | b free; pending |
| 3 | rev, case 1 only: rev(⟨⟩, ⟨⟩) | none: case 1 alone does not cover a sequence of two | b free; pending, since case 2 may yet arrive |
| 4 | rev, case 2 | b = ⟨2, 1⟩ | the same |

## Observations

- Which of the four states the system takes, and how a pending application
  is shown.
- Whether stage 4 resumes the pending application, or the application has
  to be posed again (restart cost, or intervention if done by hand).
- P08c: what happens to the application at stage 3. Is it failed, held, or
  resumed with the partial definition? Can stage 4 still reach it?
