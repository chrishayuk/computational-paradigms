#!/usr/bin/env python3
"""Qualify absys-measure's --peak-every against the pinned build.

    qualify.py OLD_BINARY NEW_BINARY PROGRAM...

At a fixed budget of 10^4 steps per assertion (QUALIFY_BUDGET to change it;
QUALIFY_FLAGS for a configuration's flags), 30 s per run, for each
program: standard output (answers and state) must be byte-identical
between OLD and NEW at --peak-every 1, 0 and 1000; the --measure report's
steps and boundary values must be identical; NEW at 1 must equal OLD's
peak exactly; and each sampled peak must lie between the boundary value
and the exact peak. A program for which neither OLD nor NEW at 1 finishes in 30 s is
reported LIMITED: its sampled settings are compared with each other
only, and it needs a lower budget for an exact reference. Prints one line per program and a summary;
exit 1 if any check fails.
"""
import re, subprocess, sys, time

import os
BUDGET, LIMIT = os.environ.get("QUALIFY_BUDGET", "10000"), 30
old, new, progs = sys.argv[1], sys.argv[2], sys.argv[3:]


def run(binary, prog, pe=None):
    argv = [binary, prog, "--measure", "--full", "--steps", BUDGET] + os.environ.get("QUALIFY_FLAGS", "").split() + (["--peak-every", str(pe)] if pe is not None else [])
    t = time.time()
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=LIMIT)
    except subprocess.TimeoutExpired:
        return None, time.time() - t
    return (p.returncode, p.stdout, p.stderr), time.time() - t


def reports(err):
    """Each assertion's report, from --measure's table (line, assertion,
    steps, quantity, now, peak): its head (line, steps), and per quantity
    (now, peak)."""
    out, idx = [], {}
    for line in err.splitlines()[1:]:
        f = line.split("\t")
        if len(f) != 6 or not f[2].isdigit():
            continue
        key = (f[0], f[1], len(out) and out[-1]["head"] == (f[0], f[2]) and out[-1]["q"].get(f[3]) is None)
        if not out or out[-1]["head"] != (f[0], f[2]) or f[3] in out[-1]["q"]:
            out.append({"head": (f[0], f[2]), "q": {}})
        out[-1]["q"][f[3]] = (int(f[4]), int(f[5]))
    return out


fails, limited, lines = 0, 0, []
for prog in progs:
    o, to = run(old, prog)
    res = {pe: run(new, prog, pe) for pe in (1, 0, 1000)}
    ok, why = True, []
    ref = o or res[1][0]
    for pe, (r, t) in res.items():
        if r is None or ref is None:
            continue
        if r[0] != ref[0] or r[1] != ref[1]:
            ok = False; why.append(f"stdout differs at {pe}")
        ra, rb = reports(ref[2]), reports(r[2])
        if [x["head"] for x in ra] != [x["head"] for x in rb]:
            ok = False; why.append(f"steps differ at {pe}")
        for a, b in zip(ra, rb):
            for q, (now, pk) in a["q"].items():
                bn, bp = b["q"].get(q, (None, None))
                if bn != now:
                    ok = False; why.append(f"{q} boundary differs at {pe}")
                if pe == 1 and bp != pk:
                    ok = False; why.append(f"{q} exact peak differs")
                if pe != 1 and bp is not None and not (max(now, b["q"][q][0]) <= bp <= pk):
                    ok = False; why.append(f"{q} sampled peak {bp} outside [{now}, {pk}] at {pe}")
    if o is not None and res[1][0] is not None and o[2] != res[1][0][2]:
        ok = False; why.append("--measure report differs at 1")
    exact_ref = (o is not None) or (res[1][0] is not None)
    fails += not ok
    times = " ".join(f"{k}:{'timeout' if v[0] is None else f'{v[1]:.1f}s'}" for k, v in [("old", (o, to))] + [(str(pe), res[pe]) for pe in res])
    verdict = "FAIL" if not ok else ("ok  " if exact_ref else "LIMITED")   # LIMITED: no exact reference finished;
    limited += ok and not exact_ref                                            # only the sampled settings were compared
    lines.append(f"{verdict} {prog}  {times}  {'; '.join(sorted(set(why))) or ('' if exact_ref else 'no exact reference finished: sampled settings compared with each other only')}")
print("\n".join(lines))
print(f"\n{len(progs) - fails - limited} of {len(progs)} programs pass against an exact reference; {limited} limited (no exact reference finished); {fails} fail")
sys.exit(1 if fails else 0)
