# S mechanisms of the SWI-Prolog configurations

*`PROTOCOL.md`, "Recording a result": every configuration's S mechanisms
are listed, with their size, at phase 4, before any program is run.
`METRICS.md`, class S and rule 12: code that provides a mechanism the
configuration lacks, counted once per mechanism per configuration. This
file lists; it is not a problem program.*

The systems file (`systems/swi-prolog/README.md`, "Configurations")
admits supporting code in one configuration only: *session*, "with
supporting code that makes an application wait for an undefined
procedure", and says that it is counted as S there. The other four
configurations are defined by what SWI-Prolog itself provides, and name no
supporting code.

| configuration | S mechanisms the configuration provides | size |
|---|---|---|
| `plain` | none | — |
| `tabling` | none | — |
| `coroutines` | none | — |
| `constraints` | none | — |
| `session` | **wait for an undefined procedure**: [`S/session-wait.pl`](S/session-wait.pl) | 19 lines, 158 tokens (comments and layout not counted) |

## session: wait for an undefined procedure

[`S/session-wait.pl`](S/session-wait.pl), loaded by the harness before the
program in *session* only, so that it is part of every *session* run, as
the systems file defines the configuration. It is general over
procedures, not written for any problem.

When the session's computation (the engine that holds the stages) calls a
procedure that has no definition, SWI-Prolog consults the hook
`user:exception(undefined_predicate, PI, Action)` before raising the
existence error. The hook gives the procedure one waiting clause and
answers `retry`. The waiting clause waits, with the harness call
`h_wait/0` (class H: the stage ends with the computation waiting, and the
next stage is received into the same computation), until a stage has
given the procedure a clause of its own (by `assertz/1`); it then removes
itself and calls the procedure. Outside the session's engine (a spawned
computation runs as a separate query) the hook does nothing and the
system raises its error as usual. (The hook cannot wait itself, since it
is called from C, and an engine cannot yield from inside such a call;
hence the waiting clause.)

Its size: the file without its comments, 19 non-blank lines, 158 lexical
tokens (atoms, variables, numbers, strings, punctuation and operator
symbols), counted by a regular-expression tokeniser; the classifiers count
its tokens by `METRICS.md` themselves. Its inferences are the program's
(S code is not paused, unlike harness code).

A program may also write supporting code of its own, in any
configuration. That is the program's S, counted against that
configuration and listed by the classifiers (`METRICS.md`, rule 12), not a
mechanism the configuration provides.

## Not S

- The harness's predicates (`h_param/2`, `h_commitment/1`, `emit/1`,
  `h_count/1`, `h_candidate/0`, `h_held/2`, `h_wait/0`) are H
  (`README.md`, section 12).
- Libraries outside a configuration's core (`library(lists)`,
  `library(clpfd)`, …) are external mechanisms, listed under that metric,
  not S (`METRICS.md`, "The core of a configuration").
