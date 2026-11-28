# Audit of the batch 1C implementation authors

Each implementation author was an agent with its own context, given only
its brief (rendered from `sandbox/briefs/implementation.md`, published
with the transcripts) and its own clone at `1f291be`. Beside the problem
files of P09–P12, the briefs list those of P03, P04 and P05, which define
the loop, rev, conc and pick that P09–P11 use. After each author ended,
every command it ran and every file it read, from its full transcript,
was checked against the brief. Each commit adds files under
`programs/<system>/` and extends that system's README; no earlier
program was changed.

## What the isolation was, and what was checked

As in batch 1B (`programs/AUDIT-1B.md`), what an author could read was
not limited by any mechanism: the authors run on the host under the
owner's account, and the agent tooling gives every agent of the session
one shared scratchpad folder. What is established is what each author
**did** read and run, from its transcript.

| author | tool calls | anything executed besides `check` | reads outside the brief | scratchpad |
|---|---|---|---|---|
| implementation-absys | 43 | none. `cat`, `ls` and `grep` in the image on the system's documentation and examples (disclosed). Probe files written, checked with `check` and deleted (disclosed). One command to copy the documentation out with `tar` was refused by the permission system and did not run (disclosed) | none | none used (the refused command would have made `absysdoc/`) |
| implementation-swi-prolog | 62 | none. Host `python3` to print parts of `stages.json` and to write text (disclosed) | none. It read three of its own long outputs, of allowed files, where the tool saved them under `~/.claude/.../tool-results/`; not disclosed | only its own folder `impl1c/` |
| implementation-python | 75 | none. Host `python3 -c` once, to print part of `stages.json` (disclosed) | none. One read under `tool-results` was its own saved output of allowed files (disclosed) | none used |
| implementation-algol-60 | 64 | none. `ls`, `cat` and `grep` in the image on the system's documentation (disclosed); host `python3` to edit text and to convert report texts to X1 texts (disclosed) | none. One read under `tool-results` was its own saved output; not disclosed. The name of `/opt/src/algol-60/compare/` and `.out` file names appeared in listings; nothing in them was read | only its own `tox1.py`, `check1.txt` and converter test outputs, each created by it |

Every `container run` in the four transcripts runs `harnesses/<system>/check`
or reads documentation (`ls`, `cat`, `grep`). No author read
`calibration/`, `reviews/`, `variants/`, `results/`, `transcripts/`, the
audits, the private variants, the scratchpad's other files or another
role's work. No program was run before this commit.

## Points the authors disclosed that bear on results

Details in each `programs/<system>/README.md`, section "Batch 1C".

- **Absys.** One text for all three configurations. **P11a and P11b are
  judged not expressible**: emit (`tout`) exists only in the 1990
  notation, and x ≥ k can be rebuilt only from arithmetic, which only the
  1969 notation has. Named variants `variants/P11a.ne.abs` and
  `P11b.ne.abs` write x ≥ k as `not(x = k)`, right only for pick's facts
  as given (not generic, by the author). Named variants
  `variants/P09a.{AB,BA}.or.ab1` and `P09b.or.ab1` pose the computations
  as alternatives of one `or`. P10's quantities are lists of their values
  (reformulation); P10d withdraws by stating `pick` again on a fresh
  unknown. P12 enumerates n > 0 as 1..16 (`gtz`), one file per
  sub-problem and n. `pos` does not fail for q ≤ 0, as in batch 1B.
- **SWI-Prolog.** 85 primaries, no variants, nothing judged not
  expressible. P10 replaces values by `retractall`/`assertz`; P10d holds
  the withdrawable comparison in the database (reformulation). P11's
  commit reads the harness's verbatim answer with `term_string/3`; it
  cannot prune stage 1's alternatives, so on replay P11d may emit again.
- **Python.** 51 primaries, no variants, nothing judged not expressible.
  *extended* uses the listed S mechanisms (search, suspension queue,
  propagator with a trail for P10d's withdrawal). *stdlib-concurrency*
  P09c–d poses each relation application as a thread.
- **ALGOL 60.** 76 programs, no variants, nothing judged not expressible.
  x1 and x1sim share one text, made from the report text by a substitution
  script the author checked against batch 1B's X1 texts. P11's commit adds
  x = v with no cut, so the author expects P11d to emit ⟨1, 2, 3⟩ (extra).
  P10d keeps pick's facts and recomputes x at each stage; the author
  names the reading that would make this anticipation. P12's `choice` is
  read as R, not as a hand-written search (S); the author names the
  broader reading. Stores are of fixed size.
