"""
This file provides functionality, to synthesize polynomials of random variables, which's expectation is itself.
More concrete, we find a p[\bar{x}_t], s.t. 

    E(p[\bar{x}_{t}] | F) = p[\bar{x}_{t+1}]
"""

from functools import cache, reduce
from itertools import product
from typing import Dict
import numpy as np
from sympy import S, Add, Expr, Float, Function, Piecewise, Symbol, linear_eq_to_matrix, nsimplify, primitive, rem, simplify, solve, symbols, sympify

from extension_ost.square_extraction import reformulate_with_squares
from invariants.invariant_ideal import InvariantIdeal
from ortools.linear_solver import pywraplp


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

        equations = []
        for var in vars_to_eliminate:
            expr = 0 if var not in var_to_coeff or len(set(var.free_symbols) - deterministic_vars)==0 else -var_to_coeff[var] 
            for monom, expression_E1 in recurrences.items():
                var_coeff =self._get_coeff(expression_E1,var)
                expr += var_coeff*var_to_coeff[monom]
            equations.append(expr)
        return equations, var_to_coeff

    def _get_axis_cut_solutions_v3(self, solutions):
        ancestor_vars = set()
        for k, v in solutions.items():
             if k!=v:
                 ancestor_vars = ancestor_vars.union(v.free_symbols)
        for k in solutions:
            if k not in ancestor_vars and k==solutions[k]:
                solutions[k] = S.Zero
        
        for solution in self._get_axis_cut_solutions_v3_recurse(solutions):
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
    
    def filter_unique_primitives(self, expressions):
        unique_map = {}
        
        for expr in expressions:
            if expr == 0:
                unique_map[0] = 0
                continue
            if expr is None:
                continue

            # as_content_primitive returns a tuple: (scalar_factor, simplified_expr)
            content, primitive = expr.as_content_primitive()
            
            if primitive not in unique_map:
                unique_map[primitive] = expr
                
        return list(unique_map.values())


    def get_sparse_expectation_maps(self, goal_var):
        recurrences = {monom: Piecewise((self._add_constant_factor(rec - (monom if len(set(monom.free_symbols) - self.deterministic_vars)==0 else 0)), True)) for monom,rec in self.recurrence_dict.items()}
        

        equations0, var_to_coeff = self._build_equation_system(recurrences, goal_var, self.deterministic_vars)
        equations = [primitive(eq)[1] for eq in equations0]
        coeff_to_var = {v:k for k,v in var_to_coeff.items()}

        variables = list(set().union(*[v.free_symbols for v in  var_to_coeff.values()]))
        A_sym, b_sym = linear_eq_to_matrix(equations,variables)
        A_num = np.array(A_sym).astype(float)
        b_num = np.array(b_sym).astype(float).flatten()
        
        solver = pywraplp.Solver.CreateSolver('SCIP')
        assert solver, "solver initialization failed"
        infinity = solver.infinity()

        x_vars = [solver.IntVar(-infinity, infinity, str(v)) for v in variables]
        
        is_nonzero = [solver.IntVar(1 if v == var_to_coeff[goal_var] else 0, 1, f'nz_{v}_{1 if v == var_to_coeff[goal_var] else 0}') for v in variables]
        

        for r in range(len(b_num)):
            constraint = solver.RowConstraint(b_num[r], b_num[r]) # lhs <= expr <= rhs (strict equality)
            for c in range(len(variables)):
                constraint.SetCoefficient(x_vars[c], A_num[r][c])

        # Big-M constraints linking x to binary indicators
        # If is_nonzero[i] == 0, then -0 <= x[i] <= 0  (x forced to zero)
        # If is_nonzero[i] == 1, then -M <= x[i] <= M  (x allowed to be anything)
        for i in range(len(variables)):
            # x[i] <= M * is_nonzero[i]
            c1 = solver.RowConstraint(-infinity, 0)
            c1.SetCoefficient(x_vars[i], 1)
            c1.SetCoefficient(is_nonzero[i], -10000)
            
            # x[i] >= -M * is_nonzero[i]  ->  x[i] + M*is_nonzero[i] >= 0
            c2 = solver.RowConstraint(0, infinity)
            c2.SetCoefficient(x_vars[i], 1)
            c2.SetCoefficient(is_nonzero[i], 10000)

        for i in range(len(variables)):
            # x[i] <= M * is_nonzero[i]
            c1 = solver.RowConstraint(-infinity, 0)
            c1.SetCoefficient(x_vars[i], -1)
            c1.SetCoefficient(is_nonzero[i], 1)
            
            # x[i] >= -M * is_nonzero[i]  ->  x[i] + M*is_nonzero[i] >= 0
            c2 = solver.RowConstraint(0, infinity)
            c2.SetCoefficient(x_vars[i], 1)
            c2.SetCoefficient(is_nonzero[i], -1)

        # minimize nonzeros
        objective = solver.Objective()
        for b_var in is_nonzero:
            objective.SetCoefficient(b_var, 1)
        objective.SetMinimization()

        status = solver.Solve()

        if status not in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            print("OR-Tools could not find an optimal solution.")
            return None

        martingale_expr = S.Zero
        for i, sym in enumerate(variables):
            val = x_vars[i].solution_value()
            # Clean up floating point noise
            if abs(val) < 1e-10: # is zero
                continue
            martingale_expr += nsimplify(Float(val), rational=True)*Symbol(f"E({coeff_to_var[sym]})")

        martingale_no_exp_rec = simplify(martingale_expr.subs({Symbol(f"E({monom})"): v for monom,v in recurrences.items()}))
        assert martingale_no_exp_rec == S.Zero, "Numerical error caused wrong result in martingale map synthesis"

        return martingale_expr
