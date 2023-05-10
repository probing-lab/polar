from sympy import *
from sympy.solvers.solveset import linsolve

n = Symbol("n", integer=True)
p0 = Symbol("p0", real=True)
p1 = Symbol("p1", real=True)
p2 = Symbol("p2", real=True)
p3 = Symbol("p3", real=True)

m1 = 1 + 2 * 4 ** (-n)
m2 = 1 + 8 * 4 ** (-n)
m3 = 1 + 26 * 4 ** (-n)

equations = [
    p0 + p1 + p2 + p3 - 1,
    0 * p0 + 1 * p1 + 2 * p2 + 3 * p3 - m1,
    (0**2) * p0 + (1**2) * p1 + (2**2) * p2 + (3**2) * p3 - m2,
    (0**3) * p0 + (1**3) * p1 + (2**3) * p2 + (3**3) * p3 - m3,
]

solution = linsolve(equations, (p0, p1, p2, p3))
print(solution)
