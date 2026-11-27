"""The Python harness's runtime: the part of the harness that has to live in
the program's own interpreter process, because CPython's step count
(sys.monitoring INSTRUCTION events), problem-operation count (PY_START),
traced memory (tracemalloc) and the program's objects can only be read from
inside that process.

It is started by harnesses/python/run, never by hand:

    python3 -B -s -P harnesses/python/runtime.py CTL_IN_FD CTL_OUT_FD

and talks to `run` over two pipes, in frames of a 4-byte big-endian length
followed by a marshal dump of a dict. It does exactly this:

  * counts the program's bytecode instructions per computation and pauses a
    computation's thread when its budget is spent (systems/python/README.md,
    "Budget": the thread is blocked at B and resumed with a new budget);
  * gives the program the `cp` object (the H calls of README.md): stage(),
    answer(), emit(), spawnable computations, and the registrations that
    observe() reads;
  * at observe(), reads the registered objects and renders them with an
    iterative equivalent of repr(), and reads the store figures of the mode.

It never orders, chooses, retries, suspends, searches or combines anything on
the program's behalf. Instructions executed by this file's own code, and by
any code it calls (threading's waits, for instance) while a computation is
inside an H call, are not counted.
"""

import marshal
import os
import sys
import threading
import time

_mon = sys.monitoring
_E = _mon.events
_TOOL = 4
_DISABLE = _mon.DISABLE
_gid = threading.get_ident

# ------------------------------------------------------------ channel ---

_CTL_IN = int(sys.argv[1])
_CTL_OUT = int(sys.argv[2])
_wlock = threading.Lock()


def _send(msg):
    data = marshal.dumps(msg)
    frame = len(data).to_bytes(4, "big") + data
    with _wlock:
        view = memoryview(frame)
        while view:
            n = os.write(_CTL_OUT, view)
            view = view[n:]


def _recv_exact(n):
    buf = bytearray()
    while len(buf) < n:
        chunk = os.read(_CTL_IN, n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return bytes(buf)


def _recv():
    head = _recv_exact(4)
    if head is None:
        return None
    data = _recv_exact(int.from_bytes(head, "big"))
    if data is None:
        return None
    return marshal.loads(data)


# ------------------------------------------------- computations, counts ---

class _TS:
    """Per-thread counter. hold is true while the thread is inside an H call
    (or is one of the runtime's own threads): nothing is counted then."""
    __slots__ = ("n", "lim", "hold", "comp")

    def __init__(self, comp, hold=False):
        self.n = 0
        self.lim = 0
        self.hold = hold
        self.comp = comp


class _Comp:
    def __init__(self, name):
        self.name = name
        self.threads = []
        self.limit = 0
        self.exhausted = False
        self.resume = threading.Event()
        self.status = "new"          # new, running, waiting-stage, paused, ended, blocked
        self.ops = {}
        self.ops_start = {}
        self.inbox = []
        self.cond = threading.Condition()
        self.bindings = None
        self.pending = {}
        self.suspended = {}
        self.held = {}
        self.problem_alts = {}
        self.stage = None
        self.alts_at_budget = None
        self.blocked_frame = None

    def total(self):
        return sum(t.n for t in self.threads)

    def set_window(self, budget):
        """A new budget window: budget more instructions from now."""
        self.limit = self.total() + budget
        self.ops_start = dict(self.ops)
        for t in self.threads:
            t.lim = self.limit if len(self.threads) == 1 else t.n


_TSMAP = {}          # thread ident -> _TS
_PARENT = {}         # id(Thread object) -> _Comp of the thread that started it
_COMPS = {}          # name -> _Comp
_REGISTERED = {}     # name -> function, from cp.computation()
_RELS = {}           # code object -> relation name, from cp.relations()
_RT = set()          # this file's code objects: never counted
_CFG = {}
_main_thread_ident = _gid()


def _cb_instruction(code, offset):
    if code in _RT:
        return _DISABLE
    ts = _TSMAP.get(_gid())
    if ts is None or ts.hold:
        return None
    ts.n += 1
    if ts.n > ts.lim:
        _over(ts)
    return None


def _over(ts):
    c = ts.comp
    if len(c.threads) == 1:
        if ts.n <= c.limit:
            ts.lim = c.limit
            return
    else:
        if c.total() <= c.limit:
            ts.lim = ts.n          # several threads: check at every instruction
            return
    # This instruction would be number limit+1 of the computation's window:
    # it is not counted, and the thread waits here until a new budget.
    ts.n -= 1
    _pause(c)
    ts.n += 1
    ts.lim = c.limit if len(c.threads) == 1 else ts.n


def _pause(c):
    if not c.exhausted:
        c.exhausted = True
        c.status = "paused"
        c.alts_at_budget = _count_all(c.pending)
        _flush_std()
        _send({"ev": "budget", "comp": c.name, "count": c.total()})
    ev = c.resume
    ev.wait()


_BOOT = threading.Thread._bootstrap.__code__
_START = threading.Thread.start.__code__


def _cb_py_start(code, offset):
    if code is _START:
        ts = _TSMAP.get(_gid())
        if ts is not None and ts.comp is not None:
            try:
                _PARENT[id(sys._getframe(1).f_locals["self"])] = ts.comp
            except Exception:
                pass
        return None
    if code is _BOOT:
        try:
            th = sys._getframe(1).f_locals["self"]
        except Exception:
            th = None
        parent = _PARENT.pop(id(th), None)
        if parent is None:
            _TSMAP[_gid()] = _TS(None, hold=True)
        else:
            ts = _TS(parent)
            parent.threads.append(ts)
            for t in parent.threads:
                t.lim = t.n
            _TSMAP[_gid()] = ts
        return None
    name = _RELS.get(code)
    if name is not None:
        ts = _TSMAP.get(_gid())
        if ts is not None and ts.comp is not None and not ts.hold:
            ops = ts.comp.ops
            ops[name] = ops.get(name, 0) + 1
    return None


def _hold():
    ts = _TSMAP.get(_gid())
    if ts is None:
        ts = _TS(None, hold=True)
        _TSMAP[_gid()] = ts
        return ts, True
    was = ts.hold
    ts.hold = True
    return ts, was


def _flush_std():
    for f in (sys.stdout, sys.stderr):
        try:
            f.flush()
        except Exception:
            pass


def _count(obj):
    """Entries of a registered structure: len() where it has one; for a
    generator or coroutine, 1 while it is suspended, else 0."""
    try:
        return len(obj)
    except TypeError:
        pass
    for attr in ("gi_frame", "cr_frame", "ag_frame"):
        if hasattr(obj, attr):
            return 0 if getattr(obj, attr) is None else 1
    return None


def _count_all(d):
    tot = 0
    for o in d.values():
        n = _count(o)
        if n is not None:
            tot += n
    return tot


# ------------------------------------------------------------- render ---

_CONTAINERS = (list, tuple, dict, set, frozenset)


def render(obj, faults):
    """repr(obj), computed iteratively for list, tuple, dict, set and
    frozenset (whose repr recurses through C and fails on deep nesting);
    repr() itself for every other object."""
    out = []
    stack = [(0, obj)]
    path = set()
    while stack:
        tag, x = stack.pop()
        if tag == 1:
            out.append(x)
            continue
        if tag == 2:
            path.discard(x)
            continue
        t = type(x)
        if t not in _CONTAINERS:
            try:
                out.append(repr(x))
            except BaseException as e:  # noqa: BLE001 - recorded, never hidden
                faults.append("observe: repr() of a %s failed: %s: %s" % (t.__name__, type(e).__name__, e))
                out.append("<repr failed: %s>" % type(e).__name__)
            continue
        if id(x) in path:
            out.append("[...]" if t is list else "{...}" if t is dict else "(...)")
            continue
        items = list(x.items()) if t is dict else list(x)
        if t is list:
            open_, close = "[", "]"
        elif t is tuple:
            open_, close = "(", ",)" if len(items) == 1 else ")"
        elif t is dict:
            open_, close = "{", "}"
        elif t is set:
            if not items:
                out.append("set()")
                continue
            open_, close = "{", "}"
        else:
            if not items:
                out.append("frozenset()")
                continue
            open_, close = "frozenset({", "})"
        path.add(id(x))
        seq = [(1, open_)]
        for i, it in enumerate(items):
            if i:
                seq.append((1, ", "))
            if t is dict:
                seq.append((0, it[0]))
                seq.append((1, ": "))
                seq.append((0, it[1]))
            else:
                seq.append((0, it))
        seq.append((1, close))
        seq.append((2, id(x)))
        stack.extend(reversed(seq))
    return "".join(out)


# ------------------------------------------------------------ the H API ---

class Stage:
    """What cp.stage() returns: the stage being posed. k is its number;
    replay is true when an earlier stage is being replayed in a reposed run;
    commitment is, for a replayed commit stage (P11), the verbatim answer the
    commit stage first gave, else None; params are the instance's
    parameters (n, order, answers, cap, spawn_order) as harnesses/stages.json
    gives them; constants is the dict of the constants the program's block
    tags with this stage (README.md, 3.1), given with it and only with it."""
    __slots__ = ("k", "replay", "commitment", "params", "constants")

    def __init__(self, k, replay, commitment, params, constants):
        self.k = k
        self.replay = replay
        self.commitment = commitment
        self.params = params
        self.constants = constants

    def __repr__(self):
        return "Stage(k=%r, replay=%r, commitment=%r)" % (self.k, self.replay, self.commitment)


class _CP:
    """The harness calls a program makes (H). See harnesses/python/README.md."""

    def __init__(self, params):
        self.params = dict(params)

    def stage(self):
        ts, was = _hold()
        try:
            if _gid() != _main_thread_ident:
                raise RuntimeError("cp.stage() may be called only by the program's main thread")
            c = _COMPS["main"]
            _flush_std()
            with c.cond:
                if not c.inbox:
                    c.status = "waiting-stage"
                    _send({"ev": "want", "comp": "main", "count": c.total(),
                           "last": None if c.stage is None else c.stage.k})
                    while not c.inbox:
                        c.cond.wait()
                s = c.inbox.pop(0)
            if s is None:
                c.status = "ended-stages"
                return None
            c.stage = s
            c.status = "running"
            _send({"ev": "recv", "comp": "main", "k": s.k, "replay": s.replay, "count": c.total()})
            return s
        finally:
            ts.hold = was

    def answer(self, value):
        ts, was = _hold()
        try:
            text = value if type(value) is str else str(value)
            sys.stdout.write(text + "\n")
            c = ts.comp
            st = _COMPS["main"].stage
            msg = {"ev": "answer", "comp": None if c is None else c.name, "text": text,
                   "count": None if c is None else c.total(),
                   "pstage": None if st is None else st.k,
                   "replay": bool(st is not None and st.replay)}
            if _CFG.get("mode") == "storage" and c is not None:
                msg["alts"] = _count_all(c.pending)
            _send(msg)
        finally:
            ts.hold = was

    def emit(self, m):
        ts, was = _hold()
        try:
            st = _COMPS["main"].stage
            _send({"ev": "emit", "entry": m if type(m) is str else str(m),
                   "comp": None if ts.comp is None else ts.comp.name,
                   "pstage": None if st is None else st.k,
                   "replay": bool(st is not None and st.replay)})
        finally:
            ts.hold = was

    def _comp(self, ts):
        return ts.comp if ts.comp is not None else _COMPS["main"]

    def bindings(self, mapping):
        ts, was = _hold()
        try:
            self._comp(ts).bindings = mapping
        finally:
            ts.hold = was

    def pending(self, name, obj):
        ts, was = _hold()
        try:
            self._comp(ts).pending[str(name)] = obj
        finally:
            ts.hold = was

    def suspended(self, name, obj):
        ts, was = _hold()
        try:
            self._comp(ts).suspended[str(name)] = obj
        finally:
            ts.hold = was

    def held(self, name, obj):
        ts, was = _hold()
        try:
            self._comp(ts).held[str(name)] = obj
        finally:
            ts.hold = was

    def problem_alternatives(self, name, obj):
        ts, was = _hold()
        try:
            self._comp(ts).problem_alts[str(name)] = obj
        finally:
            ts.hold = was

    def relations(self, **functions):
        ts, was = _hold()
        try:
            for name, fn in functions.items():
                code = getattr(fn, "__code__", None)
                if code is None:
                    raise TypeError("cp.relations(%s=...): not a Python function" % name)
                _RELS[code] = name
                if _CFG.get("mode") == "cost":
                    _mon.set_local_events(_TOOL, code, _mon.get_local_events(_TOOL, code) | _E.PY_START)
        finally:
            ts.hold = was

    def computation(self, name, fn):
        ts, was = _hold()
        try:
            _REGISTERED[str(name)] = fn
        finally:
            ts.hold = was


_RENDER_ORDER = ("bindings", "pending", "suspended", "held", "problem_alternatives")


# ----------------------------------------------------------- observe() ---

def _frame_desc(ident):
    f = sys._current_frames().get(ident)
    if f is None:
        return None
    return "%s:%d in %s" % (f.f_code.co_filename, f.f_lineno, f.f_code.co_name)


def _observe(msg):
    faults = []
    out = {"ev": "obs", "faults": faults}
    mode = _CFG["mode"]
    if mode == "storage":
        import tracemalloc
        cur, peak = tracemalloc.get_traced_memory()
        out["store"] = {"traced_current": cur, "traced_peak": peak,
                        "blocks": sys.getallocatedblocks(),
                        "blocks_start": _CFG.get("blocks_start"),
                        "traced_start": _CFG.get("traced_start")}
    if _CFG.get("rusage"):
        import resource
        ru = resource.getrusage(resource.RUSAGE_SELF)
        out["rusage"] = {"cpu": ru.ru_utime + ru.ru_stime, "maxrss": ru.ru_maxrss}
    if mode == "storage":
        import gc
        gc.collect()
        gens = cors = agens = 0
        for o in gc.get_objects():
            t = type(o).__name__
            if t == "generator" and o.gi_frame is not None and o.gi_code not in _RT:
                gens += 1
            elif t == "coroutine" and o.cr_frame is not None:
                cors += 1
            elif t == "async_generator" and o.ag_frame is not None:
                agens += 1
        out["gc"] = {"generators": gens, "coroutines": cors, "async_generators": agens}
    comps = {}
    lines = []
    for name in msg["comps"]:
        c = _COMPS.get(name)
        if c is None:
            continue
        d = {"count": c.total(), "status": c.status, "exhausted": c.exhausted,
             "ops": {k: v - c.ops_start.get(k, 0) for k, v in c.ops.items() if v - c.ops_start.get(k, 0)},
             "alts_at_budget": c.alts_at_budget, "blocked_frame": c.blocked_frame,
             "pending": {}, "suspended": {}, "problem_alts": {}, "bindings": None,
             "exposed": bool(c.bindings is not None or c.pending or c.suspended or c.held or c.problem_alts)}
        if c.bindings is not None:
            b = {}
            try:
                for key in list(c.bindings):
                    b[str(key)] = render(c.bindings[key], faults)
                d["bindings"] = b
            except BaseException as e:  # noqa: BLE001
                faults.append("observe: reading the bindings of %s failed: %r" % (name, e))
            lines.append("%s.bindings = %s" % (name, render(c.bindings, faults)))
        for cat, reg in (("pending", c.pending), ("suspended", c.suspended),
                         ("held", c.held), ("problem_alternatives", c.problem_alts)):
            for key, obj in reg.items():
                n = _count(obj)
                if cat == "pending":
                    d["pending"][key] = n
                elif cat == "suspended":
                    d["suspended"][key] = n
                elif cat == "problem_alternatives":
                    d["problem_alts"][key] = n
                lines.append("%s.%s[%s] = %s" % (name, cat, key, render(obj, faults)))
        comps[name] = d
    out["comps"] = comps
    out["raw"] = "".join(line + "\n" for line in lines)
    return out


# ----------------------------------------------------------- watcher ---

def _watcher():
    """Reports quiescence: every running computation alive but executing no
    instruction over 5 samples 0.1 s apart (a thread blocked in a wait). It
    reports; it never wakes, stops or schedules anything."""
    _TSMAP[_gid()] = _TS(None, hold=True)
    last = None
    quiet = 0
    while True:
        time.sleep(0.1)
        running = [c for c in list(_COMPS.values()) if c.status == "running"]
        if not running:
            last, quiet = None, 0
            continue
        snap = tuple((c.name, c.total()) for c in running)
        if snap == last:
            quiet += 1
        else:
            last, quiet = snap, 0
        if quiet >= 5:
            frames = {}
            for c in running:
                c.status = "blocked"
                idents = [i for i, t in list(_TSMAP.items()) if t.comp is c]
                c.blocked_frame = "; ".join(filter(None, (_frame_desc(i) for i in idents))) or None
                frames[c.name] = c.blocked_frame
            _send({"ev": "quiescent", "comps": frames})
            last, quiet = None, 0


# ----------------------------------------------------------- control ---

def _spawn(name, budget):
    fn = _REGISTERED.get(name)
    if fn is None:
        _send({"ev": "nospawn", "comp": name})
        return
    c = _Comp(name)
    _COMPS[name] = c
    ts = _TS(c)
    c.threads.append(ts)
    c.set_window(budget)
    c.stage = _COMPS["main"].stage

    def body():
        _TSMAP[_gid()] = ts
        c.status = "running"
        how, err = "returned", None
        try:
            fn()
        except BaseException as e:  # noqa: BLE001 - the program's error, verbatim
            ts.hold = True
            c.status = "ended"
            how, err = "error", _format_exc(e, c)
            sys.stderr.write(err)
        ts.hold = True
        c.status = "ended"
        _flush_std()
        _send({"ev": "done", "comp": name, "how": how, "error": err, "count": c.total()})

    th = threading.Thread(target=body, name="cp-" + name, daemon=True)
    th.start()
    _send({"ev": "started", "comp": name})


def _control():
    _TSMAP[_gid()] = _TS(None, hold=True)
    main = _COMPS["main"]
    while True:
        msg = _recv()
        if msg is None:
            os._exit(70)
        op = msg["op"]
        if op == "pose":
            if msg.get("reset"):
                main.set_window(msg["budget"])
                main.exhausted = False
                if _CFG["mode"] == "storage":
                    import tracemalloc
                    tracemalloc.reset_peak()
                    _CFG["blocks_start"] = sys.getallocatedblocks()
                    _CFG["traced_start"] = tracemalloc.get_traced_memory()[0]
            s = Stage(msg["k"], msg["replay"], msg.get("commitment"), _CFG["params"], msg.get("constants") or {})
            with main.cond:
                main.inbox.append(s)
                main.cond.notify_all()
        elif op == "continue":
            c = _COMPS[msg["comp"]]
            c.set_window(msg["budget"])
            c.exhausted = False
            c.alts_at_budget = None
            if _CFG["mode"] == "storage" and c.name == "main":
                import tracemalloc
                tracemalloc.reset_peak()
                _CFG["blocks_start"] = sys.getallocatedblocks()
                _CFG["traced_start"] = tracemalloc.get_traced_memory()[0]
            c.status = "running"
            ev, c.resume = c.resume, threading.Event()
            ev.set()
        elif op == "spawn":
            _spawn(msg["comp"], msg["budget"])
        elif op == "observe":
            try:
                _send(_observe(msg))
            except BaseException as e:  # noqa: BLE001
                _send({"ev": "obs", "faults": ["observe failed: %r" % (e,)], "comps": {}, "raw": ""})
        elif op == "end":
            with main.cond:
                main.inbox.append(None)
                main.cond.notify_all()
            _FINAL.set()


_FINAL = threading.Event()
_SOURCE = []


def _format_exc(e, me):
    """The traceback, as the interpreter would print it, without this file's
    frames. Formatting runs Python code (the traceback module); while it
    runs, instruction events are switched off when no other computation is
    running, since it is never counted and is slow under the callback."""
    quiet = not any(c.status in ("running", "blocked") for c in list(_COMPS.values()) if c is not me)
    if quiet:
        _mon.set_events(_TOOL, 0)
    try:
        import linecache
        import traceback
        # tracebacks show the text the program was compiled from, never the
        # file on disk (which holds every stage's constants)
        if _SOURCE:
            lines = _SOURCE[0].splitlines(True)
            linecache.cache[_CFG["program"]] = (len(_SOURCE[0]), None, lines, _CFG["program"])
        tb = e.__traceback__
        while tb is not None and tb.tb_frame.f_code in _RT:
            tb = tb.tb_next
        return "".join(traceback.format_exception(type(e), e, tb))
    finally:
        if quiet:
            _mon.set_events(_TOOL, _E.INSTRUCTION)


def _collect_codes(code, acc):
    acc.add(code)
    for k in code.co_consts:
        if type(k) is type(code):
            _collect_codes(k, acc)


def _init_rt():
    g = globals()
    for v in list(g.values()):
        objs = [v]
        if isinstance(v, type) and v.__module__ == __name__:
            objs = list(vars(v).values())
        for o in objs:
            code = getattr(o, "__code__", None)
            if code is not None and code.co_filename == __file__:
                _collect_codes(code, _RT)


def main():
    init = _recv()
    _CFG.update(init)
    _init_rt()
    prog = init["program"]
    # The program's text comes from run, with its constants block emptied; the
    # file itself is never read here, so no stage's constants are in this
    # process before that stage is posed.
    source = init.pop("source")
    _CFG.pop("source", None)
    _SOURCE.append(source)
    code = compile(source, prog, "exec", dont_inherit=True)
    mod = type(sys)("__main__")
    mod.__file__ = prog
    mod.__builtins__ = __builtins__
    mod.cp = _CP(init["params"])
    sys.modules["__main__"] = mod
    sys.argv = [prog]
    sys.path[0:0] = [os.path.dirname(prog)]

    mc = _Comp("main")
    _COMPS["main"] = mc
    mts = _TS(mc)
    mc.threads.append(mts)
    _TSMAP[_gid()] = mts
    mc.set_window(init["budget"])
    mc.status = "running"

    threading.Thread(target=_control, name="cp-control", daemon=True).start()
    threading.Thread(target=_watcher, name="cp-watcher", daemon=True).start()

    if init["mode"] == "storage":
        import tracemalloc
        tracemalloc.start(1)
        _CFG["blocks_start"] = sys.getallocatedblocks()
        _CFG["traced_start"] = 0
    _mon.use_tool_id(_TOOL, "cp-harness")
    _mon.register_callback(_TOOL, _E.INSTRUCTION, _cb_instruction)
    _mon.register_callback(_TOOL, _E.PY_START, _cb_py_start)
    _mon.set_local_events(_TOOL, _BOOT, _E.PY_START)
    _mon.set_local_events(_TOOL, _START, _E.PY_START)
    status, how, err = 0, "returned", None
    _mon.set_events(_TOOL, _E.INSTRUCTION)
    try:
        exec(code, mod.__dict__)
    except SystemExit as e:
        mts.hold = True
        mc.status = "ended"
        how = "exit"
        if e.code is None:
            status = 0
        elif isinstance(e.code, int):
            status = e.code
        else:
            sys.stderr.write(str(e.code) + "\n")
            status = 1
    except BaseException as e:  # noqa: BLE001 - the program's error, verbatim
        mts.hold = True
        mc.status = "ended"
        how, err = "error", _format_exc(e, mc)
        sys.stderr.write(err)
        status = 1
    mts.hold = True
    mc.status = "ended"
    _flush_std()
    _send({"ev": "end", "comp": "main", "how": how, "error": err, "status": status,
           "count": mc.total()})
    _FINAL.wait()
    _flush_std()
    os._exit(status)


if __name__ == "__main__":
    main()
