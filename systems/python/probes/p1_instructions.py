"""P1. Instruction counts: sys.monitoring INSTRUCTION vs settrace opcodes,
and how much work hides inside one instruction.

Prints, for each workload and n, the result checksum without counting,
with monitoring and with settrace, and the two counts."""
import sys
import meter

# Built-in work: a handful of instructions whatever n is.
def rev_method(xs):
    ys = xs.copy()
    ys.reverse()
    return ys

def rev_slice(xs):
    return xs[::-1]

def rev_reversed(xs):
    return list(reversed(xs))

def sum_builtin(xs):
    return sum(xs)

def sorted_builtin(xs):
    return sorted(xs, reverse=True)

# Explicit work: instructions grow with n.
def rev_loop(xs):
    ys = []
    i = len(xs) - 1
    while i >= 0:
        ys.append(xs[i])
        i -= 1
    return ys

def sum_loop(xs):
    k = 0
    for x in xs:
        k += x
    return k

WORK = [rev_method, rev_slice, rev_reversed, rev_loop,
        sum_builtin, sum_loop, sorted_builtin]


def digest(r):
    if isinstance(r, list):
        return (len(r), r[0], r[-1], sum(r))
    return r


def main():
    print("python", sys.version.split()[0])
    if meter.HAVE_MON:
        print("monitoring: meter frame instructions (excluded from counts):",
              meter.overhead_mon())
    print("trace: opcode events for a no-op fn:",
          meter.count_trace(meter._noop)[1])
    print(f"{'workload':15} {'n':>7} {'mon':>9} {'trace':>9} same_result")
    for f in WORK:
        for n in (10**2, 10**3, 10**4, 10**5):
            xs = list(range(1, n + 1))
            plain = digest(f(xs))
            rt, ct = meter.count_trace(f, xs)
            if meter.HAVE_MON:
                rm, cm = meter.count_mon(f, xs)
                same = plain == digest(rm) == digest(rt)
            else:
                cm, same = "-", plain == digest(rt)
            print(f"{f.__name__:15} {n:>7} {cm!s:>9} {ct:>9} {same}")


if __name__ == "__main__":
    main()
