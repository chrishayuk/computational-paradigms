import json
from pathlib import Path
from collections import Counter

ROOT = Path('.')
CONFIGS = ['absys', 'absys-depth-first', 'absys-wake-back']
PROBLEMS = ['P04', 'P06', 'P07', 'P08']

def records():
    for c in CONFIGS:
        for p in PROBLEMS:
            for d in ['raw', 'raw-rerun-m2']:
                for f in sorted((ROOT/'results/absys'/c/p/d).glob('*.json')):
                    yield f, json.loads(f.read_text())

def summary(f, x, full=False):
    r=x['run']
    print(str(f.relative_to(ROOT)), r['instance'], r['program']['path'], x.get('harness_faults'))
    for s in x['stages']:
        for a in s['attempts']:
            print('STAGE',s['stage'],'ATTEMPT',a['attempt'],a['posed'], 'NOTES',a['notes'])
            for c in a['computations']:
                print('STATE',c['execution_state'],'alt',c['alternatives']['at_boundary'],'susp',c['suspended'], 'queries',[(q['ended_by'],len(q['answers'])) for q in c['queries']])
            print('OBSERVE',a['observe']['raw'] if full else a['observe']['raw'][:1200])

if __name__ == '__main__':
    import sys
    for f,x in records():
        if x['run']['mode']=='behaviour' and any(z in str(f) for z in sys.argv[1:]):
            summary(f,x)
