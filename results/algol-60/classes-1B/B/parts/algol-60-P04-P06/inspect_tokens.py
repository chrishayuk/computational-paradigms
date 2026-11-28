import csv,sys,collections
from pathlib import Path
ROOT=Path('/Users/christopherhay/cp-roles/classifier-1B-B')
for name in sys.argv[1:]:
 p=ROOT/'results/algol-60/tokens'/name
 rows=list(csv.DictReader(p.read_text().splitlines(),delimiter='\t'))
 print('\nFILE',name,'TOKENS',len(rows))
 groups=collections.defaultdict(list)
 for r in rows:groups[int(r['line'])].append(r)
 for line,rs in groups.items():
  print(f"L{line} [{rs[0]['index']}:{rs[-1]['index']}]",' '.join(r['token'].replace('\u0332','') for r in rs))
