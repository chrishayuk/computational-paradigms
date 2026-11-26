"""P1b. Do both meters count a function's first execution? And are repeated
counts in one process the same?

Four copies of the same function are made, so that each starts with a code
object that has never run. Each is put through a different history and then
counted three times by each meter."""
import sys
import meter

SRC = '''
def f(xs):
    k = 0
    for x in xs:
        k += x
    return k
'''


def fresh():
    ns = {}
    exec(compile(SRC, "<f>", "exec"), ns)
    return ns["f"]


xs = [1, 2, 3]
print("python", sys.version.split()[0])

f = fresh()
print("trace first, never run before :", [meter.count_trace(f, xs)[1] for _ in range(3)])

f = fresh()
f(xs)
print("plain call, then trace        :", [meter.count_trace(f, xs)[1] for _ in range(3)])

if meter.HAVE_MON:
    f = fresh()
    print("monitoring first              :", [meter.count_mon(f, xs)[1] for _ in range(3)])
    f = fresh()
    meter.count_mon(f, xs)
    print("monitoring once, then trace   :", [meter.count_trace(f, xs)[1] for _ in range(3)])
    f = fresh()
    for _ in range(1000):  # let the specialising interpreter adapt it
        f(xs)
    print("1000 plain calls, then mon    :", [meter.count_mon(f, xs)[1] for _ in range(3)])
