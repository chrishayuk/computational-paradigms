# Classifier A, algol-60, batch 1B (P07–P08): notes

Classifier A (a Claude agent). Clone at commit 3c7c778, not modified. Output
`algol-60.json` beside this file. The scripts are here too: `atoms.py` cuts each
token file into constructs, `classify.py` classes them (rules and per-program
overrides, each with its METRICS.md rule), `tokens_out.py` writes and checks the
spans, `summ.py`, `beh.py` and `modes.py` read the records, `equiv.py` checks
the residuals, `build.py` assembles the JSON, and `verify.py` checks coverage.
`show-*.txt` are the construct-by-construct listings I reviewed.

## Texts

There are 16 texts, each classed once under the first path in
`TEXTS-1B-P07-P08.tsv`. `report/P07d.alg` also stands for P07e, `report/P08a.alg`
for P08b, and each `x1/*.a60` for its identical `x1sim` file. No class differs
between configurations: S-mechanisms.md lists no S mechanism in any of them, and
the x1 and x1sim files are byte-identical. So nothing is classed a second time.
The report and x1 texts have the same structure line for line. Only the input
and output statements differ (`ininteger`/`outstring` against `read`/`PRINTTEXT`/`NLCR`).
I checked that every line's set of classes is the same in the two dialects (`cmp.py`).

## Constructs that were hard to class, and the reading I took

1. **The holding code (rule 19).** Every program holds its relations in
   problem-specific code: an `examineN` evaluator per relation, `equal`, and a
   `propagate` fixpoint loop. I classed it R. Inside the evaluators I split
   them by rule 19:
   - P: computing a place (`xv := c1 - yv - zv`, `vv ÷ uv` with its
     divisibility test, `av := cons(...)`, the decomposition of b = s ++ c),
     and the test of a fully known relation with its verdict
     (`if … ≠ c1 then inconsistent := true`).
   - R: the knownness tests (`if xk ∧ yk then`, `if ek[e] ∨ ek[f] then`),
     `xk := true`, `rN := false`/`qN := false` and `changed := true`.

   Three points are open to dispute:
   - I classed the evaluator's procedure heading and its begin/end R, as
     part of the holding code. One could argue they are P, as the relation's
     "definition".
   - I classed `propagate`, all of it including its order dispatch on `ord[j]`
     in P07a, R by rule 19. A reader could class the fixpoint loop C
     ("explicit scheduling").
   - I classed the `ord` array and its declaration R. The instance line's
     order drives the examination order. Reading it from the input is H
     (harness README 2.7.1).
2. **The unknowns' representation.** I classed the value variables (xv, av,
   ev, xs, nx and the like) P, as the unknowns. I classed the "known" flags
   (xk, ak, ek) R, as holding state. A multiple assignment mixes the two
   (`xk := yk := zk := inconsistent := false`). It is one construct, so it
   takes one class, R. Likewise `top := rev1 := rev2 := conc1 := conc2 := 0`
   mixes the cell allocator with four counters. I classed it P, because it
   initialises the encoding (rule 13: it computes something the report
   depends on, so it is not H).
3. **`inconsistent`** is P: its declaration, its initialisation, and its
   setting by a test. **`held`** and its computation are H. I read them as
   collecting, for observe, what the program already holds (rule 13). They
   are close to the line, because the observe block depends on them. The
   guard `if ¬inconsistent then` around the answer printing in the main
   program is H, because it only chooses what to print. The same test
   inside `examine6` is P: it decides whether c is given a value.
4. **P08's late definition.** The flags `defined`, `concdef`, `rev1def` and
   `rev2def`, their setting at the defining stage, and the guards on them
   are R, by rule 19. The program says it holds "the application of a
   relation not yet defined until it can be decided". Rule 11 makes a
   *declaration* that changes how an undefined relation behaves C. These
   flags are code, not a declaration, but they do choose the open reading.
   A classifier who reads rule 11 broadly would class them C. This is
   ambiguous and could matter for the C/R split of P08.
5. **P08c's status protocol.** I classed rev and conc's "found / none /
   cannot tell" results R: `conc := 1`, `st`, `t`, the `if t = 1 then`
   tests, and `st := if rev1def ∧ rev2def then 0 else 2`. They are an extra
   result, which rule 3 treats as an extra argument, and they make the
   wait verdict. The case bodies (the head tests `same(a, pv)` and
   `a ≠ 0`, and the conjunct calls) are P, by rules 2 and 3. The guard
   `if st ≠ 1 ∧ rev2def then` combines a commitment to case 1 with the
   arrival flag. It is one construct; I classed it R.
6. **P08c case 1 as data.** rev's case 1 `rev(⟨⟩, ⟨⟩)` is read at stage 3 as
   two constant sequences p and r (`3: 0 0`). The reads and `readseq` are P,
   as stage information. This generalises the fact into data, which a reader
   could call R. The hidden variants decide whether it matters.
7. **The `b = s ++ c` evaluator in P08a.** Here conc's splitting direction is
   computed by a separate loop, not by conc. I classed it P under rules 15
   and 19: these are operations of the ++ encoding, and rule 19 says
   computing any place is P in every direction. Rule 14 (a separate
   direction function is R) would apply if this were read as a use of
   conc. The problem writes the stage with ++, so I did not read it that way.
8. **`same` and `sameel`** (the equality of the encoding) are P by rule 15.
   `sameel` treats two different unknown elements as unequal. No stage
   reaches that case.
9. **P07g's integer square root.** `entier(sqrt(c1) + 0.5)` is P, as a
   computation of the place x from c (rule 19). The built-ins sqrt and
   entier are core (3.2.4–5) and are listed under rule 9. `if nx > 0 then`
   is R, and `nx := 0` at the start is R ("x has no value").
10. **The program's outermost `begin … end`** is P, as the frame of the
    transcription (rule 1). The rules say nothing on it; H would also be
    defensible. It is 2 tokens per text.
11. **Rule 20 (separators).** A `;` goes to the construct after it. An `end`
    followed by its end-comment identifier (`end examine1`) is tokenised,
    and both tokens take the class of the compound's `begin`. A `begin` or
    `end` takes the class of the header that introduces it (rule 10).

## Outcomes

- All 45 behaviour records (3 configurations × 15 instances) are valid.
  None is `.INVALID`, none has a harness fault, a manual action or a safety
  stop, and there are no `raw-rerun-m2/` reruns. `rerun-m2-log.tsv` does not
  exist.
- x1 and x1sim agree with report on every stage, apart from the padding in
  integer printing.
- In report and x1, P08 is posed incrementally into a computation re-created
  for its budget. x1sim keeps one live process.
- **Cost and storage.** All 60 cost and storage runs agree with their
  behaviour runs in answers, states, observe text, suspended items and
  operation counts. So `mode_differences` is empty. The storage records'
  null peaks follow the harness's attribution rule (README 3.4): a peak is
  credited to a stage only where it exceeds the earlier one. They are not
  missing measurements.
- **Single-stage residuals (P07b, c, f).** Spec, Outcomes 2, counts a
  residual only if the program "holds and acts on [it] at a later stage",
  and a one-stage problem has no later stage. I counted them as reported:
  they are the program's holding structure, read by observe, which the
  mechanism would act on, and the problem file gives exactly these cases
  as *residual*. I also set **identical to the posed information** true.
  The rule is unclear for one-stage problems.
- **P07e** reports none: "no solution" in observe and no answer. I classed it
  *complete* / *explicit*, with simplification null. The table has no
  representation for an empty set reported as empty.
- **P08 readings.** In each P08 entry, `semantic` gives the open reading and
  `semantic_by_reading` gives both. At P08a/b stages 2–3 and P08c stages 2–3
  the result is *unsound* under the closed reading, because the program
  reports held solutions where that reading has none. The program never
  reports "none", so no conclusion is withdrawn at the stage where the
  definition arrives.
- **P08a stages 3–5** are *reducible*. x = y and y = z are held as
  relations to decide, not as identifications, and the solved form has
  none. equiv.py checks their equivalence by union-find.

## Files read outside the list

- None of the forbidden files was opened. I listed some directory names
  (the repository root, `programs/algol-60/`, `results/algol-60/` and its
  `report`/`x1`/`x1sim` folders). The listings showed that
  `results/algol-60/classes/`, `results/*/P0x.md` and
  `programs/algol-60/README.md` exist, but I read none of them.
- The session start showed the user's auto-memory index
  (`~/.claude/.../memory/MEMORY.md`, two lines about other matters). I did
  not open it, it bears on nothing here, and I note it only because the
  brief lists `~/.claude`.
- The brief's first paragraph says "batch 1A", but its title and paths say
  1B. I took it to be 1B.

## Summary

**Tokens** (16 texts, 17,531 tokens): P 3,409, R 3,160, H 10,962, C 0, S 0.

| text | P | R | H |
|---|---|---|---|
| report/P07a | 101 | 292 | 821 |
| report/P07b (= P07f's structure) | 66 | 172 | 598 |
| report/P07c | 37 | 108 | 495 |
| report/P07d (and P07e) | 137 | 212 | 736 |
| report/P07f | 66 | 172 | 598 |
| report/P07g | 155 | 45 | 227 |
| report/P08a (and P08b) | 713 | 370 | 1502 |
| report/P08c | 455 | 209 | 784 |
| x1/P07a (and x1sim) | 92 | 292 | 741 |
| x1/P07b | 60 | 172 | 536 |
| x1/P07c | 34 | 108 | 443 |
| x1/P07d (and P07e, x1sim) | 131 | 212 | 664 |
| x1/P07f | 60 | 172 | 536 |
| x1/P07g | 152 | 45 | 203 |
| x1/P08a (and P08b, x1sim) | 707 | 370 | 1372 |
| x1/P08c | 443 | 209 | 706 |

**Outcomes** (75 stage entries over 45 behaviour records): every stage is
reached and *complete* under the open reading.

| result | entries | which stages |
|---|---|---|
| explicit, finished | 33 | P07a in all six orders, P07d, P07e (none reported), P07g (both roots), P08a stage 6, P08c stage 4 |
| solved form, finished | 9 | P08a/b stage 1, P08c stage 1 |
| residual, reduced, suspended | 15 | P07c, P08a/b stage 2, P08c stages 2–3 |
| residual, reducible, suspended | 15 | P07b, P08a/b stage 3, P08a stages 4–5 |
| residual, inconsistency undetected, suspended | 3 | P07f |

- Under the closed reading, 18 P08 entries are *unsound*.
- No mode differences, harness faults, interventions or withdrawn conclusions.
- **Expressibility:** every P07 and P08 sub-problem is *expressible with
  reformulation* in all three configurations. The reformulation is the
  problem-specific holding code, R by rule 19. Only conc's forward
  direction in P08a is *expressible*.
- **Late definition:** all nine P08 programs take *permission awaited*:
  definition flags guard code that is already in the program.
- **S mechanisms:** none, in any program.
