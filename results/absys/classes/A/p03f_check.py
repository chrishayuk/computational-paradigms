# P03f: for every derivation printed at the end of the stage, its status and the
# length of the prefix of a it fixes (elements before any open tail &k).
# Argument: any solution of rev(a, <1,2,3>) has length 3, so a derivation whose a
# already has >= 4 elements denotes no solution (its remaining work is inconsistent).
import json, re, sys, collections
for path in sys.argv[1:]:
    d = json.load(open(path))
    for s in d['stages']:
        for a in s['attempts']:
            pr = a['print'] or ''
            blocks = re.split(r'\n(?=  derivation #)', pr)
            stat = collections.Counter(); lens = collections.Counter(); bad = []
            for b in blocks[1:]:
                m = re.match(r'  derivation #(\d+) \(([^)]*)\)', b)
                if not m: continue
                st = m.group(2)
                ma = re.search(r'\n    a = (\[.*?\])\s*(?:\(|\n|$)', b)
                if not ma:
                    ma2 = re.search(r'\n    a (.*)', b); val = ma2.group(0) if ma2 else None
                    bad.append((m.group(1), st, val)); continue
                body = ma.group(1)[1:-1]
                tail = '&' in body
                elems = body.split('&')[0].split(';') if body else []
                n = len([e for e in elems if e != ''])
                stat[st] += 1; lens[(st, n, tail)] += 1
                if st == 'hibernating': print('  hibernating', m.group(1), ma.group(1))
            print(path.split('/raw/')[-1], 'attempt', a['attempt'], 'header:', pr.split('\n')[0])
            print('  statuses', dict(stat))
            short = {k:v for k,v in lens.items() if k[1] <= 3}
            print('  derivations with prefix length <= 3:', short)
            print('  min prefix length among still elaborating:', min([k[1] for k in lens if k[0]!='hibernating'], default=None))
            print('  no a-binding parsed:', bad[:5], len(bad))
