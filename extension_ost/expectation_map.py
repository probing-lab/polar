"""
This file provides functionality, to synthesize polynomials of random variables, which's expectation is itself.
More concrete, we find a p[\bar{x}_t], s.t. 

    E(p[\bar{x}_{t}] | F) = p[\bar{x}_{t+1}]
"""

from functools import cache, reduce
from itertools import product
from typing import Dict
from sympy import S, Add, Expr, Function, Piecewise, Symbol, linear_eq_to_matrix, rem, simplify, solve, symbols, sympify

from extension_ost.square_extraction import reformulate_with_squares
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

    def _propagate_value(self, solutions: Dict[Expr, Expr], k: Expr, v: Expr):
        assert len(v.free_symbols)<=1
        for k1 in solutions:
            if k not in solutions[k1].free_symbols:
                continue
            solutions[k1] = solutions[k1].subs(k,v)
            if solutions[k1].is_number:
                self._propagate_value(solutions, k1, solutions[k1])
            if len(solutions[k1].free_symbols)==1 and rem(solutions[k1], solutions[k1].free_symbols.pop()) == 0:
                self._propagate_value(solutions, k1, solutions[k1])   

    def _get_axis_cut_solutions_v3_recurse(self, solutions: Dict[Expr, Expr]):
        progress = False
        for k, v in solutions.items():
            if len(v.free_symbols) == 1:
                # set it to zero
                progress = True
                if k == v:
                    sol = solutions.copy()
                    self._propagate_value(sol, k, S.Zero)
                    for solution in self._get_axis_cut_solutions_v3_recurse(sol):
                        yield solution
                else:
                    sol = solutions.copy()
                    sol[k] = S.Zero
                    self._propagate_value(sol, k, S.Zero)
                    k1 = v.free_symbols.pop()
                    v1 = solve(v, k1)[0]
                    self._propagate_value(sol,k1, v1)
                    for solution in self._get_axis_cut_solutions_v3_recurse(sol):
                        yield solution
        if not progress:
            assert all(len(v.free_symbols)==0 for v in solutions.values())
            yield solutions

    def _get_axis_cut_solutions_v3(self, solutions):
        ancestor_vars = set()
        for k, v in solutions.items():
             if len(v.free_symbols)>1:
                 ancestor_vars = ancestor_vars.union(v.free_symbols)
        for k in solutions:
            if k not in ancestor_vars and k==solutions[k]:
                solutions[k] = 0
        
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

            # as_content_primitive returns a tuple: (scalar_factor, simplified_expr)
            # e.g., 2*f(x) + 4*f(y)  ->  (2, f(x) + 2*f(y))
            # e.g., -f(x) - 2*f(y)   ->  (-1, f(x) + 2*f(y))
            content, primitive = expr.as_content_primitive()
            
            # We only care about the 'primitive' part as the dictionary key
            if primitive not in unique_map:
                unique_map[primitive] = expr
                
        return list(unique_map.values())

    def get_sparse_basis(self, expressions):

        variables = set()
        for expr in expressions:
            variables.update(expr.free_symbols)
        
        # Sort for deterministic matrix columns (A, B, C...)
        # We sort by the string representation of the symbol
        variables_list = sorted(list(variables), key=lambda s: s.name)

        # 2. Build the Matrix (The Coefficient Matrix)
        # rows = expressions, columns = variables
        matrix_A, _ = linear_eq_to_matrix(expressions, variables_list)

        # 3. Compute RREF (Reduced Row Echelon Form)
        # This performs Gaussian elimination to zero out as much as possible
        # and remove dependent rows.
        rref_matrix, pivot_indices = matrix_A.rref()

        # 4. Reconstruct the simplified expressions
        simplified_exprs = []
        rows, cols = rref_matrix.shape
        
        for i in range(rows):
            # Reconstruct the expression from the row coefficients
            # dot product: row[i] * variables_list
            new_expr = sum(rref_matrix[i, j] * variables_list[j] for j in range(cols))
            
            # Filter out rows that became completely zero (the redundant ones)
            if new_expr != 0:
                simplified_exprs.append(new_expr)

        return simplified_exprs

    def get_shortest_basis(self, expressions):
        # 1. Identify all variables across all expressions for matrix construction
        #    (Using free_symbols since you have symbols like f(x1))
        all_syms = set()
        for e in expressions:
            all_syms.update(e.free_symbols)
        variables = sorted(list(all_syms), key=lambda s: s.name)

        # 2. Sort expressions by "Complexity" (Number of terms)
        #    Add.make_args splits 'a + b' into (a, b). 
        #    We prefer expressions with fewer terms.
        #    Secondary sort by string length ensures 'x' comes before 'y' (cosmetic)
        sorted_exprs = sorted(expressions, key=lambda e: (len(Add.make_args(e)), str(e)))

        basis = []
        current_rank = 0

        for expr in sorted_exprs:
            # Handle zero expression
            if expr == 0:
                continue
                
            # 3. Test: Does adding this expression increase the rank?
            candidate_basis = basis + [expr]
            
            # Build matrix of the candidate basis
            mat, _ = linear_eq_to_matrix(candidate_basis, variables)
            new_rank = mat.rank()
            
            # 4. If rank increases, this expression contains NEW info. Keep it.
            #    Since we sorted by length, we are guaranteed to be keeping 
            #    the shortest possible version of this information.
            if new_rank > current_rank:
                basis.append(expr)
                current_rank = new_rank

        return basis

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
            axis_cut_solutions = list(self._get_axis_cut_solutions_v3(solution))

            unique_axis_cut_solutions = [dict(t) for t in {frozenset(d.items()) for d in axis_cut_solutions}]
            # Build the linear combination
            final_expression = 0
            for expr, coeff in var_to_coeff_list:
                final_expression+= Symbol(f"E({expr})")*coeff
            for axis_cut_solution in unique_axis_cut_solutions:
                maps.add(final_expression.subs(axis_cut_solution).simplify())
        return maps
