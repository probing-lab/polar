from sympy import *
from sympy.solvers.solveset import linsolve


p0 = Symbol("p0", real=True)
p1 = Symbol("p1", real=True)
p2 = Symbol("p2", real=True)
p3 = Symbol("p3", real=True)
p4 = Symbol("p4", real=True)
p5 = Symbol("p5", real=True)

m = {
    1: sympify(
        "1 - 2 * 9 ** (-n) + (162 / 43) * (11 / 81) ** n + (96 / 43) * (2 / 3) ** n"
    ),
    2: sympify(
        "1 - 8 * 9 ** (-n) + (992 / 43) * (11 / 81) ** n + (384 / 43) * (2 / 3) ** n"
    ),
    3: sympify(
        "1 - 26 * 9 ** (-n) + (5202 / 43) * (11 / 81) ** n + (1248 / 43) * (2 / 3) ** n"
    ),
    4: sympify(
        "1 - 80 * 9 ** (-n) + (26432 / 43) * (11 / 81) ** n + (3840 / 43) * (2 / 3) ** n"
    ),
    5: sympify(
        "1 - 242 * 9 ** (-n) + (133122 / 43) * (11 / 81) ** n + (11616 / 43) * (2 / 3) ** n"
    ),
}

equations = [
    (0**p) * p0
    + (1**p) * p1
    + (2**p) * p2
    + (3**p) * p3
    + (4**p) * p4
    + (5**p) * p5
    - m[p]
    for p in (1, 2, 3, 4, 5)
]
equations.append(p0 + p1 + p2 + p3 + p4 + p5 - 1)


solution = linsolve(equations, (p0, p1, p2, p3, p4, p5))
solution = list(solution)[0]
print([s for s in solution])
print([N(s) for s in solution])
print([limit(s, Symbol("n"), oo) for s in solution])
