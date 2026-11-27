# Amendments

Numbered, dated changes to the frozen files (`PROTOCOL.md`, "Amendments").
`spec-1.0` is the specification as frozen; `spec-1.0.1` is it with the
amendments below. No result existed before any of them, so none is rerun.
`FREEZE-MANIFEST.md` is the manifest of `spec-1.0` and is left as it was.

## 1. The hidden variants of wave 1 (27 November 2026)

**Changes** `PROTOCOL.md`, "Roles", the paragraph on hidden variants, for
wave 1.

**What happened.** The first wave-1 set (120 variants) was sealed before
the freeze, encrypted with age to the owner's key, as the protocol
requires. After the freeze, and before any program of the study was
written, the owner protected that key with a passphrase, which was then
lost. The archive cannot be opened by anyone. It stays in the repository,
unchanged, at `variants/wave-1/`.

**What replaces it.** A new set, `variants/wave-1b` (121 variants), made on
27 November 2026 by a new custodian agent with its own context. It had not
seen the first set, and no primary program or result existed: the
harnesses were being written, and no implementation author had started.
It is made after the freeze, which the protocol does not allow, and the
chronology is recorded here so that it can be checked against the
repository's history.

**How it is kept.** Not encrypted. The plaintext is kept by the owner
outside the repository, as one tar file with a 128-bit nonce, and only its
SHA-256 is committed (`variants/wave-1b/SHA256`), before any primary
program is written. It is revealed, and anyone can check it against the
hash, only after every primary program and result of wave 1 is committed.

**What this weakens.** The protocol asks that variants be made
inaccessible, not merely placed where an implementation author is told
not to look. Under this amendment they are, for wave 1, placed where the
authors are told not to look. The authors run as agents under the owner's
account, on the owner's machine, and could have read them. The hash
proves the variants were not changed after it was committed; it does not
prove the authors could not see them. That is shown, instead, by each
author's transcript, every command it ran and every file it read, which is
published with its results. Any read of the private variants would void
that author's variant results and be reported.

**Reason.** The encryption step, after the key was lost, was judged by the
owner to cost more than it protected, for agents that have no reason to
look and whose every action is recorded. Later waves follow the protocol as
written.

## 2. SWI-Prolog's step measurement (27 November 2026)

**Changes** `systems/swi-prolog/measurement.md`, the table of
measurements, row "inference limit".

The file says that `call_with_inference_limit/3` "agrees with the
`statistics/2` difference minus 1". The SWI-Prolog harness author found
that it does not, in three cases, on made-up programs:

| case | `statistics/2` difference − 1 | smallest limit that completes |
|---|---|---|
| a clpfd stage (coroutine wake-ups) | 111 | 100 |
| a tabled stage | 63 | 4 |
| plain code calling `memberchk/2` | differs by a few inferences | |

(`harnesses/swi-prolog/QUESTIONS.md`, S16.) So:

- **The measurement of record** for SWI-Prolog steps is the `statistics/2`
  inference difference, minus 1, in every configuration.
  `call_with_inference_limit/3` figures are information only.
- **The budget** is enforced with the internal predicates
  `call_with_inference_limit/3` is built from, with a slack of 8
  inferences between the program's entries into harness code and an exact
  check at each entry (S1). A stage may therefore run up to 8 inferences
  past its budget before it is stopped. The overrun is recorded.
- **Storage sampling is unavailable in *tabling*:** the sampler's own
  inferences could not be excluded exactly there (S17). Storage in
  *tabling* is read at stage boundaries only.

## 3. Readings that apply to every harness (27 November 2026)

**Changes** `PROTOCOL.md`, "Running" and "Recording a result", as
readings.

1. **Missing measurements are unavailable, not zero.** Where a harness
   cannot read a figure, the result reports it as unavailable. A 0 that a
   harness records together with a `harness_faults` entry is read as
   unavailable.
2. **Failed and never reached are different results.** A stage that is
   posed and executes and fails, or errors, is reported as such. A stage
   that is never reached, because the run stopped at an earlier stage or
   in the program's set-up, is reported as *not reached*, with what
   stopped the run, never as its own failure.
3. **No anticipation, and its limits.** Every harness delivers a stage's
   constants only when that stage is posed, and each qualification shows
   that a later constant is not in the system's state before its stage.
   Where a stage k is posed by reposing, its constants are in the process
   from the start of that run, while stages 1 to k−1 are replayed
   (SWI-Prolog S18, and in effect every reposed run). The replayed stages'
   code receives only its own constants. A primary program that reads
   another stage's constants by any other route (global state, the
   database, introspection, its own source file) breaks rule 5 of "Writing
   a program", and is reported as such. Each harness's `check` rejects
   the routes it can detect statically.
4. **Supporting mechanisms are credited for what they do.** Python
   *extended*'s three mechanisms (search, suspension queue, propagator)
   are identified and counted separately, each with its own tokens. The
   finite-domain propagator decides relations over the finite domains a
   program gives it. A program that imposes a finite domain the problem
   does not state is judged against the problem's own domain
   (`systems/swi-prolog/README.md` says the same of clpq): if the problem
   ranges over all integers, a result found only within an imposed domain
   is *partial* or *unsound*, not *complete*.
