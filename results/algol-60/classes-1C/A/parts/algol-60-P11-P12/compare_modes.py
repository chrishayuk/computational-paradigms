"""Compare cost and storage records with the behaviour record of the same
configuration and instance, on what the classification depends on: per
stage, the answers, the execution state, the observe text, the entries
emitted, and whether the stage was reached. Read-only.
Usage: python3 -I compare_modes.py RESULTS_DIR"""
import json, sys, os, glob, gzip, re

def load(p):
    if p.endswith('.gz'):
        with gzip.open(p, 'rt') as f:
            return json.load(f)
    with open(p) as f:
        return json.load(f)

def feats(d):
    out = {}
    for s in d['stages']:
        a = s['attempts'][-1]
        c = a['computations'][0]
        out[s['stage']] = {
            'answers': [x['verbatim'] for x in c['queries'][0]['answers']],
            'ended_by': c['queries'][0]['ended_by'],
            'states': c['execution_state']['states'],
            'observe': re.sub(r'\s+', ' ', a['observe']['raw'] or ''),
            'effects': [e['entry'] for e in (a.get('effects') or [])],
            'timeout': a['safety_limit']['hit'],
            'attempts': len(s['attempts']),
        }
    return out

root = sys.argv[1]
for conf in ('report', 'x1', 'x1sim'):
    for prob in ('P11', 'P12'):
        raw = os.path.join(root, conf, prob, 'raw')
        if not os.path.isdir(raw):
            continue
        recs = sorted(glob.glob(raw + '/*.json')) + sorted(glob.glob(raw + '/*.json.gz'))
        by = {}
        for p in recs:
            d = load(p)
            by.setdefault(d['run']['instance'], {})[d['run']['mode']] = (p, d)
        for inst in sorted(by):
            modes = by[inst]
            if 'behaviour' not in modes:
                print(conf, inst, 'NO BEHAVIOUR RECORD')
                continue
            fb = feats(modes['behaviour'][1])
            for m in ('cost', 'storage'):
                if m not in modes:
                    continue
                fm = feats(modes[m][1])
                for st in fb:
                    for k in fb[st]:
                        if k == 'effects':
                            continue  # cost/storage write the observation log
                        if fb[st][k] != fm.get(st, {}).get(k):
                            print('DIFF', conf, inst, m, 'stage', st, k, repr(fb[st][k])[:200], '|', repr(fm.get(st, {}).get(k))[:200])
                # effects: compare the entries, which go to the other log
                for st in fb:
                    if fb[st]['effects'] != fm[st]['effects']:
                        print('EFFECTS', conf, inst, m, 'stage', st, fb[st]['effects'], fm[st]['effects'])
            print('checked', conf, inst, sorted(modes))
