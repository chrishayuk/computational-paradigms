import json,glob,os
from build import load,spans
REPO='.'
def rec(cfg,inst,mode='behaviour'):
    fs=glob.glob(f'{REPO}/results/algol-60/{cfg}/P*/raw/{inst}.{mode}.*.json'); assert len(fs)==1,(cfg,inst,fs)
    return os.path.relpath(fs[0],REPO)
# ---------- tokens
tokens={}
for fn in sorted(glob.glob('specs/*.py')):
    b=os.path.basename(fn)[:-3]; cfg,f=b.split('_',1); text=cfg+'/'+f
    sp,n=spans(text,load(fn))
    cov=[0]*n
    for s in sp:
        for j in range(s['from'],s['to']+1): cov[j]+=1
    assert all(c==1 for c in cov),text
    tokens[text]=sp
# ---------- outcomes
O=[]
def add(cfg,inst,prog,stage,**kw):
    d={'configuration':cfg,'instance':inst,'program':prog,'record':rec(cfg,kw.pop('rinst',inst)),'stage':stage,'computation':kw.pop('computation','main'),
       'attempt':kw.pop('attempt',1),'reading':kw.pop('reading',None),
       'reached':True,'semantic':None,'representation':None,'simplification':None,'identical_to_posed':None,'residual_size':None,
       'execution_state':[],'residual_equivalence':None,'answer_completeness':None,'observations':None,'rule':None,'harness_fault':False}
    d.update(kw); O.append(d)
EXT={'report':'alg','x1':'a60','x1sim':'a60'}
NONE_REP_UNK='x is never given a value: it is represented by the Boolean xk (false) beside an integer xv, never set'
for cfg in ['report','x1','x1sim']:
    e=EXT[cfg]
    budget_or = 'budget' if cfg!='x1sim' else None
    # ---- P09a
    for inst in ['P09a.AB','P09a.BA']:
        prog=f'{inst}.{e}'
        if cfg!='x1sim':
            A=dict(computation='A',semantic='none reported',representation=None,execution_state=['budget'],
                   answer_completeness='valid outcomes empty; the program did not report that there are none (no)',
                   observations=NONE_REP_UNK+'. loop recurses until the 10^6-step budget fires (stderr: "line 75: stopped after N steps"); no answer, no observe block (the process ended). No alternatives or suspended work held. No manual action. Steps for A are its own budget (in BA, a re-created process with B as its prefix, prefix steps not charged).',
                   rule='SPECIFICATION Outcomes 1 (none reported); 3 (budget); PROTOCOL Running (each spawned computation its own budget)')
        if inst=='P09a.AB':
            if cfg!='x1sim': add(cfg,inst,prog,1,**A)
            else:
                add(cfg,inst,prog,1,computation='A',attempt=1,semantic='none reported',execution_state=['timeout'],
                    answer_completeness='valid outcomes empty; none reported (no)',
                    observations='x1sim has no budget; the 60 s safety limit stopped A (SIGKILL); no output. '+NONE_REP_UNK+'. No manual action.',rule='SPECIFICATION Outcomes 3 (timeout); PROTOCOL Running (safety limit, one rerun)')
                add(cfg,inst,prog,1,computation='A',attempt=2,semantic='none reported',execution_state=['error'],
                    answer_completeness='valid outcomes empty; none reported (no)',
                    observations='safety rerun under the 600 s limit: the process ended at about 69 s with signal SIGKILL and no error text, before the limit (safety_limit.hit false); the record does not say what sent the signal (presumably exhaustion of the simulator\'s store by the unbounded recursion, not established). Final state of the stage: error, verbatim "(no error text on stderr)". Not a timeout.',
                    rule='SPECIFICATION Outcomes 3 (error); harness README 2.4')
            for att in ([1] if cfg!='x1sim' else [1,2]):
                add(cfg,inst,prog,1,computation='B',attempt=att,reached=False,semantic='not reached',execution_state=[],
                    observations='B was never started: computation A, spawned first, ended the one instance (its process) by '+('its budget' if cfg!='x1sim' else ('the safety limit' if att==1 else 'SIGKILL'))+', so there was no instance to start B in (harness QUESTIONS A3; record: execution_state.determined false). B\'s outcome is therefore not reported when A runs first: the order of posing matters, and the configuration runs spawned computations only one after another (side_by_side false).',
                    rule='AMENDMENTS 3.2 (not reached, with what stopped the run)')
        else:  # BA
            for att in ([1] if cfg!='x1sim' else [1,2]):
                add(cfg,inst,prog,1,computation='B',attempt=att,semantic='complete',representation='explicit',execution_state=['finished'],
                    answer_completeness='1/1 valid, 0 invalid',
                    observations='b = (3, 2, 1) printed as an answer and as [bind b]; rev/1 1, rev/2 3, conc/1 3, conc/2 3 applications (the problem\'s n(n+1)/2 = 6 conc applications beyond rev\'s for n = 3). No unknown remains in B. No alternatives or suspended work. B ran to its end before A was spawned (side_by_side false). No manual action.',
                    rule='SPECIFICATION Outcomes 1, 2, 3')
            if cfg!='x1sim': add(cfg,inst,prog,1,**A)
            else:
                add(cfg,inst,prog,1,computation='A',attempt=1,semantic='none reported',execution_state=['timeout'],
                    answer_completeness='valid outcomes empty; none reported (no)',
                    observations='after B finished, A ran until the 60 s safety limit (SIGKILL). '+NONE_REP_UNK+'.',rule='SPECIFICATION Outcomes 3 (timeout)')
                add(cfg,inst,prog,1,computation='A',attempt=2,semantic='none reported',execution_state=['error'],
                    answer_completeness='valid outcomes empty; none reported (no)',
                    observations='safety rerun (600 s): B again finished with b = (3, 2, 1); A\'s process then ended at about 69 s by SIGKILL with no error text, before the limit; final state error. The record does not say what sent the signal.',
                    rule='SPECIFICATION Outcomes 3 (error)')
    # ---- P09b
    prog=f'P09b.{e}'
    add(cfg,'P09b',prog,1,computation='A',semantic='complete',representation='explicit',execution_state=['finished'],
        answer_completeness='valid outcomes empty; the program reported that there are none (yes: "no solution" in its observe block)',
        observations='No answer printed; observe "computation A ended / no solution". equals bound x to 1 while its continuation ran, the second conjunct tested 1 = 2 and failed, then x was unbound (xk false again). No alternatives or suspended work. Representation recorded as explicit for an empty set (no solution to give as values).',
        rule='SPECIFICATION Outcomes 1 (complete; empty reported as empty)')
    add(cfg,'P09b',prog,1,computation='B',semantic='complete',representation='explicit',execution_state=['finished'],
        answer_completeness='1/1 valid, 0 invalid',
        observations='y = 3 printed. A\'s failure did not affect B: B ran after A in the same instance and gave its answer. The two share the program\'s variables but no unknown. No observe bindings tag; the value is in the answer. No manual action.',
        rule='SPECIFICATION Outcomes 1, 2, 3')
    # ---- P09c
    add(cfg,'P09c',f'P09c.{e}',1,semantic='complete',representation='explicit',execution_state=['finished'],
        answer_completeness='1/1 valid, 0 invalid',
        observations='total = 6, s = (1, 2, 3, 4, 5), also as [bind s] and [bind total]. gen/1 1, gen/2 5, sum3/1 1. The consumer did not act on s before the producer finished: gen ran to its end, then sum3 began (the program says so in observe, and its code is sequential). No alternatives or suspended work. No manual action.',
        rule='SPECIFICATION Outcomes 1, 2, 3')
    # ---- P09d
    for rd in ['P09d1','P09d2']:
        if cfg!='x1sim':
            add(cfg,'P09d',f'P09d.{e}',1,reading=rd,semantic='none reported',execution_state=['budget'],
                answer_completeness=('valid outcomes empty; none reported (no)' if rd=='P09d1' else '0/1 valid (total = 6 not computed), 0 invalid'),
                observations='genu recursed until the budget fired (stderr "line 20: stopped after 1000000 steps"); a cell is made only when genu(n+1) returns, so s holds no element and total is never bound: no binding of total held while the producer ran (so nothing to record under P09d1\'s observation rule). sum3 never began: the consumer did not act on s before the producer finished. '+('P09d1: not unsound, since total = 6 was not reported.' if rd=='P09d1' else 'P09d2: producer state budget; the stream reading\'s total = 6 is not reached.')+' No alternatives or suspended work. No manual action.',
                rule='problems/09 P09d '+('(d1: none reported with budget)' if rd=='P09d1' else '(d2)')+'; SPECIFICATION Outcomes 1, 3')
        else:
            add(cfg,'P09d',f'P09d.{e}',1,reading=rd,semantic='none reported',execution_state=['error'],
                answer_completeness=('valid outcomes empty; none reported (no)' if rd=='P09d1' else '0/1 valid, 0 invalid'),
                observations='x1sim has no budget; after about 0.1 s the run-time stopped with the error, verbatim, "Error: Wrong result type in TIRD" (exit 1), before any answer or observe block. That this is the X1 run-time\'s response to the unbounded recursion of genu is likely but not shown by the record. total never bound; sum3 never began. No manual action.',
                rule='SPECIFICATION Outcomes 3 (error, recorded verbatim)')
    # ---- P09e
    pad = ' (x1 pads the integers: "x = y + +       1            , y = x - +       1            ")' if cfg=='x1' else ''
    add(cfg,'P09e',f'P09e.{e}',1,semantic='complete',representation='residual',simplification='reducible',identical_to_posed=True,
        residual_size='residual: 2 relations, x = y + 1 and y = x - 1, with 4 occurrences of unknowns; input: the same 2 relations, 4 occurrences. The smaller equivalent x = y + 1 has 1 relation, 2 occurrences',
        execution_state=['suspended'],
        residual_equivalence='equivalent: over the integers y = x - 1 holds exactly when x = y + 1, so the conjunction of the two denotes exactly the valid outcomes, every integer pair with x = y + 1. Checked also by enumeration over [-60, 60]^2 (check_residuals.py: same 120 pairs)',
        answer_completeness='valid outcomes infinite; a finite representation equivalent to them was given (yes)',
        observations='Answer "x held, y held, where x = y + 1, y = x - 1"'+pad+'; observe lists both relations held and [suspended held-relations 2]. x and y are represented as unknown by Boolean flags, each held by a relation. Each relation was examined once and waited (neither has a known place): the program reports the mutual wait as held relations, which the harness reads as suspended, and is told apart from completion (finished) by that report. No deadlock reported as such, no enumeration. The residual is state the program holds (flags r1, r2) and acts on when a value arrives, though this one-stage problem gives none. No manual action.',
        rule='SPECIFICATION Outcomes 1 (complete), 2 (residual), simplification (reducible); harness README 2.4')
    # ---- P10a
    vals={1:'10',2:'15',3:'7'}
    for k in [1,2,3]:
        add(cfg,'P10a',f'P10a.{e}',k,semantic='complete',representation='explicit',execution_state=['finished'],
            answer_completeness='1/1 valid, 0 invalid',
            observations=f'b = {vals[k]}. Replacement is native: one integer variable assigned in place; the right side of b := b + e is taken at the value before the stage. Earlier values are not kept and cannot be retrieved'+('' if k==1 else f'; the earlier report b = {vals[k-1]} is superseded by the replacement, as the problem requires (not a withdrawal of a valid conclusion)')+'. '+('Posed into the same computation: in report and x1 re-created for its budget (recreated_for_budget, prefix not charged), in x1sim one live process. ' if k>1 else '')+'No alternatives or suspended work. No manual action.',
            rule='SPECIFICATION Outcomes 1, 2, 3')
    # ---- P10b
    add(cfg,'P10b',f'P10b.{e}',1,semantic='complete',representation='residual',simplification='reduced',identical_to_posed=True,
        residual_size='residual: 1 relation, d = 2 . b, 2 occurrences of unknowns; input: the same',
        execution_state=['suspended'],
        residual_equivalence='equivalent: it is the valid outcome itself, d = 2 . b with neither valued (check_residuals.py)',
        answer_completeness='valid outcomes infinite; a finite representation was given (yes)',
        observations='Answer "b held, d held, where d = 2 . b"; observe: standing relations d = 2 . b, [suspended held-relations 1], d-recomputed 0. b and d are unknown, each a flag false, both held by the relation. No manual action.',
        rule='SPECIFICATION Outcomes 1, 2 (residual), simplification (reduced)')
    bv={2:(10,20),3:(15,30),4:(7,14)}
    for k in [2,3,4]:
        add(cfg,'P10b',f'P10b.{e}',k,semantic='complete',representation='explicit',execution_state=['finished'],
            answer_completeness='1/1 valid, 0 invalid',
            observations=f'b = {bv[k][0]}, d = {bv[k][1]}. The standing relation is held as a flag and examined after every stage: d recomputed from the current b ({k-1} recomputation(s) so far, one per replacement, d-recomputed count). The stage-1 residual is replaced by values; the relation remains in force. Earlier values of b and d are not kept. No suspended work after b has a value. No manual action.',
            rule='SPECIFICATION Outcomes 1, 2, 3')
    cv={1:'b = 10 (d has no value)',2:'b = 10, d = 20',3:'b = 15, d = 20',4:'b = 7, d = 20'}
    for k in [1,2,3,4]:
        add(cfg,'P10c',f'P10c.{e}',k,semantic='complete',representation='explicit',execution_state=['finished'],
            answer_completeness='1/1 valid, 0 invalid',
            observations=cv[k]+'. d becomes 2 . b is an assignment computed once; d keeps 20 when b is replaced, so the snapshot is told apart from P10b\'s standing relation. "d has no value" at stage 1 states that d is not yet given, which the valid outcome (b = 10) does not contradict. Earlier values not kept. No alternatives or suspended work. No manual action.',
            rule='SPECIFICATION Outcomes 1, 2, 3')
    dv={1:'x = 1, 2, 3',2:'x = 2, 3',3:'x = 1, 2, 3'}
    for k in [1,2,3]:
        add(cfg,'P10d',f'P10d.{e}',k,semantic='complete',representation='explicit',execution_state=['finished'],
            answer_completeness=f'{3 if k!=2 else 2}/{3 if k!=2 else 2} valid, 0 invalid',
            observations=dv[k]+' printed, one answer each. The alternatives are held all at once, as the values of pick\'s facts with a flag each ([problem-alternatives x '+('2' if k==2 else '3')+'], printed by the program; it prints no [alternatives] tag, so the harness state is finished). '+
            {1:'No comparison in force; x-gt-tested 0.',
             2:'x > 1 held as a comparison in force and tested on each fact (x-gt-tested 3); x = 1 removed from the reported set.',
             3:'Stage 3 sets the comparison out of force and tests the held facts again: the alternative x = 1 that x > 1 removed comes back without restating pick (pick\'s facts are applied once in all, pick/1..3 count 1). Stage 2\'s conclusion x in {2, 3} is withdrawn, shown by x = 1 being reported again and by "withdrawn: x gt 1" in observe.'}[k]+' No suspended work. No manual action.',
            rule='SPECIFICATION Outcomes 1, 2, 3')
# ---------- expressibility
EXP=[]
for cfg in ['report','x1','x1sim']:
    def x(sp,ex,reason,direction=None): EXP.append({'configuration':cfg,'subproblem':sp,'direction':direction,'expressibility':ex,'reason':reason})
    x('P09a','expressible','A: loop is transcribed by its one case (a procedure that calls itself); B: rev and conc are mode-faithful transcriptions of their cases for the direction the query uses (rule 3), all P. The program\'s R tokens (loop\'s unused parameters xk and found) are not forced by the language. The two computations cannot run side by side in ALGOL 60 (one after another, side_by_side false), which is an outcome of the run, not a limit on transcription.','A: loop(x); B: rev forward, conc forward')
    x('P09b','expressible','Each equation can be written in the direction the query uses (rule 8): x = c1 as an assignment, x = c2 then as a test of the fully known relation, y = c3 as an assignment, all P; no holding is forced, since each conjunct has its unknown computable or known when it is reached. The program instead writes a general binder-tester equals with known-flags, unbinding and the conjunction passed as a continuation: 49 R tokens (rule 19, rule 4), a reformulation that keeps the meaning but is not needed. No S.')
    x('P09c','expressible','gen and sum3 are transcribed by their cases in the direction the query uses (rule 3), with the sequence encoding (P, rule 15). No R tokens.','gen forward (s from n), sum3 forward (total from s)')
    x('P09d','expressible','P09d1 (finite, least relation): genu is transcribed by its one case as a function; its non-termination agrees with the relation having no instances. No R tokens.','P09d1, finite reading')
    x('P09d','expressible with reformulation','P09d2 (stream, greatest relation): the transcription builds s eagerly and cannot represent an infinite sequence, so it never yields total = 6. A demand-driven producer (for instance a procedure giving the i-th element, which sum3 calls three times) would keep genu\'s meaning for sum3\'s use: a reformulation, not written in this program. No S needed.','P09d2, stream reading')
    x('P09e','expressible with reformulation','The two relations are held until a place is known, by evaluators and a re-examination loop written for the problem\'s own relations (examine1, examine2, propagate, flags): rule 19, R in the core configuration (170 R tokens). Their place computations and tests are P. No S.')
    x('P10a','expressible','Replacement is native assignment; b := b + e takes b at its value before the stage. The program\'s R tokens (the flag bk) are not needed for the queries posed.')
    x('P10b','expressible with reformulation','A relation that must keep holding is not native: it is held as a flag and re-examined after every stage (examine1, r1, bk, dk), holding code for the problem\'s own relation, R by rule 19 (42 R tokens). Only d is computed from b; the stages never give d, so the other direction is not used. No S.')
    x('P10c','expressible','The snapshot is one assignment at stage 2, the replacements are assignments. The flags bk, dk (R) only print "has no value" and are not needed for the valid outcomes.')
    x('P10d','expressible with reformulation','pick\'s closed world is the stated facts, held as values (P, rule 6); x > c held with an in-force flag and re-tested from the facts after every stage, and withdrawal as clearing that flag (test, picked, r2): holding code for the problem\'s own relations, R by rule 19 (40 R tokens). It keeps the meaning on every input. No S.')
# ---------- S mechanisms
SM=[]
for text in tokens:
    cfgs=[text.split('/')[0]]+(['x1sim'] if text.startswith('x1/') else [])
    progs=[text.split('/')[1]]+(['P09a.BA.'+text.rsplit('.',1)[1]] if 'P09a.AB' in text else [])
    for c in cfgs:
        for p in progs:
            SM.append({'configuration':c,'program':p,'mechanism':None,'listed_at_phase_4':None,'tokens':0,
                       'note':'no supporting mechanism: no token classed S. harnesses/algol-60/S-mechanisms.md lists none for any ALGOL 60 configuration; the program\'s holding code (where any) is written for the problem\'s own relations and is R (rule 19), and its input and output procedures are external mechanisms or the X1 system\'s, counted as call tokens'})
out={'tokens':tokens,'outcomes':O,'mode_differences':[],'expressibility':EXP,'late_definition':[],'s_mechanisms':SM,
     'meta':{'classifier':'1C-A','batch':'1C','problems':['P09','P10'],'commit':'bd43b8d',
       'token_texts_note':'Each distinct text of TEXTS-1C-P09-P10.tsv is classed once under its first path: report/P09a.AB.alg also stands for report/P09a.BA.alg; x1/<file> also stands for x1sim/<file> (identical texts; no S mechanism differs between x1 and x1sim, so no token class differs).',
       'mode_differences_note':'Every cost and storage run of report and x1 for P09 and P10 was compared with its behaviour run (answers verbatim, ended_by, execution states, attempts, observe text): no stage differs. x1sim has behaviour runs only. There are no raw-rerun-m2 records and no INVALID records for P09 or P10.',
       'late_definition_note':'P08 is not in this batch (P09, P10).'}}
json.dump(out,open('algol-60.json','w'),indent=1,ensure_ascii=False)
# totals
tot={}
for t,sp in tokens.items():
    tt={}
    for s in sp: tt[s['class']]=tt.get(s['class'],0)+s['to']-s['from']+1
    tot[t]=tt
    print(t,sum(tt.values()),tt)
g={}
for tt in tot.values():
    for k,v in tt.items(): g[k]=g.get(k,0)+v
print('ALL',sum(g.values()),g,'outcomes',len(O))
