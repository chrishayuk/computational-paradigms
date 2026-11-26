# computational-paradigms

A comparative study of computational models. The study asks:

> **How do different computational models represent, retain and resolve
> partially specified computations?**

The same nine problems are posed, in stages, to each system. Each stage
adds information. The study records:

- what each system reports;
- what it keeps waiting;
- what it has to redo;
- how much control code, supporting code and manual help it needs.

The method follows TPK (Knuth and Trabb Pardo, 1976): one fixed problem
set, written in each language's own idiom. Here the problems are
incremental and symbolic rather than numerical.

## Status

**Draft specification. No system has been compared.**

- The specification, the metrics and the protocol are drafts awaiting
  independent review.
- Nothing is frozen.
- No programs have been written for this study.

Programs come after the freeze (`PROTOCOL.md`).

## Contents

| file | what it is |
|---|---|
| [`SPECIFICATION.md`](SPECIFICATION.md) | the question, the conventions, the classes of outcome, and what is not assumed |
| [`problems/`](problems) | the nine problems, in mathematical notation, with their valid outcomes |
| [`METRICS.md`](METRICS.md) | what is measured, and the frozen rules for classing tokens |
| [`PROTOCOL.md`](PROTOCOL.md) | phases, amendments, evidence classes, configurations, how programs are written, run and recorded |
| [`systems/`](systems) | each system's configurations and evidence class |
| [`sources/`](sources) | where the problems and the systems' idioms come from |
| [`results/`](results) | empty until the freeze |

## Systems

The first two are [Absys](systems/absys) and
[SWI-Prolog](systems/swi-prolog). Each has the configurations described in
its folder. Earlier experiments on both are in the
[absys](https://github.com/chrishayuk/absys) repository. They are not
results of this study: they were written before the problems were fixed.

Proposed after them, in order, and not started:

- PLANNER, with the described language and Micro-Planner kept separate;
- Conniver;
- Concurrent Prolog;
- concurrent constraint programming;
- Oz.

These are a sequence for comparison, not a claim that each influenced the
next.

## Licence

Apache-2.0.
