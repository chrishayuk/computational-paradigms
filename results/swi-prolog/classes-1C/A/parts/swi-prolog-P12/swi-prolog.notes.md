# swi-prolog, batch 1C, P12: classifier A's notes

Scripts in this folder: `summarise.py` (it extracts every P12 record into `rows.json`), `tokens_classes.py`
(the token spans and a check that every token is covered exactly once), and `build.py` (it checks each
answer against the problem's valid outcomes and writes `swi-prolog.json`). They read only
the records and the token files. I ran no program and no part of the system.

## Texts

There are 8 distinct texts. The plain, coroutines, constraints and session files are byte-identical
to constraints/P12x.pl (checked with `cmp`). I classed them once. No token's class differs between
these four configurations. Session loads the S hook `S/session-wait.pl`, but these programs never call an
undefined procedure, so the hook never acts on them. member/2 is an external mechanism in
plain, but under rule 12 its class is still that of its call tokens. Tabling differs only by `:- table choice/2.`

## Hard constructs

1. **The key argument n in `accept_fact(n, s)`.** This was the hardest call. accept(s) is unary in the
   problem, but its facts depend on n ("'12' below read as n"). One file serves n = 8, 12 and 16, so
   the facts are keyed by n, and `member(accept_fact(N, S), Cs)` selects them.
   I classed the key P, under rule 1: without the key, l^8 would be accepted at n = 12, so the key
   changes the solutions. The problem's own statement makes accept a family of fact sets indexed by n.
   The other reading is R: "an extra argument the problem file does not give". On that reading
   each text has 1 key per fact plus 1 in the stage body. That is 7 R tokens in P12a and 4 in each of
   P12b, P12c and P12d. Rule 20 would leave the comma that follows each key P. I flag this span as a
   likely disagreement.
2. **The full stop of the stage/3 clause.** I gave it H, with the H-headed clause (harness README 12, rule 10).
   It could be read as P, closing the last goal. That is 1 token per text.
3. **accept by `member/2` over the stage's constants.** I classed this P under rule 9. It is equivalent
   in the direction used, because S is ground when accept is evaluated. It is listed as a built-in
   (library(lists)), and in plain it is an external mechanism.
4. **`:- table choice/2.`** I classed this C. Under SLG the tables are complete before the first answer is
   returned, and the answers come back in depth-first order. Only cost and store change, so the
   solution set is the same (rule 1). Steps to the first answer grow sharply: at n = 16, P12d
   takes 103 steps in plain and 262,522 in tabling.

## Outcomes

- There are 120 behaviour runs: 5 configurations, 4 sub-problems, n = 8, 12 and 16, and the all
  and any-one modes. Each has one stage, and every stage was reached. There are no `*.INVALID.json`
  records, no `raw-rerun-m2/` folders, and no `rerun-m2-log.tsv`. `batch-log.tsv` has no P12 rows.
  The 1C logs have 72 rows per configuration, all `exit 0`. Every record's program sha256 matches
  the file in the clone.
- All 120 runs are **complete / explicit**. The "all" runs gave exactly the valid outcomes, with
  no invalid answer: P12a {<r>, l^n}, P12b {<r>}, P12c {r^n}, P12d {l^n}. The any-one runs each gave one
  valid answer.
- Execution state:
  - Every "all" run is *finished*. The search covered the whole space: 2^(n+1)−1 candidates were
    examined, which is 511, 8,191 and 131,071.
  - Every any-one run is *alternatives pending*, with one exception. Tabling P12c.n16.any is *finished*:
    its only answer was deterministic and rendered with ".", because the n = 16 fact is the last
    element of the constants list and the answer came from a completed table.
  - In P12b, P12c and P12d the pending choicepoints would yield nothing more if resumed. In P12a
    they would yield one more answer. The state follows SPECIFICATION 3's definition, not whether
    more valid answers exist.
- Candidates examined to the any-one answer agree with the problem's depth-first positions:
  - <r> is at 2^n + 1: 257, 4,097 and 65,537.
  - l^n is at n + 1: 9, 13 and 17.
  - r^n is at 2^(n+1)−1.

  Tabling examines candidates in the same order. Nothing is breadth-first, and no configuration
  avoids the search. The coroutines and constraints programs are the plain text, so neither holds
  choice until accept constrains s.
- Problem-defined partial sequences held: none recorded, because no program calls `h_held/2`. I
  report this as unavailable, not 0.

## Mode comparison

The cost runs match behaviour exactly. The storage runs have the same answers, states and candidates
in every configuration, so no stage's classification differs and `mode_differences` is empty.

There is a measurement finding, outside the classification. In plain, coroutines, constraints and
session, the storage runs' `steps_at` and `to_end` differ from behaviour and cost:
- They are usually higher, by up to about 5%. For example, plain P12a.n16.all ends at 1,311,220
  against 1,245,178.
- Sometimes they are lower. For example, plain P12b.n12 reaches its answer at 26,391 against 26,630,
  and session P12b.n8 at 1,434 against 1,669.

The harness README (section 6) says that storage steps equal behaviour steps. These figures show
that the heartbeat sampler's exclusion is not exact. Tabling has no sampler, and its storage steps
match. The cost runs are the figures of record, so they are unaffected.

Two storage readings are missing, and I report them as unavailable, not 0:
- Session's "all" storage runs have no boundary `global_live_bytes` (null).
- Several short any-one storage runs have no sampled maximum (no sample was taken).

## Rules

The rules are not wrong here, but one point is ambiguous. METRICS has no rule for an argument that
indexes a stage's constants by an instance parameter. The problem defines the constants per
instance, and the harness puts every instance's constants in one block. This decides item 1 above.

## Files outside the brief's list

- `harnesses/swi-prolog/S-mechanisms.md` and `README.md` were too long for one output. The tool saved
  that output to a file under `~/.claude/projects/.../tool-results/`, and I read that file with
  `cat`. Its content is only those two permitted harness files.
- The session's preloaded memory index (`~/.claude/.../memory/MEMORY.md`) was put into my context
  by the environment. I did not open it.
- I read nothing else outside the list. I did not open `calibration/`, `reviews/`, `variants/`,
  `transcripts/`, any classes, any result `.md`, or the author's notes. I did not open
  `systems/swi-prolog/probes/` either, although the brief allows it; I only listed it.

## Totals

Per text, as tokens by class:

| text | tokens | P | C | H |
|---|---|---|---|---|
| P12a (plain, coroutines, constraints, session) | 221 | 185 | 0 | 36 |
| P12b | 128 | 92 | 0 | 36 |
| P12c | 194 | 158 | 0 | 36 |
| P12d | 194 | 158 | 0 | 36 |
| tabling P12a | 227 | 185 | 6 | 36 |
| tabling P12b | 134 | 92 | 6 | 36 |
| tabling P12c | 200 | 158 | 6 | 36 |
| tabling P12d | 200 | 158 | 6 | 36 |

- **Per configuration:** plain, coroutines, constraints and session each have 737 tokens: P 593,
  C 0, R 0, S 0, H 144. Tabling has 761: P 593, C 24, R 0, S 0, H 144.
- **Over the 8 distinct texts:** 1,498 tokens, of which P 1,186, C 24 and H 288.
- **Outcomes:** 120 behaviour stages, all complete / explicit.
  - The 60 "all" runs are finished.
  - Of the 60 any-one runs, 59 are alternatives pending and 1 is finished (tabling P12c.n16.any).
  - There are no harness faults and no stages not reached. No classification differs between modes.
- **Expressibility:** expressible for every configuration and sub-problem.
- **S:** no program supplies S. Session's listed mechanism is loaded but not invoked.
- **Late definition:** no P08 in this batch.
