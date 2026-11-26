# ALGOL 60

The historical imperative baseline: a mainstream programming model of the
same period as Absys, with structured control, recursion, procedures, call
by name and mutable variables.

The system is the reconstruction in `~/chris-source/esoteric/algol-60`
(the `algol60` interpreter, built from the *Revised Report*, 1962),
provisionally pinned at commit `6e8740c`. The commit is fixed at the
freeze. That repository is not changed for this study; a change it needed
would make a new configuration.

## Configurations

| configuration | what it is | class |
|---|---|---|
| **report** | the Revised Report, as the interpreter implements it | reconstructed |
| **x1** | `--x1`: the Dijkstra–Zonneveld system for the Electrologica X1, as its documents describe it | reconstructed |
| **x1sim** | the surviving 1964 X1 compiler, in a C translation, on a simulator of the X1. The run-time routines it calls do not survive, and are a separate reconstruction | rehosted (compiler), reconstructed (run-time) |

The Report defines no input or output. The interpreter's `ininteger`,
`outinteger` and related procedures are from the IFIP proposals of 1964,
and are listed under external mechanisms for *report*.

ALGOL 60 has no unknowns, no relations and no alternatives of its own. As
with Python, a program uses the algorithm natural to the language, and
records its departures from the problem's definitions as reformulation.
Some problems may be *not expressible* without supporting code. That is a
result.

## Units

To be qualified before the freeze:

- **Step:** the interpreter's own steps, as `--max-steps` counts them (one
  per statement or expression evaluated; to be confirmed and stated
  exactly).
- **Store:** not yet reported by the interpreter. Reporting it would be an
  instrumentation-only change, under the conditions of `PROTOCOL.md`.
- **Alternative:** as Python: whatever structure the program keeps, named.

## The same computation

A program may read each stage with `ininteger` or `insymbol` as it
arrives, which counts as the same computation. Otherwise each stage is
posed by rerunning with stages 1 to k.
