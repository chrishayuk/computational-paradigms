"""Check the hand proofs against actual recorded residuals, without running Absys.

No finite enumeration is used to claim completeness over an infinite domain.
Integer arithmetic proofs are elimination/factorisation identities. P08 equality
graphs are existentially projected by identifying connected components.
"""
import re
from inspect_records import records

def component_map(edges):
    parent={v:v for pair in edges for v in pair}
    def find(v):
        while parent[v]!=v:
            v=parent[v]
        return v
    for a,b in edges:
        parent[find(a)]=find(b)
    return {v:find(v) for v in parent}

def check():
    checked=0
    for f,x in records():
        r=x['run']
        if r['mode']!='behaviour':continue
        for s in x['stages']:
            a=s['attempts'][-1]; raw=a['print'] or ''; p=r['subproblem']; k=s['stage']
            if p in ['P07b','P07c','P07f','P07g']:
                wanted={'P07b':['x + y = 10','4 + y = x'],
                        'P07c':['x + y = 10'],
                        'P07f':['x + y = 10','x + y = 11'],
                        'P07g':['x * x = 9']}[p]
                line=next(z for z in raw.splitlines() if z.startswith('    suspended'))
                actual=[re.sub(r'\s+\(waits.*','',z).strip()
                        for z in line.replace('    suspended','',1).split(';')]
                assert actual==wanted,(f,actual)
                # b: x=4+y, substituted into x+y=10 gives 2y=6;
                # c: exactly the input; f: subtract gives 0=1;
                # g: integral domain and x²-9=(x-3)(x+3).
                checked+=1
            if p=='P04a' and r['configuration']=='absys-depth-first':
                assert 'to do       loop(x)' in raw and 'to do       x = 1' in raw
                assert '    x = 1' not in raw.splitlines()
                checked+=1
            if p=='P08a' and k in [4,5]:
                line=next(z for z in raw.splitlines() if z.startswith('    suspended'))
                pairs=[tuple(t.strip().split(' = '))
                       for t in line.replace('    suspended','',1).split(';')]
                assert all(len(t)==2 for t in pairs)
                assert len(pairs)==(7 if k==4 else 8)
                comp=component_map(pairs)
                wanted=[{'x','y','h₁','h₂','h₆'},{'z','h₃','h₄','h₅'}] if k==4 else [set(comp)]
                actual=[{v for v in comp if comp[v]==w} for w in set(comp.values())]
                assert {frozenset(t) for t in actual}=={frozenset(t) for t in wanted}
                assert 'a = [x;y;z]' in raw and 'b = [h₅;h₆;h₁]' in raw
                assert comp['h₅']==comp['z']
                assert comp['h₆']==comp['y'] and comp['h₁']==comp['y']
                if k==5:assert comp['x']==comp['y']==comp['z']
                checked+=1
            if p in ['P08a','P08b'] and k in [2,3]:
                assert 'rev  uninstantiated' in raw
                assert 'rev([x;y;z], b)  (waits for a definition: rev)' in raw
                if k==3:assert 'suspended: x = y' in raw
                checked+=1
            if p=='P08c' and k in [2,3] and not ('variants/' in r['program']['path'] and k==3):
                name='rev' if k==2 else 'revmore'
                assert name+'([1;2], b)  (waits for a definition: '+name+')' in raw
                checked+=1
    return checked

if __name__=='__main__':print('Checked',check(),'behaviour residuals against hand equivalence proofs.')
