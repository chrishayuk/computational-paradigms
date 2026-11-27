# Resolve the specs for every distinct text and write the per-line class views for review.
import sys, csv, json
sys.path.insert(0, "/Users/christopherhay/cp-roles/classes-A/algol-60")
from spans import build, show
from spec import SPEC, X1_MARKERS
TEXTS = [r[0] for r in csv.reader(open("/Users/christopherhay/cp-roles/classifier-A/results/algol-60/tokens/TEXTS.tsv"), delimiter="\t")][1:]
def family(text):
    b = text.split("/")[1].rsplit(".", 1)[0]
    return "P02b" if b.startswith("P02b") else b
out = {}
errs = []
for t in TEXTS:
    f = family(t)
    spec = SPEC[f]
    if t.startswith("x1/"):
        ov = X1_MARKERS.get(f, {})
        spec = [(ov.get(m, m), *rest) for m, *rest in spec]
    try:
        spans, toks = build(t, spec)
    except Exception as e:
        errs.append(f"{t}: {e}"); continue
    out[t] = spans
    with open(f"/Users/christopherhay/cp-roles/classes-A/algol-60/view/{t.replace('/', '__')}.txt", "w") as fh:
        show(t, spans, toks, fh)
print("\n".join(errs) or "all resolved")
json.dump(out, open("/Users/christopherhay/cp-roles/classes-A/algol-60/tokens.json", "w"), indent=0)
