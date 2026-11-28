import sys, json
sys.path.insert(0, '.')
from engine import apply, show
from specs import TEXTS
res = {}
for name, f in TEXTS.items():
    for cfg, ext in (('report', 'alg'), ('x1', 'a60')):
        path = f'{cfg}/{name}.{ext}'
        toks, spans = apply(path, f())
        res[path] = (toks, spans)
if __name__ == '__main__':
    for p in sys.argv[1:]:
        toks, spans = res[p]
        show(p, spans, toks)
