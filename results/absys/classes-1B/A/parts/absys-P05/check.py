import json, collections
R = './results/absys/tokens/'
d = json.load(open('results/absys/classes-1B/A/parts/absys-P05/absys.json'))
ok = True
for t, spans in d['tokens'].items():
    n = sum(1 for l in open(R + t + '.tokens.tsv')) - 1
    cov = collections.Counter()
    for s in spans:
        assert s['class'] in 'PCRSH'
        for i in range(s['from'], s['to'] + 1): cov[i] += 1
    bad = [i for i in range(n) if cov[i] != 1] + [i for i in cov if i >= n]
    tot = collections.Counter()
    for s in spans: tot[s['class']] += s['to'] - s['from'] + 1
    print(t, 'tokens', n, 'bad', bad, dict(tot)); ok &= not bad
print('outcomes', len(d['outcomes']), 'mode_differences', len(d['mode_differences']), 'ALL OK' if ok else 'FAIL')
