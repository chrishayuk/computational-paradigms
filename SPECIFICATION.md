# Specification

*Draft 0.2, 26 November 2026. Not frozen. Draft 0.1 was reviewed
independently; the findings and the response to each are in
[`reviews/`](reviews). See `PROTOCOL.md` for how the specification is
frozen.*

## The question

**How do different computational models represent, retain and resolve
partially specified computations?**

A computation is *partially specified* when the information it needs has not
all arrived. Some of its unknowns have no value yet, some of its relations
have no definition yet, or some of its alternatives cannot yet be told
apart. This study poses the same partially specified problems to several
systems and records what each does with them.

The results are meant to map trade-offs along four dimensions, not to rank
systems:

| dimension | what it covers |
|---|---|
| **information** | unknowns, constraints, bindings, partial knowledge |
| **execution** | order, scheduling, suspension, resumption |
| **alternatives** | search, contradiction, backtracking, parallel derivations |
| **resources** | retained state, recomputation, control code, intervention |

Each metric in `METRICS.md` names the dimension it measures.

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

Problems proposed in review, P10 onwards, are listed in
[`problems/README.md`](problems/README.md) with their status. Which of them
are kept is decided before the freeze. None will be added after it to the
frozen suite (`PROTOCOL.md`).

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

Each stage of each run is classified on three axes, recorded separately.
Whether a problem can be written in a configuration at all is a fourth,
separate observation (*expressible*, or *not expressible without supporting
code*), made once per configuration and problem.

### 1. Semantic result

Judged on the set of solutions the report denotes, compared with the valid
outcomes.

| class | meaning |
|---|---|
| **complete** | the report denotes exactly the valid outcomes. Where the valid outcomes are empty, the system has reported that there are none |
| **partial** | the report denotes a nonempty proper subset of the valid outcomes. This includes a representation that drops solutions, such as a solver that restricts an unknown to integers when the problem lets it range wider |
| **unsound** | the report denotes an outcome that is not valid, or reports that there are none where valid outcomes exist |
| **undetermined** | the report consists of conditions the system has left unresolved, and either they are the problem's own relations essentially unreduced, or they denote the empty set and the system has not reported it empty |
| **none reported** | nothing was reported |

A system that reports one answer of several, for a query that asks for one
(*any one* queries, in later problems), is *complete* for that query.

### 2. Representation

| class | meaning |
|---|---|
| **explicit** | each solution is given as values |
| **solved form** | each unknown is either bound to a term built from values, unknowns, ⟨⟩ and ++, or free, or identified with another unknown, and no relation remains to be decided |
| **residual** | some relations remain to be decided. The residual conditions are recorded, with their size beside the size of the input |
| **cyclic** | a term that is not finite (a rational tree), presented as such |

Whether a residual is equivalent to the valid outcomes is checked by hand,
and the reasoning recorded.

### 3. Execution state

| class | meaning |
|---|---|
| **finished** | the system has stopped and holds no more work for this stage |
| **alternatives pending** | the system has stopped after an answer, and holds alternatives that a request for more answers would resume |
| **suspended** | the system has stopped, and holds work that later information may resume |
| **budget** | the step budget ran out (`PROTOCOL.md`). Nontermination is presumed, not proved |
| **timeout** | the harness's safety limit on time ran out before the budget did. The run is unclassified on the other axes, and is rerun |
| **error** | the system stopped with an error, recorded verbatim |

A run may be both *alternatives pending* and *suspended*. Both are
recorded.

### 4. Effects

Only for problems with external effects (P11, proposed), a fourth axis
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
- The problems proposed in review (P10 onwards) include revision, effects,
  large search spaces and scale, where other designs are expected to do
  well.
- Retained state and recomputation are measured as costs, with a
  comparable measure of peak store (`METRICS.md`).
