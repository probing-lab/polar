from typing import Dict
from symengine.lib.symengine_wrapper import sympify
from sympy import Eq, Expr, Piecewise, Poly, solve, symbols
from inputparser.parser import Parser
from invariants.invariant_ideal import InvariantIdeal
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder


program = Parser().parse_file("documentation/test/example_paper_2019.prob")
# Construct normal form so that Polar can analyze it
program = normalize_program(program)

recurrence_builder = RecBuilder(program)
N = symbols('n', integer=True)
C = symbols('C')

monoms = [sympify('k'),sympify('k**2'), sympify('x'), sympify('x**2'), sympify('x*k')]
vars_to_eliminate = [sympify('k'), sympify('x'), C]

def add_constant_factor(expr):
    constant_part = expr if expr.is_number else next((ele for ele in expr.args if ele.is_number), 0)

    return (expr-constant_part+constant_part*C).simplify()
recurrences = {f"E({monom})": Piecewise((add_constant_factor(recurrence_builder.get_recurrence(monom)-monom), True)) for monom in monoms}



invariant_ideal = InvariantIdeal(recurrences)
basis = invariant_ideal.compute_basis()
print(basis)

# Now we build an equation system to extract the coeffs

coeffs = list(symbols(f'c0:{len(basis)}'))
equations = []

for var in vars_to_eliminate:
    expr = 0
    for be, base_coeff in zip(basis, coeffs):
        var_coeff = be.coeff(var, 1)
        expr += var_coeff*base_coeff
    equations.append(expr)

sol_coeffs:Dict[any, any] = solve(equations, coeffs)

# all coefficients not appearing in the solution can safely be set to zero
for coeff in coeffs:
    if coeff in sol_coeffs.keys():
        continue
    elif any(s.has(coeff) for s in sol_coeffs.values()):
        sol_coeffs[coeff] = coeff
    else:
        sol_coeffs[coeff] = 0

coeffs_sorted =sorted(list(sol_coeffs.items()), key=lambda x:str(x[0]))

final_expression = 0
for expr, (_, coeff) in zip(basis, coeffs_sorted):
    final_expression+= expr*coeff

final_expression1 = final_expression.simplify()

# the coeffs which are just coeff:coeff in the solution dict can be chosen freely - we swap them with a 1
for sol_coeff in sol_coeffs:
    if sol_coeffs[sol_coeff] == sol_coeff:
        final_expression1 = final_expression1.subs(sol_coeff, 1)

pass