# S mechanisms of the Absys configurations

*`PROTOCOL.md`, "Recording a result": every configuration's S mechanisms
are listed, with their size, before any program is run. `METRICS.md`,
class S: code that implements a mechanism the configuration lacks,
counted once per mechanism per configuration.*

| configuration | S mechanisms | size |
|---|---|---|
| `absys` | none | 0 tokens |
| `absys-depth-first` | none | 0 tokens |
| `absys-wake-back` | none | 0 tokens |

**Why none.** The systems file: "Nothing else exists to be imported, so
every Absys configuration has no external mechanisms." Absys has no
library, no import and no foreign call, and this harness provides none:
it gives the system the program's text, its own commands (`.help`, `?`,
`? NAME`, `.trace`) and the parameters' assertions (README, 3.4), none of
which is a mechanism a program can use to compute. The binding of emit is
`tout`, a primitive of the core (systems file, "The core"), and is H, not
S (README, 3.12).

So any supporting code a program for Absys needs (a scheduler, a
wait-for-definition layer, a hand-written search) can only be written in
the program itself, in Absys. It is then S counted against that
configuration under `METRICS.md`, rule 12, once per mechanism, with the
problems that use it listed, and this file lists nothing for it in
advance.
