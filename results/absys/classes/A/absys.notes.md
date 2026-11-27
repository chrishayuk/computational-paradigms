# absys, batch 1A (P01-P03): classifier A's notes

Classifier A, a Claude agent (Opus 5.5). Working copy: `/Users/christopherhay/cp-roles/classifier-A` at 628a324, not modified.
Output: `absys.json`, made by `build.py`. Checking scripts, all in this folder:

- `summarise.py`: per-stage facts of a record;
- `compare_configs.py`: compares behaviour records across the three configurations;
- `compare_modes.py`: compares cost and storage runs with behaviour runs;
- `p02_check.py`: the integer solutions of R1 and R2;
- `p03f_check.py`: the derivations printed for P03f.

Nothing of the system was run.

## Tokens

All twelve texts are the same, byte for byte, in all three configurations. Their token files are the same too, and no configuration has an S mechanism (`harnesses/absys/S-mechanisms.md`). So each text is classed once, under `absys/…`, and the classes hold for `absys-depth-first` and `absys-wake-back` unchanged. The script asserts this.

**Result: 606 tokens over 12 texts, all P (P 606, C 0, R 0, S 0, H 0).** Per text: P01a 12, P01b 65, P01c 10, P02a 24, P02b 24, P02c 26, P03a 62, P03b 57, P03c 64, P03d 64, P03e 99, P03f 99.

### Constructs that were hard to class

1. **The constants block** (`zval = 2`, `ca = [1;2]`, …). The tokenizer counts it, although the harness reads it as a table and never gives it to the system.
   - I classed it **P**. Harness README 3.12 says the block is classed by METRICS.md's rules, not as H.
   - Under rule 1, removing a line of the block changes what the stage asserts: the name would then reach the system as a fresh unknown.
   - The block states the stage's constants, which is "the information of each stage".
   - The other reading is that the naming indirection is protocol plumbing, so H, or a definition the problem does not give, so R. I reject both: the protocol requires the block (genericity), and the harness lists no H tokens for it.
   - This is the construct most likely to be disputed. It is 9 to 15% of the tokens of most texts.
2. **`begin … end` around R1 R2 R3 in P02c.** I classed it P, as the conjunction connective of the 1969 notation (the tutorial says `{A, B}` is `begin A B end`). The problem's "R1, R2 and R3 as one stage" is a conjunction.
   - Under rule 1 it could be argued **C**. Without it, the three assertions side by side are still a conjunction with the same solutions. Only the elaboration order and the per-assertion budget change (harness QUESTIONS A1).
   - I kept it P because it is the problem's conjunction written in the notation's form, not an added control. It is 2 tokens.
   - The `begin {…} end` of each lambda body is part of the definition (P, rule 10).
3. **conc case 1, "for every sequence b".** The program's `p = [] q = r` does not test that q is a sequence.
   - I did not count this as an omission under rule 4. The problem gives the range of b, not a conjunct or a guard. The 1969 core as listed has no list-type test to transcribe it with. Prolog-style transcriptions conventionally omit it.
   - Its only possible effect is in P01b (see Outcomes), and it does not change the classification there.
4. **The `or` between cases** is P by rule 6, a disjunction the problem states. Rule 20 would also give it the class of case 2, which is P.

### Rules

- Rule 20 (separators) and rule 10 never changed a class here: every construct is P.
- Rule 19 does not arise. Absys holds undecided relations natively; there is no program code that does the holding.
- The constants-block question (item 1) is not settled by METRICS.md itself. A one-line reading, saying the constants block is P, or is excluded like the markers, would remove the main risk of a dispute across all systems.

## Outcomes

There are 51 behaviour records, 17 per configuration, and I classed every stage of each: 106 outcome entries.

- **P01c** has one entry per reading.
- **absys-depth-first P03f** has an entry for each of its two attempts. Attempt 1 timed out at 60 s; attempt 2 was the 600 s safety rerun.

The behaviour of `absys`, `absys-depth-first` and `absys-wake-back` is identical on every stage of every instance, except P03f (checked by `compare_configs.py`, ignoring derivation numbers). In P03f, depth-first holds 19 derivations at the budget where the other two hold 900, and needed the rerun.

### Totals over all entries

**Semantic:**
- complete: 102
- unsound: 3 (P01c, finite reading, one per configuration)
- none reported: 1 (absys-depth-first P03f, attempt 1, timeout)

**Representation:**
- explicit: 48
- solved form: 21
- residual: 30 (reduced 21, reducible 9)
- cyclic: 6 (3 under each reading)

**Execution state:**
- finished: 63
- suspended: 39
- budget and suspended: 3 (P03f)
- timeout: 1

No conclusion was withdrawn and no manual action was needed anywhere. Every stage was reached: nothing errored, and every stage was posed incrementally in behaviour runs.

### Outcomes that were hard to class

1. **P02, after R1 and R2** (P02a stage 2; P02b R1R2R3 and R2R1R3 stage 2): the two relations are held as posed.
   - The held pair is **equivalent** to the ten triples (`p02_check.py`, by divisors of 16 and by brute force).
   - I classed it *residual / reducible*. The ten explicit triples leave no relation to decide, which is "smaller" by SPECIFICATION's measure, as in its P07b example.
   - Another classifier could call it *reduced* on the view that a ten-way enumeration is not a smaller representation than two relations. **This may be classification-sensitive.**
2. **P02 after R2 and R3** (u = 2, w * 2 = v held): residual / reduced, **not** identical to the posed information. R3 was solved and its value substituted into R2.
3. **Unknowns identified by a suspended equation** (P01a stages 1 and 2, P01b stage 1):
   - I classed these *solved form* ("identified with another unknown"), since no relation remains to be decided.
   - I kept the harness's execution state *suspended*, because Absys holds the identity as a suspended equation that the next stage reactivates. The cost runs show 3 and 2 reactivating events.
4. **P01b stage 1**: `t = [1;2&m₂]`, with s identified with m₂. The program does not restrict s to sequences (Tokens, item 3). Read as the solved form t = ⟨1,2⟩ ++ s, the report denotes only sequences s, so I classed it *complete*.
5. **P01c**: `x = [1&↻]` is *cyclic*: complete under the rational reading, unsound under the finite one, as the problem file directs. The occur check is absent (docs/decisions.md rule 8, as cited in the program and the systems file; I did not read that file).
6. **P03f**:
   - One hibernating derivation has a = [3;2;1], and the others are still elaborating at the budget: 899 in absys and wake-back, 18 in depth-first.
   - `p03f_check.py` shows every still-elaborating derivation already fixes at least 32 elements of a (106 under depth-first). Any solution of rev(a, ⟨1,2,3⟩) has exactly 3, so each denotes no solution: an inconsistency not yet detected.
   - So the report denotes exactly the one valid outcome: **complete** with *budget* (and *suspended*, as the harness records), as the problem file says.
   - Following "two forms" (SPECIFICATION, Representation), I classed the representation on the valid derivation, *explicit*, and recorded the unfinished derivations under observations.
   - The answers(20) list contains 19 such unfinished derivations after the valid one. I do not count them as invalid answers, since they are conditions, not solutions.
7. **Storage susp_relations above 0 at stages the printer shows as finished** (for example P02a stage 3, and P02b R1R3R2 stage 2): this is the association of rule 10 that the harness README describes. I kept *finished*, and noted it in the observations.

### Mode differences

Every cost and storage run agrees with its behaviour run on every stage: execution states, answers verbatim and printed state. The one exception is **P03f** in every configuration, 6 entries.

In P03f, both attempts of the cost and storage runs, at 60 s and at 600 s, were killed by the safety limit with nothing collected. Their steps, store and repeated work are **unavailable** (AMENDMENTS 3.1), and this is a limit of the instrumented measurement, not of the model (PROTOCOL, Modes of running). It is not a disagreement of semantic results, since the instrumented run reported nothing.

## Expressibility

All 12 sub-problems are **expressible** in all three configurations (36 entries). Each is the problem's transcription with no R or C tokens:

- one conc definition serves every direction used (P01b, P03a-d);
- rev with its conjuncts in the problem's order serves both directions (P03e, P03f);
- arithmetic is relational in the core (P02).

P03f's run to the budget after its answer is an outcome, not a reformulation.

## Files read outside the brief's list

- The brief itself, `/Users/christopherhay/cp-roles/briefs/classifier-A-absys.md`, which I was told to read.
- My harness put the user's auto-memory index (`~/.claude/projects/…/memory/MEMORY.md`, two one-line entries about absys source papers and commit trailers) into my context without my asking. I did not open the files it points to.
- Two large outputs of my own commands were saved by the tool to `~/.claude/projects/…/tool-results/` and read back from there. They contain only output from permitted files.

I read nothing in `calibration/`, `reviews/`, `variants/`, `programs/absys/README.md`, `programs/AUDIT-1A.md`, other systems' folders, or the web. I did not read `harnesses/record.schema.json`; the records' fields were clear from `harnesses/README.md` section 9.

## Summary

- **Tokens:** 606, all P (C 0, R 0, S 0, H 0), the same for all three configurations. The likely disputes are the constants block (P here) and P02c's `begin … end` (P here, arguably C).
- **Outcomes:** 106 stage entries over 51 behaviour records.
  - Semantic: 102 complete, 3 unsound (P01c, finite reading only), 1 none reported (a timed-out first attempt).
  - Representation: 48 explicit, 21 solved form, 30 residual (21 reduced, 9 reducible: R1 with R2 held), 6 cyclic.
  - Execution state: 63 finished, 39 suspended, 3 budget with suspended (P03f, complete), 1 timeout.
  - The three configurations behave identically except on P03f.
- **Mode differences:** 6, all P03f: the cost and storage runs timed out with nothing measured. This is a limit of the measurement.
- **Expressibility:** every sub-problem is expressible in every configuration.
