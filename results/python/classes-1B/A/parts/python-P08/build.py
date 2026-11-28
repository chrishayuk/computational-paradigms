import json, glob, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from frame import spans
from spec_core import core_P08a, core_P08b, core_P08c
from spec_ext import ext_P08a, ext_P08b, ext_P08c
from spec_std import std_P08a, std_P08b, std_P08c
OUT=os.path.dirname(os.path.abspath(__file__))
RES='results/python'
SPECS={'core/P08a.py':core_P08a,'core/P08b.py':core_P08b,'core/P08c.py':core_P08c,
       'extended/P08a.py':ext_P08a,'extended/P08b.py':ext_P08b,'extended/P08c.py':ext_P08c,
       'stdlib-concurrency/P08a.py':std_P08a,'stdlib-concurrency/P08b.py':std_P08b,'stdlib-concurrency/P08c.py':std_P08c}
tokens={}; totals={}
for path,spec in SPECS.items():
    out,rows=spans(path,spec)
    tokens[path]=out
    t={}
    for s in out: t[s['class']]=t.get(s['class'],0)+s['to']-s['from']+1
    t['all']=len(rows); totals[path]=t

def rec(cfg,inst):
    f=glob.glob(f'./{RES}/{cfg}/P08/raw/{inst}.behaviour.*.json')
    assert len(f)==1; return f[0].split('classifier-1B-A/')[1]

O=[]
def add(cfg,inst,stage,**k):
    prog=inst+'.py'
    e=dict(configuration=cfg,instance=inst,program=prog,record=rec(cfg,inst),stage=stage,reached=True,
           semantic=None,representation=None,simplification=None,identical_to_posed=None,residual_size=None,
           execution_state=None,residual_equivalence=None,observations=None,rule=None)
    e.update(k); O.append(e)
def both(x): return {"closed":x,"open":x}
NR=dict(reached=False,semantic="not reached",representation=None,simplification=None,identical_to_posed=None,
        residual_size=None,execution_state=["not reached"])
SPECR="SPECIFICATION.md Outcomes 1-3; problems/08-late-definition.md (classified under both readings)"

# ---------- core ----------
OBS_C1="unknowns x, y, z are objects of the program's class Unknown, shown by name; a bound to the tuple (x, y, z); no alternatives; nothing suspended (0); no conclusion withdrawn; no manual action"
for inst in ['P08a','P08b']:
    add('core',inst,1,semantic=both("complete"),representation="solved form",execution_state=["finished"],
        residual_equivalence="a = <x, y, z>, x, y, z free: exactly the valid outcome under both readings",
        observations=OBS_C1,rule=SPECR)
    add('core',inst,2,semantic={"closed":"unsound","open":"complete"},representation="solved form",
        execution_state=["error"],
        residual_equivalence="what observe() reads is the binding a = <x, y, z> (b free). The registered list still shows ('rev', (a, b)) only because NameError was raised before decide() removed it; the process ended, so it is not state acted on at a later stage (SPECIFICATION.md, Representation) and rev(a, b) is dropped, not held. Open reading: a = <x, y, z>, b free is the valid outcome's equations, with rev(a, b) dropped (problem file: complete / solved form, the dropping recorded). Closed reading: valid is none; the binding denotes solutions, and none was reported: unsound.",
        observations="State 3 of the problem file: an application of an undefined relation is an error (NameError: name 'rev' is not defined, verbatim in the record). Pending application: none held after the error (the suspended count of 1 is the list frozen at the exception). Alternatives 0. No answer collected (ended_by error). No conclusion withdrawn. No manual action; the harness reposes the next stage after the error (restart cost).",
        rule=SPECR+"; AMENDMENTS 3.2 (the stage was posed and erred)")
core_stop="the run stopped at stage 2: every reposed run replays stage 2, which raises NameError again; the record notes that stage %d was never posed (restart_cost = the replay's whole count, 507 steps in P08a, 485 in P08b)"
for k in range(3,7):
    add('core','P08a',k,**NR,residual_equivalence=None,observations=core_stop%k+". The record's own state field says error; that error is the replayed stage 2's.",rule="AMENDMENTS 3.2; brief: a reposed stage the replay did not reach is not reached")
add('core','P08b',3,**NR,observations=(core_stop%3)+". P08b: the report at stage 2 (an error with a traceback) can be told apart from failure (which this program would print as 'no solution: ...'); it shows state 3, a reference to an unavailable definition.",rule="AMENDMENTS 3.2")
add('core','P08c',1,semantic=both("complete"),representation="solved form",execution_state=["finished"],
    residual_equivalence="no unknown is constrained (b free, bindings {}); the valid outcome is 'no unknowns', the same under both readings. Nothing was printed, which is right for a stage that constrains nothing",
    observations="b is an Unknown object; nothing held (0), no alternatives; conc defined by def; no manual action",rule=SPECR)
add('core','P08c',2,semantic={"closed":"unsound","open":"complete"},representation="solved form",execution_state=["error"],
    residual_equivalence="observe() reads bindings {}: b free; rev(<1,2>, b) appears in the registered list only because the exception came before its removal, and the process ended, so it is dropped. Open: b free is the valid outcome with the pending application dropped: complete / solved form. Closed: valid is none; b free was reported: unsound",
    observations="State 3: NameError: name 'rev' is not defined (verbatim in the record). No pending application survives. No manual action",rule=SPECR+"; AMENDMENTS 3.2")
for k in (3,4):
    add('core','P08c',k,**NR,observations="the run stopped at stage 2: the reposed replay of stage 2 raises NameError again; stage %d was never posed (restart_cost 254 = the replay's whole count). So the program never shows what happens to the application at stage 3 or whether stage 4 can reach it"%k,rule="AMENDMENTS 3.2")

# ---------- extended ----------
OBS_E1="unknowns are S.suspend Vars, unbound ones shown by name; a bound to cons cells (x, (y, (z, ()))); no alternatives (stack empty); nothing suspended (0); no manual action"
for inst in ['P08a','P08b']:
    add('extended',inst,1,semantic=both("complete"),representation="solved form",execution_state=["finished"],
        residual_equivalence="a = <x, y, z>, the rest free: the valid outcome",observations=OBS_E1,rule=SPECR)
    add('extended',inst,2,semantic=both("complete"),representation="residual",
        simplification={"closed":"inconsistency undetected","open":"reduced"},identical_to_posed=True,
        residual_size="residual: binding a = <x, y, z> and 1 relation, rev(a, b) (2 occurrences of unknowns; 4 with a's places substituted); input: 2 relations (a = <x, y, z>, rev(a, b)), 6 occurrences",
        execution_state=["suspended"],
        residual_equivalence="held: a = <x, y, z>; b free; rev(<x,y,z>, b) pending in the queue. Open reading: identical to the valid outcome (a = <x,y,z>; b free; rev(a, b) pending), and nothing smaller exists. Closed reading: rev has no instances, so the held conditions denote the empty set, which is the valid outcome (none), but the program did not report none: complete with inconsistency undetected",
        observations="State 4: the application is held as an Application in the suspension queue (q.held, 1 item), waiting on the Var 'rev is defined'. Alternatives 0. The answer printed is the binding of a only; the residual is read from the registered queue. No conclusion withdrawn; no manual action",rule=SPECR)
    add('extended',inst,3,semantic=both("complete"),representation="residual",
        simplification={"closed":"inconsistency undetected","open":"reduced"},identical_to_posed=False,
        residual_size="residual: x identified with y, a = <y, y, z>, 1 relation rev(a, b); input: 3 relations, 8 occurrences",
        execution_state=["suspended"],
        residual_equivalence="held: x = y (x bound to y), a = <y, y, z>, b free, rev(<y,y,z>, b) pending: exactly the open reading's valid outcome. Closed: denotes the empty set (rev has no instances), none not reported",
        observations="x = y was decided by unification (x's Var bound to y's), and the held application now reads rev(<y,y,z>, b); suspended 1, alternatives 0; no manual action"+("; P08b: this is the last stage. The report (an answer plus a held application, state suspended) can be told apart from failure, which this program prints as 'no solution: these do not hold'. It shows state 4, a computation awaiting its definition" if inst=='P08b' else ""),rule=SPECR)
add('extended','P08a',4,semantic=both("partial"),representation="solved form",execution_state=["alternatives pending"],
    residual_equivalence="Reported (answer and observe(), both by Var name): a = <h,h,h>, b = <h,h,h>, x = h, y = h, z = h. Read as written, every unknown is the one unknown h, which denotes only the solutions with x = y = z: a nonempty proper subset of the valid outcomes (x = y, a = <y,y,z>, b = <z,y,y>, z free), hence partial. By hand trace of unify and Queue.bind (scripts not run), the held state is right: x -> y -> h1 -> h2 -> h6 and z -> h3 -> h4 -> h5 are two distinct Vars that rev_2 and conc_2 both created with the name 'h', and b = <h5, h6, h6> = <z, y, y>. So the state held is equivalent, but the report does not show it: two different unknowns are printed under one name. Classified on the report; disputable (undetermined, or complete on the held state)",
    observations="The pending application was resumed in the same computation, with no reposing, when the definitions arrived (q.bind woke it, q.run ran it), and was solved by depth-first search, its first solution kept. Suspended 0. Alternatives pending: 11 choice points left on the registered search stack. The search generator that owns them has been dropped, though, so nothing could resume them (Python has no request for more answers). Problem operations (cost run): rev 4, conc 6, the closed forms for n = 3. Under the closed reading this stage's valid outcome contradicts stages 2 and 3 (none), but the program never reported none there, so nothing was withdrawn. No manual action",
    rule=SPECR+"; Representation (unknowns identified with other unknowns: solved form)")
add('extended','P08a',5,semantic=both("complete"),representation="solved form",execution_state=["alternatives pending"],
    residual_equivalence="reported a = b = <h,h,h>, x = y = z = h. y = z unified h6 with h5, so every name now stands for one Var: x = y = z, a = b = <z, z, z>, which is the valid outcome",
    observations="11 stale choice points still registered; suspended 0; no manual action",rule=SPECR)
add('extended','P08a',6,semantic=both("complete"),representation="explicit",execution_state=["alternatives pending"],
    residual_equivalence="a = b = <42,42,42>, c = <42,42>, x = y = z = 42: the valid outcome",
    observations="the 11 stale choice points are still registered (state alternatives pending, per the harness); suspended 0; no manual action",rule=SPECR)
add('extended','P08c',1,semantic=both("complete"),representation="solved form",execution_state=["finished"],
    residual_equivalence="b free; no unknowns constrained: the valid outcome under both readings",observations="conc's two cases added; nothing held; no manual action",rule=SPECR)
add('extended','P08c',2,semantic=both("complete"),representation="residual",simplification={"closed":"inconsistency undetected","open":"reduced"},identical_to_posed=True,
    residual_size="residual: 1 relation rev(<1,2>, b), 1 occurrence of an unknown; input: the same",execution_state=["suspended"],
    residual_equivalence="held rev(<1,2>, b) pending, b free: the open reading's valid outcome exactly. Closed: rev has no instances, so this denotes the empty set; none not reported",
    observations="State 4: Application held in the queue on the Var 'rev is defined' (1 item); no manual action",rule=SPECR)
add('extended','P08c',3,semantic={"closed":"complete","open":"unsound"},representation="explicit",execution_state=["finished"],
    residual_equivalence="printed 'no solution: these do not hold: [rev(<1,2>, b)]' (also in the registered failed list). Closed: none is the valid outcome, reported as none. Open: valid is b free with the application pending, since case 2 may yet arrive; reporting none is unsound",
    observations="The arrival of case 1 bound 'rev is defined' and woke the application, which was solved with the partial definition (the cost run counts 1 rev application) and failed. It is not held any more (suspended 0), so it is failed, not held. No manual action",rule=SPECR)
add('extended','P08c',4,semantic=both("unsound"),representation="explicit",execution_state=["finished"],
    residual_equivalence="still reports no solution; the valid outcome under both readings is b = <2, 1>",
    observations="Case 2 was added, but the application failed at stage 3 and is no longer held. q.bind on the already bound Var wakes nothing, so stage 4 cannot reach the application, and it is not posed again (no restart). The closed reading's stage-3 conclusion (none) is withdrawn by the valid outcomes, but the program does not withdraw it and goes on reporting none. No manual action",rule=SPECR)

# ---------- stdlib-concurrency ----------
OBS_S1="unknowns are Unknown objects shown by name; a bound to (x, y, z); no thread waiting (0); no alternatives; no manual action"
for inst in ['P08a','P08b']:
    add('stdlib-concurrency',inst,1,semantic=both("complete"),representation="solved form",execution_state=["finished"],
        residual_equivalence="a = <x, y, z>: the valid outcome",observations=OBS_S1,rule=SPECR)
    add('stdlib-concurrency',inst,2,semantic=both("complete"),representation="residual",simplification={"closed":"inconsistency undetected","open":"reduced"},identical_to_posed=True,
        residual_size="residual: binding a = <x, y, z> and 1 relation rev(a, b); input: 2 relations, 6 occurrences",execution_state=["suspended"],
        residual_equivalence="held: a = <x,y,z>; rev(a, b) waiting in its thread: the open reading's valid outcome. Closed: denotes the empty set; none not reported",
        observations="State 4 in effect, kept by a permission flag: the relation's thread waits on the condition 'changed' until rev is flagged as defined (1 waiting). No alternatives; no manual action",rule=SPECR)
    add('stdlib-concurrency',inst,3,semantic=both("complete"),representation="residual",simplification={"closed":"inconsistency undetected","open":"reducible"},identical_to_posed=True,
        residual_size="residual: binding a = <x, y, z> and 2 relations, rev(a, b) and x = y (4 occurrences); input: 3 relations, 8 occurrences; smaller: x identified with y and only rev(a, b) left",
        execution_state=["suspended"],
        residual_equivalence="held: a = <x,y,z>, rev(a, b), x = y, which is equivalent to the open valid outcome (x = y, a = <y,y,z>, b free, rev pending). x = y is held as a relation, because the evaluator of = cannot decide two unknown places, so a smaller form exists: reducible. Closed: denotes the empty set",
        observations="Two relation threads waiting (rev(a, b), x = y). The answer line repeats only a = <x,y,z>, so the residual is what is classified (SPECIFICATION.md, Representation). No manual action"+("; P08b: last stage. The report (threads waiting, suspended) can be told apart from failure (which would print 'no solution'); it shows the application held, waiting on a permission flag that never comes" if inst=='P08b' else ""),rule=SPECR)
add('stdlib-concurrency','P08a',4,semantic=both("complete"),representation="residual",simplification=both("reducible"),identical_to_posed=False,
    residual_size="residual: a = <x, y, z>, b = <z, y, x>, 1 relation x = y (2 occurrences); input: 3 relations and the definitions; smaller: x identified with y, no relation left",
    execution_state=["suspended"],
    residual_equivalence="held: a = <x,y,z>, b = <z,y,x>, x = y, which is equivalent to the valid outcome (x = y, a = <y,y,z>, b = <z,y,y>). The answer line alone (a and b, without x = y) is not valid, so the residual form is classified",
    observations="The definition's arrival (arrived('rev')) woke the rev thread in the same computation; it decided b forwards. The cost run counts rev 4 and conc 6, the closed forms. 1 thread waiting (x = y). No alternatives; no withdrawal shown; no manual action",rule=SPECR)
add('stdlib-concurrency','P08a',5,semantic=both("complete"),representation="residual",simplification=both("reducible"),identical_to_posed=False,
    residual_size="residual: a = <x,y,z>, b = <z,y,x>, 2 relations x = y and y = z (4 occurrences); smaller: x, y, z identified",
    execution_state=["suspended"],
    residual_equivalence="held: a = <x,y,z>, b = <z,y,x>, x = y, y = z, which is equivalent to x = y = z, a = b = <z,z,z>",
    observations="2 threads waiting; no manual action",rule=SPECR)
add('stdlib-concurrency','P08a',6,semantic=both("unsound"),representation="solved form",execution_state=["finished"],
    residual_equivalence="reported a = b = <42,42,42>, x = y = z = 42, and nothing of c: c is left unconstrained, so the report denotes outcomes with any c, where the valid outcome has c = <42,42> only. Cause, from the program and the cost run (equal applied 4 times, prefix once): prefix() receives the values of its places, so it poses the remainder equation as (None, (y, x)), the value of c and not the place c. That equation binds nothing, and c = <y, x> is lost",
    observations="No thread waiting; the dropped equation is not recorded anywhere; no manual action",rule=SPECR+" (unsound: the report denotes an outcome that is not valid)")
add('stdlib-concurrency','P08c',1,semantic=both("complete"),representation="solved form",execution_state=["finished"],
    residual_equivalence="no unknowns constrained: the valid outcome",observations="nothing held; no manual action",rule=SPECR)
add('stdlib-concurrency','P08c',2,semantic=both("complete"),representation="residual",simplification={"closed":"inconsistency undetected","open":"reduced"},identical_to_posed=True,
    residual_size="residual: 1 relation rev(<1,2>, b), 1 occurrence; input: the same",execution_state=["suspended"],
    residual_equivalence="held rev(<1,2>, b) waiting in its thread: the open valid outcome; closed: the empty set, none not reported",
    observations="1 thread waiting on the permission flag; no manual action",rule=SPECR)
add('stdlib-concurrency','P08c',3,semantic={"closed":"complete","open":"unsound"},representation="explicit",execution_state=["finished"],
    residual_equivalence="printed 'no solution: these relations do not hold: [('rev', ((1, 2), b))]'. Closed: none is right; open: unsound, since case 2 may yet arrive",
    observations="arrived('rev') with case 1 only woke the thread, which decided rev(<1,2>, b) with the partial definition (the cost run counts 1 rev call): no case applies, so it does not hold. The thread ended (failed, not held). No manual action",rule=SPECR)
add('stdlib-concurrency','P08c',4,semantic=both("unsound"),representation="explicit",execution_state=["finished"],
    residual_equivalence="still 'no solution'; valid is b = <2, 1> under both readings",
    observations="The second arrived('rev') wakes nothing: the relation's thread has ended, and the failed relation is not posed again. Stage 4 cannot reach the application. The closed reading's stage-3 none is withdrawn by the valid outcomes, but the program does not withdraw it. No manual action",rule=SPECR)

# mode comparisons
compared=sorted(os.path.relpath(f,'.') for f in glob.glob('./results/python/*/P08/raw/*.json') if '.behaviour.' not in f)

EXPR=[]
def ex(cfg,sub,e,reason): EXPR.append(dict(configuration=cfg,subproblem=sub,direction="rev forwards (first place known), conc forwards inside rev; = and ++ in the directions the stages leave open",expressibility=e,reason=reason))
for sub in ['P08a','P08b']:
    ex('core',sub,'expressible with reformulation',"rev and conc are transcribed as forward functions, P by rule 3 (the only direction the queries use). Holding the stage's equations and the application until values arrive takes code core does not have: an Unknown place class, the held list and decide(), and the evaluators' known-place tests and wait verdicts, all R by rule 19"+(" (and an unused ++ evaluator, R)" if sub=='P08b' else "")+". Holding the application until the definition arrives could be written in core as more R (a test that the name is bound). This program does not hold it: it errs.")
    ex('stdlib-concurrency',sub,'expressible with reformulation',"as core: rev and conc are P (rule 3), and the holding (Unknown, the waiting list, the evaluators' known tests) is R by rule 19. The threads, the condition, the busy count and the permission flag are C; threading is an external mechanism, not S")
    ex('extended',sub,'expressible',"conc's and rev's cases are transcribed relationally, as heads unified with the goal and bodies in the stated order (P), with a = <x,y,z> and the other equations as unifications. They run on the configuration's S: the listed search and suspension queue, and the program's own unifier, resolution and wait-for-definition layer. The only R is the failed store (5 tokens), which is not a reformulation of a definition")
ex('core','P08c','expressible with reformulation',"as P08a, and one more: a Python def replaces a function and cannot add a case to it, so stage 4's def restates case 1 (R) beside case 2")
ex('stdlib-concurrency','P08c','expressible with reformulation',"as core P08c: case 1 restated in stage 4's def (R); holding R; threads C")
ex('extended','P08c','expressible',"cases are added one by one to rev's case list (stage 3: case 1 from the stage's constants; stage 4: case 2) with no restatement; the transcription is P")

LD=[]
for inst in ['P08a','P08b','P08c']:
    LD.append(dict(configuration='core',program=inst+'.py',kind='neither',evidence={
      'P08a':"reverse() (tokens 376-442; the call r = rev(a) is in 394-401) applies rev as soon as a has a value. rev is bound only by stage 4's def (968-1008), so at stage 2 the application raises NameError. The record has stage 2 as error with that NameError, and stages 3-6 not reached, since every reposed replay errs again at stage 2. Nothing waits: the program takes state 3 (an error)",
      'P08b':"the same reverse() (365-431); stage 2 errs with NameError and stage 3 is not reached. The definition never arrives, and the application is never held",
      'P08c':"reverse() (245-311) calls rev at stage 2, before stage 3's def (827-850): NameError at stage 2, and stages 3 and 4 not reached. So the partial definition is never seen"}[inst]))
LD.append(dict(configuration='extended',program='P08a.py',kind='code awaited',evidence="Application.__call__ (S, tokens 429-552) tests cases[name], the relation's definition itself, held as data that arrives at its stage: stage 4 adds the case functions to cases (1345-1374). Until then it waits in the queue (q.wait, C, 1080-1084 and 1095-1096) on the Var defined['rev'] (S, 77-94). Records: stages 2 and 3 suspended, 'applications waiting for a definition' = {1: rev(<x,y,z>, b)}; at stage 4 the queue is empty and b is solved in the same computation. Caveat: the wake-up is by binding that Var (q.bind, 1375-1398, C), a signal the stage gives beside the definition, so the waiting is on a flag that announces the code, and the readiness test is the code's presence"))
LD.append(dict(configuration='extended',program='P08b.py',kind='code awaited',evidence="the same layer (Application, 422-545; q.wait 1013-1017, 1028-1029). Stages 2 and 3 are suspended with rev(...) held; the definition never comes, so it stays held"))
LD.append(dict(configuration='extended',program='P08c.py',kind='code awaited',evidence="Application (440-563) waits on defined['rev'] (88-105), bound at stage 3 when case 1 is appended (1197-1220). It is then solved with the cases present (case 1 only) and fails: the record shows stage 3 finished with 'no solution: [rev(<1,2>, b)]'. Stage 4 appends case 2 (1305-1316), but the application is no longer held, and q.bind on the bound Var wakes nothing (1317-1328). So it waits for the definition's first part only"))
LD.append(dict(configuration='stdlib-concurrency',program='P08a.py',kind='permission awaited',evidence="reverse()'s guard (C, tokens 423-434) is `a is not None and \"rev\" in defined`, a flag that arrived('rev') sets (1247-1251; arrived() 789-814). The thread waits on the condition 'changed' (wait_for, in 632-665) until news, then re-tests the flag. rev's def (1192-1232) is executed at stage 4 too, but the waiting is on the flag, not on the name. Records: stages 2 and 3 suspended with ('rev', (a, b)) waiting in its thread; at stage 4 b = <z, y, x> is decided in the same computation"))
LD.append(dict(configuration='stdlib-concurrency',program='P08b.py',kind='permission awaited',evidence="the same guard (412-423); the flag is never set, so the thread waits through stage 3 (suspended, 2 threads waiting)"))
LD.append(dict(configuration='stdlib-concurrency',program='P08c.py',kind='permission awaited',evidence="the guard (292-303) is passed when stage 3's arrived('rev') (1090-1094) sets the flag with case 1 only. The thread decides rev(<1,2>, b) false and ends (record: stage 3 finished, 'no solution'). Stage 4's arrived('rev') (1177-1181) finds no waiting thread"))

def stok(path,pred):
    return sum(s['to']-s['from']+1 for s in tokens[path] if s['class']=='S' and pred(s['construct']))
SM=[]
for inst in ['P08a','P08b','P08c']:
    SM.append(dict(configuration='core',program=inst+'.py',mechanism='none',listed_at_phase_4=None,tokens=0,note="core admits no S; the holding code is R (rule 19)"))
    SM.append(dict(configuration='stdlib-concurrency',program=inst+'.py',mechanism='none (threading is an external mechanism, its calls classed C)',listed_at_phase_4=None,tokens=0,note="external mechanism: threading (Thread, Condition)"))
    p='extended/'+inst+'.py'
    SM+= [dict(configuration='extended',program=inst+'.py',mechanism='backtracking search (S/search.py: search, undo; the trail convention)',listed_at_phase_4=True,tokens=0,note="176 tokens, counted once for the configuration in S/search.py; called from the program's Application layer"),
          dict(configuration='extended',program=inst+'.py',mechanism='suspension queue (S/suspend.py: Var, deref, Queue)',listed_at_phase_4=True,tokens=0,note="537 tokens, counted once in S/suspend.py; the program's q.wait / q.bind / q.run are C"),
          dict(configuration='extended',program=inst+'.py',mechanism='unification (the program\'s unify(), with its binder Queue and trail)',listed_at_phase_4=False,tokens=stok(p,lambda c:c.startswith('unify') or c.startswith('binder'))),
          dict(configuration='extended',program=inst+'.py',mechanism='resolution (children, done)',listed_at_phase_4=False,tokens=stok(p,lambda c:c.startswith('children'))),
          dict(configuration='extended',program=inst+'.py',mechanism='wait-for-definition layer (defined Vars, NAME, class Application)',listed_at_phase_4=False,tokens=stok(p,lambda c:c.startswith('defined') or c.startswith('NAME')))]
for p in SPECS:
    if p.startswith('extended'):
        assert sum(x['tokens'] for x in SM if x['configuration']=='extended' and x['program']==p.split('/')[1])==totals[p].get('S',0),p

doc=dict(tokens=tokens,outcomes=O,mode_differences=[],mode_records_compared=compared,expressibility=EXPR,late_definition=LD,s_mechanisms=SM,token_totals=totals)
json.dump(doc,open(os.path.join(OUT,'python.json'),'w'),ensure_ascii=False,indent=1)
print(json.dumps(totals,indent=0))
print(len(O),'outcome entries;',len(compared),'mode records compared')
