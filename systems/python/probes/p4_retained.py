"""P4. Retained logical state: what can be counted at an observation point.

  stack     a program's own alternative stack: its length, and its maximum
            kept by the program itself
  gens      suspended generator frames, by gc.get_objects() and by
            following the program's own references
  gcobjs    what gc.get_objects() does and does not list
  blocks    sys.getallocatedblocks() as a count of live allocator blocks
  frames    depth of the Python call stack at a point
"""
import gc
import inspect
import sys


# ---- stack: a depth-first enumeration with an explicit stack --------------
def dfs_bits(k):
    """All bit strings of length k, depth first, with an explicit stack of
    pending alternatives. Returns (answers, peak stack length)."""
    stack = [()]
    peak = 1
    out = 0
    while stack:
        s = stack.pop()
        if len(s) == k:
            out += 1
            continue
        stack.append(s + (1,))
        stack.append(s + (0,))
        if len(stack) > peak:
            peak = len(stack)
    return out, peak


# ---- gens: nested generators -----------------------------------------------
def bits(k):
    if k == 0:
        yield ()
        return
    for b in (0, 1):
        for rest in bits(k - 1):
            yield (b,) + rest


def live_generators():
    gc.collect()
    return sum(1 for o in gc.get_objects()
               if inspect.isgenerator(o) and o.gi_frame is not None)


def chain_length_locals(g):
    """Follow generators found among the suspended frame's locals."""
    n = 0
    while g is not None and g.gi_frame is not None:
        n += 1
        g = next((v for v in g.gi_frame.f_locals.values()
                  if inspect.isgenerator(v)), None)
    return n


def chain_length_referents(g):
    """Follow generators among gc.get_referents(g), which includes the
    iterator a suspended for loop holds on the frame's value stack."""
    n = 0
    while g is not None and g.gi_frame is not None:
        n += 1
        g = next((v for v in gc.get_referents(g)
                  if inspect.isgenerator(v)), None)
    return n


def frame_depth():
    f, d = sys._getframe(1), 0
    while f is not None:
        d += 1
        f = f.f_back
    return d


def main():
    print("python", sys.version.split()[0])

    print("[stack] dfs_bits(k): answers, peak length of the program's stack")
    for k in (4, 8, 16):
        print(f"  k={k:2} {dfs_bits(k)}")

    print("[gens] bits(k) suspended after its first answer")
    base = live_generators()
    for k in (4, 8, 16):
        g = bits(k)
        first = next(g)
        print(f"  k={k:2} first={first[:4]}... live generators (gc)={live_generators() - base}"
              f" chain via f_locals={chain_length_locals(g)}"
              f" chain via gc.get_referents={chain_length_referents(g)}")
        del g
    print("  after del:", live_generators() - base)

    print("[gcobjs] which objects gc.get_objects() lists")
    gc.collect()
    tracked = {id(o) for o in gc.get_objects()}
    samples = {
        "int 10**9": 10**9,
        "str built": "x" * 50,
        "tuple of ints": tuple(range(3)),
        "tuple holding a list": ([],),
        "list": [1, 2],
        "dict of str->int": {"a": 1},
        "cons cell (1, ())": (1, ()),
    }
    gc.collect()
    tracked = {id(o) for o in gc.get_objects()}
    for name, o in samples.items():
        print(f"  {name:22} listed={id(o) in tracked} is_tracked={gc.is_tracked(o)}")
    a = len(gc.get_objects())
    b = len(gc.get_objects())
    print(f"  len(gc.get_objects()) twice in a row: {a} {b}")

    print("[blocks] sys.getallocatedblocks() around keeping 10^4 cons cells")
    def cons_list(n):
        s = ()
        for i in range(n):
            s = (1000 + i, s)
        return s
    gc.collect()
    b0 = sys.getallocatedblocks()
    s = cons_list(10**4)
    b1 = sys.getallocatedblocks()
    del s
    gc.collect()
    b2 = sys.getallocatedblocks()
    print(f"  before={b0} kept={b1} (+{b1 - b0}) after del={b2} (+{b2 - b0})")

    print("[frames] Python frame depth at a point")
    def down(k):
        return frame_depth() if k == 0 else down(k - 1)
    print("  depth at top:", frame_depth(), " inside down(50):", down(50))


if __name__ == "__main__":
    main()
