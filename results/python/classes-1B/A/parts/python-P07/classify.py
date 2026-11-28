import json
from show import load
CONFIGS=['core','extended','stdlib-concurrency']
USED={'a':{'plus','equal'},'b':{'plus','minus'},'c':{'plus'},'d':{'times','equal'},
      'e':{'times','equal'},'f':{'plus'},'g':{'times'}}
EVALS={'equal','plus','minus','times'}
KNOWN_TESTS={'if a is not None and b is not None :','if a is not None :','if b is not None :',
 'if c is None :','if a is not None and c is not None :','if b is not None and c is not None :'}

def L(c,con,rule): return (c,con,rule)

def evaluator_line(text,func,used):
    if not used:
        return L('R',f'{func}: evaluator of a relation this sub-problem does not use','rule 1 (removing it changes no reported value); rule 3 (a case the sub-problem does not give)')
    if text.startswith('def '):
        return L('P',f'{func}: header of the relation\'s evaluator','rule 19 (evaluator: the relation itself)')
    if text.replace(" <NEWLINE>","") in KNOWN_TESTS:
        return L('R',f'{func}: test of which places are known','rule 19 (the tests of which places are known are R)')
    if text=='return None <NEWLINE>':
        return L('R',f'{func}: verdict that the relation must wait','rule 19 (the verdict to wait is R)')
    return L('P',f'{func}: computes a place or tests the known relation','rule 19 (computing any place, or testing a fully known relation, is P in every direction)')

def line_label(text,func,cfg,sub):
    """single label for a line (before splitting)"""
    t=text
    if func in EVALS:
        return evaluator_line(t,func,func in USED[sub])
    # constants block
    import re
    if re.match(r'^[A-Z_]+ = -?\d+ <NEWLINE>$',t):
        return L('P','constants block entry: the stage\'s information','harness README s.7 (block entries are the stages\' information, classed by the rules); rule 1')
    if t.startswith('UNKNOWNS ='):
        return L('H','names of the unknowns, used only to render the answer','rule 13 (output adapter)')
    if t.startswith('cp .'):
        return L('H','harness registration/answer call','harness README s.7 item 4; rule 13')
    if t.startswith('while ( s := cp . stage'):
        return L('H','stage loop header','harness README s.7 item 1')
    if t.startswith('if s . k =='):
        return L('H','stage dispatch test','harness README s.7 item 2')
    if t.startswith('if not s . replay'):
        return L('H','test on s.replay, only suppresses the answer during replay','harness README s.7 item 3')
    if func=='report':
        return L('H','report(): renders the computed bindings or the detected failure','rule 13 (output adapter)')
    if func=='__stage_report__':
        return L('H','renders the computed bindings or the detected failure','rule 13 (output adapter)')
    if func=='Relation.__repr__':
        return L('H','Relation.__repr__: renders a goal for observe()/print','rule 13 (output adapter)')
    # holding (rule 19) core
    if t in ('known = { } <NEWLINE>',):
        return L('R','the store of the unknowns\' values, read by the holding code','rule 19 (code that holds relations, written for the problem\'s relations: R in core)')
    if t in ('held = [ ] <NEWLINE>','waiting = [ ] <NEWLINE>'):
        return L('R','the list of relations held undecided','rule 19 (holding, what it records about what waits)')
    if t=='failed = [ ] <NEWLINE>':
        return L('R','the list of relations found not to hold (holding code\'s verdicts)','rule 19 (holding)')
    if t.startswith('EVALUATOR ='):
        return L('R','dispatch table from relation name to evaluator, used by the holding code','rule 19 (holding)')
    if func=='place':
        return L('R','place(): reads a place\'s value or None (which places are known)','rule 19 (the tests of which places are known are R)')
    if func=='decide':
        return L('R','decide(): fixpoint pass over the held relations, written for this program','rule 19 (code that holds relations until their values arrive and decides them, written for the problem\'s relations: R, core)')
    if t=='decide ( ) <NEWLINE>':
        return L('R','call of the holding code\'s fixpoint pass','rule 19')
    # stage info
    if t.startswith('relations = {') or t=='} <NEWLINE>' or t.startswith('"1" :') or t.startswith('"2" :') or t.startswith('"3" :'):
        return L('P','the stage\'s relations, as written, by position','rule 1; SPECIFICATION Conventions (decomposition is a transcription)')
    if t.startswith('for position in s . params'):
        return L('P','posts the relations in the instance\'s presentation order','SPECIFICATION "How a problem is stated" 3 (presentation order is part of the problem); s.params read is H')
    if t.startswith('for goal in relations') or t.startswith('for rel in relations'):
        return L('P','posts the conjuncts of one position in the order written','presentation order (part of the problem)')
    if t.startswith('held . extend') or t.startswith('held . append'):
        return L('R','puts a stage relation into the held list','rule 19 (holding); the relation tuple inside is P (rule 10)')
    # extended
    if t.startswith('from S .'):
        return L('S','import of the listed S mechanism (suspension queue)','rule 12; S-mechanisms.md')
    if t=='q = Queue ( ) <NEWLINE>':
        return L('C','creates the suspension queue (scheduler of goals)','METRICS C (coroutine/freeze, explicit scheduling); S-mechanisms.md "the code it writes around them"')
    if re.match(r'^[a-z] = Var \( "[a-z]" \) <NEWLINE>$',t):
        return L('P','declares a problem unknown as a logic variable','rule 1 (the problem\'s unknowns); a fresh decomposition unknown is a transcription (SPECIFICATION)')
    if t.startswith('unknowns = {'):
        return L('H','names the unknowns for cp.bindings and the answer','harness README s.7 item 4 (argument only names objects); rule 13')
    if func and func.startswith('Relation'):
        if t.startswith('q . wait'):
            return L('C','Relation.__call__: freeze call, suspends the goal on its unbound Vars','METRICS C (freeze calls); S-mechanisms.md (a freeze call is C)')
        return L('R',f'{func}: goal wrapper that holds a relation on the queue and decides it by its evaluator','rule 19 (holding code: dispatch, wait verdict, binding computed places, failures)')
    if t.startswith('q . wait'):
        return L('C','posts a relation as a goal of the suspension queue','METRICS C (freeze/scheduling call); the Relation inside is P (rule 10)')
    if t=='q . run ( ) <NEWLINE>':
        return L('C','runs the queue\'s ready goals','METRICS C (explicit scheduling)')
    # stdlib
    if t=='import threading <NEWLINE>':
        return L('C','import of threading for the relation threads','METRICS C (thread calls); external mechanism threading')
    if t.startswith('changed = threading'):
        return L('C','the condition variable that synchronises relation threads','METRICS C (thread/synchronisation)')
    if t.startswith('count = {'):
        return L('C','busy/news counters for synchronising threads and settling','METRICS C (scheduling bookkeeping)')
    if func in ('told','pose','settle') or t in ('settle ( ) <NEWLINE>',):
        if func=='told' and t=='waiting . clear ( ) <NEWLINE>':
            return L('R','told(): clears the record of waiting relations','rule 19 (what it records about what waits)')
        return L('C',f'{func or "settle call"}: thread creation, wake-up and settling','METRICS C (thread calls, explicit scheduling)')
    if t.startswith('pose ('):
        return L('C','gives a stage relation its own thread','METRICS C (thread calls); the relation tuple inside is P (rule 10)')
    if func=='hold':
        if t.startswith('with changed') or t.startswith('count [') or t.startswith('changed .') or t.startswith('seen =') or t in ('new = False <NEWLINE>','new = True <NEWLINE>','if new : <NEWLINE>','told ( ) <NEWLINE>'):
            return L('C','hold(): lock, wait, notify and busy-count synchronisation','METRICS C (thread synchronisation)')
        return L('R','hold(): holds one relation, decides it by its evaluator when it can, records waiting and failure, stores computed values','rule 19 (holding code)')
    raise Exception('unclassified: %r in %s %s'%(t,func,cfg))

def tokens_for(cfg,sub):
    path=f'{cfg}/P07{sub}.py'
    rows=load(path)
    by={}
    for i,l,t in rows: by.setdefault(l,[]).append((i,t))
    labels={}
    stack=[]
    depth=0
    func=None; method=None
    cls=None
    last_opener=None
    for l in sorted(by):
        toks=by[l]
        lay=[(i,t) for i,t in toks if t in('<INDENT>','<DEDENT>')]
        code=[(i,t) for i,t in toks if t not in('<INDENT>','<DEDENT>')]
        # layout first (they precede code on a line)
        for i,t in lay:
            if t=='<INDENT>':
                labels[i]=last_opener; stack.append(last_opener); depth+=1
            else:
                labels[i]=stack.pop(); depth-=1
        if not code: continue
        text=' '.join(t for _,t in code)
        # context
        if depth==0:
            method=None
            if text.startswith('def '): func=code[1][1]; cls=None
            elif text.startswith('class '): func='Relation'; cls='Relation'
            else: func=None; cls=None
        elif cls and depth==1 and text.startswith('def '):
            func='Relation.'+code[1][1]
        f=func
        if cfg=='extended' and func is None and depth>=2 and text not in ('if not s . replay : <NEWLINE>',) and not text.startswith('if s . k') :
            # report part of the stage loop (after if not s.replay)
            pass
        lab=line_label_ctx(text,f,cfg,sub,depth,in_report=state.get('in_report',False))
        # per token split
        toklabs=split(code,lab,text)
        for (i,t),tl in zip(code,toklabs): labels[i]=tl
        if code[-1][1]==':' or text.endswith(': <NEWLINE>'):
            last_opener=toklabs[0]
        if text.startswith('if not s . replay'):
            state['in_report']=True
        if text.startswith('while ( s := cp . stage'):
            state['in_report']=False
    n=len(rows)
    assert len(labels)==n and all(labels[i] for i in range(n)), path
    return rows,labels

state={}
def line_label_ctx(text,func,cfg,sub,depth,in_report):
    if func is None and in_report and depth>=2:
        return line_label(text,'__stage_report__',cfg,sub) if text not in ('if not s . replay : <NEWLINE>',) else line_label(text,None,cfg,sub)
    return line_label(text,func,cfg,sub)

import re
def split(code,lab,text):
    toks=[t for _,t in code]
    out=[lab]*len(toks)
    Hc=L('H','read of a stage constant or parameter (s.constants[...], s.params[...])','harness README s.7 item 3')
    # mark s . constants [ "X" ] and s . params [ "order" ]
    for j in range(len(toks)-4):
        if toks[j]=='s' and toks[j+1]=='.' and toks[j+2] in('constants','params') and toks[j+3]=='[':
            for k in range(j,j+6): out[k]=Hc
    # wrappers
    for pre,n in ((('held','.','append','('),4),(('q','.','wait','(','Relation'),4),(('pose','(','('),2)):
        if tuple(toks[:len(pre)])==pre:
            inner=L('P','a stage relation, as written','rule 1; rule 10 (nested in the posting call)')
            # inner = tokens n .. len-3 (exclude final ')' and NEWLINE)
            for k in range(n,len(toks)-2):
                if out[k] is lab: out[k]=inner
    return out

def spans(rows,labels):
    out=[]
    for i,_,_ in rows:
        c,con,rule=labels[i]
        if out and out[-1]['class']==c and out[-1]['construct']==con and out[-1]['to']==i-1:
            out[-1]['to']=i
        else:
            out.append({'from':i,'to':i,'class':c,'construct':con,'rule':rule})
    return out

if __name__=='__main__':
    import sys
    allsp={}
    for cfg in CONFIGS:
        for sub in 'abcdefg':
            state.clear()
            rows,labels=tokens_for(cfg,sub)
            sp=spans(rows,labels)
            allsp[f'{cfg}/P07{sub}.py']=sp
            tot={}
            for s in sp: tot[s['class']]=tot.get(s['class'],0)+s['to']-s['from']+1
            print(cfg,sub,len(rows),tot)
    json.dump(allsp,open('tokens.json','w'),indent=0)
