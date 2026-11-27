# Metrics

*Draft 0.5. The classification rules below are frozen with the specification,
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
| **answer completeness** | information, search | see below |
| **answer latency** | execution | steps to the first valid answer, steps between successive answers, and steps to the end of the stage |
| **suspended state** | execution | unresolved computations held, at each stage boundary and at their peak during the stage, in the system's terms, with a count |
| **retained alternatives** | search | alternatives held, at each answer, at each stage boundary, when the budget runs out, and at their peak, in the unit the systems file defines |
| **peak store** | resources | the store the computation holds during the stage, as a vector of quantities the systems file defines, each with its current value at the stage boundary and its peak during the stage. Where a true peak cannot be measured, the sampled maximum is reported and labelled as such |
| **restart cost** | resources | for a system that cannot receive a stage into its existing computation: the steps of reposing stages 1 to k−1 |
| **repeated work** | resources | work done again inside one computation after new information: relations examined again, goals re-solved, name parameters re-evaluated. Each systems file names its source for the count, or says it is not measured |
| **problem operations** | resources | applications of each case of each relation the problem defines, counted in the problem's own terms (below). Comparable across systems |
| **problem-defined alternatives** | search | alternatives held, in the problem's own terms (below). Comparable across systems |
| **intervention** | resources | manual actions needed to make progress (see below) |
| **effects** | commitment | P11's effects class, and when each effect was performed |
| **coordination** | coordination | in P09, P14 and P15: whether computations progressed independently, what they waited on, and how arbitration was decided |

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
   meaning of the program: for a declarative program, the set of solutions
   under the semantics of `SPECIFICATION.md`; for an imperative program,
   the values it reports for the queries the problem poses. It is C if
   removing it would change only operational behaviour: order,
   termination, floundering, errors, efficiency. Where this rule and rule
   5 disagree, rule 5 decides.
2. A construct that changes both (a red cut, a guard that also orders) is
   C, and is listed in the results. But a **guard** that tests only its
   case's own head (the pattern or condition the problem's case states) is
   P. This is the head test of a committed-choice clause, a pattern match,
   or an `if` that dispatches on the case. Only synchronisation or
   commitment beyond that is C.
3. **Mode-faithful transcription is P.** A function or procedure that
   computes exactly the directions the problem's queries use, with one
   branch per case of the definition, transcribes the definition. Its case
   dispatch (`if not a:`, a match on the head) is P. R covers only:
   - arguments or cases the problem does not give;
   - a changed algorithm;
   - a direction the queries do not use.

   So `conc(a, b)` in Python, returning a followed by b by the problem's
   two cases, is P for P03a. The same function offered for P03b, where
   conc is used to split a sequence, is *not expressible* in that
   direction, or R if the program writes a separate splitting function.
4. Moving a definition case or a conjunct away from the presentation order
   adds no tokens. Each move counts as one move, under reformulation.
   Likewise, a guard, case or conjunct of the problem left out of a
   program counts as one **omission**, under reformulation. The tokens that
   introduce and close the case it is missing from are R. The case's
   unchanged contents are classed on their own (rule 10).
5. An extra argument added for efficiency is R, even if the program is then
   shorter.
6. A disjunction or a set of facts that the problem states is P. An
   enumeration that the problem does not state is C.
7. A comprehension or aggregation construct that states a definition the
   problem gives (a set former for setdiff, for instance) is P, the same as
   a transcription of the definition by cases.
8. Writing an arithmetic relation as an evaluation in one direction is P
   where that direction is the one the query uses (rule 3), and R where the
   problem needs the relation in a direction the evaluation does not
   serve, plus one move if it forces a reordering.
9. **Built-ins in place of defined relations.** Using a built-in instead of
   a relation the problem defines (memberchk/2 or Python's `in` for mem;
   `sum` for sum) is P if it is equivalent in the directions used, and R
   otherwise. Either way it is listed, since it may hide the problem's
   operations from the step count.
10. **Nested constructs.** The tokens that introduce a construct (a loop
    header, an if-then-else's condition and connectives) take its class.
    The constructs inside it are classed on their own.
11. **Declarations that change failure.** A declaration that changes how an
    undefined relation behaves (`:- dynamic`, the `unknown` flag) is C, and
    is listed, since it chooses a reading of P08.
12. A built-in of the configuration's core is counted as its call tokens. A
   library outside the core is counted the same way, and is also listed
   under external mechanisms. Code written for the experiment is S,
   wherever it is kept, counted once per mechanism per configuration. S is
   reported apart from the per-problem ratios of C and R to P.
13. Code in the harness beyond the fixed harness calls is not H. It is
    classed as C or S by these rules, with one exception. **Output
    adapters** are H, however long they are: code whose only effect is to
    print, or collect for the harness, answers the program has already
    computed. That covers a printer that walks an encoded sequence, a
    callback that prints an answer, and a stand-in for the fixed harness
    calls. Code that computes anything the report depends on is not an
    adapter.
14. **A separately written function for a direction** (rule 3) is R
    throughout, its case-head tests included. Rule 2's exemption for head
    tests applies to transcriptions of the problem's own cases, not to a
    function written because a transcription cannot run in that direction.
15. **Operations on an encoding are part of the encoding.** Where a systems
    file defines an encoding as P, the operations the problem's relations
    need on encoded values (construction, decomposition, equality) are P.
    A general mechanism beyond the problem's relations, such as a unifier
    or a search, is S.
16. **A reset that only lets store be reused** is C, since removing it
    changes what is held, not what is computed (rule 1).
17. **Docstrings are comments,** and are not tokens.
18. In P13, a **native** algorithm is not reformulation (the problem says
    so). Its tokens are P. Where a system has only one way to compute a
    task, its native and prescribed programs are the same, and are
    recorded once.

### Two classifiers

**Calibration.** Before the freeze, programs for P03 and P13 are written in
each system of the first comparison, Python and ALGOL 60 included, and both
classifiers class them. They are **development examples, not results**.
They test whether the rules give consistent classes across different
styles of program, where the rules are hardest. The calibration record
(`calibration/`) gives:

- both classifiers' classes, token by token;
- the rate of agreement, per system and per class;
- the constructs that caused disagreement;
- whether the disagreements fall more on one paradigm than another;
- any amendment to the rules that resulted.

The first calibration, of draft 0.5, is recorded in
[`calibration/README.md`](calibration/README.md). Its disagreements fell
almost all on imperative code, and rules 4 and 13–18 come from it.

The rules are amended only to make classifications more defensible, never
to make the systems' totals come out more alike.

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
time is not a metric, with one exception: in P13 only, process CPU time and
the operating system's maximum resident set size are recorded as secondary
measures of **growth**, since a built-in can do work that no step count
sees. They are used only for the growth exponent, never as counts.

## Quantities comparable across systems

Each system's own units are compared within that system only. Across
systems, these quantities are compared, because each problem defines them
in its own terms:

- **Problem operations.** The applications of each case of each relation
  the problem defines. In the prescribed tasks of P13, they are fixed by
  the definitions: for example, rev on a sequence of n makes n(n+1)/2
  applications of conc's cases beyond those of rev itself. A system that
  makes more has done work the problem does not ask for. A program counts
  them with counters that are harness code (H), or by instrumentation.
- **Problem-defined alternatives.** In P05, the values of x still held. In
  P12, the candidates examined (sequences s for which accept(s) is
  evaluated) and the partial sequences held, live or kept for
  backtracking. In P15a, the interleavings held.
- **Growth.** For a problem with a size parameter (P12's n, P13's n,
  P16's n), steps, problem operations and each store quantity are fitted,
  within each system, by three models: linear (a·n), polynomial (a·nᵏ) and
  exponential (a·cⁿ). Each fit is reported, with its residuals, and the
  model that fits best is named. The fitted forms and parameters are
  compared across systems; the counts are not. P12 is expected to be
  exponential for some strategies, and is not forced into a power law.
  Three sizes are evidence of how a cost grows over that range. They do
  not establish its asymptotic complexity, and no result says they do.

## Restart cost and repeated work

The two are kept apart. Neither alone establishes how much work was done
twice.

- **Restart cost**, for a system that cannot receive stage k into its
  existing computation, is the step count of running stages 1 to k−1
  alone, measured, since those steps are spent again when stages 1 to k are
  posed together.
- **Repeated work** is counted from a source each systems file names: the
  number of times a relation, goal or constraint already examined is
  examined again after new information arrives, and the steps those
  examinations take. For Absys, the trace. For ALGOL 60, the
  `name_repeat_evaluations` count of its measurement build. For SWI-Prolog and
  Python, only problem operations counted by the program; the debugger is
  not used, because it changes the inference count.
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
