# Absys

**Evidence class: reconstructed.** No Absys implementation survives. The
system used is the reconstruction in https://github.com/chrishayuk/absys,
built from Foster (1968), Foster and Elcock (1969), Elcock (1982) and
Elcock (1990). Every rule it follows, and the evidence for each, is in its
`docs/decisions.md`.

## Pinning

The commit used is fixed when the specification is frozen. It is
provisionally `7bb61e6`, whose CI passed. Any later change to the
reconstruction, for whatever reason, makes a new configuration, reported
separately beside the pinned one. Mechanisms added after the freeze are
never counted as native in the pinned configuration.

## Decisions taken while the precursor experiments ran

The reconstruction was built while the experiments E01–E09 ran. P01–P08
come from those experiments. These rules of the machine were set or changed
because of them:

| rule in `docs/decisions.md` | what it decides | prompted by |
|---|---|---|
| 10 | a primitive relation returns for each of its variables bound, to the head of the list | Elcock 1982's printed list (E06), the precursor of P02 |
| 15 | an applied body takes the place of its literal | setdiff under first-in first-out selection (E02), the precursor of P06d |
| 18, 19 | a `not` or `set` that cannot yet be decided waits and is run again | permuting the student and setdiff texts (E02, E03), the precursors of P06 and P08 |
| 6 | an application of an identifier with no value waits for it, and outside a lambda every identifier is shared by the whole text | E90 p. 10 for the waiting; the sharing across the whole text was made general when permuting E03, the precursor of P08 |

Results on P02, P06 and P08 should be read with this in mind. Rules 10 and
15 rest on readings of the sources that the experiments helped to choose;
rules 6, 18 and 19 are partly decisions where the sources are silent.

## Configurations

| configuration | what it is | class |
|---|---|---|
| **absys** | the reconstruction's defaults | reconstructed |
| absys-depth-first | `--search depth-first`: the backtracking reading of Elcock (1982) | reconstructed, alternative reading |
| absys-wake-back | `--wake back`: returned relations appended, as the word of Elcock (1982) says | reconstructed, alternative reading |

## The core

The machine as `docs/decisions.md` describes it, in the pinned commit:
equality as a process, with suspension of equations between unknowns;
`lambda` procedures applied in any direction; `or`, distributed into
derivations; `not` and `set`; `key`; arithmetic as relations over
integers, taken up when two of three values are known; `tout`; and the
incremental acceptance of assertions. Nothing else exists to be imported,
so every Absys configuration has no external mechanisms.

## Notation

Absys is known in three notations: Absys 1 (1969), the 1982 paper's, and
the 1990 retrospective's. Absys 1 has arithmetic, and the 1990 notation has
`not` and `set`. The notation for each problem is fixed by a rule, not
chosen: the **earliest** notation that has every construct the problem
needs. A problem that needs constructs found in no single notation is
recorded as such, with the notation used.

**No notation has comparisons.** Absys's arithmetic is +, −, · and ÷ as
relations. None of its three notations has <, ≤, > or ≥, as calibration
found. So P13's range, guarded by m > n and m ≤ n, and every problem that
uses a comparison (P05, P11, P12, P15d), are *not expressible* in Absys as
transcriptions. A reformulation without the comparison may be written,
and is reported as a named variant, never as the program of record.

**Output.** The reconstruction prints at most 32 elements of a list, in
every mode, so `observe()` cannot read a longer answer. Printing in full
needs an instrumentation-only option, to be added under `PROTOCOL.md`'s
rules before the freeze.

## Units

- **Step:** one step of the machine, as its `--steps` budget counts them:
  one equation or one literal elaborated in one derivation.
- **Alternative:** one derivation. All are live at once under **absys**.
  Under **absys-depth-first**, all are held too, but only the first is
  elaborated until it hibernates or fails, so the count is of derivations
  held, of which one is live.
  A derivation is not equated with a Prolog choicepoint, or with any
  other system's unit. Comparable counts come only from quantities a
  problem defines.
- **Store:** a vector, from `--measure` on the instrumented commit
  `f1def9d` (branch `measure`). For each assertion it gives the value at
  the end and the peak, sampled after every step, so the peak is exact at
  the granularity of steps:

  | quantity | what it counts |
  |---|---|
  | derivations | live derivations of the top-level computation |
  | sub_derivations | derivations inside `not` and `set` computations |
  | variables | variables created, in every derivation. Derivations only gain variables, so for one derivation this is cumulative; it falls only when a derivation fails. It is listed, but it is not retained store in the sense the others are |
  | bindings | variables with a value |
  | susp_equations | suspended equations between two uninstantiated variables |
  | susp_applications | applications waiting for a definition or their key |
  | susp_relations | arithmetic and `tout` relations waiting for values |
  | susp_negations | `not` and `set` waiting to be decided or tried again |
  | pending | equations, literals and alternatives queued, not yet taken up |
  | term_nodes | nodes of bound values, counted in every derivation that holds them, without regard to sharing |

  term_nodes is a logical size, not memory. Derivations share structure,
  so the memory held is smaller.

The state is also sampled right after an assertion is added and before the
first step, so a peak at a stage boundary is not missed.

The instrumented commit changes nothing the machine computes on the texts
tested. That is observational equivalence over that corpus, not a proof
for every workload. With
`--measure` off and on, its output was identical to the baseline
`7bb61e6`'s, byte for byte: 20 texts in 7 output modes (140 runs), full
traces included, and the JSON of all 20. Measuring is slow, because the
whole state is read after every step. Step counts are unaffected; only
time is. Results report the baseline commit for behaviour and the
instrumented commit for store.

## The same computation

The reconstruction is incremental. Every stage is received into the same
session, with no reposing.

## Prior work, not results

The absys repository's experiments E01–E09 ran versions of P01–P08 before
this specification existed. They will be written again from the problem
files after the freeze.
