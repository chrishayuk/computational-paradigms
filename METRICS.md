# Metrics

*Draft 0.2. The classification rules below are frozen with the specification,
before any system is compared.*

Every metric is recorded per system, per configuration, per problem, and per
stage where it applies. Raw counts are kept beside every derived figure.
Counts in a system's own unit are compared within that system: across
stages, configurations and problems, not across systems. Across systems,
the comparable figures are the classifications, the qualitative
observations, and C, R and S tokens taken relative to P tokens.

## The metrics

| metric | dimension | definition |
|---|---|---|
| **problem tokens** | resources | tokens expressing the problem (class P below) |
| **control tokens** | execution | tokens specifying order, scheduling, suspension or search (class C) |
| **reformulation** | resources | tokens of definitions or arguments the problem does not give, and parts moved from the presentation order (class R) |
| **supporting code** | resources | code that provides a mechanism the configuration lacks (class S), counted once per mechanism per configuration, with the problems that use it listed |
| **external mechanisms** | resources | libraries, run-time features and extensions used beyond the core of the configuration, listed by name |
| **answer completeness** | information | see below |
| **answer latency** | execution | steps to the first valid answer, steps between successive answers, and steps to the end of the stage |
| **suspended state** | information | unresolved computations held, at each stage boundary and at their peak during the stage, in the system's terms, with a count |
| **retained alternatives** | alternatives | alternatives held, at each stage boundary and at their peak, in the unit the systems file defines |
| **peak store** | resources | the peak memory the computation holds during the stage, in the unit the systems file defines |
| **restart cost** | resources | for a system that cannot receive a stage into its existing computation: the steps of reposing stages 1 to k−1 |
| **repeated work** | resources | work done again inside one computation after new information: relations examined again, goals re-solved. Measured from a trace |
| **intervention** | resources | manual actions needed to make progress (see below) |

### Answer completeness

- Where the valid outcomes are finite and nonempty: valid answers obtained,
  over valid answers expected, with the count of invalid answers obtained
  beside it.
- Where they are empty: whether the system reported that there are none
  (yes or no).
- Where they are infinite: whether a finite representation equivalent to
  them was given (yes or no), and the answers obtained before the budget or
  the cap (`PROTOCOL.md`), listed.

## Tokens

A token is a lexical token of the language, as its own grammar defines it:
an identifier, a literal, an operator, a punctuation mark or a keyword.
Comments, whitespace and layout are not counted. Where layout is part of the
syntax (indentation, line ends), each significant layout element counts as
one token.

### Classing by construct

Tokens are classed by the construct they belong to, not one by one. A
construct is the smallest unit with a role in the program: a clause, a
goal, a declaration, a definition case, an argument. Every token of a
construct takes the construct's class, including its punctuation.

| class | what it covers |
|---|---|
| **P, problem** | the vocabulary and definitions as the problem file gives them; the information of each stage; the connectives that express them (conjunction, disjunction, negation, equality, arithmetic, comparison); the query |
| **C, control** | constructs that decide when or in what order: delay and key declarations, coroutine and freeze calls, cuts, tabling declarations, search and labelling directives, generators of values the problem does not state (between/3, for instance), explicit scheduling, priority or fairness annotations, engine and thread calls |
| **R, reformulation** | definitions, cases and extra arguments the problem file does not give (an accumulator, for instance); a relation computed in one chosen direction where the problem states it as a relation |
| **S, supporting** | code that implements a mechanism the configuration lacks: a meta-interpreter, a wait-for-definition layer, a hand-written scheduler |
| **H, harness** | the per-system harness's own calls (posing stages, requesting answers, printing), which `PROTOCOL.md` fixes before any run |

### Rules

1. **Reference semantics.** A construct is P if removing it would change the
   declarative meaning of the program, that is the set of solutions under the
   semantics of `SPECIFICATION.md`. It is C if removing it would change
   only operational behaviour: order, termination, floundering, errors,
   efficiency.
2. A construct that changes both (a red cut, a guard that also orders) is
   C, and is listed in the results.
3. Moving a definition case or a conjunct away from the presentation order
   adds no tokens. Each move counts as one move, under reformulation.
4. An extra argument added for efficiency is R, even if the program is then
   shorter.
5. A disjunction or a set of facts that the problem states is P. An
   enumeration that the problem does not state is C.
6. A comprehension or aggregation construct that states a definition the
   problem gives (a set former for setdiff, for instance) is P, the same as
   a transcription of the definition by cases.
7. Writing an arithmetic relation as an evaluation in one direction (a
   value computed from the others) is R, plus one move if it forces a
   reordering. Where the configuration cannot state the relation in more
   than one direction at all, the program for that direction is recorded
   under *not expressible* for the other directions.
8. A built-in of the configuration's core is counted as its call tokens. A
   library outside the core is counted the same way, and is also listed
   under external mechanisms. Code written for the experiment is S,
   wherever it is kept, counted once per mechanism per configuration.
9. Code in the harness beyond the fixed harness calls is not H. It is
   classed as C or S by these rules.

### Two classifiers

Each program is classed independently by two classifiers, who are named,
are not the program's author, and are not shown each other's classes. For
every token, both classes are kept. Totals are reported per classifier, so
that each classifier's classes add up to the same total of tokens, together
with the count of disputed tokens and the constructs they belong to. No rule
is added after the freeze except by a versioned amendment applied to every
system (`PROTOCOL.md`).

## The core of a configuration

The core is the language as its defining document describes it, for the
evidence class of the implementation (`PROTOCOL.md`). Each systems file
lists its configurations' cores exactly, built-in by built-in, and the
flags that change their meaning. Anything used beyond the core is listed
under external mechanisms, even if the implementation ships it.

A mechanism a library provides is therefore never counted as native. A
twelve-line suspension layer appears as twelve lines' worth of S. A
suspension that a library provides appears as an external mechanism.
Native suspension appears as neither.

## Steps and store

Each systems file names, before the freeze, the unit of steps (derivation
steps, inferences, reductions), the unit of an alternative, and the unit of
store, and how each is measured. They are not chosen afterwards. Wall-clock
time is not a metric.

## Restart cost and repeated work

The two are kept apart. Neither alone establishes how much work was done
twice.

- **Restart cost**, for a system that cannot receive stage k into its
  existing computation, is the step count of running stages 1 to k−1
  alone, measured, since those steps are spent again when stages 1 to k are
  posed together.
- **Repeated work**, for any system, is counted from a trace: the number of
  times a relation, goal or constraint already examined is examined again
  after new information arrives, and the steps those examinations take.
- For every stage, both the *incremental cost* (steps from the end of stage
  k−1 to the end of stage k, where the system allows it) and the *restated
  cost* (steps from nothing to the end of stage k) are recorded beside them.

## Intervention

An intervention is an action by a person, or by harness code written for one
problem, that the fixed harness does not perform. Each is counted per
stage:

- restarting after an error;
- choosing by hand which of several pending computations runs;
- reordering the program between stages;
- adding a control declaration tailored to one stage.

The harness reposing earlier stages automatically, for a system that cannot
receive stages incrementally, is not an intervention. It is counted under
restart cost.
