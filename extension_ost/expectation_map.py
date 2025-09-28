"""
This file provides functionality, to synthesize polynomials of random variables, which's expectation is itself.
More concrete, we find a p[\bar{x}_t], s.t. 

    E(p[\bar{x}_{t}] | F) = p[\bar{x}_{t+1}]
"""

from functools import reduce
from itertools import product
from typing import Dict
from sympy import Piecewise, Symbol, solve, symbols, sympify

from invariants.invariant_ideal import InvariantIdeal


C = symbols('_ConstVal_')

def _add_constant_factor(expr):
    """replace the constant part of a polynomial with the constant part multiplied by C, to later force elimination"""
    constant_part = expr if expr.is_number else next((ele for ele in expr.args if ele.is_number), 0)

    return (expr-constant_part+constant_part*C).simplify()

def _get_coeff(expr, monom):
    for term in expr.as_ordered_terms():
        if term.has(monom):
            factors = term.as_coeff_mul()
            coeff, rest = factors[0], factors[1]
            # Check if the rest is exactly (y,) -> means y alone
            if rest == sympify(monom).as_coeff_mul()[1]:
                return coeff
    return 0

def _build_equation_system(recurrences:Dict, goal_var, deterministic_vars):
    vars = set(recurrences.keys())
    var_to_coeff = {var:Symbol(f'c{i}') for i,var in enumerate(vars)}

    vars_to_eliminate = set(term.as_coeff_Mul()[1] for expr in recurrences.values() for term in expr.as_ordered_terms())

    equations = [var_to_coeff[goal_var] - 1]
    for var in vars_to_eliminate:
        expr = 0 if var not in var_to_coeff or len(set(var.free_symbols) - deterministic_vars)==0 else -var_to_coeff[var] 
        for monom, expression_E1 in recurrences.items():
            var_coeff =_get_coeff(expression_E1,var)
            expr += var_coeff*var_to_coeff[monom]
        equations.append(expr)
    return equations, var_to_coeff


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


def get_expectation_maps(recurrence_dict, goal_var, deterministic_vars):
    # Note the "rec-monom". We do this, as we want to find the coefficient of each monomial in the poly p.
    recurrences = {monom: Piecewise((_add_constant_factor(rec - (monom if len(set(monom.free_symbols) - deterministic_vars)==0 else 0)), True)) for monom,rec in recurrence_dict.items()}
    
    # The expression map can be constructed from an invariant ideal
    # invariant_ideal = InvariantIdeal(recurrences)
    # basis = list(invariant_ideal.compute_basis())
    # print(basis)

    # The basis is not yet a desired expression maps. We need to find an expression, where the actual random variables are cancelled out.
    # We have to do this, difference of E(p) and p must be zero NOT ONLY in expectation, but actually equal to the scalar 0. 
    # This is done by solving a linear system of equations. TODO: investigate if this could be replaced by monomial ordering in basis computation
    equations, var_to_coeff = _build_equation_system(recurrences, goal_var, deterministic_vars)
    var_to_coeff_list = list(var_to_coeff.items())
    solutions = _solve_equation_system(equations, [v for (_,v) in var_to_coeff_list])



    # We take every possible solution. TODO: check if this is necessary
    maps = []
    for solution in solutions:
        free_vars = {coeff:[] for (coeff, coeff1) in solution if coeff==coeff1}
        for (_,equation) in solution:
            for free_var in free_vars:
                if equation.has(free_var):
                    solved_solutions = solve(equation, free_var)
                    for sol in solved_solutions:
                        free_vars[free_var].append(sol)

        # Build the linear combination
        final_expression = 0
        for expr, (_, coeff) in zip([k for (k,_) in var_to_coeff_list], solution):
            final_expression+= Symbol(f"E({expr})")*coeff
        
        free_vars = free_vars.items()
        free_var_names = [f[0] for f in free_vars]
        substitutions = [f[1] for f in free_vars]

        substitution_combinations = [list(x) for x in product(*substitutions)]

        for substitution_combination in substitution_combinations:
            final_expression_substituted = final_expression
            for var, sub in zip(free_var_names, substitution_combination):
                final_expression_substituted = final_expression_substituted.subs(var, sub)

            maps.append(final_expression_substituted.simplify())
    return maps
