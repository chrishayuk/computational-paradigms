import sys,collections
f=sys.argv[1]
rows=[l.rstrip('\n').split('\t') for l in open(f)][1:]
by=collections.OrderedDict()
for i,ln,t in rows: by.setdefault(int(ln),[]).append((int(i),t))
for ln,ts in by.items():
    print(f"{ln}: [{ts[0][0]}-{ts[-1][0]}] "+" ".join(t for _,t in ts))
