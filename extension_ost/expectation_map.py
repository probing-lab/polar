"""
This file provides functionality, to synthesize polynomials of random variables, which's expectation is itself.
More concrete, we find a p[\bar{x}_t], s.t. 

    E(p[\bar{x}_{t}] | F) = p[\bar{x}_{t+1}]
"""

from functools import reduce
from sympy import Piecewise, Symbol, solve, symbols

from invariants.invariant_ideal import InvariantIdeal


C = symbols('_ConstVal_')

def _add_constant_factor(expr):
    """replace the constant part of a polynomial with the constant part multiplied by C, to later force elimination"""
    constant_part = expr if expr.is_number else next((ele for ele in expr.args if ele.is_number), 0)

    return (expr-constant_part+constant_part*C).simplify()


def _build_equation_system(basis, whitelist):
    vars = reduce(lambda symbols, expr: symbols.union(expr.free_symbols),basis, set())
    vars_to_eliminate = vars.difference(whitelist)
    coeffs = list(symbols(f'c0:{len(basis)}'))
    equations = []
    for var in vars_to_eliminate:
        expr = 0
        for be, base_coeff in zip(basis, coeffs):
            var_coeff = be.coeff(var, 1)
            expr += var_coeff*base_coeff
        equations.append(expr)
    return equations, coeffs


def _solve_equation_system(equations, coeffs):
    def solution_to_assignments(sol_coeffs):    
        for coeff in coeffs:
            if coeff in sol_coeffs.keys():
                continue
            elif any(s.has(coeff) for s in sol_coeffs.values()):
                sol_coeffs[coeff] = coeff
            else:
                # all coefficients not appearing in the solution can safely be set to zero
                sol_coeffs[coeff] = 0

        coeffs_sorted =sorted(list(sol_coeffs.items()), key=lambda x:str(x[0]))
        return coeffs_sorted

    sol_coeffs = solve(equations, coeffs, dict=True)
    if sol_coeffs is None:
        return []
    return [solution_to_assignments(c) for c in sol_coeffs]


def get_expectation_maps(recurrence_dict):
    # Note the "rec-monom". We do this, as we want to find the coefficient of each monomial in the poly p.
    recurrences = {f"E({monom})": Piecewise((_add_constant_factor(rec-monom), True)) for monom,rec in recurrence_dict.items()}
    
    # The expression map can be constructed from an invariant ideal
    invariant_ideal = InvariantIdeal(recurrences)
    basis = list(invariant_ideal.compute_basis())
    print(basis)

    # The basis is not yet a desired expression maps. We need to find an expression, where the actual random variables are cancelled out.
    # We have to do this, difference of E(p) and p must be zero NOT ONLY in expectation, but actually equal to the scalar 0. 
    # This is done by solving a linear system of equations. TODO: investigate if this could be replaced by monomial ordering in basis computation
    equations, coeffs = _build_equation_system(basis, set([Symbol(k) for k in recurrences.keys()]))
    print(equations)
    print(coeffs)
    solutions = _solve_equation_system(equations, coeffs)

    # We take every possible solution. TODO: check if this is necessary
    maps = []
    for solution in solutions:
        # Build the linear combination
        final_expression = 0
        for expr, (_, coeff) in zip(basis, solution):
            final_expression+= expr*coeff
        
        # Replace the coefficients left with 1 (as they are underspecified)
        for (coeff, coeff_sol) in solution:
            if coeff == coeff_sol:
                final_expression = final_expression.subs(coeff, 1)

        maps.append(final_expression.simplify())
    return maps
