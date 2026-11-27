# P02 stage with R1 and R2: integer solutions of u + v = 16 and w*u = v, versus the problem's ten triples.
ten = {(1,15,15),(2,14,7),(4,12,3),(8,8,1),(16,0,0),(-1,17,-17),(-2,18,-9),(-4,20,-5),(-8,24,-3),(-16,32,-2)}
sols = set()
# u = 0 gives v = 16 and w*0 = 16: impossible. Otherwise u*(w+1) = 16, so u | 16.
for u in [d for d in range(-16, 17) if d != 0 and 16 % d == 0]:
    v = 16 - u
    if v % u == 0: sols.add((u, v, v // u))
assert all(u + v == 16 and w * u == v for u, v, w in ten)
print('derived', sorted(sols)); print('equal to the ten:', sols == ten)
# brute force over a wide box as a second check
bf = {(u, 16-u, w) for u in range(-200, 201) for w in range(-200, 201) if w*u == 16-u}
print('brute force in box equal:', bf == ten)
