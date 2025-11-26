"""
This file provides functionality, to synthesize polynomials of random variables, which's expectation is itself.
More concrete, we find a p[\bar{x}_t], s.t. 

    E(p[\bar{x}_{t}] | F) = p[\bar{x}_{t+1}]
"""

from functools import cache, reduce
from itertools import product
from typing import Dict
from sympy import Expr, Piecewise, Symbol, simplify, solve, symbols, sympify

from invariants.invariant_ideal import InvariantIdeal


C = symbols('_ConstVal_')

class ExpectationMapBuilder():
    def __init__(self, recurrence_dict, deterministic_vars):
        self.recurrence_dict = recurrence_dict
        self.deterministic_vars = deterministic_vars

    def _add_constant_factor(self, expr):
        """replace the constant part of a polynomial with the constant part multiplied by C, to later force elimination"""
        constant_part = expr if expr.is_number else next((ele for ele in expr.args if ele.is_number), 0)

        return (expr-constant_part+constant_part*C).simplify()

    def _get_coeff(self, expr, monom):
        for term in expr.as_ordered_terms():
            if term.has(monom):
                factors = term.as_coeff_mul()
                coeff, rest = factors[0], factors[1]
                # Check if the rest is exactly (y,) -> means y alone
                if rest == sympify(monom).as_coeff_mul()[1]:
                    return coeff
        return 0

    def _build_equation_system(self, recurrences:Dict, goal_var, deterministic_vars):
        vars = set(recurrences.keys())
        var_to_coeff = {var:Symbol(f'c{i}') for i,var in enumerate(vars)}

        vars_to_eliminate = set(term.as_coeff_Mul()[1] for expr in recurrences.values() for term in expr.as_ordered_terms())

        equations = [var_to_coeff[goal_var] - 1]
        for var in vars_to_eliminate:
            expr = 0 if var not in var_to_coeff or len(set(var.free_symbols) - deterministic_vars)==0 else -var_to_coeff[var] 
            for monom, expression_E1 in recurrences.items():
                var_coeff =self._get_coeff(expression_E1,var)
                expr += var_coeff*var_to_coeff[monom]
            equations.append(expr)
        return equations, var_to_coeff


    def _solve_equation_system(self, equations, coeffs):
        def solution_to_assignments(sol_coeffs):    
            for coeff in coeffs:
                if coeff in sol_coeffs.keys():
                    continue
                elif any(s.has(coeff) for s in sol_coeffs.values()):
                    sol_coeffs[coeff] = coeff
                else:
                    # all coefficients not appearing in the solution can safely be set to zero
                    sol_coeffs[coeff] = 0

            return sol_coeffs

        sol_coeffs = solve(equations, coeffs, dict=True)
        if sol_coeffs is None:
            return []
        return [solution_to_assignments(c) for c in sol_coeffs]



    def _get_axis_cut_solutions(self, solutions:Dict[Expr, Expr]):
        """Given a general solution to a system of linear equations, this method returns all concrete solutions,
        which (locally) maximize the number of variables set to 0.
        
        Args:
            solutions (_type_): The solutions returned by solve for a multivariate system of equations
        """
        # get the variables which can be set to 0
        choice_vars = set()
        for k,v in solutions.items():
            if k == v:
                continue
        # expression is of form x: y+a (x,y are vars, a is some constant)
            # then we can either set x=0 and y=-a, or y=0, x=a
            if len(v.free_symbols)==1:
                choice_vars.add(k)
                break
        
        # this gives the variables, wich are "more underdetermined" an advantage
        if len(choice_vars)==0:
            for k,v in solutions.items():
                if k == v:
                    continue
                if len(v.free_symbols)>=1:
                    choice_vars = choice_vars.union({f for f in v.free_symbols if solutions[f] == f})

    

        # no more choices, set all not determined vars to 0
        if len(choice_vars) == 0:
            sol = solutions.copy()
            for k in sol:
                if sol[k] == k:
                    sol[k]=0
                elif len(sol[k].free_symbols)==0:
                    pass
                else:
                    raise Exception("this should not occur in an underspecified system of equations (probably some kind of circularity)."+\
                                    "Is this input returned from linsolve?")
            yield sol

        for choice_var in choice_vars:
            sol = solutions.copy()
            
            if sol[choice_var] != choice_var: #(sign chosen to be consistent, wlog) this handles the case: sol[choice_var] = other_var - a
                assert len(sol[choice_var].free_symbols)==1
                other_var = sol[choice_var].free_symbols.pop()
                a = solve(sol[choice_var], other_var)[0]
                sol[other_var] = a
                for k in sol:
                    sol[k]=sol[k].subs(other_var, a)
            for k in sol:
                sol[k]=sol[k].subs(choice_var, 0)
            
            for solution in self._get_axis_cut_solutions(sol):
                yield solution

    def _filter_similar_expectation_maps(self, maps):
        maps_filtered = set()
        for map in maps:
            redundant = False
            for m in maps_filtered:
                comparison = simplify(map/m)
                if comparison.is_number:
                    redundant = True
                    break
            if not redundant:
                maps_filtered.add(map)
        return list(maps_filtered)

    # TODO: cache this function
    @cache
    def get_expectation_maps(self, goal_var):
        # Note the "rec-monom". We do this, as we want to find the coefficient of each monomial in the poly p.
        recurrences = {monom: Piecewise((self._add_constant_factor(rec - (monom if len(set(monom.free_symbols) - self.deterministic_vars)==0 else 0)), True)) for monom,rec in self.recurrence_dict.items()}
        
        # The expression map can be constructed from an invariant ideal
        # invariant_ideal = InvariantIdeal(recurrences)
        # basis = list(invariant_ideal.compute_basis())
        # print(basis)

        # The basis is not yet a desired expression maps. We need to find an expression, where the actual random variables are cancelled out.
        # We have to do this, difference of E(p) and p must be zero NOT ONLY in expectation, but actually equal to the scalar 0. 
        # This is done by solving a linear system of equations. TODO: investigate if this could be replaced by monomial ordering in basis computation
        equations, var_to_coeff = self._build_equation_system(recurrences, goal_var, self.deterministic_vars)
        var_to_coeff_list = list(var_to_coeff.items())
        solutions = self._solve_equation_system(equations, [v for (_,v) in var_to_coeff_list])



        maps = set()
        for solution in solutions:
            # TODO: the following contains many duplicates - get rid of them, either in the called function (probably hard) or afterwards
            axis_cut_solutions = list(self._get_axis_cut_solutions(solution))


            # Build the linear combination
            final_expression = 0
            for expr, coeff in var_to_coeff_list:
                final_expression+= Symbol(f"E({expr})")*coeff
            for axis_cut_solution in axis_cut_solutions:
                maps.add(final_expression.subs(axis_cut_solution).simplify())
        return self._filter_similar_expectation_maps(maps)
