# Absys

**Evidence class: reconstructed.** No Absys implementation survives. The
system used is the reconstruction in https://github.com/chrishayuk/absys,
built from Foster (1968), Foster and Elcock (1969), Elcock (1982) and
Elcock (1990). Every rule it follows, and the evidence for each, is in its
`docs/decisions.md`.

## Pinning

The commit used is fixed when the specification is frozen. It is
`efd5203` (`PINS.md`): `7bb61e6` with one defect of the printer fixed.
Printing a list that contains itself (`x = [x]`, P01c) overflowed the
stack after the computation had finished. Only the printer changed, and
every example and research text prints byte for byte as at `7bb61e6`
(160 runs), which is kept as the behavioural reference. The defect is
recorded in the reconstruction's `docs/decisions.md`. Any later change to the
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

**No comparisons.** The pinned reconstruction has +, −, · and ÷ as
relations, and no <, ≤, > or ≥, as calibration found. Three claims are kept
apart:

| claim | status |
|---|---|
| the pinned reconstruction has no comparison operators | established |
| the notations recovered from the sources show none | supported by the sources examined: Foster (1968), the extracts of Foster and Elcock (1969), Elcock (1982) and Elcock (1990) |
| historical Absys never had comparisons | **not established**. The full description of Absys-4 (Elcock and Gray, 1988) and the program itself have not been seen |

Expressibility is recorded per **sub-problem**, not per problem family. A
sub-problem that needs a comparison cannot be transcribed: P05's x > 1,
P09c's n > 5, P10d's x > 1, P11's x ≥ 2, P12's n > 0, P13a–d's range, and
P15d. The other sub-problems of the same problem are recorded on their
own. The rule for every system then applies (`SPECIFICATION.md`,
expressibility):

- where a reformulation without the comparison keeps the meaning on every
  input the problem and its variants use (replacing n > 0 by an enumeration
  of the finitely many values used, for instance), it is the program of
  record, *expressible with reformulation*;
- where it does not (calibration's range, with m > n replaced by
  m = n + 1 and m ≤ n dropped, which leaves an endless derivation), the
  sub-problem is *not expressible*, and the reformulation is a named
  variant.

**Output.** The baseline prints at most 32 elements of a list and 24
derivations. The instrumented commit `5450449` (branch `measure`) adds
`--full`, which prints both in full, so `observe()` can read every answer.
With no occur check, a computation can end with a cyclic value (P01c), so
`--full` detects a list cell met again while it is being printed, and
prints `↻` for "the enclosing list again": X = [1|X] prints `[1|↻]`,
X = [X] prints `[↻]`. Tests cover cyclic tails and heads, cycles through
two variables, long and partly known lists, and many derivations.
Against the baseline, its default output is identical in all 140 runs, and
`--full` output is identical in the 132 runs the baseline did not cut
short.

**A fault, found and fixed.** At `7bb61e6` the default printer overflowed
the stack on a cycle through a list's elements, X = [X]: the computation
finished, and printing its answer crashed. It was fixed on `main` as
`efd5203`, the pinned commit, which prints `[↻]` in every mode. The fault
is kept on record, in the reconstruction's `docs/decisions.md` and in
`PINS.md`. No result is taken from `7bb61e6`.

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
  `f1a63aa` (branch `measure`; `5450449` adds `--full` and changes nothing
  measured). For each assertion it gives the value at
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
`--measure` off and on, its output was identical to the baseline's, byte
for byte: 20 texts in 7 output modes (140 runs), full traces included,
and the JSON of all 20. This was checked against `7bb61e6`, and again
after the branch was rebased onto `efd5203`, with the same result; `--full`
output also matched wherever the baseline cut nothing short (132 runs). Measuring is slow, because the
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
