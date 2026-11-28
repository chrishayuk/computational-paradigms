# Python: the supporting mechanisms (S) the programs use, batch by batch

The cumulative account of the machinery built on top of Python to state
the problems. Three mechanisms were **listed at phase 4**, before any
program was written (`harnesses/python/S-mechanisms.md`). Every other
mechanism here was **supplied by a program itself**. Results that rely on
one are identified as *extended, with program-supplied mechanisms* (named
below), and are never attributed to *extended* as listed. Use of a listed mechanism is read from each program's imports; sizes of
the program-supplied ones are each classifier's tokens per program text. Both classifiers' figures are kept
(`PROTOCOL.md`, "Two classifiers"): A is a Claude agent, B is Codex.

## Listed at phase 4

| mechanism | file | tokens | used in |
|---|---|---|---|
| backtracking search | `S/search.py` | 176 | 1A: P03; 1B: P04, P06d–e, P08 (and through the propagator in P05, which imports it) |
| suspension queue | `S/suspend.py` | 537 | 1A: P01, P02, P03; 1B: P04, P06, P07, P08 |
| constraint propagator | `S/propagate.py` | 1,260 | 1B: P05 |

## Supplied by the programs, *extended*

| mechanism | first in | problems | A: tokens per program | B: tokens per program |
|---|---|---|---|---|
| unification of terms | 1A (P03) | 1A P03; 1B P04, P06d–e, P08 | 172–182 | 172–183 |
| resolution over a goal list | 1A (P03) | 1A P03; 1B P04, P06d–e, P08 | 58 | 58–79 |
| negation as failure | 1B (P06d–e) | P06d, P06e | 50 | 50 |
| wait for a definition (application store) | 1B (P08) | P08 | 142 | 249 |
| relation adapter onto the suspension queue | 1B | P06a–c, P07 | not S (A classes it R) | 196 |

## Supplied by the programs, *core* and *stdlib-concurrency* (classifier B only)

Classifier B also classes as S code in *core* and *stdlib-concurrency*
that is general over relations and is repeated from problem to problem
(`METRICS.md`, rule 19, its "reusable from one problem to another"
reading). Classifier A classes the same code R, as written for each
program's own relations. Under B's reading, those programs use supporting
code, so they belong in an extended configuration, not in *core* or
*stdlib-concurrency* as listed. This is **classification-sensitive**
(`results/BATCH-1B.md`).

| mechanism (B's name) | configurations | problems | B: tokens per program |
|---|---|---|---|
| evaluator-driven relation holder | core, stdlib-concurrency | P06a–c (and the same code in P01, P02, P07) | 220–377 |
| named-place relation store | core, stdlib-concurrency | P08 | 51–242 |
| threaded relation and definition scheduler | stdlib-concurrency | P08 | 393–397 |

## Batch 1C (P09–P12)

Read from `results/python/classes-1C/{A,B}/python.json`, `s_mechanisms`.
For the listed mechanisms, A counts the tokens of each program's import
of the mechanism (7–11), and B the tokens of the mechanism's file
(176, 537, 1,260); the use is the same.

| mechanism | configuration | problems | listed at phase 4 | A: tokens per program | B: tokens per program |
|---|---|---|---|---|---|
| backtracking search | extended | P09a–b, P10d, P11, P12 | yes | 7–9 (import) | 176 (file) |
| suspension queue | extended | P09, P11, P12 | yes | 11 (import) | 537 (file) |
| constraint propagator | extended | P10d | yes | 7 (import) | 1,260 (file) |
| unification of terms | extended | P09a, P11, P12 | no | 177–188 | 172–177 |
| resolution over a goal list | extended | P09a, P11, P12 | no | 58 | 58–79 |
| a relation application as a goal of the queue | extended | P09c–d | no | 92 | 95 |
| an arithmetic relation as a goal of the queue | extended | P09e | no | 174 | 179 |
| relation-holding loop (`decide`, `place`) | core | P09e | no | 165 | not S |
| relation threads (A) / threaded relation dispatcher (B) | stdlib-concurrency | A: P09c–e, P10b, P10d; B: P09c–d | no | 195–349 | 331 |

In batch 1C, unlike 1B, it is **classifier A** that classes code in *core*
and *stdlib-concurrency* as program-supplied S (rule 19, "reusable from
one problem to another"): core P09e, and five *stdlib-concurrency*
programs. B classes core P09e's holding code R, and S only in
*stdlib-concurrency* P09c–d. Under either reading, the programs with such
S belong in an extended configuration, not in *core* or
*stdlib-concurrency* as listed. This is **classification-sensitive**
(`results/BATCH-1C.md`).

## Cumulative cost

Python's listed mechanisms are 1,973 tokens, written once. By batch 1B,
the programs of *extended* also carry, in each program that needs them,
unification and resolution (about 230–260 tokens), and where needed
negation (50) and waiting for a definition (142–249). That is machinery
SWI-Prolog provides natively (unification, resolution, negation as
failure) or in its *session* configuration (waiting for a definition), and
Absys provides natively (waiting for a definition).
