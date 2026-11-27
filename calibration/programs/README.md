# Calibration programs: P03 and P13

**Development examples, not results.** These programs exist so that two
classifiers can test the token-classing rules of `METRICS.md` across
programming styles before the freeze. Nothing here is a measurement.

- Author: an agent, Claude (Opus), acting as implementation author. It read
  only the public specification: `README.md`, `SPECIFICATION.md`,
  `METRICS.md`, `PROTOCOL.md`, `problems/01`, `problems/03`, `problems/13`
  and `systems/*/README.md`. For Absys it also read the reconstruction's
  `tutorial/` and `docs/decisions.md`. It did not read `reviews/`, the absys
  `research/` folder, or the absys `examples/` files.
- Specification: draft 0.5. Problem sizes: P13 at n = 10² only.
- Each program was fixed before it was run. None was revised after its
  output was seen, except `algol-60/p13.alg`: its first run stopped with a
  syntax error, because a semicolon inside its opening comment ended the
  comment. The comment was reworded ("never reclaimed; the arrays" became
  "never reclaimed, and the arrays"). No code changed.
- Each program's output is saved beside it with the extension `.out`.
- Tokens are not classed here. The comments in the programs say what each
  part transcribes or reformulates, as the protocol asks, but every class is
  left to the classifiers. Code marked "Harness (H)" is a stand-in for the
  harness that `PROTOCOL.md` fixes before the freeze. It is there only so
  that the programs can run.

## Exposure to precursor programs

- **Absys.** The tutorial contains the retrospective's append (`app`, ch.
  4), its accumulator reverse (`rev1` and `rev`, ch. 6), and `item` and
  `map` (ch. 8). The author read all of these. `examples/` holds
  `append.abs` and `reverse.abs`. The author saw their names in a directory
  listing but did not open them. The experiments E01 to E09 (absys
  `research/`) were not seen. P13f's reverse is the retrospective's
  `rev1`/`rev`, written in the 1969 notation, and was taken from the
  tutorial on purpose, as Absys's own idiom.
- **SWI-Prolog, Python, ALGOL 60.** No precursor program for this study was
  seen. conc and rev are the textbook `append` and naive reverse, which the
  author knew beforehand (Clocksin and Mellish, *Programming in Prolog*,
  1981).

## How they were run

| system | version | command |
|---|---|---|
| Absys | reconstruction at `/esoteric/absys`, `target/release/absys`, as built locally (commit not recorded; the provisional pin is `7bb61e6`) | `absys --steps 1000000 p03X.ab1`; `absys --steps 100000 p13X.ab1` |
| SWI-Prolog | 11.0.1, arm64-darwin | `swipl p03.pl`, `swipl p13.pl` |
| Python | 3.12.2 | `python3 p03.py`, `python3 p13.py` |
| ALGOL 60 | `algol60` at `/esoteric/algol-60`, `target/release/algol60`, report dialect (commit not recorded; the provisional pin is `6e8740c`) | `algol60 p03.alg`, `algol60 p13.alg` |

---

## Absys (`absys/`)

**Notation: 1969 (`.ab1`) throughout.** P03 needs lists, procedures and
`or`, which every notation has, so the 1969 notation is the earliest with
all of them. P13 needs arithmetic, which only the 1969 notation (and the
1982 one, derived from it) has. P13 also needs the comparisons > and ≤,
which **no notation has**. The 1969 parser refuses `<` and `>` ("`<` is not
in the 1969 notation"), and the 1990 and 1982 notations refuse them too. Nor
is there `not` in the 1969 notation, which could have stood in for ≤.

**One text per query.** In Absys every identifier outside a lambda is shared
by the whole text, and each assertion is added to every live derivation. Six
queries in one text would share names, and the three derivations of P03b
would each carry every later query, so each query is a separate text
holding the definitions and that query alone. P13's two- and three-part
queries are each one assertion, `begin … end`, because a query is one stage.

Idiom sources: tutorial ch. 8 and `docs/decisions.md` rules 6, 21 to 23.
These cover the 1969 notation: `name' = lambda … {… or …}`, primes for new
names, `[h&t]` and `[1;2;3]`, `begin … end`, and arithmetic as an
assertion. The primed top-level name (`conc' = lambda`) follows FE69's
`item'=lambda` as the tutorial gives it.

No external mechanisms, by the systems file. Flags: the defaults (fair
search, body in place, `not` immediate, wake to the front), except
`--steps`.

### P03 (`p03a.ab1` to `p03f.ab1`)

conc and rev are transcribed by cases, in the problem's order, with the
conjuncts in its order. There is one definition per relation, with no
reformulation, and it is used in every direction. Budget: `--steps 1000000`,
the protocol's 10⁶.

| query | reported | valid outcomes | state |
|---|---|---|---|
| P03a | c = [1;2;3] | c = ⟨1,2,3⟩ | 1 derivation, hibernating |
| P03b | (a, b) = ([], [1;2]), ([1], [2]), ([1;2], []) | the same three | 3 derivations, hibernating |
| P03c | b = [2;3] | b = ⟨2,3⟩ | 1 derivation, hibernating |
| P03d | a = [1;2] | a = ⟨1,2⟩ | 1 derivation, hibernating |
| P03e | b = [3;2;1] | b = ⟨3,2,1⟩ | 1 derivation, hibernating |
| P03f | a = [3;2;1] (derivation #101, hibernating) | a = ⟨3,2,1⟩, exactly one | budget: 900 derivations, 899 still elaborating, each with a longer partial `a` |

Every query was expressible.

### P13 (`p13a.ab1` to `p13f.ab1`)

**Representation:** Absys lists. `s = [h'&t']` takes the head and tail by
one equation.

**Not expressible as stated: range.** Both cases are guarded by a
comparison (m > n, m ≤ n), and Absys has none. range, and therefore every
P13 query, which all start with range(1, n, s), is *not expressible* in
any notation without supporting code. Supporting code could not supply it
either: Absys has no primitive that fails on a sign.

**Reformulation, marked in each text.** Case 1's test m > n is written as
the equation m = n + 1. That agrees with m > n for every call that
range(1, n, s) makes when n ≥ 0, but not for range in general. Case 2's
test m ≤ n cannot be written, and is left out. Consequence: when m = n + 1,
both cases apply. Case 1 gives the answer, and that derivation hibernates.
Case 2 goes on for ever (m = n + 2, n + 3, …), because m = n + 1 never
holds again. So every P13 run finds its answer and then runs to the budget,
with one or two endless derivations. sum, conc, rev, revacc and racc are
transcribed by cases without change.

**Budget.** These runs use `--steps 100000`, the reconstruction's default,
not P13's 10⁸. Each step of the endless derivation costs more as its list
grows, and CPU time grew about quadratically with the budget: 0.02 s at
5,000 steps, 0.22 s at 20,000, 1.4 s at 50,000 and about 5 s at 100,000.
That projects to about 10 minutes at 10⁶, and the 600-second safety limit
falls short of 10⁸ by orders of magnitude. Under the protocol, P13 in this
reformulation would end in *timeout*, not *budget*, at every n, although
the answer is found within the first few hundred to twenty thousand steps.

**Native (P13e, P13f).** Absys has no means of building, summing or
reversing a list other than relations like these, so its native programs
use the same algorithms. P13e is range (reformulated, as above) with sum,
and P13f is range with the retrospective's accumulator reverse (`rev1`,
`rev`; Elcock 1990, pp. 11 to 13, from tutorial ch. 6), which is linear.
P13e and P13f have the same expressibility problem as P13a to P13d.

| query | reported (hibernating derivation) | valid | state |
|---|---|---|---|
| P13a | s = [1;…;100] | ⟨1, …, 100⟩ | budget, 1 derivation elaborating |
| P13b | k = 5050 | 5050 | budget, 1 elaborating |
| P13c | r = [100;…;1] | ⟨100, …, 1⟩ | budget, 1 elaborating (answer at derivation #20753) |
| P13d | r = [100;…;1] | ⟨100, …, 1⟩ | budget, 2 elaborating |
| P13e | k = 5050 | 5050 | budget, 1 elaborating |
| P13f | r = [100;…;1] | ⟨100, …, 1⟩ | budget, 2 elaborating |

**The full value cannot be printed.** Absys prints at most 32 elements of
a list, and writes `…` for the rest. This holds in every output mode: plain,
`--env` and `json`. So the `.out` files do not show the whole of s or r. The
author checked each list answer in a separate run, not saved, which added
the assertion `s = [1;…;100]` or `r = [100;…;1]` to each text. In every
case the hibernating derivation survived it. A harness's `observe()` will
need another way to read a long value.

---

## SWI-Prolog (`swi-prolog/`), configuration *plain*

Idiom sources: Clocksin and Mellish, *Programming in Prolog* (1981), for
`append` and naive reverse. Integer arithmetic is `is/2` and `>`/`=<`,
which are in the core listed in `systems/swi-prolog/README.md`.

Flags: the defaults (`occurs_check` false, `unknown` error).

The harness stand-in, at the bottom of each file, uses
`call_with_inference_limit/3`, `nb_setval/2`, `nb_getval/2`, `format/2`,
`forall/2`, `initialization/1` and `halt/0`. Most of these are outside the
ISO core of *plain*. They are there only as the harness: they collect
answers up to the cap of 20 under the stage's budget, and print the state.
The limit is cumulative across backtracking (checked), so it acts as a
stage budget. The `query/3` facts only tabulate the queries for that
harness.

### P03 (`p03.pl`)

conc and rev are transcribed by cases in order. There is one definition per
relation, used in every direction, with no reformulation and no external
mechanism in the program. Budget 10⁶ inferences.

| query | reported | state |
|---|---|---|
| P03a | [1,2,3] | finished (deterministic exit) |
| P03b | []-[1,2], [1]-[2], [1,2]-[] | finished after retrying for a fourth |
| P03c | [2,3] | finished (deterministic) |
| P03d | [1,2] | finished after retrying |
| P03e | [3,2,1] | finished (deterministic) |
| P03f | [3,2,1] | budget: on retrying, rev(A, [1,2,3]) recurses on longer and longer A |

All of these match the valid outcomes. P03f is *complete* with *budget*,
as the problem anticipates. Every query was expressible.

### P13 (`p13.pl`)

**Representation:** Prolog lists, `[H|T]`, which take the head and tail in
constant time.

Prescribed tasks: range, sum, conc, rev, revacc and racc are transcribed by
cases in order. range case 2's m + 1 is written `M1 is M + 1` before the
recursive call, and sum's k = h + j as `K is H + J` after it. Both are
evaluations in the direction the query uses. range leaves a choicepoint
after its last answer (clause 2 is tried and fails on `M =< N`), so P13a to
P13d each finish only when the harness asks for a second answer. Budget 10⁸
inferences.

Native tasks: `numlist/3`, then `sum_list/2` (P13e) or `reverse/2`
(P13f), all from `library(lists)`. **External mechanisms:**
`library(lists)`, with `numlist/3`, `sum_list/2` and `reverse/2`.
`reverse/2` uses an accumulator, so it is linear, and `sum_list/2` sums
with an accumulator. The alternative, a plain-only native program, would
have been a hand-written accumulator sum and reverse. That is the same
algorithm as P13d, so the library version was chosen as SWI-Prolog's own
idiom.

| query | reported | valid |
|---|---|---|
| P13a | [1,…,100] | ⟨1,…,100⟩ |
| P13b | 5050 | 5050 |
| P13c | [100,…,1] | ⟨100,…,1⟩ |
| P13d | [100,…,1] | ⟨100,…,1⟩ |
| P13e | 5050 (deterministic) | 5050 |
| P13f | [100,…,1] (deterministic) | ⟨100,…,1⟩ |

---

## Python (`python/`), configuration *core*

No imports. The built-ins used are `print`, `len`, `list`, `range`, `sum`,
list slicing and list and tuple equality. Idiom sources: the Python
Language Reference and Library Reference (built-in functions), and ordinary
recursive transcription. Flags: none. At n ≥ 10³, `sys.setrecursionlimit`
would be needed as a configuration flag. An unsaved check at n = 1000 gave
`RecursionError: maximum recursion depth exceeded` in the first query,
range.

### P03 (`p03.py`)

Representation: Python lists, sliced for the tail. P03 makes no rule about
this.

conc is transcribed by cases as `conc(a, b)`, returning c, which serves
P03a. rev is `rev(a)`, returning b, by cases with conc, which serves P03e.
A Python function computes in one direction, so **P03b, P03c, P03d and
P03f are not expressible with these functions**. Each is answered by a
**separate function, a reformulation**, written from the same cases read
in that direction. Each returns the list of every solution:

- `conc_split(c)` (P03b): case 1 gives (⟨⟩, c). Case 2 puts c's head on
  the front of each split of c's tail.
- `conc_suffix(a, c)` (P03c): case 1 gives c when a is empty. Case 2 needs
  the two heads equal, and recurses on the tails.
- `conc_prefix(b, c)` (P03d): case 1 gives ⟨⟩ when b = c. Case 2 puts c's
  head on the front of each solution for c's tail.
- `rev_inverse(r)` (P03f): case 1 gives ⟨⟩ when r is empty. Case 2 reads
  conc(q, ⟨h⟩, r) first, through `conc_split`, keeping the splits whose
  second part has one element. It then solves rev(l, q) recursively. This
  **moves a conjunct** (conc before rev), which is one move. A shorter
  `rev(r)`, using the fact that rev is its own inverse, was not used: that
  fact is a conclusion about the relation, which the program would encode
  rather than compute.

| query | reported | valid |
|---|---|---|
| P03a | [1, 2, 3] | ⟨1,2,3⟩ |
| P03b | [([], [1, 2]), ([1], [2]), ([1, 2], [])] | the three splits |
| P03c | [[2, 3]] | ⟨2,3⟩ |
| P03d | [[1, 2]] | ⟨1,2⟩ |
| P03e | [3, 2, 1] | ⟨3,2,1⟩ |
| P03f | [[3, 2, 1]] | ⟨3,2,1⟩, exactly one |

Every query finishes. In each multi-answer direction, a list of solutions
says that there are no more.

### P13 (`p13.py`)

**Representation (prescribed tasks):** a chain of pairs, with `None` for ⟨⟩
and `(h, t)` for ⟨h⟩ ++ t. Unpacking `h, t = s` takes the head and tail in
constant time. A Python list was not used, because slicing it copies.
range, sum, conc, rev, revacc and racc are recursive functions, one branch
per case, each returning the unknown its query asks for. `as_list` only
converts a chain for printing, and is marked as harness.

**Native (P13e, P13f):** `s = list(range(1, N + 1))`, then the built-in
`sum(s)`, or `s[::-1]`, a reversing copy, linear. The sequence is built and
held as a list.

| query | reported | valid |
|---|---|---|
| P13a | [1, …, 100] | ⟨1,…,100⟩ |
| P13b | 5050 | 5050 |
| P13c | [100, …, 1] | ⟨100,…,1⟩ |
| P13d | [100, …, 1] | ⟨100,…,1⟩ |
| P13e | 5050 | 5050 |
| P13f | [100, …, 1] | ⟨100,…,1⟩ |

Every list answer was checked element by element against the expected
list.

---

## ALGOL 60 (`algol-60/`), configuration *report*

**Representation (both problems):** a heap of cells in the parallel
integer arrays `hd` and `tl`, with 0 for ⟨⟩. `cons` takes the next free
cell. This is the second encoding that `systems/algol-60/README.md` names
("parallel arrays of heads and tail indices"), and it takes the head and
tail in constant time. Cells are never reclaimed.

**External mechanisms:** `outstring` and `outinteger` (IFIP 1964 /
Modified Report), used only for printing. Flags: none (the report dialect,
the interpreter's default). The query constants are written in the program,
as in the other systems, not read with `ininteger`.

Idiom sources: the Revised Report (1962) for typed procedures, value
parameters, procedures as parameters and nested procedure declarations
(4.7, 5.4). The interpreter's `examples/man-or-boy.alg` and
`examples/hanoi.alg` show a nested procedure passed as an actual parameter,
and recursion with value parameters.

`same(x, y)` compares two sequences element by element. ALGOL has no
equality on this encoding, and conc's case 1 in direction P03d needs it.

### P03 (`p03.alg`)

As in Python. `conc(a, b)` (P03a) and `rev(a)` (P03e) are integer
procedures, transcribed by cases. P03b, P03c, P03d and P03f are **not
expressible** with them, and are answered by separate procedures,
**reformulations**, from the same cases read in that direction: `splits`,
`suffix`, `prefix` and `revinverse`. Each passes every solution to a
procedure parameter `found`. Case 2's "put c's head on the front" is a
procedure declared inside the procedure and passed down the recursion.
This is how ALGOL 60 states "for each solution of the smaller problem",
since it has no lists of results. `revinverse` takes conc(q, ⟨h⟩, r) before
rev(l, q), which **moves a conjunct**, as in Python.

Output: `p03a <1 2 3 >`, `p03b (<>, <1 2 >) (<1 >, <2 >) (<1 2 >, <>)`,
`p03c <2 3 >`, `p03d <1 2 >`, `p03e <3 2 1 >`, `p03f <3 2 1 >`. All of these
match the valid outcomes, and every query finishes.

### P13 (`p13.alg`)

Prescribed tasks: range, sum, conc, rev, revacc and racc are integer
procedures on the heap, one branch per case. range's `if m > n then … else`
states both cases' tests. The heap is declared in an inner block after n is
known, with n × n + 10 × n cells, which is enough for rev's n(n+1)/2. `free`
is set back to 0 before each query. Native tasks: `integer array s[1:n]`
filled by a `for` statement. P13e sums with a `for` statement. P13f copies
into a second array `r[i] := s[n + 1 − i]`, which is linear.

Output: P13a ⟨1 … 100⟩, P13b 5050, P13c ⟨100 … 1⟩, P13d ⟨100 … 1⟩, P13e
5050, P13f ⟨100 … 1⟩. All of these match the valid outcomes; the list
answers were checked element by element.

---

## Expressibility summary

| | Absys | SWI-Prolog plain | Python core | ALGOL 60 report |
|---|---|---|---|---|
| P03a | yes | yes | yes | yes |
| P03b | yes | yes | not with conc; reformulated (split function) | not with conc; reformulated |
| P03c | yes | yes | not with conc; reformulated | not with conc; reformulated |
| P03d | yes | yes | not with conc; reformulated | not with conc; reformulated |
| P03e | yes | yes | yes | yes |
| P03f | yes (then budget) | yes (then budget) | not with rev; reformulated, one conjunct moved | not with rev; reformulated, one conjunct moved |
| P13a to P13d | **not expressible** (no comparison); reformulated range, then budget | yes | yes | yes |
| P13e, P13f | as P13a to P13d (same algorithms) | yes, with library(lists) | yes | yes |

## Problems found in the problem files and protocol

1. **P13 needs comparisons, and no Absys notation has them.** The notation
   rule ("the earliest notation having every construct needed") has no
   answer when no notation has a construct. The systems file foresees
   constructs split across notations, not constructs missing from all of
   them. The study should say whether P13 is then *not expressible* for
   Absys, or whether a reformulation like this one is the program of record.
2. **A timeout erases an answer that was found.** The Absys reformulation
   reaches its answer early. It then cannot reach P13's 10⁸-step budget
   inside 600 seconds, because each step of the endless derivation costs
   more as its list grows. By `SPECIFICATION.md`, a *timeout* is
   "unclassified on the other axes". So a run whose answer is already held
   in a hibernating derivation would go unclassified. It would be clearer
   if answers held when the safety limit stops a run counted as reported,
   as they do when a budget runs out.
3. **"Native" is undefined for a system with a single mechanism.** P13e and
   P13f ask for "whatever means is the system's own idiom". Absys has no
   means other than relations of the prescribed kind, so its native program
   is the prescribed one, apart from the choice of reverse. Should native
   then be *the same as prescribed*, recorded once?
4. **The Absys printer cuts lists after 32 elements**, in every output
   mode, including JSON. For P13 at n ≥ 33, `observe()` cannot read the
   answer from the system's own output. This is a harness matter, not a
   problem-file one, but it needs settling before P13 is measured.
5. **P03, the inverse directions in imperative systems.** `METRICS.md` rule
   3 makes a separate splitting function R. It does not say whether a
   by-cases inverse that reorders case 2's conjuncts (P03f) costs one move
   as well as R, nor how to class `rev(r)`, which relies on rev being an
   involution and would give the right answer. The second would make a
   program shorter by encoding a conclusion. A sentence saying which is
   intended would help.
6. **"conc relates sequences only."** Case 1 says "for every sequence b",
   but no system here restricts b to sequences: conc(⟨⟩, 5, 5) holds in
   Absys and Prolog, and the Python and ALGOL programs never check. No
   query of P03 or P13 depends on it, but a hidden variant might.
7. **What a P13 query reports.** The valid outcome of P13b names only k,
   and of P13c and P13d only r, but s is bound as well, and the
   declarative systems report it. It would help to say whether reporting s
   too is expected.
8. **Query constants.** `systems/algol-60/README.md` says stages are read
   from input. For a one-stage query it is unclear whether writing the
   constants in the program, as done here in every system, is acceptable.
   Genericity (`PROTOCOL.md`, rule 6) is unaffected either way.
