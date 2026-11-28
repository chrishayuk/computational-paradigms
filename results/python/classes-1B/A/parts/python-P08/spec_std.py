from spec_core import H7, ADP, STG, R19H, R19P, R19R, evaluators_equal, shift
THR="METRICS C: engine and thread calls, explicit scheduling, synchronisation (decide when a computation runs)"
EXT="rule 1 (operational only); threading is an external mechanism of stdlib-concurrency, listed"
PERM="rule 2: a guard that both tests which places are known (rule 19, R) and synchronises on a permission flag (whether rev's definition has arrived) is C"
def post(line, what, inner_h=None):
    out=[(f"L{line}","C","pose(...): starts the relation's thread",THR),((f"L{line}",3),"P",what,STG)]
    if inner_h:
        a,b=inner_h
        out+=[((f"L{line}",a),"H","s.constants[...] read",H7),((f"L{line}",b),"P",what+" (rest)",STG)]
    out.append(((f"L{line}",-2),"C","pose(...) (close)",THR))
    return out
def evaluator_rev(d):
    return [
     (f"L{d}","P","evaluator of rev(a, b): header",R19P),
     (f"L{d+3}","C","reverse: a known and rev's definition flagged as arrived",PERM),
     (f"L{d+4}","P","reverse: b computed by rev forwards; no case applies -> does not hold",R19P),
     (f"L{d+7}","R","reverse: test that b is unknown",R19R),
     (f"L{d+8}","P","reverse: b given its value / equation b = r",R19P),
     (f"L{d+10}","R","reverse: verdict to wait",R19R),
    ]
def prefix_ev(d, dead=False):
    if dead:
        return [(f"L{d}","R","prefix evaluator (s = p ++ t): a relation P08b does not have (dead code)","METRICS R: a definition the problem does not give; rule 1")]
    return [
     (f"L{d}","P","evaluator of s = p ++ t: header",R19P),
     (f"L{d+4}","R","prefix: test that s and p are known",R19R),
     (f"L{d+5}","P","prefix: decomposition of s by p, t computed",R19P+"; rule 15"),
     (f"L{d+8}","R","prefix: test that t and p are known",R19R),
     (f"L{d+9}","P","prefix: s computed from p and t",R19P),
     (f"L{d+10}","R","prefix: verdict to wait",R19R),
    ]
def machinery(d):
    """d = line of 'EVALUATOR =' (P08a: 124). Lines relative to it."""
    r=lambda k: f"L{d+k}"
    return [
     (r(0),"R","EVALUATOR table and place()",R19H),
     (r(8),"C","told(): count the news, wake every waiting relation thread",THR),
     (r(17),"R","hold(rel): the thread of one held relation: header, its places",R19H),
     (r(20),"C","with changed: (the relation thread takes the condition's lock)",THR),
     (r(21),"R","hold: evaluate; verdict to wait while the evaluator says None",R19H),
     (r(22),"R","hold: record what waits (waiting.append)",R19R),
     (r(23),"C","hold: busy count, notify, wait_for news",THR),
     (r(27),"R","hold: outcome False -> failed; list -> decided in its stead",R19H),
     (r(31),"C","hold: pose each equation decided in its stead (a new thread each)",THR),
     (r(32),"R","hold: bind the places computed",R19H),
     (r(38),"C","hold: if new: told(); busy count; notify",THR),
     (r(44),"C","arrived(name): set the definition's permission flag and wake the threads",THR),
     (r(51),"C","pose(rel): count busy, start the relation's thread",THR),
     (r(58),"C","settle(): the main thread waits until no relation thread is busy",THR),
     (r(64),"H","show() and report(): output adapters",ADP),
    ]
std_P08a=[
 ("L42","C","import threading",EXT),
 ("L46","P","constants block: stage 6 prefix <42>","README section 7; rule 1"),
 ("L49","P","the sub-problem's unknowns (names)","rule 1"),
 ("L51","C","changed = threading.Condition(): the condition every relation thread waits on",THR),
 ("L53","R","class Unknown and the UNKNOWN table: an unknown represented as a place",R19H),
 ("L64","P","the problem's unknowns bound as places","rule 1"),
 ("L66","R","stores of the holding: known, waiting, failed",R19H),
 ("L69","C","count (busy threads, news) and defined (permission flags for definitions)",THR),
 ("L72","H","cp.bindings / cp.suspended / cp.held",H7),
]+evaluators_equal(78,0,0)+prefix_ev(96)+evaluator_rev(109)+[
 ("L122","H","cp.relations(equal, prefix)",H7),
]+machinery(124)+[
 ("L207","H","stage loop header, stage-1 test",H7),
]+post(209,"stage 1: a = <x, y, z>")+[("L210","H","elif s.k == 2",H7)]+post(211,"stage 2: rev(a, b)")+[
 ("L212","H","elif s.k == 3",H7)]+post(213,"stage 3: x = y")+[
 ("L214","H","elif s.k == 4",H7),
 ("L215","P","stage 4: conc, forwards, by its two cases",'rule 3'),
 ("L221","P","stage 4: rev, forwards, by its two cases",'rule 3; rule 15'),
 ("L227","H","cp.relations(conc, rev)",H7),
 ("L228","C","arrived('rev'): the permission flag",THR),
 ("L229","H","elif s.k == 5",H7)]+post(230,"stage 5: y = z")+[
 ("L231","H","elif s.k == 6",H7)]+post(232,"stage 6: b = PREFIX ++ c",inner_h=(9,15))+[
 ("L233","C","settle(): wait for the relation threads",THR),
 ("L234","H","if not s.replay: report(); closing layout",H7),
]

std_P08b=[
 ("L41","C","import threading",EXT),
 ("L43","P","the sub-problem's unknowns (names)","rule 1"),
 ("L45","C","changed = threading.Condition(): the condition every relation thread waits on",THR),
 ("L47","R","class Unknown and the UNKNOWN table: an unknown represented as a place",R19H),
 ("L58","P","the problem's unknowns bound as places","rule 1"),
 ("L60","R","stores of the holding: known, waiting, failed",R19H),
 ("L63","C","count (busy threads, news) and defined (permission flags for definitions)",THR),
 ("L66","H","cp.bindings / cp.suspended / cp.held",H7),
]+evaluators_equal(72,0,0)+prefix_ev(90,dead=True)+evaluator_rev(103)+[
 ("L116","H","cp.relations(equal, prefix)",H7),
]+machinery(118)+[
 ("L201","H","stage loop header, stage-1 test",H7),
]+post(203,"stage 1: a = <x, y, z>")+[("L204","H","elif s.k == 2",H7)]+post(205,"stage 2: rev(a, b)")+[
 ("L206","H","elif s.k == 3",H7)]+post(207,"stage 3: x = y")+[
 ("L208","C","settle(): wait for the relation threads",THR),
 ("L209","H","if not s.replay: report(); closing layout",H7),
]
std_P08c=[
 ("L43","C","import threading",EXT),
 ("L47","P","constants block: stage 2 sequence <1,2>; stage 3 case-1 fact","README section 7; rule 1"),
 ("L53","P","the sub-problem's unknowns (names)","rule 1"),
 ("L55","C","changed = threading.Condition()",THR),
 ("L57","R","class Unknown and the UNKNOWN table: an unknown represented as a place",R19H),
 ("L68","P","the problem's unknown b bound as a place","rule 1"),
 ("L70","R","stores of the holding: known, waiting, failed",R19H),
 ("L73","C","count (busy threads, news) and defined (permission flags for definitions)",THR),
 ("L76","H","cp.bindings / cp.suspended / cp.held",H7),
]+evaluators_equal(82,0,0)+evaluator_rev(100)+[
 ("L113","H","cp.relations(equal)",H7),
 ("L115","R","EVALUATOR table",R19H),
 ("L117","P","case1: the store of rev's case-1 fact, as stage 3 gives it","rule 1"),
 ("L120","R","place()",R19H),
]+machinery(117)[1:]+[
 ("L200","H","stage loop header, stage-1 test",H7),
 ("L202","P","stage 1: conc, forwards, by its two cases",'rule 3'),
 ("L208","H","cp.relations(conc)",H7),
 ("L209","H","elif s.k == 2",H7),
 ("L210","C","pose(...): starts the relation's thread",THR),
 (("L210",3),"P","stage 2: rev(<seq>, b)",STG),
 (("L210",7),"H","s.constants[\"FORWARDS\"]",H7),
 (("L210",13),"P","stage 2 (rest)",STG),
 (("L210",-2),"C","pose(...) (close)",THR),
 ("L211","H","elif s.k == 3",H7),
 ("L212","P","stage 3: case-1 fact stored from the stage's constants",STG),
 (("L212",11),"H","s.constants[...] reads",H7),
 (("L212",-1),"P","stage 3 statement end",STG),
 ("L214","P","stage 3: rev with case 1 only: head test a == <> -> <>",'rule 2; rule 3'),
 ("L219","H","cp.relations(rev)",H7),
 ("L220","C","arrived('rev'): the permission flag",THR),
 ("L221","H","elif s.k == 4",H7),
 ("L222","P","stage 4: rev redefined: header",'rule 3'),
 ("L224","R","stage 4: case 1 restated inside the new def","METRICS R: a case the stage does not give (stage 3's information written again)"),
 ("L226","P","stage 4: rev case 2: head test, rev(l, q) then conc(q, <h>, r), failure of a conjunct propagated","rule 2; rule 3; rule 1"),
 ("L230","H","cp.relations(rev)",H7),
 ("L231","C","arrived('rev') again (flag already set)",THR),
 ("L232","C","settle(): wait for the relation threads",THR),
 ("L233","H","if not s.replay: report(); closing layout",H7),
]
