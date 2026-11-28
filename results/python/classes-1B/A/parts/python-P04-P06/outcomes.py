"""Builds classifier A's outcome entries for python P04-P06 from the behaviour
records and the judgements below (one per instance and stage, with the
configuration-specific facts read from each record)."""
import json,glob,os,re
REPO='.'
OUT='results/python/classes-1B/A/parts/python-P04-P06'
RULE='SPECIFICATION.md Outcomes 1-3; problem file valid outcomes'

def facts(conf,inst,st,c,at):
    a=[x['verbatim'] for q in c['queries'] for x in q['answers']]
    ended=[q['ended_by'] for q in c['queries']]
    alt=c['alternatives']; sus=c['suspended']
    err=(c['execution_state'].get('error_verbatim') or '').strip().splitlines()
    return dict(answers=a,ended=ended,states=c['execution_state']['states'],err=err[-1] if err else None,
                alts=alt['at_boundary'],alt_types=alt['by_type'],pd=alt.get('problem_defined'),
                susp=sus['at_boundary'],susp_items=sus['items'],obs=re.sub(r' at 0x[0-9a-f]+','',at['observe']['raw']),
                printed=at['print'],steps=c['steps']['stage'],manual=at['manual_actions'],notes=at['notes'])

def unk(conf,inst):
    if conf=='extended':
        if inst[:3]=='P05': return 'x is a variable name of the propagator store ("x"), with no domain until a relation gives it one'
        return 'unknowns are Vars of the S suspension queue (S/suspend.py), unbound until bound'
    if inst in ('P06a','P06b','P06c'): return 'x is an object of the program\'s class Unknown, a place of the held relations; its value, once known, is in the dict known'
    if inst[:3]=='P05': return 'x is represented by the list of its values still held (values) and the flag x_has_values; no value list while no relation has given values'
    return 'an unknown is None as a generator argument; the generator yields its values'

def judge(conf,inst,k,f):
    """returns dict of classification fields"""
    ext=conf=='extended'; std=conf=='stdlib-concurrency'
    d=dict(reached=True,semantic=None,representation=None,simplification=None,identical_to_posed=None,
           residual_size=None,execution_state=f['states'],residual_equivalence=None,rule=RULE)
    a=f['answers']
    if inst in ('P04a','P04c','P04d'):
        d.update(semantic='none reported',representation=None)
        if 'error' in f['states']:
            obs='%s before any answer (%s); the left alternative/left-recursive case recursed until the recursion limit. '%('error',f['err'])
        else:
            obs='budget (10^6 instructions) ran out before any answer; the S search is iterative, so the endless branch never errs: %d choice points held on the search stack at the budget, kept for backtracking. '%f['alts']
        if inst=='P04a': obs+='x = 1 (the second alternative) is never reached: the endless alternative hides the finite one in depth-first order. '
        if inst=='P04c': obs+='alist-left calls alist(m) with m unknown before testing s = <A> ++ m: no answer is found for the ground query. '
        if inst=='P04d': obs+='alist-left enumerates nothing: the first case recurses before any solution, so no solution would be reached given more steps (unfair, left recursion). '
        d['observations']=obs
        d['rule']=RULE+'; SPEC Outcomes 1 (none reported), 3 (error verbatim / budget presumed nontermination)'
    elif inst=='P04b':
        d.update(semantic='complete',representation='explicit')
        d['observations']='x = 1 reported first (%s); then the second alternative loop(x) %s. '%(a, 'recursed until RecursionError (%s): the computation did not finish'%f['err'] if 'error' in f['states'] else 'ran to the budget: %d choice points on the search stack'%f['alts'])
        d['rule']=RULE+'; answers reported before the error/budget are classed on the semantic axis'
    elif inst=='P04e':
        d.update(semantic='complete',representation='explicit')
        d['observations']='reports "true" once and finishes; nothing pending at the end (%s). '%('search stack empty' if ext else 'the registered generator is exhausted')
    elif inst=='P04f':
        d.update(semantic='partial',representation='explicit')
        n=len(a)
        d['observations']=('%d answers collected (cap 20), in order of length: %s ... %s; more printed after the cap (%s); budget ran out. '
            'No finite representation of the infinite set was given (answer completeness: no). Every solution would be reached given enough steps '
            '(alist-right enumerates <>, <A>, <A,A>, ... in order). %s pending at the budget. ')%(n,a[0],a[-1],'%s more printed, not collected'%re.search(r'printed (\d+) more',' '.join(f['notes'])).group(1),
            ('%d choice points on the search stack'%f['alts']) if ext else '1 suspended generator (the query)')
        d['rule']=RULE+'; SPEC Outcomes 1 (partial: nonempty proper subset); METRICS answer completeness (infinite)'
    elif inst=='P05a':
        valid={1:[1,2,3],2:[2,3],3:[3]}[k]
        d.update(semantic='complete',representation='explicit')
        w={1:'',2:'x = 1, reported at stage 1, is withdrawn: it is dropped from the values held and not reported again; no explicit withdrawal is shown. ',3:'x = 2, reported at stages 1 and 2, is withdrawn the same way (not reported again, no explicit withdrawal). '}[k]
        d['observations']='answers %s; values of x held all at once (problem-defined alternatives: %s), not kept for backtracking; nothing suspended. %s'%(a,f['pd'],w)
    elif inst=='P05b':
        if k==1:
            d.update(semantic='complete',representation='residual',simplification='reduced',identical_to_posed=True,
                residual_size='1 relation (x > 1), 1 occurrence of x; input: 1 relation, 1 occurrence',
                residual_equivalence='equivalent: the held comparison (\'>\', 1) on x denotes every integer x > 1, which is the valid outcome (comparisons other than = hold only of integers); checked by hand and on a sample by residuals.py')
            d['observations']=('the comparison is held, not enumerated and not an error: %s; no values of x yet (problem-defined alternatives 0); nothing reported as an answer. '
                '%s. ')%(f['obs'].strip().split('\n')[0], 'held by the program\'s own list (rule 19, R) until pick gives x a finite domain; no finite domain is imposed (AMENDMENTS 3.4 respected)' if ext else ('its thread waits on the condition `changed` (1 waiting thread)' if std else 'held in the program\'s list `held` (1 item)'))
            d['rule']=RULE+'; SPEC Outcomes 2 (residual held and acted on at stage 2, read by observe)'
        else:
            d.update(semantic='complete',representation='explicit')
            d['observations']='pick gives x its values and the held comparison is taken up: answers %s; values held all at once (%s); nothing suspended. Same outcome as P05a stage 2. '%(a,f['pd'])
    elif inst=='P05c':
        if k==1:
            d.update(semantic='complete',representation='explicit')
            d['observations']='answers %s; values held all at once (%s). '%(a,f['pd'])
        else:
            d.update(semantic='complete',representation='explicit')
            d['observations']=('no answers; printed %r: the empty outcome is reported as empty. %sStage %d could be posed. %s')%(f['printed'].strip(),
                'The store holds x with an empty domain and the posted constraints. ' if ext else 'values held: []. ',k,
                'x = 1, 2, 3, reported at stage 1, are withdrawn by the report of no solution. ' if k==2 else '')
            d['rule']=RULE+'; empty valid outcome: reported that there are none (answer completeness: yes)'
    elif inst in ('P06a','P06c') and k==1:
        d.update(semantic='complete',representation='residual',simplification='reduced',identical_to_posed=True,
            residual_size='1 relation, not (x = 1), 1 occurrence of x; input: 1 relation, 1 occurrence',
            residual_equivalence='equivalent: the held relation not (x = 1) denotes every value other than 1, the valid outcome; no domain is imposed (x ranges over all values); checked by hand and on a sample by residuals.py')
        d['observations']=('the negation is held as a condition until x has a value (delayed, not decided at once, not an error): %s. %s No answer reported. ')%(f['obs'].strip().split('\n')[1] if '\n' in f['obs'].strip() else f['obs'].strip(),
             'Held as a goal of the S queue, waiting on x.' if ext else ('Held by a thread waiting on the condition `changed`.' if std else 'Held in the list `held`.'))
        d['rule']=RULE+'; SPEC Outcomes 2 (residual held and acted on at stage 2, read by observe)'
    elif inst=='P06a' and k==2:
        d.update(semantic='complete',representation='explicit')
        d['observations']='x = 2 binds x and the held negation is then decided (true) at stage 2; answer %s; nothing held. Same outcome as P06b stage 2. '%a
    elif inst=='P06b':
        d.update(semantic='complete',representation='explicit')
        d['observations']='answer %s; %s; nothing held. '%(a,'the value comes first; the negation, arriving with x known, is decided at once' if k==2 else 'x = 2 binds x')
    elif inst=='P06c' and k==2:
        d.update(semantic='complete',representation='explicit')
        d['observations']=('x = 1 binds x and wakes the held negation, which is found not to hold; printed %r; no answer. observe also reads the binding x = 1 beside the '
            'relation recorded as failed; taken together they denote no solution, which the program reports. ')%f['printed'].strip()
        d['rule']=RULE+'; empty valid outcome reported as none'
    elif inst=='P06d':
        d.update(semantic='complete',representation='explicit')
        d['observations']='answer %s; finished. %s'%(a,'The search exhausts and undoes its bindings: observe shows d unbound after the stage, the answer having been reported while it was bound. ' if ext else '')
    elif inst=='P06e1':
        d.update(semantic='complete',representation='explicit')
        d['observations']='reports %s once (brown does not take c301); finished. '%a
    elif inst=='P06e2':
        d.update(semantic='complete',representation='explicit')
        d['observations']='no answer; printed %r: false reported; finished. '%f['printed'].strip()
        d['rule']=RULE+'; empty valid outcome reported as none'
    elif inst=='P06e3':
        d.update(semantic='complete',representation='explicit')
        d['observations']='answer %s; p and k are both known before not takes(p, k) is decided (student generates p, maths generates k, then the negation is tested on known values). '%a
    else: raise ValueError((inst,k))
    d['observations']='Unknowns: '+unk(conf,inst)+'. '+d['observations']+'Suspended at boundary: %d %s; alternatives (cp.pending) at boundary: %d. Steps (stage): %d. Manual actions: none. '%(f['susp'],f['susp_items'] or '',f['alts'],f['steps'])
    return d

outcomes=[]
for conf in ['core','extended','stdlib-concurrency']:
    for b in sorted(glob.glob(f'{REPO}/results/python/{conf}/P0[456]/raw/*.behaviour.*.json')):
        r=json.load(open(b)); inst=r['run']['instance']; prog=os.path.basename(r['run']['program']['path'])
        for st in r['stages']:
            at=st['attempts'][-1]; c=at['computations'][0]
            f=facts(conf,inst,st['stage'],c,at)
            d=judge(conf,inst,st['stage'],f)
            e=dict(configuration=conf,instance=inst,program=prog,record=os.path.relpath(b,REPO),stage=st['stage'])
            e.update(d)
            if r.get('harness_faults') or b.endswith('INVALID.json'): e['harness_fault']=True
            outcomes.append(e)
json.dump(outcomes,open(OUT+'/outcomes.json','w'),indent=1,ensure_ascii=False)
print(len(outcomes))
import collections
print(collections.Counter((o['semantic'],o['representation'],tuple(o['execution_state'])) for o in outcomes))
