import json, gzip, sys, re, collections
def load(p): return json.load(gzip.open(p) if p.endswith('.gz') else open(p))
d = load(sys.argv[1]); stg = int(sys.argv[2]); att = int(sys.argv[3]) if len(sys.argv)>3 else -1
a = d['stages'][stg-1]['attempts'][att]
raw = a['observe']['raw'] or a['print'] or ''
head = raw.split('\n',1)[0]; print('HEAD', head)
blocks = re.split(r'\n(?=  derivation #)', raw)
ders = [b for b in blocks if b.lstrip().startswith('derivation #')]
print('n derivs', len(ders))
cat = collections.Counter(); vals = collections.defaultdict(list)
for b in ders:
    m = re.match(r'\s*derivation #(\d+) \(([^)]*)\)', b)
    num, status = m.group(1), m.group(2)
    xm = re.search(r'^    x = (.*)$', b, re.M) or re.search(r'^    x\s+(.*)$', b, re.M)
    xv = xm.group(1)[:60] if xm else '?'
    bound = re.fullmatch(r'-?\d+', xv.strip()) is not None
    key = (status, 'int' if bound else xv[:30])
    cat[key] += 1
    if bound: vals[status].append(int(xv))
for k,v in sorted(cat.items(), key=lambda t:-t[1])[:20]: print(k, v)
for s,v in vals.items(): print(s, 'ints', len(v), 'distinct', len(set(v)), 'min', min(v), 'max', max(v), 'missing in range', sorted(set(range(min(v),max(v)+1))-set(v))[:20])
if len(sys.argv)>4:
    import itertools
    for b in ders:
        if sys.argv[4] in b: print(b[:int(sys.argv[5])]); break
