#!/usr/bin/env python3
"""The Absys harness: the code behind harnesses/absys/run and harnesses/absys/check.

Runs inside the pinned image (cp-agent-systems:spec-1.0), with its python3
(3.11, standard library only) and the pinned builds in /usr/local/bin.
What it does, and every way in which it does more than pass stages in,
collect answers and read state, is in harnesses/absys/README.md.
"""

import datetime
import hashlib
import json
import os
import queue
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DEFAULT_STAGES = os.path.join(REPO, "harnesses", "stages.json")
VALIDATE = os.path.join(REPO, "harnesses", "validate.py")

BIN = "/usr/local/bin/absys-measure"        # branch measure, 5450449: --measure and --full
BASELINE_BIN = "/usr/local/bin/absys"       # main, efd5203: the behavioural reference
COMMITS_FILE = "/opt/src/COMMITS"

CONFIGS = {
    "absys": [],
    "absys-depth-first": ["--search", "depth-first"],
    "absys-wake-back": ["--wake", "back"],
}
HELD_AS = {"absys": "all-live", "absys-depth-first": "mixed", "absys-wake-back": "all-live"}
MODES = ("behaviour", "cost", "storage")
STEP_UNIT = "step"
ALT_UNIT = "derivation"
MEASURE_FIELDS = ["derivations", "sub_derivations", "variables", "bindings", "susp_equations",
                  "susp_applications", "susp_relations", "susp_negations", "pending", "term_nodes"]
SUSP_FIELDS = ["susp_equations", "susp_applications", "susp_relations", "susp_negations"]

# The repl's reply to `.help`, byte for byte (src/main.rs, REPL_HELP). The harness sends `.help`
# after each section it feeds, and this reply marks where the system's output for the section ends.
REPL_HELP = (
    "Type assertions; each is added to every derivation, and whatever can be done is done.\n"
    "  ?          the state: every derivation, what it knows and what is suspended\n"
    "  ? X        the value of X in each derivation\n"
    "  .env       the state, with each derivation's whole binding environment\n"
    "  .trace     show every step from now on (.trace off to stop)\n"
    "  .help      this\n"
    "  .quit      end (or end of input)\n"
)
HELP_B = REPL_HELP.encode()
# When a section ends inside an unfinished assertion, the repl reads the `.help` line as the
# assertion's continuation and replies with this syntax error instead (the `.` at column 1).
EATEN_B = re.compile(rb"(?m)^error at \d+:1: `\.` is not in the (?:1969 )?notation[^\n]*\n")

CONFOUNDS = [
    "behaviour runs use the instrumented build absys-measure (branch measure, 5450449) with --full and without --measure, not the baseline absys (efd5203), so that every list and derivation is printed in full (systems/absys/README.md, Output); --full changes only the printer",
    "in behaviour runs the harness writes each section of the program to `absys-measure repl` on standard input, line by line as the program file has it, and after each section a `.help` line, whose fixed reply marks where the system's output for the section ends; a section that ends inside an unfinished assertion makes the repl read `.help` as its continuation and report a syntax error",
    "the state is read with the repl's own commands `?` and `? NAME` after a stage (and after each spawned computation's section); they read the state and change nothing",
    "instance parameters that a program declares (% PARAMETERS) are given to the system as assertions `NAME = VALUE` written by the harness in the program's notation, before the prelude",
    "a program written in PART sections has part order[k-1] fed at stage k, as the instance's order names it",
    "spawn(): Absys has one computation per session; a spawned computation's section is accepted into it, after the previous one has run to its end or its budget (side_by_side false), and that computation's answers and state are read right after its section",
    "the budget is the system's own, --steps, which counts per assertion: a stage of several assertions can take more than the problem's budget in all before the system reports budget",
    "cost and storage runs read steps and store from --measure, which reports them only for a whole text: each stage k of such a run is a new process on the text of the prelude and stages 1 to k, so those records show reposed stages, with the steps of stages 1 to k-1 as restart cost; the incremental behaviour run does not pay it",
    "the restart cost of a reposed stage in a behaviour run (after an error or a safety-limit stop) is measured on a separate run of the replayed text with `absys-measure json`, which reports the steps of each assertion without sampling the store",
    "in P11 runs (and in cost runs with the default budget) the system's trace is switched on (`.trace`, --trace), to read when tout performs an output; printing the trace changes nothing the machine does",
    "answers(cap) takes the first cap derivations of the system's printed state, in the system's order; every derivation is in observe.raw",
    "the constants block is never given to the system: the harness replaces each constant's name, in the text of the section that uses it, by its value, when that section is given",
]


# ------------------------------------------------------------------ util ---

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%S") + ".%03dZ" % (t.microsecond // 1000)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def decode(b, faults, what):
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        faults.append("%s was not valid UTF-8; invalid bytes are written as U+FFFD" % what)
        return b.decode("utf-8", errors="replace")


def relpath(p):
    ap = os.path.abspath(p)
    if ap.startswith(REPO + os.sep):
        return os.path.relpath(ap, REPO)
    return ap


def git(*args):
    try:
        r = subprocess.run(["git", "-c", "safe.directory=*", "-C", REPO] + list(args),
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def notation_of(path):
    """The system's own rule (src/session.rs, notation_for): .ab1 is 1969, .ab2 1982, else 1990."""
    if path.endswith(".ab1"):
        return "1969"
    if path.endswith(".ab2"):
        return "1982"
    return "1990"


EXT = {"1990": "abs", "1969": "ab1", "1982": "ab2"}


def signal_name(status):
    if status is not None and status < 0:
        try:
            return signal.Signals(-status).name
        except ValueError:
            return "signal %d" % -status
    return None


# -------------------------------------------------------------- stages ---

def load_stages(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    idx = {}
    for prob in doc["problems"]:
        for sub in prob["subproblems"]:
            for inst in sub["instances"]:
                idx[inst["id"]] = (prob, sub, inst)
    return doc, idx


def problem_limits(doc, prob):
    lim = dict(doc.get("default_limits", {}))
    lim.update(prob.get("limits", {}))
    return lim


def query_cap(q, inst):
    return q["cap"] if q.get("cap") is not None else inst.get("parameters", {}).get("cap")


# ------------------------------------------------------------- program ---

MARK_STAGE = re.compile(r"^\s*%\s*STAGE\s+(\d+)\s*$")
MARK_PART = re.compile(r"^\s*%\s*PART\s+(\S+)\s*$")
MARK_SPAWN = re.compile(r"^\s*%\s*SPAWN\s+(\S+)\s*$")
MARK_PARAMS = re.compile(r"^\s*%\s*PARAMETERS\b(.*)$")
MARK_CB = re.compile(r"^\s*%.*\bCONSTANTS BEGIN\b")
MARK_CE = re.compile(r"^\s*%.*\bCONSTANTS END\b")
PARAM_NAMES = ("n", "order", "answers", "cap", "spawn_order")


class Program:
    """The program's sections, found by reading its bytes and nothing else."""

    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.raw = f.read()
        self.text = self.raw.decode("utf-8", errors="replace")
        self.notation = notation_of(path)
        self.lines = self.text.splitlines(keepends=True)
        if self.lines and not self.lines[-1].endswith("\n"):
            self.lines[-1] += "\n"
        self.prelude = []          # [(lineno, text)]
        self.stages = {}           # k -> [(lineno, text)]
        self.parts = {}            # name -> [(lineno, text)]
        self.params = []
        self.constants = None      # (begin, end) line numbers, 1-based
        self.problems = []
        cur = self.prelude
        cb = ce = None
        for i, line in enumerate(self.lines, 1):
            m = MARK_STAGE.match(line)
            p = MARK_PART.match(line)
            if m:
                k = int(m.group(1))
                if k in self.stages:
                    self.problems.append("line %d: a second section for stage %d" % (i, k))
                cur = self.stages.setdefault(k, [])
            elif p:
                if p.group(1) in self.parts:
                    self.problems.append("line %d: a second section for part %s" % (i, p.group(1)))
                cur = self.parts.setdefault(p.group(1), [])
            mp = MARK_PARAMS.match(line)
            if mp:
                if cur is not self.prelude:
                    self.problems.append("line %d: % PARAMETERS must be in the prelude" % i)
                for name in mp.group(1).split():
                    if name not in PARAM_NAMES:
                        self.problems.append("line %d: %r is not an instance parameter (%s)" % (i, name, ", ".join(PARAM_NAMES)))
                    elif name not in self.params:
                        self.params.append(name)
            if MARK_CB.match(line):
                if cb is not None:
                    self.problems.append("line %d: a second CONSTANTS BEGIN" % i)
                cb = i
                if cur is not self.prelude:
                    self.problems.append("line %d: the constants block must be in the prelude" % i)
            if MARK_CE.match(line):
                if ce is not None:
                    self.problems.append("line %d: a second CONSTANTS END" % i)
                ce = i
                if cur is not self.prelude:
                    self.problems.append("line %d: the constants block must be in the prelude" % i)
            cur.append((i, line))
        if (cb is None) != (ce is None) or (cb is not None and ce < cb):
            self.problems.append("the constants block needs one CONSTANTS BEGIN line and, after it, one CONSTANTS END line")
        elif cb is not None:
            self.constants = (cb, ce)
        if self.stages and self.parts:
            self.problems.append("a program has STAGE sections or PART sections, not both")
        # The constants block is a table, never given to the system: each name in it is replaced,
        # in the text of the section that uses it, by its value, when that section is given.
        self.table = {}
        if self.constants:
            cb, ce = self.constants
            for (i, line) in self.prelude:
                if cb < i < ce:
                    t = line.strip()
                    if not t or t.startswith("%"):
                        continue
                    m = CONST_LINE.match(t)
                    if not m:
                        self.problems.append("line %d: a line of the constants block must be NAME = VALUE: %s" % (i, t))
                    elif m.group(1) in self.table:
                        self.problems.append("line %d: %s is given twice in the constants block" % (i, m.group(1)))
                    else:
                        self.table[m.group(1)] = m.group(2).strip()
            self.prelude = [(i, l) for (i, l) in self.prelude if not (cb <= i <= ce)]
        if self.table:
            self.prelude = [(i, substitute(l, self.table)) for (i, l) in self.prelude]
            for d in (self.stages, self.parts):
                for key in d:
                    d[key] = [(i, substitute(l, self.table)) for (i, l) in d[key]]

    def section(self, k, inst):
        """The lines of stage k's section: stage k, or the part the instance's order names."""
        if self.parts:
            order = inst.get("parameters", {}).get("order")
            if not order or k > len(order):
                return None, "the program is written in PART sections, but the instance's order names no part for stage %d" % k
            name = order[k - 1]
            if name not in self.parts:
                return None, "the program has no PART %s, which the instance's order names for stage %d" % (name, k)
            return self.parts[name], None
        if k not in self.stages:
            return None, "the program has no section for stage %d" % k
        return self.stages[k], None


CONST_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*(?:-[A-Za-z][A-Za-z0-9_]*)*)\s*=\s*(\S.*?)\s*(?:%.*)?$")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:-[A-Za-z][A-Za-z0-9_]*)*'?")


def substitute(line, table):
    """The line with every identifier that names a constant replaced by the constant's value.
    Quoted constants ('...', "...") and comments (% to the end of the line) are left alone, and
    so is a name with a prime (1969: a new local name)."""
    out, i, n = [], 0, len(line)
    while i < n:
        c = line[i]
        if c == "%":
            out.append(line[i:])
            break
        if c in "'\"":
            j = line.find(c, i + 1)
            j = n - 1 if j < 0 else j
            out.append(line[i:j + 1])
            i = j + 1
            continue
        m = IDENT.match(line, i) if (c.isalpha() or c == "_") and (i == 0 or not (line[i - 1].isalnum() or line[i - 1] in "_-")) else None
        if m:
            w = m.group(0)
            if w[0].isupper() and "-" in w:       # a hyphen is part of a name only after a small letter
                w = w[:w.index("-")]
                m = re.match(re.escape(w), line[i:])
                out.append(table.get(w, w))
                i += len(w)
                continue
            out.append(table.get(w, w) if not w.endswith("'") else w)
            i = m.end()
            continue
        out.append(c)
        i += 1
    return "".join(out)


def split_spawns(lines):
    """A section's lines before its first SPAWN marker, and each SPAWN subsection."""
    pre, spawns, cur = [], {}, None
    for (i, line) in lines:
        m = MARK_SPAWN.match(line)
        if m:
            cur = spawns.setdefault(m.group(1), [])
        (pre if cur is None else cur).append((i, line))
    return pre, spawns


def render_value(v, notation):
    if isinstance(v, bool):
        raise ValueError("a boolean parameter")
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        if "'" in v or "\n" in v:
            raise ValueError("a parameter string with a quote")
        return "'%s'" % v
    if isinstance(v, list):
        sep = {"1990": ", ", "1969": ";", "1982": ","}[notation]
        return "[" + sep.join(render_value(x, notation) for x in v) + "]"
    raise ValueError("a parameter of type %s" % type(v).__name__)


class Unit:
    """One piece of text the harness gives the system: params, prelude, a stage's own text, a spawn."""

    def __init__(self, kind, stage, comp, lines):
        self.kind, self.stage, self.comp = kind, stage, comp
        self.lines = [l for (_, l) in lines] if lines and isinstance(lines[0], tuple) else list(lines)
        self.text = "".join(self.lines)

    def label(self):
        if self.kind == "spawn":
            return "stage %d, spawn %s" % (self.stage, self.comp)
        if self.kind == "stage":
            return "stage %d" % self.stage
        return self.kind


class Plan:
    """What the harness gives the system, unit by unit, for an instance."""

    def __init__(self, prog, sub, inst, faults):
        self.prog, self.sub, self.inst = prog, sub, inst
        self.faults = faults
        self.param_lines = []
        params = inst.get("parameters", {})
        for name in prog.params:
            if name not in params:
                faults.append("the program declares parameter %r, which instance %s does not have; nothing is given for it" % (name, inst["id"]))
                continue
            try:
                self.param_lines.append("%s = %s\n" % (name, render_value(params[name], prog.notation)))
            except ValueError as e:
                faults.append("parameter %r cannot be written as an Absys value: %s" % (name, e))
        self.notes = []

    def spawn_order(self, st):
        order = self.inst.get("parameters", {}).get("spawn_order")
        return list(order) if order else list(st.get("spawns", []))

    def stage_units(self, k):
        """The units of stage k: its own text (before any SPAWN), then each spawned computation's."""
        st = self.sub["stages"][k - 1]
        lines, problem = self.prog.section(k, self.inst)
        if problem:
            if problem not in self.notes:
                self.notes.append(problem)
            lines = []
        units = []
        if k == 1:
            units.append(Unit("params", 1, None, self.param_lines))
            units.append(Unit("prelude", 1, None, self.prog.prelude))
        spawns = self.spawn_order(st)
        if spawns:
            pre, subs = split_spawns(lines)
            units.append(Unit("stage", k, None, pre))
            for c in spawns:
                if c not in subs:
                    n = "stage %d spawns %s, and the program's section has no % SPAWN %s: nothing is given for it" % (k, c, c)
                    if n not in self.notes:
                        self.notes.append(n)
                units.append(Unit("spawn", k, c, subs.get(c, [])))
            extra = [c for c in subs if c not in spawns]
            if extra:
                self.notes.append("stage %d: SPAWN sections %r are not computations the stage spawns; they are not given" % (k, extra))
        else:
            units.append(Unit("stage", k, None, lines))
        return units

    def units_upto(self, k):
        out = []
        for j in range(1, k + 1):
            out += self.stage_units(j)
        return out


# ------------------------------------------------------- reading output ---

STATE_HEAD = re.compile(r"^(\s*)(?:(\d+) derivations?(?: \((\d+) still elaborating when the budget ran out\))?:|(No derivation survives: the assertions are unsatisfiable\.))\s*$")
EVENT = re.compile(r"^  (?:  )*#\d+\s+(\S+)\s+(.*)$")
ERROR_LINE = re.compile(r"(?m)^(?:error at \d+:\d+: .*|error: .*)$")
SUSP_KIND = [
    ("(waits for a definition:", "susp_applications"),
    ("(waits for its key:", "susp_applications"),
    ("(waits for two of its numbers:", "susp_relations"),
    ("(waits for its term:", "susp_relations"),
    ("(waits for its variables:", "susp_negations"),
    ("(cannot be decided yet; waits for:", "susp_negations"),
]


def parse_state(text):
    """The system's printed state (`?`, or the end of `absys FILE`), split into derivations."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    res = {"text": text, "header": None, "count": None, "running": 0, "none": False,
           "derivs": [], "suspended": {k: 0 for k in SUSP_FIELDS}, "any_suspended": False}
    if not lines:
        return res
    m = STATE_HEAD.match(lines[0])
    if not m:
        return res
    indent = m.group(1)
    res["header"] = lines[0]
    if m.group(4):
        res["none"], res["count"] = True, 0
        return res
    res["count"] = int(m.group(2))
    res["running"] = int(m.group(3) or 0)
    cur = None
    for line in lines[1:]:
        if line.startswith(indent + "  derivation #"):
            cur = [line]
            res["derivs"].append(cur)
        elif cur is not None:
            cur.append(line)
            if line.startswith(indent + "    suspended   "):
                res["any_suspended"] = True
                for item in line[len(indent + "    suspended   "):].split(";  "):
                    kind = "susp_equations"
                    for marker, k in SUSP_KIND:
                        if marker in item:
                            kind = k
                            break
                    res["suspended"][kind] += 1
    res["derivs"] = ["\n".join(b) + "\n" for b in res["derivs"]]
    return res


def emits_from_events(events):
    """The entries of tout("emit", ...) outputs the trace shows performed, in order."""
    out = []
    for kind, text in events:
        if kind == "output" and text.startswith("emit = "):
            out.append(text[len("emit = "):])
    return out


def events_of(text):
    ev = []
    for line in text.split("\n"):
        m = EVENT.match(line)
        if m:
            ev.append((m.group(1), m.group(2)))
    return ev


# ---------------------------------------------------------------- repl ---

class Repl:
    """`absys-measure repl`, fed on standard input; its output read as it comes."""

    def __init__(self, argv):
        self.argv = argv
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, bufsize=0)
        self.out = bytearray()
        self.err = bytearray()
        self.cond = threading.Condition()
        self.eof = False
        self.sentinels = []     # (start, end, eaten_error_text or None)
        self.scan = 0
        self.wq = queue.Queue()
        self.status = None
        self.rusage = None
        threading.Thread(target=self._read, args=(self.p.stdout, self.out, True), daemon=True).start()
        threading.Thread(target=self._read, args=(self.p.stderr, self.err, False), daemon=True).start()
        threading.Thread(target=self._write, daemon=True).start()

    def _read(self, f, buf, is_out):
        fd = f.fileno()
        while True:
            try:
                chunk = os.read(fd, 1 << 16)
            except OSError:
                chunk = b""
            with self.cond:
                if not chunk:
                    if is_out:
                        self.eof = True
                    self.cond.notify_all()
                    return
                buf.extend(chunk)
                if is_out:
                    self._find_sentinels()
                self.cond.notify_all()

    def _find_sentinels(self):
        while True:
            hb = self.out.find(HELP_B, self.scan)
            em = EATEN_B.search(self.out, self.scan)
            cands = []
            if hb >= 0:
                cands.append((hb, hb + len(HELP_B), None))
            if em:
                cands.append((em.start(), em.end(), em.group(0).decode("utf-8", "replace")))
            if not cands:
                return
            s = min(cands)
            self.sentinels.append(s)
            self.scan = s[1]

    def _write(self):
        while True:
            data = self.wq.get()
            if data is None:
                try:
                    self.p.stdin.close()
                except OSError:
                    pass
                return
            try:
                self.p.stdin.write(data)
            except (BrokenPipeError, OSError, ValueError):
                pass

    def send(self, s):
        self.wq.put(s.encode("utf-8"))

    def wait(self, n, deadline):
        """Wait until n sentinels in all have been seen. 'ok', 'timeout' or 'eof'."""
        with self.cond:
            while len(self.sentinels) < n:
                if self.eof:
                    return "eof"
                left = deadline - time.monotonic()
                if left <= 0:
                    return "timeout"
                self.cond.wait(min(left, 0.5))
            return "ok"

    def kill(self):
        try:
            self.p.send_signal(signal.SIGKILL)
        except OSError:
            pass
        return self.finish(kill=True)

    def finish(self, kill=False, timeout=30):
        if self.status is not None:
            return self.status
        if not kill:
            self.wq.put(None)
        t0 = time.monotonic()
        while True:
            pid, st, ru = os.wait4(self.p.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - t0 > timeout:
                self.p.send_signal(signal.SIGKILL)
                pid, st, ru = os.wait4(self.p.pid, 0)
                break
            time.sleep(0.02)
        self.rusage = ru
        self.p.returncode = os.waitstatus_to_exitcode(st)
        self.status = self.p.returncode
        with self.cond:
            deadline = time.monotonic() + 5
            while not self.eof and time.monotonic() < deadline:
                self.cond.wait(0.2)
        return self.status


# ------------------------------------------------------------- the run ---

class Harness:
    def __init__(self, argv):
        self.argv = argv
        self.faults = []
        self.notes = []

    # ---- setup
    def usage(self, msg):
        sys.stderr.write("usage: harnesses/absys/run CONFIGURATION PROBLEM SUBPROBLEM MODE PROGRAM OUTDIR\n%s\n" % msg)
        sys.exit(2)

    def setup(self):
        a = self.argv[1:]
        if len(a) != 6:
            self.usage("six arguments are needed")
        self.config, self.problem, self.instance_id, self.mode, prog_arg, self.outdir = a
        if self.config not in CONFIGS:
            self.usage("unknown configuration %r: %s" % (self.config, ", ".join(CONFIGS)))
        if self.mode not in MODES:
            self.usage("unknown mode %r" % self.mode)
        self.stages_path = os.environ.get("ABSYS_HARNESS_STAGES") or DEFAULT_STAGES
        self.doc, idx = load_stages(self.stages_path)
        if self.instance_id not in idx:
            self.usage("unknown instance %r" % self.instance_id)
        self.prob, self.sub, self.inst = idx[self.instance_id]
        if self.prob["problem"] != self.problem:
            self.usage("instance %s belongs to %s, not %s" % (self.instance_id, self.prob["problem"], self.problem))
        prog_path = prog_arg if os.path.isabs(prog_arg) else os.path.join(REPO, prog_arg)
        if not os.path.isfile(prog_path):
            if os.path.isfile(prog_arg):
                prog_path = os.path.abspath(prog_arg)
            else:
                self.usage("no program %r" % prog_arg)
        self.prog_path = prog_path
        self.purpose = os.environ.get("ABSYS_HARNESS_PURPOSE", "primary")
        if self.purpose not in ("primary", "variant", "qualification"):
            self.usage("ABSYS_HARNESS_PURPOSE must be primary, variant or qualification")
        self.force_repose = os.environ.get("ABSYS_HARNESS_POSING") == "reposed"
        if self.force_repose and self.purpose != "qualification":
            self.usage("ABSYS_HARNESS_POSING=reposed is for qualification runs only")
        self.lim = problem_limits(self.doc, self.prob)
        self.B = int(self.lim["budget_steps"])
        self.effects = bool(self.prob.get("effects"))
        self.trace = self.effects or (self.mode == "cost" and self.B <= 1000000)
        os.makedirs(self.outdir, exist_ok=True)

    # ---- the record skeleton
    def run_meta(self):
        commits = {}
        try:
            with open(COMMITS_FILE) as f:
                for line in f:
                    p = line.split()
                    if len(p) == 2:
                        commits[p[0]] = p[1]
        except OSError:
            pass
        head = git("rev-parse", "HEAD") or "0000000"
        dirty = git("status", "--porcelain", "--", "harnesses/absys", "harnesses/stages.json",
                    "harnesses/validate.py", "harnesses/record.schema.json",
                    ":(exclude)harnesses/absys/qualification")
        cb = self.program.constants
        if self.purpose == "variant":
            variant = os.environ.get("ABSYS_HARNESS_VARIANT") or None
        else:
            variant = None
        self.meta = {
            "run_id": self.run_id,
            "spec_tag": self.doc.get("spec_tag", "spec-1.0"),
            "system": "absys",
            "configuration": self.config,
            "problem": self.problem,
            "subproblem": self.sub["id"],
            "instance": self.instance_id,
            "parameters": self.inst.get("parameters", {}),
            "mode": self.mode,
            "purpose": self.purpose,
            "program": {"path": relpath(self.prog_path), "sha256": sha256_file(self.prog_path),
                        "repo_commit": git("rev-parse", "HEAD")},
            "constants": {"how": "block" if cb else "none", "input_path": None, "input_sha256": None,
                          "variant": variant},
            "system_build": {
                "commit": commits.get("absys-measure"),
                "image": os.environ.get("CP_IMAGE_DIGEST") or None,
                "binary": BIN,
                "version_output": None,
                "instrumented": True,
            },
            "harness": {"path": "harnesses/absys/run", "commit": head[:40] if re.match(r"^[0-9a-f]{7,40}$", head) else "0000000",
                        "dirty": bool(dirty)},
            "command": ["harnesses/absys/run"] + self.argv[1:],
            "posing": "incremental",
            "limits": {"budget_steps": self.B, "step_unit": STEP_UNIT,
                       "safety_limit_s": self.lim["safety_limit_s"], "rerun_limit_s": self.lim["rerun_limit_s"]},
            "started_utc": iso(self.started),
            "ended_utc": None,
            "complete": False,
            "incomplete_reason": None,
            "confounds": CONFOUNDS + (["qualification only: ABSYS_HARNESS_POSING=reposed, every stage after the first is posed by reposing stages 1 to k into a new session"] if self.force_repose else []),
            "environment": {},
        }
        self.notes.append("system: absys-measure %s (branch measure, on the pinned main %s); absys has no version option, so version_output is null and the commits are from %s" % (commits.get("absys-measure"), commits.get("absys"), COMMITS_FILE))
        self.notes.append("notation: %s (from the program's file name, as the system decides it); flags of the configuration: %s" % (self.program.notation, " ".join(CONFIGS[self.config]) or "none"))
        if self.stages_path != DEFAULT_STAGES:
            self.notes.append("stages file: %s (ABSYS_HARNESS_STAGES)" % relpath(self.stages_path))

    def sys_flags(self):
        return CONFIGS[self.config] + ["--notation", self.program.notation, "--steps", str(self.B)]

    # ---- the effects log
    def log_paths(self):
        return (os.path.join(self.outdir, "%s.effects.jsonl" % self.instance_id),
                os.path.join(self.outdir, "%s.effects-observation.jsonl" % self.instance_id))

    def read_log(self, path):
        out = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        out.append(json.loads(line))
        return out

    def emit(self, entries, stage, attempt, replay_of, observation):
        """The stub: append each entry, verbatim, to L (or to the observation log)."""
        if not self.effects:
            return []
        path = self.obs_log if observation else self.cls_log
        log = self.read_log(path)
        seq = len(log)
        out = []
        with open(path, "a", encoding="utf-8") as f:
            for e in entries:
                seq += 1
                rec = {"seq": seq, "entry": e, "run_id": self.run_id, "stage": stage, "attempt": attempt,
                       "during_replay_of": replay_of, "log": "observation" if observation else "classification"}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.append(rec)
        return out

    # ---- shared pieces of an attempt
    def empty_comp(self, cid, spawned, idx, st_budget):
        return {
            "id": cid, "spawned": spawned, "spawn_index": idx, "side_by_side": False if spawned else None,
            "queries": [],
            "execution_state": {"states": [], "determined": False, "basis": "", "error_verbatim": None},
            "steps": {"unit": STEP_UNIT, "budget": st_budget, "budget_exhausted": False, "stage": None,
                      "restated": None, "restart_cost": None, "restart_cost_method": None,
                      "restart_cost_source": None, "to_first_answer": None, "between_answers": [],
                      "to_end": None, "repeated_work": None},
            "alternatives": {"unit": ALT_UNIT, "at_boundary": None, "at_budget": None, "peak": None,
                             "held_as": HELD_AS[self.config], "by_type": None, "problem_defined": None},
            "suspended": {"unit": "suspended processes the system prints (waiting on an uninstantiated variable), summed over derivations", "at_boundary": None, "peak": None, "items": None},
            "problem_operations": None,
        }

    def queries_for(self, st, cid):
        return [q for q in st["queries"] if q["computation"] == cid]

    def fill_comp(self, comp, st, state, errors, timeout, steps_info=None):
        """Execution state, answers, alternatives and suspended work, from what the system printed."""
        es = comp["execution_state"]
        states, basis = [], []
        if timeout:
            states.append("timeout")
            basis.append("the safety limit stopped the attempt")
            if state is not None and state["any_suspended"]:
                states.append("suspended")
                basis.append("a derivation prints suspended processes")
        elif state is None or state["header"] is None:
            if errors:
                states.append("error")
                basis.append("the system reported an error, and printed no state")
            else:
                basis.append("the system printed no state")
        else:
            if state["running"] > 0:
                states.append("budget")
                basis.append("the system's state reports %d derivation(s) still elaborating when the budget ran out" % state["running"])
            elif errors:
                states.append("error")
                basis.append("the system reported an error for the stage's text (verbatim in error_verbatim)")
            if state["any_suspended"]:
                states.append("suspended")
                basis.append("a derivation prints suspended processes")
            if not states:
                states.append("finished")
                basis.append("no derivation is still elaborating, none prints a suspended process, and no error was reported" +
                             ("; no derivation survives" if state["none"] else ""))
        if errors:
            es["error_verbatim"] = "".join(e if e.endswith("\n") else e + "\n" for e in errors)
            if "error" not in states:
                basis.append("the system also reported an error, in error_verbatim")
        es["states"] = states
        es["determined"] = bool(states)
        es["basis"] = "; ".join(basis) or "nothing could be read"
        comp["steps"]["budget_exhausted"] = "budget" in states
        derivs = state["derivs"] if state else []
        for q in self.queries_for(st, comp["id"]):
            cap = query_cap(q, self.inst)
            ans = []
            for i, d in enumerate(derivs[:cap], 1):
                a = {"index": i, "verbatim": d}
                if steps_info is not None:
                    a["steps_at"] = steps_info
                ans.append(a)
            if "timeout" in states:
                ended = "timeout"
            elif "budget" in states:
                ended = "budget"
            elif "error" in states:
                ended = "error"
            elif state is not None and state["count"] is not None and state["count"] > cap:
                ended = "cap"
            else:
                ended = "exhausted"
            comp["queries"].append({"id": q["id"], "cap": cap, "answers": ans, "ended_by": ended,
                                    "collected_on": "this-run"})
        if state is not None and state["header"] is not None:
            comp["alternatives"]["at_boundary"] = state["count"]
            if "budget" in states:
                comp["alternatives"]["at_budget"] = state["count"]
            comp["suspended"]["at_boundary"] = sum(state["suspended"].values())
            comp["suspended"]["items"] = dict(state["suspended"])

    def new_attempt(self, n, limit, posed):
        return {"attempt": n, "limit_s": limit, "posed": posed, "computations": [],
                "observe": {"raw": "", "method": "", "taken_on": "this-run", "bindings": None},
                "print": None, "store": {"quantities": {}, "source": None}, "wall_time_s": 0.0,
                "cpu_time_s": None, "max_rss_kb": None, "stdout": "", "stderr": "",
                "exit": {"status": None, "signal": None},
                "safety_limit": {"hit": False, "action": "none", "how_stopped": None},
                "effects": [], "manual_actions": [], "separate_run": None, "notes": []}

    def unknown_names(self):
        return [u for u in self.sub.get("unknowns", []) if re.match(r"^[A-Za-z][A-Za-z0-9_]*$", u)]

    # ---- restart cost on a separate run (behaviour mode)
    def measure_restart(self, units, k, attempt_no, limit):
        text = "".join(u.text for u in units)
        tmp = tempfile.mkdtemp(prefix="absys-restart-")
        path = os.path.join(tmp, "replay.%s" % EXT[self.program.notation])
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        argv = [BIN, "json", path, "--full"] + self.sys_flags()
        t0 = time.monotonic()
        try:
            r = subprocess.run(argv, capture_output=True, timeout=limit)
        except subprocess.TimeoutExpired:
            return None, "the separate run of stages 1 to %d (%s) was stopped after %s s" % (k - 1, " ".join(argv[:2]), limit), []
        took = time.monotonic() - t0
        try:
            doc = json.loads(r.stdout.decode("utf-8", "replace"))
        except ValueError:
            return None, "the separate run of stages 1 to %d printed no JSON (exit %s): %s" % (k - 1, r.returncode, r.stderr.decode("utf-8", "replace")), []
        steps = sum(int(s["steps"]) for s in doc.get("steps", []))
        src = "separate run of the replayed text (params, prelude, stages 1 to %d), `absys-measure json` with the configuration's flags, %.2f s: the sum of the steps of its %d assertions" % (k - 1, took, len(doc.get("steps", [])))
        if doc.get("error"):
            src += "; it stopped at a syntax error, %r, so any assertion after it, which the repl replay runs, is not counted" % doc["error"].get("message")
            self.faults.append("stage %d attempt %d: the restart cost may undercount: the json run stops at the first syntax error, the repl replay goes on past it" % (k, attempt_no))
        # tout outputs of the separate run go to the observation log
        entries = []
        if self.effects:
            ranges = self.unit_lines(units)
            for s in doc.get("steps", []):
                evs = [(e["kind"], e["text"]) for e in s.get("events", [])]
                if s.get("eventCount", 0) > len(evs):
                    self.faults.append("stage %d attempt %d: the json run lists only %d of %d events of an assertion; observation-log entries may be missing" % (k, attempt_no, len(evs), s["eventCount"]))
                u = self.unit_at(ranges, s["line"] - 1)
                entries += [(e, u.stage if u else None) for e in emits_from_events(evs)]
        return steps, src, entries

    def unit_lines(self, units):
        ranges, line = [], 0
        for u in units:
            ranges.append((line, line + len(u.lines), u))
            line += len(u.lines)
        return ranges

    def unit_at(self, ranges, line0):
        for (a, b, u) in ranges:
            if a <= line0 < b:
                return u
        return None

    # ================================================= behaviour (the repl)
    def repl_argv(self):
        return [BIN, "repl", "--full"] + self.sys_flags()

    def behaviour(self):
        K = len(self.sub["stages"])
        self.repl = None
        stages_out = []
        prev_final = None
        last_proc_attempt = None
        for k in range(1, K + 1):
            st = self.sub["stages"][k - 1]
            atts = []
            for n in (1, 2):
                limit = self.lim["safety_limit_s"] if n == 1 else self.lim["rerun_limit_s"]
                if k == 1:
                    how, reason = "fresh", ("first-stage" if n == 1 else "safety-rerun")
                elif n == 2:
                    how, reason = "reposed", "safety-rerun"
                else:
                    pst = set()
                    for c in prev_final["computations"]:
                        pst |= set(c["execution_state"]["states"])
                    if "error" in pst:
                        how, reason = "reposed", "after-error"
                    elif "timeout" in pst:
                        how, reason = "reposed", "after-timeout"
                    elif self.force_repose:
                        how, reason = "reposed", "configuration"
                    elif self.repl is None or self.repl.status is not None:
                        how, reason = "reposed", "after-error"
                    else:
                        how, reason = "incremental", "configuration"
                cab = bool(how == "incremental" and prev_final is not None and
                           any("budget" in c["execution_state"]["states"] for c in prev_final["computations"]))
                posed = {"how": how, "reason": reason, "replayed": list(range(1, k)) if how == "reposed" else [],
                         "replayed_commitments": [], "continued_after_budget": cab,
                         "instance_parameters_passed": {p: self.inst["parameters"][p] for p in self.program.params if p in self.inst.get("parameters", {})}}
                att = self.new_attempt(n, limit, posed)
                if how != "incremental" and self.repl is not None and self.repl.status is None:
                    # the old session is not continued: end it, and say so where it was left running
                    status = self.repl.finish()
                    if last_proc_attempt is not None and last_proc_attempt["exit"]["status"] is None:
                        last_proc_attempt["exit"] = {"status": status, "signal": signal_name(status)}
                        last_proc_attempt["notes"].append("the harness ended this session (closing its input) to pose the next stage by reposing")
                self.behaviour_attempt(k, st, att, how)
                last_proc_attempt = att
                atts.append(att)
                if att["safety_limit"]["hit"]:
                    if n == 1 and self.lim["rerun_limit_s"] is not None:
                        att["safety_limit"]["action"] = "rerun"
                        continue
                    att["safety_limit"]["action"] = "final-timeout" if n == 2 else "fixed-limit-timeout"
                break
            stages_out.append({"stage": k, "attempts": atts})
            prev_final = atts[-1]
        if self.repl is not None and self.repl.status is None:
            status = self.repl.finish()
            last_proc_attempt["exit"] = {"status": status, "signal": signal_name(status)}
            self.p13_usage(last_proc_attempt, self.repl)
        return stages_out

    def p13_usage(self, att, repl):
        if self.problem == "P13" and repl.rusage is not None:
            att["cpu_time_s"] = round(repl.rusage.ru_utime + repl.rusage.ru_stime, 3)
            att["max_rss_kb"] = int(repl.rusage.ru_maxrss)
            att["notes"].append("cpu_time_s and max_rss_kb: getrusage of the absys process (os.wait4) when it ended, for P13's growth only")

    def behaviour_attempt(self, k, st, att, how):
        n_att = att["attempt"]
        plan = []       # (kind, unit or name, stage), one per `.help` the harness sends
        if how in ("fresh", "reposed"):
            if how == "reposed":
                rc, src, obs_entries = self.measure_restart(self.plan.units_upto(k - 1), k, n_att, 10 * att["limit_s"])
                if rc is None:
                    self.faults.append("stage %d attempt %d: no restart cost: %s" % (k, n_att, src))
                att["_restart"] = (rc, src)
                for (e, j) in obs_entries:
                    att["effects"] += self.emit([e], k, n_att, j, True)
            t0 = time.monotonic()
            self.repl = Repl(self.repl_argv())
            out0 = err0 = 0
            if self.trace:
                self.repl.send(".trace\n")
            if how == "reposed":
                for u in self.plan.units_upto(k - 1):
                    if u.text:
                        self.repl.send(u.text + ".help\n")
                        plan.append(("unit", u, u.stage))
        else:
            t0 = time.monotonic()
            with self.repl.cond:
                out0, err0 = len(self.repl.out), len(self.repl.err)
        repl = self.repl
        base = len(repl.sentinels)
        units = self.plan.stage_units(k)
        spawns = [u for u in units if u.kind == "spawn"]
        for u in units:
            if u.text:
                repl.send(u.text + ".help\n")
                plan.append(("unit", u, k))
            if u.kind == "spawn":
                repl.send("?\n.help\n")
                plan.append(("state", u.comp, k))
        repl.send("?\n.help\n")
        plan.append(("state", None, k))
        names = self.unknown_names()
        for nm in names:
            repl.send("? %s\n.help\n" % nm)
            plan.append(("name", nm, k))
        res = repl.wait(base + len(plan), t0 + att["limit_s"])
        timeout = res == "timeout"
        if timeout:
            status = repl.kill()
            att["safety_limit"]["hit"] = True
            att["safety_limit"]["how_stopped"] = "SIGKILL to the absys-measure repl process (pid %d) after %s s" % (repl.p.pid, att["limit_s"])
            att["exit"] = {"status": status, "signal": signal_name(status)}
        elif res == "eof":
            status = repl.finish()
            att["exit"] = {"status": status, "signal": signal_name(status)}
            att["notes"].append("the system's process ended before replying to every line the harness sent")
        att["wall_time_s"] = round(time.monotonic() - t0, 3)
        with repl.cond:
            out_b, err_b, sents = bytes(repl.out), bytes(repl.err), list(repl.sentinels)
        att["stdout"] = decode(out_b[out0:], self.faults, "stage %d attempt %d stdout" % (k, n_att))
        att["stderr"] = decode(err_b[err0:], self.faults, "stage %d attempt %d stderr" % (k, n_att))
        # the system's output, cut at the harness's `.help` lines
        segs, prev = [], out0
        for i, what in enumerate(plan):
            j = base + i
            if j < len(sents):
                s, e, eaten = sents[j]
                segs.append((what, out_b[prev:s].decode("utf-8", "replace"), eaten))
                prev = e
            else:
                segs.append((what, out_b[prev:].decode("utf-8", "replace"), None))
                break
        errors_by, emits, states, name_out = {}, [], {}, {}
        for (what, text, eaten) in segs:
            kind, ref, stg = what
            if kind == "unit":
                errs = ERROR_LINE.findall(text)
                if eaten:
                    errs.append(eaten.rstrip("\n"))
                    att["notes"].append("%s ended inside an unfinished assertion: the repl read the harness's `.help` line as its continuation" % ref.label())
                if stg == k:
                    errors_by.setdefault(ref.comp if ref.kind == "spawn" else None, []).extend(errs)
                elif errs:
                    att["notes"].append("replay of %s: the system reported: %s" % (ref.label(), "; ".join(errs)))
                for e in emits_from_events(events_of(text)):
                    emits.append((e, stg if stg != k else None))
            elif kind == "state":
                states[ref] = text
            elif kind == "name":
                name_out[ref] = text
        for e, j in emits:
            att["effects"] += self.emit([e], k, n_att, j, False)
        rc = att.pop("_restart", None)
        stage_errors = errors_by.get(None, [])
        if res == "eof":
            stage_errors = stage_errors + [died(att["exit"]["status"], att["stderr"])]
        comps = []
        for idx, u in enumerate(spawns, 1):
            c = self.empty_comp(u.comp, True, idx, self.B)
            stt = parse_state(states[u.comp]) if u.comp in states else None
            self.fill_comp(c, st, stt, stage_errors + errors_by.get(u.comp, []), timeout and stt is None)
            comps.append(c)
        if not spawns or self.queries_for(st, "main"):
            c = self.empty_comp("main", False, None, self.B)
            stt = parse_state(states[None]) if None in states else None
            self.fill_comp(c, st, stt, stage_errors, timeout)
            comps.append(c)
        if timeout:
            for c in comps:
                es = c["execution_state"]
                if "timeout" not in es["states"]:
                    es["states"] = ["timeout"] + [s for s in es["states"] if s == "suspended"]
                    es["determined"] = True
                    es["basis"] = "the safety limit stopped the attempt after this computation's state was read; " + es["basis"]
                    c["steps"]["budget_exhausted"] = False
                    for q in c["queries"]:
                        q["ended_by"] = "timeout"
        for c in comps:
            if how == "reposed":
                c["steps"]["restart_cost"] = rc[0] if rc else None
                c["steps"]["restart_cost_method"] = "separate-run"
                c["steps"]["restart_cost_source"] = rc[1] if rc else None
                if rc and rc[0] is not None:
                    c["steps"]["budget"] = self.B + rc[0]
        att["computations"] = comps
        final = states.get(None)
        att["print"] = final
        att["observe"] = {
            "raw": (final or "") + "".join(name_out.get(nm, "") for nm in names),
            "method": "the repl's `?` (every derivation: its status, bindings, suspended processes, outputs), then `? NAME` for each unknown of the sub-problem written as a plain identifier (%s), read at the end of the stage" % (", ".join(names) or "none"),
            "taken_on": "this-run",
            "bindings": {nm: name_out[nm] for nm in names if nm in name_out} or None}
        if st.get("commit"):
            att["notes"].append("commit stage: Absys keeps every derivation live and selects none; answers(1) is the first derivation the system prints, and nothing is replayed as a commitment if a later stage is reposed")

    # ===================================== cost and storage (absys FILE --measure)
    def measured(self):
        K = len(self.sub["stages"])
        stages_out = []
        prev_final = None
        for k in range(1, K + 1):
            st = self.sub["stages"][k - 1]
            atts = []
            for n in (1, 2):
                limit = self.lim["safety_limit_s"] if n == 1 else self.lim["rerun_limit_s"]
                if k == 1:
                    how, reason = "fresh", ("first-stage" if n == 1 else "safety-rerun")
                elif n == 2:
                    how, reason = "reposed", "safety-rerun"
                else:
                    pst = set()
                    for c in prev_final["computations"]:
                        pst |= set(c["execution_state"]["states"])
                    how = "reposed"
                    reason = "after-error" if "error" in pst else ("after-timeout" if "timeout" in pst else "configuration")
                posed = {"how": how, "reason": reason, "replayed": list(range(1, k)) if how == "reposed" else [],
                         "replayed_commitments": [], "continued_after_budget": False,
                         "instance_parameters_passed": {p: self.inst["parameters"][p] for p in self.program.params if p in self.inst.get("parameters", {})}}
                att = self.new_attempt(n, limit, posed)
                self.measured_attempt(k, st, att, how)
                atts.append(att)
                if att["safety_limit"]["hit"]:
                    if n == 1 and self.lim["rerun_limit_s"] is not None:
                        att["safety_limit"]["action"] = "rerun"
                        continue
                    att["safety_limit"]["action"] = "final-timeout" if n == 2 else "fixed-limit-timeout"
                break
            stages_out.append({"stage": k, "attempts": atts})
            prev_final = atts[-1]
        return stages_out

    def measured_attempt(self, k, st, att, how):
        n_att = att["attempt"]
        units = self.plan.units_upto(k)
        ranges = self.unit_lines(units)
        uix = {id(u): i for i, u in enumerate(units)}
        spawns = [u for u in units if u.kind == "spawn" and u.stage == k]
        each = bool(spawns)
        text = "".join(u.text for u in units)
        tmp = tempfile.mkdtemp(prefix="absys-measure-")
        path = os.path.join(tmp, "stages-1-to-%d.%s" % (k, EXT[self.program.notation]))
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        argv = [BIN, path, "--measure", "--full"] + self.sys_flags() + (["--trace"] if self.trace else []) + (["--each"] if each else [])
        att["notes"].append("measured run: absys-measure FILE %s, FILE the text of the parameters, prelude and stages 1 to %d (%d lines), the system's process started anew" % (" ".join(argv[2:]), k, len(text.splitlines())))
        t0 = time.monotonic()
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        timeout = False
        try:
            out_b, err_b = p.communicate(timeout=att["limit_s"])
        except subprocess.TimeoutExpired:
            timeout = True
            p.send_signal(signal.SIGKILL)
            out_b, err_b = p.communicate()
            att["safety_limit"]["hit"] = True
            att["safety_limit"]["how_stopped"] = "SIGKILL to the absys-measure process (pid %d) after %s s" % (p.pid, att["limit_s"])
        att["wall_time_s"] = round(time.monotonic() - t0, 3)
        att["exit"] = {"status": p.returncode, "signal": signal_name(p.returncode)}
        out = decode(out_b, self.faults, "stage %d attempt %d stdout" % (k, n_att))
        err = decode(err_b, self.faults, "stage %d attempt %d stderr" % (k, n_att))
        att["stdout"], att["stderr"] = out, err
        reports = parse_measure(err)
        blocks, final = split_file_output(out, each, self.trace)
        errors = []
        if not timeout and p.returncode != 0:
            msg = err.split("line\tassertion")[0].strip("\n")
            errors.append(msg if (msg and p.returncode > 0) else died(p.returncode, msg))
        ok = not timeout and not errors
        rep_unit = [self.unit_at(ranges, r["line"]) for r in reports]
        if ok and (each or self.trace) and len(blocks) != len(reports):
            self.faults.append("stage %d attempt %d: %d measure reports, but %d printed assertions" % (k, n_att, len(reports), len(blocks)))
        before_k = [i for i, u in enumerate(rep_unit) if u is not None and u.stage < k]
        restart = sum(reports[i]["steps"] for i in before_k)
        if self.effects:
            for i, b in enumerate(blocks):
                u = rep_unit[i] if i < len(rep_unit) else None
                j = u.stage if (u is not None and u.stage < k) else None
                for e in emits_from_events(b["events"]):
                    att["effects"] += self.emit([e], k, n_att, j, True)

        sep = {}

        def sep_restart():
            """This run reported no steps (it stopped with an error, or at the safety limit): the
            restart cost is measured on a separate run of stages 1 to k-1, as in a behaviour run."""
            if "rc" not in sep:
                rc, src, entries = self.measure_restart(self.plan.units_upto(k - 1), k, n_att, 10 * att["limit_s"])
                if rc is None:
                    self.faults.append("stage %d attempt %d: no restart cost: %s" % (k, n_att, src))
                sep["rc"] = (rc, src)
                for (e, j) in entries:
                    att["effects"] += self.emit([e], k, n_att, j, True)
            return sep["rc"]

        def computation(cid, spawned, idx, mine_units, last_unit, state_text):
            c = self.empty_comp(cid, spawned, idx, self.B)
            stt = parse_state(state_text) if state_text is not None else None
            mine = [i for i, u in enumerate(rep_unit) if u is not None and id(u) in mine_units]
            upto = [i for i, u in enumerate(rep_unit) if u is not None and uix[id(u)] <= last_unit]
            stage_steps = sum(reports[i]["steps"] for i in mine) if ok else None
            self.fill_comp(c, st, stt, errors, timeout, steps_info=stage_steps)
            s = c["steps"]
            if ok:
                s["stage"] = stage_steps
                s["restated"] = sum(reports[i]["steps"] for i in upto)
                s["to_end"] = stage_steps
                if any(q["answers"] for q in c["queries"]):
                    s["to_first_answer"] = stage_steps
                if self.mode == "cost" and self.trace:
                    evs = [e for i in mine if i < len(blocks) for e in blocks[i]["events"]]
                    s["repeated_work"] = {"reactivating_events": sum(1 for (kind, t) in evs if "reactivated " in t)}
                if stage_steps > self.B and "budget" not in c["execution_state"]["states"]:
                    att["notes"].append("%s: the assertions of the stage took %d steps in all, more than the budget of %d, which the system counts per assertion" % (cid, stage_steps, self.B))
            if how == "reposed" and ok:
                s["restart_cost"] = restart
                s["restart_cost_method"] = "in-run"
                s["restart_cost_source"] = "this run: the steps --measure reports for the assertions of the parameters, prelude and stages 1 to %d, which come before stage %d's text" % (k - 1, k)
                s["budget"] = self.B + restart
            elif how == "reposed":
                rc = sep_restart()
                s["restart_cost"] = rc[0]
                s["restart_cost_method"] = "separate-run"
                s["restart_cost_source"] = rc[1]
                if rc[0] is not None:
                    s["budget"] = self.B + rc[0]
            if ok and upto:
                nowv = reports[upto[-1]]["now"]
                c["alternatives"]["at_boundary"] = nowv["derivations"]
                if mine:
                    c["alternatives"]["peak"] = {"value": max(reports[i]["peak"]["derivations"] for i in mine), "kind": "exact"}
                if "budget" in c["execution_state"]["states"]:
                    c["alternatives"]["at_budget"] = nowv["derivations"]
            return c

        comps = []
        for idx, u in enumerate(spawns, 1):
            upto = [i for i, uu in enumerate(rep_unit) if uu is not None and uix[id(uu)] <= uix[id(u)]]
            stext = blocks[upto[-1]]["state"] if (ok and upto and upto[-1] < len(blocks)) else None
            comps.append(computation(u.comp, True, idx, {id(u)}, uix[id(u)], stext))
        if not spawns or self.queries_for(st, "main"):
            comps.append(computation("main", False, None, {id(u) for u in units if u.stage == k}, len(units) - 1, final if ok else None))
        # the stage's store: the value after its last assertion; the peak over its assertions
        mine = [i for i, u in enumerate(rep_unit) if u is not None and u.stage == k]
        if ok and mine:
            nowv = reports[mine[-1]]["now"]
            att["store"] = {"quantities": {q: {"boundary": nowv[q], "peak": {"value": max(reports[i]["peak"][q] for i in mine), "kind": "exact"}, "unit": "count"} for q in MEASURE_FIELDS},
                            "source": "--measure (absys-measure, branch measure): each quantity after the stage's last assertion, and the largest value it had after any step of the stage's assertions, or when each was added (exact at the granularity of steps)"}
        elif ok and reports:
            nowv = reports[-1]["now"]
            att["store"] = {"quantities": {q: {"boundary": nowv[q], "peak": None, "unit": "count"} for q in MEASURE_FIELDS},
                            "source": "--measure: the stage's text has no assertion; each quantity after the last assertion before it"}
        att["computations"] = comps
        att["print"] = final if ok else None
        att["observe"] = {"raw": final if (ok and final) else "",
                          "method": "the state absys FILE prints at the end of the text of stages 1 to %d (--full)%s" % (k, "; with --each, the state after each assertion, from which each spawned computation's state is read" if each else ""),
                          "taken_on": "this-run", "bindings": None}
        if st.get("commit"):
            att["notes"].append("commit stage: Absys keeps every derivation live and selects none; answers(1) is the first derivation the system prints, and nothing is replayed as a commitment")

    # ================================================================ main
    def main(self):
        self.setup()
        self.started = utcnow()
        # a run_id not used before in OUTDIR
        while True:
            self.run_id = "%s.%s.%s" % (self.instance_id, self.mode, utcnow().strftime("%Y%m%dT%H%M%SZ"))
            if not any(os.path.exists(os.path.join(self.outdir, self.run_id + s)) for s in (".json", ".INVALID.json")):
                break
            time.sleep(1.0)
        self.program = Program(self.prog_path)
        for p in self.program.problems:
            self.faults.append("program structure: " + p)
        self.plan = Plan(self.program, self.sub, self.inst, self.faults)
        self.run_meta()
        self.cls_log, self.obs_log = self.log_paths()
        before = len(self.read_log(self.cls_log)) if self.effects else 0
        try:
            stages = self.behaviour() if self.mode == "behaviour" else self.measured()
            complete = len(stages) == len(self.sub["stages"])
        except Exception as e:  # a fault of the harness, not of the system
            import traceback
            self.faults.append("harness exception: " + "".join(traceback.format_exception(e)))
            stages, complete = getattr(self, "_partial", []), False
        for n in self.plan.notes:
            self.notes.append(n)
        self.meta["ended_utc"] = iso(utcnow())
        self.meta["complete"] = bool(complete and stages)
        if not self.meta["complete"]:
            self.meta["incomplete_reason"] = "the harness failed: see harness_faults"
        rec = {"record_format": "cp-raw-record/1", "made_up": False, "run": self.meta,
               "stages": stages if stages else [], "effects": None, "manual_actions": [],
               "harness_faults": self.faults, "notes": self.notes}
        if self.effects:
            rec["effects"] = {"log_path": relpath(self.cls_log), "observation_log_path": relpath(self.obs_log),
                              "entries_before_run": before, "log_after_run": self.read_log(self.cls_log)}
        out = os.path.join(self.outdir, self.run_id + ".json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
            f.write("\n")
        r = subprocess.run([sys.executable, VALIDATE, "--stages", self.stages_path, out], capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode != 0 or not stages:
            bad = os.path.join(self.outdir, self.run_id + ".INVALID.json")
            os.replace(out, bad)
            sys.stderr.write("the record did not validate; kept as %s\n" % bad)
            return 3
        print(relpath(out))
        return 0


def died(status, stderr):
    """What the harness can say of a system process that ended on its own before its work was done."""
    if status is not None and status < 0:
        s = "the system's process was ended by %s, which the harness did not send" % signal_name(status)
        if status == -signal.SIGKILL:
            s += " (the kernel sends it when the container's memory is exhausted: the system keeps every event of its run in memory, about 85 bytes a step)"
    else:
        s = "the system's process ended with exit status %s before it replied to every line" % status
    return s + ("; its standard error: " + stderr.strip("\n") if stderr.strip() else "")


def parse_measure(err):
    """--measure's table: one report per assertion, with its steps and each quantity now and at peak."""
    reports = []
    lines = err.split("\n")
    try:
        i = lines.index("line\tassertion\tsteps\tquantity\tnow\tpeak")
    except ValueError:
        return reports
    cur = None
    for line in lines[i + 1:]:
        p = line.split("\t")
        if len(p) != 6:
            continue
        ln, src, steps, q, now, peak = p
        if q == "derivations" or cur is None:
            cur = {"line": int(ln), "source": src, "steps": int(steps), "now": {}, "peak": {}}
            reports.append(cur)
        cur["now"][q] = int(now)
        cur["peak"][q] = int(peak)
    return reports


def split_file_output(out, each, trace):
    """absys FILE's standard output: per assertion (with --trace or --each) its events and state,
    and the state at the end."""
    blocks = []
    lines = out.split("\n")
    if not (each or trace):
        # the budget's notes, one per assertion that ran out, and then the state at the end
        for idx, line in enumerate(lines):
            if STATE_HEAD.match(line) and not line.startswith(" "):
                return blocks, "\n".join(lines[idx:])
        return blocks, None
    final_start = None
    cur = None
    mode = None
    pos = 0
    offsets = []
    for line in lines:
        offsets.append(pos)
        pos += len(line) + 1
    for idx, line in enumerate(lines):
        if line.startswith("» "):
            cur = {"events": [], "state_lines": [], "state": None}
            blocks.append(cur)
            mode = "src"
            continue
        if not each and STATE_HEAD.match(line) and not line.startswith(" "):
            final_start = idx
            break
        if cur is None:
            continue
        m = EVENT.match(line)
        if mode in ("src", "events") and m:
            cur["events"].append((m.group(1), m.group(2)))
            mode = "events"
            continue
        if each and mode in ("src", "events") and re.match(r"^  (\d+ derivations?\b|No derivation survives)", line):
            mode = "state"
            cur["state_lines"].append(line)
            continue
        if mode == "state":
            if line == "":
                mode = "done"
            else:
                cur["state_lines"].append(line)
            continue
    for b in blocks:
        if b["state_lines"]:
            b["state"] = "\n".join(b["state_lines"]) + "\n"
        del b["state_lines"]
    if each:
        final = blocks[-1]["state"] if blocks else None
    else:
        final = "\n".join(lines[final_start:]) if final_start is not None else None
    return blocks, final


# ================================================================== check

def check_main(argv):
    """harnesses/absys/check CONFIGURATION PROGRAM: syntax and static errors, executing nothing."""
    if len(argv) != 3:
        sys.stderr.write("usage: harnesses/absys/check CONFIGURATION PROGRAM\n")
        return 2
    config, prog_arg = argv[1], argv[2]
    if config not in CONFIGS:
        sys.stderr.write("unknown configuration %r: %s\n" % (config, ", ".join(CONFIGS)))
        return 2
    path = prog_arg if os.path.isabs(prog_arg) or os.path.exists(prog_arg) else os.path.join(REPO, prog_arg)
    if not os.path.isfile(path):
        sys.stderr.write("no program %r\n" % prog_arg)
        return 2
    prog = Program(path)
    problems = list(prog.problems)
    warnings = []
    n = prog.notation
    print("check %s %s: notation %s; nothing in the program is executed" % (config, relpath(path), n))
    if not prog.stages and not prog.parts:
        problems.append("the program has no % STAGE or % PART section")
    if prog.stages:
        ks = sorted(prog.stages)
        if ks != list(range(1, len(ks) + 1)):
            problems.append("STAGE sections are numbered %r, not 1..%d" % (ks, len(ks)))
    text = prog.text
    if not re.search(r"(?mi)^\s*%.*\bauthor\b", text):
        warnings.append("no provenance comment (% AUTHOR: ...); README, 'Provenance'")
    # the sections as the harness gives them, each fed to the repl line by line
    sections = [("prelude", prog.prelude)]
    for k in sorted(prog.stages):
        pre, subs = split_spawns(prog.stages[k])
        sections.append(("stage %d" % k, pre))
        sections += [("stage %d, spawn %s" % (k, c), l) for c, l in subs.items()]
    for p in prog.parts:
        pre, subs = split_spawns(prog.parts[p])
        sections.append(("part %s" % p, pre))
        sections += [("part %s, spawn %s" % (p, c), l) for c, l in subs.items()]
    tmp = tempfile.mkdtemp(prefix="absys-check-")
    count = 0
    for label, lines in sections:
        buf = []
        for (i, line) in lines:
            t = line.strip()
            if not buf:
                if t.startswith("?") or t.startswith("."):
                    problems.append("line %d (%s): a line that begins with `%s` is a command to the repl, not Absys" % (i, label, t[0]))
                    continue
                if t == "":
                    continue
            buf.append((i, line))
            btext = "".join(l for (_, l) in buf)
            res = parse_only(btext, n, tmp, config)
            if res is None:
                problems.append("line %d: the system's checker could not be run" % i)
                buf = []
                continue
            err, items = res
            if err is None:
                count += items
                buf = []
                continue
            if err["start"] >= len(btext.rstrip().encode("utf-8")):
                continue     # unfinished: the repl reads on
            line_no = buf[0][0] + err["line"] - 1
            problems.append("line %d, column %d (%s): %s" % (line_no, err["column"], label, err["message"]))
            count += items
            buf = []
        if buf:
            problems.append("line %d (%s): the section ends inside an unfinished assertion: %s" % (buf[0][0], label, "".join(l for (_, l) in buf).strip()))
    for w in warnings:
        print("warning: " + w)
    for p in problems:
        print("error: " + p)
    print("%d assertions parsed and compiled in %d sections; %d error(s)" % (count, len(sections), len(problems)))
    return 1 if problems else 0


def parse_only(text, notation, tmp, config):
    """Parse and compile a text with `absys-measure json --steps 0`. Each assertion is parsed,
    compiled and added to the goal, and no step of the machine is taken, so nothing is elaborated:
    no equation, application, `or`, `not`, `set` or `tout`. Only the error (a syntax error, or a
    static error of compiling, such as a variable bound twice by one lambda) and the number of
    assertions are read; nothing the program would compute is printed."""
    path = os.path.join(tmp, "check.%s" % EXT[notation])
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    try:
        r = subprocess.run([BIN, "json", path, "--steps", "0", "--notation", notation] + CONFIGS[config],
                           capture_output=True, timeout=60)
        doc = json.loads(r.stdout.decode("utf-8", "replace"))
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    steps = doc.get("steps", [])
    for s in steps:
        if s.get("steps", 0) != 0 or s.get("eventCount", 0) != 0 or any(d.get("outputs") for d in s.get("derivations", [])):
            raise SystemExit("check: the system took a step; check is broken")
    return doc.get("error"), len(steps)


def run_main(argv):
    return Harness(argv).main()
