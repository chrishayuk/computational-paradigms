# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P15d, written before any program was run
#   idioms:
#     - the stage loop, cp calls; a program that reads each stage as it
#       arrives is one computation: harnesses/python/README.md, sections 2
#       ("Posing") and 3
#     - named quantities as entries of a dict, a replacing stage as
#       assignment: The Python Language Reference (3.13), "Assignment
#       statements"; this configuration's P10 programs
#     - a request as a thread of its own that, when the resource is held,
#       queues itself and waits on a condition variable until it is
#       granted; a release notifies the waiting threads: The Python Library
#       Reference (3.13), "threading -- Thread-based parallelism": "Thread
#       Objects" (daemon threads), "Condition Objects" (wait_for,
#       notify_all, the with statement on a condition, and its example of a
#       consumer waiting for an item); the count of busy threads and the wait
#       for none (settle) as this configuration's P02, P08 and P09c programs
#     - the queue as a tuple; atoms as strings, shown with a leading quote;
#       none as None: The Python Tutorial, "Tuples and Sequences"; this
#       configuration's earlier programs (programs/python/README.md, batch
#       1B)
#
# P15d. Three replacing stages: <atom> requests, <atom> requests, <atom>
# releases. holder and queue are named quantities, starting as none and <>.
# Each request is a thread of its own: it makes the replacement the
# problem's case gives (holder becomes p if there is none, otherwise queue
# becomes queue ++ <p>), and, if it was queued, waits until it is the
# holder. A release, posed by the main thread, makes its replacement (holder
# becomes none, or the head of the queue, and queue its tail) and wakes the
# waiting requests; the one now granted ends its wait. So B's waiting is held
# as a thread blocked on the condition, and stage 3 resumes it. A grant is
# never withdrawn by a later request. A release by anyone but the holder is
# outside the definition: recorded, and it changes nothing. External
# mechanism: threading.

import threading

# CONSTANTS BEGIN
# stage 1
REQUESTER = "a"
# stage 2
REQUESTER = "b"
# stage 3
RELEASER = "a"
# CONSTANTS END

changed = threading.Condition()             # guards everything below; notified at every change
state = {"holder": None, "queue": ()}       # the named quantities: none and <> at first
waiting = []                                # requesters whose threads wait to be granted
failed = []                                 # releases outside the definition
count = {"busy": 0}                         # request threads not waiting

cp.bindings(state)
cp.suspended("requests waiting in their threads to be granted", waiting)
cp.held("releases by one who is not the holder", failed)


def request(p):
    """p requests, in a thread of its own: if holder = none, holder becomes
    p; otherwise queue becomes queue ++ <p>, and the thread waits until p is
    the holder."""
    with changed:
        if state["holder"] is None:
            state["holder"] = p
        else:
            state["queue"] = state["queue"] + (p,)
            waiting.append(p)
            count["busy"] -= 1
            changed.notify_all()
            changed.wait_for(lambda: state["holder"] == p)
            waiting.remove(p)
        count["busy"] -= 1
        changed.notify_all()


def release(p):
    """p releases, where holder = p: if queue = <>, holder becomes none;
    otherwise, with queue = <h> ++ t, holder becomes h and queue becomes t.
    The request granted, if its thread waits, is counted busy again and
    woken."""
    with changed:
        if state["holder"] != p:
            failed.append(("release", p))
        elif state["queue"] == ():
            state["holder"] = None
        else:
            state["holder"], state["queue"] = state["queue"][0], state["queue"][1:]
            if state["holder"] in waiting:
                count["busy"] += 1
        changed.notify_all()


cp.relations(request=request, release=release)


def pose(p):
    """A request arrives: give it its own thread."""
    with changed:
        count["busy"] += 1
    threading.Thread(target=request, args=(p,), daemon=True).start()


def settle():
    """Wait until no request thread is busy."""
    with changed:
        changed.wait_for(lambda: count["busy"] == 0)


def atom(x):
    """Output adapter: an atom with a leading quote, none as none."""
    return "none" if x is None else "'" + x


def report():
    with changed:
        if failed:
            print("no solution: released by one who is not the holder:", failed)
        else:
            cp.answer("holder = %s, queue = ⟨%s⟩" % (atom(state["holder"]), ",".join(atom(p) for p in state["queue"])))


while (st := cp.stage()) is not None:
    if st.k == 1:
        pose(st.constants["REQUESTER"])
    elif st.k == 2:
        pose(st.constants["REQUESTER"])
    elif st.k == 3:
        release(st.constants["RELEASER"])
    settle()
    if not st.replay:
        report()
