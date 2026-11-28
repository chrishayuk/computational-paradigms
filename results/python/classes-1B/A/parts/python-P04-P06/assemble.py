import json,collections
OUT='results/python/classes-1B/A/parts/python-P04-P06'
tokens=json.load(open(OUT+'/tokens.json')); outcomes=json.load(open(OUT+'/outcomes.json'))
# shared texts: core path stands for stdlib-concurrency too
SHARED={'P04a','P04b','P04c','P04d','P04e','P04f','P06d','P06e1','P06e2','P06e3'}
EXP=[]
def ex(conf,sp,e,reason): EXP.append(dict(configuration=conf,subproblem=sp,direction=None,expressibility=e,reason=reason))
for conf in ['core','stdlib-concurrency','extended']:
    tag={'core':'core','stdlib-concurrency':'stdlib-concurrency (same text as core)','extended':'extended'}[conf]
    for sp in ['P04a','P04b']:
        ex(conf,sp,'expressible','loop and = transcribed by their cases, the disjunction in presentation order (P only; no R tokens). '+('Generators in Python core.' if conf!='extended' else 'Relations as clause generators solved by the S search with the program\'s own unify/resolution (S).')+' That the endless alternative errs or runs to the budget is an outcome, not a limit of expressibility.')
    for sp,defn in [('P04c','alist-left'),('P04d','alist-left'),('P04e','alist-right'),('P04f','alist-right')]:
        ex(conf,sp,'expressible','%s transcribed by its cases in the order given, conjuncts in order (P). '%defn+('The only R tokens are cons(), which encodes the constant tuple as cons cells for the unifier (and is dead code where unused); it changes no definition.' if conf=='extended' else 'The "s is None" tests are case/direction dispatch of a mode-faithful transcription serving both directions the program uses (rule 3).'))
    for sp in ['P05a','P05b','P05c']:
        ex(conf,sp,'expressible with reformulation','pick, >, != and = are transcribed (P), but holding x\'s values across stages and holding a comparison until x has values is code the problem does not give (rule 19, R: values/x_has_values/held, arrive, source\'s wait verdict, the dispatch by name)'+(' around the S propagator, which takes over the values once x has a finite domain' if conf=='extended' else '')+(' with one thread per relation (C)' if conf=='stdlib-concurrency' else '')+'. The reformulation keeps the relations\' meaning on every input the problem uses; no finite domain is imposed.')
    for sp in ['P06a','P06b','P06c']:
        ex(conf,sp,'expressible with reformulation','= and not(=) are transcribed as evaluators (computing and testing P), but the negation is held until x has a value by holding code the problem does not give (rule 19, R: known-place tests, wait verdict, held/failed records, '+{'core':'decide()','stdlib-concurrency':'hold() in a thread per relation, with C synchronisation','extended':'the Relation goal class around the S suspension queue (freeze call C)'}[conf]+'). Meaning kept on every input; no domain imposed.')
    ex(conf,'P06d','expressible','mem and setdiff transcribed by their cases in order; setdiff in the one direction the query uses (forwards), case 3\'s guard "not mem(h, s2)" as stated (P). '+('Negation is the program\'s own negation-as-failure mechanism (S), applied to a ground goal; cons() is R input encoding only.' if conf=='extended' else 'mem as a test, e and s known, as the query reaches it (rule 3).'))
    for sp in ['P06e1','P06e2','P06e3']:
        ex(conf,sp,'expressible','the closed world as facts, nonmajor by its one case with conjuncts in order, "not takes(p, k)" '+('as the S-level negation-as-failure goal on known p, k' if conf=='extended' else 'as Python\'s not on a test with p and k known')+' (P).')
# S mechanisms
SM=[]
def cnt(text,pred):
    return sum(s['to']-s['from']+1 for s in tokens[text] if s['class']=='S' and pred(s['construct']))
for text in tokens:
    conf,f=text.split('/'); prog=f
    if conf!='extended': continue
    def add(name,listed,pred,extra=''):
        SM.append(dict(configuration=conf,program=prog,mechanism=name+extra,listed_at_phase_4=listed,tokens=cnt(text,pred)))
    cons=[s['construct'] for s in tokens[text] if s['class']=='S']
    if any('S backtracking search' in c for c in cons) or any('trail' in c for c in cons):
        add('backtracking search (S/search.py: search, undo, the trail)',True,lambda c:'S backtracking search' in c or c.startswith('trail'),' -- 176 tokens in S-mechanisms.md, counted once for extended; tokens here are the program\'s import and trail')
    if any('suspension queue' in c for c in cons):
        add('suspension queue (S/suspend.py: Var, deref, Queue%s)'%('.wait, bind, run, held' if f.startswith('P06') and f[3] in 'abc' else '.bind with a trail'),True,lambda c:'suspension queue' in c,' -- 537 tokens in S-mechanisms.md, counted once; tokens here are the program\'s import'+(' and q = Queue()' if f[3] in 'abc' and f.startswith('P06') else ''))
    if any('propagator' in c for c in cons):
        add('constraint propagator (S/propagate.py: Store, var, relation, dom)',True,lambda c:'propagator' in c,' -- 1,260 tokens in S-mechanisms.md, counted once; tokens here are the import and store = Store()')
    if any('"unify"' in c for c in cons):
        add('unify (program-supplied: unification of terms of values, cons cells and Vars, no occurs check; with its binder Queue)',False,lambda c:'"unify"' in c)
    if any('"resolution"' in c for c in cons):
        add('resolution (program-supplied: children and done, a goal list reduced by its first goal\'s cases, depth first)',False,lambda c:'"resolution"' in c)
    if any('"negation"' in c for c in cons):
        add('negation (program-supplied: not R by a search of its own, negation as failure)',False,lambda c:'"negation"' in c)
# check: all S tokens accounted
for text in tokens:
    tot=sum(s['to']-s['from']+1 for s in tokens[text] if s['class']=='S')
    acc=sum(m['tokens'] for m in SM if m['configuration']+'/'+m['program']==text)
    assert tot==acc,(text,tot,acc)
res=dict(tokens=tokens,outcomes=outcomes,mode_differences=[],expressibility=EXP,late_definition=[],s_mechanisms=SM)
json.dump(res,open(OUT+'/python.json','w'),indent=1,ensure_ascii=False)
# totals
T=collections.Counter(); per={}
for text,spans in tokens.items():
    c=collections.Counter()
    for s in spans: c[s['class']]+=s['to']-s['from']+1
    per[text]=c; T.update(c)
print('texts',len(tokens),'totals',dict(T),'sum',sum(T.values()))
print('outcomes',len(outcomes),'expr',len(EXP),'sm',len(SM))
for m in SM: print(m['program'],m['mechanism'][:40],m['tokens'])
