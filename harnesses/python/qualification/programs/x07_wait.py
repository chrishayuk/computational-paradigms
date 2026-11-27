# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Library Reference (threading.Event)
# Made-up X07a (stdlib-concurrency): A waits for a signal that B never gives;
# B answers and returns. A is left blocked in a wait.
import threading

# CONSTANTS BEGIN
# stage 1
B_VALUE = 7
# CONSTANTS END

signal_given = threading.Event()
waiters = []
C = {}
cp.suspended("waiting for the signal", waiters)


def A():
    waiters.append("A")
    signal_given.wait()
    waiters.remove("A")
    cp.answer("w = from A")


def B():
    cp.answer("w = %d" % C["B_VALUE"])


cp.computation("A", A)
cp.computation("B", B)

while (s := cp.stage()) is not None:
    C.update(s.constants)
