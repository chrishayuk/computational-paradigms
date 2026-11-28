# Classes the tokens of the P12 texts by construct, from the frozen token files.
import csv, json, sys
R='/Users/christopherhay/cp-roles/classifier-1C-A/results/swi-prolog/tokens/'
TEXTS=['constraints/P12a.pl','constraints/P12b.pl','constraints/P12c.pl','constraints/P12d.pl',
       'tabling/P12a.pl','tabling/P12b.pl','tabling/P12c.pl','tabling/P12d.pl']
def load(t):
    rows=list(csv.DictReader(open(R+t+'.tokens.tsv'),delimiter='\t'))
    return [(int(r['index']),int(r['line']),r['token']) for r in rows]
def spans_for(t):
    toks=load(t); lines={}
    for i,l,x in toks: lines.setdefault(l,[]).append((i,x))
    out=[]
    def sp(a,b,c,con,rule): out.append({"from":a,"to":b,"class":c,"construct":con,"rule":rule})
    for l in sorted(lines):
        ts=lines[l]; first=ts[0][1]; a=ts[0][0]; b=ts[-1][0]; text=' '.join(x for _,x in ts)
        if first=='accept_fact':
            sp(a,b,'P','accept fact (CONSTANTS block, stage 1): '+text,
               'METRICS class P, rule 6: a set of facts the problem states (accept, closed world); the first argument keys the facts by the instance size n, which the problem itself makes accept depend on ("12 below read as n"); rule 1: removing the key changes the solutions')
        elif first==':-' and ts[1][1]=='table':
            sp(a,b,'C','tabling declaration :- table choice/2.','METRICS class C (tabling declarations); rule 1: changes order and cost only, not the solution set')
        elif first=='choice':
            if ts[5][1]==']' or text.startswith('choice ( _ , [ ]'):
                sp(a,b,'P','choice case 1: choice(n, <>), as a fact','METRICS class P: transcription of the problem\'s case 1')
            else:
                sp(a,b,'P','choice case 2: choice(N,[E|T]) :- N > 0, (E = l ; E = r), N1 is N - 1, choice(N1, T)',
                   'METRICS class P: transcription of case 2 in the order written; disjunction in order written (rule 6), n - 1 by is/2 in the direction used (rule 8), n > 0 the case\'s own condition (rule 2)')
        elif first=='unknowns':
            sp(a,b,'H','unknowns/2 fact','harness README 12: the whole of each unknowns/2 fact is H')
        elif first=='stage':
            sp(a,b,'H','stage/3 head with :-','harness README 12: stage/3 head, with its :-, is H')
        elif first=='h_param':
            # body: h_param ( n , N ) , choice ( N , S ) , h_candidate , member ( ... ) .
            idx=[i for i,_ in ts]; xs=[x for _,x in ts]
            j=xs.index(')')  # end of h_param call
            sp(idx[0],idx[j],'H','h_param(n, N): the instance size from the harness','harness README 12: calls of h_param/2 are H')
            k=xs.index('h_candidate')
            sp(idx[j+1],idx[k-2],'P','conjunct choice(N, S), first in the order written (with the preceding comma)','METRICS class P (the query, first conjunct); rule 20 for the comma')
            sp(idx[k-1],idx[k],'H','h_candidate: candidate count','harness README 12: calls of h_candidate/0 are H; rule 20 for the comma')
            sp(idx[k+1],idx[-2],'P','conjunct accept(S) as member(accept_fact(N, S), Cs), second in the order written (with the preceding comma)',
               'METRICS class P (the query, second conjunct); rule 9: member/2 of library(lists) in place of a lookup among accept\'s facts, equivalent in the direction used (S ground); listed; rule 20 for the comma')
            sp(idx[-1],idx[-1],'H','the full stop closing the stage/3 clause','harness README 12 with METRICS rule 10: the closing token of the H-headed stage clause takes the clause\'s class')
        elif first=='query':
            sp(a,b,'H','query(_, _). fact','harness README 12: head of query/2, here with no body')
        else:
            raise SystemExit('unclassed line %s %s %s'%(t,l,text))
    # coverage check
    n=len(toks); cov=[0]*n
    for s in out:
        for i in range(s['from'],s['to']+1): cov[i]+=1
    assert all(c==1 for c in cov), (t,[i for i,c in enumerate(cov) if c!=1])
    assert [i for i,_,_ in toks]==list(range(n))
    return out,n
if __name__=='__main__':
    res={}; tot={}
    for t in TEXTS:
        s,n=spans_for(t); res[t]=s
        c={}
        for x in s: c[x['class']]=c.get(x['class'],0)+x['to']-x['from']+1
        tot[t]=(n,c); print(t,n,c)
    json.dump(res,open(sys.argv[1],'w'),indent=1)
