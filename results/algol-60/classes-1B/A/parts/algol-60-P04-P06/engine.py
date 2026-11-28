"""Span engine for classifier A, algol-60 P04-P06.
A spec is a list of entries (lines, cls, construct, rule, start, end), applied in
order, later entries overriding earlier ones. lines is 'a' or 'a-b'. start/end are
token texts ('text' or 'text#n', the n-th occurrence) located within the selected
lines (end searched from the start position); None means the first / last token of
the selection; '$' means the last. After assignment, every ';' and ',' takes the
class of the construct that follows it (METRICS.md rule 20), or of the one before it
where the next token is 'end' or 'else'."""
import csv, sys
TOK = '/Users/christopherhay/cp-roles/classifier-1B-A/results/algol-60/tokens/'

def load(path):
    rows = []
    with open(TOK + path + '.tokens.tsv') as f:
        r = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            rows.append((int(row[0]), int(row[1]), row[2]))
    assert [x[0] for x in rows] == list(range(len(rows)))
    return rows

def find(sel, toks, pat, frm=0):
    if pat == '$':
        return sel[-1]
    n = 1
    if '#' in pat and pat != '#':
        pat, n = pat.rsplit('#', 1); n = int(n)
    c = 0
    for i in sel:
        if i < frm: continue
        if toks[i][2] == pat:
            c += 1
            if c == n: return i
    raise ValueError(f'pattern {pat}#{n} not found from {frm}')

def apply(path, spec):
    toks = load(path)
    N = len(toks)
    asg = [None] * N
    for ent in spec:
        lines, cls, construct, rule = ent[:4]
        start = ent[4] if len(ent) > 4 else None
        end = ent[5] if len(ent) > 5 else None
        if isinstance(lines, int): a = b = lines
        elif '-' in str(lines): a, b = map(int, str(lines).split('-'))
        else: a = b = int(lines)
        sel = [t[0] for t in toks if a <= t[1] <= b]
        if not sel: raise ValueError(f'{path}: no tokens on lines {lines}')
        s = sel[0] if start is None else find(sel, toks, start)
        e = sel[-1] if end is None else find(sel, toks, end, s)
        for i in range(s, e + 1):
            asg[i] = (cls, construct, rule)
    missing = [toks[i] for i in range(N) if asg[i] is None]
    if missing:
        raise ValueError(f'{path}: unassigned tokens {missing[:10]} ... {len(missing)}')
    for i in range(N):
        if toks[i][2] in (';', ','):
            j = i + 1
            while j < N and toks[j][2] in (';', ','): j += 1
            if j < N and toks[j][2] not in ('end', 'else'):
                asg[i] = asg[j]
            else:
                k = i - 1
                while k >= 0 and toks[k][2] in (';', ','): k -= 1
                asg[i] = asg[k]
    spans = []
    for i in range(N):
        if spans and spans[-1]['_key'] == asg[i]:
            spans[-1]['to'] = i
        else:
            spans.append({'from': i, 'to': i, 'class': asg[i][0], 'construct': asg[i][1], 'rule': asg[i][2], '_key': asg[i]})
    for s in spans: del s['_key']
    return toks, spans

def show(path, spans, toks):
    for s in spans:
        txt = ' '.join(toks[i][2] for i in range(s['from'], s['to'] + 1))
        print(f"{s['from']:4}-{s['to']:4} L{toks[s['from']][1]:3} {s['class']} | {txt[:110]}")
