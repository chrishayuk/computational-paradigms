# Builds absys.json from the classifier's judgements, and checks token coverage against the token files.
import json, glob, os, csv
REPO='/Users/christopherhay/cp-roles/classifier-1C-A'
OUT='/Users/christopherhay/cp-roles/classes-1C-A/absys-P09-P11'
CONFS=['absys','absys-depth-first','absys-wake-back']

def S(a,b,c,con,rule=None): return {"from":a,"to":b,"class":c,"construct":con,"rule":rule}
CONST="constants block line (a stage constant, never given to the system; the harness substitutes it into its section)"
RC="SPECIFICATION.md Conventions; harnesses/absys/README.md 3.9, 3.12: the constants block is classed by METRICS rules; the stage's information is P"
loop=S(9,18,'P',"loop definition, P04 case 1 (loop' = lambda p begin loop(p) end)","METRICS class P: transcription of the vocabulary")
conc=S(19,60,'P',"conc definition, P03/P01 cases 1 and 2 in order, case heads as equations","METRICS class P; rule 3 (mode-faithful transcription, one branch per case)")
rev=S(61,102,'P',"rev definition, P03 cases 1 and 2 in order, conjuncts in order","METRICS class P; rule 3")
raS=S(0,8,'P',"constant ra = [1;2;3] (B's sequence): "+CONST,RC)
OR_R="METRICS class R (a disjunction the problem does not state, written so that the two computations become two derivations); rule 10 (the tokens that introduce and close the construct take its class); rule 20 does not apply: or is the connective of the reformulated construct, not a separator between problem constructs"
tok={}
tok['absys/P09a.ab1']=[raS,loop,conc,rev,S(103,106,'P',"computation A (SPAWN A): loop(x)","METRICS class P: the query"),S(107,112,'P',"computation B (SPAWN B): rev(ra, b)","METRICS class P: the query")]
tok['absys/variants/P09a.AB.or.ab1']=[raS,loop,conc,rev,S(103,103,'R',"{ opening the or that joins A and B",OR_R),S(104,107,'P',"computation A: loop(x)","class P: the query"),S(108,108,'R',"or between A and B (reformulated disjunction)",OR_R),S(109,114,'P',"computation B: rev(ra, b)","class P: the query"),S(115,115,'R',"} closing the or",OR_R)]
tok['absys/variants/P09a.BA.or.ab1']=[raS,loop,conc,rev,S(103,103,'R',"{ opening the or that joins B and A",OR_R),S(104,109,'P',"computation B: rev(ra, b)","class P: the query"),S(110,110,'R',"or between B and A (reformulated disjunction)",OR_R),S(111,114,'P',"computation A: loop(x)","class P: the query"),S(115,115,'R',"} closing the or",OR_R)]
c3=lambda off,names:[S(off+3*i,off+3*i+2,'P',f"constant {n}: "+CONST,RC) for i,n in enumerate(names)]
tok['absys/P09b.ab1']=c3(0,['ak1','ak2','bk'])+[S(9,16,'P',"computation A: begin x = ak1 x = ak2 end (the conjunction x = 1 and x = 2)","class P: stage information and its conjunction"),S(17,19,'P',"computation B: y = bk","class P")]
tok['absys/variants/P09b.or.ab1']=c3(0,['ak1','ak2','bk'])+[S(9,9,'R',"{ opening the or that joins A and B",OR_R),S(10,17,'P',"computation A: begin x = ak1 x = ak2 end","class P"),S(18,18,'R',"or between A and B",OR_R),S(19,21,'P',"computation B: y = bk","class P"),S(22,22,'R',"} closing the or",OR_R)]
CMPR="METRICS class R: a definition the problem does not give, written because the configuration has no comparison (systems/absys/README.md, Notation)"
CALL="P by rule 1 and rule 9 read by analogy: the application stands in the problem's own place for its primitive comparison, and the relation it applies is equivalent to it over the integers (least relation); the defining code is R"
tok['absys/P09c.ab1']=[S(0,2,'P',"constant gk = 1: "+CONST,RC),S(3,5,'P',"constant gmax = 5, the bound in gen's definition (vocabulary, given with the prelude)",RC),
 S(6,22,'R',"gt definition (a > b as a = b + d', pos(d))",CMPR),S(23,39,'R',"le definition (a <= b as b = a + d', nonneg(d))",CMPR),
 S(40,60,'R',"pos definition (least relation: pos(1), pos(e+1) if pos(e))",CMPR),S(61,76,'R',"nonneg definition (q = 0 or pos(q))",CMPR),
 S(77,88,'P',"gen definition header and case 1 head (w = [])","class P; rule 3"),S(89,94,'P',"case 1 conjunct n > 5 written gt(g, gmax)",CALL),
 S(95,102,'P',"or, case 2 head (w = [g & rest'])","class P; rule 3"),S(103,108,'P',"case 2 conjunct n <= 5 written le(g, gmax)",CALL),
 S(109,121,'P',"case 2: g1' = g + 1 (n + 1 as a fresh unknown) and gen(g1, rest); closing } end","class P; SPECIFICATION.md Arithmetic (compound or decomposed is transcription)"),
 S(122,147,'P',"sum3 definition, its one case: head equation then p + q + r = t","class P; rule 3"),S(148,161,'P',"stage 1: begin gen(gk, s) sum3(s, total) end, in order","class P: the query")]
tok['absys/P09d.ab1']=[S(0,2,'P',"constant gk = 1: "+CONST,RC),S(3,28,'P',"genu definition, its one case","class P; rule 3"),S(29,54,'P',"sum3 definition","class P; rule 3"),S(55,68,'P',"stage 1: begin genu(gk, s) sum3(s, total) end, in order","class P: the query")]
tok['absys/P09e.ab1']=c3(0,['ek1','ek2'])+[S(6,17,'P',"stage 1: begin x = y + ek1 y = x - ek2 end","class P: stage information, arithmetic relations")]
IDX="METRICS class R (rule 3/5: arguments the problem does not give); problems/10 Observations: indexing written for the purpose is reformulation. The history-list cell and the open tail encode the named quantity"
BE="METRICS class R, rule 10: begin ... end joins the reformulated replacement (the history-list cell) to the new value, so it belongs to the reformulated construct"
VAL="class P: the new value as the problem states it (b becomes e, with b at its value before the stage); the version name bvk is the reformulation's, the relation is the problem's"
def repl(i0,label,cell_from,cell_to,val_from,val_to):
    return [S(i0,i0,'R',f"{label}: begin",BE),S(cell_from,cell_to,'R',f"{label}: history-list cell (tail = [v & t])",IDX),S(val_from,val_to,'P',f"{label}: the new value",VAL),S(val_to+1,val_to+1,'R',f"{label}: end",BE)]
tok['absys/P10a.ab1']=c3(0,['c1','c2','c3'])+repl(9,"stage 1, b becomes c1",10,16,17,19)+repl(21,"stage 2, b becomes b + c2",22,28,29,33)+repl(35,"stage 3, b becomes c3",36,42,43,45)
tok['absys/P10b.ab1']=c3(0,['dk','c1','c2','c3'])+[S(12,17,'R',"dbl definition header (dbl' = lambda p, q): a relation between the two history lists","METRICS class R: definition the problem does not give (the indexing of P10's reformulation)"),
 S(18,19,'C',"key p (dbl waits for its key, the list b)","METRICS class C: key declarations"),
 S(20,44,'R',"dbl body: begin { null(p) null(q) or p = [r' & s'] q = [e' & u'] (recursion over the lists, null case, head equations)","class R (program comment and METRICS class R)"),
 S(45,49,'P',"e = dk * r: the problem's relation d = k * b, item by item","class P: the stage-1 relation"),
 S(50,57,'R',"dbl(s, u) recursion and } end","class R"),
 S(58,63,'R',"stage 1: dbl(b, d), the standing relation stated over the history lists","class R: the application of the reformulated relation over encoded quantities; not equivalent to d = 2 * b on the problem's values except through the encoding")]+repl(64,"stage 2, b becomes c1",65,71,72,74)+repl(76,"stage 3, b becomes b + c2",77,83,84,88)+repl(90,"stage 4, b becomes c3",91,97,98,100)
tok['absys/P10c.ab1']=c3(0,['c1','dk','c2','c3'])+repl(12,"stage 1, b becomes c1",13,19,20,22)+repl(24,"stage 2, d becomes dk * b",25,31,32,36)+repl(38,"stage 3, b becomes b + c2",39,45,46,50)+repl(52,"stage 4, b becomes c3",53,59,60,62)
tok['absys/P10d.ab1']=c3(0,['pk1','pk2','pk3','gtk'])+[S(12,30,'P',"pick definition: the three facts as alternatives, in order","class P; rule 6 (a set of facts the problem states)"),
 S(31,47,'R',"gt definition",CMPR),S(48,68,'R',"pos definition",CMPR),S(69,72,'P',"stage 1: pick(x)","class P"),
 S(73,78,'P',"stage 2: x > gtk written gt(x, gtk)",CALL),
 S(79,82,'R',"stage 3: withdraw x > k, carried out as pick(x3): the information not withdrawn restated of a new unknown x3","METRICS class R: a construct the problem does not give (Absys cannot withdraw an assertion); the new name x3 is written for the purpose")]
EMIT="class P: problems/11 Rules, 'emit and commit are problem tokens' (frozen problem file). harnesses/absys/README.md 3.12 would class tout ( \"emit\" , ) as H; the problem file's rule is taken to decide"
p11=c3(0,['pk1','pk2','pk3','nek'])+[S(12,32,'P',"pick definition, the three facts in order","class P; rule 6"),S(33,37,'P',"stage 1: { pick(x)","class P"),S(38,44,'P',"stage 1: , tout(\"emit\", x), the emit stub on x",EMIT+"; rule 20 (the comma takes the class of the construct that follows)"),S(45,45,'P',"} closing the stage-1 conjunction","class P")]
tok['absys/P11c.abs']=p11+[S(46,51,'P',"stage 2: x != nek written not(x = nek)","class P: negation and equality are problem connectives")]
tok['absys/P11d.abs']=p11+[S(46,51,'P',"stage 3: x != nek written not(x = nek)","class P: negation and equality are problem connectives")]
NE="METRICS class R: x >= k replaced by not(x = gelo), a construct the problem does not give, which changes the meaning off pick's three facts (SPECIFICATION.md expressibility: not expressible, run as a named variant); rule 20 (the comma goes with it)"
base11=c3(0,['pk1','pk2','pk3'])+[S(9,11,'R',"constant gelo = 1: the value of pick below k, derived by the author, not stated by the problem","class R: a constant of the meaning-changing reformulation, not of the problem"),S(12,32,'P',"pick definition","class P; rule 6"),S(33,37,'P',"{ pick(x)","class P")]
tok['absys/variants/P11a.ne.abs']=base11+[S(38,44,'R',", not(x = gelo) in place of x >= k",NE),S(45,51,'P',", tout(\"emit\", x)",EMIT),S(52,52,'P',"}","class P")]
tok['absys/variants/P11b.ne.abs']=base11+[S(38,44,'P',", tout(\"emit\", x)",EMIT),S(45,51,'R',", not(x = gelo) in place of x >= k",NE),S(52,52,'P',"}","class P")]

# coverage check
totals={}
for k,spans in tok.items():
    path=f'{REPO}/results/absys/tokens/{k}.tokens.tsv'
    rows=list(csv.reader(open(path),delimiter='\t'))[1:]
    n=len(rows); cov=[0]*n
    for s in spans:
        for i in range(s['from'],s['to']+1): cov[i]+=1
    assert all(c==1 for c in cov), (k,[i for i,c in enumerate(cov) if c!=1])
    t={}
    for s in spans: t[s['class']]=t.get(s['class'],0)+s['to']-s['from']+1
    totals[k]=(n,t)
    # the same text in the other configurations
    for c in CONFS[1:]:
        other=f'{REPO}/results/absys/tokens/{k.replace("absys/",c+"/",1)}.tokens.tsv'
        assert open(other).read()==open(path).read(), other
json.dump(totals,open(f'{OUT}/token_totals.json','w'),indent=1)
print(json.dumps(totals,indent=1))

# ---------- records ----------
import gzip
def load(p):
    if p.endswith('.gz'):
        with gzip.open(p,'rt') as f: return json.load(f)
    with open(p) as f: return json.load(f)
RECS={}
for c in CONFS:
    for prob in ['P09','P10','P11']:
        for p in sorted(glob.glob(f'{REPO}/results/absys/{c}/{prob}/raw/*.json*')):
            if p.endswith('.jsonl'): continue
            if os.path.getsize(p)>5_000_000:
                # big records: only the run header is needed; read the start of the file
                op=gzip.open(p,'rt') if p.endswith('.gz') else open(p)
                head=op.read(6000); op.close()
                import re
                prog=re.search(r'"path": "programs/absys/([^"]+)"',head).group(1)
                inst=re.search(r'"instance": "([^"]+)"',head).group(1)
                mode=re.search(r'"mode": "([^"]+)"',head).group(1)
            else:
                r=load(p)['run']; prog=r['program']['path'].split('programs/absys/',1)[1]; inst=r['instance']; mode=r['mode']
            RECS[(c,inst,prog.split('/',1)[1],mode)]=os.path.relpath(p,REPO)
json.dump({'|'.join(k):v for k,v in RECS.items()},open(f'{OUT}/records_index.json','w'),indent=1)
print(len(RECS),'records indexed')

# ---------- outcomes ----------
O=[]
def add(conf,inst,prog,stage,**kw):
    e={"configuration":conf,"instance":inst,"program":prog,"record":RECS[(conf,inst,prog,'behaviour')],"stage":stage,
       "computation":kw.pop('computation',None),"reading":kw.pop('reading',None),"reached":kw.pop('reached',True),
       "semantic":None,"representation":None,"simplification":None,"identical_to_posed":None,"residual_size":None,
       "execution_state":[],"residual_equivalence":None,"answer_completeness":None,"effects":None,"observations":"","rule":None}
    e.update(kw)
    if prog=='P10d.ab1': e['harness_fault']=True
    O.append(e)
NR_RULE="SPECIFICATION.md Outcomes 1 (none reported: nothing was reported); 3 (budget)"
A5="The harness accepts each spawned computation's text into the one session (harnesses/absys/README.md 3.6; QUESTIONS A5), side_by_side false"
for conf in CONFS:
    df = conf=='absys-depth-first'
    # ---- P09a primary
    for inst in ['P09a.AB','P09a.BA']:
        if inst=='P09a.AB':
            add(conf,inst,'P09a.ab1',1,computation='A',semantic='none reported',execution_state=['budget'],
                answer_completeness="valid outcomes empty; the system did not report that there are none",
                observations="A spawned first. 1 derivation, still elaborating loop(x) when the budget ran out; x uninstantiated (printed x = x). No suspended work (0). Alternatives: 1 derivation, all live. "+A5+".",
                rule=NR_RULE)
            add(conf,inst,'P09a.ab1',1,computation='B',semantic='none reported',execution_state=['budget'],
                answer_completeness="0 of 1 valid answers; 0 invalid",
                observations="B's rev(ra, b) was added to A's one derivation and stays in its to-do list behind loop(x) (to do: loop(x); rev([1;2;3], b)); b does not occur. B is blocked by A: it is conjoined with A, not run beside it ("+A5+"). The order of posing matters (compare P09a.BA). Valid b = <3,2,1> not reached.",
                rule=NR_RULE)
        else:
            add(conf,inst,'P09a.ab1',1,computation='B',semantic='complete',representation='explicit',execution_state=['finished'],
                answer_completeness="1 of 1 valid answers; 0 invalid",residual_equivalence="b = [3;2;1] is the valid outcome <3,2,1>",
                observations="B spawned first: derivation hibernating with b = [3;2;1], read before A was posed. No suspended work; 1 derivation.",
                rule="SPECIFICATION.md Outcomes 1, 2 (explicit), 3 (finished)")
            add(conf,inst,'P09a.ab1',1,computation='A',semantic='none reported',execution_state=['budget'],
                answer_completeness="valid outcomes empty; the system did not report that there are none",
                observations="A's loop(x) added to B's derivation (#19), which then elaborated loop(x) to the budget; the derivation still holds b = [3;2;1]. x uninstantiated. B's outcome was reported before A ran; posing order decides whether B is reported at all ("+A5+").",
                rule=NR_RULE)
    # ---- P09a or-variants
    for inst in ['P09a.AB','P09a.BA']:
        for prog in ['variants/P09a.AB.or.ab1','variants/P09a.BA.or.ab1']:
            mismatch = (inst=='P09a.AB' and 'BA.or' in prog) or (inst=='P09a.BA' and 'AB.or' in prog)
            mm = " The variant is written for the other spawn order; its or is given before the empty SPAWN sections, so the instance's spawn order has no effect and the run is the variant's own order." if mismatch else ""
            b_blocked = df and 'AB.or' in prog
            add(conf,inst,prog,1,computation='A',semantic='none reported',execution_state=['budget'],
                answer_completeness="valid outcomes empty; the system did not report that there are none",
                observations=("A's disjunct, derivation with loop(x), still elaborating at the budget; x uninstantiated. The harness lists every derivation under both computations (the SPAWN sections are empty); the other derivation is B's disjunct and says nothing of x (x does not occur), so it is not read as an outcome of A."+mm),
                rule=NR_RULE+"; a derivation of B's disjunct is not an answer of A (named variant: the two computations are the two alternatives of one or)")
            if b_blocked:
                add(conf,inst,prog,1,computation='B',semantic='none reported',execution_state=['budget'],
                    answer_completeness="0 of 1 valid answers; 0 invalid",
                    observations="depth-first: the first derivation (loop(x)) is elaborated alone until it hibernates or fails, so the second (rev([1;2;3], b), still in its to-do list) was never started; b does not occur. 2 derivations held, 1 live (mixed)."+mm,
                    rule=NR_RULE)
            else:
                add(conf,inst,prog,1,computation='B',semantic='complete',representation='explicit',execution_state=['budget'],
                    answer_completeness="1 of 1 valid answers; 0 invalid",residual_equivalence="b = [3;2;1] is the valid outcome",
                    observations=("B's disjunct is a derivation of its own, hibernating with b = [3;2;1], while A's derivation still elaborates loop(x) at the budget; the state is budget because of A's derivation. B reported while A runs."+(" depth-first: the rev derivation comes first in the or, so it hibernates before loop(x) is elaborated." if df else " Both derivations are live at once (all-live).")+mm),
                    rule="SPECIFICATION.md Outcomes 1, 2; 3 (budget: the harness's state is of the one session, A's derivation still elaborating)")
    # ---- P09b
    add(conf,'P09b','P09b.ab1',1,computation='A',semantic='complete',representation='explicit',execution_state=['finished'],
        answer_completeness="valid outcomes empty; reported that there are none: yes",
        observations="'No derivation survives: the assertions are unsatisfiable' (the last failure: 1 = 2). 0 derivations, 0 suspended.",
        rule="SPECIFICATION.md Outcomes 1 (the empty valid outcome reported as empty), 3 (finished)")
    add(conf,'P09b','P09b.ab1',1,computation='B',semantic='unsound',representation='explicit',execution_state=['finished'],
        answer_completeness="0 of 1 valid answers; reported none where y = 3 is valid",
        observations="A's failure removed the one computation's only derivation, so y = bk was added to no derivation: 'no derivation survives' for x and y. A's failure affects B (A5: B is conjoined with A).",
        rule="SPECIFICATION.md Outcomes 1 (unsound: reports that there are none where valid outcomes exist)")
    add(conf,'P09b','variants/P09b.or.ab1',1,computation='A',semantic='complete',representation='explicit',execution_state=['finished'],
        answer_completeness="valid outcomes empty; A's derivation failed and disappeared (yes, by its absence)",
        observations="A's disjunct failed (x = 1 and x = 2) and its derivation disappeared; the surviving derivation #2 is B's (x does not occur). The harness lists it under A too; it is not an outcome of A.",
        rule="SPECIFICATION.md Outcomes 1; named variant (or of the two computations)")
    add(conf,'P09b','variants/P09b.or.ab1',1,computation='B',semantic='complete',representation='explicit',execution_state=['finished'],
        answer_completeness="1 of 1 valid answers; 0 invalid",residual_equivalence="y = 3",
        observations="Derivation #2 hibernating, y = 3. A's failure does not affect B in this variant. 1 derivation, 0 suspended.",
        rule="SPECIFICATION.md Outcomes 1, 2, 3")
    # ---- P09c
    if df:
        add(conf,'P09c','P09c.ab1',1,semantic='none reported',execution_state=['timeout'],
            answer_completeness="0 of 1 valid answers; 0 invalid",
            observations="Attempt 1 stopped by the 60 s limit, the rerun by the 600 s limit (final timeout); nothing was read (no observe output). Under depth-first the first derivation is elaborated alone: by the absys runs, that is a gen branch whose gt/le test on a known non-positive difference descends through pos(e) without end, so the derivation holding s = <1..5>, total = 6 is not reached. Steps not measured (cost run also timed out).",
            rule="SPECIFICATION.md Outcomes 1 (none reported), 3 (timeout, final after the one rerun: PROTOCOL.md Safety limit)")
    else:
        add(conf,'P09c','P09c.ab1',1,semantic='complete',representation='residual',simplification='reducible',identical_to_posed=False,
            residual_size="16 derivations: 1 solved (s = [1;2;3;4;5], total = 6) and 15 still elaborating, holding 42 undecided relations in their to-do lists (pos(...), e + 1 = -k, or-alternatives, gen(...), sum3(...)), with partial bindings of s; input: 2 relations, gen(1, s) and sum3(s, total), 3 occurrences of unknowns",
            execution_state=['budget'],
            residual_equivalence="Equivalent. Each of the 15 elaborating derivations holds a to-do list containing pos(q) or q' + 1 = q with q a known negative integer, or -k = 1, each false under pos's least relation (pos holds only of positive integers), so each denotes the empty set; the one hibernating derivation denotes s = <1,2,3,4,5>, total = 6, the valid outcome. The union is the valid outcome. Smaller equivalent: the solved derivation alone, so reducible.",
            answer_completeness="1 of 1 valid answers (derivation #269); 0 invalid finished answers",
            observations="Attempt 1 hit the 60 s limit; the rerun (600 s) reached the budget (10^6 steps: 1000012 in the cost run). The consumer acted on s before the producer finished: sum3 ran on the solved branch (#269, a low-numbered derivation), while 15 branches still elaborate the reformulated comparisons (gt/le via pos, descending through negative numbers: -20849 ...). 16 derivations all live; 0 suspended processes printed. The partial bindings of s in the 15 elaborating derivations are conditional on their unfinished to-do lists and are not finished answers.",
            rule="SPECIFICATION.md Outcomes 1 (complete: correctness and simplification kept apart), 2 (residual; simplification reducible); 3 (budget after the safety rerun)")
    # ---- P09d (two readings)
    P9D="Attempt 1 hit the 60 s limit; the rerun reached the budget (1000004 steps in the cost run). 1 derivation still elaborating: s = [1;2;...;333333 & rest] and to do: rest = [333334 & ...]; 333334 + 1 = g1; genu(g1, rest); sum3([...], total). total does not occur: sum3 was never taken up, so the consumer did not act on s before the producer ran out of budget. 0 suspended, 1 derivation."
    add(conf,'P09d','P09d.ab1',1,reading='P09d1 (finite)',semantic='none reported',execution_state=['budget'],
        answer_completeness="valid outcomes empty; the system did not report that there are none",
        observations=P9D+" No binding of total is held (the P09d1 observation: none).",rule="problems/09 P09d1: none reported with budget")
    add(conf,'P09d','P09d.ab1',1,reading='P09d2 (stream)',semantic='none reported',execution_state=['budget'],
        answer_completeness="total = 6 not obtained",
        observations=P9D+" Producer state: budget (still elaborating). total = 6 never computed: the stream's consumer does not run while the producer produces.",rule="problems/09 P09d2; SPECIFICATION.md Outcomes 1 (none reported)")
    # ---- P09e
    add(conf,'P09e','P09e.ab1',1,semantic='complete',representation='residual',simplification='reducible',identical_to_posed=False,
        residual_size="2 relations, y + 1 = x twice, 4 occurrences of unknowns; input 2 relations (x = y + 1, y = x - 1), 4 occurrences",
        execution_state=['suspended'],
        residual_equivalence="Equivalent: y = x - 1 is the same integer relation as y + 1 = x, and x = y + 1 likewise; the two held relations denote every integer pair with x = y + 1. Reducible: the two are the same relation, one alone is smaller.",
        answer_completeness="valid outcomes infinite; a finite equivalent representation was given: yes",
        observations="Derivation #0 hibernating, x and y uninstantiated, 2 suspended relations (each 'waits for two of its numbers: y, x'), susp_relations 2. Reports a residual and suspends; no deadlock reported, no enumeration. Told apart from completion: the derivation prints suspended processes and the harness classes it suspended, not finished. Steps 3.",
        rule="SPECIFICATION.md Outcomes 1, 2 (residual, reducible), 3 (suspended)")
    # ---- P10a
    vals={1:'b = 10',2:'b = 15',3:'b = 7'}
    lists={1:'b = [10&bt1]',2:'b = [10;15&bt2]',3:'b = [10;15;7&bt3]'}
    for k in (1,2,3):
        add(conf,'P10a','P10a.ab1',k,semantic='complete',representation='explicit',execution_state=['finished'],
            residual_equivalence=f"Under the program's encoding (a quantity is the list of its values, the current value its last bound element) {lists[k]} gives {vals[k]}, the valid outcome.",
            answer_completeness="1 of 1 valid answers; 0 invalid",
            observations=f"{lists[k]}, bv1..bv{k} bound, tail bt{k} uninstantiated. Replacement by indexing (version names and a history list, R), not native. Earlier values are still retrievable (the list and bv1.. keep them). 1 derivation, 0 suspended. Steps 3 per stage (cost run)."+(" No conclusion withdrawn: the earlier value stays in the list, superseded by the encoding's reading." if k>1 else ""),
            rule="SPECIFICATION.md Outcomes 1, 2 (explicit, read through the reformulated encoding: a form derived by reformulation keeps its R tokens), 3")
    # ---- P10b
    add(conf,'P10b','P10b.ab1',1,semantic='complete',representation='residual',simplification='reduced',identical_to_posed=True,
        residual_size="1 relation, dbl(b, d), 2 occurrences of unknowns; input d = 2 * b, 1 relation, 2 occurrences",
        execution_state=['suspended'],
        residual_equivalence="Equivalent: dbl(b, d), waiting for its key b, is the program's statement of d = 2 * b over the encoded quantities (item i of d is 2 times item i of b); neither has a value, as the valid outcome says.",
        answer_completeness="valid outcome is a relation; held: yes",
        observations="dbl(b, d) suspended, 'waits for its key: b' (susp_applications 1). b, d uninstantiated. The residual is the assertion as posed, held and acted on at the next stage. Steps 4.",
        rule="SPECIFICATION.md Outcomes 2 (residual; identical to the posed information), 3 (suspended)")
    bd={2:('b = [10&bt1]','d = [20&u1]','d = 20',10),3:('b = [10;15&bt2]','d = [20;30&u2]','d = 30',12),4:('b = [10;15;7&bt3]','d = [20;30;14&u3]','d = 14',12)}
    for k,(bl,dl,dv,st) in bd.items():
        add(conf,'P10b','P10b.ab1',k,semantic='complete',representation='explicit',execution_state=['suspended'],
            residual_equivalence=f"{bl}, {dl}: last bound elements b = {bl.split(';')[-1].split('&')[0].strip('b = [')}, {dv}, the valid outcome; the standing relation is still held for later values.",
            answer_completeness="1 of 1 valid answers; 0 invalid",
            observations=f"{bl}, {dl}; suspended: bt{k-1} = s{k-1} (an equation) and dbl(s{k-1}, u{k-1}) waiting for its key (2 items). One dependent value computed per replacement (d's new item), {st} steps for the stage (cost run). The relation keeps holding: it is applied to each new value, not recomputed for old ones. Earlier values retrievable. The held standing relation is recorded as an observation; the stage's values are explicit.",
            rule="SPECIFICATION.md Outcomes 2 (the more explicit valid form), 3 (suspended)")
    # ---- P10c
    p10c={1:('b = [10&bt1]','d does not occur','b = 10'),2:('b = [10&bt1]','d = [20&dt1]','d = 20 (b = 10)'),3:('b = [10;15&bt2]','d = [20&dt1]','b = 15, d = 20'),4:('b = [10;15;7&bt3]','d = [20&dt1]','b = 7, d = 20')}
    for k,(bl,dl,v) in p10c.items():
        add(conf,'P10c','P10c.ab1',k,semantic='complete',representation='explicit',execution_state=['finished'],
            residual_equivalence=f"{bl}; {dl}: read through the encoding, {v}, the valid outcome.",
            answer_completeness="1 of 1 valid answers; 0 invalid",
            observations=f"{bl}; {dl}. d is a snapshot: dv1 = dk * bv1 was decided once and is not tied to later values of b. 1 derivation, 0 suspended; 3 steps per stage (cost run). Earlier values retrievable.",
            rule="SPECIFICATION.md Outcomes 1, 2, 3")
    # ---- P10d (INVALID record)
    add(conf,'P10d','P10d.ab1',1,semantic='complete',representation='explicit',execution_state=['finished'],
        residual_equivalence="x = 1, 2, 3 in three derivations: x in {1,2,3}",answer_completeness="3 of 3 valid answers; 0 invalid",
        observations="3 derivations hibernating, all live (depth-first: held, mixed); 0 suspended; 14 steps. The record is .INVALID.json (harness fault of step accounting at stage 3).",
        rule="SPECIFICATION.md Outcomes 1, 2, 3")
    add(conf,'P10d','P10d.ab1',2,semantic='none reported',execution_state=['timeout'],
        answer_completeness="0 of 2 valid answers; 0 invalid",
        observations="Attempt 1 (incremental) stopped at 60 s; the rerun, by reposing stages 1-2 (restart cost 14), stopped at 600 s: final timeout, nothing read. gt(x, 1) in the derivation x = 1 gives 1 = 1 + d, d = 0, and pos(0) descends through pos(-1), pos(-2), ... without end (the reformulated comparison does not fail finitely); the separate replay run shows the stage's assertion spends its whole budget (stages 1-2 = 1000014 steps, 960-2978 s), so the stage would end in budget, not with x in {2,3} reported. Whether the derivation that x > 1 removes would come back is not observable.",
        rule="SPECIFICATION.md Outcomes 1 (none reported), 3 (timeout, final after the rerun); AMENDMENTS 3.1")
    add(conf,'P10d','P10d.ab1',3,reached=False,semantic='not reached',execution_state=[],
        observations="Not reached: both attempts reposed stages 1-2, and the process was killed (60 s, then 600 s) while still replaying stage 2's gt(x, gtk) (the attempts' stdout ends after stage 1's state); stage 3's pick(x3) was never given. What stopped the run: stage 2's timeout. The record's fields for stage 3 (timeout, restart_cost) describe the replay, not stage 3. harness_faults: 'stage 3 attempt 1: no restart cost: the separate run of stages 1 to 2 ... was stopped after 600 s'.",
        rule="AMENDMENTS 3.2 (never reached is not reached, with what stopped the run); the brief's reading of a reposed stage the replay did not reach")
    # ---- P11a, P11b (named variants, no primary)
    for inst,prog in (('P11a','variants/P11a.ne.abs'),('P11b','variants/P11b.ne.abs')):
        add(conf,inst,prog,1,semantic='complete',representation='explicit',execution_state=['finished'],
            residual_equivalence="answers(1): derivation #2, x = 2, one of the valid x in {2,3} (any one)",
            answer_completeness="1 of 1 (any one); 0 invalid",
            effects={"class":"extra","log":["1","2","3"],"when":"all three performed during stage 1, before the outcome was committed (it is committed when reported); 1 and 3 for outcomes never committed, 1 for an outcome refuted in the same stage"},
            observations=("L = <1, 2, 3>. tout(\"emit\", x) performed in each pick derivation before not(x = gelo) failed derivation 1"+(" (the variant writes the test before emit, but Absys elaborates the conjuncts of all derivations together, so the order does not defer the effect)" if inst=='P11a' else "")+". 2 derivations survive (x = 2, x = 3); both all live; no selection; commitment in Absys's terms: none (the end of the query). No control tokens avoid extra. Named variant: x >= 2 replaced by not(x = 1) (meaning changed off pick's facts), judged against the problem's valid outcomes."),
            rule="problems/11 Effects (extra), Commitment (one stage: committed when reported); SPECIFICATION.md Outcomes 1 (any one)")
    # ---- P11c
    LOG="L = <1, 2, 3>, all performed at stage 1 (on provisional outcomes, before commitment)"
    add(conf,'P11c','P11c.abs',1,semantic='complete',representation='explicit',execution_state=['finished'],
        residual_equivalence="answers(1): x = 1, one of x in {1,2,3}",answer_completeness="1 of 1 (any one); 0 invalid",
        effects={"class":None,"log_so_far":["1","2","3"],"when":"stage 1, before commitment"},
        observations="3 derivations hibernating, each with its output emit = v; all live (depth-first: held, mixed). "+LOG+". Effects are classed at the end of the problem.",
        rule="SPECIFICATION.md Outcomes 1 (any one), 2, 3")
    add(conf,'P11c','P11c.abs',2,semantic='complete',representation='explicit',execution_state=['finished'],
        residual_equivalence="answers(1): x = 2, one of x in {2,3}",answer_completeness="1 of 1 (any one); 0 invalid",
        observations="not(x = 1) failed derivation #1, which disappeared with its output from the state; its entry 1 stays in L. Stage 1's reported answer x = 1 is withdrawn, shown only by the derivation's absence. 2 derivations live; no new effect.",
        rule="SPECIFICATION.md Outcomes 1, 2, 3; Stages and monotonicity (withdrawn conclusion recorded)")
    add(conf,'P11c','P11c.abs',3,semantic='complete',representation='explicit',execution_state=['finished'],
        residual_equivalence="No selection: classified against the outcomes before the commit, x in {2,3}; answers(1) x = 2 is one of them",
        answer_completeness="1 of 1 (any one); 0 invalid",
        effects={"class":"extra","log":["1","2","3"],"when":"all at stage 1, before commitment; 1 on the outcome refuted at stage 2; 3 on an outcome never committed (no commitment was made at all)"},
        observations="Commit stage: the section is empty; Absys selects none and both derivations (x = 2, x = 3) stay live; answers(1) is the first printed, not a selection (record note). Commitment in Absys's terms: none. No control tokens used to avoid extra. L judged on every entry: more than one entry, extra. The commit is one omission in the program (no construct).",
        rule="problems/11 Commitment (a system that cannot select is judged on every entry; semantic result against the outcomes before the commit), Effects (extra)")
    # ---- P11d
    add(conf,'P11d','P11d.abs',1,semantic='complete',representation='explicit',execution_state=['finished'],
        residual_equivalence="answers(1): x = 1, one of x in {1,2,3}",answer_completeness="1 of 1 (any one); 0 invalid",
        effects={"class":None,"log_so_far":["1","2","3"],"when":"stage 1, before commitment"},
        observations="3 derivations, each with its output; all live. "+LOG+".",rule="SPECIFICATION.md Outcomes 1, 2, 3")
    add(conf,'P11d','P11d.abs',2,semantic='complete',representation='explicit',execution_state=['finished'],
        residual_equivalence="No selection: classified against the outcomes before the commit, x in {1,2,3}; answers(1) x = 1 is one of them",
        answer_completeness="1 of 1 (any one); 0 invalid",
        observations="Commit stage, empty section: no derivation selected, 3 stay live; answers(1) x = 1 is the first printed, not a selection; nothing replayed as x = v. Commitment in Absys's terms: none.",
        rule="problems/11 Commitment (a system that cannot select: semantic result against the outcomes before the commit)")
    add(conf,'P11d','P11d.abs',3,semantic='complete',representation='explicit',execution_state=['finished'],
        residual_equivalence="With no v selected, the information is pick(x), emit(x), x != 1: x in {2,3}; answers(1) x = 2 is one of them. Alternative reading, if stage 2's first printed answer x = 1 were taken as v: the valid outcome is none and x = 2 would be unsound; not taken, since the harness and record say no selection was made.",
        answer_completeness="1 of 1 (any one); 0 invalid",
        effects={"class":"extra","log":["1","2","3"],"when":"all at stage 1, before the commit stage; none at or after it. Under either reading L holds more than one entry"},
        observations="not(x = 1) removed derivation #1 (and its output from the state); entry 1 stays in L. What the system does with information contradicting an effect: the derivation that performed it fails silently; the effect is not undone and nothing reports the contradiction. Stage 1 and 2's answer x = 1 withdrawn, shown by absence. 2 derivations live.",
        rule="problems/11 Commitment, Effects (extra), P11d")

# ---------- expressibility ----------
E=[]
EX={
 'P09a':("expressible with reformulation","Each computation is transcribed (loop, rev, conc: all P), but Absys has one computation per session: the primary's two SPAWN texts are conjoined by the harness into one derivation (A5), and a conjunction with loop(x) has no solutions, so B's b = <3,2,1> is not a solution of what the system holds. Two computations sharing no unknowns can be written as the two alternatives of one or (variants P09a.AB.or, P09a.BA.or: 3 R tokens, {, or, }), each a derivation of its own, which keeps each computation's solutions on every input sharing no unknowns. Under depth-first the or's order decides whether B runs, which is operational, not meaning."),
 'P09b':("expressible with reformulation","As P09a: conjoined (primary), A's failure removes the only derivation and B is reported unsatisfiable; the or variant (3 R tokens) keeps each computation's outcomes, A's failure being its own derivation's."),
 'P09c':("expressible with reformulation","n > 5 and n <= 5 need comparisons, which no Absys notation has. gt, le, pos, nonneg (71 R tokens) define them from arithmetic over the least relation pos; equivalent over the integers, but they do not fail finitely on a false comparison (pos of a non-positive number descends without end), which costs termination, not meaning."),
 'P09d':("expressible","genu and sum3 transcribed (all P). Under P09d1 the least relation and under P09d2 the stream reading, the same text; Absys builds the partial list incrementally."),
 'P09e':("expressible","Two arithmetic relations, transcribed (all P)."),
 'P10a':("expressible with reformulation","An Absys variable takes one value; a named quantity is written as a history list with version names (27 R tokens), the current value its last element. Keeps the meaning of 'b becomes e' on every input (b inside e is the previous version)."),
 'P10b':("expressible with reformulation","As P10a, and the standing relation d = k * b as dbl over the two history lists (R) with key p (C, 2 tokens); the relation itself e = dk * r is P. 72 R tokens in all."),
 'P10c':("expressible with reformulation","As P10a: history lists for b and d (36 R tokens); the snapshot dv1 = dk * bv1 is P."),
 'P10d':("expressible with reformulation","x > k reformulated with gt/pos (38 R tokens of definitions), and the withdrawal, which Absys cannot do (an assertion's failed derivations are gone), carried out by restating the information not withdrawn of a new unknown x3 (4 R tokens). Both keep the meaning if x3 is read as x from stage 3 on; observe() still asks for x, which keeps its stage-2 values."),
 'P11a':("not expressible","x >= 2 needs a comparison; tout (emit) and not exist only in the 1990 notation, which has no arithmetic to define one. The only text is the named variant P11a.ne, which replaces x >= k by not(x = 1), the same only on pick's three facts (10 R tokens); no primary."),
 'P11b':("not expressible","As P11a; named variant P11b.ne."),
 'P11c':("expressible","pick, emit and x != 1 (as not(x = 1)) transcribed, all P. The commit stage has no construct (Absys selects none): one omission, judged by the problem's rule for a system that cannot select."),
 'P11d':("expressible","As P11c; commit is one omission."),
}
for conf in CONFS:
    for sp,(ex,why) in EX.items():
        E.append({"configuration":conf,"subproblem":sp,"direction":None,"expressibility":ex,"reason":why})
E.append({"configuration":"all three","subproblem":"P09a (rev, conc)","direction":"rev(known, unknown); conc(known, known, unknown) within it","expressibility":"expressible","reason":"Only the direction of P03e is used; the definitions are transcribed."})

# ---------- S mechanisms ----------
SM=[]
for conf in CONFS:
    for k in tok:
        SM.append({"configuration":conf,"program":k.split('/',1)[1],"mechanism":"none","listed_at_phase_4":True,"tokens":0,
                   "note":"harnesses/absys/S-mechanisms.md lists none; the program supplies none (gt, le, pos, nonneg, dbl and the history lists are written for this problem's relations: R, rule 19 by analogy, not general mechanisms)"})

doc={"tokens":tok,"outcomes":O,"mode_differences":[],"expressibility":E,"late_definition":[],"s_mechanisms":SM,
     "notes":{"mode_differences":"Every cost and storage record of P09, P10, P11, in all three configurations, gives the same classification on every stage as its behaviour run (scripts compare_modes.py and compare_modes.out). The only difference is attempt history: in P09d the behaviour run hit the 60 s limit once before its rerun reached the budget, while the cost and storage runs reached the budget at the first attempt. No raw-rerun-m2 records exist for these problems.",
              "late_definition":"No P08 program in this batch.",
              "shared_texts":"Every text is byte-identical in the three configurations, and its tokens are classed once, under its absys path; no token's class differs between configurations (no S mechanism in any)."}}
json.dump(doc,open(f'{OUT}/absys.json','w'),indent=1,ensure_ascii=False)
print('outcomes',len(O))
from collections import Counter
print(Counter((o['semantic']) for o in O))
