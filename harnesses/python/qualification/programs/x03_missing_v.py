# CP-POSING: incremental
# PROVENANCE: author harness-python (agent), qualification only; precursor seen: no; idioms: Python Language Reference
# Made-up X03a: two computations U and V, spawned by the harness, each counting
# to its own limit and printing every multiple of STEP it passes.

# CONSTANTS BEGIN
# stage 1
U_TO = 30
V_TO = 20
STEP = 10
# CONSTANTS END

trace = []
C = {}            # the constants, once stage 1 has delivered them
cp.held("trace", trace)


def count(name, to):
    i = 0
    while i < to:
        i += 1
        if i % C["STEP"] == 0:
            trace.append((name, i))
            cp.answer("%s = %d" % (name, i))


def U():
    count("u", C["U_TO"])


def V():
    count("v", C["V_TO"])


cp.computation("U", U)

while (s := cp.stage()) is not None:
    C.update(s.constants)
