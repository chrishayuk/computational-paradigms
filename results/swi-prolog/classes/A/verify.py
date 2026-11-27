# Independent check of swi-prolog.json: valid JSON, every token of every text covered once.
import json, csv
TOK = '/Users/christopherhay/cp-roles/classifier-A/results/swi-prolog/tokens'
d = json.load(open('/Users/christopherhay/cp-roles/classes-A/swi-prolog/swi-prolog.json'))
texts = list(csv.reader(open(TOK + '/TEXTS.tsv'), delimiter='\t'))[1:]
assert set(d['tokens']) == {r[0] for r in texts}
per_cfg = {}
for r in texts:
    n = sum(1 for _ in open('%s/%s.tokens.tsv' % (TOK, r[0]))) - 1
    cov = [0] * n
    t = {}
    for s in d['tokens'][r[0]]:
        assert s['class'] in 'PCRSH'
        for i in range(s['from'], s['to'] + 1): cov[i] += 1
        t[s['class']] = t.get(s['class'], 0) + s['to'] - s['from'] + 1
    assert cov == [1] * n, r[0]
    for path in [r[0]] + (r[1].split() if len(r) > 1 else []):
        cfg = path.split('/')[0]
        pc = per_cfg.setdefault(cfg, {k: 0 for k in 'PCRSH'})
        for k, v in t.items(): pc[k] += v
print('coverage ok for', len(texts), 'texts')
for c, v in sorted(per_cfg.items()): print(c, v, sum(v.values()))
from collections import Counter
print(Counter((o['semantic'], tuple(o['execution_state'] or [])) for o in d['outcomes']).most_common())
print(Counter(o['configuration'] + ' ' + o['semantic'] for o in d['outcomes']).most_common())
