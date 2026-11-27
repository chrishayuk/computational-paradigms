"""Runs the tests of the S mechanisms (harnesses/python/S) and prints their
sizes. Made-up examples only; no problem of the study. From the repository
root, in the pinned image:

    container run --rm --platform linux/amd64 --volume "$PWD":/work --workdir /work \\
        cp-agent-python:spec-1.0 python3 harnesses/python/S/tests/run.py

Output is kept in harnesses/python/S/tests/output.txt.
"""
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[0:0] = [HERE, os.path.dirname(os.path.dirname(HERE))]   # tests/, harnesses/python/
import size  # noqa: E402

failed = total = 0
print(sys.version.split()[0])
for name in sorted(f[:-3] for f in os.listdir(HERE) if f.startswith("test_") and f.endswith(".py")):
    mod = __import__(name)
    for fn in [v for k, v in vars(mod).items() if k.startswith("test_") and callable(v)]:
        total += 1
        try:
            fn()
            print("PASS  %s.%s" % (name, fn.__name__))
        except Exception:
            failed += 1
            print("FAIL  %s.%s\n%s" % (name, fn.__name__, traceback.format_exc()))
print("%d of %d tests passed" % (total - failed, total))
print()
size.main()
sys.exit(1 if failed else 0)
