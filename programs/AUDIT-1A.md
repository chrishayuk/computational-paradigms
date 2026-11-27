# Audit of the batch 1A implementation authors

Each implementation author was an agent with its own context, given only
its brief (`sandbox/briefs/implementation.md`, rendered per system) and its
own clone of the repository at `spec-1.0.1`. After it ended, every command
it ran and every file it read, from its full transcript, was checked
against the brief: it may read only the files listed there, and run only
the harness's `check`. Each changed nothing outside `programs/<system>/`.

| author | commands | `check` calls | anything executed besides `check` | reads outside the brief |
|---|---|---|---|---|
| implementation-absys | 29 | 8 | none. `cat`/`ls` in the image to read the Absys documentation the brief allows; `python3` on the host to read `stages.json` and to edit its own README | none. It did not open `docs/research.md` or any `research/` directory (the precursors) |
| implementation-swi-prolog | 33 | 21 | none. One `python3 -c` on the host reading `stages.json` (disclosed); bash, awk and sed to write files | none. Two reads under the session's `tool-results` folder were its own saved outputs of allowed files (checked) |
| implementation-python | 37 | 11 | none. One command beginning `python3 -c "print(1)"` was refused before it ran (disclosed) | none. Reads under `tool-results` were its own saved outputs of allowed files |
| implementation-algol-60 | 53 | 19 | none. `python3` on the host to read `stages.json`; one `check` of a scratch file with a deliberate error, to see that `check` reports errors | part of `harnesses/QUESTIONS.md` (the common harness's questions; no programs or outcomes), disclosed |

No author read `calibration/`, `reviews/`, `variants/`, `results/`, the
private variants or another role's work. No program was run before this
commit.

Points the authors disclosed that bear on results (details in each
`programs/<system>/README.md`):

- **Absys.** One text serves all three configurations. P01c's sequence
  constant is held as list members without brackets, so a hidden variant
  with an empty sequence cannot be substituted into it.
- **SWI-Prolog.** P02 in *plain* and *tabling* raises an instantiation
  error wherever fewer than two places are known, by design. One named
  variant, P01c with the occurs check, in every configuration.
- **Python.** *extended* P03 uses two mechanisms of the program author's
  own, unification and resolution, counted by the author as S. They are
  not in the phase-4 list (`harnesses/python/S-mechanisms.md`). P02b's
  constants are tagged under all three stages, because which relation
  arrives at a stage depends on the order, so values reach the process
  before their stage (`AMENDMENTS.md`, 3.3).
- **ALGOL 60.** P02b has one program and constants file per order. P01b has
  a fixed store of 1000 cells. x1 and x1sim share one text; report has its
  own, with the IFIP input and output procedures. The image's
  documentation was not read (a listing was refused); idioms are cited
  from the Revised Report and the harness.
