import json, sys, glob, os
root = '/Users/christopherhay/cp-roles/classifier-1B-A/results/algol-60'
out = []
for path in sorted(glob.glob(root + '/*/P0[456]/raw*/*.json')):
    r = json.load(open(path))
    rel = os.path.relpath(path, '/Users/christopherhay/cp-roles/classifier-1B-A')
    for st in r['stages']:
        for at in st['attempts']:
            for c in at['computations']:
                q = c['queries'][0] if c['queries'] else {}
                s = c.get('steps') or {}
                out.append(dict(rec=rel, mode=r['run']['mode'], inst=r['run']['instance'], cfg=r['run']['configuration'],
                    stage=st['stage'], att=at['attempt'], posed=at['posed']['how'], reason=at['posed'].get('reason'),
                    answers=[a['verbatim'] for a in q.get('answers', [])], ended=q.get('ended_by'),
                    states=c['execution_state'].get('states'), err=c['execution_state'].get('error_verbatim'),
                    obs=(at.get('observe') or {}).get('raw'), stage_steps=s.get('stage'), restated=s.get('restated'),
                    budget=s.get('budget'), rw=s.get('repeated_work'), ttfa=s.get('to_first_answer'), toend=s.get('to_end'),
                    pd=(c.get('alternatives') or {}).get('problem_defined'), susp=(c.get('suspended') or {}).get('items'),
                    ops=c.get('problem_operations'),
                    store={k: v for k, v in ((at.get('store') or {}).get('quantities') or {}).items()},
                    nans_stdout=(at.get('stdout') or '').count('[answer]'),
                    stderr_last=(at.get('stderr') or '').strip().splitlines()[-1:] ,
                    safety=at.get('safety_limit'), wall=at.get('wall_time_s'),
                    faults=r.get('harness_faults'), manual=(at.get('manual_actions') or []) + (r.get('manual_actions') or [])))
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print(len(out))
