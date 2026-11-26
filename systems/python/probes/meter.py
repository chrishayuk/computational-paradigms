"""Counting helpers shared by the probes. Measurement-qualification only:
nothing here is a study program.

count_mon(fn, *a)    -> (result, instructions)   sys.monitoring INSTRUCTION, global
count_trace(fn, *a)  -> (result, opcode events)  sys.settrace + f_trace_opcodes
histogram_mon(fn,*a) -> (result, Counter{opname: n})
"""
import sys
import dis
from collections import Counter

HAVE_MON = hasattr(sys, "monitoring")
TOOL = 4  # any free tool id 0..5; 4 is not one of the named ids


def _noop():
    return None


def count_mon(fn, *a):
    """Count every INSTRUCTION event while fn runs, excluding the
    instructions of the meter's own frame (count_mon's code object), which
    executes a fixed number of them between enabling and disabling."""
    mon = sys.monitoring
    E = mon.events
    n = 0
    own = _OWN

    def cb(code, offset):
        nonlocal n
        if code is not own:
            n += 1

    mon.use_tool_id(TOOL, "meter")
    mon.register_callback(TOOL, E.INSTRUCTION, cb)
    mon.set_events(TOOL, E.INSTRUCTION)
    try:
        r = fn(*a)
    finally:
        mon.set_events(TOOL, 0)
        mon.register_callback(TOOL, E.INSTRUCTION, None)
        mon.free_tool_id(TOOL)
    return r, n


_OWN = count_mon.__code__


def count_mon_raw(fn, *a):
    """As count_mon but counting the meter's own frame too."""
    global _OWN
    saved, _OWN = _OWN, None
    try:
        return count_mon(fn, *a)
    finally:
        _OWN = saved


def overhead_mon():
    """Instructions of the meter's own frame (raw minus filtered, no-op fn)."""
    return count_mon_raw(_noop)[1] - count_mon(_noop)[1]


def count_trace(fn, *a):
    """Count 'opcode' trace events in frames created while tracing is on.
    The calling frame is not traced, so there is no constant overhead
    except the frames of fn itself (counted, as they should be)."""
    n = 0

    def tr(frame, event, arg):
        nonlocal n
        if event == "call":
            frame.f_trace_lines = False
            frame.f_trace_opcodes = True
        elif event == "opcode":
            n += 1
        return tr

    old = sys.gettrace()
    sys.settrace(tr)
    try:
        r = fn(*a)
    finally:
        sys.settrace(old)
    return r, n


def histogram_mon(fn, *a):
    """Per-opcode histogram (slow; for inspection only)."""
    mon = sys.monitoring
    E = mon.events
    at = Counter()

    def cb(code, offset):
        at[(code, offset)] += 1

    mon.use_tool_id(TOOL, "meter")
    mon.register_callback(TOOL, E.INSTRUCTION, cb)
    mon.set_events(TOOL, E.INSTRUCTION)
    try:
        r = fn(*a)
    finally:
        mon.set_events(TOOL, 0)
        mon.register_callback(TOOL, E.INSTRUCTION, None)
        mon.free_tool_id(TOOL)
    names = {}
    h = Counter()
    for (code, off), k in at.items():
        if code not in names:
            names[code] = {i.offset: i.opname for i in dis.get_instructions(code)}
        h[(code.co_name, names[code].get(off, "?"))] += k
    return r, h
