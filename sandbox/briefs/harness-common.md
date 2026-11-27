# Brief: harness author, common part

You are the harness author (`PROTOCOL.md`, "Roles", phase 4) for the part
of the harness that all four systems of wave 1 share. You are working in
CLONE, your own clone of the public repository at tag `spec-1.0`, the frozen
specification. You have no other context: you have not seen any earlier
work on this study, and you must not look for it outside CLONE.

Read first: `README.md`, `SPECIFICATION.md`, `PROTOCOL.md` (especially
"The harness interface", "Running", "Modes of running", "Recording a
result"), `METRICS.md` (the H class, and the metrics a stage records), the
four `systems/*/README.md`, and every file in `problems/`.

Do not modify any file that existed at `spec-1.0`. The specification is
frozen. If you find something in it that a harness cannot implement as
written, or that is ambiguous, do not resolve it by changing it: write it
down in `harnesses/QUESTIONS.md`, say which reading you implemented and
why, and carry on.

## What to write, all under `harnesses/`

1. **`stages.json`**: for every problem P01–P16 and every sub-problem, the
   ordered list of its stages as the problem file gives them: for each
   stage, its number, a one-line description quoted or closely
   paraphrased from the problem file, the query or queries it poses, and
   each query's answer cap (1 for an *any one* query, 20 otherwise, as the
   problem states), whether it is a commit stage (P11), whether it spawns
   a computation (P09), and the problem file's line where the stage is
   stated. **No constants and no valid outcomes**: the program holds the
   stage information; the harness only knows the structure. Where a
   sub-problem varies a size n (P12, P13, P16), list the sizes the problem
   file gives.
2. **`README.md`**: the contract that every per-system harness implements
   and every program is written against, in terms concrete enough that a
   program author who cannot run anything can write to it correctly:
   - how a run is driven: one sub-problem, one configuration, one mode;
     the operations pose, spawn, answers, observe, print, as `PROTOCOL.md`
     defines them, and nothing that orders, chooses or re-poses goals on
     its own;
   - the two ways a stage is posed (into the same computation, or by
     reposing stages 1 to k, replacements and withdrawals included) and
     the rule that observing must not consume the computation;
   - commitments preserved on reposing, and the effects log (P11);
   - the budget (10⁶ steps per stage and computation, in each system's
     unit, plus the measured restart cost for a reposed run), the safety
     limit (60 s per stage, one rerun at 600 s, both recorded), and what
     is done after *budget* and after *error*;
   - the three modes (behaviour, cost, storage), which run gives which
     figure, and the rule that a sampled measurement never comes from the
     run that gives the step count or the classification;
   - **the raw record**: one JSON schema, the same for every system, for
     what a run writes. Per stage at least: stage number, how it was posed
     (and which stages were replayed), each query's answers verbatim and
     the cap, the execution state in the vocabulary of `SPECIFICATION.md`
     ("Execution state") as far as the harness can tell it mechanically
     (classifiers decide the semantic and representation axes, not the
     harness), the raw state `observe()` read, alternatives and suspended
     work in the systems file's units, steps, store, wall time, stdout
     and stderr verbatim, safety-limit events, manual actions. Plus run
     metadata: spec tag, system, configuration, mode, program path and
     SHA-256, system build (commit or image digest), harness commit.
     Write it as `harnesses/record.schema.json` too;
   - where raw records go: `results/<system>/<configuration>/<problem>/raw/`;
   - the per-system harness's command line, the same shape for all four:
     `harnesses/<system>/run CONFIGURATION PROBLEM SUBPROBLEM MODE PROGRAM OUTDIR`;
   - what a program must provide so the verifier can substitute hidden
     variants' constants (`PROTOCOL.md`, "Writing a program", rule 6): one
     marked constants block, or input. Say which, per system, or leave it
     to the system harnesses and say so.
3. **`harnesses/validate.py`**: checks a raw record against the schema
   (Python 3 standard library only).

Do not write any harness for a particular system, and do not write a
program for any problem. Do not run anything except `validate.py` on
records you make up by hand to test it, which you put in
`harnesses/examples/`, clearly marked as made up.

When you are done, commit your work in CLONE on a branch
`harness-common` (author `harness-common <harness-common@sandbox>`, no
trailers), and end with a short summary: what you wrote, and every entry
in `QUESTIONS.md`.
