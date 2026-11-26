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

## Notation

Absys is known in three notations: Absys 1 (1969), the 1982 paper's, and
the 1990 retrospective's. One notation is fixed per problem before any
program is written, and recorded with it. Absys 1 has arithmetic, and the
1990 notation has `not` and `set`.

## Units

- **Step:** one step of the machine, as its `--steps` budget counts them:
  one equation or one literal elaborated in one derivation.
- **Alternative:** one derivation. All are live at once under **absys**.
- **Store:** to be settled before the freeze. The proposal is the number of
  bindings and suspended relations held across all live derivations. The
  reconstruction does not yet report this at its peak. Reporting it would
  be an instrumentation-only change to the absys repository, needing your
  approval while changes there are on hold.

## The same computation

The reconstruction is incremental. Every stage is received into the same
session, with no reposing.

## Prior work, not results

The absys repository's experiments E01–E09 ran versions of P01–P08 before
this specification existed. They will be written again from the problem
files after the freeze.
