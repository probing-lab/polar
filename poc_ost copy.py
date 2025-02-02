from functools import reduce
from typing import Dict
from symengine.lib.symengine_wrapper import sympify
from sympy import Piecewise, solve, symbols
from inputparser.parser import Parser
from invariants.invariant_ideal import InvariantIdeal
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder

program = Parser().parse_file("documentation/test/example_paper_2019.prob")
# Construct normal form so that Polar can analyze it
program = normalize_program(program)

recurrence_builder = RecBuilder(program)
C = symbols('C')

vars = [sympify('k'), sympify('x')]
monoms = [sympify('k'),sympify('k**2'),sympify('x**2'), sympify('x*k')]
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

final_expression = final_expression.simplify()
final_expression1 = final_expression

# the coeffs which are just coeff:coeff in the solution dict can be chosen freely - we swap them with a 1
for sol_coeff in sol_coeffs:
    if sol_coeffs[sol_coeff] == sol_coeff:
        final_expression1 = final_expression1.subs(sol_coeff, 1)
print(final_expression1)
# get initial value
monom_subs = {f"E({monom})":monom for monom in monoms}
initial_value_dict = {var: recurrence_builder.get_initial_value(var) for var in vars}
initial_value = final_expression1.subs(monom_subs).subs(initial_value_dict).simplify()

final_expression1= final_expression1 - initial_value
# Use Expected value function of sympy - this allows us to use solve and stuff like this. Unfortunately incompatible with most of polar.
for monom in monoms:
    final_expression1 = final_expression1.subs(f"E({monom})", Expexted(monom))

goal_monom = Expexted(sympify('k**2'))

print(final_expression1.expand().simplify())
print(final_expression1.subs(sympify('k'), sympify('(k-1)')).expand().simplify())

res = solve(final_expression1, goal_monom)
print(res)

res1 = solve (final_expression1.subs(sympify('k'), sympify('(k-1)')).expand().simplify(), goal_monom)
print(res1)
pass