# P02. Late information -- Python, configuration "core".
#
# A held-out calibration program (a development example, not a result).
# Author: Claude (Opus 5.5), as an agent.  Written from
# problems/02-late-information.md.  The author has not seen any precursor
# program (the absys experiments E01-E09) or any other program written for
# this study.
#
# Standard library: none.  No imports.
#
# How the program is laid out, for the classifiers:
#   1. THE STAGE CONSTANTS: the one marked place (PROTOCOL.md, rule 6).
#   2. The three relations, R1, R2 and R3, each a function of its own.
#      Each transcribes one relation of the problem, in every direction the
#      stages need, deciding it from whatever is already known.
#   3. The computation: the unknowns known so far, and the relations held
#      until they can be decided.  When a stage arrives, its relations are
#      added and every held relation is taken up again.  This is the part
#      the problem probes, and it is written for this problem's relations
#      only (not a general constraint store).
#   4. A reformulation used only for the report: R1 and R2 together have
#      finitely many integer solutions, which are enumerated.
#   5. Output adapters and a stand-in for the harness (pose, print), which
#      poses P02a, the six orders of P02b, and P02c.
#
# What the program reports after each stage (SPECIFICATION.md, Outcomes):
#   - the unknowns bound, and those still free;
#   - the relations still held, with known values put in (a residual,
#     read from the program's own state, which the next stage acts on);
#   - where the held relations are R1 and R2 alone, with nothing known,
#     the solutions as values (explicit), since there are finitely many;
#   - "no solutions" where a relation fails.
# So an infinite outcome is reported as bindings plus held relations
# (solved form where nothing is held, residual otherwise).


# ---------------------------------------------------------------------------
# 1. THE STAGE CONSTANTS (the one place a verifier changes them)
# ---------------------------------------------------------------------------
# R1: u + v = R1_SUM
# R2: w * u = v                 (R2 has no constants)
# R3: u + R3_ADDEND = R3_SUM
R1_SUM = 16
R3_ADDEND = 10
R3_SUM = 12
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 2. The relations.  Each takes the unknowns known so far (a dict from the
#    names "u", "v", "w" to integers) and returns a verdict:
#       ("bind", name, value)  the relation determines this unknown
#       ("holds",)             the relation is true for every value of the
#                              unknowns it still has: it is decided
#       ("fails",)             the relation is false: no solutions
#       ("waits", names)       it cannot be decided yet; these unknowns are
#                              what it waits for
#    The problem states each as a relation, with any place unknown, so each
#    branch below is one direction of it; no direction is left out.
# ---------------------------------------------------------------------------

def r1(known):
    """R1: u + v = R1_SUM."""
    if "u" in known and "v" in known:
        return ("holds",) if known["u"] + known["v"] == R1_SUM else ("fails",)
    if "u" in known:
        return ("bind", "v", R1_SUM - known["u"])
    if "v" in known:
        return ("bind", "u", R1_SUM - known["v"])
    return ("waits", ("u", "v"))


def r2(known):
    """R2: w * u = v."""
    if "w" in known and "u" in known and "v" in known:
        return ("holds",) if known["w"] * known["u"] == known["v"] else ("fails",)
    if "w" in known and "u" in known:
        return ("bind", "v", known["w"] * known["u"])
    if "u" in known and "v" in known:
        u, v = known["u"], known["v"]
        if u == 0:
            # 0 * w = v: true for every w if v = 0, else false.
            return ("holds",) if v == 0 else ("fails",)
        if v % u == 0:
            return ("bind", "w", v // u)
        return ("fails",)               # w would not be an integer
    if "w" in known and "v" in known:
        w, v = known["w"], known["v"]
        if w == 0:
            return ("holds",) if v == 0 else ("fails",)
        if v % w == 0:
            return ("bind", "u", v // w)
        return ("fails",)
    if "u" in known and known["u"] == 0:
        return ("bind", "v", 0)         # w * 0 = v, so v = 0
    if "w" in known and known["w"] == 0:
        return ("bind", "v", 0)         # 0 * u = v, so v = 0
    return ("waits", tuple(x for x in ("w", "u", "v") if x not in known))


def r3(known):
    """R3: u + R3_ADDEND = R3_SUM."""
    if "u" in known:
        return ("holds",) if known["u"] + R3_ADDEND == R3_SUM else ("fails",)
    return ("bind", "u", R3_SUM - R3_ADDEND)


RELATIONS = {"R1": r1, "R2": r2, "R3": r3}


# ---------------------------------------------------------------------------
# 3. The computation, and taking up held relations when information arrives.
#    Reformulation: Python has no unknowns and no suspended relations, so the
#    program keeps them itself: `known` for the unknowns that have values,
#    `held` for the relations not yet decided, in the order they arrived,
#    and `waits` for what each held relation is waiting for.
# ---------------------------------------------------------------------------

def new_computation():
    return {"known": {}, "held": [], "waits": {}, "failed": False,
            "trace": [], "examined": {}}


def resume(comp):
    """Take up every held relation again, in arrival order, until a whole
    pass decides nothing new (a fixpoint)."""
    progress = True
    while progress and not comp["failed"]:
        progress = False
        for name in list(comp["held"]):
            verdict = RELATIONS[name](comp["known"])
            comp["examined"][name] = comp["examined"].get(name, 0) + 1
            note_trace(comp, name, verdict)
            if verdict[0] == "bind":
                comp["known"][verdict[1]] = verdict[2]
                progress = True
            elif verdict[0] == "holds":
                comp["held"].remove(name)
                comp["waits"].pop(name, None)
                progress = True
            elif verdict[0] == "fails":
                comp["failed"] = True
                break
            else:
                comp["waits"][name] = verdict[1]


def take(comp, names):
    """A stage arrives: its relations join the held ones, and all are taken
    up again in the same computation."""
    comp["trace"] = []
    comp["examined"] = {}
    for name in names:
        comp["held"].append(name)
    resume(comp)


# ---------------------------------------------------------------------------
# 4. Reformulation, for the report only.  R1 and R2 held together, with u,
#    v and w all unknown: by R1, v = R1_SUM - u; put in R2, w*u = R1_SUM - u,
#    so u * (w + 1) = R1_SUM.  If R1_SUM is not 0, u must divide it, and
#    each divisor d gives one solution: u = d, v = R1_SUM - d,
#    w = R1_SUM / d - 1.  If R1_SUM is 0 there are infinitely many, and the
#    relations are left as the residual.  This derivation is not in the
#    problem file; it is how a Python programmer gets the finite answer.
# ---------------------------------------------------------------------------

def r1_and_r2_solutions(known):
    if R1_SUM == 0 or known:
        return None
    solutions = []
    for d in range(1, abs(R1_SUM) + 1):
        if R1_SUM % d == 0:
            for u in (d, -d):
                solutions.append((u, R1_SUM - u, R1_SUM // u - 1))
    return solutions


# ---------------------------------------------------------------------------
# 5. Output adapters and the stand-in for the harness.
# ---------------------------------------------------------------------------

def show_relation(name, known):
    """Print a held relation with the known values put in."""
    def val(x):
        return str(known[x]) if x in known else x
    if name == "R1":
        return "%s + %s = %d" % (val("u"), val("v"), R1_SUM)
    if name == "R2":
        return "%s * %s = %s" % (val("w"), val("u"), val("v"))
    return "%s + %d = %d" % (val("u"), R3_ADDEND, R3_SUM)


def note_trace(comp, name, verdict):
    if verdict[0] == "bind":
        comp["trace"].append("%s binds %s = %d" % (name, verdict[1], verdict[2]))
    elif verdict[0] == "holds":
        comp["trace"].append("%s decided" % name)
    elif verdict[0] == "fails":
        comp["trace"].append("%s fails" % name)
    else:
        comp["trace"].append("%s waits on %s" % (name, ", ".join(verdict[1])))


def report(comp, label):
    print(label)
    print("  trace:    " + "; ".join(comp["trace"]))
    print("  examined: " + ", ".join("%s %d" % (n, comp["examined"][n])
                                     for n in sorted(comp["examined"])))
    if comp["failed"]:
        print("  outcome:  no solutions")
        return
    known = comp["known"]
    bound = ", ".join("%s = %d" % (x, known[x]) for x in ("u", "v", "w") if x in known)
    free = ", ".join(x for x in ("u", "v", "w") if x not in known)
    print("  bound:    " + (bound or "none"))
    print("  unbound:  " + (free or "none"))
    if not comp["held"]:
        print("  held:     none")
        print("  outcome:  " + ("solved form" if free else "explicit")
              + (" (" + free + " free)" if free else ""))
        return
    for name in comp["held"]:
        print("  held:     %s: %s   waits on %s"
              % (name, show_relation(name, known), ", ".join(comp["waits"][name])))
    solutions = None
    if sorted(comp["held"]) == ["R1", "R2"]:
        solutions = r1_and_r2_solutions(known)
    if solutions is None:
        print("  outcome:  residual (the held relations above)")
    else:
        print("  outcome:  explicit, %d solutions (u, v, w):" % len(solutions))
        for s in solutions:
            print("            (%d, %d, %d)" % s)


def run(label, stages):
    comp = new_computation()
    for k, names in enumerate(stages, 1):
        take(comp, names)
        report(comp, "%s stage %d: %s" % (label, k, ", ".join(names)))
    print()


run("P02a", [["R1"], ["R2"], ["R3"]])

for order in (("R1", "R2", "R3"), ("R1", "R3", "R2"), ("R2", "R1", "R3"),
              ("R2", "R3", "R1"), ("R3", "R1", "R2"), ("R3", "R2", "R1")):
    run("P02b " + " ".join(order), [[name] for name in order])

run("P02c", [["R1", "R2", "R3"]])
