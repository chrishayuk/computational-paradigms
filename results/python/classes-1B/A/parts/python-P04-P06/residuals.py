"""Residual equivalence checks (classifier A, python P04-P06).
Each residual a program holds is compared with the valid outcome over a sample
of the problem's domain: integers -1000..1000, atoms, and sequences."""
ints=list(range(-1000,1001)); atoms=["'a","'brown","'c101"]; seqs=[(),(1,),(1,2)]
values=ints+atoms+seqs
isint=lambda v: isinstance(v,int)
checks={
 # P05b stage 1: held ('>', 1): the comparison x > 1 (holds only of integers)
 'P05b stage 1: held x > 1 vs every integer x > 1':
   (lambda v: isint(v) and v>1, lambda v: isint(v) and v>1),
 # P06a/P06c stage 1: held not (x = 1)
 'P06a/c stage 1: held not (x = 1) vs every value other than 1':
   (lambda v: not (isint(v) and v==1), lambda v: v!=1 or not isint(v)),
}
for name,(res,valid) in checks.items():
    bad=[v for v in values if res(v)!=valid(v)]
    print(name, 'equivalent on sample' if not bad else 'DIFFERS on %r'%bad[:5])
