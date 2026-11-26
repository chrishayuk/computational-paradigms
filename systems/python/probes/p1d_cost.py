"""P1d. Cost and perturbation of the two instruction meters.

- time: an explicit loop of 10^6 iterations, plain and under each meter
  (best of runs 2 and 3, process CPU time);
- store: tracemalloc peak of the same work, with and without the meter;
- depth: the deepest plain recursion reached before RecursionError, at the
  default recursion limit, with and without the meter."""
import sys
import time
import tracemalloc
import meter


def sum_loop(n):
    k = 0
    for x in range(n):
        k += x
    return k


def best(f, *a):
    """Best of 3 runs that return the same result. All three runs are
    printed, since a meter may count nothing on one of them (P1b)."""
    t, rs = [], []
    for _ in range(3):
        t0 = time.process_time()
        rs.append(f(*a))
        t.append(time.process_time() - t0)
    print("   runs:", [(round(x, 3), r[1] if isinstance(r, tuple) else r)
                       for x, r in zip(t, rs)])
    return rs[-1], min(t[1:])


def peak_of(f, *a):
    tracemalloc.start()
    tracemalloc.reset_peak()
    base = tracemalloc.get_traced_memory()[0]
    r = f(*a)
    cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return r, peak - base


def depth_probe():
    d = 0

    def down():
        nonlocal d
        d += 1
        down()

    try:
        down()
    except RecursionError:
        pass
    return d


N = 10**6
print("python", sys.version.split()[0], "recursionlimit", sys.getrecursionlimit())
r0, t0 = best(sum_loop, N)
print(f"time plain        : {t0:.3f}s result={r0}")
if meter.HAVE_MON:
    (r1, n1), t1 = best(meter.count_mon, sum_loop, N)
    print(f"time monitoring   : {t1:.3f}s result={r1} instructions={n1} ratio={t1 / t0:.1f}")
(r2, n2), t2 = best(meter.count_trace, sum_loop, N)
print(f"time settrace     : {t2:.3f}s result={r2} opcode events={n2} ratio={t2 / t0:.1f}")

M = 10**5
print("peak bytes plain      :", peak_of(sum_loop, M)[1])
if meter.HAVE_MON:
    print("peak bytes monitoring :", peak_of(meter.count_mon, sum_loop, M)[1])
print("peak bytes settrace   :", peak_of(meter.count_trace, sum_loop, M)[1])

print("depth plain           :", depth_probe())
if meter.HAVE_MON:
    print("depth monitoring      :", meter.count_mon(depth_probe)[0])
print("depth settrace        :", meter.count_trace(depth_probe)[0])
