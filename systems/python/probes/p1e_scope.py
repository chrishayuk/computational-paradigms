"""P1e. What a global INSTRUCTION count covers: Python code called back
from C (a sort key), and Python code run in another thread."""
import sys
import threading
import meter

if not meter.HAVE_MON:
    print("python", sys.version.split()[0], ": no sys.monitoring; probe skipped")
    sys.exit(0)

xs = list(range(1000))


def sort_plain():
    return len(sorted(xs))


def sort_key():
    return len(sorted(xs, key=lambda x: -x))


def work():
    k = 0
    for i in range(1000):
        k += i


def two_threads():
    t = threading.Thread(target=work)
    t.start()
    work()
    t.join()


print("python", sys.version.split()[0])
print("sorted(xs)              :", meter.count_mon(sort_plain)[1])
print("sorted(xs, key=lambda)  :", meter.count_mon(sort_key)[1])
print("work() in this thread   :", meter.count_mon(work)[1])
print("work() here and in a new thread:", meter.count_mon(two_threads)[1])
