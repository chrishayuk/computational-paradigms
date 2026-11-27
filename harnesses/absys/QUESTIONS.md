# Questions: the Absys harness

*What the common contract (`harnesses/README.md`, `harnesses/QUESTIONS.md`)
or the specification could not be implemented as written for Absys, or
left open, and the reading implemented here. No frozen file was changed.
An amendment can settle any of them.*

## A1. The budget counts per assertion, not per stage

`PROTOCOL.md`: 10⁶ steps "per stage and per computation". The systems
file's step is "one step of the machine, as its `--steps` budget counts
them", and `--steps N` is "the budget of steps for each assertion"
(`src/main.rs`): `Session::accept` elaborates each assertion for at most N
steps. A stage's section may hold several assertions (a definition and an
application, several facts). The repl offers no way to change the budget
while it runs, and reports no step count, so the harness cannot stop a
stage when its assertions together reach 10⁶.

**Implemented:** `--steps B` with the problem's B, per assertion. A stage is
*budget* when the system reports derivations still elaborating at its end.
A stage of *m* assertions may spend up to *m*·B steps; when a cost run
shows a stage over B without *budget*, the record says so in a note. A
program author who wants the stage's budget to be exactly B can write a
stage as one assertion (a conjunction `{…, …}` in the 1990 notation,
`begin … end` in 1969); that choice is the author's and changes the order
in which the machine takes the parts, so the harness does not require it.

## A2. Behaviour from the baseline, or answers in full

The systems file says results "report the baseline commit for behaviour
and the instrumented commit for store", and also that `--full`, on the
instrumented branch, exists "so `observe()` can read every answer". The
baseline prints at most 32 elements of a list and 24 derivations, and P13
has lists of up to 10⁵ elements. One run cannot do both.

**Implemented:** behaviour runs use `absys-measure` (`5450449`) with
`--full` and without `--measure`. The systems file records that its
default output is identical to the baseline's in 140 runs and `--full`'s
in the 132 the baseline did not cut short; the qualification checks again
that every `print()` the harness records equals the baseline `absys
FILE`'s output, where nothing is cut short. Records say `instrumented:
true` and give the measure commit.

## A3. Where the system's output for a stage ends

The repl prints nothing when it has finished with a line (no prompt when
its input is not a terminal), so the harness cannot tell from its output
alone that a stage is done.

**Implemented:** after each section the harness writes `.help`, a command
of the repl that only prints a fixed text; the text marks the end. If a
section ends inside an unfinished assertion, the repl reads `.help` as its
continuation and replies ``error at L:1: `.` is not in the notation``,
which the harness recognises as the same mark, and records as the stage's
error. `check` rejects such a section, so a checked program never meets
it.

## A4. Steps and store only for a whole text

The repl, the incremental system, reports no step count and no store;
`--measure` (the systems file's qualified measurement) works only in
`absys FILE`, which reads the whole file before it starts and prints its
results at the end. A cost or storage run cannot both receive stage *k*
only when it is posed and measure it.

**Implemented:** each stage *k* of a cost or storage run is a new process,
`absys-measure FILE --measure --full`, FILE the text of the parameters,
prelude and stages 1 to *k*. Its session accepts the assertions one at a
time, like the repl's, so its state and each assertion's steps at stage
*k* are those of the incremental session; the qualification checks this
for every stage of every test. The records say what was done:
`posed.how: "reposed"`, `reason: "configuration"` (the schema has no
reason for "the measurement's way"), the steps of stages 1 to *k*−1 as
`restart_cost` (in-run), `steps.stage` the steps of stage *k*'s own
assertions (the incremental cost) and `steps.restated` the whole run.
Absys's behaviour runs pay no restart cost; classifiers should not read
one from these records. A syntax error anywhere in stages 1 to *k* stops
the whole `absys FILE` run with no output, where the repl would have gone
on: after an error, a cost or storage run measures nothing more.

## A5. spawn() in a system with one computation

P09a, P09b and P16b spawn computations "in the same instance of the
system, sharing one database". Absys has one computation per session: an
assertion is added to every derivation, and there is nothing else to add
it to. The systems file lists no concurrency.

**Implemented:** `spawn(c)` gives the system the computation's SPAWN
subsection, into the one session, after the previous computation has run
"to its end or its budget" (`side_by_side: false`). Each spawned
computation's answers and state are read right after its own section,
before the next is given, since that is the moment it has run to its end;
the next computation's are read with it included. (`PROTOCOL.md` lists
the calls as spawn, then answers; in a configuration that runs one
computation to its end before the next, this reading takes each one's
answers at its end.) Each has its own budget, per assertion as in A1.

Because the spawned computations are one computation, they share every
unknown. So for P16b the harness spawns the four contributors and does not
use `spawn_fallback`; that the fallback ("posed as one conjunction in
main") and Absys's spawn come to the same computation is for the
classifiers to note. Whether P09a's "not conjoined" can be met at all is
the program author's and the classifiers' question, not the harness's.

## A6. A commit stage in a system that never selects

At a commit stage "the system selects one of its current outcomes v", and a
reposed run replays it as x = v. Absys keeps every derivation live, and
has no way to receive v at run time: it reads no input.

**Implemented:** the program's section for a commit stage is given as it
is (it may hold only comments). `answers(1)` is the first derivation
printed, as for any any-one query; it is not a selection, and the record
says so in a note. `replayed_commitments` is always empty, and a reposed
run replays the commit stage's section as written. `validate.py` warns of
this ("the system selected nothing?"), as the contract foresees.

## A7. emit, and when an effect is performed

The contract's emit appends m "rendered as the system renders m". Absys's
one external effect is `tout(label, term)`, which keeps its output in the
derivation that performed it: a derivation that later fails loses its
outputs from the printed state.

**Implemented:** `tout("emit", T)` is the binding of emit. The harness
reads each output from the system's trace (an `output` event, `emit =
VALUE`), at the moment it is performed, so an output of a derivation that
later fails is still in the log. The entry is the text after `emit = `.
The trace is on in P11 runs only (and in cost runs with the 10⁶ budget,
for repeated work); it prints the events the machine records in every
run, and changes nothing.

## A8. alternatives pending

The state means a system "has stopped after an answer, and holds
alternatives that a request for more answers would resume". Absys
elaborates every derivation before it reports, and reports all of them; no
request resumes anything, under fair or depth-first search.

**Implemented:** the harness never records *alternatives pending*. The
derivations held are counted in `alternatives.at_boundary` (unit:
derivation), and those beyond the cap are in `observe.raw`.

## A9. How a program learns its instance's parameters and orders

The contract has the program "take n, an arrival order, a spawn order or
the answer mode from the harness". An Absys program reads no input, and
its stages are fixed text.

**Implemented:** (1) parameters the program declares (`% PARAMETERS`) are
given to the system as assertions `NAME = VALUE`, written by the harness
in the program's notation, before the prelude; (2) where the order names
the stages' relations (P02b, P07a), a program may write them as PART
sections, and the harness gives part `order[k-1]` at stage *k*. Both are
listed as confounds. Without (2), a program would have to choose each
stage's relation from `order` with its own code, adding alternatives and
steps the problem does not have.

## A10. Where the constants are, without anticipation

The constants must be in one place the verifier can replace, and a stage's
constants may not reach the system before that stage (`PROTOCOL.md`,
"Writing a program", rule 5). In Absys every assertion is a relation the
machine holds and acts on, so a block of assertions `c = 7` given at
stage 1 would give the system later stages' constants as information from
stage 1.

**Implemented:** the block, in the prelude, is a table `NAME = VALUE` that
the harness reads and never gives to the system. When it gives a section
(the prelude, a stage, a part, a spawned computation), it replaces each
name of the table in that section's text by its value, textually, outside
quoted constants and comments (README, 3.9). A constant reaches the system
only with the section that uses it. The verifier replaces only the block.
The replacement is listed as a confound; the qualification shows, for
X10a in every mode, that a later stage's constant is not in the system's
state before its stage, and that no constant's name reaches the system.

## A11. check, with no parse-only mode

The brief asks whether `absys lsp` can give diagnostics without running
the text. It cannot: its diagnostics accept each assertion with a budget
of 20 000 steps (`src/lsp.rs`, `analyse`), and report, among others,
"after this assertion no derivation survives".

**Implemented:** `check` uses `absys-measure json FILE --steps 0`, which
parses, compiles and adds each assertion to the goal, and takes no step;
it reads only the error and the count, and it stops if the system reports
a step or an event. Adding an assertion to the goal without a step is not
running it: nothing is elaborated, no binding made, no output performed.

## A12. A reposed stage whose replay cannot finish

Rule 5 of `validate.py`: a reposed stage has a measured restart cost. If
the replay of stages 1 to *k*−1 cannot finish (the system is killed for
lack of memory, or stopped at ten times the safety limit), the restart
cost cannot be measured, and nothing honest can stand in for it.

**Implemented:** `restart_cost: null`, the reason in `harness_faults`, and
the record is kept as `<run_id>.INVALID.json` with exit 3. With enough
memory (README, section 1), the replay of a stage that ended in *budget*
always finishes, since every assertion stops at the budget.

## A13. An error the system recovers from

The repl reports a syntax error and goes on with the next line, so the
session could continue. `PROTOCOL.md` reposes after an error "in every
configuration, incremental ones included".

**Implemented:** the stage is *error*, with the system's message
verbatim (and *suspended* beside it if a derivation holds suspended
work), and the next stage is reposed into a new session, replaying every
section, the erroneous one included.

## A14. Probes

The brief asks for the systems file's probes to be run. `systems/absys/`
has none (only Python and SWI-Prolog have `probes/`).

**Implemented:** the qualification uses its own made-up programs, and the
system's own output run directly as the reference.
