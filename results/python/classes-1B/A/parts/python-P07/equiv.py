"""Brute-force check, over integers in [-N, N], that each residual held at the end
of the stage denotes exactly the valid outcomes of the problem file.
The residuals are those read from the records' observe.raw (identical in all three
configurations up to the rendering of Vars). Algebraic reasoning is in python.notes.md."""
N=200
R=range(-N,N+1)
cases={
 'P07b':(lambda x,y: x+y==10 and x-y==4, lambda x,y:(x,y)==(7,3)),
 'P07c':(lambda x,y: x+y==10, lambda x,y: x+y==10),
 'P07f':(lambda x,y: x+y==10 and x+y==11, lambda x,y: False),
}
for k,(res,valid) in cases.items():
    bad=[(x,y) for x in R for y in R if res(x,y)!=valid(x,y)]
    print(k,'residual == valid outcomes on [-%d,%d]^2:'%(N,N),not bad, 'solutions:',sum(1 for x in R for y in R if res(x,y)))
bad=[x for x in R if (x*x==9)!=(x in (3,-3))]
print('P07g residual x*x=9 == {3,-3} on [-%d,%d]:'%(N,N),not bad,[x for x in R if x*x==9])
# P07e: the program reports none; check none exists
print('P07e no integer w with w*2==15 on range:',not [w for w in R if w*2==15])
# P07a/P07d explicit answers satisfy the relations and are unique
print('P07a', [ (x,y,z) for x in range(-30,31) for y in range(-30,31) for z in range(-30,31) if x+y+z==12 and y+z==7 and z==3])
print('P07d', [w for w in R if w*2==14])
