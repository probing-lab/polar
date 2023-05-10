from sympy import *

n = Symbol("n")
x = Symbol("x")
y = Symbol("y")
s = Symbol("s")

p1 = 3 * n / 4 - 1 - x
p2 = 3 * n / 2 + 1 - y
p3 = n * (3 * n**2 + 3 * n - 8) / 8 - s

p1 = p1.as_poly()
p2 = p2.as_poly()
p3 = p3.as_poly()

gb = groebner([p1, p2, p3], n, x, y, s)

invariants = []
for poly in gb.args[0]:
    if n not in poly.free_symbols:
        print(poly)
