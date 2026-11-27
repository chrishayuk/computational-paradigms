# S mechanisms of the ALGOL 60 configurations

*Phase 4, before any program is run (`PROTOCOL.md`, "Recording a result":
every configuration's S mechanisms are listed, with their size). Class S is
code that implements a mechanism the configuration lacks (`METRICS.md`,
class S, rules 12 and 19).*

The systems file (`systems/algol-60/README.md`) admits supporting code for
every ALGOL 60 configuration: "ALGOL 60 has no unknowns, no relations and no
alternatives of its own … Some problems may be *not expressible* without
supporting code. That is a result." It names no supporting code that the
configurations provide, and none has been written for this study.

| configuration | S mechanisms provided | size |
|---|---|---|
| **report** | none | 0 tokens |
| **x1** | none | 0 tokens |
| **x1sim** | none | 0 tokens |

So every configuration of ALGOL 60 is, for this study, its **core** only
(the Revised Report, with the input and output procedures listed as external
mechanisms in report, and the X1 system's own procedures in x1 and x1sim). A
program that needs a mechanism ALGOL 60 lacks (a constraint store or
propagator general over relations, a unifier, a scheduler, a search) and
writes it is, by `METRICS.md` rule 19, in an *extended* configuration named
by that mechanism; since no such mechanism is listed here, such a program is
reported as a named variant, and the problem is *not expressible* in the
configuration as listed.

What is **not** S, so that it is not mistaken for it:

- the harness's own constructs in a program (reading the instance line and
  messages, the message dispatch, the printed tags, `emit`'s binding, output
  adapters, counters): these are **H**, listed in `README.md`, section 2.7;
- the input and output procedures (`ininteger`, `outinteger`, `outstring`;
  `read`, `print`, `PRINTTEXT`, `NLCR`): external mechanisms of the
  configuration (report), or the X1 system's own (x1, x1sim), counted as
  their call tokens;
- code written for one problem's own relations that holds them until their
  values arrive: **R**, in the core configuration (`METRICS.md` rule 19).

The harness itself (`run`) supplies no mechanism to any program: it passes
stages in and reads what the program prints (`README.md`, section 3.5).
