# Classifier 1C-A: ALGOL 60, P09 and P10

The classes and outcomes are in `algol-60.json`, beside this file. The per-text span specs are in
`specs/`. `build.py` checks that every token is covered exactly once. `derive_x1.py` derives the x1
spans from the report spans by aligning the token sequences, with hand overrides. The texts
differ only in their I/O procedures and stropping. `cmpnonh.py` confirms that the non-H classes of
report and x1 are identical apart from the read syntax. `cmpmodes.py` compares the modes, and
`check_residuals.py` checks the residuals.

## Texts

There are 18 distinct texts, from TEXTS-1C-P09-P10.tsv:

- `report/P09a.AB.alg` also stands for `report/P09a.BA.alg`.
- `x1/<file>` also stands for `x1sim/<file>`. The x1 and x1sim files are byte-identical, and no S
  mechanism differs between the two configurations, so no text was classed separately.

## Constructs that were hard to class, and the choice made

1. **Outer `begin`/`end` of the program, and the `end` of an inner block.** I classed these P,
   as the frame of the program (rule 10). The message loop's own `begin`/`end`, and the
   `begin`/`end` of each `if k = …` branch, are H, as part of the dispatch (harness README 2.7.2).
   Another reading would put the program frame under H.
2. **Rule 20, applied literally.** Every `;` or `,` takes the class of the construct that follows
   it, including the `;` that ends a declaration when a counter (H) follows it. This produces many
   one-token boundary differences that a classifier reading `;` as a declaration terminator would
   not have.
3. **Multiple assignments that mix roles** (`top := gen1 := gen2 := sum31 := 0`,
   `xk := yk := inconsistent := false`, `picked := r2 := w2 := false`). I split them by left part:
   each `v :=` takes v's class, and the shared right side takes the class of the first left part.
4. **Known-flags (`xk`, `yk`, `bk`, `dk`, `picked`, `r1`, `r2`).** I classed these R (rule 19: the
   record of which places are known, or of what is held). That includes P10a and P10c, where
   nothing waits and the flag only feeds the output "has no value". There the flag is still extra
   state that the problem does not give. Rule 1 alone would make it hard to call it P: removing it
   changes nothing reported for the posed queries.
5. **Continuation parameters.** The formal parameter `found` of `loop` (P09a) and of `equals`
   (P09b), and the argument `seconda` (the conjunction passed as a continuation), are R, under
   rule 4 (arguments the problem does not give). An actual argument that names an output adapter
   (`answera`, `answerb`) is H (rule 13). I first had `found` as H in P09a, and changed it so that
   P09a and P09b agree.
6. **P09b `equals`.** It is an evaluator of `=` that binds, tests and unbinds. I split it as rule 19
   says:
   - `u := cv` and the test `u = cv` are P;
   - `if uk`, `uk := true/false` and the call of the continuation are R.
7. **P09e.** `examine1`, `examine2` and `propagate` are written for the problem's own two
   relations, so they are R in the core configuration (rule 19), not S. Inside the evaluators:
   - the place computations, and the tests of fully known relations with their verdict
     `inconsistent := true`, are P;
   - the known-tests, the held-flags and the change flag are R.

   I classed `inconsistent` as P because it carries the relation's failure. `held` is computed only
   for the observe output, so it is H.
8. **P10d.** I split the construct three ways:
   - pick's facts are held as values, `xv`, `xa` and the loop over the facts: P (rule 6, a stated
     closed world);
   - the comparison `xv[j] > c2` and its verdict `xa[j] := false`: P;
   - `picked`, `r2`, the call `test` after every stage, and the withdrawal `r2 := false`: R
     (rule 19).

   `w2` (withdrawn) is read only by the observe output, so it is H, and so are the counters `pk`,
   `tested` and `alive`.
9. **Other H calls.** The answer counters `na`, `nb` (P09b), used only to print "no solution" in
   observe, are H as output-adapter state. The same goes for `if ¬ok then "no solution"` and for
   every answer and observe block.
10. **Array sizes and allocation.** `cells := if g > 5 then 1 else 6 - g` (P09c), the fixed
    `[1:1000]` (P09d, P10d), and `top := 0` are P, as part of the sequence encoding (rule 15).
    `top := 0` is a start-of-block initialisation, not a rule-16 reset.

## Outcomes that were hard to class

- **P09a.AB, computation B (report, x1, x1sim): *not reached*.** A was spawned first and ended the
  one instance, by budget in report and x1, and by the safety limit or SIGKILL in x1sim. B was never
  started (AMENDMENTS 3.2). In BA, B is complete. So the order of posing matters, because the
  computations run only one after the other.
- **P09a.BA in x1sim, attempt 2 (the 600 s rerun): A ended by SIGKILL at about 69 s**, before the
  limit (`safety_limit.hit` false), with no error text. I classed the final state as *error*, not
  *timeout*. The record does not say what sent the signal; store exhaustion is likely but not shown.
  I give both attempts as separate entries.
- **P09d in x1sim** ended with "Error: Wrong result type in TIRD" after 0.1 s. That is *error*,
  recorded verbatim, and *none reported* under both readings. That it is the reconstructed
  run-time's response to the deep recursion is not established.
- **P09d1 and P09d2 (report, x1).** Both are *none reported* with *budget*. genu makes a cell only
  when its recursive call returns, so no element of s and no total is ever held. P09d1 is not
  unsound. P09d2 misses total = 6.
- **P09b A.** The valid outcome is empty, and the program said "no solution" in its observe block.
  I classed it *complete*. For an empty set I recorded the representation as *explicit*, for want of
  a better class.
- **P09e.** The residual {x = y + 1, y = x − 1} is held as program state (the flags r1 and r2, which
  examine1 and examine2 act on). It is *complete*, *residual*, *reducible*, identical to the posed
  information, and *suspended*. SPECIFICATION 2 says a residual counts only if the program "acts on
  [it] at a later stage". This problem has one stage, so no later stage can exist. I accepted the
  held state as a report: the program examined each relation once and decided to wait, which is
  more than printing the input back.
- **P10d.** The program prints `[problem-alternatives x N]` but no `[alternatives]` tag, so the
  harness reads the state as *finished* while every alternative is held, all live. I kept
  *finished*, because nothing is pending for a request for more answers, and recorded the
  alternatives as an observation.
- **No mode differences.** Every cost and storage run of report and x1 has the same answers, ended_by,
  states and observe text as its behaviour run. There are no raw-rerun-m2 or INVALID records for P09
  or P10, so no entry carries `harness_fault`.

## Rules I find ambiguous

- **Rule 20, for the `;` that ends an ALGOL declaration**: is it a separator or part of the
  declaration? (See point 2 above.)
- **Known-flags where nothing waits** (P10a, P10c): R by analogy with rule 19, or P or H? Rule 19
  covers only code that holds undecided relations.
- **Expressibility when a program's R tokens are avoidable.** I judged the configuration, not the
  program. P09a, P09b, P10a and P10c are *expressible*, though their programs carry R tokens.
  P09b is the clearest case: rule 8 allows x := c1 followed by a test of x = c2. The program's
  R tokens are recorded all the same.
- **The SPECIFICATION 2 "acts on at a later stage" test**, for one-stage problems. (See P09e
  above.)

## Files read outside the brief's list

None in the repository. I read only the files the brief allows: README, SPECIFICATION, METRICS,
PROTOCOL, AMENDMENTS, the problems README and P03, P04, P05, P09 and P10, `systems/algol-60/README.md`,
`harnesses/README.md`, `stages.json` (the P09 and P10 part), `harnesses/algol-60/`
(README, S-mechanisms, QUESTIONS, and a listing of qualification), the P09 and P10 programs and
constants, their raw records, the batch-1C logs, and the token files. `rerun-m2-log.tsv` does not
exist. Two disclosures about locations outside the repository:

- **Saved tool output under `~/.claude`.** Two of my commands produced output too long to show.
  The tool harness saved that output under `~/.claude/projects/.../tool-results/`, and I read those
  two files there. They hold only my own command output, which was copies of allowed files:
  `systems/algol-60/README.md` with `harnesses/README.md`, and `harnesses/algol-60/README.md` with
  `S-mechanisms.md`.
- **The memory index in my session context.** The session started with the user's auto-memory index
  (`~/.claude/projects/.../memory/MEMORY.md`, two lines about an unrelated project) already in my
  context. I did not open or read that file or anything it names.

I did not read `programs/algol-60/README.md` or any `AUDIT-*` file, any earlier classes, or
anything under calibration, reviews, variants or transcripts. I ran no program and no system.

## Summary

**Tokens.** There are 18 texts and 9871 tokens, all covered exactly once. No token is C or S.

| configuration | P | R | H | total |
|---|---|---|---|---|
| report (9 texts) | 1204 | 350 | 3606 | 5160 |
| x1, also standing for x1sim (9 texts) | 1135 | 350 | 3226 | 4711 |
| all | 2339 | 700 | 6832 | 9871 |

R tokens per program, the same in both configurations:

| program | R |
|---|---|
| P09a | 19 |
| P09b | 49 |
| P09c | 0 |
| P09d | 0 |
| P09e | 170 |
| P10a | 11 |
| P10b | 42 |
| P10c | 19 |
| P10d | 40 |

**Outcomes.** There are 76 entries, covering every stage, computation and reading of the
behaviour records, plus both attempts in x1sim P09a:

- 58 are *complete*: P09a B (BA order), P09b A and B, P09c, P09e (residual, reducible,
  suspended), P10a, P10b (stage 1 residual and reduced, then explicit), P10c and P10d.
- 14 are *none reported*. P09a A is *budget* in report and x1, and *timeout* then *error* in
  x1sim. P09d1 and P09d2 are *budget* in report and x1, and *error* ("Wrong result type in TIRD")
  in x1sim.
- 4 are *not reached*: P09a.AB B.
- None is *unsound*.

There are no mode differences and no harness faults. Expressibility, the same in all three
configurations:

- *expressible*: P09a, P09c, P09d1, P10a and P10c, and P09b (its R tokens are avoidable);
- *expressible with reformulation*: P09d2 (needs a demand-driven producer, which the program does
  not write), P09e, P10b and P10d (rule 19 holding code);
- none *not expressible*.

No S mechanism is used. There is no late-definition entry, since P08 is not in this batch.
