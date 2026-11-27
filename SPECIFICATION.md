# Specification

*Draft 0.6, 27 November 2026. Not frozen; the freeze candidate. Draft 0.1 was reviewed
independently; the findings and the response to each are in
[`reviews/`](reviews). Draft 0.3 added the decisions taken on draft 0.2
(`reviews/decisions-0.2.md`). Draft 0.4 answered the second review, of
draft 0.3 (`reviews/review-2.md`). Draft 0.5 applied the decisions on
draft 0.4 (`reviews/decisions-0.4.md`). Draft 0.6 answers the third review
(`reviews/review-3.md`). See `PROTOCOL.md` for how the specification is
frozen.*

## The question

**How do different computational models represent, retain and resolve
partially specified computations?**

A computation is *partially specified* when the information it needs has not
all arrived. Some of its unknowns have no value yet, some of its relations
have no definition yet, or some of its alternatives cannot yet be told
apart. This study poses the same partially specified problems to several
systems and records what each does with them.

The results are meant to map trade-offs along six dimensions of design, not
to rank systems:

| dimension | what it covers | problems that bear most on it |
|---|---|---|
| **information** | how incomplete knowledge is represented | P01, P02, P06, P07, P16 |
| **execution** | how computations become runnable: order, scheduling, suspension, resumption | P02, P04, P08, P13 |
| **state** | how information changes over time | P10, P14 |
| **search** | how alternatives are explored and retained | P03, P04, P05, P12 |
| **coordination** | how computations communicate and cooperate | P09, P14, P15, P16 |
| **commitment** | how tentative results become final, and irreversible actions | P11, P15 |

**Resources** cut across all six: retained state, recomputation, control
code, supporting code and intervention. Each metric in `METRICS.md` names
the dimension it measures, or resources.

## What this specification does not assume

None of the following is taken as true. Each is a question the results may
bear on:

- that declarative computation is better than imperative computation;
- that a fair search is better than a depth-first one;
- that suspending a computation is better than restarting it;
- that keeping alternatives alive is better than backtracking;
- that less explicit control code makes a better programming model;
- that information only ever accumulates. Some problems replace or
  retract information (P10).

Each design may have advantages under different limits of memory, time or
implementation effort.

## The problems

| | problem | what it probes |
|---|---|---|
| P01 | [unknown equality](problems/01-unknown-equality.md) | how a relation between unknowns is represented |
| P02 | [late information](problems/02-late-information.md) | whether a computation resumes when information arrives |
| P03 | [reversible relations](problems/03-reversible-relations.md) | whether one definition serves several directions |
| P04 | [unbounded alternative](problems/04-unbounded-alternative.md) | whether an endless alternative hides a finite one, in either order |
| P05 | [late contradiction](problems/05-late-contradiction.md) | how alternatives are kept and dropped as constraints arrive |
| P06 | [negation](problems/06-negation.md) | whether negation is sound while its unknowns are unknown |
| P07 | [simultaneous constraints](problems/07-simultaneous-constraints.md) | which sets of equations are solved, and how |
| P08 | [late definition](problems/08-late-definition.md) | what an application of a relation not yet defined means and does |
| P09 | [concurrent goals](problems/09-concurrent-goals.md) | independent computations, and computations that share information |
| P10 | [state replacement](problems/10-state-replacement.md) | values that change, relations that keep holding, information withdrawn |
| P11 | [irreversible effects](problems/11-irreversible-effects.md) | whether external actions are tied to committed outcomes |
| P12 | [large alternative space](problems/12-large-alternative-space.md) | the time and store of each search strategy |
| P13 | [deterministic scale](problems/13-deterministic-scale.md) | how bookkeeping grows with size, apart from search |
| P14 | [message stream](problems/14-message-stream.md) | a persistent process with state, answering between messages |
| P15 | [merge and committed choice](problems/15-merge-and-committed-choice.md) | interleaving, fairness and arbitration of a resource |
| P16 | [shared information at scale](problems/16-shared-information.md) | propagation, contributors, localised updates and contradiction in a large structure of relations |

The problems are stated in mathematical notation only. A definition's
numbered cases describe a relation; they are not a program, and a program
may express them in whatever form its language uses.

## How a problem is stated

Each problem file gives:

1. **Vocabulary.** The relations, with a definition by cases for every
   relation the problem uses that is not primitive.
2. **Stages.** The information initially available (stage 1), and each
   later piece of information, in the order it arrives. A problem of one
   stage is a query.
3. **Presentation order.** Where a definition or a conjunction has parts,
   the order in which they are written. Some systems' behaviour depends on
   it, so it is part of the problem. A program that changes it is
   *reformulated* (`METRICS.md`).
4. **Valid outcomes.** After every stage, the set of solutions that the
   information so far admits, under the semantics below and any reading the
   problem names.
5. **Observations.** What to record, beyond the common observations below.

## Conventions

### Values and names

- **Values** are integers, atoms and finite sequences of values.
- **Atoms** are written in small capitals, as ᴀ, ʙʀᴏᴡɴ, ᴄ101. In plain
  text they may be written with a leading quote: 'a, 'brown, 'c101.
- ⟨⟩ is the empty sequence, ⟨1,2⟩ a sequence of two, and a ++ b the
  sequence a followed by b. ++ is defined only on sequences.
- **Unknowns** are written in italic lower case where the format allows,
  and are never the same letters as an atom or a relation in the same
  problem. An unknown ranges over all values unless its problem says
  otherwise. Where a relation's case says "for every sequence b", b ranges
  over sequences only.
- **Relations** are written in lower case words: conc, rev, mem.

### Definitions

- A definition is a list of numbered cases. Each is a fact or an
  implication "r(…) if …", whose conjuncts are joined by *and* in the order
  written.
- A definition with no negation is read as the **least relation**
  satisfying its cases.
- A definition with negation is read under the **stratified** (perfect
  model) semantics. Negation is applied only to relations defined at a lower
  stratum, as every definition in this suite does.
- Where a problem says a relation is given by facts in a **closed world**,
  only the stated facts are true.
- Some problems also name a second reading, such as a stream reading over
  infinite sequences. There, the problem gives valid outcomes under each
  reading, and a result is classified under each separately.

### Arithmetic and comparison

The primitive vocabulary is +, −, · on integers, written as relations
(a + b = c holds of three integers; any place may be unknown), and the
comparisons =, ≠, <, ≤, >, ≥. Comparisons other than = and ≠ hold only of
integers. A compound expression such as x + y + z = 12 abbreviates a
conjunction of primitive relations with fresh unknowns. Writing it either
way, compound or decomposed, is a transcription of the problem
(`METRICS.md`, class P).

## Stages and monotonicity

A stage adds information to what came before it, unless the problem marks it
as **replacing** (a named quantity takes a new value) or **retracting**
(information given earlier is withdrawn), as P10 does. Two monotonicities
are distinguished:

- **Information monotonicity.** The stated information only grows. This
  holds in every problem except those that say they replace or retract.
- **Conclusion monotonicity.** Every conclusion a system reports stays
  valid once later information arrives. This does not follow from the first.
  Under a closed world, adding a definition or a fact can make a conclusion
  that was valid (no solutions; a negation true) invalid at the next stage.

The valid outcomes after stage k are always computed from the whole of the
information of stages 1 to k, under the problem's readings. Where they
contradict a valid outcome of an earlier stage, the problem file says so.
Each result records every reported conclusion that a later stage withdrew,
and how the system showed the withdrawal, if it did.

## Outcomes

Each stage of each run is classified on three axes, recorded separately,
and on a fourth, effects, in P11 only. A residual representation also
records its simplification (below).

Separately from the axes, **expressibility** is recorded once per
configuration and sub-problem (for a relation used in several directions,
once per direction), by one rule for every system:

| expressibility | meaning | the program of record |
|---|---|---|
| **expressible** | the problem's definitions can be transcribed | the transcription |
| **expressible with reformulation** | it cannot be transcribed, but a reformulation keeps the relation's meaning on every input the problem and its hidden variants use | the reformulation, with its R tokens counted |
| **not expressible** | only a reformulation that changes the meaning (dropping a guard the inputs depend on, for instance), or supporting code, can be written | none. Any such reformulation is run and reported as a named variant |

Both the classification and any named variant are always reported. That a
reformulation was needed is itself a result.

### 1. Semantic result

Judged on the set of solutions the report denotes, compared with the valid
outcomes.

| class | meaning |
|---|---|
| **complete** | the report denotes exactly the valid outcomes. Whether an empty set was reported as empty is recorded by simplification (*inconsistency undetected*) and by answer completeness |
| **partial** | the report denotes a nonempty proper subset of the valid outcomes. This includes a representation that drops solutions, such as a solver that restricts an unknown to integers when the problem lets it range wider |
| **unsound** | the report denotes an outcome that is not valid, or reports that there are none where valid outcomes exist |
| **undetermined** | the report consists of conditions whose equivalence to the valid outcomes the classifiers cannot establish |
| **none reported** | nothing was reported |

A system that reports one answer of several, for a query that asks for one
(*any one* queries, in later problems), is *complete* for that query.

**Correctness and simplification are kept apart.** A residual that is
equivalent to the valid outcomes is *complete*, however unreduced. How far
the system reduced it is recorded separately, as **simplification**:

| simplification | meaning |
|---|---|
| **reduced** | no smaller equivalent representation exists |
| **reducible** | a smaller equivalent representation exists, which the system did not reach |
| **inconsistency undetected** | the conditions denote the empty set, and the system has not reported that there are none |

One representation is smaller than another if it has fewer relations left
to decide, or the same number with fewer occurrences of unknowns. So:

- P02, stage 1: u + v = 16, held, is *complete* / *residual* / *reduced*.
- P07c: x + y = 10, held, is *complete* / *residual* / *reduced*.
- P07b: x + y = 10 and x − y = 4, held, is *complete* / *residual* /
  *reducible*, since x = 7, y = 3 is smaller.
- P07f: x + y = 10 and x + y = 11, held, is *complete* / *residual* /
  *inconsistency undetected*.

So a system that does nothing with a set of relations it cannot solve is
not marked wrong. Its simplification shows what it left undone, and is
compared alongside the semantic result.

A binding that the system holds is **reported** if the harness's
`observe()` can read it at the end of the stage, including at the moment
a budget runs out, whether or not the system's mechanism for answers
would deliver it (P09d2, P15b). The one exception is P09d1, whose finite
reading has no solution: there, a binding held while the producer still
runs is recorded as an observation, and the result is *none reported*.

### 2. Representation

| class | meaning |
|---|---|
| **explicit** | each solution is given as values |
| **solved form** | each unknown is either bound to a term built from values, unknowns, ⟨⟩ and ++, or free, or identified with another unknown, and no relation remains to be decided |
| **residual** | some relations remain to be decided. The residual conditions are recorded, with their size beside the size of the input |
| **cyclic** | a term that is not finite (a rational tree), presented as such |

Whether a residual is equivalent to the valid outcomes is checked by the
classifiers (`PROTOCOL.md`, Roles), by hand or by a published checking
script, with the reasoning recorded. Sizes of representations are measured
on the primitive decomposition (`Conventions`).

A residual counts as reported only if it is state that the system or the
program holds and acts on at a later stage, read by `observe()`. Printing
the posed information back is not a report. Beside simplification, a flag
records a residual **identical to the posed information**, so that a
system that held the relations and did nothing yet can be told apart from
one that transformed them.

### 3. Execution state

| class | meaning |
|---|---|
| **finished** | the system has stopped and holds no more work for this stage |
| **alternatives pending** | the system has stopped after an answer, and holds alternatives that a request for more answers would resume |
| **suspended** | the system has stopped, and holds work that later information may resume |
| **budget** | the step budget ran out (`PROTOCOL.md`). Nontermination is presumed, not proved |
| **timeout** | the harness's safety limit on time ran out before the budget did. The run is rerun once with the limit raised (`PROTOCOL.md`). Answers reported before the limit are classified on the semantic axis |
| **error** | the system stopped with an error, recorded verbatim |

A run may be both *alternatives pending* and *suspended*. Both are
recorded.

### 4. Effects

Only for problems with external effects (P11), a fourth axis
records whether the effects performed match the outcome committed to. P11
defines it.

## Observations common to every problem

After each stage, record:

1. the outcomes reported, verbatim, collected as `PROTOCOL.md` says;
2. the three classifications above;
3. how the unknowns that remain unknown are represented;
4. the alternatives the system holds, and whether they are all live at once
   or kept for backtracking, in the unit its systems file defines;
5. what the system holds as suspended or waiting work, in its own terms,
   and how many items;
6. the metrics of `METRICS.md` that apply to a stage;
7. any conclusion reported at an earlier stage that this stage withdrew;
8. any manual action needed to pose the stage.

## Disclosure: where the problems came from

P01–P08 were first run, in other forms, on a reconstruction of Absys
(1967–68), and most were chosen because Absys did something notable with
them. The reconstruction itself was developed while those experiments ran,
and some of its decisions were taken because of them
(`systems/absys/README.md`). The suite may therefore favour systems that
resemble Absys. Disclosure does not remove that, so:

- P07 includes cases that Absys is known or expected to handle badly.
- P10–P16 were added after review: state replacement, effects, large
  search spaces, scale, persistent processes, arbitration, and shared
  information at scale. These are
  problems where imperative, backtracking and concurrent designs are
  expected to do well, and Absys may do badly or not at all.
- The first comparison includes two imperative baselines (Python and
  ALGOL 60), so that the suite is not only a comparison of declarative
  systems.
- Retained state and recomputation are measured as costs. Each system's
  store is measured in its own units, which are not comparable. What is
  compared across systems is the **problem-defined quantities**, such as
  the alternatives a problem's own terms say are held, and the **growth
  exponent** of each system's store and steps as a problem's size grows
  (`METRICS.md`).
