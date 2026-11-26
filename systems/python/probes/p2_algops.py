"""P2. Counting operations a problem defines, four ways, on tiny
transcriptions of the P13 vocabulary over cons cells (() is the empty
sequence, (h, t) is <h> ++ t). These are probes of counting, not study
programs: they fix no representation or idiom for the study.

Methods:
  A  explicit counters written into the functions (harness-class lines);
  B  wrapper functions rebound to the same global names;
  C  sys.monitoring PY_START events, enabled locally on the chosen code
     objects only (no change to the program text);
  D  sys.setprofile 'call' events filtered by code object.
Each method's counts are checked against the closed forms:
  range(1, n): n + 1 calls;  sum: n + 1;  rev: n + 1 rev, n(n+1)/2 conc;
  revacc: 1 revacc, n + 1 racc."""
import sys
import time
from collections import Counter

sys.setrecursionlimit(5000)

# ---- plain transcriptions (the program as it would be written) ----------
def rng(m, n):
    return () if m > n else (m, rng(m + 1, n))

def sm(s):
    return 0 if not s else s[0] + sm(s[1])

def conc(a, b):
    return b if not a else (a[0], conc(a[1], b))

def rev(a):
    return () if not a else conc(rev(a[1]), (a[0], ()))

def revacc(a):
    return racc(a, ())

def racc(a, c):
    return c if not a else racc(a[1], (a[0], c))

PLAIN = dict(rng=rng, sm=sm, conc=conc, rev=rev, revacc=revacc, racc=racc)

# ---- A: explicit counters -------------------------------------------------
OPS = Counter()

def rng_A(m, n):
    OPS["rng"] += 1
    return () if m > n else (m, rng_A(m + 1, n))

def sm_A(s):
    OPS["sm"] += 1
    return 0 if not s else s[0] + sm_A(s[1])

def conc_A(a, b):
    OPS["conc"] += 1
    return b if not a else (a[0], conc_A(a[1], b))

def rev_A(a):
    OPS["rev"] += 1
    return () if not a else conc_A(rev_A(a[1]), (a[0], ()))

def racc_A(a, c):
    OPS["racc"] += 1
    return c if not a else racc_A(a[1], (a[0], c))

def revacc_A(a):
    OPS["revacc"] += 1
    return racc_A(a, ())


def workload(n, f):
    """P13-shaped: build the range, then sum, rev and revacc it."""
    s = f["rng"](1, n)
    return (f["sm"](s), f["rev"](s)[0], f["revacc"](s)[0])


def expected(n):
    return Counter(rng=n + 1, sm=n + 1, rev=n + 1, conc=n * (n + 1) // 2,
                   revacc=1, racc=n + 1)


def method_none(n):
    return workload(n, PLAIN), None


def method_A(n):
    OPS.clear()
    f = dict(rng=rng_A, sm=sm_A, rev=rev_A, revacc=revacc_A)
    return workload(n, f), Counter(OPS)


def method_B(n):
    counts = Counter()
    g = globals()
    saved = {k: g[k] for k in PLAIN}

    def counted(name, fn):
        def w(*a):
            counts[name] += 1
            return fn(*a)
        return w

    for k, fn in saved.items():
        g[k] = counted(k, fn)
    try:
        r = workload(n, {k: g[k] for k in PLAIN})
    finally:
        g.update(saved)
    return r, counts


def method_C(n):
    mon = sys.monitoring
    T, E = 3, mon.events  # the instruction meter uses 4
    names = {fn.__code__: k for k, fn in PLAIN.items()}
    counts = Counter()

    def cb(code, offset):
        counts[names[code]] += 1

    mon.use_tool_id(T, "ops")
    mon.register_callback(T, E.PY_START, cb)
    for code in names:
        mon.set_local_events(T, code, E.PY_START)
    try:
        r = workload(n, PLAIN)
    finally:
        for code in names:
            mon.set_local_events(T, code, 0)
        mon.register_callback(T, E.PY_START, None)
        mon.free_tool_id(T)
    return r, counts


def method_D(n):
    names = {fn.__code__: k for k, fn in PLAIN.items()}
    counts = Counter()

    def prof(frame, event, arg):
        if event == "call":
            k = names.get(frame.f_code)
            if k:
                counts[k] += 1

    sys.setprofile(prof)
    try:
        r = workload(n, PLAIN)
    finally:
        sys.setprofile(None)
    return r, counts


def main():
    print("python", sys.version.split()[0], "recursionlimit", sys.getrecursionlimit())
    methods = [("none", method_none), ("A counters", method_A),
               ("B wrappers", method_B), ("D setprofile", method_D)]
    if hasattr(sys, "monitoring"):
        methods.insert(3, ("C monitoring", method_C))
    for n in (100, 1000):
        print(f"n={n} expected {dict(sorted(expected(n).items()))}")
        ref = None
        for name, m in methods:
            t0 = time.process_time()
            try:
                r, c = m(n)
            except RecursionError as e:
                print(f"  {name:13} RecursionError: {e}")
                continue
            dt = time.process_time() - t0
            ref = ref or r
            ok = "-" if c is None else (c == expected(n))
            print(f"  {name:13} result={r} same={r == ref} counts_match={ok} cpu={dt:.3f}s")
    # do the counters change the step count?
    if hasattr(sys, "monitoring"):
        import meter
        print("instructions of the n=100 workload, counted by meter.count_mon:")
        for name, m in methods:
            print(f"  {name:13} {meter.count_mon(m, 100)[1]}")
    # depth needed: B adds one Python frame per counted call
    sys.setrecursionlimit(1500)
    print("recursionlimit 1500, n=1000:")
    for name, m in methods:
        try:
            m(1000)
            print(f"  {name:13} ok")
        except RecursionError as e:
            print(f"  {name:13} RecursionError: {e}")


if __name__ == "__main__":
    main()
