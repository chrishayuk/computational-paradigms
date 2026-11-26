# Specification

*Draft 0.1, 26 November 2026. Not frozen. See `PROTOCOL.md` for how it is
reviewed and frozen.*

## The question

**How do different computational models represent, retain and resolve
partially specified computations?**

A computation is *partially specified* when the information it needs has not
all arrived. Some of its unknowns have no value yet, some of its relations
have no definition yet, or some of its alternatives cannot yet be told
apart. This study poses the same partially specified problems to several
systems and records what each does with them.

## What this specification does not assume

None of the following is taken as true. Each is a question the results may
bear on:

- that declarative computation is better than imperative computation;
- that a fair search is better than a depth-first one;
- that suspending a computation is better than restarting it;
- that keeping alternatives alive is better than backtracking;
- that less explicit control code makes a better programming model.

Each design may have advantages under different limits of memory, time or
implementation effort. Nothing here ranks the systems. The results record
behaviour and cost.

## The problems

| | problem | what it probes |
|---|---|---|
| P01 | [unknown equality](problems/01-unknown-equality.md) | how a relation between unknowns is represented |
| P02 | [late information](problems/02-late-information.md) | whether a computation resumes when information arrives |
| P03 | [reversible relations](problems/03-reversible-relations.md) | whether one definition serves several directions |
| P04 | [unbounded alternative](problems/04-unbounded-alternative.md) | whether an endless alternative hides a finite one |
| P05 | [late contradiction](problems/05-late-contradiction.md) | how alternatives are kept and dropped as constraints arrive |
| P06 | [negation](problems/06-negation.md) | whether negation is sound while its unknowns are unknown |
| P07 | [simultaneous constraints](problems/07-simultaneous-constraints.md) | which systems of equations are solved, and how |
| P08 | [late definition](problems/08-late-definition.md) | what happens to an application of a relation not yet defined |
| P09 | [concurrent goals](problems/09-concurrent-goals.md) | independent computations, and computations that share information |

The problems are stated in mathematical notation only. No problem file
contains the syntax of any programming language.

## How a problem is stated

Each problem file gives:

1. **Vocabulary.** The relations, with their definitions where a definition
   is part of the problem.
2. **Stages.** The information initially available (stage 1), and each
   later piece of information, in the order it arrives.
3. **Presentation order.** Where a definition or a conjunction has parts,
   the order in which they are written. Some systems' behaviour depends on
   it, so it is part of the problem. A program that changes it is
   *reformulated* (`METRICS.md`).
4. **Valid outcomes.** After each stage, the set of solutions that the
   information so far admits, under the semantics stated in the problem.
5. **Observations.** What to record after each stage, beyond the common
   observations below.

## Conventions

- **Values.** Integers, the atoms named in a problem, and finite sequences
  of these. ⟨⟩ is the empty sequence, ⟨1,2⟩ a sequence of two, and a ++ b
  the sequence a followed by b.
- **Unknowns** are written in lower case: x, y, s. They range over the
  values unless a problem says otherwise.
- **Relations** are written r(a, b). A definition is a list of numbered
  cases, each one an equation or an implication "r(…) if …", read as the
  least relation satisfying them. Where a problem uses a closed world (only
  the stated facts are true), it says so.
- **Arithmetic** is on the integers. a + b = c and a · b = c are relations,
  not functions: any of the three places may be unknown.
- A **stage** adds information to what came before. It does not replace it.

## Outcomes

Each run of a stage is classified on two axes, recorded separately.

**What is reported:**

| class | meaning |
|---|---|
| complete | exactly the valid outcomes, as explicit values or as an equivalent finite representation |
| residual | a representation with conditions left unresolved (suspended equations, residual constraints) that is equivalent to the valid outcomes; the conditions are recorded |
| partial | some valid outcomes, and no invalid ones, but not all |
| none | nothing reported |
| unsound | an outcome that is not valid, or "no solutions" where valid outcomes exist |
| not expressible | the problem cannot be written in the system's configuration without supporting code |

Whether a residual representation is equivalent to the valid outcomes is
checked by hand and the reasoning recorded.

**How the computation stands:**

| class | meaning |
|---|---|
| finished | the system has stopped and holds no more work for this stage |
| suspended | the system has stopped, and holds work that later information may resume |
| budget | the step budget ran out (`PROTOCOL.md`); nontermination is presumed, not proved |
| error | the system stopped with an error |

A system may report a partial answer and then exhaust its budget. That is
recorded as *partial* with *budget*.

## Observations common to every problem

After each stage, record:

1. the outcomes reported, verbatim;
2. the two classifications above;
3. how the unknowns that remain unknown are represented;
4. how many alternatives the system holds, and whether they are all live at
   once, or one is live and the others are kept for backtracking;
5. what the system holds as suspended or waiting work, in its own terms,
   and how many items;
6. the steps used, in the system's own unit (`METRICS.md`);
7. any manual action needed to pose the stage (`METRICS.md`,
   intervention).

## Disclosure: where the problems came from

Most of these problems were first run on a reconstruction of Absys (1967–68),
and most of them were chosen because Absys did something notable with them.
The suite may therefore favour systems that resemble Absys. To offset this:

- P07 and P09 include cases that Absys is known, or expected, to handle
  badly or not at all.
- `METRICS.md` measures retained state and recomputation, which are costs
  of the Absys design as much as benefits.
- The review in `PROTOCOL.md` is asked specifically to look for problems
  missing from the suite: those a backtracking or an imperative system
  handles well and an assertional one does not.
