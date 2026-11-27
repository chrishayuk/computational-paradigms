# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no;
#   idioms: Python Library Reference (os.open, os.path.exists)
# Made-up X10a: each stage's constant is a distinctive string. At each stage the
# program says it is ready (a file) and spins until qualify.py, having scanned
# this process's whole memory from outside, lets it go on (another file).
import os

# CONSTANTS BEGIN
# stage 1
EARLY = "QZ-EARLY-STAGE-CONSTANT-1180"
# stage 2
LATER = "QZ-LATER-STAGE-CONSTANT-5521"
# CONSTANTS END

held = {}
cp.bindings(held)

while (s := cp.stage()) is not None:
    held.update(s.constants)
    os.close(os.open("/tmp/cpq-ready-%d" % s.k, os.O_CREAT | os.O_WRONLY))
    while not os.path.exists("/tmp/cpq-go-%d" % s.k):
        pass
    cp.answer(", ".join(sorted(held)))
