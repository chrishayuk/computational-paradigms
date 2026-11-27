# Python programs, wave 1, batch 1A (P01-P03)

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

## Shared texts

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

## Per configuration and sub-problem

All programs: primary; author `implementation-python` (an agent, Claude
Opus 5.5); precursor seen: none. "Idioms" lists the sources each file's
`PROVENANCE` block cites; "S" is the S mechanisms used (`S-mechanisms.md`),
and any of the program's own.

### core

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

### stdlib-concurrency

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

### extended

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

## What the programs report

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

## Ambiguities, and the reading taken

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

## Conduct

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
