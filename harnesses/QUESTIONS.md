# Questions on the specification, and the readings implemented

*Harness author, common part, wave 1, against `spec-1.0`. No frozen file
was changed. Each entry says what is open, the reading implemented in
`harnesses/`, and why. An amendment (`PROTOCOL.md`, "Amendments") can
settle any of them; until then, every system harness implements the
reading here.*

## Q1. Descriptions in `stages.json` without constants

The brief asks for each stage's description "quoted or closely
paraphrased from the problem file", and also for "no constants". Most
stages' information is mostly constants (z = 2, pick's facts, ⟨1,2⟩).

**Implemented:** descriptions paraphrase the problem file with every
constant of the stage information replaced by a placeholder: `<k>` an
integer, `<atom>`, `<seq>` a sequence, `<facts>` a set of facts. The
names of unknowns and relations, and structural numbers fixed by the
problem rather than by its constants (sizes n, j = ⌈n/2⌉, m = n/4, the
four contributors), are kept. The line number points to the full text.
*Why:* the harness must not hold, or be able to pass, a stage's
information (`PROTOCOL.md`, "Writing a program", rule 6); the
constants are public in `problems/`, but a structure file that carried
them would invite a harness to supply them, and would be wrong for the
hidden variants.

## Q2. The command line has no place for size, order or answer mode

`run CONFIGURATION PROBLEM SUBPROBLEM MODE PROGRAM OUTDIR` names one
sub-problem, but P02b (six orders), P07a (six orders), P09a (two spawn
orders), P12 (n = 8, 12, 16; all and any one), P13 (four n) and P16
(three n; P16a also three arrival orders) are each several runs.

**Implemented:** SUBPROBLEM is an **instance id** from `stages.json`. A
sub-problem with one instance keeps its own id (`P07c`); the others name
their parameters (`P02b.R2R1R3`, `P07a.312`, `P09a.BA`, `P12c.n16.any`,
`P13d.n10000`, `P16a.n1000.interleaved`). P07a's instance in the written
order keeps the id `P07a`. The harness passes the instance's parameters
to the program; they are structure, not constants, since
`variants/README.md` says sizes and arrival orders were not varied.

## Q3. What a stage's query is

The problem files give the information of each stage and its valid
outcomes, but rarely a separate query. `PROTOCOL.md` says `answers(cap)`
is called at each stage.

**Implemented:** each stage poses one query per computation: the answers
to all the information of stages 1 to k, over the sub-problem's unknowns
(listed by name in `stages.json`), with cap 1 where the problem says
*any one* (P11 throughout, line 15; P12's any-one instances; P15a1,
P15b, P15b2, P15c) and 20 otherwise. The P11 stages before and after the
commit are any-one queries too, since P11 says its queries are for any
one outcome. P06e1 and P06e2, ground queries, are cap 20: they are not
*any one* queries.

## Q4. P16b: whose answers at stage 1, and whose budget

P16b's stage 1 is four spawned contributors, but its valid outcome is
joint (xᵢ = x₁ + i − 1), and only stages 2 and 3 are said to be "posed to
the shared instance … with one budget per stage for the whole".

**Implemented:** at stage 1 each contributor C1–C4 is spawned with its own
query (cap 20), its own budget and its own execution state, as for any
spawned computation (`PROTOCOL.md`: each separate computation has its own
budget); the joint state is read by `observe()`, and the classifiers
classify on it. Stages 2 and 3 are posed to `main`, the instance's top
level, with one budget. Where the configuration cannot share unknowns
between computations, stage 1 is one conjunction in `main`
(`spawn_fallback`, `fallback_queries`), as line 47 says. Whether a
configuration can share unknowns between computations is stated by its
system harness.

## Q5. P09b's order

P09a is posed in both orders; P09b says nothing of order.

**Implemented:** P09b is spawned once, in the order written (A, then B).

## Q6. How restart cost is measured, and so a reposed budget

`PROTOCOL.md` gives a reposed run a budget of "its measured restart cost
plus 10⁶", and `METRICS.md` defines restart cost as "the step count of
running stages 1 to k−1 alone, measured". It does not say whether that
run includes collecting stage k−1's answers, nor which run measures it.

**Implemented:** the restart cost is always measured, in the system's
step unit, and the budget of a reposed stage k is always that plus 10⁶
(10⁸ for P12, P13, P16):
- **in-run**, by default: the harness reads the system's step count at
  the moment stage k is first posed in the reposed run, after the replay
  of stages 1 to k−1 (each replayed stage having the budget it had when
  first posed). That count is the restart cost; the stage then runs on
  with 10⁶ more steps. In a configuration that poses stages 1 to k as one
  conjunction, "first posed" is the first entry into stage k's part,
  marked by the program's H call for it; work done after backtracking
  into earlier stages counts in the stage, not in the restart cost;
- **separate-run**, only where the system cannot read its count at that
  moment: stages 1 to k−1 are run alone first, posed as in the replay,
  without `answers()`, and their steps are the restart cost.

`restart_cost_method` records which. A reposed stage with no measured
restart cost is invalid (`validate.py`), except in a configuration that
has no step count at all (ALGOL 60 x1sim), whose records say
`budget_enforced: false` and `restart_cost: null`, as in Q12. *Why:*
`PROTOCOL.md` requires the measured restart cost plus the budget, so the
budget cannot fall back to the budget alone; in-run measurement measures
the replay actually spent, without an extra run.

## Q7. What follows a timeout, and how the rerun is posed

`PROTOCOL.md` says what follows *budget* and *error*, and that a stage
stopped by the safety limit is rerun once, but not how the rerun is posed
in an incremental configuration, nor how stage k+1 is posed after a final
*timeout*.

**Implemented:** a safety-limit stop kills the computation (the harness
cannot continue what it stopped from outside), so: the rerun of stage k
is a reposed run of stages 1 to k under the raised limit (attempt 2,
`reason: "safety-rerun"`), with the reposed budget; and after a final
*timeout*, stage k+1 is posed by reposing stages 1 to k+1
(`reason: "after-timeout"`), counted under restart cost, as after
*error*. A system harness that can stop a stage at the limit without
losing the computation (an engine it can abort and keep) says so, and
may then rerun incrementally.

## Q8. The scope of the effects log, and which runs write to it

`PROTOCOL.md` says effects are written to "one log per problem, never
reset, across every run the harness makes for classification", and that
separate observation runs write to a separate log. P11 judges L "when the
problem ends", and gives each of P11a–d its own valid L.

**Implemented:**
- one classification log **per configuration and instance** (P11a, P11b,
  P11c, P11d each), since each sub-problem's effects class is judged on
  its own L;
- behaviour runs write to it, their reposed stages and safety reruns
  included. Cost and storage runs, which are not used for classification,
  write to the observation log with the separate observation runs;
- never reset, even when the same instance is run in behaviour mode a
  second time (after a harness fault, for instance). Each record carries
  `entries_before_run`, so the classifiers can see what an earlier run
  left in L. Whether such a log can still be judged *exact* is theirs to
  say.

## Q9. "One identical stub for every system"

P11 says the harness provides L and emit "as one identical stub for every
system". The four systems cannot run the same code.

**Implemented:** the stub is identical in behaviour and in its log format
(`README.md`, section 6): append m, rendered as the system renders it,
with its run, stage, attempt and replay context; never fail, defer,
buffer past the stage, deduplicate or read. Each system harness binds it
into its language and lists that binding's tokens as H.

## Q10. P13's "larger values of n are not run after it"

P13 says a run stopped by either limit is recorded and the larger values
of n are not run after it. A run of the harness is one instance (one n),
so `run` cannot apply it. P12 and P16 take P13's *limits* ("as in P13")
but do not repeat this rule.

**Implemented:** the rule is applied by whoever runs the batch, across
runs, for P13 only (`stages.json`: `stop_larger_n_after_limit` on P13
alone), per configuration, task and mode, and an n not run is recorded
as not run. P12 and P16 run every n. *Why:* the text states the rule
under P13's own budget section; extending it is an amendment.

## Q11. No rerun in P12, P13 and P16

`PROTOCOL.md` reruns a stopped stage once with the limit raised tenfold;
P12, P13 and P16 fix their limit of 600 s and say it is not raised.

**Implemented:** in those three, the first stop is final
(`safety_limit.action = "fixed-limit-timeout"`, state *timeout*); there
is no second attempt (`rerun_limit_s: null`). The problem's own text is
the more specific.

## Q12. A budget that cannot be enforced (ALGOL 60, x1sim)

x1sim is behaviour only and reports no step count, so 10⁶ steps cannot be
enforced.

**Implemented:** its records say `budget_enforced: false`, only the
safety limit stops it, and no stage of x1sim can be *budget*. Its
non-terminating stages are therefore *timeout*, which is to be read as
the absence of a budget, not as evidence about the time taken.

## Q13. What the safety limit times in a reposed stage

"60 seconds per stage" does not say whether, in a reposed run of stages
1 to k, the replay of 1 to k−1 is inside the limit.

**Implemented:** the limit covers one attempt: the whole reposed run,
replay included, or, for an incremental stage, from posing stage k to the
end of `print()`. *Why:* the harness cannot tell from outside where a
replay ends in every system, and the limit protects the harness rather
than measuring.

## Q14. Execution state when answers are taken on a separate run

Where collecting answers would consume an incremental computation,
`answers()` and `observe()` are taken on a separate run of 1 to k; but
"the execution state is classified after the call", which is then on the
separate run.

**Implemented:** the execution state recorded is the one after
`answers()`, on whichever run it was called (`collected_on`). Whatever
the harness can read of the incremental computation's own state without
consuming it goes in that attempt's `notes`, with its source.

## Q15. P16d2's stage numbers

P16d2 is "P16d with stage 2 omitted and stage 3 replaced by xₙ = x₁", so
its stages could be numbered 1 and 3.

**Implemented:** they are numbered 1 and 2, consecutively, as every
harness poses them, and `stages.json` gives the file's number,
`file_stage: 3`, for stage 2.

## Q16. How the harness learns v at a commit stage

A reposed run "replays a commit as the information x = v, with the v
first selected", but nothing says how v reaches the harness.

**Implemented:** v is the commit stage's answer, from `answers(1)`,
verbatim. The harness passes that string back unchanged when it replays
the commit stage, and the program turns it into its information x = v.
The harness does not parse it. A system that selected nothing has
nothing replayed, and that is recorded. *Why:* anything else would have
the harness reconstruct an answer.

## Q17. Step counting in behaviour mode

Behaviour mode has "no instrumentation beyond the harness", but the
budget must be enforced, and in Python the budget and the step count are
the same `sys.monitoring` callback.

**Implemented:** the budget counter is part of the harness and runs in
every mode. Steps a behaviour run records incidentally are kept, but the
figures of record for steps come from the cost run (`README.md`,
section 8). Where a system harness's budget mechanism is itself the
instrumentation (Python), its README says so as a confound.

## Q18. What `print()` is

`PROTOCOL.md` lists `print()` among the operations without defining it.

**Implemented:** `print()` records the system's own rendering of what it
holds at the end of the stage, verbatim, distinct from `observe()`, which
records the state the observations need. The harness never reformats
either.

## Q19. Readings classified twice

P01c (finite and rational), P08 (closed and open) and P09d (P09d1 and
P09d2) are run once and classified under each of their readings. P15b and
P15b2 have one reading only, the stream reading of P09d2 with fairness
(problems/15 lines 25, 38–44), and `stages.json` lists that one.

**Implemented:** each is one instance and one run; `stages.json` lists
its readings; nothing in the harness depends on a reading.
