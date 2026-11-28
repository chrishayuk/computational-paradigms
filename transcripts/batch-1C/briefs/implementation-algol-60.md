# Brief: implementation author for ALGOL 60, batch 1C (P09–P12)

You are the implementation author (`PROTOCOL.md`, "Roles", phase 5) for
ALGOL 60 in batch 1C of wave 1: problems P09, P10, P11 and P12. You are working in
`~/cp-roles/implementation-1C-algol-60`, your own clone of the public repository at commit `1f291be` (`spec-1.0.1`, with the programs of batches 1A and 1B committed). You
have no other context: you have not seen any earlier work on this study.

## What you may read

- `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md`,
  `AMENDMENTS.md`;
- `problems/README.md`, `problems/09-concurrent-goals.md`,
  `problems/10-state-replacement.md`, `problems/11-irreversible-effects.md`,
  `problems/12-large-alternative-space.md`, and, for the definitions these
  refer to (loop, rev and conc, pick), `problems/03-reversible-relations.md`,
  `problems/04-unbounded-alternative.md` and `problems/05-late-contradiction.md`;
- `systems/algol-60/` in full;
- `harnesses/README.md`, `harnesses/stages.json`, and `harnesses/algol-60/`
  in full (its README is the contract your programs are written against);
- your own system's programs from earlier batches, `programs/algol-60/`, and
  its README, which you extend with a section for this batch. They were
  written before any program was run, and hold no outcome;
- inside the image cp-agent-systems:spec-1.0: the system and its own documentation and
  examples (`/opt/src/algol-60` (`README.md`, `docs/`, `examples/`, `historical/`) and `/opt/src/x1sim` (`README.md`, `doc/`, `examples/`)).

## What you may not read

Anything else, in particular: `calibration/` (it holds other authors'
programs and outputs for some of these problems), `reviews/`, `variants/`,
`results/`, `transcripts/`, `programs/AUDIT-*.md`, other systems' folders and harnesses, any other problem file,
`/opt/src/algol-60/compare/` and any test outputs, anything under `~/.claude`, `~/cp-private`,
`~/chris-source`, or `~/cp-roles` outside `~/cp-roles/implementation-1C-algol-60`, and the web. If you come
across any of these by accident, stop reading and say so in your report.

## What you may run

Only the harness's syntax check, which executes nothing:

    container run --rm --platform linux/amd64 --volume ~/cp-roles/implementation-1C-algol-60:/work --workdir /work cp-agent-systems:spec-1.0 harnesses/algol-60/check CONFIGURATION PROGRAM

**Nothing else that executes a program**: not `harnesses/algol-60/run`, not
the system or an interpreter on a program or a fragment of one, on the host
or in the image (`PROTOCOL.md`, phase 5: programs are fixed before any is
run; `sandbox/README.md`, "Syntax checking"). You may read files, write
files, and use git. Every command you run is recorded and published; any
execution other than `check` is reported as a breach of protocol.

## What to write

For every configuration of ALGOL 60 in `systems/algol-60/README.md`
(`report`, `x1`, `x1sim`), and every sub-problem of P09, P10, P11 and P12 in `stages.json`:

1. **The primary program**, under `programs/algol-60/<configuration>/`,
   named and laid out as `harnesses/algol-60/README.md` requires, written
   from the problem file by the rules of `PROTOCOL.md`, "Writing a
   program": transcribe the definitions given (anything else is
   reformulation, R); idioms of the system's period where known, each cited
   (a manual, a paper or a published program: the system's own
   documentation counts); no anticipation; every stage constant in the
   harness's constants block, tagged by stage, so the verifier can
   substitute hidden variants; genericity: correct for other constants in
   the problem's domain, never encoding a conclusion. Configurations may
   share one program text where the same text is the natural program in
   each; say so.
2. **Where a configuration cannot express a sub-problem** (`SPECIFICATION.md`,
   "Outcomes", expressibility): say so, with the reason, and write a
   program only as a **named variant**, never as the primary. Where several
   idiomatic programs are possible, choose one as primary before any is run
   (`PROTOCOL.md`, rule 4).
3. **`programs/algol-60/README.md`**: for each configuration and sub-problem:
   the program (or "not expressible" and why), whether it is primary or a
   named variant, its expressibility as you see it, the idioms used and
   their sources, any S mechanism used, that you had not seen any precursor
   program (or which, if you had), and the author (`implementation-algol-60`,
   an agent, with the model). Also anything in the problem files or the
   contract you found ambiguous, and the reading you took.

Run `check` on every program until it reports no errors. Then commit in
`~/cp-roles/implementation-1C-algol-60` on a branch `implementation-algol-60` (author
`implementation-algol-60 <implementation-algol-60@sandbox>`, no trailers), do
not push, and end with a short summary: the programs, per configuration and
sub-problem; which configurations share a text; what you judged not
expressible; and every ambiguity.
