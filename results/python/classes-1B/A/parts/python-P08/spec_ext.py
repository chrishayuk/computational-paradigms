from spec_core import H7, ADP, STG, shift
S15="METRICS rule 15: a general mechanism beyond the problem's relations (a unifier, a search) is S; rule 12"
SRES="rule 12 / rule 15: resolution (goal-list reduction by a relation's cases), general over relations, the program's own S"
SWAIT="METRICS class S ('a wait-for-definition layer'); rule 12: the program's own, general over relations"
CUSE="S-mechanisms.md: code a program writes around a listed mechanism is classed as usual (a freeze call, a search directive is C)"
IMP="rule 1: an import of a mechanism's interface changes only whether the program runs; its calls are classed where they are used"
R11="rule 11: a declaration that changes how an undefined relation behaves is C (here an empty case list: a relation with no case fails inside a search instead of raising NameError), listed"
P15="rule 15: operations on the encoding (construction of cons cells, equality as unification of encoded values) are P"
head_a=[  # P08a line numbers, from L57
 ("L57","S","binder Queue and trail: the unifier's binding store and undo trail",S15),
 ("L59","C","stack: the search's pending choice points (set up for the search directive)",CUSE),
 ("L60","P","NIL: the encoding of <>",P15),
 ("L62","H","cp.pending",H7),
 ("L65","C","q = Queue(): the suspension queue for the freeze calls",CUSE),
 ("L66","C","cases: rev and conc declared with no cases",R11),
 ("L67","S","defined: one Var per relation, bound when its definition arrives",SWAIT),
 ("L68","R","failed: the store of relations found not to hold","METRICS R: a definition the problem does not give (the program's record of verdicts)"),
 ("L70","H","cp.suspended / cp.held",H7),
 ("L74","S","unify(): unification of terms, no occurs check",S15),
 ("L94","S","children() and done(): resolution",SRES),
 ("L107","P","rev: the relation as its cases, tried in order",'rule 6 (the disjunction of the cases the problem states)'),
 ("L114","P","conc: the relation as its cases, tried in order",'rule 6'),
 ("L121","H","cp.relations(rev, conc)",H7),
 ("L123","S","NAME and class Application (init, call): an application held until its relation has a case, then solved by the search",SWAIT),
 ("L141","H","Application.__repr__: renders a held application for observe()",ADP),
 ("L145","P","equation(s, t): = as unification; a failure noted",P15),
 ("L151","P","cons(): the encoding of a sequence",P15),
]
onto_a=[("L159","P","onto(): the encoding of seq ++ tail",P15)]
tail_a=[
 ("L169","H","show(): output adapter",ADP),
]
def post(line, what, wrap_cls, wrap_name, wrap_rule, inner_h=None):
    out=[(f"L{line}",wrap_cls,wrap_name,wrap_rule),((f"L{line}",5),"P",what,STG)]
    if inner_h:
        a,b=inner_h
        out+=[((f"L{line}",a),"H","s.constants[...] read",H7),((f"L{line}",b),"P",what+" (rest)",STG)]
    out.append(((f"L{line}",-2),wrap_cls,wrap_name+" (close)",wrap_rule))
    return out
FREEZE="rule 10 / METRICS C: q.wait(...) is a freeze call"
ext_P08a=[
 ("L49","C","imports of S.search and S.suspend",IMP),
 ("L54","P","constants block: stage 6 prefix <42>","README section 7; rule 1"),
]+head_a+onto_a+tail_a+[
 ("L189","P","the problem's unknowns as Vars","rule 1"),
 ("L190","H","unknowns: the mapping collected for cp.bindings and the report; cp.bindings; report()",ADP),
 ("L203","H","stage loop header, stage-1 test",H7),
 ("L205","P","stage 1: a = <x, y, z>",STG+"; rule 15"),
 ("L206","H","elif s.k == 2",H7),
]+post(207,"stage 2: rev(a, b), posed as an application","C","q.wait(...)",FREEZE)+[
 ("L208","H","elif s.k == 3",H7),
 ("L209","P","stage 3: x = y",STG),
 ("L210","H","elif s.k == 4",H7),
 ("L211","P","stage 4: conc's two cases, rev's two cases, heads by unification, bodies in order",'rule 3 / rule 15 (head unification with the encoding is the case head)'),
 ("L229","P","stage 4: the cases added to the relations (the definitions arrive)",STG),
 ("L231","C","q.bind(defined[...]): wake the applications waiting for the definitions",CUSE),
 ("L233","H","elif s.k == 5",H7),
 ("L234","P","stage 5: y = z",STG),
 ("L235","H","elif s.k == 6",H7),
 ("L236","P","stage 6: b = PREFIX ++ c",STG),
 (("L236",7),"H","s.constants[\"PREFIX\"]",H7),
 (("L236",13),"P","stage 6 (rest)",STG),
 ("L237","C","q.run(): run the ready applications",CUSE),
 ("L238","H","if not s.replay: report(); closing layout",H7),
]
ext_P08b=[
 ("L49","C","imports of S.search and S.suspend",IMP),
]+shift(head_a,-5)+shift(tail_a,-15)+[
 ("L174","P","the problem's unknowns as Vars","rule 1"),
 ("L175","H","unknowns: the mapping collected for cp.bindings and the report; cp.bindings; report()",ADP),
 ("L188","H","stage loop header, stage-1 test",H7),
 ("L190","P","stage 1: a = <x, y, z>",STG+"; rule 15"),
 ("L191","H","elif s.k == 2",H7),
]+post(192,"stage 2: rev(a, b), posed as an application","C","q.wait(...)",FREEZE)+[
 ("L193","H","elif s.k == 3",H7),
 ("L194","P","stage 3: x = y",STG),
 ("L195","C","q.run(): run the ready applications",CUSE),
 ("L196","H","if not s.replay: report(); closing layout",H7),
]
ext_P08c=[
 ("L49","C","imports of S.search and S.suspend",IMP),
 ("L54","P","constants block: stage 2 sequence <1,2>; stage 3 case-1 fact","README section 7; rule 1"),
]+shift(head_a,3)+shift(tail_a,-7)+[
 ("L182","P","the problem's unknown b as a Var","rule 1"),
 ("L183","H","unknowns: the mapping collected for cp.bindings and the report; cp.bindings; report()",ADP),
 ("L196","H","stage loop header, stage-1 test",H7),
 ("L198","P","stage 1: conc's two cases",'rule 3 / rule 15'),
 ("L207","P","stage 1: the cases added to conc",STG),
 ("L208","C","q.bind(defined['conc'])",CUSE),
 ("L209","H","elif s.k == 2",H7),
 ("L210","C","q.wait(...)",FREEZE),
 (("L210",5),"P","stage 2: rev(<seq>, b), posed as an application",STG),
 (("L210",12),"H","s.constants[\"FORWARDS\"]",H7),
 (("L210",18),"P","stage 2 (rest)",STG),
 (("L210",-2),"C","q.wait(...) (close)",FREEZE),
 ("L211","H","elif s.k == 3",H7),
 ("L212","P","stage 3: the case-1 fact from the stage's constants",STG+"; rule 15"),
 (("L212",6),"H","s.constants[\"CASE1_FIRST\"]",H7),
 (("L212",12),"P","stage 3 fact (cont.)",STG),
 (("L212",16),"H","s.constants[\"CASE1_SECOND\"]",H7),
 (("L212",22),"P","stage 3 fact (close)",STG),
 ("L214","P","stage 3: rev case 1, head unified with the fact",'rule 3 / rule 15'),
 ("L218","P","stage 3: case 1 added to rev",STG),
 ("L219","C","q.bind(defined['rev'])",CUSE),
 ("L220","H","elif s.k == 4",H7),
 ("L221","P","stage 4: rev case 2, head and body in order",'rule 3 / rule 15'),
 ("L226","P","stage 4: case 2 added to rev",STG),
 ("L227","C","q.bind(defined['rev']) (already bound: wakes nothing)",CUSE),
 ("L228","C","q.run(): run the ready applications",CUSE),
 ("L229","H","if not s.replay: report(); closing layout",H7),
]
