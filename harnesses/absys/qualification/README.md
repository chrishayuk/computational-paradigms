# Qualification of the Absys harness

Evidence that `harnesses/absys/run` does what its README says and does
not change what the system computes. **Everything here is made up**:
problems X10–X21 (`stages-qualification.json`) are invented, are not in
the suite, and use none of its constants; no program here is a program
for P01–P16. Nothing here is a result.

| file | what |
|---|---|
| `run-qualification` | reruns every test, writes `output.txt` and `records/` |
| `output.txt` | its output, from the last run |
| `stages-qualification.json` | the made-up problems, in the format of `harnesses/stages.json` (valid under `validate.py --check-stages`) |
| `programs/` | the made-up programs |
| `records/` | every raw record the run wrote, `records/<configuration>/<problem>/raw/` |

Run, from the repository root:

    container run --rm --platform linux/amd64 --volume "$PWD":/work --workdir /work \
        cp-agent-systems:spec-1.0 harnesses/absys/qualification/run-qualification

It takes about a minute and a half, under the container's default 1 GiB
of memory (which X21a needs, to show a process killed for lack of memory).

## What it checks

1. **Runs.** 17 made-up instances × 3 modes, under all three
   configurations, and X21a: each exits 0 with a record.
2. **(a) The system run directly.** For every stage *k* of ten instances
   (both notations used, PART order, parameters, effects, budget): the
   harness's `print()` from the repl equals `absys-measure FILE --full`
   run directly on the text of stages 1 to *k*, and equals the **baseline
   `absys` (`efd5203`)**'s output; cost and storage records print the
   same; the steps the cost record gives (restated, stage, restart cost)
   equal `--measure`'s, run directly; the storage record's vector equals
   `--measure`'s last row. Each spawned computation's answers equal the
   system's state on the text up to its section. `absys-measure json`'s
   steps (used for a reposed behaviour stage's restart cost) equal
   `--measure`'s, assertion by assertion. The effects log's entries equal
   the outputs `absys FILE --trace` shows performed.
3. **(b) Incremental against reposed.** Seven instances run again in
   behaviour mode with every stage reposed (`ABSYS_HARNESS_POSING=reposed`):
   every stage's answers and `print()` are identical. Behaviour (repl)
   and cost (`absys FILE` on stages 1..k) answers are identical too.
4. **(c) Budget, safety limit and error.** X12a: budget, then the next
   stage continued into the same session after it (behaviour). X15a: the
   safety limit, the rerun under the raised limit, the final timeout, and
   the next stage reposed after it. X16a: a fixed limit, no rerun. X13a
   and X13b: a syntax error, and a section ending in an unfinished
   assertion, each *error*, and the next stage reposed. X21a: the
   system's process killed by the kernel, recorded as *error* with its
   signal. In every mode.
5. **check executes nothing.** On `marker.abs`, whose only effect when run
   is to output a marker (and to loop): `check` reports no error and its
   output has no marker, while running the program does output it; the
   system's parse that `check` uses reports zero steps, zero events and
   no output for every assertion. On `bad-syntax.abs`, `check` reports
   each error with the system's own message. Every other program checks
   clean, and the two made to fail do fail.
6. **(d)** Every record passes `validate.py --stages stages-qualification.json`.
7. **Size.** Records over 400 kB (the cost run of X12a, whose trace of a
   10⁶-step budget is about 100 MB) are validated in full, then their long
   `stdout`, `stderr` and `print` strings are cut to their first and last
   4000 characters, and a note in the record gives the full record's size
   and SHA-256; `output.txt` lists them. The truncated records still
   validate; all records together are under 5 MB.

Also under (a): for X10a in every mode, a constant reaches the system only
with the stage that uses it (41 is not in the state before stage 2, nor
`'red'` before stage 3), and the block's names never reach the system.

The warnings `validate.py` prints for X18a ("reposed past commit stage 2
with no replayed commitment") are expected: Absys selects nothing at a
commit stage (`../QUESTIONS.md`, A6).
