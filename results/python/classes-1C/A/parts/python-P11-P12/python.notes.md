# Classifier A: python, batch 1C, P11 and P12. Notes

Classes are in `python.json` beside this file. The scripts that made them
are here too: `tokens_spec.py` (the markers, one construct each, with its
class and rule), `build_tokens.py` (spans and the coverage check),
`build_outcomes.py` (stage classes from the raw records), `assemble.py`,
`summarize.py` and `view.py` (read-only views of records and token files).
No program and no part of the system was run. Only the scripts above were
run, over the records and token files.

## Texts

There are 16 distinct texts. The 8 stdlib-concurrency files are byte-identical
to core's, use no module of that configuration, and get the same classes, so
each is classed once under `core/` (TEXTS-1C-P11-P12.tsv). No class differs
between the two configurations. Every token index of every text is covered
exactly once, which the scripts check.

**Layout.** An INDENT takes the class of the header that opens its block.
A DEDENT takes the class of the header whose block it closes (rule 10,
worked out with a stack). A NEWLINE goes with the statement it ends.

## Constructs that were hard to class

1. **`cp.emit(x)`: P, not H.** P11's own "Rules" say "emit and commit are
   problem tokens". `harnesses/python/README.md` §7 item 4 and
   `harnesses/README.md` §11 ("the emit stub's binding") list it as H. I
   followed the problem file. That is 6 tokens (`cp.emit(x)` and its
   NEWLINE) in each core program, and 10 (`cp.emit(deref(x))`) in each
   extended `emit` relation. The rule conflict should be settled for
   all systems.
2. **The holding code of P11c/P11d is R (rule 19), not C.** This covers
   `known`, `solutions`, `added`, `holds`'s dispatch, `satisfies`, `advance`,
   `add`, extended's `next_solution`, and storing the stage-1 solution. It
   keeps the solution taken and the relations added, and asks stage 1's
   generator (or search) for the next solution when a later relation refutes
   the one held. That retry is backtracking, so it looks like control. But
   removing it changes the values reported at stage 2 (rule 1). It is
   written for this problem's relations, so rule 19's first bullet makes it
   R, in extended too. The evaluators `different` and `equal`, and the
   `return different(...)` / `return equal(...)` calls, are P (rule 19's
   evaluator split).
3. **Commit.** `def commit`, the selection `v = known.get("x")` and
   `add("=", v)` are P (P11 Rules: commit is a problem token). The branch
   that decodes a replayed `s.commitment` (`if commitment is not None: chosen
   = …; v = …; else:`) is H. It only takes the verbatim answer as x = v
   (README §7 item 3), and an incremental program reaches it only after an
   error.
4. **`solutions.clear()` (core) and `stack.clear(); solutions.clear()`
   (extended) are C.** They are a cut. They give up the alternatives beyond
   the problem's own x = v, which already fixes the values reported. Without
   them, P11d stage 3 would resume the generator and perform emit(2) and
   emit(3), which is *extra*. So they are exactly "the control tokens used to
   avoid extra" that P11 asks to record: 6 tokens in core and 12 in extended.
   Rule 16 (a reset that only lets store be reused) would also make them C.
5. **Taking one answer (`next(...)`, extended P12's `break`) and the "all"
   loop (`for found in answers`, `for _ in solutions`) are P.** I read them
   as the query itself (the any-one query and the all query), not as a
   deferral. The tests on `st.params["answers"]` that choose between them
   are H (README §7 item 3).
6. **`known` in P11a/P11b core is H, but in P11c/P11d it is R.** In P11a/b
   it only exposes the answer to observe() (rule 13). In P11c/d the program
   reads it back (advance, commit).
7. **`stack = []` in extended is H.** The search would make its own stack.
   The list exists only to be registered with `cp.pending`. `trail = []` and
   `binder = Queue()` are S: they are the state the program's own unifier
   binds through.
8. **`NIL = ()` in extended.** In P12 it is P, as the encoding of ⟨⟩
   (rule 15). In P11 it is never used (dead text copied with the mechanisms),
   so I classed it S with "unify". Rule 1 would leave it unclassifiable:
   removing it changes neither meaning nor behaviour.
9. **Extended `either` and `equal` are P.** They implement the problem's
   disjunction and equality as relations over the S unifier (rules 6 and
   15), just as core's `for e in ("l", "r")` is P. They could be argued S,
   as generic connectives reusable across problems (the provenance cites the
   P04 programs).
10. **The imports `from S.search …` and `from S.suspend …` are S**, credited
    to their listed mechanisms (9 and 11 tokens). The `search(...)` call is C
    (S-mechanisms.md: a search directive is C). The goals inside it are P.
11. **core `pick(x)`'s `if x is None or x == v` is P,** as the head match of
    each fact (rules 2 and 6). Strictly, the `x == v` branch serves a
    direction no query uses (x known), which rule 3 would make R. That is
    the 4 tokens `or x == v` per text.
12. **The constants blocks are P** (stage information), including P12's
    dict of accept's facts keyed by n.

## Outcomes that were hard to class

1. **Bindings held at a budget (5 runs: extended P12a.n16.all, P12b.n16.all,
   P12c.n16.all, P12c.n16.any, P12d.n16.all).** All five stopped at 10⁸
   instructions. Each holds, in its registered bindings, the candidate the
   search was trying: a full sequence that is not accepted, or (P12c) a
   15-element prefix ++ t. SPECIFICATION ("reported") says a binding
   `observe()` can read at the moment a budget runs out is reported, whether
   or not the answers mechanism would deliver it. Under that rule the report
   denotes an invalid outcome, so I classed all five **unsound**. Each entry
   also gives `alternative_reading`, judged on the answers alone:
   P12a.n16.all *partial* (⟨ʟ×16⟩ only), P12b.n16.all *complete* (⟨ʀ⟩, but
   the space was not covered), P12c.n16.* *none reported*, P12d.n16.all
   *complete*. These are **classification-sensitive**. I think the rule was
   written for a producer's binding (P09d2, P15b), not for a search's trial
   binding, which the trail would undo. It should be clarified.
2. **P11d stage 3** is an empty valid outcome, reported by a printed "no
   solution" line and empty bindings, with no `cp.answer`. I classed it
   *complete*, representation *explicit* (none, given as none), and answer
   completeness yes. The program's standard mechanism for answers is what it
   prints.
3. **The effects axis** is not in the brief's output template. I added
   `effects`, `effects_log` and `effects_this_stage` to the P11 entries:
   - P11a: *exact* in all three configurations.
   - P11b: *extra* (⟨1,2⟩; 1 performed before commitment and refuted by the
     test).
   - P11c: *extra* (⟨1,2⟩; 1 at stage 1, refuted at stage 2 and never
     committed; 2 at stage 2, before commitment, then committed).
   - P11d: *exact* (⟨1⟩, emitted at stage 1 and committed at stage 2).

   No entry was duplicated by reposing, since every stage was posed
   incrementally. The cost and storage runs wrote only to the observation
   logs, as they should.
4. **P11a/P11b keep alternatives after commitment.** These are one-stage
   problems that commit when they report, but the generator (core) or the
   search's 4 choice points (extended) are still held afterwards. The state
   is *alternatives pending*, and a further request would emit(3).
5. **P12 problem-defined alternatives** (partial sequences held) were not
   registered by any program, so they are unavailable (AMENDMENTS 3.1). I
   give the storage run's suspended generator frames and choice points
   instead.

## Other observations

- There are no `*.INVALID.json` records, no `raw-rerun-m2/` folders and no
  `rerun-m2-log.tsv` (`results/python/rerun-m2-log.tsv` does not exist).
  `batch-log.tsv` has no P11 or P12 line. The 1C logs list 252 jobs (84 per
  configuration), and every one has its record.
- **Mode differences: none.** In every cost and storage run, the answers,
  the execution state, the observed bindings and the step counts are
  identical to the behaviour run. This includes the five runs that ended in
  budget, which stopped at the same candidate.
- Candidates examined (cost runs) match the depth-first positions in P12's
  table exactly. For any one: P12a/d n+1, P12b 2ⁿ+1, P12c 2ⁿ⁺¹−1. For all:
  2ⁿ⁺¹−1. That holds in core at every n, and in extended at n = 8 and 12.
  At n = 16 extended's budget ran out after 37,858 (a), 88,650 (b) and
  41,061 (c, d) of 131,071 candidates.
- Genericity (not a classification): P12's constants block keys accept's
  facts by the n values posed (8, 12, 16). A hidden variant with another n
  would find no facts.

## Rules I think ambiguous

- METRICS rule 13 / harness README §7 against P11 "Rules" on `emit` (item 1
  above).
- SPECIFICATION "reported" for bindings held at a budget by a backtracking
  search (outcome item 1).
- Whether giving up alternatives at a commit is P (part of "commit") or C
  (a cut). I chose C because the problem's commitment is the information
  x = v, which the program adds separately.
- Expressibility where only the staging needs R tokens. Under rule 19, P11c
  and P11d are *expressible with reformulation* in all three
  configurations, because the programs of record carry R tokens. The
  relations themselves are transcribed. Rule 19 lists P05-like staged
  problems, which is why I applied it here.

## Files read outside the brief's list

- Two files under `~/.claude/projects/…/tool-results/` (`bzjtgc1p9.txt`,
  `bs1nbfy9f.txt`). These are the tool's saved copies of the output of my
  own `cat` of `harnesses/README.md` and `harnesses/python/README.md`, both
  of which the brief allows. They hold nothing else. A third such file
  (`b5ol4x5jz.txt`, the output of `systems/python/README.md` with
  `harnesses/python/S-mechanisms.md`) was created but not opened; I re-read
  those two files directly instead.
- I did not open any file under `~/.claude` myself beyond those. The
  session's harness injected the contents of an auto-memory file
  (`~/.claude/projects/…/memory/MEMORY.md`, two lines, [redacted by tools/redact-transcripts.py: what the entries are about]) into my context at the start. I
  did not read it, and it has no bearing on these classes.
- The shell's working directory was under `~/chris-source` (the session's
  start folder). I read nothing there.
- Nothing from `calibration/`, `reviews/`, `variants/`, `transcripts/`,
  earlier classes or results, `programs/python/README.md`,
  `programs/AUDIT-*.md`, other systems' folders or the web.

## Totals

**Tokens** (16 texts, 10,096 tokens):

| texts | P | C | R | S | H | all |
|---|---|---|---|---|---|---|
| core/P11a, core/P11b (each) | 166 | 0 | 0 | 0 | 88 | 254 |
| core/P11c, core/P11d (each) | 193 | 6 | 180 | 0 | 196 | 575 |
| core/P12a | 245 | 0 | 0 | 0 | 217 | 462 |
| core/P12b | 170 | 0 | 0 | 0 | 217 | 387 |
| core/P12c, core/P12d (each) | 233 | 0 | 0 | 0 | 217 | 450 |
| extended/P11a, P11b (each) | 150 | 15 | 0 | 266 | 119 | 550 |
| extended/P11c, P11d (each) | 204 | 23 | 206 | 266 | 201 | 900 |
| extended/P12a | 405 | 14 | 0 | 261 | 292 | 972 |
| extended/P12b | 330 | 14 | 0 | 261 | 292 | 897 |
| extended/P12c, P12d (each) | 393 | 14 | 0 | 261 | 292 | 960 |
| **core (8 texts; also stdlib-concurrency)** | 1,599 | 12 | 360 | 0 | 1,436 | 3,407 |
| **extended (8 texts)** | 2,229 | 132 | 412 | 2,108 | 1,808 | 6,689 |
| **all** | 3,828 | 144 | 772 | 2,108 | 3,244 | 10,096 |

S per extended program: search import 9, suspension-queue import 11,
"unify" 188 (P11) or 183 (P12; NIL is P there), and "resolution" 58. The
program's own mechanisms are counted once for the configuration. The
listed mechanisms' own sizes (176 and 537 tokens) are counted once, apart.

**Outcomes:** 96 stage entries from 84 behaviour runs (P11: 12 runs, 24
stages; P12: 72 runs, 72 stages).

- **91 complete.** That is all of core and stdlib-concurrency (64), and
  27 of extended's 32.
- **5 unsound, and classification-sensitive.** These are extended's n = 16
  runs that ended in budget with a trial binding held. Judged on answers
  alone they would be 1 partial, 2 complete and 2 none reported.
- **Execution state:** finished for every "all" query that covered the
  space and for every committed P11 stage. Alternatives pending for every
  "any" query and every pre-commit P11 stage. Budget for those 5.
- **Effects:** exact for P11a and P11d, extra for P11b and P11c, the same
  in all three configurations.
- **Mode differences:** 0.
- **Expressibility:** P11a, P11b and P12a–d are *expressible* in every
  configuration. P11c and P11d are *expressible with reformulation* in
  every configuration, because rule 19 makes their holding code R.
- **Late definition:** none in this batch (no P08). There are no harness
  faults.
