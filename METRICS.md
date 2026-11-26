# Metrics

*Draft 0.1. The classification rules below are frozen with the specification,
before any system is compared.*

Every metric is recorded per system, per configuration, per problem, and
per stage where it applies. Raw counts are kept beside every derived figure.

## The metrics

| metric | definition |
|---|---|
| **problem tokens** | tokens expressing the domain facts, the relations and the query (class P below) |
| **control tokens** | tokens specifying order of execution, scheduling, suspension or search (class C) |
| **reformulation** | tokens of auxiliary relations or changed definitions not in the problem file, and the number of parts moved from the presentation order (class R) |
| **supporting code** | code that provides a computational mechanism the configuration lacks, counted per mechanism (class S) |
| **external mechanisms** | libraries, run-time features or extensions used beyond the core of the configuration (see below), listed by name |
| **answer completeness** | valid outcomes obtained over valid outcomes expected; for infinite sets, whether a finite equivalent representation was given |
| **suspended state** | the unresolved computations held at each observation point, counted in the system's terms and described in words |
| **retained alternatives** | the alternatives held at each observation point, and whether live or kept for backtracking |
| **recomputed work** | work done before a stage that is done again after it (see below) |
| **intervention** | manual actions needed to make progress (see below) |

## Tokens

A token is a lexical token of the language, as its own grammar defines it:
an identifier, a literal, an operator, a punctuation mark or a keyword.
Comments, whitespace and layout are not counted. Where layout is part of the
syntax (indentation, line ends), each significant layout element counts as
one token and is classed with the construct it belongs to.

Every token is given exactly one class.

| class | what it covers |
|---|---|
| **P, problem** | the vocabulary and definitions as the problem file gives them; the information of each stage; the connectives that express them (conjunction, disjunction, negation, equality, arithmetic); the query |
| **C, control** | anything that says when or in what order: delay and key declarations, coroutine and freeze calls, cuts, search or labelling directives, explicit scheduling, priority or fairness annotations, engine calls, explicit enumeration of alternatives |
| **R, reformulation** | auxiliary relations, extra arguments (an accumulator, for instance) and changed definitions that the problem file does not give |
| **S, supporting** | code that implements a mechanism the configuration lacks: a meta-interpreter, a wait-for-definition layer, a hand-written scheduler. Counted per mechanism |
| **H, harness** | posing stages, reading input, printing results, budgets and timing. Counted but excluded from comparisons |

Rules for cases that are hard to class:

1. A token is P if deleting it would change *what* is computed, and C if
   deleting it would change only *when*, *in what order* or *whether in
   time* it is computed.
2. A token that does both (a guard that also orders, for instance) is C,
   and the case is listed in the results.
3. Moving a clause or conjunct away from the presentation order adds no
   tokens. Each move is counted under reformulation as one move.
4. An extra argument added for efficiency is R, even if the program is
   then shorter.
5. A built-in that the configuration's core provides is counted as its call
   tokens only. A library outside the core is counted the same way, and is
   also listed under external mechanisms. Code written for the experiment
   is S, token by token, wherever it is kept.
6. Code that only exists to pose a stage to a system that cannot receive
   information incrementally is H, and the restating of earlier stages is
   counted under intervention.

Each program is classed independently by two classifiers. Their
disagreements are counted and reported. A disputed token is reported under
both classes. No rule is added after the freeze except by a versioned
amendment applied to every system (`PROTOCOL.md`).

## The core of a configuration

The core is the language as its defining document describes it, for the
evidence class of the implementation (`PROTOCOL.md`). For example, the core
of the Prolog configuration *plain* is ISO Prolog: unification, resolution
in textual order with backtracking, the cut, negation as failure, findall
and arithmetic evaluation. Coroutining is not in that core. Anything used
beyond the core is listed under external mechanisms, even if the
implementation ships it.

So a mechanism a library provides is never counted as native. A twelve-line
suspension layer appears as twelve lines of S. A suspension a library
provides appears as an external mechanism. Native suspension appears as
neither.

## Steps

Steps are counted in the system's own unit: derivation steps, inferences,
reductions, machine instructions. The unit is recorded with every count.
Counts are compared within a system, across stages and configurations, and
not across systems. Wall-clock time is not a metric.

## Recomputed work

For a stage k:

- *incremental cost*: steps from the end of stage k−1 to the end of stage
  k, when the system receives the stage into the same computation;
- *restated cost*: steps to reach the end of stage k from nothing, given
  stages 1 to k together.

Recomputation is recorded when the system cannot receive stage k into the
same computation, and must be given stages 1 to k again; the steps of
repeating stages 1 to k−1 are the recomputed work. Where it can, both costs
are recorded, since an incremental system may also redo work internally (a
relation examined again after a binding, for instance).

## Intervention

Each of these is one intervention, counted per stage:

- restating information given at an earlier stage;
- restarting after an error;
- choosing by hand which of several pending computations runs;
- reordering the program between stages;
- adding a control declaration tailored to one stage.
