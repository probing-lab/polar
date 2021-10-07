from sympy import *

n = Symbol("x1")
x = Symbol("x2")
y = Symbol("x3")
s = Symbol("x4")

p1 = 3*n/4 - 1 - x
p2 = 3*n/2 + 1 - y
p3 = n*(3*n**2 + 3*n - 8)/8 - s

p1 = p1.as_poly([n, x, y, s])
p2 = p2.as_poly([n, x, y, s])
p3 = p3.as_poly([n, x, y, s])

gb = groebner([p1, p2, p3])

invariants = []
subs = {n: Symbol("n"), x: Symbol("x"), y: Symbol("y"), s: Symbol("s")}
for poly in gb.args[0]:
    if n not in poly.free_symbols:
        print(poly.subs(subs))
