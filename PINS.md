# Pins

*Candidate for `spec-1.0`.* The version or commit of every system in the
first comparison, fixed at the freeze (`PROTOCOL.md`, phase 3). A change
to any of them after the freeze makes a new configuration, reported
separately.

| system | what is pinned | pin | used for |
|---|---|---|---|
| Absys | the reconstruction, https://github.com/chrishayuk/absys, `main` | `efd5203` | behaviour |
| | the same, branch `measure` (`--measure`, `--full`) | `5450449` | cost and storage; `--full` output |
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
- **ALGOL 60 `151cdff`** was checked against `6e8740c` on all 100 programs
  of that repository, in both dialects, with measurement on and off (200
  runs).
