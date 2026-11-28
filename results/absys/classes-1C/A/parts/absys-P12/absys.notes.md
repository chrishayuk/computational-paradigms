# Classifier 1C-A: absys, P12. Notes

Classifier A, batch 1C, problem P12 (sub-problems P12a to P12d, n = 8, 12, 16, all and any).
Output: `absys.json` beside this file. Scripts, all read-only on the clone: `summarize.py` (dumps every
record's stage to `summary.jsonl`), `spans.py` (builds the token spans from the frozen token files and
checks that each token is covered exactly once), `build.py` (outcomes, comparison of modes,
expressibility, S, and the JSON).

## Texts

There are 12 distinct texts (`TEXTS-1C-P12.tsv`). Each is byte-identical in `absys`,
`absys-depth-first` and `absys-wake-back`, which I checked with `cmp`. No S mechanism is present in any
configuration, so no token's class differs between configurations. Each text is classed once, under
`absys/<file>`.

Every text has the same constructs:

| construct | class | rule |
|---|---|---|
| constants block, `accK = [...]`, one per fact of accept | P | rule 6: facts the problem states |
| `gtz'=lambda q begin {q = 1 or ... or q = 16} end` | R | a definition the problem does not give; systems README, Notation |
| `choice'=lambda m, w begin {` | P | rule 10 |
| case 1 `w = []`, then `or` | P | rule 2 (head), rule 6 / 20 |
| case 2 head `w = [e'&t']` | P | rule 2 |
| `gtz(m)` (stands for n > 0) | R | the reformulation's application |
| `{e = 'l' or e = 'r'}` | P | rule 6 |
| `m1' = m - 1` | P | SPECIFICATION, Arithmetic; rule 8 |
| `choice(m1, t)`, then `} end` | P | |
| `accept'=lambda u begin ... end` | P | rule 6 |
| query `begin choice(n, s) accept(s) end` | P | the query, in presentation order |

## Hard to class

1. **gtz: R or C.** Rule 6 says that "an enumeration that the problem does not state is C". gtz is an
   enumeration of 1..16, but it does not generate values. m is always known when gtz is applied, and
   gtz acts as the test n > 0. Removing it changes the solution set: without the test, choice would
   recurse below 0 and never end. So by rule 1 it is not C, and I class it R, as the systems file's
   own example says ("replacing n > 0 by an enumeration of the finitely many values used"). A
   classifier who reads rule 6 literally would put these 71 tokens under C. If so, the R count of every
   P12 text moves by 71 tokens, and the result is classification-sensitive.
2. **The call `gtz(m)` (4 tokens).** I class it R with the definition, because it is the reformulation
   applied in place of the problem's conjunct n > 0. Someone could argue that the call site is the
   problem's conjunct (P) and that only the definition is R.
3. **The constants block.** Its `accK =` tokens are never given to the system. The harness substitutes
   the values into accept. They are in the frozen token file, so I class them. They are accept's
   closed-world facts (P), and accept's body `u = acc1 or u = acc2` is P too. Both are P, so there is
   no double counting of class. There is double counting of the facts' *occurrence*, though.
4. **`begin ... end` around the query.** I class it P, as the connective that conjoins the stage's two
   relations. It also makes them one assertion, which is operational. But removing it would change the
   parse, not only the order, so I left it P.

## Outcomes

There are 72 behaviour runs (3 configurations × 4 sub-problems × 3 sizes × 2 answer modes), each with
one stage, plus 144 cost and storage records. No `.INVALID.json` file, no `raw-rerun-m2/` folder and
no P12 row in `rerun-m2-log.tsv` or `batch-log.tsv` exists. The 1C logs (`logs/1C-absys*-P12.tsv`) show
an earlier attempt marked "no program" (05:02Z) for every instance. That attempt left no records. The
runs of record are the `1C-p12-*` logs (08:28Z onwards). Every run exited 0. No harness faults were
recorded.

- **Complete / explicit / finished: 56 runs.** That is every `absys-depth-first` run (24), and the
  n = 8 and n = 12 runs of `absys` and `absys-wake-back` (16 each). Each derivation binds s to a list
  of atoms, with no relation left. The collected answers equal the valid outcomes, checked by script:
  P12a gives {⟨ʀ⟩, ʟⁿ}, P12b gives {⟨ʀ⟩}, P12c gives {ʀⁿ}, and P12d gives {ʟⁿ}. For P12a "any", cap 1
  takes the first printed derivation, ʟⁿ. That is valid, so the run is complete for an any-one query.
  The printed state still holds both derivations. Absys elaborates every derivation before it reports,
  so steps to the first answer equal steps to the end, and *alternatives pending* never arises
  (QUESTIONS A8).
- **None reported / timeout: 16 runs.** These are `absys` and `absys-wake-back` at n = 16, all four
  sub-problems, both modes. SIGKILL came at the fixed 600 s limit. Nothing was printed and nothing was
  rerun. The 10⁸ budget was not reported exhausted. Steps, store and alternatives are unavailable
  (AMENDMENTS 3.1). This is a timeout, not budget, so P12's "budget means the strategy did not cover
  it" does not apply. `absys-depth-first` covers n = 16 in about 6.3 to 6.6 M steps, in about 16 s.
- **Modes.** Every cost and storage record agrees with its behaviour run on the answers, their order,
  `ended_by` and the execution state, including the n = 16 timeouts. So `mode_differences` is empty.
- **Observations.**
  - Steps per configuration: `absys` and `absys-wake-back` give identical step counts, as does
    `absys-depth-first`. For example, P12a takes 25,560, 409,560 and 6,553,560 steps at n = 8, 12 and
    16, and P12b–d take 24,537 and 393,177 steps (6,291,417 at n = 16, depth-first). They grow by
    about 16× per 4 added to n, which is 2ⁿ. All three configurations searched the whole space. None
    avoided search.
  - Peak derivations (sampled) differ: under the all-live configurations they are 7,530–7,554 at
    n = 8 and 130,170–130,554 at n = 12. Under depth-first they are 108–152.
  - Candidates examined are not counted by the Absys harness, so they are unavailable.
  - Order reported: in P12a, ʟⁿ is printed before ⟨ʀ⟩ in every configuration.
  - Suspended work is 0. No conclusion was withdrawn. No manual action was taken.

## Expressibility

All 12 configuration and sub-problem pairs are *expressible with reformulation*: n > 0 is replaced by
the gtz enumeration. Caveat: gtz is correct only for q ≤ 16. The problem poses only n ∈ {8, 12, 16},
but a hidden variant with n > 16 would make choice give only ⟨⟩. I cannot see the variants, so this
judgement assumes they keep n ≤ 16.

## Late definition and S

- P08 is not in this batch, so `late_definition` is empty.
- No program uses an S mechanism. `S-mechanisms.md` lists none, and the programs supply none: the
  search is the configuration's own, and gtz is problem-specific R. Each program has an entry with
  `mechanism: null` and 0 tokens.

## Rules I think ambiguous

Rule 6 against rule 1 for an enumeration that replaces a missing comparison (item 1 above). The
systems file settles it in favour of R, but METRICS does not say so.

## Files outside the brief's list

- The brief itself, `~/cp-roles/briefs/classifier-1C-A-absys-P12.md`, which I was told to read.
- The session put the user's auto-memory index (`~/.claude/projects/.../memory/MEMORY.md`, two
  one-line entries, [redacted by tools/redact-transcripts.py: what the entries are about]) into my context. I did not open it,
  or the files it links to.
- Two long command outputs were saved by the tool to `~/.claude/projects/.../tool-results/`, and I read
  them there. They were copies of `harnesses/absys/README.md` and of the P12 programs, both on the
  list.
- Directory listings showed the *names* of `results/absys/classes*/`, `results/absys/RERUN-M2.md`,
  `results/absys/*/P*.md`, `calibration/`, `reviews/` and `variants/`. I opened none of them.

## Summary

- **Tokens:** 12 texts, 1,947 tokens: P 1,047, R 900, C 0, S 0, H 0. Each text has R 75 (gtz 71 +
  call 4). P is 68–109 per text, depending on accept's facts.
- **Outcomes (72 behaviour stages):**
  - 56 complete / explicit / finished;
  - 16 none reported / timeout (`absys` and `absys-wake-back` at n = 16);
  - 0 harness faults, 0 not reached, 0 mode differences.
- **Expressibility:** 12 × expressible with reformulation.
- **S mechanisms:** none.
