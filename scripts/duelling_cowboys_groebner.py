from sympy import *

n = Symbol("n")
ahit = Symbol("ahit")
bhit = Symbol("bhit")
turn = Symbol("turn")

# Solutions to expected values:

p1 = -Rational(-1, 2) ** n / 6 + Rational(2, 3) - Rational(1, 2) ** n / 2 - ahit
p2 = Rational(-1, 2) ** n / 6 + Rational(1, 3) - Rational(1, 2) ** n / 2 - bhit
p3 = -Rational(-1, 2) ** n / 3 + Rational(1, 3) - turn


# Replace Rational(-1, 2)**n by "a" and Rational(1, 2)**n by "b"
# Also a and b are polynomially related by a**2 = b**2

a = Symbol("a")
b = Symbol("b")

p1 = -a / 6 + Rational(2, 3) - b / 2 - ahit
p2 = a / 6 + Rational(1, 3) - b / 2 - bhit
p3 = -a / 3 + Rational(1, 3) - turn
p4 = a**2 - b**2


gb = groebner([p1, p2, p3, p4], n, a, b, ahit, bhit, turn)
for poly in gb.args[0]:
    if not {n, a, b} & poly.free_symbols:
        print(poly)
