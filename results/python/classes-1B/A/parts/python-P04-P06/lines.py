import csv,re,sys,collections
REPO='/Users/christopherhay/cp-roles/classifier-1B-A'
def texts():
    rows=list(csv.reader(open(REPO+'/results/python/tokens/TEXTS-1B-P04-P06.tsv'),delimiter='\t'))[1:]
    return [r[0] for r in rows]
def load(path):
    src=open(f'{REPO}/programs/python/{path}').read().split('\n')
    toks=list(csv.reader(open(f'{REPO}/results/python/tokens/{path}.tokens.tsv'),delimiter='\t',quoting=csv.QUOTE_NONE))[1:]
    toks=[(int(a),int(b),c) for a,b,c in toks]
    # context per line
    ctx={}; cur='<module>'
    for i,l in enumerate(src,1):
        if l and not l[0].isspace() and not l.startswith('#'):
            m=re.match(r'(def|class)\s+(\w+)',l)
            if m: cur=m.group(2)
            elif l.startswith('while'): cur='<main>'
            else: cur='<module>'
        ctx[i]=cur
    return src,toks,ctx
if __name__=='__main__':
    seen=collections.OrderedDict()
    for t in texts():
        src,toks,ctx=load(t)
        lines=sorted(set(b for a,b,c in toks if c not in('<INDENT>','<DEDENT>')))
        for ln in lines:
            k=(ctx[ln],src[ln-1].split('#')[0].strip() if not src[ln-1].strip().startswith(('"','\'')) else src[ln-1].strip())
            seen.setdefault(k,[]).append(t)
    for (c,l),ts in seen.items(): print(f'{c:12s} | {l}   [{len(ts)}]')
