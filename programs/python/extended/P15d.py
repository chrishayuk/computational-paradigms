# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of core and of extended for P15d (one text, the same
#   file in both folders), written before any program was run
#   idioms:
#     - the stage loop, cp calls; a program that reads each stage as it
#       arrives is one computation, holding its state between stages:
#       harnesses/python/README.md, sections 2 ("Posing") and 3
#     - named quantities as entries of a dict, a replacing stage as
#       assignment (the right-hand side evaluated from the values before the
#       stage): The Python Language Reference (3.13), "Assignment
#       statements"; this configuration's P10 programs
#     - the queue as a tuple: + to add at its end, [0] and [1:] for its head
#       and tail: The Python Tutorial, "Tuples and Sequences"
#     - atoms as strings, shown with a leading quote; none as None: this
#       configuration's earlier programs (programs/python/README.md, batch
#       1B); The Python Library Reference, "Built-in Constants" (None)
#
# P15d. Three replacing stages: <atom> requests, <atom> requests, <atom>
# releases. holder and queue are named quantities, starting as none and <>.
# Each stage is one replacement, by the problem's cases: a request makes the
# requester the holder if there is none, and otherwise puts it at the end of
# the queue; a release by the holder passes the resource to the head of the
# queue, or leaves it with none. A grant is never withdrawn by a later
# request. A release by anyone but the holder is outside the definition
# ("where holder = p"): it is recorded as not holding, and changes nothing.

# CONSTANTS BEGIN
# stage 1
REQUESTER = "a"
# stage 2
REQUESTER = "b"
# stage 3
RELEASER = "a"
# CONSTANTS END

state = {"holder": None, "queue": ()}       # the named quantities: none and <> at first
failed = []                                 # releases outside the definition

cp.bindings(state)
cp.held("releases by one who is not the holder", failed)


def request(p):
    """p requests: if holder = none, holder becomes p; otherwise queue
    becomes queue ++ <p>."""
    if state["holder"] is None:
        state["holder"] = p
    else:
        state["queue"] = state["queue"] + (p,)


def release(p):
    """p releases, where holder = p: if queue = <>, holder becomes none;
    otherwise, with queue = <h> ++ t, holder becomes h and queue becomes t."""
    if state["holder"] != p:
        failed.append(("release", p))
    elif state["queue"] == ():
        state["holder"] = None
    else:
        state["holder"], state["queue"] = state["queue"][0], state["queue"][1:]


cp.relations(request=request, release=release)


def atom(x):
    """Output adapter: an atom with a leading quote, none as none."""
    return "none" if x is None else "'" + x


def report():
    if failed:
        print("no solution: released by one who is not the holder:", failed)
    else:
        cp.answer("holder = %s, queue = ⟨%s⟩" % (atom(state["holder"]), ",".join(atom(p) for p in state["queue"])))


while (st := cp.stage()) is not None:
    if st.k == 1:
        request(st.constants["REQUESTER"])
    elif st.k == 2:
        request(st.constants["REQUESTER"])
    elif st.k == 3:
        release(st.constants["RELEASER"])
    if not st.replay:
        report()
