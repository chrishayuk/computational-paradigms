# Absys programs: batch 1A (P01, P02, P03)

*Phase 5 (`PROTOCOL.md`, "Implementation"), wave 1. Written against
`spec-1.0.1` and the contract of `harnesses/absys/README.md`. No program
here has been run. Only `harnesses/absys/check` was used, and it reports
no errors for any of them, in each configuration.*

**Author of every program:** `implementation-absys`, an agent (Claude
Opus 5.5, model id `claude-opus-5-5`), with its own context. It had not
seen any earlier work on this study.

**Precursor programs (E01–E09): not seen.** None of their texts was read.
`/opt/src/absys/research/`, `/opt/src/absys-measure/research/` and
`/opt/src/absys/docs/research.md` were not opened. Two things that bear on
these problems were seen in the documentation the brief allows, and are
disclosed:

- the reconstruction's `README.md` summarises findings of E02, E03, E06,
  E07 and E09 in prose. It gives, among others, the result of
  `app([1,2], S, T)` (close to P01b) and of `x + y = 10`, `x - y = 4`;
- the tutorial (ch. 8) and `examples/relation-list.ab2` give Elcock's own
  1982 text `u+v = 16 and w*u = v and u+10 = 12` with its trace. P02 is
  taken from that published source. It is a source, not a precursor
  program.

## Layout

One file per sub-problem, `programs/absys/<configuration>/<sub-problem>.ab1`,
for the three configurations of `systems/absys/README.md`:

    programs/absys/absys/              P01a P01b P01c P02a P02b P02c P03a P03b P03c P03d P03e P03f
    programs/absys/absys-depth-first/  the same twelve, byte for byte
    programs/absys/absys-wake-back/    the same twelve, byte for byte

**The three configurations share one text** for every sub-problem. The
flags (`--search depth-first`, `--wake back`) change how the machine
schedules derivations and returned relations, not the language, so the
natural program is the same text in each. The copies are identical; each
configuration has its own path only because the harness takes one.

P02b is one file for its six instances: its relations are PART sections
`R1`, `R2`, `R3`, and the harness gives part `order[k-1]` at stage *k*
(`harnesses/absys/README.md`, 3.5). Every other sub-problem has one
instance and uses STAGE sections.

## Notation

`systems/absys/README.md`, Notation: the earliest notation that has every
construct the problem needs. All twelve are in the **1969 notation**
(`.ab1`, Absys 1):

- P02 needs arithmetic, which the reconstruction has in the 1969 notation
  only (`docs/decisions.md`, rule 23).
- P01 and P03 need equations, lists, and a relation defined with
  alternatives. The 1969 notation has all three (`lambda … begin {A or B}
  end`, `[a;b]`, `[h&t]`), so it is the earliest, and the 1990 notation of
  Elcock's `app` is not used. The relations are written as relations (no
  `=> z` result, no `key`).

## Per configuration and sub-problem

The same entries hold for `absys`, `absys-depth-first` and
`absys-wake-back`.

| sub-problem | program | primary or variant | expressibility, as the author sees it | S used |
|---|---|---|---|---|
| P01a | `P01a.ab1`: `x = y`; `y = z`; `z = zval` | primary | expressible | none |
| P01b | `P01b.ab1`: conc; `conc(left, s, t)`; `s = sval` | primary | expressible | none |
| P01c | `P01c.ab1`: `x = [pfx&x]` | primary | expressible (no occur check, `docs/decisions.md` rule 8) | none |
| P02a | `P02a.ab1`: R1, R2, R3, one per stage | primary | expressible | none |
| P02b | `P02b.ab1`: PART R1, R2, R3, every order | primary | expressible | none |
| P02c | `P02c.ab1`: `begin` R1 R2 R3 `end`, one stage | primary | expressible | none |
| P03a | `P03a.ab1`: conc; `conc(ca, cb, c)` | primary | expressible | none |
| P03b | `P03b.ab1`: conc; `conc(a, b, cc)` | primary | expressible | none |
| P03c | `P03c.ab1`: conc; `conc(ca, b, cc)` | primary | expressible | none |
| P03d | `P03d.ab1`: conc; `conc(a, cb, cc)` | primary | expressible | none |
| P03e | `P03e.ab1`: conc, rev; `rev(ra, b)` | primary | expressible | none |
| P03f | `P03f.ab1`: conc, rev; `rev(a, rb)` | primary | expressible | none |

Nothing was judged not expressible, so there are no named variants. Every
program is a transcription: no extra argument, case, key, or reordering.
Expressibility here is the author's judgement; it does not anticipate the
outcome. P03f, for instance, is expected by the problem file to reach the
budget after its one answer in some systems; that is a result, not a
reason to reformulate.

### The definitions

conc (P01, P03), its two cases in the problem's order, case 2's head as
equations and then its condition:

    conc'=lambda p, q, r
        begin {p = [] q = r or
               p = [h'&k'] r = [h&m'] conc(k, q, m)} end

rev (P03e, P03f), likewise, with its two conjuncts in the stated order:

    rev'=lambda p, r
        begin {p = [] r = [] or
               p = [h'&k'] rev(k, n') conc(n, [h], r)} end

- The lambda's parameters stand for the case heads' three (two) places;
  each head pattern is an equation on a parameter, as in Elcock 1990's
  `app`. The names inside differ from the problem's (`p, q, r, h, k, m, n`
  for `a, b, c, h, a, c, q`): in the 1969 notation an unprimed name that a
  lambda does not bind is shared with the whole text, and the problem's
  own names are the sub-problems' top-level unknowns. Renaming is not a
  token class change.
- Local names are introduced with a prime at their first occurrence, once
  each (`docs/decisions.md`, rule 6), as FE69's `map` and `item` do. The
  procedure name is primed where it is defined (`conc'=`, `item'=`).
- P03a–d define only conc, which is all they use; P03e and P03f define
  conc and then rev, the vocabulary's order.

### Idioms and their sources

| idiom | source | used in |
|---|---|---|
| equations as assertions, side by side | Foster and Elcock 1969, "x=y y = 2" (`examples/assertions.ab1`) | P01a, P01c |
| a relation as `name'=lambda x, y begin {A or B} end`, primes for new names | Foster and Elcock 1969, `map` and `item` (`examples/map.ab1`, `examples/triples.ab1`; tutorial ch. 8) | P01b, P03 |
| lists `[a;b]`, `[]`, `[h&t]`; ⟨e1,…,en⟩ ++ x as `[e1;…;en&x]` | Foster and Elcock 1969 (tutorial ch. 8, ch. 10) | P01, P03 |
| the two cases as `{R = [], S = T} or {R = [X|L], T = [X|N], app(L, S, N)}` | Elcock 1990, p. 8 (`examples/append.abs`; tutorial ch. 4) | conc, rev |
| arithmetic as an assertion in any direction | Foster and Elcock 1969, "a = b + 1 … equivalent" (tutorial ch. 8); Foster 1968, pass sets | P02 |
| the relations written `u+v = 16`, `w*u = v`, `u+10 = 12` | Elcock 1982, p. 123 (`examples/relation-list.ab2`) | P02 |
| `begin … end` for one conjunction of assertions | Foster and Elcock 1969 (`docs/decisions.md`, "Three notations") | P02c |

### Constants

Each program's constants are in its block (`% CONSTANTS BEGIN` … `END`),
one per line, written in the 1969 notation, each tagged in a trailing
comment with the stage (or, in P02b, the part) that uses it, and referred
to by name in that stage. Under the harness's replacement (3.9), a constant
reaches the system only with its stage. The names (`zval`, `left`, `sval`,
`pfx`, `r1sum`, `r3add`, `r3sum`, `ca`, `cb`, `cc`, `ra`, `rb`) are used
for nothing else. No program depends on the values: P02's constants are
any integers, P01 and P03's any sequences (with P01a's any value).

## Ambiguities, and the readings taken

1. **P01c's constant is a sequence spliced into a list.** The stage is
   x = ⟨seq⟩ ++ x. In Absys, ⟨e1,…,en⟩ ++ x is the list `[e1;…;en&x]`,
   and there is no ++ to apply to a whole list value. So the block holds
   the sequence's *members* as the 1969 notation writes them inside a
   list, without brackets: `pfx = 1` for ⟨1⟩, and a variant ⟨1,2⟩ would
   be `pfx = 1;2`, giving `x = [1;2&x]`. A variant whose sequence is ⟨⟩
   would need `x = x` instead, which this form cannot give; the verifier
   should know that. The alternative, `conc(pfx, x, x)` with `pfx = [1]`,
   would take any sequence but replaces the problem's equation by an
   application of conc that the problem does not state (R), and was not
   chosen.
2. **P02c, "as one stage, in that order".** In the 1969 notation,
   assertions side by side are accepted one at a time, each elaborated
   before the next (harness README 3.2, decision 17), which would make
   P02c compute exactly as P02a. Elcock's 1982 program is one assertion
   (`… and … and …`), whose three relations go on one list in that order.
   The reading taken: one conjunction, `begin R1 R2 R3 end`, one
   assertion with one budget (harness QUESTIONS A1 says the choice is the
   author's).
3. **The notation for P01 and P03.** The rule picks the earliest notation
   with every construct needed. Whether the 1969 notation's relations
   without `=> z` and `key` are as FE69 wrote them is not shown by the
   extracts; the reconstruction's grammar allows them (tutorial ch. 10),
   and FE69's `map` and `small` are such relations. The 1969 notation was
   taken.
4. **R2 as `w * u = v`.** The problem writes w · u = v; it is transcribed
   as one primitive relation, `*` being the 1969 notation's product.
5. **Which unknowns are reported.** The unknowns are named as
   `stages.json` names them (`x`, `s`, `t`, `u`, `c`, `a`, `b`, …). The
   procedure names `conc` and `rev` are also identifiers of the text, and
   the system prints them among the procedures; they are not unknowns of
   the problems.

## What could not be read

The brief allows `/opt/src/absys` (`README.md`, `docs/`, `tutorial/`,
`examples/`) in the image. Reading it needs a container started with
`cat` or `ls`; a first attempt (`sh -c 'ls …'`) was refused by the
author's permission system, and later plain `cat` and `ls` calls
succeeded. Read: `README.md`, `docs/decisions.md`, tutorial chapters 3, 4,
8 and 10, and the examples listed above. Not read: `docs/research.md`
(it describes the precursor experiments), tutorial chapters 1, 2, 5–7, 9.

Something outside the brief's list was in the author's context without
being opened: at the start of the session, its environment supplied the
two-line index of an auto-memory file under `~/.claude/projects/…`
(titles only: one on access to Absys sources, one on commit trailers). The
files it points to were not opened. Nothing else outside the brief's list
was read.
