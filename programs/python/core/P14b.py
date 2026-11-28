# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core for P14b, written before any program was run
#   idioms:
#     - the stage loop, cp calls; a program that reads each stage as it
#       arrives is one computation, holding its state between stages:
#       harnesses/python/README.md, sections 2 ("Posing") and 3;
#       systems/python/README.md, "The same computation"
#     - the counter as a process holding its count (problems/14: "A program
#       may instead implement the counter as a process holding its count"),
#       the count an entry of a dict, replaced by assignment: The Python
#       Language Reference (3.13), "Assignment statements"; The Python
#       Library Reference, "Mapping Types -- dict"
#     - atoms as strings, a message READ(r) as the tuple ("read", r):
#       this configuration's earlier programs (programs/python/README.md,
#       batch 1B, "What the programs report")
#
# P14b. Messages as one sequence: one stage, in which the counter receives
# the sequence <INC, INC, READ(r1), INC, READ(r2)>. The counter takes the
# messages in their order, applying run's case for each to the count it holds
# (case 2 for INC, case 3 for READ(r)); after the last, the rest of the
# sequence is <>, for which case 1 holds and nothing is left to do.

# CONSTANTS BEGIN
# stage 1
MESSAGES = ("inc", "inc", ("read", "r1"), "inc", ("read", "r2"))
# CONSTANTS END

state = {"count": 0}    # the counter's count, 0 at first
known = {}              # the bindings: unknown -> value
failed = []             # messages for which no case of run holds

cp.bindings(known)
cp.held("the counter's state", state)
cp.held("messages for which no case of run holds", failed)


def run(message):
    """One application of run's cases, to the message received, with the
    count c the counter holds: run(<message> ++ s, c)."""
    if message == "inc":                                    # 2. run(<inc> ++ s, c) if run(s, c + 1)
        state["count"] = state["count"] + 1
    elif isinstance(message, tuple) and len(message) == 2 and message[0] == "read":
        r = message[1]                                      # 3. run(<read(r)> ++ s, c)
        if r not in known:                                  #    if r = c
            known[r] = state["count"]
        elif known[r] != state["count"]:
            failed.append(message)
    else:
        failed.append(message)                              # no case of run holds


cp.relations(run=run)


def report():
    if failed:
        print("no solution: no case of run holds for these messages:", failed)
    elif known:
        cp.answer(", ".join("%s = %d" % (r, v) for r, v in known.items()))


while (st := cp.stage()) is not None:
    if st.k == 1:
        for message in st.constants["MESSAGES"]:    # the messages, in the order they arrive;
            run(message)                            # 1. run(<>, c) after the last
    if not st.replay:
        report()
