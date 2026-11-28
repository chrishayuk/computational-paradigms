# Python programs, wave 1, batches 1A (P01-P03), 1B (P04-P08) and 1C (P09-P12)

Batches 1B and 1C are in their own sections, after batch 1A's ("Batch 1B
(P04-P08)", "Batch 1C (P09-P12)").

## Batch 1A (P01-P03)

*Written by `implementation-python`, an agent (Claude Opus 5.5,
`claude-opus-5-5`), on 2026-11-27, at `spec-1.0.1`, from the problem files
by the rules of `PROTOCOL.md`, "Writing a program", against the harness
contract in `harnesses/python/README.md`. The author had seen no precursor
program (the absys experiments E01-E09) and no other program for these
problems. Every program here is the **primary** program of its
configuration and sub-problem, fixed before any program was run. None has
been run: the only thing executed was `harnesses/python/check`, which
reported no errors for every file below. No named variant was written.*

Layout: `programs/python/<configuration>/<sub-problem>.py`, one file per
configuration and sub-problem; P02b's one program serves its six instances
(the order comes from `s.params["order"]`). Every program is
`# CP-POSING: incremental`, carries its `PROVENANCE` block and one constants
block tagged by stage, and is run as

    harnesses/python/run CONFIGURATION PROBLEM INSTANCE MODE programs/python/CONFIGURATION/SUBPROBLEM.py OUTDIR

### Shared texts

- **P03a-P03f: core and stdlib-concurrency share one text.** The files in
  `stdlib-concurrency/` are byte-for-byte copies of those in `core/`. The
  queries are single computations with every input known; threads, queues
  and event loops have nothing to do there, so the core program is the
  natural program of stdlib-concurrency too.
- P01 and P02 have a text of their own in each configuration, because each
  configuration offers a different way of holding a relation until its
  information arrives, which is what those problems probe:
  - **core**: a list of held relations, taken up by a loop after each stage
    (code written for the problem's relations: R by `METRICS.md`, rule 19);
  - **stdlib-concurrency**: one thread per relation, waiting on a
    `threading.Condition` until a binding it needs arrives;
  - **extended**: S's logic variables (`S.suspend.Var`), with equations as
    bindings (P01) and relations as goals the suspension queue holds (P02).
- Within a configuration, P02a, P02b and P02c share everything but their
  stage dispatch and constants block.

### Per configuration and sub-problem

All programs: primary; author `implementation-python` (an agent, Claude
Opus 5.5); precursor seen: none. "Idioms" lists the sources each file's
`PROVENANCE` block cites; "S" is the S mechanisms used (`S-mechanisms.md`),
and any of the program's own.

#### core

| sub-problem | program | expressibility (as I see it) | how | S |
|---|---|---|---|---|
| P01a | `core/P01a.py` | expressible with reformulation | each equation held as a pair of places; `equal` (the evaluator of =) decides it once a place has a value; a loop takes the held equations up after each stage. The holding is R (rule 19) | none |
| P01b | `core/P01b.py` | expressible with reformulation | conc transcribed forwards (`conc(a, b)`, two cases); conc(<seq>, s, t) held until s has a value, then t computed; s = <seq> held as an equation | none |
| P01c | `core/P01c.py` | expressible with reformulation | as P01b; conc(<seq>, x, x) is held and never decided (x never gets a value). Under the rational reading core has no value to give: tuples cannot be cyclic | none |
| P02a | `core/P02a.py` | expressible with reformulation | each relation held as its three places; `plus` and `times` (the evaluators of + and ·) compute any one place from the other two, in every direction, or test them; a loop takes them up after each stage | none |
| P02b | `core/P02b.py` | expressible with reformulation | as P02a; the relation of stage k is `s.params["order"][k-1]` | none |
| P02c | `core/P02c.py` | expressible with reformulation | as P02a, the three relations posed in one stage, in order | none |
| P03a | `core/P03a.py` | expressible | conc forwards, the direction the query uses (rule 3) | none |
| P03b | `core/P03b.py` | expressible with reformulation | a separate generator `split(c)` for conc with c known, by conc's two cases in order (rule 3: "the author has no choice") | none |
| P03c | `core/P03c.py` | expressible with reformulation | a separate generator `rest(a, c)` for conc with a and c known | none |
| P03d | `core/P03d.py` | expressible with reformulation | a separate generator `front(b, c)` for conc with b and c known | none |
| P03e | `core/P03e.py` | expressible | rev and conc forwards, rev's conjuncts in their order | none |
| P03f | `core/P03f.py` | expressible with reformulation | a separate generator `unrev(r)` for rev with its second place known; in case 2 the conjunct conc(q, ⟨h⟩, r) is taken first (one move, rule 4), by `split`, keeping splits whose second part has one element; then `unrev(q)` | none |

Idioms (core): `harnesses/python/README.md` sections 3 and 8 (the stage
loop, the `cp` calls, and its example `x01_total.py`, which holds a relation
in a list until its values arrive); METRICS.md rule 3 (conc in Python, `if
not a:`, a separate splitting function for P03b); The Python Tutorial,
"Tuples and Sequences", "Dictionaries", "More on Lists"; The Python Library
Reference, "Sequence Types -- list, tuple, range"; The Python Language
Reference, "Assignment expressions", "The while statement", "The for
statement", "Yield expressions", "Binary arithmetic operations", "Value
comparisons"; PEP 255 (generators), PEP 380 (`yield from`).

#### stdlib-concurrency

| sub-problem | program | expressibility (as I see it) | how | S |
|---|---|---|---|---|
| P01a | `stdlib-concurrency/P01a.py` | expressible with reformulation | each equation, when it arrives, gets a daemon thread that evaluates it (`equal`) and, while it cannot decide, waits on the condition `changed`; every new binding wakes the waiting threads; the main thread ends the stage when no relation thread is busy | none (threading is an external mechanism) |
| P01b | `stdlib-concurrency/P01b.py` | expressible with reformulation | as P01a, with conc forwards and its evaluator | none |
| P01c | `stdlib-concurrency/P01c.py` | expressible with reformulation | as P01b; the relation's thread waits for ever (x never gets a value) | none |
| P02a | `stdlib-concurrency/P02a.py` | expressible with reformulation | one thread per relation, with core's `plus` and `times` | none |
| P02b | `stdlib-concurrency/P02b.py` | expressible with reformulation | as P02a, in the instance's order | none |
| P02c | `stdlib-concurrency/P02c.py` | expressible with reformulation | as P02a, three threads started in one stage, in order | none |
| P03a-f | `stdlib-concurrency/P03?.py` | as core | core's text (above) | none |

Idioms (stdlib-concurrency, beyond core's): The Python Library Reference,
"threading -- Thread-based parallelism", "Thread Objects" (daemon threads)
and "Condition Objects" (`wait_for`, `notify_all`, a condition in a `with`
statement). External mechanism: `threading`.

#### extended

| sub-problem | program | expressibility (as I see it) | how | S |
|---|---|---|---|---|
| P01a | `extended/P01a.py` | expressible | x, y, z are `Var`s; x = y and y = z are bindings that make the unknowns one variable; z = <k> binds it to the value | suspension queue (`Var`, `deref`, `Queue.bind`) |
| P01b | `extended/P01b.py` | expressible | sequences as cons cells; conc forwards with an unknown second place gives the term ⟨1,2⟩ ++ s (case 1 returns the unknown as the tail), to which t is bound; s = <seq> is a binding | suspension queue (as P01a) |
| P01c | `extended/P01c.py` | expressible | x is bound to conc(⟨1⟩, x) = ⟨1⟩ ++ x; the binding has no occurs check, so x is a cyclic term, which the output adapter shows as cyclic. Under the finite reading this report is unsound; under the rational reading it is the one solution | suspension queue (as P01a) |
| P02a | `extended/P02a.py` | expressible with reformulation | each relation a goal (`Relation`, a callable object) of `S.suspend.Queue`: when run it evaluates (core's `plus`, `times`) and decides, or waits on its unbound unknowns (`q.wait`), and is run again when one is bound. The tests of which places are known and the wait are R and C by rule 19 | suspension queue (`Var`, `deref`, `Queue.wait`, `bind`, `run`, `held`) |
| P02b | `extended/P02b.py` | expressible with reformulation | as P02a, in the instance's order | suspension queue |
| P02c | `extended/P02c.py` | expressible with reformulation | as P02a, three goals in one stage, in order | suspension queue |
| P03a | `extended/P03a.py` | expressible | conc transcribed **once**, as a relation: a generator that, for each case in order, unifies the case's head with the goal's arguments and yields the case's body; the query is solved by `S.search.search`, depth first, cases in order, conjuncts left to right; every answer reported | backtracking search (`search`, `undo`, the trail); suspension queue (`Var`, `deref`, `Queue.bind` with the trail); and the program's own **unify** and **resolution** (below) |
| P03b | `extended/P03b.py` | expressible | the same conc, the query conc(a, b, <seq>) | as P03a |
| P03c | `extended/P03c.py` | expressible | the same conc, conc(<seq>, b, <seq>) | as P03a |
| P03d | `extended/P03d.py` | expressible | the same conc, conc(a, <seq>, <seq>) | as P03a |
| P03e | `extended/P03e.py` | expressible | rev and conc once each, as relations; rev's body keeps its conjuncts in order | as P03a |
| P03f | `extended/P03f.py` | expressible | the same rev and conc, rev(a, <seq>). After the one answer the search goes on looking (rev(l, q) with both unknown has endless solutions), as the problem file anticipates for a depth-first search: expected *budget* | as P03a |

**The program's own S mechanisms (extended, P03).** Not in
`S-mechanisms.md`; general over relations, so S by `METRICS.md` rules 12, 15
and 19, the same text in all six P03 programs, to be counted once per
mechanism for the configuration:

- **unify**: unification of terms built from values, cons cells (2-tuples),
  ⟨⟩ (`()`) and `Var`s, iterative, binding through S's trail, undoing its own
  bindings on failure; no occurs check. `S.suspend.Var` does not unify inside
  terms, which conc and rev in every direction need.
- **resolution**: `children` (a goal list reduced by the cases of its first
  goal's relation, the case's body put before the rest) and `done` (no goal
  left), given to `S.search.search`. With the relations written as
  generators of their cases, these two functions are a small
  meta-interpreter.

Idioms (extended, beyond core's): the docstrings of `harnesses/python/S/`
(`search.py`, `suspend.py`) and the qualification program `x01_extended.py`;
McCarthy, "Recursive functions of symbolic expressions and their
computation by machine, Part I", CACM 3(4), 1960 (cons cells), and the same
encoding in `systems/python/measurement.md`, section 2; Robinson, "A
machine-oriented logic based on the resolution principle", JACM 12(1), 1965
(unification, resolution); The Python Language Reference, "Data model"
("Emulating callable objects", "Basic customization").

### What the programs report

- **Answers** (`cp.answer`) are values only: one line per solution, giving
  each unknown that has a value (or, in extended, that is bound to a term
  or identified with another unknown: `x = y`, `t = ⟨1,2⟩ ++ s`). A stage
  that leaves every unknown without a value answers nothing.
- **Held relations** are registered for `observe()`: core's and
  stdlib-concurrency's held relations with `cp.suspended`, extended's
  waiting goals (`q.held`) with `cp.suspended`; relations found not to hold
  with `cp.held`; the bindings with `cp.bindings`; P03's pending generators
  or search stack with `cp.pending`.
- **No solution**: when a relation is found not to hold, the program prints
  (`print`, not `cp.answer`) `no solution: ...` with the relations, and
  answers nothing, since it has no solution to report.
- Sequences are printed as the problem writes them, ⟨1,2,3⟩; a cyclic term
  (extended P01c) as `⟨1⟩ ++ ⟨1⟩ ++ … (cyclic)`.

### Ambiguities, and the reading taken

1. **File names.** The harness README fixes how a program is written, not
   its name. I took `programs/python/<configuration>/<sub-problem>.py`, one
   program per sub-problem (P02b's serving its six instances).
2. **P02b's constants and the order.** The constants block is tagged by
   stage, but in P02b which relation arrives at stage k depends on the
   instance's order. I tagged each relation's constants (`R1_SUM`,
   `R3_ADDEND`, `R3_SUM`) under every stage, with the same values; at stage k
   the program reads only the constants of the relation that arrives at k.
   So, for instance, R3's constants are in the process at stage 1 of the
   order R1 R2 R3, unread until stage 3. A verifier substituting a variant
   should give the same values under all three stages (the program would
   still be consistent if not: each relation arrives once, and uses the
   values delivered with its own stage).
3. **Holding code: R or S** (`METRICS.md`, rule 19). Core's holding loop
   (`decide`) and stdlib-concurrency's thread machinery (`told`, `hold`,
   `pose`, `settle`) are written for each problem's relations, in its
   program, and I took them as R (with the thread calls C). But their shape
   does not depend on the relations (a list of (name, places), a table of
   evaluators), so a classifier could hold them general, hence S.
4. **Evaluators in every direction.** Rule 19 makes computing any place
   from the others P "in every direction". P02's `plus` and `times` do so,
   including the cases of a zero factor (0 · b = 0 holds for every b, which
   stays unknown; 0 · b = c ≠ 0 fails). P01's conc evaluator computes only c
   from a and b, and waits otherwise: in P01b and P01c the first place is
   always a given sequence and the third is never given, so no stage or
   variant of these shapes reaches the other directions.
5. **Places: names and values.** In core and stdlib-concurrency a place is
   an unknown's name (a `str`) or a value. `stages.json` gives the constants
   as integers (`<k>`) and sequences (`<seq>`), so no constant is a `str`;
   an atom constant, written as a Python string, would be taken for an
   unknown's name.
6. **What is an answer.** Where nothing has a value (P01a stages 1-2 in core,
   P02 stages that decide nothing, P01c in core and stdlib-concurrency), the
   program answers nothing and leaves the held relations to `observe()`
   (SPECIFICATION.md: printing the posed information back is not a
   report). Extended answers its solved form (`x = y`, `t = ⟨1,2⟩ ++ s`),
   which is the state of its variables, not the posed text.
7. **"No solution" is printed, not answered**, so that an empty outcome is
   not counted as an answer.
8. **"for every sequence b"** in conc's case 1: none of the programs tests
   that b is a sequence (neither does a Prolog transcription); no query or
   stage of P01-P03 gives conc a b that is not one.
9. **P01c in core and stdlib-concurrency.** Python tuples cannot be cyclic,
   and core has no unknowns. The program holds x = ⟨1⟩ ++ x as a relation
   waiting for x, which never comes. I did not write a variant that builds a
   cyclic mutable structure (a list containing itself): that would not be
   the problem's conc, and the brief asks for variants only where a
   configuration cannot express a sub-problem.
10. **extended P01c's bindings** are registered as their rendering (a dict
    of strings, updated after the stage), because `repr` of a cyclic `Var`
    recurses without end and would be a harness fault.
11. **Problem operations.** P02's relations are counted per evaluator:
    `plus` counts R1's and R3's examinations together, `times` R2's. In
    core P03, each direction function is registered under the relation it
    computes (`conc=split`, `rev=unrev`, ...). In extended P03, `conc` and
    `rev` are generator functions; PY_START counts each application (one
    per goal reduced), not each case tried.
12. **stdlib-concurrency and determinism.** The threads make instruction
    counts vary between runs (`systems/python/measurement.md`, 1); the
    bindings reached are the same in any order, since each relation binds
    only places that are unknown when it decides.
13. **P03f and the budget.** Core's `unrev` takes the conc conjunct first and
    finishes after the one answer; extended's relational rev keeps the
    definition's order and is expected to search on to the budget after it,
    as the problem file anticipates. The two are the natural program of each
    configuration, not a choice made to reach either outcome.

### Conduct

- Files read: those the brief allows, and `harnesses/python/qualification/programs/`
  (`x01_extended.py`, `x02_pick.py`, `x07_wait.py`), which are in
  `harnesses/python/`. `harnesses/stages.json` was read from its start, so
  the stage descriptions of P04-P06 (placeholders, no constants) passed
  before me. Two long outputs of my own `cat` of allowed files (METRICS.md
  with `systems/python/`, and `harnesses/python/README.md`) were saved by
  the tool under `~/.claude/projects/.../tool-results/` and I read them
  there; their content was only those allowed files. A third such read was
  refused by the permission system, and I read `harnesses/README.md` with
  `sed` instead.
- One command I composed began with `python3 -c "print(1)" >/dev/null`,
  joined by mistake to a `grep`; the permission system refused it and
  nothing ran. No program, interpreter or fragment was executed, on the
  host or in the image; only `harnesses/python/check`.

## Batch 1B (P04-P08)

*Written by `implementation-python`, an agent (Claude Opus 5.5,
`claude-opus-5-5`), on 2026-11-27, at `spec-1.0.1` (commit `651a55b`), from
the problem files by the rules of `PROTOCOL.md`, "Writing a program",
against `harnesses/python/README.md`. The author had seen no precursor
program (the absys experiments E01-E09) and no other author's program for
these problems; the only earlier programs it read are its own batch-1A
programs in this folder. Every program below is the **primary** program of
its configuration and sub-problem, chosen and fixed before any program was
run. None has been run: the only thing executed on them was
`harnesses/python/check`, which reported no errors for all 78 files. No
named variant was written, and no sub-problem was judged not expressible.*

Layout as for batch 1A: `programs/python/<configuration>/<sub-problem>.py`,
every file `# CP-POSING: incremental`, with its `PROVENANCE` block. P07a's
one program serves its six instances (the order comes from
`s.params["order"]`). P04d, P04f and P08b have no constants block
(`constants.how = "none"`); every other file has one block, tagged by stage.

### Shared texts

- **core and stdlib-concurrency share one text** for P04a-P04f, P06d and
  P06e1-P06e3: the files in `stdlib-concurrency/` are byte-for-byte copies of
  those in `core/`. These are queries whose every input is known when they
  are posed (P04's disjunctions and definitions, setdiff, the closed world of
  P06e); nothing waits for information, so threads have nothing to do and
  the core program is the natural program of stdlib-concurrency too.
- **P05, P06a-P06c, P07 and P08** have a text of their own in each
  configuration, because each offers its own way of holding what waits for
  information (as in batch 1A's P01 and P02):
  - **core**: a list of held relations taken up by a loop after each stage
    (`decide`), or, in P05, a list of the values of x still held and a list
    of comparisons waiting for x to have values;
  - **stdlib-concurrency**: one thread per relation, waiting on the
    `threading.Condition` `changed` (the same `told`, `hold`, `pose`,
    `settle` as batch 1A's P02);
  - **extended**: the S mechanisms (below).
- Within a configuration, the sub-problems of one problem share everything
  but their stage dispatch, constants block and description: P05a-c,
  P06a-c, P07a-g, P08a-c (P08b is P08a with stages 4-6 and the block
  removed). In extended, P04a-f, P06d-e3 and P08a-c carry, unchanged, the
  `unify`, `children` and `done` of extended's P03 programs.

### Per configuration and sub-problem

All 78 programs: **primary**; author `implementation-python` (an agent,
Claude Opus 5.5); precursor seen: none. Each file's `PROVENANCE` block cites
its idioms; they are collected after each table.

#### core

| sub-problem | expressibility (as I see it) | how | S |
|---|---|---|---|
| P04a | expressible | `loop` and `=` as generators of the values of x that satisfy them (x given as `None` while unknown); the disjunction one generator after the other, as written. `loop` calls itself before yielding anything: expected `RecursionError` (*error*) before x = 1 is reported | none |
| P04b | expressible | as P04a, the other order: x = 1 reported, then `RecursionError` | none |
| P04c | expressible | `alist` (alist-left) as one generator for both directions (s known, or `None`), cases in order and case 1's conjuncts in order: alist(m) with m unknown first, so it recurses before testing s: expected `RecursionError`. A ground query answers `true` once per solution | none |
| P04d | expressible | the same alist-left, s unknown: expected `RecursionError`, no answer | none |
| P04e | expressible | alist-right, cases in order; case 2's head gives m as the rest of s when s begins with ᴀ: `true`, then the generator is exhausted | none |
| P04f | expressible | the same alist-right, s unknown: s = ⟨⟩, ⟨ᴀ⟩, ⟨ᴀ,ᴀ⟩, … in that order, each one level deeper, until the budget or the recursion limit | none |
| P05a | expressible with reformulation | the values of x still held, all at once, in a list; pick (by its facts) or x = k (by k) gives x its values when it has none, and every relation then keeps only the values it holds of. A comparison posed before x has values is held (R by rule 19) | none |
| P05b | expressible with reformulation | the same text: stage 1's x > k is held until pick gives x its values | none |
| P05c | expressible with reformulation | the same text; x = 4 empties the list, and x = 3 keeps it empty | none |
| P06a | expressible with reformulation | the batch-1A holding loop: x = k and not (x = k) held as places; `not_equal` holds exactly when `equal` does not, and is decided only once x has a value (R: the holding, rule 19) | none |
| P06b | expressible with reformulation | as P06a, the other order | none |
| P06c | expressible with reformulation | as P06a; stage 2 makes not (x = 1) fail: "no solution" printed | none |
| P06d | expressible | mem (a test) and setdiff (forwards) by their cases in order; case 3's guard `not mem(h, s2)` written as stated (so mem is applied again there) | none |
| P06e1 | expressible | the closed world as tuples; student and maths as generators (place `None` while unknown), takes as a test (both places are known when the definition reaches it); nonmajor's conjuncts in order; `true` once per solution | none |
| P06e2 | expressible | the same text, the other atom: `false` printed, no answer | none |
| P06e3 | expressible | the same, p unknown: `p = 'brown` once per solution | none |
| P07a | expressible with reformulation | the batch-1A holding loop with evaluators `equal`, `plus`, `minus`, `times`, each computing any one place from the others or testing them (P, rule 19); x + y + z = k decomposed as x + y = t, t + z = k with a fresh unknown t; the relations posted in the instance's order | none |
| P07b-P07g | expressible with reformulation | the same text, each with its own relations. Relations with two unknown places wait (P07b, P07c, P07f: residual); `times` fails P07e (15 is not a multiple of 2); P07g's x · x waits (its evaluator sees two unknown factors) | none |
| P08a | expressible with reformulation | the holding loop over places that are `Unknown` objects or values; a = ⟨x,y,z⟩ gives a the tuple (x, y, z); = on two sequences of one length is decided place by place, s = p ++ t with s known by p's places and the rest. rev and conc are `def` statements executed when stage 4 is posed. rev(a, b) is decided, by calling `rev`, as soon as a has a value, which it has at stage 2: expected `NameError` at stage 2, Python's own meaning of a name not yet defined (state 3 of the problem file); every later stage is reposed after the error and meets it again in the replay of stage 2 | none |
| P08b | expressible with reformulation | P08a's text, stages 1-3 only: the same `NameError` at stage 2 | none |
| P08c | expressible with reformulation | conc by `def` at stage 1; rev by `def` at stage 3 with case 1 only (a fact, from the block; the function falls through to `None` where no case applies, which the evaluator takes as rev not holding), and again at stage 4 with both cases. rev(⟨1,2⟩, b) is decided at stage 2: expected `NameError` | none |

Idioms (core), beyond batch 1A's: The Python Language Reference (3.13),
"Yield expressions", "Function definitions", "Naming and binding"
("Resolution of names"), "Boolean operations", "Membership test
operations", "Value comparisons"; The Python Library Reference, "Built-in
Constants" (`None`), "Text Sequence Type -- str"; The Python Tutorial, "List
Comprehensions"; PEP 255, PEP 380; METRICS.md rule 3 (the `if not a:`
dispatch); `harnesses/python/README.md` sections 3 and 8 (the stage loop,
`x01_total.py`'s holding list); Clark, "Negation as failure", in Gallaire
and Minker (eds.), *Logic and Data Bases*, Plenum, 1978 (the closed world of
P06e, as the problem file cites it).

#### stdlib-concurrency

| sub-problem | expressibility (as I see it) | how | S |
|---|---|---|---|
| P04a-P04f | as core | core's text | none |
| P05a-P05c | expressible with reformulation | core's list of the values of x still held; each relation, when it arrives, gets a daemon thread that, while x has no values and the relation cannot give it any, waits on `changed`; the thread that gives x its values wakes the others | none (`threading` is an external mechanism) |
| P06a-P06c | expressible with reformulation | one thread per relation, with core's `equal` and `not_equal`; not (x = k)'s thread waits until x has a value | none |
| P06d, P06e1-P06e3 | as core | core's text | none |
| P07a-P07g | expressible with reformulation | one thread per relation, with core's evaluators; in P07a the relations' threads are started in the instance's order | none |
| P08a | expressible with reformulation | one thread per relation, with core's evaluators; rev(a, b)'s thread waits while rev has no definition (a dict `defined`, which stage 4 fills and notifies): the application waits for its definition (state 4), and is decided when stage 4 is posed. Equations decided place by place are posed as new threads | none |
| P08b | expressible with reformulation | P08a's text, stages 1-3: rev(a, b)'s thread is still waiting at the end | none |
| P08c | expressible with reformulation | as P08a; stage 3's `def` (case 1 only) wakes rev(⟨1,2⟩, b)'s thread, which decides it with the case rev then has: it fails, "no solution" is printed; stage 4's second `def` finds no thread waiting | none |

Idioms (stdlib-concurrency, beyond core's): The Python Library Reference
(3.13), "threading -- Thread-based parallelism": "Thread Objects" (daemon
threads), "Condition Objects" (`wait_for`, `notify_all`, a condition in a
`with` statement; the default lock of a `Condition` is an `RLock`, so a
thread holding it can pose a new thread). External mechanism: `threading`.

#### extended

| sub-problem | expressibility (as I see it) | how | S |
|---|---|---|---|
| P04a | expressible | loop, = and the disjunction as relations (generators of their cases, each unifying its head and giving its body), the disjunction's cases being its alternatives in order; solved by `S.search.search`, depth first. The search is iterative, so loop(x) does not exhaust the recursion limit: expected *budget*, no answer | search (`search`, `undo`, the trail); suspension queue (`Var`, `deref`, `Queue.bind` with the trail); the program's own **unify** and **resolution** (batch 1A's text) |
| P04b | expressible | as P04a: x = 1, then *budget* | as P04a |
| P04c | expressible | alist-left as a relation, case 1's conjuncts in order: the search descends alist(m) for ever: expected *budget*, no answer | as P04a |
| P04d | expressible | the same, s unknown: *budget*, no answer | as P04a |
| P04e | expressible | alist-right: `true`, then the search is exhausted | as P04a |
| P04f | expressible | alist-right, s unknown: s = ⟨⟩, ⟨'a⟩, ⟨'a,'a⟩, … until the budget | as P04a |
| P05a | expressible with reformulation | the propagator's `Store`: pick, by its facts, gives x its finite domain (the domain the problem states); every relation is posted as `Store.relation` on x (arc consistency), which narrows the domain: all values held at once. A comparison posted before x has a domain is held in a list (R by rule 19), since no finite domain the problem states exists then and imposing one is judged against the problem (AMENDMENTS.md, 3.4) | constraint propagator (`Store`, `var`, `relation`, `dom`) |
| P05b | expressible with reformulation | the same text: x > k held until pick arrives | as P05a |
| P05c | expressible with reformulation | the same text: x = 4 empties the domain; the store keeps it empty | as P05a |
| P06a-P06c | expressible with reformulation | batch 1A's P02 goals: each relation a goal of `S.suspend.Queue` (`Relation`, a callable object) that evaluates (`equal`, `not_equal`) and decides, or waits on its unbound unknowns; not (x = k) waits on x (the tests of which places are known and the wait are R and C by rule 19) | suspension queue (`Var`, `deref`, `Queue.wait`, `bind`, `run`, `held`) |
| P06d | expressible | mem and setdiff as relations, by their cases in order; case 3's guard is the goal negation(mem(h, s2)) | as P04a, and the program's own **negation** (below) |
| P06e1-P06e3 | expressible | the facts and nonmajor as relations; nonmajor's conjuncts in order, the third being negation(takes(p, k)); p and k are bound before it is reached | as P06d |
| P07a-P07g | expressible with reformulation | batch 1A's P02 goals, with core's evaluators; equations (z = 3, u = 2) are goals with `equal`, so the relations are run in the order posted (P07a: the instance's order) | suspension queue (as P06a) |
| P08a | expressible with reformulation | the unknowns are `Var`s and equations unifications; each relation is the list of its cases that have arrived (`cases`), each case a generator; rev(a, b), posed while rev has no case, is an `Application` held in a `Queue` waiting on the `Var` `defined["rev"]`, which stage 4 binds; it is then solved by search and its first solution kept (the search's remaining choice points stay registered as pending). b = ⟨42⟩ ++ c is a unification with the cons cells of the prefix ending in c | as P04a, and the suspension queue's `Queue.wait`, `run`, `held` for the applications |
| P08b | expressible with reformulation | P08a's text, stages 1-3: rev(a, b) still held at the end | as P08a |
| P08c | expressible with reformulation | conc's cases arrive at stage 1; rev's case 1 (a fact, from the block) at stage 3, which binds `defined["rev"]` and wakes rev(⟨1,2⟩, b): solved with case 1 only, it has no solution and is recorded as failed; case 2 arrives at stage 4 and nothing is waiting for it | as P08a |

**The program's own S mechanisms (extended).** As in batch 1A, general over
relations, so S by `METRICS.md` rules 12, 15 and 19, to be counted once per
mechanism for the configuration:

- **unify** and **resolution** (`children`, `done`): the same text, byte for
  byte, as in extended's P03 programs, used by P04a-f, P06d-e3 and P08a-c.
- **negation** (P06d, P06e1-e3): `negation(*goals)`, a relation that holds
  exactly when a search of its own for the goals finds no solution (negation
  as failure), undoing any bindings that search made. In P06d and P06e its
  goals are ground when it is reached, by the definitions' conjunct order.
- The holding of applications that wait for a definition (P08's
  `Application`, `cases`, `defined`) is written for the problem's relations,
  in its program: I took it as R (with the wait, `q.wait`, C), as rule 19
  says of holding code; a classifier may hold it general, hence S (rule 12's
  "wait-for-definition layer").

Idioms (extended, beyond core's and batch 1A's): the docstrings of
`harnesses/python/S/` (`search.py`, `suspend.py`, `propagate.py`);
Robinson, "A machine-oriented logic based on the resolution principle",
JACM 12(1), 1965; McCarthy, "Recursive functions of symbolic expressions and
their computation by machine, Part I", CACM 3(4), 1960; Clark, "Negation as
failure", 1978 (negation as failure); Naish, *Negation and Control in
Prolog*, LNCS 238, Springer, 1986 (negation decided only once its unknowns
have values); Mackworth, "Consistency in networks of relations", Artificial
Intelligence 8(1), 1977 (arc consistency); The Python Language Reference,
"Data model" ("Emulating callable objects"), "Function definitions".

### What the programs report

As batch 1A: answers are values or solved forms, one `cp.answer` per
solution (P05: one per value of x still held; P04c, P04e, P06e1, P06e2:
`true` once per solution of a ground query, and `false: …` printed, not
answered, when there is none); an empty outcome is printed as `no solution:
…`, never answered; held relations, waiting goals or threads, pending
generators or search stacks, and P05's values of x
(`cp.problem_alternatives`) are registered for `observe()`. Atoms are
Python strings, shown with a leading quote (`'brown`), sequences as ⟨…⟩.

### Ambiguities, and the reading taken

1. **P08: "rev and conc are as in P03".** P03's problem file is not among
   the files this brief lets me read. I took rev and conc as my batch-1A P03
   programs transcribe them: conc(⟨⟩, b, b); conc(⟨h⟩ ++ a, b, ⟨h⟩ ++ c) if
   conc(a, b, c); rev(⟨⟩, ⟨⟩); rev(⟨h⟩ ++ l, r) if rev(l, q) and conc(q,
   ⟨h⟩, r), in those orders. If P03 differs, P08's programs carry the
   difference.
2. **P08's constants.** `stages.json` writes P08a stage 6 as `b = <seq> ++
   c`, so its constant is the sequence ⟨42⟩ (`PREFIX = (42,)`), not 42, and
   every program handles a prefix of any length. It writes P08c stage 3 as
   `rev(<seq>, <seq>)`, so case 1's two sequences are constants
   (`CASE1_FIRST`, `CASE1_SECOND`, both `()`), and rev's case 1 is
   transcribed as that fact. P08a stage 4 ("the definitions of rev and
   conc") has no placeholder, and its definitions are program text.
3. **P08 in core: which state.** I took Python's own meaning of an
   undefined name, `NameError` (state 3), as core's primary: the definitions
   are `def` statements executed when their stage is posed, and rev(a, b) is
   decided by calling `rev` as soon as a has a value. Holding the
   application until `rev` is defined would be a test that chooses P08's
   open reading (rule 11's kind of declaration), which the core program does
   not add. stdlib-concurrency and extended add exactly that, with their own
   mechanism for waiting (a thread on a `Condition`; a goal on a `Var`), and
   so take state 4; their definedness tests (`"rev" in defined`, `if not
   cases[name]`) are the constructs a classifier may class C by rule 11.
4. **P08c: what wakes the waiting application.** In stdlib-concurrency and
   extended, the arrival of rev's first part (case 1, stage 3) wakes it, and
   it is decided with the cases rev has then, so it fails and stage 4 cannot
   reach it. The programs cannot know that a definition is incomplete (rule
   5), and I did not make the application wait again after a failure.
5. **P04 and directions.** P04's relations are used with their argument
   known and unknown (alist-left's case 1 calls alist(m) with m unknown even
   for a ground query). In core each is one generator serving both, with the
   argument `None` while unknown; its `s is None` tests may be read as case
   dispatch (P) or as tests of which places are known (R, rule 19).
   Keeping alist-left's conjuncts in their order makes core P04c recurse
   before testing s; computing m from s first (one move, rule 4) would
   terminate. I kept the order and wrote no variant.
6. **P04 in stdlib-concurrency.** Running each alternative of a disjunction
   in its own thread would be another program (or-parallelism, C), not the
   natural reading of an ordered disjunction; stdlib-concurrency shares
   core's text.
7. **Unknown places and atom constants.** In batch 1A (note 5) an unknown
   was a `str` place, so an atom constant would be taken for an unknown. In
   P06a-c (where x ranges over all values) and P08 (whose sequences could
   hold atoms in a variant), core and stdlib-concurrency now use a small
   class `Unknown` for places. P07's unknowns are integers, and its places
   stay names (`str`), as in P02.
8. **P05: the alternatives.** core and stdlib-concurrency hold the values of
   x in a list, in the facts' order; extended holds them in the propagator's
   domain (a set) and reports them in increasing order. All three hold every
   surviving value at once. extended's x > k before any domain is held by the
   program (R), not posted with an imposed domain.
9. **P06e: takes as a test.** nonmajor's conjunct order binds p and k before
   not takes(p, k), so core's takes is a test (the direction the definition
   uses), with `in` on the closed world's tuple of facts (rule 9: listed).
   student and maths are generators, serving the ground query (P06e1, e2)
   and the open one (P06e3) alike.
10. **P06d: case 3's guard.** Written `if not mem(h, s2):` after case 2's
    `if mem(h, s2):`, not as an `else`, so that the guard is not omitted
    (rule 4); mem is applied twice for an element not in s2.
11. **P07a's compound relation.** x + y + z = k is decomposed as (x + y) + z,
    with the fresh unknown t (SPECIFICATION.md allows either form). The
    instance's order places both halves where relation 1 goes.
12. **P07g and P07b, c, f.** Each evaluator decides one relation from its
    own places; none combines relations or solves x · x = 9. That is what
    these programs do, not a choice made to reach an outcome.
13. **extended P08: first solution only.** An `Application` keeps the first
    solution of its search; rev on a sequence of known length has one, and
    any choice points left are registered as pending. A relation applied
    inside a search with no cases simply has no solutions there; only the
    applications posed as stages wait.

### Conduct

- Files read: those the brief allows (the top-level documents, the five
  problem files and `problems/README.md`, `systems/python/README.md` and
  `measurement.md`, `harnesses/README.md`, `harnesses/stages.json`,
  `harnesses/python/` (README, QUESTIONS, S-mechanisms, the three `S/`
  modules), and my own batch-1A programs and this README). Of
  `stages.json` I printed only its header, vocabulary and the entries of
  P04-P08.
- Three long outputs of my own `cat` of allowed files (PROTOCOL.md with
  AMENDMENTS.md and METRICS.md; `systems/python/README.md` with
  `measurement.md`; `harnesses/README.md` with `harnesses/python/README.md`)
  were saved by the tool under `~/.claude/projects/.../tool-results/`, and I
  read them there. Their content was only those allowed files. The session
  also put my user-level memory index (`~/.claude/.../memory/MEMORY.md`,
  two lines about another project) into my context unasked; I did not open
  anything under `~/.claude` otherwise.
- **Two uses of an interpreter on the host, not on any program:** to print
  parts of `stages.json` I ran `python3 -c` with a few lines of my own that
  load the JSON and print the P04-P08 entries (three times); and once,
  composing a command, I left in `python3 - <<'X' ... X` with an empty
  input, which started the host interpreter on an empty script. Neither ran
  a program of the study or any fragment of one, and neither ran in the
  image. All program files were written with shell heredocs, `sed`, `perl`
  and `awk`, and checked only with `harnesses/python/check`.
- One file was briefly written to `/tmp` (an output of `perl` that I then
  redid in my scratch directory) and deleted.

## Batch 1C (P09-P12)

*Written by `implementation-python`, an agent (Claude Opus 5.5,
`claude-opus-5-5`), on 2026-11-28, at `spec-1.0.1` (commit `1f291be`), from
the problem files by the rules of `PROTOCOL.md`, "Writing a program",
against `harnesses/python/README.md`. The author had seen no precursor
program (the absys experiments E01-E09) and no other author's program for
these problems; the only earlier programs it read are this folder's own
batch-1A and 1B programs. Every program below is the **primary** program of
its configuration and sub-problem, chosen and fixed before any program was
run. None has been run: the only thing executed on them was
`harnesses/python/check`, which reported no errors for all 51 files. No
named variant was written, and no sub-problem was judged not expressible.*

Layout as for batches 1A and 1B: `programs/python/<configuration>/<sub-problem>.py`,
every file `# CP-POSING: incremental`, with its `PROVENANCE` block and one
constants block tagged by stage. One program serves every instance of its
sub-problem: P09a's two spawn orders (the harness applies `spawn_order`),
and P12's six instances each (n and the answer mode come from
`s.params["n"]` and `s.params["answers"]`).

### Shared texts

- **core and stdlib-concurrency share one text** (the files in
  `stdlib-concurrency/` are byte-for-byte copies of those in `core/`) for:
  - **P09a, P09b**: the computations are functions registered with
    `cp.computation`; running them side by side is what the harness's
    `spawn()` does in stdlib-concurrency, with threads, the configuration's
    own mechanism (`harnesses/python/README.md`, 3.4). Nothing inside either
    computation waits for anything, so the program has no thread code of
    its own;
  - **P11a-P11d, P12a-P12d**: queries whose information is all known when
    each stage is posed; nothing waits for information, so threads have
    nothing to do.
- **core, stdlib-concurrency and extended share one text** for **P10a and
  P10c**, and **core and extended** for **P10b**: replacement is Python's own
  assignment. None of extended's S mechanisms replaces a value (a
  `S.suspend.Var` is bound once; a `S.propagate.Store` domain only narrows,
  or is undone through a trail), so the core program is the natural program
  of extended too. stdlib-concurrency has its own P10b (below).
- **Their own text in each configuration**: P09c, P09d, P09e and P10d, which
  hold relations until information arrives (P09c-e) or withdraw information
  (P10d), as each configuration offers its own way of doing so; and
  extended's P09a, P09b, P11 and P12, which use S's search or variables.
- **Within a configuration**, P09c and P09d share everything but gen/genu
  and the constants block; P11a/P11b, P11c/P11d and P12a-P12d likewise share
  everything but the conjunct order, the stage dispatch, or the facts.
  extended's P09a, P11 and P12 carry, unchanged, the `unify`, `children` and
  `done` of extended's P03 programs.

### Per configuration and sub-problem

All 51 programs: **primary**; author `implementation-python` (an agent,
Claude Opus 5.5); precursor seen: none. Each file's `PROVENANCE` block cites
its idioms; they are collected after each table.

#### core

| sub-problem | expressibility (as I see it) | how | S |
|---|---|---|---|
| P09a | expressible | A and B are functions registered with `cp.computation`, each with its own bindings. A: loop as in core P04a, a generator that calls itself before yielding (expected `RecursionError`, *error*); B: rev and conc forwards as in core P03e. The harness runs them one after the other in the instance's order | none |
| P09b | expressible | A: the first equation gives x its value (assignment), the second tests it (comparison), each in the direction it is reached; the conjunction fails, "no solution" is printed, and no binding is registered. B: y = k | none |
| P09c | expressible | gen (s from n) and sum3 (total from s) forwards, by their cases, each a function; the conjunction in its order: gen gives the whole of s, then sum3 acts on it. The consumer never acts before the producer has finished | none |
| P09d | expressible | the same text with genu, by its one case: sequences are tuples, which are finite, and genu calls itself without end: expected `RecursionError` before s exists, so no binding and no answer | none |
| P09e | expressible with reformulation | the batch-1A holding loop (`decide`) with the evaluators `plus` and `minus` (each computing any one place from the other two, or testing them: P by rule 19); x = y + k held as y + k = x, y = x - k as x - k = y. Neither has two known places, so both stay held (registered as suspended) and nothing is answered | none |
| P10a | expressible | b is an entry of a dict, replaced by assignment; b + k is evaluated before the assignment, from b's old value | none |
| P10b | expressible with reformulation | b replaced by assignment; the standing relation d = k · b is held in a list for as long as the program runs (`maintain`, after every stage, gives d the value the relation defines from b's current value, where b has one). The holding is R by rule 19; the relation is evaluated in the one direction it is used, d from b (rule 8) | none |
| P10c | expressible | every stage an assignment; d is computed once, at stage 2, and keeps its value | none |
| P10d | expressible with reformulation | core P05's text (the values of x held in a list, all at once, narrowed by each relation as it arrives), and the information given and not withdrawn, with each relation's stage. A withdrawal restates: the values of x are worked out again from pick's facts and the information left, in order | none |
| P11a | expressible | the conjunction as a generator of its solutions (pick's facts in order, the test, `cp.emit`, then the solution); one answer is taken with `next`, the generator left suspended (registered as pending) | none |
| P11b | expressible | the same text, conjuncts in P11b's order: `cp.emit` before the test, so the first value pick gives is emitted and then refuted (expected log ⟨1,2⟩) | none |
| P11c | expressible | stage 1's conjunction as a generator; one solution held. A relation added later (x ≠ k) is kept, and the solution held must satisfy every one: otherwise the generator is asked for its next solution, which performs that solution's effect (expected log ⟨1,2⟩). Commit selects the solution held, v: x = v is added, and the generator is dropped. A replayed commit takes v from `s.commitment` | none |
| P11d | expressible | the same text, stages in P11d's order: commit at stage 2 drops the generator, so stage 3's x ≠ k, if it refutes v, leaves no solution ("no solution" printed, no answer, no binding) | none |
| P12a | expressible | choice as a recursive generator of the sequences it holds of, by its cases in order (⟨⟩ first, then ⟨e⟩ ++ t for e = 'l, then 'r, with every t of choice(n − 1, t)): depth first in the order written; accept a test of s against the closed world's facts (`in`, rule 9); the conjunction a generator over choice testing accept. All solutions, or one with `next` | none |
| P12b-P12d | expressible | the same text, each with its own facts | none |

Idioms (core), beyond batches 1A's and 1B's: The Python Language Reference
(3.13), "Assignment statements" (the right-hand side evaluated before the
target is bound), "Yield expressions", "Value comparisons", "Binary
arithmetic operations"; The Python Library Reference, "Built-in Functions"
(`next` with a default), "Mapping Types -- dict", "Common Sequence
Operations" (`in`), "Text Sequence Type -- str"; The Python Tutorial,
"Tuples and Sequences", "List Comprehensions", "More on Lists"; PEP 255;
METRICS.md, rules 2, 3, 8 and 9; `harnesses/python/README.md`, sections 3
and 8, and its qualification programs `x03_two.py` (computations registered
for spawn, constants kept by main for them) and `x02_pick.py` (a commit stage
taken from `s.commitment`); Clocksin and Mellish, *Programming in Prolog*,
Springer, 1981, chapter 4 ("Backtracking and the Cut": commitment as giving
up the alternatives not taken).

#### stdlib-concurrency

| sub-problem | expressibility (as I see it) | how | S |
|---|---|---|---|
| P09a, P09b | as core | core's text; the harness runs A and B side by side, in threads | none |
| P09c | expressible with reformulation | each application of a relation is given a thread of its own (batch 1A's `told`, `hold`, `pose`, `settle`), in the order posed. gen, by its cases, binds s to its first cell ⟨n⟩ ++ rest (a `Cell` whose tail is a new `Unknown`) and poses its body's goal gen(n + 1, rest) as a new thread; sum3's thread waits on the condition `changed` until s is known as far as three elements, then binds total. So the consumer may act on s before the producer has finished, as the threads are scheduled. Main reports the conjunction's solution once s is known to its end and total has a value | none (`threading` is an external mechanism) |
| P09d | expressible with reformulation | the same text with genu: each genu thread poses the next, without end, while sum3's thread binds total = p + q + r once three cells exist. Main's `settle` never returns: expected *budget* (the threads the program starts count in main's budget), with total's binding in the registered bindings and no answer | none |
| P09e | expressible with reformulation | one thread per relation with core's `plus` and `minus`; both threads wait (registered as suspended), nothing is answered | none |
| P10a, P10c | as core | core's text | none |
| P10b | expressible with reformulation | b replaced by assignment under the condition, and every replacement wakes the waiting threads (`become`, `told`); the standing relation has a thread of its own that never ends: each time it is woken it gives d the value the relation defines from b's current value, and waits again | none |
| P10d | expressible with reformulation | stdlib-concurrency P05's text (one thread per relation on the list of values of x), and the information given and not withdrawn; a withdrawal clears the values and gives each relation not withdrawn a new thread, in order | none |
| P11a-P11d, P12a-P12d | as core | core's text | none |

Idioms (stdlib-concurrency, beyond core's and the earlier batches'): The
Python Library Reference (3.13), "threading -- Thread-based parallelism":
"Thread Objects" (daemon threads), "Condition Objects" (`wait_for`,
`notify_all`, the `with` statement, the default `RLock`); McCarthy, "Recursive
functions of symbolic expressions and their computation by machine, Part I",
CACM 3(4), 1960 (a cell of a head and a tail); The Python Language Reference,
"Data model" (`__repr__`). External mechanism: `threading`.

#### extended

| sub-problem | expressibility (as I see it) | how | S |
|---|---|---|---|
| P09a | expressible | loop (as in extended P04a), rev and conc (as in extended P03e) as relations; each computation runs its own `S.search.search`, with its own stack registered as its pending structure. The search is iterative, so A's loop(x) is expected to run to its *budget*; then (or first, in the order B A) B reports b = ⟨3,2,1⟩ and goes on searching, as extended P03e does | search (`search`, `undo`, the trail); suspension queue (`Var`, `deref`, `Queue.bind`); the program's own **unify** and **resolution** (batch 1A's text) |
| P09b | expressible | each equation a `Queue.bind` on a `Var`, the second failing; A's bindings are undone through a trail on failure, so none is registered as held; B binds y | suspension queue (`Var`, `deref`, `Queue.bind` with a trail); search's `undo` only |
| P09c | expressible with reformulation | s and total are `Var`s; each relation application a goal (`Goal`, a callable object) of `S.suspend.Queue`, posted in order. gen binds s to the cons cell (n, rest), rest a new `Var`, and posts gen(n + 1, rest); sum3 walks s and waits (`q.wait`) on the first unbound tail it meets, then binds total. The queue runs ready goals first in, first out, so the consumer acts on each cell as the producer makes it. The waiting test and wait are R and C by rule 19 | suspension queue (`Var`, `deref`, `Queue.wait`, `bind`, `run`, `held`) |
| P09d | expressible with reformulation | the same text with genu: the queue is never empty, `q.run()` does not return: expected *budget*, with total bound to p + q + r and s a sequence of cells ending in an unbound `Var`, both read through the registered bindings (rendered by the output adapter `Shown`, without recursion); no answer | as P09c |
| P09e | expressible with reformulation | batch 1A's P02 goals (`Relation`) with `plus` and `minus`; both wait on their unbound unknowns | as P09c |
| P10a, P10b, P10c | as core | core's text (see "Shared texts") | none |
| P10d | expressible with reformulation | extended P05's text (pick gives x its domain in the propagator's `Store`; each relation posted on x narrows it), with the store keeping a trail. Each relation's stage and the trail's length before it are kept; a withdrawal undoes the store back to that length (`S.search.undo`), restoring the domain and removing the relation, and posts again every relation given after it (none, here) | constraint propagator (`Store` with a trail, `var`, `relation`, `dom`); search's `undo` only |
| P11a | expressible | pick (its facts as cases), x ≥ k (a test) and emit (a goal that calls `cp.emit` and holds) as relations; the query solved by `S.search.search`, depth first; one solution taken with `next`, the stack's choice points left registered as pending | as P09a |
| P11b | expressible | the same text, the goals in P11b's order | as P09a |
| P11c | expressible | stage 1's query solved by search, one solution held; a relation added later must hold of it, else the search is asked for its next solution (backtracking into pick, and performing that solution's emit); commit adds x = v and clears the search's stack (its choice points given up). A replayed commit takes v from `s.commitment` | as P09a |
| P11d | expressible | the same text, stages in P11d's order | as P09a |
| P12a | expressible | choice, its disjunction (e = 'l or e = 'r, as extended P04a's `either` and `equal`) and accept (its facts as cases, as cons cells) as relations, by their cases in order; the query choice(n, s) and accept(s) solved by `S.search.search`, depth first; every solution reported, or the first (`break` after one) | as P09a |
| P12b-P12d | expressible | the same text, each with its own facts | as P09a |

**The program's own S mechanisms (extended).** As in batches 1A and 1B,
general over relations, so S by `METRICS.md` rules 12, 15 and 19, counted
once per mechanism for the configuration: **unify** and **resolution**
(`children`, `done`), the same text, byte for byte, as in extended's P03
programs, used by P09a, P11a-d and P12a-d. No new mechanism of the
program's own was written in this batch. The `Goal` class of P09c/P09d and
the `Relation` class of P09e are written for each problem's relations, in
its program, as in batch 1A's P02: I took them as R (with `q.wait` C), as
rule 19 says of holding code; a classifier may hold them general, hence S.

Idioms (extended, beyond core's and the earlier batches'): the docstrings of
`harnesses/python/S/` (`search.py`: "a caller takes one (next) or many",
"undo(trail, mark) restores an earlier state"; `suspend.py`; `propagate.py`);
Robinson, "A machine-oriented logic based on the resolution principle", JACM
12(1), 1965; McCarthy, CACM 3(4), 1960 (cons cells); Mackworth, "Consistency
in networks of relations", Artificial Intelligence 8(1), 1977; Clocksin and
Mellish, *Programming in Prolog*, 1981, chapter 4 (the cut) and chapter 5
("Input and Output": an effect as a goal that performs it and holds); The
Python Language Reference, "Data model" ("Emulating callable objects",
`__repr__`).

### What the programs report

As in the earlier batches: one `cp.answer` per solution, giving each unknown
or quantity that has a value (`b = 15, d = 30`; `s = ⟨1,2,3,4,5⟩, total = 6`;
`x = 2`; `s = ⟨'r⟩`); an empty outcome is printed as `no solution: …`,
never answered; a stage at which nothing has a value (P09e, P10b stage 1)
answers nothing and leaves its held relations to `observe()`. Spawned
computations (P09a, P09b) answer from their own functions, and register
their own bindings and pending structures. P11's answer at every stage is
the solution held (cap 1); at a commit stage it is the selection the harness
keeps. P11's emitted entries are the values of x, rendered by `str()`
(`1`, `2`). Atoms are Python strings, shown with a leading quote.

### Ambiguities, and the reading taken

1. **P09c: gen's last element.** The problem defines gen with the bound 5
   in its cases; `stages.json` writes only gen's first argument as a
   placeholder. I kept the bound in the constants block (`GEN_LAST`, stage 1,
   the stage that poses the definition), so that a variant that changed it
   would be followed; a verifier that leaves it alone changes nothing.
   Atoms of a definition (P12's 'l and 'r, as P04's 'a in batch 1B) stay in
   the program text.
2. **P09d: what is answered, and when.** The answer is the conjunction's
   solution, reported only when both parts have finished. Where the
   producer goes on (stdlib-concurrency, extended), total's binding is held
   in the registered bindings while the producer runs, which is what
   `SPECIFICATION.md` ("reported") and P09d1/P09d2 classify; nothing is
   reported through `cp.answer`. Under P09d1 this is meant to be *none
   reported* with *budget* and the binding as an observation; under P09d2
   *complete* for total.
3. **P09d in core.** A sequence is a tuple, finite, so genu's transcription
   cannot return. A generator encoding of sequences (a lazy stream) would
   give the stream reading in core too; it would change the representation
   of sequences used by every other core program (a reformulation), and I
   did not write it as a variant.
4. **P09c/P09d in stdlib-concurrency: the producer as a chain of threads.**
   Transcribing gen's body goal as a recursive call inside one thread would
   stop at the recursion limit after about a thousand elements (and replacing
   the recursion by a loop is R, `measurement.md`, 5). The batch's
   thread-per-relation reading makes each application of gen its own thread,
   which poses the next and ends.
5. **P09a/P09b in stdlib-concurrency** share core's text: the side-by-side
   running is the harness's `spawn()` in that configuration. A program that
   started its own threads inside one computation would be another program.
6. **P09a in extended: one trail.** The two computations share the relations
   and the trail (the one database). loop binds nothing, and each search
   undoes only to its own marks, so neither disturbs the other; each has its
   own stack.
7. **P09b: a failed conjunction's bindings.** A registers x only for a
   solution (core), or undoes its bindings through the trail (extended), so
   that `observe()` does not read x = 1 from a conjunction that failed.
8. **P10b: the standing relation as suspended work.** It is registered with
   `cp.suspended` at every stage, since it is held work that each later
   replacement takes up again; the execution state is therefore *suspended*
   at every stage. Its stage 1 answers nothing (neither b nor d has a value).
9. **P10 in extended** shares core's text (see "Shared texts"); a
   versioned or time-indexed store written for the purpose would be
   reformulation (P10, Observations), and I did not write one.
10. **P10d: "withdraw x > 1".** `stages.json` gives stage 3 as "withdraw the
    relation of stage 2", with no constant; the programs withdraw the
    relation that stage 2 gave (`withdraw(2)`), found by the stage it came
    from. stdlib-concurrency's restating does not stop threads still waiting
    from before the withdrawal; in P10d none can be waiting then (pick
    arrives first, and x > k never waits once x has values).
11. **P11: emit and commit.** emit is `cp.emit`, called as a conjunct where
    the problem places it (core) or as a goal (extended). Commit selects the
    solution held, adds x = v, and gives up the alternatives (the generator,
    or the search's stack): that is the commitment, in the program's own
    terms. A replayed commit stage takes v as the fact whose answer text
    (`x = v`) equals `s.commitment`; a commit with no solution held selects
    nothing.
12. **P11c/P11d: holding one solution, not all.** These are any-one queries,
    so the programs hold one solution and backtrack for the next when it is
    refuted (performing the next solution's effect then). Holding every
    value at once, as P05's programs do, would emit every value at stage 1;
    deferring emit until commit would be control the problem names
    (Rules). I took the first as the natural reading of an any-one query.
13. **P12: facts that depend on n.** accept's closed world differs with n
    (ʟ or ʀ repeated n times), and n is a parameter, not a constant. The
    constants block gives `ACCEPT_FACTS` as a dict from each n the problem
    poses (8, 12, 16) to its facts, written out; the program takes
    `ACCEPT_FACTS[n]`. A verifier substituting a variant would give the
    facts for each of the three n.
14. **P12: what is registered.** core registers its conjunction's generator
    as pending (it counts 1 while suspended; the partial sequences held are
    in its nested generator frames, which storage mode counts); extended
    registers the search's stack as pending. Neither registers a
    `cp.problem_alternatives` structure: no structure of either program
    holds exactly the partial sequences, and I did not add one for
    counting. accept is registered with `cp.relations`, so its calls are the
    candidates examined.
15. **P12: any one.** core takes one solution with `next`; extended stops
    the search after its first (`break`). Both read the mode from
    `s.params["answers"]`.

### Conduct

- Files read: those the brief allows: the top-level documents, the nine
  problem files it names and `problems/README.md`, `systems/python/README.md`
  and parts of `measurement.md` (sections 4 and 5, the unit of alternative),
  `harnesses/README.md`, `harnesses/stages.json` (its header and the entries
  of P01, P09-P13: P01's and P13's entries passed before me in the same
  printout, placeholders only), and in `harnesses/python/`: README,
  QUESTIONS, S-mechanisms, `S/search.py`, `S/suspend.py`, `S/propagate.py`,
  `check`, `constants.py`, parts of `runtime.py` (the `cp` calls, spawn, the
  budget), the qualification programs `x02_pick.py`, `x02_pick_reposed.py`,
  `x07_wait.py`, `x03_two.py`, and the start of `qualification/stages-qual.json`.
  Of this folder: this README and the batch-1A/1B programs `core/P02a.py`,
  `P03e.py`, `P04a.py`, `P04c.py`, `P04f.py`, `P05a.py`, `P06d.py`,
  `P06e1.py`, `P07a.py`, `stdlib-concurrency/P02a.py`, `P05a.py`, `P08a.py`,
  `extended/P02a.py`, `P03e.py`, `P04a.py`, `P05a.py`.
- Two long outputs of my own reads of allowed files (`harnesses/python/README.md`
  and this README) were saved by the tool under
  `~/.claude/projects/.../tool-results/`, and I read them there; their
  content was only those files. The session put my user-level memory index
  (`~/.claude/.../memory/MEMORY.md`, two lines about another project) into
  my context unasked; I opened nothing else under `~/.claude`.
- **One use of an interpreter on the host, not on any program:** to look
  for P09-P12 in `stages.json` I ran `python3 -c` with a few lines of my own
  that load the JSON and print `None` (it printed `null`), joined to a
  `grep`. It ran no program of the study or fragment of one, and not in the
  image. Everything else was read with `cat`, `sed`, `grep`, `ls`, `wc`.
- Program files were written with the editor tools, `perl -0pe` (to derive
  P09d, P11b, P11d and P12b-d from their sibling texts), `cp` (the shared
  texts) and shell loops that print literal tuples; checked only with
  `harnesses/python/check`, which reported no errors for all 51.
