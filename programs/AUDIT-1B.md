# Audit of the batch 1B implementation authors

Each implementation author was an agent with its own context, given only
its brief (`transcripts/batch-1A/briefs/` holds batch 1A's; batch 1B's are
rendered from `sandbox/briefs/implementation.md`, published with the
transcripts) and its own clone at `651a55b`. After it ended, every command
it ran and every file it read, from its full transcript, was checked
against the brief. Each commit changes nothing outside
`programs/<system>/`.

## What the isolation was, and what was checked

The authors run as agents under the owner's account on the owner's
machine (`AMENDMENTS.md` 1). Their only container use is the syntax check
and reading the system's documentation; their other commands run on the
host. So **what an author could read was not limited by any mechanism**.
In particular, the agent tooling gives every agent of the session one
shared scratchpad folder, which holds the owner's and earlier roles' work
files (among them batch 1A's agreement files and some qualification
scripts). What is established is what each author **did** read and run,
from its transcript:

| author | commands | anything executed besides `check` | reads outside the brief | scratchpad |
|---|---|---|---|---|
| implementation-absys | 40 | none. `ls` and `tar` in the image to copy `/opt/src/absys` `README.md`, `docs/decisions.md`, `tutorial/`, `examples/` out for reading (disclosed); host `python3` to read `stages.json` keys and to edit its README | none | only its own folder `absysdoc/` |
| implementation-swi-prolog | 37 | none. Host `python3` once, to list `stages.json`'s keys (disclosed); shell, perl and sed to write files | none | one top-level listing of the scratchpad's file names (disclosed; nothing opened); otherwise only its own folder `impl-1B-swi/` |
| implementation-python | 84 tool calls | none. Host `python3 -c` three times to print parts of `stages.json`, once on an empty script (disclosed) | none. Reads under `tool-results` were its own saved outputs of allowed files | only 45 files of its own, each created by it before first use |
| implementation-algol-60 | 56 | none. `ls` and `cat` in the image on the system's documentation (disclosed); host `python3` to edit text | none. The name of `/opt/src/algol-60/compare/` appeared in a listing; nothing in it was listed or read | only its own `chk.sh`, `checkall.sh`, `tox1.py`, `final-check.txt`, each created by it |

Every `container run` in the four transcripts runs `harnesses/<system>/check`
or reads documentation (`ls`, `cat`, `tar`). No author read `calibration/`,
`reviews/`, `variants/`, `results/`, `transcripts/`, the audits, the
private variants or another role's work. No program was run before this
commit.

**Documentation with outcomes.** The Absys reconstruction's README and
tutorial, which its author was allowed to read, show results for cases
close to P04a, P06a/b, P06d, P06e and P07b. That documentation was written
alongside the precursor experiments, so the Absys author's familiarity
with the system's behaviour on these problems is greater than the other
authors'. Disclosed by the author, and recorded here.

## Points the authors disclosed that bear on results

Details in each `programs/<system>/README.md`, section "Batch 1B".

- **Absys.** One text for all three configurations. P05a and P05b
  rebuild > from arithmetic (`pos(q)` recursive), judged *with
  reformulation*; `pos` does not fail for q ≤ 0. P08c holds rev as "case 1
  or `revmore(p, r)`" at stage 3, with `revmore` defined at stage 4,
  judged *with reformulation* and not anticipation, by the author. Named
  variants in `variants/`: `P06d.set.abs`, `P08c.redefine.ab1`.
  **Harness defect:** the Absys harness's PART sections cannot pose
  P07a's orders (P07a is one stage, and part k is given at stage k), so
  the author wrote one file per instance.
- **SWI-Prolog.** P08 outside *session* raises the undefined-procedure
  error, the configuration's own result; *tabling* P08 uses the plain
  text. Named variants `P08{a,b,c}-unknown-fail.pl` in every
  configuration. ≠ is `dif/2`, not `#\=`.
- **Python.** *extended* uses an S mechanism of the author's own for
  negation as failure, with batch 1A's unify and resolution; neither is
  in the phase-4 list (`harnesses/python/S-mechanisms.md`). *core* P08
  takes Python's own `NameError` as primary.
- **ALGOL 60.** P08's definitions are written into the program, and a
  flag marks their arrival at their stage; the author judges this not
  anticipation, and names the readings that would make it so. P04's
  solution-passing procedures could be read as a search mechanism (S).
  Stores are of fixed size. x1 and x1sim texts were made from the report
  texts by a substitution script.

The programs are run as written (owner's decision, 28 November 2026:
"Proceed with Batch 1B as written, without correcting the primary
programs before execution").
