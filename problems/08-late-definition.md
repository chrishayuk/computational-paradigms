# P08. Late definition

**Probes:** what a system does with an application of a relation that has
no definition yet, and what happens when the definition arrives.

rev is defined as in P03, together with conc.

## P08a. A definition that arrives

| stage | information |
|---|---|
| 1 | a = ⟨x, y, z⟩ |
| 2 | rev(a, b) |
| 3 | x = y |
| 4 | the definitions of rev and conc |
| 5 | y = z |
| 6 | b = ⟨42⟩ ++ c |

Valid outcomes, from stage 4 on:

- after 4: x = y, a = ⟨y, y, z⟩, b = ⟨z, y, y⟩.
- after 5: x = y = z, b = ⟨z, z, z⟩.
- after 6: x = y = z = 42, a = b = ⟨42, 42, 42⟩, c = ⟨42, 42⟩.

Before stage 4, rev has no definition. Two readings are legitimate:

- **closed:** an undefined relation has no instances, so after stages 2
  and 3 there are no solutions;
- **open:** the definition may yet arrive, so the application is pending.

Neither reading is the valid one. Record which the system takes. Under the
open reading, the valid outcomes after stages 2 and 3 are those of the
equations alone.

## P08b. A definition that never arrives

Stages 1 to 3 of P08a, and no more. Record whether the outcome the system
reports can be told apart from failure.

## P08c. A definition that arrives in parts

| stage | information |
|---|---|
| 1 | the definition of conc |
| 2 | rev(⟨1, 2⟩, b) |
| 3 | rev case 1 only: rev(⟨⟩, ⟨⟩) |
| 4 | rev case 2 |

Valid outcomes: after 3, under the closed reading, none, since case 1 alone
does not cover a sequence of two. After 4, b = ⟨2, 1⟩.

## Observations

- Which reading the system takes, and how a pending application is shown.
- Whether posing stage 4 resumes the pending application, or requires it
  to be posed again (intervention).
- P08c: what happens to the application at stage 3. Is it failed, held, or
  resumed with the partial definition? Can stage 4 still reach it?
