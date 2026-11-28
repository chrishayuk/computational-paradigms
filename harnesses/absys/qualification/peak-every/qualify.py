#!/usr/bin/env python3
"""Qualify absys-measure's --peak-every against the pinned build.

    qualify.py OLD_BINARY NEW_BINARY PROGRAM...

At a fixed budget of 10^4 steps per assertion (QUALIFY_BUDGET to change it;
QUALIFY_FLAGS for a configuration's flags), 30 s per run, for each
program: standard output (answers and state) must be byte-identical
between OLD and NEW at --peak-every 1, 0 and 1000; the --measure report's
steps and boundary values must be identical; NEW at 1 must equal OLD's
peak exactly; and each sampled peak must lie between the boundary value
and the exact peak. A run that OLD cannot finish in 30 s is compared on
the settings that finish. Prints one line per program and a summary;
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


fails, lines = 0, []
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
    fails += not ok
    times = " ".join(f"{k}:{'timeout' if v[0] is None else f'{v[1]:.1f}s'}" for k, v in [("old", (o, to))] + [(str(pe), res[pe]) for pe in res])
    lines.append(f"{'ok  ' if ok else 'FAIL'} {prog}  {times}  {'; '.join(sorted(set(why)))}")
print("\n".join(lines))
print(f"\n{len(progs) - fails} of {len(progs)} programs pass")
sys.exit(1 if fails else 0)
