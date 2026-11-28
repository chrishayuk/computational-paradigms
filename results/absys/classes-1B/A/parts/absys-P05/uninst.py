import json, gzip, sys, re, collections
def load(p): return json.load(gzip.open(p) if p.endswith('.gz') else open(p))
d = load(sys.argv[1]); stg = int(sys.argv[2]); att = int(sys.argv[3])
a = d['stages'][stg-1]['attempts'][att]
raw = a['observe']['raw'] or a['print'] or ''
blocks = re.split(r'\n(?=  derivation #)', raw)
ders = [b for b in blocks if b.lstrip().startswith('derivation #')]
c = collections.Counter(); ex = {}
for b in ders:
    status = re.match(r'\s*derivation #\d+ \(([^)]*)\)', b).group(1)
    xm = re.search(r'^    x(?: = |\s+)(.*)$', b, re.M); xv = xm.group(1).strip() if xm else '?'
    xb = 'int' if re.fullmatch(r'-?\d+', xv) else xv
    todo = re.search(r'^    to do\s+(.*)$', b, re.M)
    susp = re.search(r'^    suspended\s+(.*)$', b, re.M)
    nsusp = susp.group(1).count('waits for') if susp else 0
    td = todo.group(1) if todo else ''
    # classify to-do content
    kinds = tuple(sorted(set(re.findall(r'(pos\(|pick\(|gt\(|\w+ = \d+(?!\s*[+])|\+ 1 = |\{)', td))))
    other = [l.split()[0] for l in b.split('\n')[1:] if l.strip() and not re.match(r'    (procedures|x|to do|suspended)\b', l)]
    key = (status, xb, kinds, tuple(sorted(set(other))))
    c[key] += 1
    ex.setdefault(key, (nsusp, td[:300]))
for k, v in sorted(c.items(), key=lambda t: -t[1]): print(v, k, ex[k])
