# Pins

*Candidate for `spec-1.0`.* The version or commit of every system in the
first comparison, fixed at the freeze (`PROTOCOL.md`, phase 3). A change
to any of them after the freeze makes a new configuration, reported
separately.

| system | what is pinned | pin | used for |
|---|---|---|---|
| Absys | the reconstruction, https://github.com/chrishayuk/absys, `main` | `efd5203` | behaviour |
| | the same, branch `measure` (`--measure`, `--full`) | `5450449` | cost and storage; `--full` output |
| | the same, branch `measure`, adding `--peak-every N` | `8a0eefd` | labelled measurement reruns only (`results/absys/*/*/raw-rerun-m2/`), reported separately from the original records |
| | the behavioural reference, before the printer fix | `7bb61e6` | kept, not run |
| SWI-Prolog | the `swipl:11.0.1` image | `sha256:b51af487f3306fe240eae8c13159c85b5526509952e1b949cc22f48a1f82a742` | every mode |
| Python | the `python:3.13.7` image (CPython 3.13.7) | `sha256:fe841081ec55481496a4ab25e538833741295d57d2abdec8d38d74d65fb4715b` | every mode |
| ALGOL 60 | the interpreter, https://github.com/chrishayuk/algol-60, `main` | `6e8740c` | *report* and *x1*: behaviour and cost |
| | the same, branch `measure` (`--measure`) | `151cdff` | storage |
| | x1sim: Vakulenko's X1 compiler and simulator, https://github.com/sergev/x1-algol-compiler | `938fa03` | *x1sim*: behaviour only |

Results are taken on Linux x86_64 in the pinned images, or from the pinned
commits built there with the toolchain the repository's CI uses. The
measurements were also qualified on macOS arm64 (SWI-Prolog 11.0.1 from
Homebrew; CPython 3.13.7 from python-build-standalone), where every count
compared was the same; a figure from macOS is marked as such.

## Why each commit

- **Absys `efd5203`** is `7bb61e6` with one defect fixed: printing a list
  that contains itself (`x = [x]`, problem P01c) overflowed the stack, after
  the computation had finished. Only the printer changed. Against
  `7bb61e6`, every example and research text prints byte for byte the same
  in eight output modes and as JSON (160 runs); only runs that crashed print
  differently. The defect is recorded in the reconstruction's
  `docs/decisions.md`, "Defects found in the reconstruction".
- **Absys `5450449`** is the measurement branch rebased onto `efd5203`.
  Against `efd5203`, with measurement on and off, its output is the same
  byte for byte (`systems/absys/README.md`).
- **Absys `8a0eefd`** adds one option to `5450449`, `--peak-every N`:
  how often `--measure` takes the peak (1, the default: every step, as
  `5450449` does; 0: only at the start and end of each assertion). It was
  made in wave 1, batch 1B, after `5450449`'s per-step walk of the whole
  computation was found to stop cost and storage runs at the safety limit
  long before the step budget (P03f, P04d, P04f). The machine is unchanged.
  Qualified by `harnesses/absys/qualification/peak-every/qualify.py`
  (output in `qualify.txt` beside it). At every setting, standard output
  and every step count must be byte for byte the same as `5450449`; at 1,
  the peak identical; otherwise, each sampled peak between the boundary
  value and the exact peak. By configuration:

  | configuration | budget | programs | against an exact reference | limited | fail |
  |---|---|---|---|---|---|
  | absys | 10^4 | 56 (batches 1A and 1B, the variants, the system's examples) | 54 | 2 (P04d, P04f: no exact reference finished in 30 s) | 0 |
  | absys | 10^3 | 3 (P04d, P04f, P03f) | 3 | 0 | 0 |
  | absys-depth-first | 10^4, P04 at 10^3 | 39 + 6 | 45 | 0 | 0 |
  | absys-wake-back | 10^4, P04 at 10^3 | 39 + 6 | 45 | 0 | 0 |

  So the two limited cases are qualified against an exact reference only
  at the lower budget. The fixed build is used only for the reruns of the
  measurements the old one could not make, which are labelled and kept
  apart; every original record
  stands. Image `cp-systems:spec-1.0-m2` (`sandbox/Containerfile.systems`,
  `--build-arg ABSYS_MEASURE=8a0eefd`).
- **ALGOL 60 `151cdff`** was checked against `6e8740c` on all 100 programs
  of that repository, in both dialects, with measurement on and off (200
  runs).
