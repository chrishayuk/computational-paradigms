# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of stdlib-concurrency for P14c, written before any program was run
#   idioms:
#     - the stage loop, cp calls; a program that reads each stage as it
#       arrives is one computation: harnesses/python/README.md, sections 2
#       ("Posing") and 3; systems/python/README.md, "The same computation"
#     - the counter as a process holding its count (problems/14: "A program
#       may instead implement the counter as a process holding its count"):
#       a daemon thread that takes its messages from a queue in the order
#       they arrive, the sender waiting with join() until each message has
#       been received (task_done): The Python Library Reference (3.13),
#       "queue -- A synchronized queue class" (Queue.get, put, task_done,
#       join, and its example of a worker thread), "threading --
#       Thread-based parallelism", "Thread Objects" (daemon threads)
#     - atoms as strings, a message READ(r) as the tuple ("read", r): this
#       configuration's earlier programs (programs/python/README.md, batch
#       1B, "What the programs report")
#
# P14c. A stream that stays open: the stages of P14a, then INC and READ(r3);
# no stage closes the stream. One message per stage. The counter is a thread
# of its own, started once, holding its count between messages; each stage's
# message is sent to it through its queue (its inbox), and it applies run's
# case for that message (case 2 for INC, case 3 for READ(r)) when it receives
# it. The main thread waits until the message has been received, then
# reports. Between messages the counter's thread waits on its inbox
# (registered as suspended). External mechanisms: threading, queue.

import queue
import threading

# CONSTANTS BEGIN
# stage 1
MESSAGE = "inc"
# stage 2
MESSAGE = "inc"
# stage 3
MESSAGE = ("read", "r1")
# stage 4
MESSAGE = "inc"
# stage 5
MESSAGE = ("read", "r2")
# stage 6
MESSAGE = "inc"
# stage 7
MESSAGE = ("read", "r3")
# CONSTANTS END

END = None              # the end of the stream: the rest of the messages is <>
inbox = queue.Queue()   # the messages sent to the counter and not yet received
state = {"count": 0}    # the counter's count, 0 at first
known = {}              # the bindings: unknown -> value
failed = []             # messages for which no case of run holds
processes = []          # the counter's thread, while it waits for messages

cp.bindings(known)
cp.held("the counter's state", state)
cp.suspended("counter processes waiting for messages", processes)
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


def counter():
    """The counter, as a process: it receives its messages one at a time,
    in the order they arrive, and applies run to each; the end of the
    stream ends it."""
    while True:
        message = inbox.get()
        if message is END:                                  # 1. run(<>, c)
            processes.clear()
            inbox.task_done()
            return
        run(message)
        inbox.task_done()


def send(message):
    """Send a message to the counter, and wait until it has received it."""
    inbox.put(message)
    inbox.join()


def report():
    if failed:
        print("no solution: no case of run holds for these messages:", failed)
    elif known:
        cp.answer(", ".join("%s = %d" % (r, v) for r, v in known.items()))


process = threading.Thread(target=counter, name="counter", daemon=True)
processes.append(process)
process.start()

while (st := cp.stage()) is not None:
    send(st.constants["MESSAGE"])       # every stage is one message, sent as it arrives
    if not st.replay:
        report()
