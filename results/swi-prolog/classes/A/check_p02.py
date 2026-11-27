# Checks that u + v = 16 and w * u = v, over the integers, have exactly the ten
# triples of problems/02-late-information.md. From u + v = 16 and v = w*u:
# u*(w+1) = 16, so u != 0 and u divides 16, hence |u| <= 16, v = 16 - u, and
# w = v / u, so a box |u| <= 16 contains every solution; w is then determined.
sols = set()
for u in range(-16, 17):
    v = 16 - u
    if u == 0:
        if v == 0:
            raise SystemExit('u = 0 would need v = 0')
        continue  # w*0 = v != 0 has no w
    if v % u == 0:
        sols.add((u, v, v // u))
ten = {(1, 15, 15), (2, 14, 7), (4, 12, 3), (8, 8, 1), (16, 0, 0), (-1, 17, -17),
       (-2, 18, -9), (-4, 20, -5), (-8, 24, -3), (-16, 32, -2)}
print(sorted(sols)); assert sols == ten; print('equal to the ten triples')
# R2, R3: u = 2 and w*2 = v: v = 2w for every integer w (checked on a range)
assert all((2 * w) == v for w in range(-50, 51) for v in [2 * w])
# R1, R2, R3: u = 2 -> v = 14 -> w = 7
assert 16 - 2 == 14 and 14 % 2 == 0 and 14 // 2 == 7; print('final stage: (2, 14, 7)')
