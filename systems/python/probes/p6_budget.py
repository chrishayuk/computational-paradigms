"""P6. An instruction budget in Python's own unit.

  stop      a callback on INSTRUCTION events raises BudgetExhausted after B
            instructions; does it stop an endless loop at exactly B?
  catch     can the program under test swallow the budget exception?
            (except Exception, bare except, finally)
  pause     instead of raising, the callback blocks the worker thread at the
            budget; the harness observes, grants a new budget, and the same
            computation continues
  C loop    an endless loop inside one C call executes no instructions:
            the budget cannot see it (child process, killed by a timeout)
  cost      CPU of the budget meter against the plain counter of P1"""
import subprocess
import sys
import threading
import time

mon = sys.monitoring
E = mon.events
T = 4


class BudgetExhausted(BaseException):
    """BaseException, so that 'except Exception' in the program does not
    catch it."""


def run_with_budget(fn, budget, *a, sticky=False):
    """Raise BudgetExhausted at instruction budget+1. With sticky=False the
    meter is switched off as it raises, so that unwinding is not counted.
    With sticky=True every later instruction raises again, so the program
    cannot run on after catching the exception."""
    used = 0
    own = run_with_budget.__code__

    def cb(code, offset):
        nonlocal used
        if code is own:
            return
        used += 1
        if used > budget:
            if not sticky:
                mon.set_events(T, 0)
            raise BudgetExhausted(budget)

    mon.use_tool_id(T, "budget")
    mon.register_callback(T, E.INSTRUCTION, cb)
    mon.set_events(T, E.INSTRUCTION)
    try:
        return ("finished", fn(*a), used)
    except BudgetExhausted as b:
        return ("budget", None, b.args[0])
    finally:
        mon.set_events(T, 0)
        mon.register_callback(T, E.INSTRUCTION, None)
        mon.free_tool_id(T)


def endless():
    k = 0
    while True:
        k += 1


def finite(n):
    k = 0
    for i in range(n):
        k += i
    return k


def swallow_exception():
    try:
        endless()
    except Exception:
        return "caught by except Exception"


def swallow_bare():
    try:
        endless()
    except:  # noqa: E722  (the point of the probe)
        return "caught by bare except"


cleanup_ran = []


def with_finally():
    try:
        endless()
    finally:
        cleanup_ran.append(True)


# ---- pause: block the worker thread at the budget ------------------------
def paused_run(fn, budgets, *a):
    """Run fn in a worker thread. Each time the instructions counted reach
    the current budget the callback blocks; the main thread records the
    state and grants the next budget. Returns the log."""
    used = 0
    limit = budgets[0]
    at_limit = threading.Event()
    resume = threading.Event()
    worker = None
    own = {paused_run.__code__}
    tfile = threading.__file__
    result = []

    def cb(code, offset):
        nonlocal used
        if (threading.current_thread() is not worker or code in own
                or code.co_filename == tfile):
            return
        used += 1
        if used >= limit:
            at_limit.set()
            resume.wait()
            resume.clear()

    def body():
        result.append(fn(*a))

    own.add(body.__code__)
    mon.use_tool_id(T, "budget")
    mon.register_callback(T, E.INSTRUCTION, cb)
    mon.set_events(T, E.INSTRUCTION)
    log = []
    try:
        worker = threading.Thread(target=body)
        worker.start()
        for b in budgets[1:] + [None]:
            while not at_limit.wait(0.01):
                if not worker.is_alive():
                    break
            if not worker.is_alive():
                break
            at_limit.clear()
            log.append(("paused at", used))
            limit = b if b is not None else float("inf")
            resume.set()
        worker.join()
        log.append(("finished", result[0] if result else None, "instructions", used))
    finally:
        mon.set_events(T, 0)
        mon.register_callback(T, E.INSTRUCTION, None)
        mon.free_tool_id(T)
    return log


C_LOOP = r'''
import itertools, sys
mon = sys.monitoring
n = 0
def cb(code, off):
    global n
    n += 1
    if n > 1000:
        raise SystemExit("budget reached")
mon.use_tool_id(4, "b"); mon.register_callback(4, mon.events.INSTRUCTION, cb)
mon.set_events(4, mon.events.INSTRUCTION)
any(itertools.repeat(0))   # never returns; no Python instruction inside
'''


def main():
    print("python", sys.version.split()[0])
    print("[stop]")
    for B in (10, 1000, 10**6):
        print(f"  endless, budget {B}:", run_with_budget(endless, B))
    print("  finite(100), budget 10**6:", run_with_budget(finite, 10**6, 100))
    U = run_with_budget(finite, 10**6, 100)[2]
    print(f"  finite(100), budget {U - 1}:", run_with_budget(finite, U - 1, 100))
    print(f"  finite(100), budget {U}:", run_with_budget(finite, U, 100))

    print("[catch]")
    print("  except Exception:", run_with_budget(swallow_exception, 1000))
    print("  bare except     :", run_with_budget(swallow_bare, 1000))
    print("  finally         :", run_with_budget(with_finally, 1000),
          "cleanup ran:", bool(cleanup_ran))
    cleanup_ran.clear()
    print("  sticky, except Exception:", run_with_budget(swallow_exception, 1000, sticky=True))
    print("  sticky, bare except     :", run_with_budget(swallow_bare, 1000, sticky=True))
    print("  sticky, finally         :", run_with_budget(with_finally, 1000, sticky=True),
          "cleanup ran:", bool(cleanup_ran))

    print("[pause] finite(1000) with budgets 2000, 2000, 2000, then unlimited")
    for entry in paused_run(finite, [2000, 4000, 6000], 1000):
        print("  ", entry)
    import meter
    print("  finite(1000) under meter.count_mon:", meter.count_mon(finite, 1000))

    print("[C loop] budget 1000 around any(itertools.repeat(0)), 5 s timeout")
    try:
        p = subprocess.run([sys.executable, "-E", "-s", "-c", C_LOOP],
                           capture_output=True, text=True, timeout=5)
        print("  exit", p.returncode, p.stderr.strip()[-80:])
    except subprocess.TimeoutExpired:
        print("  not stopped by the budget; killed by the 5 s timeout")

    print("[cost] finite(10**6)")
    t0 = time.process_time(); finite(10**6); t1 = time.process_time()
    run_with_budget(finite, 10**8, 10**6); t2 = time.process_time()
    print(f"  plain {t1 - t0:.3f}s  under budget meter {t2 - t1:.3f}s  ratio {(t2 - t1) / (t1 - t0):.1f}")


if __name__ == "__main__":
    main()
