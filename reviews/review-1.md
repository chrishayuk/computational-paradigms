# Review 1, of draft 0.1

*26 November 2026.*

This draft had two reviews:

- **A**: an independent review by a model agent with a fresh context. It
  read every file and modified none. Its 46 findings are numbered as it
  gave them.
- **U**: points raised by the project's owner on reading draft 0.1, given
  separately and marked U1–U5.

Each response says what draft 0.2 does. *Accepted* means changed as
proposed. *Adapted* means changed, differently. *Open* means it needs a
decision before the freeze.

The reviewer found no wrong final answer in any problem. Its findings are
about edge cases, classification, protocol and bias.

## The outcome classes

| finding | in short | response |
|---|---|---|
| A7, U1 | complete and residual overlap, and a system that does nothing can be *residual* | Adapted. There are now three axes: semantic result, representation and execution state. *Undetermined* covers a residual that is the input unreduced, or one that hides an inconsistency |
| A8, U1 | a correctly reported empty set has no class | Accepted. It is *complete*; *none reported* is kept for silence |
| A10 | open choicepoints are neither finished nor suspended | Accepted. A new state, *alternatives pending* |
| A13 | is a cyclic answer unsound? | Adapted. P01c has two readings, finite and rational. A cyclic answer is *complete* under the rational one and *unsound* under the finite one |
| A17 | a typed solver that drops solutions | Accepted. It is *partial* |
| U1 | add timeout as a state | Accepted. A timed-out run is unclassified, and is rerun |
| A44 | effects | Accepted, as a fourth axis applied only to P11 |

## Mathematics and semantics

| finding | in short | response |
|---|---|---|
| A1 | conc's case 1 admits non-sequences | Accepted. "for every sequence b"; the same for mem |
| A2 | P02 after stage 2 is ten triples, not infinite | Accepted, and checked by enumeration. The ten are listed, with the outcome after every subset of relations for P02b |
| A3 | "least relation" is undefined with negation | Accepted. Stratified semantics |
| A4, U5 | P08's closed reading breaks the monotone stage rule | Adapted. The specification now separates information monotonicity from conclusion monotonicity, and every result records withdrawn conclusions. P08 lists four meanings of an undefined relation, and gives outcomes for every stage under both readings |
| A5, A34, U2 | P09d has no class for a stream consumer, and the finite domain penalises dataflow | Accepted. P09d1 (finite, least relation) and P09d2 (stream, greatest relation, where total = 6 is complete) |
| A6 | the arithmetic used is wider than the vocabulary given | Accepted. Primitive vocabulary listed; compound expressions abbreviate conjunctions and count as P either way |
| A14 | atoms and unknowns share letters | Accepted. Atoms in small capitals; colliding names changed (pick, rest, total, p, k) |
| A15 | setdiff, nonmajor and sum3 are given by meaning only | Accepted. Definitions by cases; a set former stating the same definition is P |
| A16 | "built one element at a time" is behaviour | Accepted. Removed |

## Protocol

| finding | in short | response |
|---|---|---|
| A9 | what "reported" means for on-demand answers, and observation that consumes the computation | Accepted. A fixed harness interface with a cap of 20 answers; observation on a separate run where it would consume the computation |
| A11 | budget and error between stages | Accepted. Budget per stage and per computation; after budget or error the next stage is posed by reposing |
| A12 | P09 can be passed by running two processes | Accepted. One instance and one database; concurrency is a mechanism of the configuration; the harness may not run computations concurrently |
| A19 | control can hide in the harness | Accepted. A generic harness interface, fixed with the freeze; any other harness code is C or S |
| A29 | the Absys reconstruction is not frozen, and was built alongside the problems | Accepted. Pinned at the freeze, with later commits as new configurations. The decisions taken because of the precursor experiments are listed in `systems/absys/README.md` |
| A38 | qualifiers used but not defined | Accepted. Two qualifiers defined |
| A41 | problems added after results are seen | Accepted. A separate, dated supplementary suite |
| A42 | transcription errors, precursor exposure, choice among idioms | Accepted, all three |

## Metrics

| finding | in short | response |
|---|---|---|
| A18, U4 | P versus C needs a reference semantics, and tokens should be classed by role | Accepted. Declarative meaning is the reference, and constructs are classed as wholes |
| A20 | units can be chosen afterwards | Accepted. Each systems file names its units now. Two remain open (below) |
| A21 | reposing is counted twice, as harness and as intervention | Accepted. Automated reposing is restart cost only; intervention is manual or problem-specific |
| A22, U4 | retained state is not comparable; memory only at boundaries | Accepted. Peak store and peak retained alternatives during a stage, in named units |
| A23, U4 | recomputation has no formula, and restarting is not repeated work | Accepted. Restart cost and repeated work are separate metrics, each defined |
| A24 | completeness ratio undefined for empty or infinite sets | Accepted |
| A25 | S counted two ways | Accepted. Once per mechanism per configuration |
| A26, U4 | disputed tokens counted twice | Accepted. Both classifiers' classes are kept per token, and each classifier's totals add up |
| A27 | P tokens compare syntax | Accepted. C, R and S are compared relative to P; one Absys notation fixed per problem |
| A28 | enumeration versus disjunction | Accepted. Rules 5 and 6, with examples |
| U4 | answer latency | Accepted. A new metric |

## Bias

| finding | in short | response |
|---|---|---|
| A30 | no tabling configuration for Prolog; clpq is over rationals | Accepted. A *tabling* configuration; clpq judged on integers |
| A31 | the plain core is misstated | Accepted. Built-ins and flags listed |
| A32, U3, A43 | every stage adds information | Accepted. Replacing and retracting stages; P10 proposed and written |
| A33 | no case where clause order favours depth-first | Accepted. P04e and P04f, right-recursive with the base case first |
| A35 | leftover language terms | Accepted. "elaboration", "system" of equations and `as` replaced |
| A36 | imperative systems are disclaimed but not included | **Open** |
| A37, A44–A46, U3 | missing problems | P10, P11 (reduced) and P12 written; P13–P15 summarised; retries dropped. **Which are kept is open** |
| A39, A40 | README mismatches and a garbled sentence | Accepted |

## Open before the freeze

1. Which of P10–P15 are kept.
2. Whether an imperative baseline system is added, and which.
3. The unit of store for Absys. Measuring it at its peak needs an
   instrumentation-only change to the absys repository, which is on hold.
4. How SWI-Prolog choicepoints and peak store are measured.
5. A second review of draft 0.2.
