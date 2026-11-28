# Classifier A (Claude), python, batch 1B, P08: notes

Output: `python.json` beside this file. It is built by `build.py` from the
span specifications `spec_core.py`, `spec_ext.py` and `spec_std.py`, using
`frame.py` and `toklines.py`. `check.py` confirms that every token of all
nine texts is covered exactly once. `summ.py` and `modes.py` are the
read-only record summaries I used. No program, and not the system, was run.

There are nine distinct texts (`TEXTS-1B-P08.tsv`). None is shared between
configurations, so none needed separate classing.

A note on conventions. Layout tokens (`INDENT`, `DEDENT`, and an `INDENT`
on a docstring line) take the class of the construct that follows them
(rule 20). A `NEWLINE` goes with its statement. The `DEDENT`s at the end of
the file go with the stage loop (H).

## Constructs that were hard to class

1. **The holding machinery in core and stdlib-concurrency: R or S?**
   `decide()`, `held`, `place()`, the `EVALUATOR` table and the `Unknown`
   class make up a small fixpoint loop over named relations. That loop is
   arguably "general over relations" (rule 19, second bullet), and so S.
   That reading would move the core and stdlib programs into *extended*.
   I classed it R (rule 19, first bullet): its evaluators, its conventions
   and its table exist only for this problem's =, ++ and rev. This is the
   largest single block likely to be disputed (about 200 tokens per
   program).
2. **Wrapper calls around a stage's information.** `held.append((...))`
   (core), `pose((...))` (stdlib) and `q.wait(Application(...))` (extended)
   are split by rule 10. The posed relation is P. The wrapper is R in core
   (holding), and C in stdlib (it starts a thread) and in extended (a
   freeze call).
3. **`cases = {"rev": [], "conc": []}` in extended.** I classed it C under
   rule 11, and list it here as rule 11 asks. It declares rev and conc as
   relations with no cases, so an undefined relation fails inside a search
   rather than raising NameError. That is the same effect as `:- dynamic`.
   The dispatchers `rev()` and `conc()` that iterate over the arrived
   cases are P (rule 6: the disjunction of the stated cases, in order).
4. **The `Application` class, `NAME` and `defined` in extended.** I
   classed these S, as a wait-for-definition layer of the program's own.
   METRICS gives this as an example of S. The author's provenance lists
   only `unify` and resolution as the program's own S, so classifier B may
   differ here. `Application.__repr__` is H (an adapter for `observe()`).
5. **Imports** (`from S.search import ...`, `import threading`). I
   classed them C by rule 1: removing one changes only whether the program
   runs. Their calls are classed where they are used. S is defensible for
   the S imports.
6. **reverse()'s guard in stdlib** (`a is not None and "rev" in defined`)
   is C, by rule 2. It is both a rule-19 known-place test (R) and
   synchronisation on a permission flag.
7. **Restating case 1 in P08c's stage-4 def (core, stdlib).** I classed it
   R. A Python def replaces a function, so stage 4 writes stage 3's case
   again. It could be argued P, since it is still rev's case 1.
8. **The `failed` stores** are R in every configuration: the program's
   record of verdicts, not given by the problem. This puts 5 R tokens into
   each extended program. I still judged extended P08a, P08b and P08c
   *expressible*.
9. **The dead `prefix` evaluator in P08b** (core, stdlib) is R. P08b has no
   ++ relation, so removing it changes nothing (rule 1).

## Outcomes that were hard to class

- **Both readings.** I recorded `semantic` and `simplification` as
  `{"closed": ..., "open": ...}`. Under the closed reading, a residual
  that holds rev(...) with no definition denotes the empty set. I classed
  it *complete* / residual / *inconsistency undetected*, applying
  SPECIFICATION's definitions literally. The problem file names only the
  "no solutions" report as closed-complete, and does not say how a held
  application is classed under the closed reading.
- **Core stage 2, error.** `observe()` reads a = ⟨x,y,z⟩. The registered
  list still shows ('rev', (a, b)), but only because NameError came before
  its removal, and the process then ended. So I classed it as rev dropped:
  open *complete* / solved form, closed *unsound*, state *error*. The
  alternative is *none reported*, since no answer was collected.
- **Core stages 3 to 6 (P08a), 3 (P08b) and 3 to 4 (P08c)** are *not
  reached* (AMENDMENTS 3.2 and the brief). Each reposed run errs while
  replaying stage 2, and the record notes that stage k was never posed.
  The records' own state field says `error`.
- **Extended P08a stage 4: partial, disputed.** The report prints
  a = ⟨h,h,h⟩, b = ⟨h,h,h⟩, x = y = z = h. Read as written, that denotes
  x = y = z, a proper subset of the valid outcomes. I traced `unify` and
  `Queue.bind` by hand. The held state is in fact right: two distinct Vars
  are both named "h" (from `rev_2` and `conc_2`), and b = ⟨z, y, y⟩. I
  classed it on the report, as *partial*. *undetermined*, or *complete* on
  the held state, are possible readings.
- **Extended P08a stages 4 to 6: alternatives pending.** The harness says
  so: 11 choice points stay registered after the first solution is kept.
  But the search generator that owns them has been dropped, so nothing can
  resume them. Recorded as an observation.
- **Stdlib P08a stage 6: unsound.** c is never bound. `prefix()` is
  passed the *values* of its places, so it poses the tail equation as
  (None, ⟨y,x⟩), which binds nothing. The cost run's counts agree (equal 4
  times, prefix once). The report leaves c unconstrained. Core has the same
  bug, but never reaches stage 6.
- **Stdlib stages 3 to 5: reducible.** x = y is held as a relation,
  because the evaluator of = cannot decide two unknown places.
- **The "no solution" reports** (P08c stage 3 onwards, extended and
  stdlib) are printed, not passed to `cp.answer`. I took them as reported:
  for Python, the standard mechanism for answers is what the program
  prints, and the `failed` list is registered. Representation is
  *explicit* (none).

## Rules I think ambiguous

- Rule 19 does not say where "written for the problem's own relations"
  ends and "general over relations" begins, for a generic fixpoint loop
  dispatched through a per-problem table.
- The schema has one `semantic` field, but P08 needs two readings.
- SPECIFICATION's "not expressible ... or supporting code" sits uneasily
  with *extended*, where S is the configuration. I read it as applying to
  S a configuration lacks.
- The brief's "code awaited" against "permission awaited" is not sharp
  for extended. The application waits on a flag Var (`defined[name]`), but
  its readiness test is the definition's presence (`cases[name]`). I
  called it *code awaited*, with that caveat. I called stdlib *permission
  awaited*: the thread tests only the flag `"rev" in defined`.

## Mode runs

Each of the 18 cost and storage records agrees with its behaviour run on
every stage: answers, states, `observe` (after masking object addresses),
print output and errors. So `mode_differences` is empty, and the records
compared are listed under `mode_records_compared`. There are no
`*.INVALID.json` records, no `raw-rerun-m2/` directories, and no
`rerun-m2-log.tsv`.

## Files read outside the brief's list

None of the repository's forbidden files were read. Directory listings
showed the names `calibration/`, `reviews/`, `results/python/classes/` and
`programs/python/README.md`; none was opened. The session's environment
also put the user's auto-memory index (`~/.claude/projects/.../MEMORY.md`,
[redacted by tools/redact-transcripts.py: what the entries are about]) into my context
unasked. I read nothing further from it, and it has no bearing on these
classes. Large command outputs were saved by the tool under
`~/.claude/projects/.../tool-results/`. Those files are my own outputs of
the allowed files (METRICS.md, systems/python/README.md,
harnesses/python/README.md), and I read them back only as that.

## Summary

**Tokens**, over the 9 texts (10,545 tokens):

| class | tokens |
|---|---|
| P | 3,086 |
| H | 3,011 |
| R | 2,249 |
| S | 1,146 (extended only, 382 per program: unify 182, resolution 58, wait-for-definition layer 142) |
| C | 1,053 (stdlib 816, extended 237) |

Per program, P/C/R/S/H:

| program | P | C | R | S | H |
|---|---|---|---|---|---|
| core P08a | 403 | 0 | 387 | 0 | 309 |
| core P08b | 204 | 0 | 460 | 0 | 262 |
| core P08c | 303 | 0 | 342 | 0 | 318 |
| extended P08a | 567 | 83 | 5 | 382 | 427 |
| extended P08b | 232 | 59 | 5 | 382 | 390 |
| extended P08c | 467 | 95 | 5 | 382 | 401 |
| stdlib P08a | 403 | 282 | 325 | 0 | 314 |
| stdlib P08b | 204 | 267 | 412 | 0 | 267 |
| stdlib P08c | 303 | 267 | 308 | 0 | 323 |

**Outcomes** (39 behaviour stages):

- **core.** Stage 1 is complete. Stage 2 is an error (NameError, state 3):
  open complete / solved form, closed unsound. Every later stage is *not
  reached* (7 stages). Late definition: *neither*.
- **extended.** The application is held (state 4) and resumed in the same
  computation at stage 4. P08a: stages 1 to 3 complete (2 and 3
  residual: reduced open, inconsistency undetected closed); stage 4
  *partial* (two unknowns printed under one name; the held state is
  right); stages 5 and 6 complete. P08b: complete, with the report
  distinguishable from failure. P08c: stage 3 is closed complete / open
  unsound (solved with case 1 only, and failed); stage 4 is unsound under
  both readings, since the application is not reached. Late definition:
  *code awaited*.
- **stdlib-concurrency.** Threads wait on a permission flag. P08a: stages
  1 to 5 complete (residual, reducible from stage 3); stage 6 *unsound* (c
  dropped). P08b: complete. P08c: as extended. Late definition:
  *permission awaited*.
- **All configurations.** No harness faults, no manual actions, no mode
  differences.
