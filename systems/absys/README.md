# Absys

**Evidence class: reconstructed.** No Absys implementation survives. The
system used is the reconstruction in https://github.com/chrishayuk/absys,
built from Foster (1968), Foster and Elcock (1969), Elcock (1982) and
Elcock (1990). Every rule it follows, and the evidence for each, is in its
`docs/decisions.md`. It is pinned at commit `7bb61e6`, whose CI passed.

The study uses the reconstruction as it stands. It does not change it. A
change the study needs would go to the absys repository, with its
evidence, and the commit used here would move.

## Configurations

| configuration | what it is | classes |
|---|---|---|
| **absys** | the reconstruction's defaults, the rules it rests on the sources | reconstructed |
| absys-depth-first | `--search depth-first`: the backtracking reading of Elcock (1982) | reconstructed, with a decision reversed |
| absys-wake-back | `--wake back`: returned relations appended, as the word of Elcock (1982) says | reconstructed, with a decision reversed |

The second and third rest on readings of the sources that the
reconstruction did not take. They are kept because the sources conflict.
They are not extensions.

## Notation

Absys is known in three notations: Absys 1 (1969), the 1982 paper's, and
the 1990 retrospective's. Each program states which it uses. Absys 1 has
arithmetic, and the 1990 notation has `not` and `set`. A problem that
needs both is recorded as such.

## Prior work, not results

The absys repository's experiments E01–E09 ran versions of P01–P08 before
this specification existed. They are where the problems came from. They
will be written again from the problem files after the freeze.
