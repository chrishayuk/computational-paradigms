# Audit of the batch 1D implementation authors

Each implementation author was an agent with its own context, given only
its brief (rendered from `sandbox/briefs/implementation.md`, published
with the transcripts) and its own clone at `1cf7c13`. Beside the problem
files of P13–P16, the briefs list those of P07, P09 and P10, which P15
(the stream reading of P09d2, named quantities as in P10) and P16 (P07f)
refer to. After each author ended, every command it ran and every file it
read, from its full transcript, was checked against the brief. Each
commit adds files under `programs/<system>/` and extends that system's
README (its title now names batch 1D); no earlier program was changed.

**A gap in the briefs.** P13 says rev is "as in P03", and P03's problem
file was not in the briefs. Every author who needed rev took it from its
own system's batch 1A program (allowed: `programs/<system>/`), and said
so.

## What the isolation was, and what was checked

As in batches 1B and 1C (`programs/AUDIT-1B.md`, `programs/AUDIT-1C.md`),
what an author could read was not limited by any mechanism: the authors
run on the host under the owner's account, and the agent tooling gives
every agent of the session one shared scratchpad folder. What is
established is what each author **did** read and run, from its
transcript.

| author | tool calls | anything executed besides `check` | reads outside the brief | scratchpad |
|---|---|---|---|---|
| implementation-absys | 69 | host `python3 -c` three times, each printing part of `harnesses/stages.json`, and one `python3 -` with no input (disclosed). `bash` and `awk` to write program text (disclosed). Two `container run` commands to read the system's documentation (`tar`, `ls`) were refused by the permission system and did not run (disclosed) | none. One read under `tool-results` was its own saved output of allowed files (disclosed); one was its own background `check` loop's output | its own `absysdoc/` (empty: the copy was refused), `gen/`, `check-all*.txt` |
| implementation-swi-prolog | 65 | none. `bash` and `perl` scripts to write program text (disclosed) | none | its own `impl1d/` |
| implementation-python | 112 | host `python3 -c` once, printing the type of `stages.json`, reported by the author as a breach (disclosed). `sed`, `awk`, `perl` to write text | none. One read under `tool-results` was its own saved output of allowed files (disclosed). A listing of the scratchpad showed other files' names, and a folder it made, `impl1D/`, was on this case-insensitive file system the SWI-Prolog author's `impl1d/`: its listing showed that author's file names. It opened none of them, moved its own two files to `mine-py1D-x7/`, and disclosed it | `mine-py1D-x7/` |
| implementation-algol-60 | 100 | host `python3 -c` once, printing the top-level keys of `stages.json` (disclosed). `sed` scripts to convert report texts to X1 texts (disclosed) | none. Three reads under `tool-results` were its own saved outputs; not disclosed | its own `chk.sh` (runs only `check`; it replaced an older file of that name, a temporary script of the coordinator's), `conv.sh` and `*.sed` |

Every `container run` in the four transcripts runs `harnesses/<system>/check`,
except the two refused Absys commands. No author read `calibration/`,
`reviews/`, `variants/`, `results/`, `transcripts/`, the audits, the
private variants, a problem file outside its list, another system's
folders or another role's work. (The Absys author's named variants of
P13 cite "calibration's range": that is from `systems/absys/README.md`,
Notation, which it may read.) No program was run before this commit.

## Points the authors disclosed that bear on results

Details in each `programs/<system>/README.md`, section "Batch 1D".

- **Absys.** One text for all three configurations. Nothing judged not
  expressible. P13a–d rebuild m > n and m ≤ n from arithmetic (batch 1C's
  `gt`, `le`), with reformulation; named variants
  `variants/P13a–d.eq.ab1` write m > n as m = n + 1 and drop m ≤ n (the
  meaning changes). P13e–f: the builder carries on below 0 in a
  derivation that never ends, so the author expects *budget*. P16: every
  relation written out, one file per instance (21 files); P16b's
  contributors in SPAWN sections, conjoined in one session. The image's
  documentation was not read (the commands were refused); idioms are
  cited as in batches 1A–1C.
- **SWI-Prolog.** 107 files, 20 primaries per configuration; named
  variants `P15c-once.pl` (committed choice by `once/1`) in all five, and
  `P14a-engine.pl`, `P14c-engine.pl` in *session*. Nothing judged not
  expressible. P14's count is held in the database (the author reads the
  problem's "either is a transcription" as covering it). No fair merge
  was written. P16 in *plain* and *tabling* errs when both places of a
  relation are unknown.
- **Python.** 60 primaries, no variants, nothing judged not expressible.
  *core* P13a–d are recursive and are expected to end in `RecursionError`;
  *extended* solves them by search, with a new resolution text (a linked
  goal list, to avoid copying the goal list at each step). *core* P15b
  uses delayed streams (reformulation), unlike batch 1C's *core* P09d,
  which kept tuples. P16 in *core* and *stdlib-concurrency* indexes each
  held relation under the unknowns it waits for, instead of batch 1A's
  loop that re-examines every relation.
- **ALGOL 60.** 60 program–configuration pairs, all primary, nothing
  judged not expressible. x1 and x1sim share one text, made from the
  report text by a fixed substitution. P13c declares its store in advance
  (about n(n+1)/2 cells) and may fail to allocate at n = 10⁴; P13 recursion
  is n deep. P16 keeps, for each unknown, the relations it occurs in, and
  a queue of unknowns newly given values, instead of the passes of
  batches 1A–1C (chosen before any run, because the passes would be
  quadratic); the author names the reading under which this is S. Stores
  are of fixed size.
