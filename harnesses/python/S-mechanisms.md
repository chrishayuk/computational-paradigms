# Supporting-code (S) mechanisms of the Python configurations

*Phase 4, before any program is run (`PROTOCOL.md`, "Recording a result":
every configuration's S mechanisms are listed, with their size, at phase
4). Source: `systems/python/README.md`, "Configurations". This file lists;
it implements nothing, and no problem program was written.*

| configuration | admits S? | S mechanisms it provides | size |
|---|---|---|---|
| **core** | no: the language and its built-ins, no imports | none | — |
| **stdlib-concurrency** | no: core plus `threading`, `queue`, `asyncio`, which are external mechanisms (listed by name), not S | none | — |
| **extended** | yes: "mechanisms written for the experiment: for instance a backtracking search, a suspension queue, a constraint propagator. Counted as S, once per mechanism" | **none defined.** The systems file names three mechanisms *for instance*, and defines none of them: no code, interface or size exists for any at the freeze or at phase 4 | — |

## What this means for programs

- A program for **extended** can use, at phase 4, no S mechanism, since none
  is listed here with its size. Until one is defined and listed (with its
  code, its interface and its size in tokens, counted once for the
  configuration, `METRICS.md` rule 12), extended is the same as core for
  any program written against this file. See [`QUESTIONS.md`](QUESTIONS.md),
  Q3.
- Code a program writes for itself that is general over relations, and
  reusable from one problem to another (a constraint store, a propagator,
  a scheduler), is S by `METRICS.md` rules 12 and 19 wherever it is kept, and
  puts the program in *extended*, named by that mechanism. That is a
  classification of the program by the classifiers, not a mechanism this
  harness provides.
- The harness's own machinery (the step meter, the pause at the budget, the
  threads that run spawned computations, the watcher for quiescence, the
  `cp` calls) is harness code, not S, and is not available to a program as a
  mechanism: it is listed in [`README.md`](README.md) as H tokens and as
  confounds.
