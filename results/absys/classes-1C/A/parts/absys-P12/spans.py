# Builds the token spans for the 12 P12 texts from the frozen token files, and checks coverage.
import csv, json, sys
TOK='./results/absys/tokens/absys/'
FILES=[f'P12{s}.n{n}.ab1' for s in 'abcd' for n in (12,16,8)]
def load(f):
    rows=list(csv.reader(open(TOK+f+'.tokens.tsv'),delimiter='\t'))[1:]
    return [r[2] for r in rows]
def find(t,val,start=0):
    return t.index(val,start)
def spans_for(f):
    t=load(f); S=[]
    def add(a,b,c,con,rule):
        S.append({"from":a,"to":b,"class":c,"construct":con,"rule":rule})
    g=find(t,"gtz'")
    # constants block: one fact per line, NAME = VALUE
    i=0; k=1
    while i<g:
        j=i+1
        while j<g and not (t[j].startswith('acc') and t[j+1]=='='): j+=1
        add(i,j-1,"P",f"constants block: {t[i]} = <sequence>, accept's fact {k} as the problem's closed-world facts give it (the table the harness substitutes into accept)","rule 6 (a set of facts the problem states is P); SPECIFICATION 'the information of each stage'")
        i=j; k+=1
    # gtz definition
    ge=find(t,"end",g)
    add(g,ge,"R","gtz'=lambda q begin {q = 1 or ... or q = 16} end: a definition the problem does not give, standing for the primitive comparison n > 0 by an enumeration of the values 1..16","METRICS class R (a definition the problem file does not give); systems/absys/README.md Notation (n > 0 replaced by an enumeration of the finitely many values used); not rule 6's C, since removing it changes the solution set (rule 1)")
    c=find(t,"choice'")
    ob=find(t,"{",c)
    add(c,ob,"P","choice'=lambda m, w begin { : the head of choice's definition (two parameters, n and s)","rule 10 (introducing tokens take the class of the definition); class P (a definition as the problem gives it)")
    # case 1
    o1=find(t,"or",ob)
    add(ob+1,o1-1,"P","choice case 1: w = [] (choice(n, <>), its head as an equation)","class P; rule 2 (a head test of the problem's own case)")
    add(o1,o1,"P","or between choice's cases 1 and 2 (the definition's disjunction of cases)","rule 6 (a disjunction the problem states); rule 20")
    gz=find(t,"gtz",o1)
    add(o1+1,gz-1,"P","choice case 2 head: w = [e'&t'] (s = <e> ++ t)","class P; rule 2")
    add(gz,gz+3,"R","choice case 2 conjunct gtz(m), standing for n > 0 (application of the reformulated comparison)","METRICS class R (the reformulation of n > 0); rule 10 (the call is classed with the construct it applies, not the surrounding case)")
    b=gz+4; be=find(t,"}",b)
    add(b,be,"P","choice case 2 conjunct {e = 'l' or e = 'r'} (e = L or e = R, in that order)","rule 6 (a disjunction the problem states); class P")
    m1=be+1; me=m1+4
    assert t[m1]=="m1'" and t[me]=="1", (f,t[m1:me+1])
    add(m1,me,"P","choice case 2 conjunct m1' = m - 1 (n - 1 as a fresh unknown)","SPECIFICATION Arithmetic (a compound or decomposed arithmetic relation is a transcription); rule 8 (relation, not one-way evaluation)")
    ch=me+1; che=find(t,")",ch)
    add(ch,che,"P","choice case 2 conjunct choice(m1, t) (choice(n - 1, t))","class P")
    add(che+1,che+2,"P","} end closing choice's definition","rule 10")
    assert t[che+1]=="}" and t[che+2]=="end"
    a=find(t,"accept'"); ae=find(t,"end",a)
    add(a,ae,"P","accept'=lambda u begin ... end: accept given by facts in a closed world, the facts as alternatives (u = acc1 [or u = acc2])","rule 6 (a set of facts the problem states is P); class P")
    q=ae+1
    add(q,len(t)-1,"P","the stage's query: begin choice(n, s) accept(s) end, in the order written","class P (the query); presentation order kept, so no move (rule 4)")
    # coverage check
    cov=[0]*len(t)
    for s in S:
        for x in range(s['from'],s['to']+1): cov[x]+=1
    assert all(v==1 for v in cov), (f,cov)
    return S,len(t)
out={}; tot={}
for f in FILES:
    S,n=spans_for(f); out['absys/'+f]=S
    cnt={}
    for s in S: cnt[s['class']]=cnt.get(s['class'],0)+s['to']-s['from']+1
    tot[f]=(n,cnt)
json.dump(out,open('results/absys/classes-1C/A/parts/absys-P12/tokens.part.json','w'),indent=1,ensure_ascii=False)
for f,(n,c) in tot.items(): print(f,n,c)
