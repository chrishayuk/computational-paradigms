import sys,csv
base='./results/python/tokens/'
def load(path):
    rows=[]
    with open(base+path+'.tokens.tsv') as f:
        next(f)
        for line in f:
            i,l,t=line.rstrip('\n').split('\t',2)
            rows.append((int(i),int(l),t))
    return rows
if __name__=='__main__':
    rows=load(sys.argv[1])
    cur=None;buf=[]
    for i,l,t in rows:
        if l!=cur:
            if buf: print('L%d [%d-%d] %s'%(cur,buf[0][0],buf[-1][0],' '.join(x[1] for x in buf)))
            cur=l;buf=[]
        buf.append((i,t))
    print('L%d [%d-%d] %s'%(cur,buf[0][0],buf[-1][0],' '.join(x[1] for x in buf)))
