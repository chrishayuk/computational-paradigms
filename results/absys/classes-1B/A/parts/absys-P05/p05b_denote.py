"""P05b residual-equivalence check. For each derivation the system prints at the end of a
stage, compute the set of x it denotes from its binding, its suspended relations and the
visible items of its 'to do', and compare the union with the valid outcomes.
Usage: python3 p05b_denote.py RECORD STAGE ATTEMPT_INDEX
Assumptions (checked by the counts printed): every relation is a + b = c over integers;
a pending pos(v), or 'v = 1 or {pos(?), ? + 1 = v}', means v >= 1 (pos's least relation);
a pending pick(x) at stage 2 means x in {1,2,3}; truncated 'to do' items ('... N more')
are the derivation's remaining arithmetic checks and its pick(x) (stage 2)."""
import json, gzip, re, sys, collections
def load(p): return json.load(gzip.open(p) if p.endswith('.gz') else open(p))
SUB = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
d = load(sys.argv[1]); stage = int(sys.argv[2]); att = int(sys.argv[3])
a = d['stages'][stage-1]['attempts'][att]
raw = (a['observe']['raw'] or '').split('\n#', 1)[0]
ders = [b for b in re.split(r'\n(?=  derivation #)', raw) if b.lstrip().startswith('derivation #')]
head = raw.split('\n', 1)[0]
print('record', sys.argv[1].split('/')[-1], 'stage', stage, 'attempt', att+1, '|', head)
def isint(s): return re.fullmatch(r'-?\d+', s) is not None
pts = collections.Counter(); lows = []; kinds = collections.Counter(); bad = []
for b in ders:
    m = re.match(r'\s*derivation #(\d+) \(([^)]*)\)', b); num, status = m.group(1), m.group(2)
    xm = re.search(r'^    x(?: = |\s+)(\S+)', b, re.M).group(1).translate(SUB)
    susp = re.search(r'^    suspended\s+(.*)$', b, re.M); susp = susp.group(1) if susp else ''
    todo = re.search(r'^    to do\s+(.*)$', b, re.M); todo = todo.group(1) if todo else ''
    rels = re.findall(r'(\S+) \+ (\S+) = ([^\s;)]+)', (susp + ' ;; ' + todo).translate(SUB))
    val = {}
    if isint(xm): val['x'] = int(xm)
    rels = [(A.strip('{'), B, C) for A, B, C in rels]
    byvar = collections.defaultdict(list)
    for i, r in enumerate(rels):
        for t in r:
            if not isint(t): byvar[t].append(i)
    def g(t): return int(t) if isint(t) else val.get(t)
    work = list(range(len(rels)))
    while work:
        i = work.pop(); A, B, C = rels[i]
        va, vb, vc = g(A), g(B), g(C); newv = None
        if va is not None and vb is not None and vc is None: newv = (C, va+vb)
        elif va is not None and vc is not None and vb is None: newv = (B, vc-va)
        elif vb is not None and vc is not None and va is None: newv = (A, vc-vb)
        elif None not in (va, vb, vc) and va+vb != vc: bad.append((num, A, B, C))
        if newv:
            val[newv[0]] = newv[1]; work.extend(byvar[newv[0]])
    pickpending = 'pick(' in todo or '… ' in todo
    if 'x' in val:
        v = val['x']; kinds[(status, 'value')] += 1
        if stage == 2 and v not in (1, 2, 3) and status != 'hibernating':
            kinds[('pick pending on a value outside pick: denotes nothing', '')] += 1
        else: pts[v] += 1
        continue
    # symbolic: x = w + k along the chain of +1 relations
    k = 0; cur = 'x'; seen = set()
    byC = collections.defaultdict(list)
    for A, B, C in rels: byC[C].append((A, B))
    while True:
        nxt = None
        for A, B in byC.get(cur, []):
            if isint(B) and not isint(A): nxt = (A, int(B)); break
            if isint(A) and not isint(B): nxt = (B, int(A)); break
        if not nxt or nxt[0] in seen: break
        seen.add(nxt[0]); cur, k = nxt[0], k + nxt[1]
    if cur in val:
        v = val[cur] + k; kinds[(status, 'value via chain')] += 1
        if stage == 2 and v not in (1, 2, 3): kinds[('pick pending on a value outside pick: denotes nothing', '')] += 1
        else: pts[v] += 1
        continue
    if re.search(r'pos\(' + re.escape(cur) + r'\)|' + re.escape(cur) + r' = 1 or \{pos', todo.translate(SUB)):
        low = k + 1; kinds[(status, 'open tail: x >= %d' % low)] += 1
        if stage == 2: kinds[('open tail with pick(x): x >= %d and x in pick: denotes nothing' % low, '')] += 1
        else: lows.append(low)
        continue
    kinds[(status, 'UNRESOLVED')] += 1; print('UNRESOLVED', num, todo[:200])
for kk, v in sorted(kinds.items()): print('  ', v, kk)
print('  inconsistent fully-known relations seen:', len(bad))
vs = sorted(pts)
print('  distinct explicit values', len(vs), 'min', vs[0] if vs else None, 'max', vs[-1] if vs else None,
      'duplicates', sum(1 for v in pts.values() if v > 1))
if vs:
    gaps = sorted(set(range(vs[0], vs[-1]+1)) - set(vs)); print('  gaps', gaps[:10])
print('  open tails (lower bounds)', lows)
if stage == 1:
    ok = vs and vs[0] == 2 and not gaps and len(lows) == 1 and lows[0] == vs[-1] + 1
    print('  UNION == {x > 1}:', bool(ok))
else:
    print('  UNION == {2,3}:', vs == [2, 3])
