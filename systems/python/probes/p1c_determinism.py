"""P1c. Determinism of instruction counts across runs.

Three functions search a collection for a target and stop when found:
- in a list (order fixed by the program);
- in a set of strings (order depends on str hashes, so on PYTHONHASHSEED);
- in a set of plain objects (hash from id(), so from memory addresses).
Run this file several times with different PYTHONHASHSEED values."""
import os
import sys
import meter

WORDS = [f"w{i}" for i in range(200)]


class Node:
    __slots__ = ("k",)

    def __init__(self, k):
        self.k = k


def find(coll, pred):
    steps = 0
    for x in coll:
        steps += 1
        if pred(x):
            return steps
    return -1


def main():
    lst = list(WORDS)
    st = set(WORDS)
    nodes = [Node(i) for i in range(200)]
    ns = set(nodes)
    is_w100 = lambda x: x == "w100"
    is_n100 = lambda x: x.k == 100
    out = [
        ("list of str", meter.count_mon(find, lst, is_w100)),
        ("set of str", meter.count_mon(find, st, is_w100)),
        ("set of objects (id hash)", meter.count_mon(find, ns, is_n100)),
    ]
    seed = os.environ.get("PYTHONHASHSEED", "unset")
    print("python", sys.version.split()[0], "PYTHONHASHSEED=" + seed)
    for name, (pos, n) in out:
        print(f"  {name:26} position={pos:4} instructions={n}")


if __name__ == "__main__":
    main()
