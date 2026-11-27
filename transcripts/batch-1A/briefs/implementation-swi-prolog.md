# Brief: implementation author for SWI-Prolog, batch 1A (P01–P03)

You are the implementation author (`PROTOCOL.md`, "Roles", phase 5) for
SWI-Prolog in batch 1A of wave 1: problems P01, P02 and P03. You are working in
`~/cp-roles/implementation-swi-prolog`, your own clone of the public repository at tag `spec-1.0.1`. You
have no other context: you have not seen any earlier work on this study.

## What you may read

- `README.md`, `SPECIFICATION.md`, `METRICS.md`, `PROTOCOL.md`,
  `AMENDMENTS.md`;
- `problems/README.md`, `problems/01-unknown-equality.md`,
  `problems/02-late-information.md`, `problems/03-reversible-relations.md`;
- `systems/swi-prolog/` in full;
- `harnesses/README.md`, `harnesses/stages.json`, and `harnesses/swi-prolog/`
  in full (its README is the contract your programs are written against);
- inside the image cp-agent-swi-prolog:spec-1.0: the system and its own documentation and
  examples (SWI-Prolog's installed library sources and documentation).

## What you may not read

Anything else, in particular: `calibration/` (it holds other authors'
programs and outputs for some of these problems), `reviews/`, `variants/`,
`results/`, other systems' folders and harnesses, any other problem file,
 anything under `~/.claude`, `~/cp-private`,
`~/chris-source`, or `~/cp-roles` outside `~/cp-roles/implementation-swi-prolog`, and the web. If you come
across any of these by accident, stop reading and say so in your report.

## What you may run

Only the harness's syntax check, which executes nothing:

    container run --rm --platform linux/amd64 --volume ~/cp-roles/implementation-swi-prolog:/work --workdir /work cp-agent-swi-prolog:spec-1.0 harnesses/swi-prolog/check CONFIGURATION PROGRAM

**Nothing else that executes a program**: not `harnesses/swi-prolog/run`, not
the system or an interpreter on a program or a fragment of one, on the host
or in the image (`PROTOCOL.md`, phase 5: programs are fixed before any is
run; `sandbox/README.md`, "Syntax checking"). You may read files, write
files, and use git. Every command you run is recorded and published; any
execution other than `check` is reported as a breach of protocol.

## What to write

For every configuration of SWI-Prolog in `systems/swi-prolog/README.md`
(`plain`, `tabling`, `coroutines`, `constraints`, `session`), and every sub-problem of P01, P02 and P03 in `stages.json`:

1. **The primary program**, under `programs/swi-prolog/<configuration>/`,
   named and laid out as `harnesses/swi-prolog/README.md` requires, written
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
3. **`programs/swi-prolog/README.md`**: for each configuration and sub-problem:
   the program (or "not expressible" and why), whether it is primary or a
   named variant, its expressibility as you see it, the idioms used and
   their sources, any S mechanism used, that you had not seen any precursor
   program (or which, if you had), and the author (`implementation-swi-prolog`,
   an agent, with the model). Also anything in the problem files or the
   contract you found ambiguous, and the reading you took.

Run `check` on every program until it reports no errors. Then commit in
`~/cp-roles/implementation-swi-prolog` on a branch `implementation-swi-prolog` (author
`implementation-swi-prolog <implementation-swi-prolog@sandbox>`, no trailers), do
not push, and end with a short summary: the programs, per configuration and
sub-problem; which configurations share a text; what you judged not
expressible; and every ambiguity.
