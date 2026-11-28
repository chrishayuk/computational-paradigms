# Residual equivalence checks, by enumeration over a finite window of integers (the argument by hand is in algol-60.json).
W=range(-60,61)
# P09e: held residual {x = y + 1, y = x - 1} against the valid outcome {x = y + 1} (every integer pair).
res=[(x,y) for x in W for y in W if x==y+1 and y==x-1]
val=[(x,y) for x in W for y in W if x==y+1]
print('P09e residual == valid on window:',res==val,len(res))
# P10b stage 1: held residual d = 2 . b against the valid d = 2 . b.
res=[(b,d) for b in W for d in range(-130,131) if d==2*b]
val=[(b,d) for b in W for d in range(-130,131) if d==2*b]
print('P10b stage 1 residual == valid on window:',res==val,len(res))
