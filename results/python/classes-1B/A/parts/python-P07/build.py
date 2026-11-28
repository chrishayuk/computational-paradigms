import json
S=json.load(open('summary.json'))
tokens=json.load(open('tokens.json'))
UNK={'core':"unknowns are names (str) absent from the bindings dict until computed; no object stands for an unbound unknown",
     'stdlib-concurrency':"unknowns are names (str) absent from the bindings dict until computed; no object stands for an unbound unknown",
     'extended':"unknowns are S.suspend Var objects; an unbound one renders as its name in the bindings"}
SUSP={'core':"held list 'relations waiting for values' (decide() re-examines it at each stage)",
      'stdlib-concurrency':"one daemon thread per held relation, blocked in changed.wait_for, plus its entry in the list 'relations waiting in their threads'",
      'extended':"goals in Queue.held, each suspended on its unbound Vars (S suspension queue)"}
MECH={'core':"local propagation: decide() passes over the held relations until none is decided; each relation is decided by its evaluator as soon as enough places are known",
      'stdlib-concurrency':"local propagation by threads: each relation's thread evaluates it when a binding notifies the condition",
      'extended':"local propagation through the S suspension queue: a goal runs, binds a place, and wakes goals suspended on that Var"}
T={
 'P07a':dict(semantic='complete',representation='explicit',simplification=None,identical_to_posed=None,residual_size=None,
   equiv="not a residual: the explicit answer x = 5, y = 4, z = 3 is the one valid outcome (checked by equiv.py: the only integer triple satisfying the three relations)",
   obs="answer 'x = 5, y = 4, z = 3'; {mech}; solved one relation at a time, in every order. Unknowns: {unk}{t}. Alternatives held: none (0). Suspended at the boundary: 0. No conclusion withdrawn (one stage). No manual action."),
 'P07b':dict(semantic='complete',representation='residual',simplification='reducible',identical_to_posed=True,
   residual_size="2 relations held (x + y = 10, x - y = 4), 4 occurrences of unknowns; input: 2 relations, 4 occurrences. Smaller equivalent: x = 7, y = 3 (no relation left)",
   equiv="equivalent: x + y = 10 and x - y = 4 over the integers has the unique solution x = 7, y = 3 (add and halve: 2x = 14); the held relations are exactly the posed ones, so they denote exactly the valid outcome (equiv.py confirms on [-200,200]^2). SPECIFICATION's own example: complete / residual / reducible",
   obs="no answer; the two relations are held undecided: {held}. No elimination is attempted: each evaluator needs two known places. Unknowns: {unk}. Alternatives: none. Suspended: 2 ({susp}). No conclusion withdrawn; no manual action."),
 'P07c':dict(semantic='complete',representation='residual',simplification='reduced',identical_to_posed=True,
   residual_size="1 relation held (x + y = 10), 2 occurrences of unknowns; input: 1 relation, 2 occurrences",
   equiv="equivalent: the held relation is the posed relation x + y = 10, whose integer solutions are the valid outcomes; no smaller representation exists (SPECIFICATION's example: complete / residual / reduced)",
   obs="no answer; the relation is held: {held}. Unknowns: {unk}. Alternatives: none. Suspended: 1 ({susp}). No conclusion withdrawn; no manual action."),
 'P07d':dict(semantic='complete',representation='explicit',simplification=None,identical_to_posed=None,residual_size=None,
   equiv="not a residual: w = 7 (with the given u = 2, v = 14) is the one valid outcome; 14 % 2 == 0 and 14 // 2 = 7 is exact in the integers",
   obs="answer 'w = 7, u = 2, v = 14'; {mech}; w computed by times() from the known u and v (exact division). Unknowns: {unk}. Alternatives: none. Suspended: 0. No conclusion withdrawn; no manual action."),
 'P07e':dict(semantic='complete',representation='explicit',simplification=None,identical_to_posed=None,residual_size=None,
   equiv="not a residual: the program reports that there is no solution (times(): 15 % 2 != 0 gives False), which is the valid outcome (none); no rational w = 15/2 is reported. Answer completeness (empty outcomes): reported none: yes",
   obs="no cp.answer; the program prints 'no solution: these relations do not hold: {failed}' and holds the failed relation in the registered 'relations found not to hold'; inconsistency detected. The report of none is by print (Python's standard mechanism for answers is what the program prints), not cp.answer, so the record's answers list is empty. Bindings u = 2, v = 15 kept; w unknown ({unk}). Alternatives: none. Suspended: 0. No conclusion withdrawn; no manual action."),
 'P07f':dict(semantic='complete',representation='residual',simplification='inconsistency undetected',identical_to_posed=True,
   residual_size="2 relations held (x + y = 10, x + y = 11), 4 occurrences of unknowns; input: 2 relations, 4 occurrences; they denote the empty set",
   equiv="equivalent: x + y = 10 and x + y = 11 together have no integer solution, and the valid outcomes are none; the held relations are the posed ones. The problem file's own reading: complete / residual / inconsistency undetected, with suspended",
   obs="no answer and no report of inconsistency; both relations held: {held}. Unknowns: {unk}. Alternatives: none. Suspended: 2 ({susp}). No conclusion withdrawn; no manual action."),
 'P07g':dict(semantic='complete',representation='residual',simplification='reducible',identical_to_posed=True,
   residual_size="1 relation held (x * x = 9), 2 occurrences of x; input: 1 relation, 2 occurrences. Smaller equivalent: the explicit x = 3 or x = -3 (no relation left to decide)",
   equiv="equivalent: x * x = 9 over the integers holds exactly for x = 3 and x = -3, the valid outcomes; the held relation is the posed one (equiv.py confirms on [-200,200]). Neither solution was found",
   obs="no answer; neither solution found; the relation is held: {held}, since times() needs two of its three places known and both factors are the one unknown x. Unknowns: {unk}. Alternatives: none. Suspended: 1 ({susp}). No conclusion withdrawn; no manual action."),
}
outcomes=[]
for o in S:
    if o['mode']!='behaviour': continue
    sub=o['inst'].split('.')[0]
    t=T[sub]; cfg=o['cfg']
    held=[l for l in o['raw'].splitlines() if 'suspended[' in l][0].split(' = ',1)[1]
    failed=[l for l in o['raw'].splitlines() if 'held[' in l][0].split(' = ',1)[1]
    tt=", and the fresh unknown t of the decomposition is bound to 9 in the registered bindings" if (sub=='P07a' and cfg!='extended') else (", and the fresh t is a Var not registered in the bindings" if sub=='P07a' else "")
    obs=t['obs'].format(mech=MECH[cfg],unk=UNK[cfg],held=held,susp=SUSP[cfg],failed=failed,t=tt)
    obs+=" Record: answers %s, ended_by %s, steps %d, registered suspended entries %d."%(o['ans'],o['ended'],o['steps'],o['susp'])
    outcomes.append(dict(configuration=cfg,instance=o['inst'],program=o['prog'],record=o['rec'],stage=1,reached=True,
      semantic=t['semantic'],representation=t['representation'],simplification=t['simplification'],
      identical_to_posed=t['identical_to_posed'],residual_size=t['residual_size'],execution_state=o['states'],
      residual_equivalence=t['equiv'],observations=obs,
      rule="SPECIFICATION Outcomes 1-3; problems/07 Observations"+("; SPECIFICATION 'reported' (a residual held in a registered structure the program acts on at a later stage, read by observe())" if t['representation']=='residual' else ""),
      harness_fault=False))
order={'core':0,'extended':1,'stdlib-concurrency':2}
outcomes.sort(key=lambda x:(order[x['configuration']],x['instance']))
expr=[]
for cfg in order:
    for sub in 'abcdefg':
        r=("Python has no unknowns and no relation that waits: the relation(s) of P07%s are transcribed as evaluators that compute any place from the others, or test a known relation (P in every direction, rule 19), but they can be stated only with holding code written for the program (%s), which is R by rule 19 in the program of record. That reformulation keeps the relations' meaning on every input (it never reports a non-integer or a wrong value; what it cannot decide it holds)."%(sub,
           {'core':"the held list, place(), EVALUATOR and decide()",
            'stdlib-concurrency':"a thread per relation, the held/waiting lists, place(), EVALUATOR and hold(); the threads themselves are C",
            'extended':"the Relation goal wrapper around the S suspension queue (the queue is S; the freeze and run calls are C)"}[cfg]))
        if sub in 'bg': r+=" It does not solve the set (no elimination; x * x with one unknown is never decided): that is recorded by simplification, not expressibility."
        if sub=='f': r+=" It does not detect the inconsistency: recorded by simplification."
        expr.append(dict(configuration=cfg,subproblem='P07'+sub,direction=None,expressibility='expressible with reformulation',reason=r))
smech=[]
for sub in 'abcdefg':
    smech.append(dict(configuration='extended',program='P07%s.py'%sub,mechanism='suspension queue (harnesses/python/S/suspend.py: Var, Queue.wait, Queue.bind, Queue.run, Queue.held, deref)',listed_at_phase_4=True,tokens=537,
      note="537 is the mechanism's own size (S-mechanisms.md), counted once for extended. In the program, the import line is S by my classes (11 tokens); the calls around it are C (Queue(), q.wait, q.run) or R (the Relation wrapper, q.bind). No program-supplied S mechanism: the Relation wrapper is R (rule 19, written for these relations), though it is the same text as extended's P02 programs (see notes)."))
for cfg in ('core','stdlib-concurrency'):
    for sub in 'abcdefg':
        smech.append(dict(configuration=cfg,program='P07%s.py'%sub,mechanism=None,listed_at_phase_4=None,tokens=0,
          note=("none listed (core admits no S). decide()/place()/EVALUATOR/held is R by rule 19, though textually reused across core P01, P02, P06, P07 (see notes)" if cfg=='core' else
                "none (threading is an external mechanism, its calls C, not S). hold()/place()/EVALUATOR is R by rule 19")))
out=dict(tokens=tokens,outcomes=outcomes,mode_differences=[],expressibility=expr,late_definition=[],s_mechanisms=smech)
json.dump(out,open('python.json','w'),indent=1)
# checks
from show import load
for k,sp in tokens.items():
    n=len(load(k)); cov=[0]*n
    for s in sp:
        assert s['class'] in 'PCRSH'
        for i in range(s['from'],s['to']+1): cov[i]+=1
    assert all(c==1 for c in cov),k
print('ok',len(outcomes),len(expr),len(smech))
tot={}
for k,sp in tokens.items():
    c=k.split('/')[0]
    for s in sp: tot.setdefault(c,{}).setdefault(s['class'],0); tot[c][s['class']]+=s['to']-s['from']+1
print(tot); print({c:sum(v.values()) for c,v in tot.items()})
