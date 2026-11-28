# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P15c, written before any program was run
#   idioms:
#     - the stage loop, cp calls: harnesses/python/README.md, sections 3 and 8
#     - one resource as a lock, two requests at once as two threads, each
#       trying to acquire it without blocking; the one that acquires it is
#       granted, and the lock is not released, so the grant is not revisited:
#       The Python Library Reference (3.13), "threading -- Thread-based
#       parallelism": "Lock Objects" (acquire(blocking=False) returns
#       whether the lock was acquired), "Thread Objects" (start, join)
#     - atoms as strings, shown with a leading quote: this configuration's
#       earlier programs (programs/python/README.md, batch 1B)
#
# P15c. One stage: grant(<atom>, <atom>, g), any one.
# grant's two facts are the two requests, from p (fact 1) and from q (fact
# 2), each made by a thread of its own; the threads are started together,
# p's first, and the one that acquires the resource's lock is granted: g is
# its requester. Which one acquires it is decided by the threads'
# scheduling, not by the program. The lock is never released: the choice is
# committed. The main thread waits for both requests, then reports.
# External mechanism: threading.

import threading

# CONSTANTS BEGIN
# stage 1
FIRST = "a"
SECOND = "b"
# CONSTANTS END

resource = threading.Lock()     # the one resource: held by the request granted
known = {}                      # the bindings: unknown -> value
cp.bindings(known)


def request(p):
    """A request for the resource, from p, in a thread of its own: granted
    if it acquires the resource, and then never released."""
    if resource.acquire(blocking=False):
        known["g"] = p


def grant(p, q):
    """grant(p, q, g): the two requests made at once, one thread each (fact
    1, from p; fact 2, from q); g is the requester that acquired the
    resource."""
    requests = [threading.Thread(target=request, args=(p,)),    # 1. grant(p, q, p)
                threading.Thread(target=request, args=(q,))]    # 2. grant(p, q, q)
    for t in requests:
        t.start()
    for t in requests:
        t.join()
    return known.get("g")


cp.relations(grant=grant)

while (st := cp.stage()) is not None:
    if st.k == 1:
        g = grant(st.constants["FIRST"], st.constants["SECOND"])    # any one
        if not st.replay:
            cp.answer("g = '%s" % g)
