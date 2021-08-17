from sympy import solve, sympify

equations = [
    "-k*a + b + 5*f/6 + 2*c/9 + 5*d/6 + 4*a/3",
    "-k*f + 4*f/3 + d/2",
    "-k*d + f/6 + d",
    "13*b/18 + 13*c/18 + 13*a/18",
    "-k*c + b/2 + 20*c/9 + a",
    "-k*b + b + c/18 + a/6",
    "5*b/3 + c/3 + a",
    "2*b/3 + 2*c + 4*a/3",
    "-g"
]
equations = [sympify(e) for e in equations]
unknowns = {s for e in equations for s in e.free_symbols}

solutions = solve(equations, unknowns, dict=True)

print(solutions)

# Should all be zero but are not:
for solution in solutions:
    for e in equations:
        print(e.subs(solution).simplify())