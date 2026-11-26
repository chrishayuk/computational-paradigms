"""P3. Allocated memory: tracemalloc current and peak, against
resource.getrusage ru_maxrss.

Sections:
  peak      a 10^6-element list is built and freed inside a call; is the
            peak seen after the call returns?
  ints      lists of small cached ints vs larger ints vs a shared object
  strings   interned / constant strings vs built strings
  freelist  floats freed and reallocated
  outside   memory allocated outside the Python allocators (mmap), done
            first, so that ru_maxrss has not already passed it
  maxrss    ru_maxrss of this process and of child processes, with
            tracemalloc off and on; its unit on this platform
  overhead  tracemalloc's own memory, and CPU cost on a build of 10^6 ints
Run twice to check that the tracemalloc figures repeat."""
import mmap
import resource
import sys
import time
import tracemalloc

import meter


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def traced(f, *a):
    """(result, current growth, peak growth) of f, relative to the start."""
    tracemalloc.reset_peak()
    c0 = tracemalloc.get_traced_memory()[0]
    r = f(*a)
    c1, p = tracemalloc.get_traced_memory()
    return r, c1 - c0, p - c0


def build_and_drop(n):
    xs = list(range(1000, 1000 + n))
    return len(xs)


def keep_small_ints(n):
    return [i % 256 for i in range(n)]        # cached ints: list storage only


def keep_large_ints(n):
    return [1000 + i for i in range(n)]       # one new int object each


def keep_same_obj(n):
    return [None] * n


def keep_const_str(n):
    return ["abc" for _ in range(n)]          # one constant string, shared


def keep_built_str(n):
    return [str(1000 + i) for i in range(n)]  # one new str each


def float_churn(n):
    k = 0.0
    for i in range(n):
        x = float(i)                          # freed at once; free list
        k += x
    return k


def mm(nbytes):
    m = mmap.mmap(-1, nbytes)
    for off in range(0, nbytes, 4096):        # touch every page
        m[off] = 1
    return m


def main():
    sys.stdout.reconfigure(line_buffering=True)
    print("python", sys.version.split()[0], sys.platform)
    rss0 = rss()
    tracemalloc.start()
    print("[outside] mmap of 64 MiB, every page touched")
    rss_a = rss()
    r, cur, peak = traced(mm, 64 * 2**20)
    rss_b = rss()
    print(f"  tracemalloc current growth={cur} peak growth={peak}")
    print(f"  ru_maxrss before={rss_a} after={rss_b} growth={rss_b - rss_a}")
    r.close()

    print("[peak] build and drop 10^6 ints inside a call")
    r, cur, peak = traced(build_and_drop, 10**6)
    print(f"  current growth={cur} peak growth={peak}")

    N = 10**5
    print(f"[ints/strings] lists of {N} elements kept (current growth, bytes)")
    keep = []
    for f in (keep_small_ints, keep_large_ints, keep_same_obj,
              keep_const_str, keep_built_str):
        r, cur, peak = traced(f, N)
        keep.append(r)
        print(f"  {f.__name__:16} current={cur:9} peak={peak:9} per_element={cur / N:.1f}")
    del keep

    print("[freelist] 10^5 floats created and freed one at a time")
    r, cur, peak = traced(float_churn, N)
    print(f"  current growth={cur} peak growth={peak}")

    print("[maxrss] process")
    print(f"  ru_maxrss at start={rss0} now={rss()} "
          f"(unit: {'bytes' if sys.platform == 'darwin' else 'KiB'} on {sys.platform})")
    print(f"  tracemalloc own memory={tracemalloc.get_tracemalloc_memory()}")
    tracemalloc.stop()

    print("[overhead] CPU for keep_large_ints(10^6), best of 3")
    def best(f, *a):
        ts = []
        for _ in range(3):
            t0 = time.process_time(); f(*a); ts.append(time.process_time() - t0)
        return min(ts)
    t_off = best(keep_large_ints, 10**6)
    tracemalloc.start()
    t_on = best(keep_large_ints, 10**6)
    tracemalloc.stop()
    tracemalloc.start(25)
    t_on25 = best(keep_large_ints, 10**6)
    tracemalloc.stop()
    print(f"  off={t_off:.3f}s on(1 frame)={t_on:.3f}s ratio={t_on / t_off:.1f} "
          f"on(25 frames)={t_on25:.3f}s ratio={t_on25 / t_off:.1f}")

    print("[maxrss of a child process] keep_large_ints(10^6), tracemalloc off/on")
    import subprocess
    child = ("import resource,sys,tracemalloc;"
             "sys.argv[1]=='on' and tracemalloc.start();"
             "a=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;"
             "xs=[1000+i for i in range(10**6)];"
             "b=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;"
             "t=tracemalloc.get_traced_memory() if tracemalloc.is_tracing() else (0,0);"
             "m=tracemalloc.get_tracemalloc_memory();"
             "print(f'  {sys.argv[1]:3} maxrss start={a} end={b} growth={b-a} traced_peak={t[1]} tracemalloc_own={m}')")
    for mode in ("off", "on", "off", "on"):
        subprocess.run([sys.executable, "-E", "-s", "-c", child, mode], check=True)

    if meter.HAVE_MON:
        print("[steps] instructions of keep_large_ints(10^4), tracemalloc off/on")
        a = meter.count_mon(keep_large_ints, 10**4)[1]
        tracemalloc.start()
        b = meter.count_mon(keep_large_ints, 10**4)[1]
        tracemalloc.stop()
        print(f"  off={a} on={b}")


if __name__ == "__main__":
    main()
