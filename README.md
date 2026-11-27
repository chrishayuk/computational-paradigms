# computational-paradigms

A comparative study of computational models. The study asks:

> **How do different computational models represent, retain and resolve
> partially specified computations?**

The same sixteen problems are posed to each system, most of them in stages. A stage
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

**Draft 0.6, the freeze candidate. No system has been compared.**

- Draft 0.1 was reviewed independently. Draft 0.2 answered every finding
  ([`reviews/review-1.md`](reviews/review-1.md)). Draft 0.3 applied the
  decisions on its open questions
  ([`reviews/decisions-0.2.md`](reviews/decisions-0.2.md)). A second,
  fresh review of draft 0.3 was answered in draft 0.4
  ([`reviews/review-2.md`](reviews/review-2.md)), and the decisions on it
  in draft 0.5 ([`reviews/decisions-0.4.md`](reviews/decisions-0.4.md)).
  A third review, of draft 0.5, is answered in draft 0.6
  ([`reviews/review-3.md`](reviews/review-3.md)). Draft 0.7 is the freeze
  candidate: it fixes the pins ([`PINS.md`](PINS.md)), the ALGOL 60 step,
  the assessment of hidden variants, and three clarifications from the
  held-out check.
- The classification rules have been calibrated on P03 and P13 in all four
  systems, by two independent classifiers
  ([`calibration/`](calibration)), and checked on a held-out problem, P02
  in Python and ALGOL 60 ([`calibration/held-out/`](calibration/held-out)).
  The calibration programs are development examples, not results.
- Nothing is frozen.
- No programs have been written for this study.

Programs come after the freeze (`PROTOCOL.md`).

## Contents

| file | what it is |
|---|---|
| [`SPECIFICATION.md`](SPECIFICATION.md) | the question, the conventions, the classes of outcome, and what is not assumed |
| [`problems/`](problems) | the sixteen problems, in mathematical notation, with their valid outcomes |
| [`METRICS.md`](METRICS.md) | what is measured, and the frozen rules for classing tokens |
| [`PROTOCOL.md`](PROTOCOL.md) | phases, amendments, evidence classes, configurations, how programs are written, run and recorded |
| [`PINS.md`](PINS.md) | the version or commit of every system, fixed at the freeze |
| [`systems/`](systems) | each system's configurations and evidence class |
| [`calibration/`](calibration) | the checks of the classification rules: development examples, not results |
| [`variants/`](variants) | the sealed hidden variants, one set per wave |
| [`tools/`](tools) | the hygiene check, and the script that seals the variants |
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
