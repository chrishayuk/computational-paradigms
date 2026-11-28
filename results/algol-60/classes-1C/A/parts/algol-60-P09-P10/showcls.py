import sys,os,collections
from build import load,spans,BASE
text=sys.argv[1]; pat=sys.argv[2] if len(sys.argv)>2 else None
cfg,f=text.split('/')
sp,n=spans(text,load(f'specs/{cfg}_{f}.py'))
cls=['?']*n
for s in sp:
    for j in range(s['from'],s['to']+1): cls[j]=s['class']
rows=[l.rstrip('\n').split('\t') for l in open(os.path.join(BASE,text+'.tokens.tsv'))][1:]
by=collections.OrderedDict()
for i,ln,t in rows: by.setdefault(int(ln),[]).append((int(i),t.replace('̲','')))
for ln,ts in by.items():
    s=" ".join(f"{t}/{cls[i]}" for i,t in ts)
    if pat is None or any(p in s for p in pat.split('|')):
        print(f"{ln}: [{ts[0][0]}] {s}")
