# computational-paradigms

A comparative study of computational models. The study asks:

> **How do different computational models represent, retain and resolve
> partially specified computations?**

The same fifteen problems are posed to each system, most of them in stages. A stage
adds information, or in a few problems replaces or withdraws it. The study
records:

- what each system reports;
- what it keeps waiting;
- what it has to redo;
- how much control code, supporting code and manual help it needs.

The method follows TPK (Knuth and Trabb Pardo, 1976), which wrote one fixed
problem in each language's own idiom. Here there is a fixed set of
problems, incremental and symbolic rather than numerical. The aim is a map
of trade-offs, not a ranking.

## Status

**Draft 0.4. No system has been compared.**

- Draft 0.1 was reviewed independently. Draft 0.2 answered every finding
  ([`reviews/review-1.md`](reviews/review-1.md)). Draft 0.3 applied the
  decisions on its open questions
  ([`reviews/decisions-0.2.md`](reviews/decisions-0.2.md)). A second,
  fresh review of draft 0.3 is answered in draft 0.4
  ([`reviews/review-2.md`](reviews/review-2.md)).
- Nothing is frozen.
- No programs have been written for this study.

Programs come after the freeze (`PROTOCOL.md`).

## Contents

| file | what it is |
|---|---|
| [`SPECIFICATION.md`](SPECIFICATION.md) | the question, the conventions, the classes of outcome, and what is not assumed |
| [`problems/`](problems) | the fifteen problems, in mathematical notation, with their valid outcomes |
| [`METRICS.md`](METRICS.md) | what is measured, and the frozen rules for classing tokens |
| [`PROTOCOL.md`](PROTOCOL.md) | phases, amendments, evidence classes, configurations, how programs are written, run and recorded |
| [`systems/`](systems) | each system's configurations and evidence class |
| [`sources/`](sources) | where the problems and the systems' idioms come from |
| [`reviews/`](reviews) | the reviews of each draft, and the response to every finding |
| [`results/`](results) | empty until the freeze |

## Systems

The first comparison is of four:

- [Absys](systems/absys), reconstructed;
- [SWI-Prolog](systems/swi-prolog), modern;
- [Python](systems/python), the modern imperative baseline;
- [ALGOL 60](systems/algol-60), the historical imperative baseline.

Each has the configurations described in its folder. Earlier experiments on Absys and SWI-Prolog are in
the [absys](https://github.com/chrishayuk/absys) repository. They are not
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
