# CP-POSING: incremental
#
# PROVENANCE
#   author: implementation-python (an agent: Claude Opus 5.5, claude-opus-5-5), 2026-11-28
#   seen a precursor (absys E01-E09): no
#   primary program of extended for P14b, written before any program was run
#   S mechanisms used: suspension queue (S/suspend.py): Var, deref,
#     Queue.wait, bind, run, held.
#   idioms:
#     - the stage loop, cp calls; a program that reads each stage as it
#       arrives is one computation: harnesses/python/README.md, sections 2
#       ("Posing") and 3; systems/python/README.md, "The same computation"
#     - the counter as a process over a stream of messages whose tail is not
#       yet bound: the process is a goal run(s, c), the count its argument;
#       it waits on the stream's unbound tail and, woken by each message,
#       takes the message by run's case and becomes the goal of the case's
#       body: Shapiro and Takeuchi, "Object oriented programming in
#       Concurrent Prolog", New Generation Computing 1(1), 1983 (a process
#       as a recursive goal over a stream, its state in its arguments);
#       the S mechanisms' docstrings (harnesses/python/S/suspend.py: a goal
#       held until a var is bound)
#     - goals as callable objects of S's queue, waiting on the Var they
#       name: this configuration's P09c and P09d (Goal)
#     - streams as cons cells, <h> ++ t as the pair (h, t), <> as (), the
#       tail a Var: McCarthy, "Recursive functions of symbolic expressions
#       and their computation by machine, Part I", CACM 3(4), 1960
#     - atoms as strings, a message READ(r) as the pair ("read", r)
#
# P14b. Messages as one sequence: one stage, in which the counter receives
# the sequence <INC, INC, READ(r1), INC, READ(r2)>. The messages are a
# stream m, bound at once to the whole sequence, ending in <>; the counter is
# the goal run(m, 0), which takes each message by run's case (case 2 for
# INC, case 3 for READ(r), which binds the Var r to the count) and becomes
# the goal of the case's body, until case 1, run(<>, c), holds.

from S.suspend import Var, Queue, deref

# CONSTANTS BEGIN
# stage 1
MESSAGES = ("inc", "inc", ("read", "r1"), "inc", ("read", "r2"))
# CONSTANTS END

q = Queue()
NIL = ()
stream = Var("m")       # the messages, a stream
reads = {}              # the unknowns READ messages name: name -> Var
failed = []             # relations found not to hold

cp.bindings(reads)
cp.suspended("goals waiting for a binding", q.held)
cp.held("relations found not to hold", failed)


def run(s, c):
    """The relation run(s, c), by its cases in order, c the count before the
    messages s: the unbound Var it must wait on while s is not known; False
    if no case holds; True once the case has been taken (its body's goal
    posted)."""
    t = deref(s)
    if isinstance(t, Var):
        return t
    if t == NIL:                                            # 1. run(<>, c)
        return True
    message, rest = t
    message = deref(message)
    if message == "inc":                                    # 2. run(<inc> ++ s, c)
        q.wait(Run(rest, c + 1))                            #    if run(s, c + 1)
        return True
    if isinstance(message, tuple) and len(message) == 2 and message[0] == "read":
        if not q.bind(message[1], c):                       # 3. run(<read(r)> ++ s, c) if r = c
            return False
        q.wait(Run(rest, c))                                #    and run(s, c)
        return True
    return False


cp.relations(run=run)


def show(t):
    """Output adapter: a stream of messages as the problem writes it, its
    unbound tail as the Var's name."""
    items = []
    t = deref(t)
    while isinstance(t, tuple) and len(t) == 2:
        message = deref(t[0])
        if isinstance(message, tuple):
            items.append("read(%s)" % message[1].name)
        else:
            items.append(str(message))
        t = deref(t[1])
    shown = "⟨" + ",".join(items) + "⟩"
    if isinstance(t, Var):
        return shown + " ++ " + t.name
    return shown


class Run:
    """One application of run, as a goal of the queue: the counter, as a
    process, with the count c it holds before the messages s."""

    def __init__(self, s, c):
        self.s, self.c = s, c

    def __call__(self):
        outcome = run(self.s, self.c)
        if outcome is False:
            failed.append(self)
        elif isinstance(outcome, Var):
            q.wait(self, outcome)

    def __repr__(self):
        return "run(%s, %d)" % (show(self.s), self.c)


def term(message):
    """A message as a term of the stream: READ(r)'s r as the Var named r."""
    if isinstance(message, tuple) and len(message) == 2 and message[0] == "read":
        if message[1] not in reads:
            reads[message[1]] = Var(message[1])
        return ("read", reads[message[1]])
    return message


def report():
    if failed:
        print("no solution: these relations do not hold:", failed)
        return
    told = ["%s = %s" % (r, deref(v)) for r, v in reads.items() if not isinstance(deref(v), Var)]
    if told:
        cp.answer(", ".join(told))


while (st := cp.stage()) is not None:
    if st.k == 1:
        messages = NIL
        for message in reversed(st.constants["MESSAGES"]):
            messages = (term(message), messages)
        q.bind(stream, messages)        # the messages, as one sequence
        q.wait(Run(stream, 0))          # posed with run(m, 0)
    q.run()
    if not st.replay:
        report()
