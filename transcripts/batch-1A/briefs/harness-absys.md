# Brief: harness author for Absys

You are the harness author (`PROTOCOL.md`, "Roles", phase 4) for Absys in
wave 1. You are working in `~/cp-roles/harness-absys`, your own clone of the public repository at
commit `f3fcecd` (branch `harness-common`): the frozen specification (`spec-1.0`) plus the common
harness contract in `harnesses/`. You have no other context: you have not
seen any earlier work on this study, and you must not look for it outside
`~/cp-roles/harness-absys` and the system sources named below.

Read first: `harnesses/README.md`, `harnesses/stages.json`,
`harnesses/record.schema.json`, `harnesses/QUESTIONS.md` if present,
`PROTOCOL.md` ("The harness interface", "Running", "Modes of running"),
`SPECIFICATION.md` ("Outcomes", "Observations common to every problem"),
`METRICS.md` (the H class; "Steps and store"; "Restart cost and repeated
work"), and `systems/absys/` in full, including its probes.

## Where the system runs

The harness runs inside the system's pinned Linux x86_64 image, never on
the host. Run anything you need to run as

    container run --rm --platform linux/amd64 --volume ~/cp-roles/harness-absys:/work --workdir /work cp-agent-systems:spec-1.0 COMMAND...

(Apple's `container`; the first start of a container takes a few seconds).
The image runs as an unprivileged user `agent`. `harnesses/absys/run`
and `check` are invoked inside it, as `harnesses/absys/run ...` from
`/work`. Write the harness in whatever the image provides; say what in the
README. Do not install anything into the image at run time. Read nothing
on the host outside `~/cp-roles/harness-absys`; do not read anything under `~/.claude`,
`~/cp-private`, `~/chris-source`, `~/cp-roles` other than `~/cp-roles/harness-absys`, or any
file named `*.key` or `*.age`. Do not push.

## The system

The image holds the pinned builds: `absys` (main `efd5203`) and `absys-measure` (branch measure `5450449`) in `/usr/local/bin`, with their sources at `/opt/src/absys` and `/opt/src/absys-measure` (read them freely: `README.md`, `docs/`, `src/`, `examples/`), and `python3` (3.11) for the harness driver. Absys has three configurations: `absys`, `absys-depth-first` (`--search depth-first`) and `absys-wake-back` (`--wake back`). Absys has no parse-only mode on its command line; see whether `absys lsp` (a language server) can give diagnostics without running the text, for `check`.

## The first principle

**The harness observes what the system computes; it never supplies it.**
It must not implement, on the system's behalf, suspension, waiting for
information, search or backtracking, scheduling, constraint propagation,
reconstruction or simplification of answers, or the combination of
stages. Where a configuration lacks a mechanism, the harness does not
make up for it: the program must, as S code counted against that
configuration, or the problem is not expressible there. Anything the
harness does beyond passing stages in, collecting answers through the
system's standard mechanism, and reading state for `observe()`, must be
listed in its README as a possible confound.

## What to write, all under `harnesses/absys/`

1. **The harness**, `harnesses/absys/run`, with the command line the
   common contract gives, for every configuration of Absys in
   `systems/absys/README.md`, and all three modes where the systems
   file allows them. It implements pose, spawn, answers, observe and print
   exactly as `PROTOCOL.md` defines them, for every problem P01–P16 (the
   whole interface, including spawn for P09 and the effects log for P11,
   since it is published before any program is run and is not changed
   afterwards), and writes raw records that pass `harnesses/validate.py`.
   It enforces the budget in the systems file's unit and the safety limit,
   and it reads steps and store only by the measurements the systems file
   qualifies. It must not order, choose or re-pose goals on its own.
2. **`harnesses/absys/README.md`**: the contract a program for Absys
   must meet, per configuration, so precisely that an author who will not
   be allowed to run the program before its results are taken can write it
   correctly: file layout, how the program learns which stage to handle,
   how it receives a stage into the same computation (where the
   configuration allows it), how it reports answers so the harness
   collects them through the system's standard mechanism, what `observe()`
   reads and how, the marked constants block or input format the verifier
   substitutes hidden constants into, and which constructs of the program
   are H tokens. Give a complete minimal example program for a made-up
   problem that is not one of P01–P16.
3. **`harnesses/absys/S-mechanisms.md`** (`PROTOCOL.md`, "Recording a
   result": every configuration's S mechanisms are listed, with their size,
   before any program is run): for each configuration whose systems file
   admits supporting code, the S mechanisms the configuration provides, or
   "none", as the systems file defines them. List; do not write problem
   programs.
4. **Qualification**, `harnesses/absys/qualification/`: evidence that
   the harness does what its README says and does not change what the
   system computes. At least: (a) for programs that are not problem
   programs (the made-up example, the systems file's probes, small tests
   you write), the system's own output run directly and the answers the
   harness collects agree, and steps and store agree with the systems
   file's qualified measurement; (b) incremental and reposed posing give
   the same answers where both are possible; (c) budget, safety limit and
   error paths each produce a valid record; (d) every record you produce
   passes `validate.py`. Write a script that reruns all of it, and its
   output.

You may not write, sketch or run a program for any problem P01–P16, or
use any problem's constants in a test. Use made-up problems.

Do not modify any file outside `harnesses/absys/`. If the common
contract or the specification cannot be implemented as written for
Absys, do not change them: write it in
`harnesses/absys/QUESTIONS.md` with the reading you implemented.

5. **`harnesses/absys/check`** `CONFIGURATION PROGRAM`: a syntax
   check that never executes the program. It may parse or compile it, and
   report syntax and static errors verbatim, but must not run any of its
   statements, goals, directives or assertions, pose any stage, or print
   anything the program would compute. Say in the README exactly what it
   does for each configuration, and show in the qualification that it
   executes nothing (a program whose only effect would be to write a file
   or print a marker, checked, leaves no trace). Where the system offers
   no way to check without executing, say so and make `check` report that.
   Program authors may use `check`, and nothing else, before their
   programs are fixed.

When you are done, commit in `~/cp-roles/harness-absys` on a branch `harness-absys`
(author `harness-absys <harness-absys@sandbox>`, no trailers), and
end with a short summary: what you wrote, what the qualification showed,
and every entry in your `QUESTIONS.md`.
