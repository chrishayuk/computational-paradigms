# Absys: labelled measurement reruns (m2)

**Why.** The measurement build of the original runs, absys-measure
`5450449`, walked the whole computation after every step to keep an exact
store peak. In runs that hold many alternatives this made cost and storage
runs reach the safety limit (60 s, then 600 s) long before the step budget,
so their steps and store were not measured. The behaviour runs were not
affected. The protocol reads such a stop as a limit of the measurement,
not of the model (`PROTOCOL.md`, "Modes of running").

**What changed.** Only the measurement. absys-measure `8a0eefd` adds
`--peak-every N` (PINS.md, with its qualification). The Absys harness at
`98baa62` uses `--peak-every 0` in cost runs, where no store peak is
taken, and `--peak-every 1000` in storage runs, where peaks are recorded
as `kind: "sampled"` with their interval. Image
`cp-agent-systems:spec-1.0-m2`. The programs, the machine and the limits
are unchanged.

**Which runs.** Every Absys cost or storage record in which an attempt
reached the safety limit was rerun once, by `tools/rerun-measurements.py`,
into `<configuration>/<problem>/raw-rerun-m2/`. Each rerun names its
original record in its notes (`HARNESS_RUN_LABEL`), and
`rerun-m2-log.tsv` lists both. **The original records stand, unchanged**,
as the records of those runs. A rerun is reported beside its original,
labelled, and never in its place.

**Large records.** In cost runs the harness turns Absys's step trace on,
and the record keeps standard output verbatim. Where a run now reaches
the full budget, that trace is hundreds of megabytes. Records over 50 MB
are committed gzip-compressed, as `.json.gz`, after they were validated.
They are the three P03f cost reruns (400, 185 and 185 MB; 15 to 17 MB
compressed).

## What the reruns measured

| problem | configuration | mode | original | rerun |
|---|---|---|---|---|
| P03f | absys | cost, storage | safety limit at 60 s and 600 s, nothing measured | budget at 1,000,004 steps; 900 derivations; 2,416,542 term nodes (peak, sampled: the same) |
| P03f | absys-wake-back | cost, storage | the same | budget at 1,000,004 steps; 900 derivations; 2,416,519 term nodes (peak the same) |
| P03f | absys-depth-first | cost, storage | the same | budget at 1,000,004 steps; 19 derivations at the budget, peak 107 (sampled); 10,762 term nodes, peak 1,196,434 |
| P04d, P04f | all three | cost, storage | safety limit, nothing measured | **error**: the system's process was killed when the container's memory (4 GB) ran out, within seconds, as in the behaviour run. Steps and store at the budget remain **unavailable** |

For P04d, the store's growth was established separately, by diagnostic
runs without instrumentation at fixed smaller budgets: peak resident
memory 216 MB, 849 MB and 3,382 MB at 10⁴, 2×10⁴ and 4×10⁴ steps (about
2,001, 4,001 and 8,001 derivations), and three out-of-memory kills
confirmed by the container's `memory.events`. Those are diagnostics, not
records of the study.
