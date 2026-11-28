import os,difflib
from build import load,spans,BASE
def seq(text):
    cfg,f=text.split('/')
    sp,n=spans(text,load(f'specs/{cfg}_{f}.py'))
    toks=[l.rstrip('\n').split('\t')[2].replace('̲','').replace('boolean','Boolean') for l in open(os.path.join(BASE,text+'.tokens.tsv'))][1:]
    out=[]
    for s in sp:
        if s['class']!='H': out+= [s['class']+':'+t for t in toks[s['from']:s['to']+1]]
    return out
for p in ['P09a.AB','P09b','P09c','P09d','P09e','P10a','P10b','P10c','P10d']:
    a=seq('report/'+p+'.alg'); b=seq('x1/'+p+'.a60')
    d=[l for l in difflib.unified_diff(a,b,lineterm='',n=0) if not l.startswith(('---','+++','@@'))]
    print(p,' '.join(d))
