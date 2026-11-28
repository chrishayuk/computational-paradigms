import sys,csv
R='./results/python/tokens/'
def load(t):
    rows=[]
    with open(R+t+'.tokens.tsv') as f:
        next(f)
        for line in f:
            i,l,tok=line.rstrip('\n').split('\t',2)
            rows.append((int(i),int(l),tok))
    return rows
if __name__=='__main__':
    rows=load(sys.argv[1])
    by={}
    for i,l,t in rows: by.setdefault(l,[]).append((i,t))
    for l in sorted(by):
        toks=by[l]
        print(f"{l:4d} [{toks[0][0]}-{toks[-1][0]}] "+' '.join(t for _,t in toks))
