"""P5. Recursion limits for recursive definitions.

Each case runs in a child process (the same interpreter), so that a crash
of the child is observed and reported, not suffered. Cases:

  range     rng(1, n) over cons cells, recursive as the definition is
  sum       sm(s) of that range, recursive
  eq        s == t on two equal cons lists of length n (C recursion)
  repr      repr(s) (C recursion)
  viaC      a Python recursion whose every level passes through a C call
            (list(map(f, ...)))

for n in 10^4, 10^5 (and 10^6 for range), at the default recursion limit and
at sys.setrecursionlimit(10**7); and, by bisection in a child, the largest n
for which eq, repr and viaC still work."""
import subprocess
import sys

CHILD = r'''
import sys
lim, case, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
if lim != "default":
    sys.setrecursionlimit(int(lim))
def rng(m, k):
    return () if m > k else (m, rng(m + 1, k))
def sm(s):
    return 0 if not s else s[0] + sm(s[1])
def build(k):              # iterative, so that only the case under test recurses
    s = ()
    for i in range(k, 0, -1):
        s = (i, s)
    return s
def viaC(k):
    return 0 if k == 0 else 1 + list(map(viaC, [k - 1]))[0]
if case == "range":
    s = rng(1, n); print("ok head", s[0])
elif case == "sum":
    print("ok", sm(build(n)) == n * (n + 1) // 2)
elif case == "eq":
    print("ok", build(n) == build(n))
elif case == "repr":
    print("ok len", len(repr(build(n))))
elif case == "viaC":
    print("ok", viaC(n))
elif case == "bisect":     # largest n that works, for eq, repr, viaC
    tests = {"eq": lambda k: build(k) == build(k),
             "repr": lambda k: repr(build(k)),
             "viaC": lambda k: viaC(k)}
    out = []
    for name, t in tests.items():
        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi + 1) // 2
            try:
                t(mid); lo = mid
            except RecursionError:
                hi = mid - 1
        out.append(f"{name}={lo}")
    print("largest n that works:", " ".join(out))
'''


def run(lim, case, n):
    p = subprocess.run([sys.executable, "-E", "-s", "-c", CHILD, lim, case, str(n)],
                       capture_output=True, text=True, timeout=120)
    if p.returncode == 0:
        return p.stdout.strip()
    err = [l for l in p.stderr.strip().splitlines() if l.strip()]
    last = err[-1] if err else ""
    sig = f" signal {-p.returncode}" if p.returncode < 0 else f" exit {p.returncode}"
    return (last[:90] + sig).strip()


def main():
    print("python", sys.version.split()[0], "default recursionlimit", sys.getrecursionlimit())
    for lim in ("default", str(10**7)):
        print(f"recursionlimit={lim}")
        for case, ns in (("range", (10**4, 10**5, 10**6)), ("sum", (10**4, 10**5)),
                         ("eq", (10**4, 10**5)), ("repr", (10**4, 10**5)),
                         ("viaC", (10**4, 10**5))):
            for n in ns:
                print(f"  {case:6} n={n:>8}: {run(lim, case, n)}")
        print("  " + run(lim, "bisect", 10**6))


if __name__ == "__main__":
    main()
