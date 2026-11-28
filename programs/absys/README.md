# Absys programs: batch 1A (P01, P02, P03) and batch 1B (P04-P08)

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
([redacted by tools/redact-transcripts.py: what the entries are about]). The
files it points to were not opened. Nothing else outside the brief's list
was read.

# Batch 1B: P04, P05, P06, P07, P08

*Phase 5, wave 1, against `spec-1.0.1` and the contract of
`harnesses/absys/README.md`. No program here has been run. Only
`harnesses/absys/check` was used, and it reports no errors and no warnings
for any of them, primary or variant, in each of the three configurations.*

**Author of every program:** `implementation-absys`, an agent (Claude
Opus 5.5, model id `claude-opus-5-5`), in a fresh context with no other
knowledge of this study than the files listed below. It had not seen any
earlier work on it, and in particular not batch 1A's results.

**Precursor programs (E01-E09): not seen.** No text of them was read:
`/opt/src/absys/research/`, `/opt/src/absys-measure/research/` and
`/opt/src/absys/docs/research.md` were not opened. What the allowed
documentation says of them, and of these problems, is disclosed:

- the reconstruction's `README.md` reports in prose that
  `{loop(A)} or {A = 1}` gives `A = 1` while the loop runs on, that left
  recursion over known data terminates, that `not(X = 1)` then `X = 2` has
  no derivation while the other order has `X = 2`, that `x + y = 10` and
  `x - y = 4` leave both relations waiting, and what its `setdiff` computes;
- tutorial ch. 5 runs `{loop(A)} or {A = 1}`, ch. 7 runs `X = 2`,
  `not(X = 1)` in both orders, the 1990 `setdiff` with `set` on
  `[1,2,3,4]` and `[2,4,6]`, and the student database with
  `non-maths-major('SMITH')`; ch. 4 applies `app` before it is defined;
- `examples/setdiff.abs` and `examples/students.abs` are Elcock's own 1990
  texts (with the reconstruction's `mem`), and are cited below as sources
  of idioms. They are published programs, not precursor programs.

None of this changed a program: every text below is the transcription the
rules give, and none was chosen for an outcome.

## Layout

    programs/absys/<configuration>/P04a.ab1 … P04f.ab1
                                  P05a.ab1  P05b.ab1  P05c.ab1
                                  P06a.abs  P06b.abs  P06c.abs  P06d.abs  P06e1.abs  P06e2.abs  P06e3.abs
                                  P07a.ab1  P07a.132.ab1  P07a.213.ab1  P07a.231.ab1  P07a.312.ab1  P07a.321.ab1
                                  P07b.ab1 … P07g.ab1
                                  P08a.ab1  P08b.ab1  P08c.ab1
    programs/absys/<configuration>/variants/P06d.set.abs        named variant
    programs/absys/<configuration>/variants/P08c.redefine.ab1   named variant

for each of `absys`, `absys-depth-first`, `absys-wake-back`. **The three
configurations share one text** for every sub-problem and variant, byte
for byte, for the reason given for batch 1A: the flags change how the
machine schedules derivations and returned relations, not the language,
so the natural program is the same text in each.

Every file is one instance, named by its instance id in `stages.json`
(the sub-problem's id where it has one instance). P07a has six instances,
and so six files (ambiguity 1 below).

## Notation

By the rule of `systems/absys/README.md` (the earliest notation with every
construct the problem needs):

| problem | notation | why |
|---|---|---|
| P04 | 1969 (`.ab1`) | needs procedures with alternatives, lists and an atom, all in Absys 1 |
| P05c | 1969 | needs a closed world of facts (a procedure with alternatives) and equations |
| P05a, P05b | 1969 | need comparisons, which **no** notation has; they are reformulated with arithmetic, which only the 1969 notation has. P05a's x ≠ k also needs `not`, only in the 1990 notation; the problem's constructs are found in no single notation, and the notation used is 1969, with ≠ reformulated too |
| P06 | 1990 (`.abs`) | needs `not` (`docs/decisions.md` rule 18: 1990 only) |
| P07 | 1969 | needs arithmetic (rule 23: 1969 only) |
| P08 | 1969 | needs rev and conc, as in P03 (batch 1A) |

## Per configuration and sub-problem

The same entries hold for `absys`, `absys-depth-first` and
`absys-wake-back`. "S used": none anywhere (`harnesses/absys/S-mechanisms.md`;
no program contains code that supplies a mechanism the configuration
lacks). No control construct is used: no `key`, no declaration.

| sub-problem | program | primary or variant | expressibility, as the author sees it |
|---|---|---|---|
| P04a | `P04a.ab1`: loop; `{loop(x) or x = xval}` | primary | expressible |
| P04b | `P04b.ab1`: loop; `{x = xval or loop(x)}` | primary | expressible |
| P04c | `P04c.ab1`: alist-left; `alist(sq)` | primary | expressible |
| P04d | `P04d.ab1`: alist-left; `alist(s)` | primary | expressible |
| P04e | `P04e.ab1`: alist-right; `alist(sq)` | primary | expressible |
| P04f | `P04f.ab1`: alist-right; `alist(s)` | primary | expressible |
| P05a | `P05a.ab1`: pick, gt, pos, ne; `pick(x)`; `gt(x, gtk)`; `ne(x, nek)` | primary | **expressible with reformulation** (> and ≠) |
| P05b | `P05b.ab1`: pick, gt, pos; `gt(x, gtk)`; `pick(x)` | primary | **expressible with reformulation** (>) |
| P05c | `P05c.ab1`: pick; `pick(x)`; `x = xeq2`; `x = xeq3` | primary | expressible |
| P06a | `P06a.abs`: `not(x = nk1)`; `x = xk2` | primary | expressible |
| P06b | `P06b.abs`: `x = xk1`; `not(x = nk2)` | primary | expressible |
| P06c | `P06c.abs`: `not(x = nk1)`; `x = xk2` | primary | expressible |
| P06d | `P06d.abs`: mem, setdiff by its three cases; `setdiff(s1v, s2v, d)` | primary | expressible |
| P06d | `variants/P06d.set.abs`: mem, setdiff with `set` | **named variant** | (see P06d below) |
| P06e1 | `P06e1.abs`: student, maths, takes, nonmajor; `nonmajor(who)` | primary | expressible |
| P06e2 | `P06e2.abs`: the same; `nonmajor(who)` | primary | expressible |
| P06e3 | `P06e3.abs`: the same; `nonmajor(p)` | primary | expressible |
| P07a | `P07a.ab1` and `P07a.<order>.ab1`: `begin R R R end` in the instance's order | primary | expressible |
| P07b | `P07b.ab1`: `begin x + y = bsum  x - y = bdiff end` | primary | expressible |
| P07c | `P07c.ab1`: `x + y = csum` | primary | expressible |
| P07d | `P07d.ab1`: `begin w * u = v  u = uval  v = vval end` | primary | expressible |
| P07e | `P07e.ab1`: the same text, P07e's constants | primary | expressible |
| P07f | `P07f.ab1`: `begin x + y = fsum1  x + y = fsum2 end` | primary | expressible |
| P07g | `P07g.ab1`: `x * x = gsq` | primary | expressible |
| P08a | `P08a.ab1`: six stages; rev and conc defined at stage 4 | primary | expressible |
| P08b | `P08b.ab1`: stages 1-3 of P08a | primary | expressible |
| P08c | `P08c.ab1`: conc; `rev(rs, b)`; rev = case 1 or `revmore`; revmore = case 2 | primary | **expressible with reformulation** |
| P08c | `variants/P08c.redefine.ab1`: rev equated with case 1, then with case 2 | **named variant** | (see P08c below) |

Expressibility is the author's judgement, recorded before any run; it
anticipates no outcome. Several of these texts are expected by the problem
files to run to the budget in some systems (P04a, P04d, P05a, P05b); that
is a result, not a reason to reformulate.

### P04

- loop, its one case, `loop'=lambda p begin loop(p) end`.
- alist-left, `{alist(m') p = ['a'&m] or p = []}`: case 1 first, its
  conjuncts in the stated order (alist(m), then the equation for s), then
  case 2. alist-right, `{p = [] or p = ['a'&m'] alist(m)}`: case 1, then
  case 2 with its head ⟨ᴀ⟩ ++ m as an equation on the parameter and then
  alist(m). The atom ᴀ is written `'a'` (1969 quoted constant).
- P04a and P04b are one assertion, `{A or B}`, the alternatives in the
  stated order.
- Constants: `xval` (P04a, P04b), `sq` (P04c, P04e). P04d and P04f have
  none (`harnesses/README.md`, section 11), so they have no block. ᴀ
  belongs to the definitions, not to a stage, and is not in a block.

### P05

- pick is the completion of its three facts, `{p = pk1 or p = pk2 or
  p = pk3}`, in their order, each fact's value a constant (`pk1`-`pk3`).
  It is vocabulary, so it is in the prelude; its constants are tagged
  stage 1, where `stages.json` places the facts.
- **x > k and x ≠ k (P05a, P05b).** No notation of the pinned
  reconstruction has a comparison (`systems/absys/README.md`, Notation),
  so they cannot be transcribed. The reformulation, all R:
  - `gt(a, b)`: `a = b + d'` and `pos(d)`;
  - `pos(q)`: `{q = 1 or pos(e') q = e + 1}`, the least relation with
    pos(1) and pos(e + 1) if pos(e), which is exactly the positive integers;
  - `ne(a, b)` (P05a only): `{gt(a, b) or gt(b, a)}`.

  Over the integers these are exactly > and ≠, on every input; they use
  only arithmetic (FE69, rule 23) and alternatives. That is why the author
  judges P05a and P05b *expressible with reformulation*, with this as the
  program of record, rather than *not expressible*: the reformulation
  drops no guard and keeps the relations' meaning
  (`SPECIFICATION.md`, expressibility). Two limits, recorded so that the
  classifiers can judge otherwise:
  - comparisons hold only of integers. If a variant's facts of pick were
    not integers, `a = b + d` with a non-number neither holds nor fails
    (rule 23: it waits), where x > k is false. ≠ is reformulated only for
    integers; in P05a x is an integer by stage 2's x > k, so in the
    conjunction the two agree.
  - `pos` with a known argument q ≤ 0 has no failing derivation: the
    recursion goes on down. The meaning is the same; the operational
    behaviour is not that of a primitive comparison. `pos` with an
    unknown argument enumerates the positive integers; a classifier may
    see that as a generator of values (C, `METRICS.md` table) rather than
    the definition of a relation (R). The author classes it R: it is the
    definition of x > k, used in whichever direction the data allow.
- P05c needs no comparison and is a transcription.

### P06

- P06a-c: `not(x = k)` and `x = k`, one per stage, as stated.
- **P06d.** Primary: mem and setdiff by the problem's cases, in order,
  each head as equations on the lambda's parameters (Elcock 1990's `app`
  idiom), then the case's conjuncts in the order written; case 3's
  `not mem(h, s2)` as `not(mem(H, S2))`. mem has the shape of the
  reconstruction's own mem (tutorial ch. 7), which is the problem's two
  cases. **Named variant** `variants/P06d.set.abs`: Elcock's 1990
  `{set(X), {mem(X, S1), not(mem(X, S2))}, S}`, which the problem allows
  (METRICS.md, rule 7). It was not chosen as primary, before any run,
  because it is not the problem's definition on every input: `set` gives
  the *distinct* values of X, so an s1 with a repeated element (a variant
  could have one) would lose the repetition, and its order is the order in
  which the derivations stand (`docs/decisions.md` rule 19), which the
  problem does not state. The variant is to be run and reported.
- **P06e.** student, maths and takes are the completions of their facts,
  as Elcock 1990 p. 15 renders Clark's database (`examples/students.abs`),
  each fact's atoms constants (`st1`, `st2`, `mc1`, `mc2`, `tp1`/`tc1` …
  `tp3`/`tc3`), the facts in the order given. nonmajor is the problem's one
  case, `{student(P), maths(K), not(takes(P, K))}`, the conjuncts in the
  stated order. Elcock's `non-maths-major` omits `student(X)`; the
  problem's case has it, and it is kept. The atoms are written as Elcock
  writes them, `'BROWN'`, `'C101'`.

### P07

- Each sub-problem is one stage, its relations in the order given. Where
  the stage has several relations they are one conjunction,
  `begin … end`, one assertion, as P02c in batch 1A (ambiguity 2 there):
  so the stage has one budget, and its relations go to the machine
  together in the order written.
- Compound relations are written as the problem writes them
  (`x + y + z = r1sum`), which `SPECIFICATION.md` counts as transcription.
  `x - y = bdiff` and `w * u = v` are the 1969 notation's `-` and `*`.
- P07d and P07e are the same text with different constants.

### P08

- rev and conc are batch 1A's texts (P03e), with one change: the procedure
  names are not primed where they are defined (`rev=lambda`, `conc=lambda`,
  not `rev'=lambda`). In P08 the name is applied before it is defined, and
  in the 1969 notation a prime introduces a new name, so the definition is
  written as an equation on the name already in use (rule 6: an
  application of an identifier with no value waits for it). This is the
  reading of the 1969 notation the author took; it is ambiguity 4.
- P08a: stage 1 `a = [x;y;z]`, stage 2 `rev(a, b)`, stage 3 `x = y`,
  stage 4 the definitions of rev and then conc (the order the stage names
  them), stage 5 `y = z`, stage 6 `b = [pfx&c]`. No declaration of any
  kind (rule 11 of `METRICS.md` has nothing to count): an undefined
  relation waits by the machine's own rule.
- P08b: stages 1-3 of P08a, the same text.
- **P08c.** Stage 1 conc; stage 2 `rev(rs, b)`; stage 3 "rev, case 1
  only"; stage 4 "rev, case 2". An Absys procedure is one value, given by
  one equation on its name; nothing in the language adds a case to a
  procedure already defined. Two programs were considered:
  - **primary**, `P08c.ab1`: stage 3 defines rev as case 1 *or* an
    application `revmore(p, r)` of a name for the cases not yet given;
    stage 4 defines `revmore` as case 2. Under the closed reading at stage
    3 revmore has no instances, so rev is case 1 alone; under the open
    reading revmore waits; after stage 4 rev is the union of its two cases,
    which is the problem's rev. So the reformulation keeps the meaning, and
    the author judges P08c *expressible with reformulation*. R: the name
    revmore, its alternative in rev, and the head of its definition; the
    cases' contents are P.
  - **named variant**, `variants/P08c.redefine.ab1`: each stage's part as
    an equation on rev by itself. That keeps each stage's text, but the
    two equations equate rev with two different lambdas; they do not
    denote rev's two cases. It changes the meaning, and is not the program
    of record. It is to be run and reported.
- The two ⟨⟩ of case 1 are constants (`r1p`, `r1r`), because `stages.json`
  places constants there ("rev, case 1 only: rev(<seq>, <seq>)"); the ⟨⟩ of
  the other definitions are not, as `stages.json` places none in them.

### Idioms and their sources

| idiom | source | used in |
|---|---|---|
| a relation as `name'=lambda x begin {A or B} end`, primes for new local names | Foster and Elcock 1969, `map`, `item` (`examples/map.ab1`, `examples/triples.ab1`) | P04, P05, P08 |
| alternatives asserted at the top level, `{A or B}` | Foster and Elcock 1969, `p=[1;2] {p = [a;b] or p = [b;a]}` (`examples/alternatives.ab1`) | P04a, P04b |
| loop as a procedure whose body applies itself | the reconstruction's tutorial, ch. 5, `loop = lambda X {loop(X)}` | P04a, P04b |
| a case's head as equations on the lambda's parameters | Elcock 1990 p. 8, `app` (`examples/append.abs`) | P04, P06d, P08 |
| a closed world as the completion of its facts, a procedure with one alternative per fact | Elcock 1990 p. 15 (`examples/students.abs`) | P05, P06e |
| `not(A)`, an independent computation with the criteria reversed | Elcock 1990 p. 14 (tutorial ch. 7) | P06 |
| `{set(X), {…}, S}` | Elcock 1990 p. 15 (`examples/setdiff.abs`) | P06d variant |
| mem as `{S = [X\|T]} or {S = [Y\|T], mem(X, T)}` | the reconstruction's own (tutorial ch. 7, `examples/setdiff.abs`) | P06d |
| arithmetic as an assertion usable in every direction | Foster and Elcock 1969 (tutorial ch. 8); Foster 1968, pass sets | P05a, P05b, P07 |
| relations written as Elcock writes them, `u+v = 16`, `w*u = v` | Elcock 1982 p. 123 (`examples/relation-list.ab2`) | P07 |
| `begin … end` for one conjunction | Foster and Elcock 1969 (`docs/decisions.md`, Three notations) | P07 |
| a procedure applied before it is defined waits for it | Elcock 1990 p. 10 (`docs/decisions.md` rule 6; tutorial ch. 4) | P08 |

### Constants

As in batch 1A: one block per program, one constant per line, each tagged
with the stage that uses it, referred to by name only in that stage (or,
for the facts of a definition, in the prelude, given at stage 1). The
names are used for nothing else. No program depends on the values within
the problem's domain: P04's constants are any value (P04a) and any
sequence (P04c, P04e); P05's and P07's any integers; P06's any values
(P06a-c), sequences (P06d) and atoms (P06e); P08's any sequences.

## Ambiguities, and the readings taken

1. **P07a's six orders, in one stage.** `stages.json` makes P07a one stage
   whose relations come in the instance's order. The harness's PART
   mechanism (`harnesses/absys/README.md`, 3.5, which names P07a) gives
   part `order[k-1]` at stage *k*. For a one-stage instance that gives only
   the first relation of the order, never the other two (the harness's
   `Program.section`). So PART sections cannot pose P07a as its instances
   need. Choosing the order with the program's own code from the
   `order` parameter would add alternatives and steps the problem does not
   have (harness QUESTIONS, A9), and C tokens. **The reading taken:** one
   file per instance (`P07a.ab1` for the written order, the instance
   `P07a`, and `P07a.132.ab1` … `P07a.321.ab1`), each one stage with the
   three relations as one conjunction in that instance's order. The six
   texts differ only in the order of the conjuncts. The order is the
   instance's structure, not a constant, and is not varied by the hidden
   variants; but the verifier has six blocks to substitute, identical in
   each.
2. **The number of facts in a closed world (P05, P06e).** `stages.json`
   writes the facts as `<facts>`. Each fact's values are constants here,
   and the number of facts is the problem's ("a closed world of three
   facts", and the facts listed in P06e). A variant with a different
   number of facts needs an alternative added or removed in the
   definition, which the block alone cannot do. Holding the facts as one
   list constant would need a membership relation the problem does not
   give (R), and was not chosen.
3. **P05's comparisons: reformulation or not expressible.** The systems
   file says a sub-problem with a comparison "cannot be transcribed", and
   leaves the choice between *expressible with reformulation* and *not
   expressible* to the rule. The author's reading, above: positivity
   defined from arithmetic keeps the meaning of > on every integer input,
   so it is the program of record. The classifiers may take the other view,
   on the grounds given above (no failure for q ≤ 0; non-integers).
4. **Primes on a name applied before it is defined (P08).** The 1969
   notation introduces a name with a prime, and batch 1A primes each
   procedure where it is defined. Whether a top-level prime makes a new
   variable distinct from an earlier unprimed use is not shown by the
   documentation read. The reading taken: no prime on a procedure name in
   P08, so that the definition is an equation on the name the earlier
   application waits on.
5. **P08c, "rev, case 1 only" and then "case 2".** See P08c above: Absys
   cannot add a case to a defined procedure. Writing case 1 with an
   application of `revmore`, for the cases still to come, uses the stage's
   own statement that the definition is partial ("case 1 only"); it does
   not use the content of stage 4. Whether that counts as anticipation
   (`PROTOCOL.md`, rule 5) the author judged not, and records it here.
6. **P08a stage 6, b = ⟨42⟩ ++ c**, and the sequence constant spliced into
   a list: as batch 1A, ambiguity 1 (`pfx = 42` gives `b = [42&c]`; a
   variant ⟨1,2⟩ would be `pfx = 1;2`, and ⟨⟩ cannot be given this way).
7. **Several relations in one stage (P07)** as one conjunction: as P02c
   in batch 1A (ambiguity 2 there).
8. **Which unknowns are reported.** Named as `stages.json` names them.
   In the 1990 notation (P06) the top-level unknowns `x`, `d`, `p` are
   small-letter names, shared by the whole text; the variables inside the
   lambdas are capitals, local, and distinct from them.

## What was read, and anything outside the brief

Read: the brief's list, that is `README.md`, `SPECIFICATION.md`,
`METRICS.md`, `PROTOCOL.md`, `AMENDMENTS.md`, `problems/README.md`, the
problem files of P04-P08, `systems/absys/README.md`, `harnesses/README.md`,
`harnesses/stages.json`, `harnesses/absys/` (`README.md`, `QUESTIONS.md`,
`S-mechanisms.md`, `check`, `absys_harness.py` in part, the
qualification's file list and `x19-parts.abs`), batch 1A's programs and
this README. In the image: `/opt/src/absys` was listed with `ls`, and
`README.md`, `docs/decisions.md`, `tutorial/` and `examples/` were copied
out with `tar` to a scratch directory (two `container run` calls of `ls`
and `tar`, to read files; no Absys program, harness `run` or interpreter
was run on anything). Read from the copy: `README.md`,
`docs/decisions.md`, tutorial chapters 02, 03, 04, 05, 06, 07, 08 and 10,
and every program text in `examples/` (not their `.out` files). Not read:
tutorial chapters 01 and 09, `docs/research.md`, `research/`.

P08 says "rev and conc are as in P03". The problem file of P03 is outside
the brief's list and was not opened; rev and conc were taken from batch
1A's P03e program, which transcribes them.

Something outside the brief's list was in the author's context without
being opened: at the start of the session its environment supplied the
index of an auto-memory file under `~/.claude/projects/…` (two lines:
[redacted by tools/redact-transcripts.py: what the entries are about]). The files it
points to were not opened. Nothing else outside the list was read.

# Batch 1C: P09, P10, P11, P12

*Phase 5, wave 1, against `spec-1.0.1` and the contract of
`harnesses/absys/README.md`. No program here has been run. Only
`harnesses/absys/check` was used, and it reports no errors for any of
them, primary or variant, in each of the three configurations.*

**Author of every program:** `implementation-absys`, an agent (Claude
Opus 5.5, model id `claude-opus-5-5`), in a fresh context with no other
knowledge of this study than the files listed at the end. It had not seen
any earlier work on it, and in particular no result of batches 1A or 1B.

**Precursor programs (E01-E09): not seen.** No text of them was read:
`/opt/src/absys/research/`, `/opt/src/absys-measure/research/` and
`/opt/src/absys/docs/research.md` were not opened. The allowed
documentation runs `{loop(A)} or {A = 1}` (tutorial ch. 5) and FE69's
`map` with `key` (`examples/map.ab1`); both are published texts, cited
below as sources of idioms, not precursor programs. None of the problems
P09-P12 appears in the documentation read.

## Layout

    programs/absys/<configuration>/P09a.ab1  P09b.ab1  P09c.ab1  P09d.ab1  P09e.ab1
                                  P10a.ab1  P10b.ab1  P10c.ab1  P10d.ab1
                                  P11c.abs  P11d.abs
                                  P12a.n8.ab1  P12a.n12.ab1  P12a.n16.ab1   (and the same for P12b, P12c, P12d)
    programs/absys/<configuration>/variants/P09a.AB.or.ab1  P09a.BA.or.ab1  P09b.or.ab1   named variants
    programs/absys/<configuration>/variants/P11a.ne.abs  P11b.ne.abs                      named variants (no primary)

for each of `absys`, `absys-depth-first`, `absys-wake-back`. **The three
configurations share one text** for every sub-problem and variant, byte
for byte, for the reason given for batch 1A: the flags change how the
machine schedules derivations and returned relations, not the language,
so the natural program is the same text in each.

Which file serves which instance of `stages.json`:

| instances | file |
|---|---|
| `P09a.AB`, `P09a.BA` | `P09a.ab1` (the harness gives the SPAWN subsections in the instance's `spawn_order`) |
| `P09b`, `P09c`, `P09d`, `P09e`, `P10a`-`P10d`, `P11c`, `P11d` | the file of that name |
| `P12x.nN.all`, `P12x.nN.any` | `P12x.nN.ab1` (accept's facts depend on n; the answer mode is the harness's cap) |
| `P11a`, `P11b` | none: not expressible. The named variants `variants/P11a.ne.abs`, `variants/P11b.ne.abs` |

## Notation

By the rule of `systems/absys/README.md` (the earliest notation with every
construct the problem needs):

| sub-problem | notation | why |
|---|---|---|
| P09a | 1969 | loop, rev and conc, as in P04 and P03 |
| P09b, P09e | 1969 | equations; P09e arithmetic |
| P09c | 1969 | n > 5 and n ≤ 5 are comparisons, which no notation has; reformulated with arithmetic, 1969 only |
| P09d | 1969 | lists and arithmetic (n + 1) |
| P10a-c | 1969 | arithmetic; P10b also `key` (1969 only) |
| P10d | 1969 | x > k reformulated with arithmetic, as P05 |
| P11c, P11d | 1990 | emit is `tout`, and ≠ is written with `not`: both 1990 only (below) |
| P11a, P11b | none | they need emit (1990 only) and x ≥ k, which can be reformulated only with arithmetic (1969 only): **not expressible** |
| P12 | 1969 | n − 1 needs arithmetic; n > 0 reformulated |

**`tout` is the 1990 notation's only.** `docs/decisions.md` rule 1 and
the tutorial's grammar (ch. 10) list `tout` in the 1990 notation and not
in the 1969 one. `check` confirms it without running anything: in a `.abs`
file `tout(x)` is refused ("tout takes a label and a term"), while in a
`.ab1` file `tout(x)`, `tout(x, y, z)` and `tout("emit", x)` are all
accepted, as applications of an identifier `tout` that has no definition
(`not(x = 1)` is likewise refused in `.ab1`). So in the 1969 notation
`tout("emit", x)` would be an application waiting for a definition of
`tout` (rule 6), never the output assertion, and emit cannot be written.
(These probes were scratch files, checked and deleted; they are not
programs.)

## Per configuration and sub-problem

The same entries hold for `absys`, `absys-depth-first` and
`absys-wake-back`. "S used": none anywhere (`harnesses/absys/S-mechanisms.md`;
no program contains code that supplies a mechanism the configuration
lacks). C constructs: `key` in P10b only.

| sub-problem | program | primary or variant | expressibility, as the author sees it |
|---|---|---|---|
| P09a | `P09a.ab1`: loop, conc, rev; SPAWN A `loop(x)`, SPAWN B `rev(ra, b)` | primary | expressible (ambiguity 1) |
| P09a | `variants/P09a.AB.or.ab1`, `variants/P09a.BA.or.ab1`: `{loop(x) or rev(ra, b)}` in the spawn order | named variant | (see P09) |
| P09b | `P09b.ab1`: SPAWN A `begin x = ak1  x = ak2 end`, SPAWN B `y = bk` | primary | expressible (ambiguity 1) |
| P09b | `variants/P09b.or.ab1`: `{begin x = ak1  x = ak2 end or y = bk}` | named variant | (see P09) |
| P09c | `P09c.ab1`: gt, le, pos, nonneg, gen, sum3; `begin gen(gk, s) sum3(s, total) end` | primary | **expressible with reformulation** (> and ≤) |
| P09d | `P09d.ab1`: genu, sum3; `begin genu(gk, s) sum3(s, total) end` | primary | expressible |
| P09e | `P09e.ab1`: `begin x = y + ek1  y = x - ek2 end` | primary | expressible |
| P10a | `P10a.ab1`: b as the list of its values; each stage extends it | primary | **expressible with reformulation** (replacement) |
| P10b | `P10b.ab1`: stage 1 `dbl` with `key` and `dbl(b, d)`; stages 2-4 as P10a | primary | **expressible with reformulation** (replacement; the standing relation over the lists) |
| P10c | `P10c.ab1`: as P10a; stage 2 `d = [dv1&dt1]  dv1 = dk * bv1` | primary | **expressible with reformulation** (replacement) |
| P10d | `P10d.ab1`: pick, gt, pos; `pick(x)`; `gt(x, gtk)`; withdrawal as `pick(x3)` | primary | **expressible with reformulation** (> ; withdrawal by restating) (ambiguity 4) |
| P11a | none | - | **not expressible** (emit and ≥ in no one notation) |
| P11a | `variants/P11a.ne.abs`: `{pick(x), not(x = gelo), tout("emit", x)}` | named variant | meaning changed: ≥ k written as ≠ the one value of pick below k |
| P11b | none | - | **not expressible**, as P11a |
| P11b | `variants/P11b.ne.abs`: `{pick(x), tout("emit", x), not(x = gelo)}` | named variant | meaning changed, as P11a's |
| P11c | `P11c.abs`: pick; `{pick(x), tout("emit", x)}`; `not(x = nek)`; commit: empty | primary | expressible (ambiguity 5) |
| P11d | `P11d.abs`: pick; `{pick(x), tout("emit", x)}`; commit: empty; `not(x = nek)` | primary | expressible (ambiguity 5) |
| P12a-d | `P12x.nN.ab1`: gtz, choice, accept; `begin choice(n, s) accept(s) end` | primary | **expressible with reformulation** (n > 0) |

Expressibility is the author's judgement, recorded before any run; it
anticipates no outcome. Several of these texts may well run to the budget
or never report (P09a in the order A then B, P09c, P09d, P10d, P12 at
n = 16); that is a result, not a reason to reformulate.

### P09

- **P09a, P09b: spawned computations in a system with one computation.**
  The primary programs give each computation's text, as the problem states
  it, in its own SPAWN subsection, and the harness spawns them in the
  instance's order (`side_by_side: false`, harness README 3.6). Absys has
  one computation per session: B's text is accepted into the derivations
  that hold A, so the two are conjoined (QUESTIONS, A5). Every relation is
  transcribed and the computations are posed with the protocol's own
  `spawn` for a configuration that cannot run them side by side; that B is
  then conjoined with A is the configuration's behaviour, which the
  problem's observations ask about ("whether A's failure affects B"). The
  author therefore judges P09a and P09b *expressible*, with these as the
  primaries. The other reading, that "not conjoined" cannot be met and the
  sub-problems are *not expressible*, is ambiguity 1.
- **Named variants:** FE69 describes the conjunctions an `or` makes as
  "parallel non-interacting programs". `variants/P09a.AB.or.ab1` and
  `P09a.BA.or.ab1` write the two computations as the two alternatives of
  one `or`, in the instance's spawn order; `variants/P09b.or.ab1` likewise,
  in the order written. Each computation is then a derivation of its own.
  Not primary, chosen before any run: it states a disjunction the problem
  does not, and does not pose the computations with `spawn` (the `or` is
  given before the SPAWN subsections, which are left empty, so both
  computations' answers are read from the one state). R: the `or` and its
  braces.
- **P09c.** gen's comparisons n > 5 and n ≤ 5 are reformulated, all R, as
  P05's x > k was in batch 1B: `gt(a, b)` is `a = b + d'` and `pos(d)`;
  `le(a, b)` is `b = a + d'` and `nonneg(d)`; `nonneg(q)` is
  `{q = 0 or pos(q)}`; `pos` is batch 1B's text. Over the integers these
  are exactly > and ≤, on every input, so the author judges P09c
  *expressible with reformulation*. The limit recorded for P05 applies:
  with a known argument that is not positive, `pos` has no failing
  derivation (the recursion goes on down), so a case whose guard is false
  does not fail; it keeps elaborating. The meaning is kept; the operational
  behaviour is not a primitive comparison's. The bound 5 of gen's
  definition is in the block as `gmax`, tagged as vocabulary, not a stage
  constant, so that a verifier can change it too.
- gen, genu and sum3: each case's head as equations on the lambda's
  parameters (Elcock 1990's `app`), then the case's conjuncts in the order
  written; n + 1 as a fresh unknown `g1' = g + 1` before the application
  that uses it (`SPECIFICATION.md`, Arithmetic: compound or decomposed is a
  transcription). sum3's head ⟨p, q, r⟩ ++ m is the list `[p';q';r'&m']`.
  P09c and P09d are one conjunction each, `begin … end`, as P02c and P07
  (one stage of several relations is one assertion, with one budget).
- **P09d** needs no comparison and is a transcription. It is one text for
  both readings, P09d1 and P09d2.
- **P09e** is the two relations as one conjunction, the constants 1 and 1
  in the block.

### P10

- **Replacement (P10a-c).** An Absys variable takes one value and keeps
  it: an equation is an assertion, not an assignment (`docs/decisions.md`
  rules 9, 17; `examples/assertions-not-assignments.abs`), and a second
  value for b makes every derivation fail. So the replacement the problem
  states cannot be transcribed. Reformulation, R: a named quantity is the
  **list of the values it has taken, in order, with an open tail**, its
  current value the last element. "b becomes e" equates the tail with
  `[v&t]`, v a new name for the new value equated with e (a b inside e
  being the name of the previous value), t the new tail:

      stage 1  begin b = [bv1&bt1]  bv1 = c1 end
      stage 2  begin bt1 = [bv2&bt2]  bv2 = bv1 + c2 end
      stage 3  begin bt2 = [bv3&bt3]  bv3 = c3 end

  This is indexing written for the purpose, which the problem names as
  reformulation. It keeps the meaning: after each stage the last element
  is the value the problem gives, on every input. Earlier values stay in
  the list (the problem's observation on retrieval). The encoding is
  chosen from the problem's vocabulary (b and d are named quantities that
  replacing stages change), not from any later stage's content.
- **P10b, the standing relation.** "d = 2 · b, at all times" is, in this
  encoding, a relation between the two lists, item by item: `dbl(b, d)`,
  written as FE69's `map`, with `key p` so that it waits for b's values
  (`docs/decisions.md` rule 21: without the key, `map` on a list not yet
  present makes lists of every length and never stops). Its recursion over
  the lists, its null case and its head equations are R; `e = dk * r` is
  the problem's relation; `key p` is C (`METRICS.md`, class C). dbl is
  defined in stage 1, with the application, since it is stage 1's
  information. Stages 2-4 are P10a's stages 1-3, the same text.
- **P10c, the snapshot**: stage 2 is d's first value, computed once from
  b's current value, `d = [dv1&dt1]  dv1 = dk * bv1`; no relation between
  the lists is stated, so d keeps its value when b is replaced.
- **P10d, retraction.** Stages 1 and 2 are P05a's `pick(x)` and
  `gt(x, gtk)`, with batch 1B's pick, gt and pos. Absys cannot withdraw an
  assertion: the derivations that x > k made fail are gone, and every
  later assertion is added to those that remain. Stage 3 therefore
  **restates the information not withdrawn**, `pick(x3)`, of a new unknown
  x3 that stands for x from that stage on; the derivations that hold
  x > k are left as they are, and x3 is not related to x. R: the whole of
  stage 3's text, and the name x3. It keeps the meaning (x3 ranges over the
  valid outcomes, on every input), so the author judges P10d *expressible
  with reformulation*. That it needs restating is what the problem's
  observation asks; ambiguity 4 gives the other reading.
- Constants: `c1`, `c2`, `c3`, `dk`, tagged by stage; in P10b `dk` is used
  inside dbl, given with stage 1. The value names `bv1`..., `bt1`...,
  `dv1`, `dt1` are R, not constants.

### P11

- **P11a, P11b: not expressible.** Both need emit and x ≥ k. Emit is
  `tout`, which only the 1990 notation has (Notation, above); x ≥ k is a
  comparison, which no notation has, and the only reformulation that keeps
  its meaning on every input is built from arithmetic, which only the 1969
  notation has (`docs/decisions.md` rule 23; batch 1B's `pos`). No single
  notation, and so no program, has both. Writing ≥ in the 1990 notation
  without arithmetic is possible only for particular values, which changes
  the meaning. So, by `SPECIFICATION.md`, expressibility, P11a and P11b are
  *not expressible* in every configuration, and there is no primary.
- **Named variants** `variants/P11a.ne.abs`, `variants/P11b.ne.abs`:
  the 1990 notation, with x ≥ k replaced by `not(x = gelo)`, gelo being the
  one value of pick's facts below k (1 for the problem's facts and k = 2).
  On pick's facts as given that is x ≥ k; on other values it is not, and a
  variant whose facts or k leave no value or two values below k needs
  another text. The conjuncts are in the problem's order, one conjunction.
  To be run and reported as named variants.
- **P11c, P11d** (1990): pick as the completion of its facts; stage 1
  `{pick(x), tout("emit", x)}`, the two in order, one conjunction; x ≠ k as
  `not(x = nek)`, negation and equality being the problem's connectives
  (x is bound by pick by then, so `not`, which is decided on the bindings
  as they stand, decides x ≠ k). `tout("emit", T)` is the harness's emit
  (harness README 3.10); its tokens `tout ( "emit" , )` are H, `x` is P.
- **Commit** (P11c stage 3, P11d stage 2): Absys has no construct that
  selects one derivation, and keeps every derivation live (QUESTIONS,
  A6). The section is comments only. The problem provides for a system
  that cannot select ("judged on every entry it emitted"), so the author
  records the commit as having no construct, and P11c and P11d as
  *expressible*; ambiguity 5.
- No control is used to avoid *extra* (the problem's rule: any deferral the
  program arranges is C); there is none to use.

### P12

- **n > 0.** choice's guard is a comparison. Here the systems file's own
  example applies (`systems/absys/README.md`, Notation: "replacing n > 0 by
  an enumeration of the finitely many values used"): choice is applied
  only to n, n − 1, …, 0, and n is at most 16 (the sizes are structure,
  not varied by the hidden variants). `gtz(q)` is `{q = 1 or … or q = 16}`,
  which is q > 0 on every input the problem uses, and terminates. R: gtz.
  It is preferred to batch 1B's `pos` here because `pos` on q = 0 never
  fails, and would leave an endless derivation at every leaf of the tree,
  so that *budget* would say nothing about the strategy. The same gtz text
  (1..16) is in every file, so that its cost per application does not vary
  with n. A classifier may count the enumeration as a generator of values
  (C) rather than a definition (R); it is applied only to known values.
- choice: case 1 `w = []`; case 2 its head equation `w = [e'&t']`, then
  `gtz(m)`, then `{e = 'l' or e = 'r'}` in that order, then
  `m1' = m - 1` and `choice(m1, t)`. The atoms ʟ and ʀ are `'l'` and `'r'`.
- accept is the completion of its facts (two for P12a, one for the
  others), each fact a constant in the block (`acc1`, `acc2`), given with
  the prelude, tagged stage 1. "ʟ repeated n times" is written out for
  each n, so each n has its own file; the facts are transcribed, with no
  relation to build them from n.
- n is the harness's parameter (`% PARAMETERS n`, README 3.4). The query
  is one conjunction, choice then accept, in the order given (no move).
  No search is written by hand: the strategy is the configuration's.

### Idioms and their sources

| idiom | source | used in |
|---|---|---|
| a relation as `name'=lambda x begin {A or B} end`, primes for new local names | Foster and Elcock 1969, `map`, `item` (`examples/map.ab1`, `examples/triples.ab1`) | P09, P10b, P10d, P12 |
| a case's head as equations on the lambda's parameters | Elcock 1990 p. 8, `app` (`examples/append.abs`) | P09, P12 |
| loop as a procedure whose body applies itself | the reconstruction's tutorial, ch. 5 | P09a |
| rev and conc | batch 1A's texts (P03e) | P09a |
| a closed world as the completion of its facts | Elcock 1990 p. 15 (`examples/students.abs`) | P10d, P11, P12 |
| alternatives as "parallel non-interacting programs" | Foster and Elcock 1969 (tutorial ch. 5; `examples/alternatives.ab1`) | P09a, P09b variants |
| arithmetic as an assertion usable in every direction | Foster and Elcock 1969 (tutorial ch. 8); Foster 1968, pass sets | P09c-e, P10, P12 |
| gt, pos (> from arithmetic) | batch 1B, P05 | P09c, P10d |
| `begin … end` for one conjunction | Foster and Elcock 1969 (`docs/decisions.md`, Three notations) | P09-P12 |
| a relation over each item of a list, with `key` so that it waits for the list | Foster and Elcock 1969, `map` (`examples/map.ab1`; `docs/decisions.md` rule 21) | P10b |
| a list with an open tail, extended by equating the tail | Foster and Elcock 1969, `[h&t]` (tutorial ch. 8, ch. 10) | P10a-c |
| `tout(label, term)`, output when the term is complete | Elcock 1990 note 11 (tutorial ch. 9; `docs/decisions.md` rule 20); the harness's emit | P11 |
| `not(A)` | Elcock 1990 p. 14 (tutorial ch. 7) | P11 |
| `{A, B}` for one conjunction (1990) | Elcock 1990 p. 8 | P11 |

### Constants

As in batches 1A and 1B: one block per program, one constant per line,
each tagged with the stage that uses it, referred to by name only in that
stage (or, for facts and the bound of a definition, in the prelude, given
at stage 1). The names are used for nothing else. No program depends on
the values within the problem's domain: P09's are any sequence (`ra`) and
any integers; P10's any integers; P11c-d's any integers (pick's facts and
k); P12's accept facts any sequences over 'l' and 'r'. The exceptions are
said where they arise: the P11 variants (gelo), and P12's gtz, which
covers n up to 16.

## Ambiguities, and the readings taken

1. **P09a and P09b, "separate computations" in one computation.** Absys
   has no separate computations, and the harness accepts a spawned text
   into the one session (QUESTIONS, A5). The reading taken: the protocol's
   `spawn`, for a configuration that cannot run computations side by side,
   is how the sub-problem is posed, and the program transcribes each
   computation; that the second is conjoined with the first is a result.
   So *expressible*, with the SPAWN programs as primaries. The other
   reading, that "not conjoined" is part of the problem and cannot be met,
   would make both *not expressible*, with the SPAWN programs and the `or`
   programs as named variants. The classifiers may take it.
2. **P09c's bound 5** is part of gen's definition, not a stage constant
   (`stages.json` gives only gen(<k>, s)). It is in the block as `gmax`,
   marked as vocabulary, so that a verifier can vary it if a variant does.
3. **P10's quantities as lists.** The encoding chosen at stage 1 is
   justified by the vocabulary (named quantities, replacing stages), not by
   any later stage. `observe()` asks for `b` and `d`, which are the lists of
   values; the current value is the last element, also printed under its
   own name (`bv3`, …). Whether the classifiers read the list or the last
   value as "b" is theirs to say; both are reported.
4. **P10d, withdrawal by restating.** The program restates the
   information that is not withdrawn, of a fresh unknown x3, at the
   withdrawing stage. It is the program, not the harness, that works out
   what remains (the contract forbids the harness to). The author judges
   it a reformulation that keeps the meaning (*expressible with
   reformulation*). The other reading, that a withdrawal Absys cannot
   perform is not expressible and restating is a different program, would
   make P10d *not expressible* with this program as a named variant. The
   old x, with x > k, is still held, and `? x` reports it; the current
   unknown is x3.
5. **P11's commit in a system that never selects.** The commit stage has
   no construct; its section is comments only (QUESTIONS, A6). Taken as
   *expressible*, since the problem says how a system that cannot select
   is judged. One could instead record commit as not expressible.
6. **≠ as `not(x = k)` (P11c, P11d).** Taken as a transcription (negation
   and equality, the problem's connectives), since x is bound when it is
   decided. A classifier might class it R, as a replacement of the
   primitive ≠.
7. **P12's facts depend on n.** `stages.json` says the program holds them;
   one file per sub-problem and n, each fact written out. The verifier
   substitutes each file's block.
8. **Several relations in one stage** (P09c, P09d, P09e, P10, P11, P12)
   are one conjunction, as P02c (batch 1A, ambiguity 2).
9. **Which unknowns are reported.** Named as `stages.json` names them
   (`x`, `b`, `y`, `s`, `total`, `d`), except P10d's x3 (ambiguity 4).
   Lambda-local names are primed (1969) or capitals (1990) and distinct
   from them.

## What was read, and anything outside the brief

Read: the brief's list, that is `README.md`, `SPECIFICATION.md`,
`METRICS.md`, `PROTOCOL.md`, `AMENDMENTS.md`, `problems/README.md`, the
problem files of P09-P12 and of P03, P04 and P05, `systems/absys/README.md`,
`harnesses/README.md`, `harnesses/stages.json`, `harnesses/absys/`
(`README.md`, `QUESTIONS.md`, `S-mechanisms.md`, `check`, a search of
`absys_harness.py` for its handling of spawn, notation and tout, the
qualification's `README.md`, file list and programs `x17-spawn.abs`,
`x18-emit.abs`, `x19-parts.abs`, `x20-arith.ab1`), batch 1A and 1B's
programs (some read in full: P03e, P04a, P05a-c, P06a, P07b, P08c) and
this README. In the image, with `container run … cat`/`ls`/`grep` (no
Absys program, harness `run` or interpreter was run on anything):
`docs/decisions.md`, tutorial chapters 04-10, every program text in
`examples/` (not their `.out` files), and a search of `README.md`,
`tutorial/` and `docs/decisions.md` for "tout" and "notation". Not read:
tutorial chapters 01-03, the reconstruction's `src/`, `docs/research.md`,
`research/`.

Something outside the brief's list was in the author's context without
being opened: at the start of the session its environment supplied the
two-line index of an auto-memory file under `~/.claude/projects/…`. The
files it points to were not opened. Nothing else outside the list was
read.

# Batch 1D: P13, P14, P15, P16

*Phase 5, wave 1, against `spec-1.0.1` and the contract of
`harnesses/absys/README.md`. No program here has been run. Only
`harnesses/absys/check` was used, and it reports no errors and no warnings
for any of them, primary or variant, in each of the three configurations.*

**Author of every program:** `implementation-absys`, an agent (Claude
Opus 5.5, model id `claude-opus-5-5`), in a fresh context with no other
knowledge of this study than the files listed at the end. It had not seen
any earlier work on it, and in particular no result of batches 1A-1C.

**Precursor programs (E01-E09): not seen.** No text of them was read:
`/opt/src/absys/research/`, `/opt/src/absys-measure/research/` and
`/opt/src/absys/docs/research.md` were not opened. None of P13-P16 was
seen in any form other than its problem file.

## Layout

    programs/absys/<configuration>/P13a.ab1 P13b.ab1 P13c.ab1 P13d.ab1 P13e.ab1 P13f.ab1
                                  P14a.ab1 P14b.ab1 P14c.ab1
                                  P15a1.abs P15a2.abs P15b.ab1 P15b2.ab1 P15c.ab1 P15d.abs
                                  P16a.n<N>.<order>.ab1   (N = 100, 1000, 10000; order = ascending, descending, interleaved)
                                  P16b.n<N>.ab1  P16c.n<N>.ab1  P16d.n<N>.ab1  P16d2.n<N>.ab1
    programs/absys/<configuration>/variants/P13a.eq.ab1 ... P13d.eq.ab1   named variants

for each of `absys`, `absys-depth-first`, `absys-wake-back`. **The three
configurations share one text** for every sub-problem and variant, byte
for byte, for the reason given for batch 1A: the flags change how the
machine schedules derivations and returned relations, not the language,
so the natural program is the same text in each.

Which file serves which instance of `stages.json`:

| instances | file |
|---|---|
| `P13x.n100` … `P13x.n100000` | `P13x.ab1`: n is the harness's parameter (`% PARAMETERS n`, README 3.4) |
| `P14a`, `P14b`, `P14c`, `P15a1`, `P15a2`, `P15b`, `P15b2`, `P15c`, `P15d` | the file of that name |
| `P16a.n<N>.<order>`, `P16b.n<N>`, `P16c.n<N>`, `P16d.n<N>`, `P16d2.n<N>` | the file of that name: one per instance, the relations written out (P16, below) |

## Notation

By the rule of `systems/absys/README.md` (the earliest notation with every
construct the problem needs):

| sub-problem | notation | why |
|---|---|---|
| P13a-d | 1969 | range's m > n and m ≤ n are comparisons, which no notation has; reformulated with arithmetic, 1969 only (as P09c, batch 1C) |
| P13e, P13f | 1969 | arithmetic, and `key` for the consumer (both 1969 only) |
| P14 | 1969 | arithmetic (c + 1) and `key` |
| P15a1, P15a2 | 1990 | b ≠ ⟨⟩ needs `not`, 1990 only; no arithmetic |
| P15b, P15b2 | 1969 | i = j + 1 needs arithmetic (1969 only), and h ≠ e, b ≠ ⟨⟩ need `not` (1990 only): constructs in no single notation. 1969 is used, with both ≠ reformulated, as P05a (batch 1B) |
| P15c | 1969 | alternatives and equations |
| P15d | 1990 | the cases' "otherwise" (holder ≠ none, queue ≠ ⟨⟩) needs `not`; no arithmetic |
| P16 | 1969 | arithmetic (succ) |

## Per configuration and sub-problem

The same entries hold for `absys`, `absys-depth-first` and
`absys-wake-back`. "S used": none anywhere (`harnesses/absys/S-mechanisms.md`;
no program contains code that supplies a mechanism the configuration
lacks). C constructs: `key` in P13e, P13f and P14 only.

| sub-problem | program | primary or variant | expressibility, as the author sees it |
|---|---|---|---|
| P13a | `P13a.ab1`: gt, le, pos, nonneg, range; `range(rk, n, s)` | primary | **expressible with reformulation** (> and ≤) |
| P13b | `P13b.ab1`: the same and sum; `begin range(rk, n, s) sum(s, k) end` | primary | **expressible with reformulation** |
| P13c | `P13c.ab1`: the same, conc and rev; `begin range(rk, n, s) rev(s, r) end` | primary | **expressible with reformulation** |
| P13d | `P13d.ab1`: the same, revacc and racc; `begin range(rk, n, s) revacc(s, r) end` | primary | **expressible with reformulation** |
| P13a-d | `variants/P13x.eq.ab1`: range with m > n as m = n + 1 and m ≤ n dropped | **named variant** | meaning changed (calibration's range: `systems/absys/README.md`, Notation) |
| P13e | `P13e.ab1` (native): upto, total; `begin upto(n, [], s) total(s, 0, k) end` | primary | expressible (native: not reformulation, METRICS.md rule 18) |
| P13f | `P13f.ab1` (native): upto, backw; `begin upto(n, [], s) backw(s, [], r) end` | primary | expressible (native) |
| P14a | `P14a.ab1`: run with `key`; stage 1 `run(ms, 0)` and the first message; one message per stage | primary | expressible |
| P14b | `P14b.ab1`: run; `run([...], 0)` | primary | expressible |
| P14c | `P14c.ab1`: P14a's text, and stages 6 and 7 | primary | expressible |
| P15a1, P15a2 | `P15a1.abs`, `P15a2.abs` (the same text): merge; `merge(ma, mb, m)` | primary | expressible |
| P15b | `P15b.ab1`: gt, pos, ne, zeros, merge, position; `begin zeros(z) merge(z, bs, m) position(pk, m, i) end` | primary | **expressible with reformulation** (h ≠ e; b ≠ ⟨⟩ and a ≠ ⟨⟩) |
| P15b2 | `P15b2.ab1`: the same, `merge(bs, z, m)` | primary | **expressible with reformulation** |
| P15c | `P15c.ab1`: grant; `grant(ga, gb, g)` | primary | expressible (ambiguity 7) |
| P15d | `P15d.abs`: app, request, release; holder and queue as lists of values | primary | **expressible with reformulation** (replacement; ++) |
| P16a | `P16a.n<N>.<order>.ab1`: succ; the n − 1 relations as one conjunction in the order; `x<j> = xjk` | primary | expressible |
| P16b | `P16b.n<N>.ab1`: succ; SPAWN C1-C4, each its segment as one conjunction; total; `x1 = bk` | primary | expressible (ambiguity 10) |
| P16c | `P16c.n<N>.ab1`: succ; x then y relations as one conjunction; `x1 = ck2`; `y1 = ck3` | primary | expressible |
| P16d | `P16d.n<N>.ab1`: the same stage 1; `x1 = dk2`; `x<n> = dk3` | primary | expressible |
| P16d2 | `P16d2.n<N>.ab1`: the same stage 1; `x<n> = x1` | primary | expressible |

Nothing was judged *not expressible*. Expressibility is the author's
judgement, recorded before any run; it anticipates no outcome. Several of
these texts may well run to the budget or report nothing in some
configurations (P13a-d, whose guards never fail when false; P13e and P13f,
whose builder goes on below 0 after the answer; P15b under depth-first
search; P16d2's contradiction, which no value reveals); that is a result,
not a reason to reformulate.

### P13

- **The prescribed tasks (P13a-d).** range's guards m > n and m ≤ n are
  comparisons, which no notation of the pinned reconstruction has. They
  are reformulated exactly as batch 1C's gen (P09c) was: `gt(a, b)` is
  `a = b + d'` and `pos(d)`; `le(a, b)` is `b = a + d'` and `nonneg(d)`;
  `pos` and `nonneg` are batch 1B's and 1C's texts, unchanged. Over the
  integers these are > and ≤ on every input, so the solutions of range are
  the problem's on every input (any start <k>, any n), and the author
  judges P13a-d *expressible with reformulation*, with these as the
  programs of record (`systems/absys/README.md`, Notation: "where a
  reformulation without the comparison keeps the meaning on every input
  … it is the program of record"). R: gt, le, pos, nonneg. The rest is
  transcribed: range, sum, conc, rev, revacc and racc by their cases, in
  order, each head as equations on the lambda's parameters (Elcock 1990's
  `app`), then each case's conjuncts in the order written; m + 1 as a fresh
  unknown `a1' = a + 1`.
- **What the reformulation does to the prescribed algorithm**, recorded so
  that the classifiers can weigh it (ambiguity 1): `pos` of a known
  argument has no failing derivation (batch 1B, P05). So at every level of
  range the case whose guard is false (case 1 while m ≤ n, case 2 at
  m = n + 1) leaves a derivation that never ends, and the guard that is
  true costs steps in proportion to n − m, with an endless derivation of
  its own beyond its success. The problem operations of range, sum, rev and
  racc are still the problem's; the work added is the guards'.
- **Named variants** `variants/P13x.eq.ab1`: range with m > n written
  m = n + 1 and m ≤ n dropped, the calibration reformulation that
  `systems/absys/README.md` names as changing the meaning (with a start
  above n + 1 it has no solution, where the problem has s = ⟨⟩; case 2
  applies again at m = n + 1 and goes on for ever). Not primary, chosen
  before any run. To be run and reported.
- conc and rev are batch 1A's texts (P03e) with their local names renamed
  (`h, t, u, v, w` for `h, k, m, n, r`), so that no local name is one of
  this text's top-level names: the parameter `n` and the unknowns `s`, `k`,
  `r`. Renaming changes no token's class.
- racc's case 2 holds "for every sequence b"; Absys does not restrict an
  unknown to sequences, and here the place is always a list.
- **The native tasks (P13e, P13f).** The algorithm, recorded as the
  problem asks: ⟨1, …, n⟩ is built by counting q down from n to 0 with an
  accumulator (`upto(q, a, w)`: w = ⟨1, …, q⟩ ++ a), so that it is built
  from its last element to its first with no concatenation, and bound to s
  by one equation when q = 0. P13e then sums it with a running total
  (`total`), P13f reverses it with an accumulator (`backw`): both linear,
  and both written with `key p`, FE69's `map` idiom, so that they wait for
  the list instead of making lists of every length (`docs/decisions.md`
  rule 21). The sequence is built and held, as the problem requires.
  upto's second case has no guard q > 0: no notation with arithmetic has a
  comparison or a negation, and pos would leave an endless derivation at
  every step. Without the guard the text is correct for every n ≥ 0, which
  every instance has (n is structure, not a constant): at q = 0 the first
  case gives the sequence, and the second goes on below 0, where the first
  never holds again; that derivation never gives a solution and never
  ends (ambiguity 2). P13e and P13f have no stage constant
  (`stages.json`), so no constants block.

### P14

- run is the problem's relation, its three cases in order, each head as
  equations on the lambda's parameters; c + 1 as a fresh unknown
  `c1' = c + 1`. The problem allows a relation or a process, and says both
  are transcriptions (P). In Absys the relation is the process: an
  application of run waiting for the next cell of its list holds the
  count as its argument.
- `key p` (C, as in batch 1C's P10b): without it, run applied to a list
  not yet present would make lists of every length (FE69's `map`;
  `docs/decisions.md` rule 21) instead of waiting for the next message.
- **Messages.** ɪɴᴄ is the atom `'inc'`; ʀᴇᴀᴅ(r) is the list `['read';r]`,
  Absys having no other compound term. The stream is a list `ms` with an
  open tail. Stage 1 starts the counter, `run(ms, 0)` ("the messages are
  posed with run(m, 0)"), and gives the first message, `ms = [inc1&t1]`;
  each later stage equates the open tail with `[message&new tail]`. No
  stage closes the stream.
- P14b is one stage, `run([inc1;inc2;['read';r1];inc4;['read';r2]], 0)`,
  with the same run.
- Constants: `stages.json` writes each ɪɴᴄ stage as "message <atom>", so the
  atom of each ɪɴᴄ message is a constant (`inc1`, `inc2`, `inc4`, `inc6`),
  tagged by stage. ʀᴇᴀᴅ's tag `'read'` and run's `'inc'` are vocabulary.

### P15

- **P15a** (1990): merge's four cases in order, each head as equations,
  then the guard, then the recursive application. b ≠ ⟨⟩ is
  `not(B = [])`: negation and equality, the problem's connectives (as
  batch 1C took x ≠ k in P11c); the arguments are known, so `not` is
  decided at once. P15a1 and P15a2 are the same text; the harness's cap
  makes the answer mode.
- **P15b, P15b2** (1969): zeros, its one case, as an unbounded producer,
  under P09d2's stream reading (batch 1C's genu). merge as in P15a, but
  the 1969 notation has no `not`, so case 3's b ≠ ⟨⟩ and case 4's a ≠ ⟨⟩
  are written as the patterns `q = [g1'&v1']` and `p = [g2'&v2']`, which
  for sequences (merge's arguments are sequences) is the same: R.
  position's h ≠ e is `ne(h, e)`, batch 1B's reformulation (`gt(a, b) or
  gt(b, a)`, with gt and pos), R; i = j + 1 is the problem's. The query is
  one conjunction, in the order given. Nothing is written for fairness:
  the problem asks whether the system's own merge is fair, and adding an
  arbitration would be C. Limits, recorded for the classifiers: ne is ≠
  only for integers (the items here are integers: zeros' 0 and the items
  of <seq>); and with h = e the case 2 guard does not fail, it never ends,
  as pos with a known argument never fails.
- **P15c** (1969): grant's two cases, `{w = p or w = q}`. Absys keeps both
  derivations and has no construct that selects one (harness QUESTIONS,
  A6, A8); `answers(1)` reports the first printed. Nothing is written for
  commitment (ambiguity 7).
- **P15d** (1990): holder and queue are named quantities "as in P10", and
  are encoded as batch 1C encoded P10's: each the list of the values it
  has taken, with an open tail (R). They start, in the prelude, as
  `'none'` and `[]` ("starting as none and ⟨⟩"). Each stage equates both
  tails with `[new value|new tail]` and states the stage's case relation
  between the old values and the new: `request(p, h, q, h2, q2)` and
  `release(p, h, q, h2, q2)`, their cases in the problem's order. A
  quantity a case does not mention keeps its value (`Q2 = Q`, `H2 = H`).
  "Otherwise" is `not(H = 'none')` and `not(Q = [])`; "where holder = p"
  is `H = P` in each case of release. queue ++ ⟨p⟩ needs concatenation of
  a list already held, which Absys has only as a relation defined for it:
  Elcock 1990's `app`, R. The problem allows a process instead; the
  quantities are written as P10's so that `observe()` reads them by name.
  none is the atom `'none'`.

### P16

- succ is defined as the vocabulary gives it, `succ'=lambda a, b begin
  b = a + 1 end`, and every relation is an application of it,
  `succ(x1, x2)`. The unknowns x_1 … and y_1 … are `x1` … and `y1` ….
- **Each instance is its own file**, with its relations written out in the
  instance's arrival order, as P12's facts were (batch 1C). Sizes and
  orders are structure, not constants (`stages.json`, about), and the
  hidden variants do not vary them. Writing the order into the text, not
  choosing it with the program's own code from the `order` parameter,
  avoids steps and C tokens the problem does not have (harness QUESTIONS,
  A9; batch 1B's P07a). The files were written by a shell script from the
  problem's definitions of the orders; the script is not part of the
  program and is not in the repository (ambiguity 9).
- **Each stage's relations are one conjunction**, `begin … end`, one
  assertion with one budget, in the order given, as P02c and P07 (batch
  1A, ambiguity 2). In P16b, each contributor's segment is one
  conjunction, in its own SPAWN subsection (`C1`-`C4`, as `stages.json`
  names them). Layout: a hundred relations to a line, which changes no token (fewer lines make `check`, which parses the assertion again after each line, fast enough to run).
- P16a stage 2: `x<j> = xjk`, j = ⌈n/2⌉ (50, 500, 5000), which is
  structure; the value is the constant. P16b stage 2 is written as the
  problem writes it, `total = x1 + x<m+1> + … + x<4m+1>`, a compound
  relation (`SPECIFICATION.md`, Arithmetic). P16d2's stage 2 is
  `x<n> = x1`; it has no constant, so no block.
- Constants: `xjk`, `bk`, `ck2`, `ck3`, `dk2`, `dk3`, tagged by stage.

### Idioms and their sources

| idiom | source | used in |
|---|---|---|
| a relation as `name'=lambda x begin {A or B} end`, primes for new local names | Foster and Elcock 1969, `map`, `item` (`examples/map.ab1`, `examples/triples.ab1`) | P13, P14, P15b, P15c, P16 |
| a case's head as equations on the lambda's parameters | Elcock 1990 p. 8, `app` (`examples/append.abs`) | P13, P14, P15 |
| alternatives of conjunctions, `{…} or {…}`, in the 1990 notation | Elcock 1990 p. 8 (`examples/append.abs`; tutorial ch. 4) | P15a, P15d |
| `app`, Elcock's own text | Elcock 1990 p. 8 | P15d |
| conc and rev | batch 1A's texts (P03e), locals renamed | P13c |
| gt, le, pos, nonneg (> and ≤ from arithmetic) | batch 1B (P05) and 1C (P09c) | P13a-d |
| gt, pos, ne (≠ from arithmetic) | batch 1B (P05a) | P15b |
| an unbounded producer | batch 1C's genu (P09d) | P15b |
| a relation over a list, with `key` so that it waits for the list | Foster and Elcock 1969, `map` (`examples/map.ab1`; `docs/decisions.md` rule 21) | P13e, P13f, P14 |
| a list with an open tail, extended by equating the tail | Foster and Elcock 1969, `[h&t]` (tutorial ch. 8, ch. 10) | P14 |
| a named quantity as the list of its values | batch 1C's P10 | P15d |
| arithmetic as an assertion usable in every direction | Foster and Elcock 1969 (tutorial ch. 8); Foster 1968, pass sets | P13, P14, P15b, P16 |
| `not(A)` | Elcock 1990 p. 14 (tutorial ch. 7) | P15a, P15d |
| `begin … end` (1969), `{A, B}` (1990) for one conjunction | Foster and Elcock 1969 (`docs/decisions.md`, Three notations); Elcock 1990 p. 8 | P13, P15b, P15d, P16 |

These sources are cited as batches 1A-1C cite them. This batch's author
could not open the reconstruction's documentation itself (below).

### Constants

As in batches 1A-1C: one block per program, one constant per line, each
tagged with the stage that uses it, referred to by name only in that
stage. The names are used for nothing else. No program depends on the
values within the problem's domain: P13's start <k> any integer (with
the reformulated guards; the eq variants only for a start at most
n + 1); P14's ɪɴᴄ atoms are the message ɪɴᴄ; P15a's sequences any
sequences; P15b's <seq> and <k> any integers (ne is ≠ on integers only);
P15c's and P15d's atoms any atoms other than `'none'`; P16's values any
integers. P13e, P13f and P16d2 have no constants and no block.

## Ambiguities, and the readings taken

1. **P13a-d: expressible with reformulation, or not expressible.**
   `systems/absys/README.md` lists P13a-d's range among the sub-problems
   that need a comparison, and gives calibration's reformulation as one
   that changes the meaning. The reformulation taken here (batch 1C's,
   from P09c) keeps the meaning on every integer input, so by the rule it
   is the program of record. But P13's prescribed tasks are meant to hold
   the algorithm fixed, and these guards add work in proportion to n − m
   at every level and leave endless derivations. A classifier may judge
   that the prescribed algorithm is not kept, and P13a-d *not
   expressible*, with both programs as named variants.
2. **P13e, P13f: a native builder that does not stop.** No terminating
   count is writable in a notation with arithmetic, as far as the author
   could establish; the native builder gives the sequence and then goes on
   below 0 in a derivation of its own that never gives a solution. Whether
   ÷ could give a terminating sign test was considered and not used: its
   semantics could not be checked. The algorithm is recorded; whether the
   endless derivation makes the native program a different computation
   from the task is the classifiers'.
3. **`key` in a native program (P13e, P13f)** is C by the table, and P by
   METRICS.md rule 18 (a native algorithm's tokens are P). Both readings
   are open; the author records it as used for the native algorithm.
4. **P14's messages.** ʀᴇᴀᴅ(r) as `['read';r]` and ɪɴᴄ as `'inc'` is an
   encoding of the messages as Absys values, taken as P. The ɪɴᴄ atoms of
   the stages are constants because `stages.json` places a placeholder
   there; a variant that changed one to anything but ɪɴᴄ would leave run no
   case.
5. **Where P14's `run(m, 0)` is posed.** At stage 1, with the first
   message, not in the prelude: the problem poses the messages with it,
   and the prelude holds the definitions.
6. **P15b's ≠** reformulated with arithmetic (as P05a), and merge's
   ≠ ⟨⟩ as a pattern; P15a's merge is a different text (1990, with `not`),
   by the rule for notations.
7. **P15c's committed choice.** Absys has no construct that commits to one
   derivation. The query is *any one*; the program states the relation, and
   whether the choice is committed is the system's behaviour, as the
   problem's observation asks. Taken as *expressible*, as P11's commit was
   (batch 1C, ambiguity 5).
8. **P15d's "otherwise" and the precondition.** Otherwise is ≠, written
   with `not` (the systems file lists P15d among the sub-problems needing a
   comparison; the 1990 `not` decides holder ≠ none and queue ≠ ⟨⟩ since
   both are known). "where holder = p" is a condition of each case of
   release. Initial values in the prelude, since the problem gives them
   before stage 1.
9. **P16's relations written out.** One file per instance; the files were
   generated by a shell script from the problem's definitions of the
   orders (`bash` and `awk`, writing text only; nothing was executed on a
   program). A verifier substitutes each file's block.
10. **P16b: spawned contributors in one computation.** The harness spawns
    the four into the one session, where they share every unknown
    (QUESTIONS, A5), and does not use the fallback. The program gives each
    contribution in its own SPAWN subsection; that the contributions are
    then one computation is the configuration's behaviour.
11. **Several relations in one stage** (P13b-f, P15b, P16) are one
    conjunction, as P02c (batch 1A, ambiguity 2); in P14a stage 1 the
    counter's start and the first message are two assertions.
12. **Which unknowns are reported.** Named as `stages.json` names them
    (`s`, `k`, `r`, `r1`-`r3`, `m`, `i`, `z`, `g`, `holder`, `queue`,
    `total`). P16's `x_1 … x_n` are not plain identifiers, so the harness
    asks for none of them by name (`unknown_names`); `?` prints every one.
    P15d's `holder` and `queue` are the lists of values; the current value
    is the last element, also printed as `h3`, `q3` (as P10, batch 1C,
    ambiguity 3).

## What was read, and anything outside the brief

Read: the brief's list, that is `README.md`, `SPECIFICATION.md`,
`METRICS.md`, `PROTOCOL.md`, `AMENDMENTS.md`, `problems/README.md`, the
problem files of P13-P16 and of P07, P09 and P10, `systems/absys/README.md`,
`harnesses/README.md` (sections 4 and 11 in full, and a search of the
rest), `harnesses/stages.json` (P13-P16, and its header), `harnesses/absys/`
(`README.md`, `QUESTIONS.md`, `S-mechanisms.md`, `check`, the parts of
`absys_harness.py` that read a program, substitute constants, name
unknowns and check; the qualification's `README.md` and every program in
`qualification/programs/`), batch 1A-1C's programs (P03e, P05a, P09a,
P09c, P09d, P10a, P10b, P10d, P11c, P12a.n8 in full) and this README.

**The reconstruction's documentation in the image was not read.** Two
attempts to read `/opt/src/absys` with `container run` (`tar` to copy it
out, then `ls`) were refused by the author's permission system; no other
attempt was made. Its idioms are cited above as batches 1A-1C cite them.

Commands other than `check`, disclosed: `python3 -c` three times, to read
and print the P13-P16 entries of `harnesses/stages.json` (reading a JSON
file; no program of the study); one accidental `python3 -` with no input,
which read nothing and ran nothing; `bash` and `awk` to write the P16
files and the P13 variants (text only); `sed`, `cp`, `diff`, `git`. No
Absys program, harness `run` or interpreter was run on a program or a
fragment of one.

Outside the brief's list: at the start of the session its environment
supplied the two-line index of an auto-memory file under
`~/.claude/projects/…`; the files it points to were not opened. The tool
that ran the author's commands saved one long output (the text of
`PROTOCOL.md` and `SPECIFICATION.md`, both on the list) to a file under
`~/.claude/projects/…/tool-results/`, which the author read back; it held
nothing but those two files. Nothing else outside the list was read.
