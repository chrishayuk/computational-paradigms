# Qualification of the Python harness

Evidence that `harnesses/python/run` does what [`../README.md`](../README.md)
says and does not change what CPython computes. Every program here is for a
**made-up** problem (X01–X10, in [`stages-qual.json`](stages-qual.json)),
not one of P01–P16, and uses no problem's constants. Nothing here is a
result.

    container run --rm --platform linux/amd64 --volume "$PWD":/work --workdir /work \
        cp-agent-python:spec-1.0 python3 -B -s harnesses/python/qualification/qualify.py

| file | what it is |
|---|---|
| [`qualify.py`](qualify.py) | reruns everything below and prints PASS or FAIL for each claim |
| [`output.txt`](output.txt) | its output, from the run whose records are in `records/` |
| `records/<stamp>/` | every raw record that run wrote (all pass `validate.py --stages stages-qual.json`), and the X02 effects logs |
| [`direct.py`](direct.py) | runs a program **without the harness** (a stub `cp`, no shared code), counting instructions as `systems/python/probes/meter.py` does and relation calls as `p2_algops.py` method C does |
| [`programs/`](programs) | the made-up programs; `x01_total.py` is the README's example |
| [`peek.py`](peek.py) | prints a summary of records (for reading them, not used by `qualify.py`) |

What it checks:

- **(a)** For the example, the counting and store programs, the systems
  file's probe workloads (`finite` from `p6_budget.py`, `build_and_drop`
  from `p3_memory.py`) and spawned computations: the answers the harness
  collects equal what the program prints when run directly; its standard
  output is byte-identical; instructions per stage and relation calls per
  stage equal the direct counts; the probe figures (609 and 6,009
  instructions; a traced peak growth of 40,000,208 bytes, within the
  harness's own traffic; 17 suspended generator frames for depth 16) are
  reproduced through the harness; behaviour, cost and storage runs agree.
- **(b)** The same program posed incrementally and reposed gives the same
  answers and observations; a reposed run replays a commit stage as its
  verbatim answer; the effects log is never reset and marks replayed
  entries.
- **(c)** Budget (exactly 10⁶, continued in the same computation with the
  uninterrupted total), an endless loop, a `RecursionError`, a process
  killed by a signal, a loop inside one C call (safety limit, rerun, final
  timeout), a fixed limit, a program that raises at stage 1 or in its
  set-up (every later reposed stage stops in the replay and still has a
  measured restart cost), the cap, a waiting thread (quiescence), a
  computation the program did not register, and usage errors (exit 2, no
  record): each gives a valid record, or none where it should.
- **(f)** No anticipation: at stage 1 the whole memory of the program's
  process, read from outside through `/proc/<pid>/mem`, holds stage 1's
  constant and not stage 2's; at stage 2 it holds stage 2's. A constant not
  tagged with a stage is rejected by `check` and `run`.
- **(d)** Every record validates.
- **(e)** `check` executes nothing (a program whose only effects are writing
  a file and printing a marker leaves neither), and reports syntax and
  static errors.

X04 and X05 have made-up safety limits of 4 s (rerun 8 s) so that the
qualification runs in minutes; the harness takes every limit from the
stages file, as it does for P01–P16.
