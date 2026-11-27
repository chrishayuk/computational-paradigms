import json,re
d=json.load(open('summary.json'))
def norm(s):
    if s is None: return None
    return re.sub(r'_\d+','_G',re.sub(r'_[A-Z]\d*\b','_V',s))
key=lambda x:(x['cfg'],x['inst'],x['prog'],x['stage'],x['att'])
beh={key(x):x for x in d if x['mode']=='behaviour'}
n=0
for x in d:
    if x['mode']=='behaviour': continue
    b=beh.get(key(x))
    if b is None: print('NO BEHAVIOUR', key(x), x['mode']); continue
    diffs=[]
    for f in ['answers','ended','states','coll']:
        if b[f]!=x[f]: diffs.append((f,b[f],x[f]))
    if norm(b['err'])!=norm(x['err']): diffs.append(('err',b['err'],x['err']))
    if norm(b['obs'])!=norm(x['obs']): diffs.append(('obs',b['obs'][:100] if b['obs'] else b['obs'],x['obs'][:100] if x['obs'] else x['obs']))
    if b['susp']['at_boundary']!=x['susp']['at_boundary']: diffs.append(('susp',b['susp'],x['susp']))
    if b['steps']!=x['steps']: diffs.append(('steps',b['steps'],x['steps']))
    if diffs:
        n+=1; print(x['mode'],key(x),x['rec']); [print('   ',dd) for dd in diffs]
# attempts count
from collections import Counter
c=Counter((x['cfg'],x['inst'],x['prog'],x['mode']) for x in d)
print(n)
