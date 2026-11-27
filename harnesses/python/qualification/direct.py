"""Run a made-up qualification program directly, without the harness, and
print what it computed: the lines it printed per stage, its instructions per
stage, and the calls of its registered relations per stage.

    python3 -B -s -P direct.py PROGRAM K [n]

This is the comparison for qualification (a). It shares no code with
harnesses/python/run or runtime.py. Its `cp` is a stub that poses stages 1..K
in order (never replaying), gives each stage the constants its block tags
with it (read by this file's own parser), prints each answer with print(), and ignores the
registrations. Instructions are counted as systems/python/probes/meter.py
counts them (one global sys.monitoring INSTRUCTION callback, the meter's own
code excluded); relation calls as probes/p2_algops.py method C counts them
(PY_START, local events on the relations' code objects). Spawned
computations are run after main's part of their stage, one after another.
"""
import json
import sys

mon = sys.monitoring
E = mon.events
TOOL = 3
OWN = set()
count = [0]
ops = {}
RELS = {}


def cb(code, offset):
    if code in OWN:
        return mon.DISABLE
    count[0] += 1


def ps(code, offset):
    name = RELS.get(code)
    if name is not None:
        ops[name] = ops.get(name, 0) + 1


class Stage:
    def __init__(self, k, params, constants):
        self.k, self.replay, self.commitment, self.params = k, False, None, params
        self.constants = constants


def split_block(text):
    """Its own reading of the constants block (not harnesses/python/constants.py):
    one 'NAME = literal' per line under '# stage k' lines. Returns the text
    with the block's lines emptied, and {stage: {name: value}}."""
    import ast
    lines = text.split("\n")
    out, consts, inside, stage = [], {}, False, None
    for line in lines:
        st = line.strip()
        if st.startswith("#") and "CONSTANTS BEGIN" in st:
            inside = True
            out.append(line)
            continue
        if st.startswith("#") and "CONSTANTS END" in st:
            inside = False
            out.append(line)
            continue
        if inside:
            if st.startswith("#") and st[1:].strip().startswith("stage "):
                stage = int(st[1:].strip()[6:])
            elif "=" in st and not st.startswith("#"):
                name, val = st.split("=", 1)
                consts.setdefault(stage, {})[name.strip()] = ast.literal_eval(val.strip())
            out.append("")
        else:
            out.append(line)
    return "\n".join(out), consts


class Stub:
    def __init__(self, K, params):
        self.K, self.k, self.params = K, 0, params
        self.marks = []        # (stage, instruction count at its end, ops, stdout lines)
        self.comps = {}
        self.lines = []

    def _end_stage(self):
        if self.k:
            self.marks.append({"stage": self.k, "count": count[0], "ops": dict(ops), "answers": self.lines})
            self.lines = []
            spawns = SPAWNS.get(self.k, [])
            for name in spawns:
                c0 = count[0]
                self.comps[name]()
                self.marks[-1].setdefault("spawned", {})[name] = {"steps": count[0] - c0, "answers": self.lines}
                self.lines = []
            self.marks[-1]["count_after"] = count[0]

    def stage(self):
        self._end_stage()
        self.k += 1
        if self.k > self.K:
            return None
        return Stage(self.k, self.params, CONSTS.get(self.k, {}))

    def answer(self, value):
        text = value if type(value) is str else str(value)
        print(text)
        self.lines.append(text)

    def emit(self, m):
        pass

    def relations(self, **fns):
        for name, fn in fns.items():
            RELS[fn.__code__] = name
            mon.set_local_events(TOOL, fn.__code__, E.PY_START)

    def computation(self, name, fn):
        self.comps[name] = fn

    def bindings(self, *a):
        pass

    pending = suspended = held = problem_alternatives = lambda self, *a: None


SPAWNS = {}
CONSTS = {}


def main():
    prog, K = sys.argv[1], int(sys.argv[2])
    params = {"n": int(sys.argv[3])} if len(sys.argv) > 3 else {}
    if len(sys.argv) > 4:
        SPAWNS[1] = sys.argv[4].split(",")
    for obj in list(globals().values()) + list(vars(Stub).values()) + list(vars(Stage).values()):
        code = getattr(obj, "__code__", None)
        if code is not None:
            OWN.add(code)
    OWN.add(main.__code__)
    text, consts = split_block(open(prog, encoding="utf-8").read())
    CONSTS.update(consts)
    code = compile(text, prog, "exec", dont_inherit=True)
    stub = Stub(K, params)
    g = {"__name__": "__main__", "__file__": prog, "cp": stub}
    mon.use_tool_id(TOOL, "direct")
    mon.register_callback(TOOL, E.INSTRUCTION, cb)
    mon.register_callback(TOOL, E.PY_START, ps)
    mon.set_events(TOOL, E.INSTRUCTION)
    exec(code, g)
    mon.set_events(TOOL, 0)
    out, prev, prev_ops = [], 0, {}
    for m in stub.marks:
        d = {"stage": m["stage"], "steps": m["count"] - prev, "answers": m["answers"],
             "ops": {k: v - prev_ops.get(k, 0) for k, v in m["ops"].items() if v - prev_ops.get(k, 0)}}
        if "spawned" in m:
            d["spawned"] = m["spawned"]
        out.append(d)
        prev, prev_ops = m.get("count_after", m["count"]), m["ops"]
    sys.stderr.write("DIRECT " + json.dumps(out) + "\n")


main()
