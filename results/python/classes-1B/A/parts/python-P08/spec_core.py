R19H="rule 19, first bullet: code that holds the problem's relations until their values arrive, written for this problem's relations, in core, is R"
R19P="rule 19, evaluator split: computing a place from the others, or testing a fully known relation, is P"
R19R="rule 19, evaluator split: the test of which places are known, and the verdict to wait, are R"
H7="harnesses/python/README.md section 7 (H list), METRICS rule 13"
ADP="METRICS rule 13: output adapter (prints or collects for the harness an answer already computed) is H"
STG="rule 1: the information of the stage, posed; rule 10 for the wrapper call"
def post(line, what, hold_cls="R", hold_name="held.append (the holding list)", hold_rule=R19H, inner_h=None):
    """held.append(( ... )) : wrapper R/C, inner relation P, optional H sub-span."""
    out=[(f"L{line}",hold_cls,hold_name+": posting "+what,hold_rule),
         ((f"L{line}",5),"P",what,STG)]
    if inner_h:
        a,b=inner_h
        out+= [((f"L{line}",a),"H","s.constants[...] read",H7),((f"L{line}",b),"P",what+" (rest)",STG)]
    out.append(((f"L{line}",-2),hold_cls,hold_name+" (close)",hold_rule))
    return out

def evaluators_equal(d, h, l):
    # d = line of 'def equal', lines relative layout identical in core/stdlib
    return [
     (f"L{d}","P","evaluator of =: header",R19P),
     (f"L{d+5}","R","equal: test that both places are known",R19R),
     (f"L{d+6}","P","equal: sequences decided place by place / fully known test",R19P+"; rule 15 (equality on the encoding)"),
     (f"L{d+11}","R","equal: test that a is known",R19R),
     (f"L{d+12}","P","equal: b computed from a",R19P),
     (f"L{d+13}","R","equal: test that b is known",R19R),
     (f"L{d+14}","P","equal: a computed from b",R19P),
     (f"L{d+15}","R","equal: verdict to wait (return None)",R19R),
    ]
core_P08a = [
 ("L36","P","constants block: stage 6 prefix <42>","README section 7: block entries are stage information, classed by the rules; rule 1"),
 ("L39","P","the sub-problem's unknowns (names)","rule 1"),
 ("L42","R","class Unknown and the UNKNOWN table: an unknown represented as a place",R19H),
 ("L53","P","the problem's unknowns a, b, c, x, y, z bound as places","rule 1"),
 ("L55","R","stores of the holding: known, held, failed",R19H),
 ("L59","H","cp.bindings / cp.suspended / cp.held registrations",H7),
]+evaluators_equal(64,0,0)+[
 ("L82","P","evaluator of s = p ++ t: header",R19P),
 ("L86","R","prefix: test that s and p are known",R19R),
 ("L87","P","prefix: decomposition of s by p, t computed",R19P+"; rule 15"),
 ("L90","R","prefix: test that t and p are known",R19R),
 ("L91","P","prefix: s computed from p and t",R19P),
 ("L92","R","prefix: verdict to wait",R19R),
 ("L95","P","evaluator of rev(a, b): header",R19P),
 ("L97","R","reverse: test that a is known",R19R),
 ("L98","P","reverse: b computed by rev forwards; no case applies -> does not hold",R19P),
 ("L101","R","reverse: test that b is unknown",R19R),
 ("L102","P","reverse: b given its value / equation b = r",R19P),
 ("L104","R","reverse: verdict to wait",R19R),
 ("L107","H","cp.relations(equal, prefix)",H7),
 ("L109","R","EVALUATOR table, place(), decide(): the holding loop",R19H),
 ("L140","H","show() and report(): output adapters",ADP),
 ("L159","H","stage loop header and stage-1 test",H7),
]+post(161,"stage 1: a = <x, y, z>")+[
 ("L162","H","elif s.k == 2",H7)]+post(163,"stage 2: rev(a, b)")+[
 ("L164","H","elif s.k == 3",H7)]+post(165,"stage 3: x = y")+[
 ("L166","H","elif s.k == 4",H7),
 ("L167","P","stage 4: conc, forwards, by its two cases",'rule 3 (mode-faithful transcription; "if not a:" dispatch is P)'),
 ("L173","P","stage 4: rev, forwards, by its two cases, conjuncts in order",'rule 3; rule 15 (tuple + as <h> ++ t)'),
 ("L179","H","cp.relations(conc, rev)",H7),
 ("L180","H","elif s.k == 5",H7)]+post(181,"stage 5: y = z")+[
 ("L182","H","elif s.k == 6",H7)]+post(183,"stage 6: b = PREFIX ++ c",inner_h=(11,17))+[
 ("L184","R","decide(): run the holding loop",R19H),
 ("L185","H","if not s.replay: report(); closing layout",H7),
]

def shift(spec, d, drop=()):
    out=[]
    for s,c,con,rule in spec:
        line = s if isinstance(s,str) else s[0]
        n=int(line[1:])
        if n in drop: continue
        nl="L%d"%(n+d)
        out.append((nl if isinstance(s,str) else (nl,s[1]),c,con,rule))
    return out
_a=[e for e in core_P08a if not (isinstance(e[0],str) and e[0]=="L36")]
def _ln(e): return int((e[0] if isinstance(e[0],str) else e[0][0])[1:])
_b = shift([e for e in _a if _ln(e)<166], -6) + shift([e for e in _a if _ln(e)>=184], -24)
# P08b has no ++ relation: the prefix evaluator is a definition the sub-problem does not give
core_P08b=[]
for e in _b:
    s=e[0]; n=int((s if isinstance(s,str) else s[0])[1:])
    if 76<=n<89:
        if n==76: core_P08b.append(("L76","R","prefix evaluator (s = p ++ t): a relation P08b does not have (dead code)","METRICS R: a definition the problem does not give; rule 1 (removing it changes nothing reported)"))
        continue
    core_P08b.append(e)
core_P08b=[(s,c,con.replace("a, b, c, x, y, z","a, b, x, y, z"),r) for s,c,con,r in core_P08b]

core_P08c = [
 ("L36","P","constants block: stage 2 sequence <1,2>; stage 3 case-1 fact <> and <>","README section 7: block entries are stage information; rule 1"),
 ("L42","P","the sub-problem's unknowns (names)","rule 1"),
 ("L45","R","class Unknown and the UNKNOWN table: an unknown represented as a place",R19H),
 ("L56","P","the problem's unknown b bound as a place","rule 1"),
 ("L58","R","stores of the holding: known, held, failed",R19H),
 ("L62","H","cp.bindings / cp.suspended / cp.held registrations",H7),
]+evaluators_equal(67,0,0)+[
 ("L85","P","evaluator of rev(a, b): header",R19P),
 ("L87","R","reverse: test that a is known",R19R),
 ("L88","P","reverse: b computed by rev forwards; no case applies -> does not hold",R19P),
 ("L91","R","reverse: test that b is unknown",R19R),
 ("L92","P","reverse: b given its value / equation b = r",R19P),
 ("L94","R","reverse: verdict to wait",R19R),
 ("L97","H","cp.relations(equal)",H7),
 ("L99","R","EVALUATOR table",R19H),
 ("L101","P","case1: the store of rev's case-1 fact, as stage 3 gives it","rule 1 (the fact's sequences are stage information the program must keep)"),
 ("L104","R","place(), decide(): the holding loop",R19H),
 ("L132","H","show() and report(): output adapters",ADP),
 ("L151","H","stage loop header and stage-1 test",H7),
 ("L153","P","stage 1: conc, forwards, by its two cases",'rule 3 ("if not a:" dispatch is P); rule 15'),
 ("L159","H","cp.relations(conc)",H7),
 ("L160","H","elif s.k == 2",H7),
 ("L161","R","held.append: posting stage 2",R19H),
 (("L161",5),"P","stage 2: rev(<seq>, b)",STG),
 (("L161",9),"H","s.constants[\"FORWARDS\"]",H7),
 (("L161",15),"P","stage 2: rev(<seq>, b) (rest)",STG),
 (("L161",-2),"R","held.append (close)",R19H),
 ("L162","H","elif s.k == 3",H7),
 ("L163","P","stage 3: case-1 fact stored from the stage's constants",STG),
 (("L163",11),"H","s.constants[...] reads",H7),
 (("L163",-1),"P","stage 3 statement end",STG),
 ("L165","P","stage 3: rev with case 1 only: head test a == <> -> <>",'rule 2 (head test of its own case is P); rule 3'),
 ("L170","H","cp.relations(rev)",H7),
 ("L171","H","elif s.k == 4",H7),
 ("L172","P","stage 4: rev redefined: header",'rule 3'),
 ("L174","R","stage 4: case 1 restated inside the new def (information of stage 3, written again because a def replaces the function)","METRICS R: a case the stage does not give; rule 4 by analogy"),
 ("L176","P","stage 4: rev case 2: head test, rev(l, q) then conc(q, <h>, r), failure of a conjunct propagated","rule 2 (head test); rule 3; rule 1 (None if q is None: conjunction fails)"),
 ("L180","H","cp.relations(rev)",H7),
 ("L181","R","decide(): run the holding loop",R19H),
 ("L182","H","if not s.replay: report(); closing layout",H7),
]
