"""This algorithm continuously tries to obtain new bounds as long as possible.

Note that in the current implementation, there needs to be an iter-variable named "k" present in the loop to analyze.

TODO: check if positivity (of symbols in bounds) is a necessary requirement (i think so)
"""
from typing import Dict, List

from sympy import Add, Expr, Interval, Mul, Symbol, oo, simplify, sympify, solve

from extension_ost.helpers import Expexted

# ITER_VAR = Symbol("k", integer=True, positive=True)

class BoundStore:
    def __init__(self):
        self.upper_bounds = {} # TODO: consider upgrading to multiple different bounds (i.e. list of bounds per expression)
        self.lower_bounds = {}

    def add_upper_bound(self, expression, upper_bound):
        self.upper_bounds[expression] = upper_bound
        
    def add_lower_bound(self, expresssion, lower_bounds):
        self.lower_bounds[expresssion] = lower_bounds

    def _get_upper_bound_for_expression(self, expression:Expr):
        if expression.is_Number:
            return expression
        if expression in self.upper_bounds:
            return self.upper_bounds[expression]
        if isinstance(expression, Add):
            parts =[self._get_upper_bound_for_expression(arg) for arg in expression.args]
            return Add(*parts)
        if isinstance(expression, Mul): # Case split based on signs of bounds
            # TODO: Currently only extract numbers from multiplication
            number_args = [arg for arg in expression.args if arg.is_Number]
            if len(number_args)==0:
                raise NotImplementedError("Can currently only split if one part of multiplication is number")
            # evaluate to check sign
            coeff:Expr = simplify(Mul(*number_args))
            if coeff.is_positive:
                return coeff*self._get_upper_bound_for_expression(Mul(*[arg for arg in expression.args if not arg.is_Number]))
            if coeff.is_negative:
                return coeff*self._get_lower_bound_for_expression(Mul(*[(arg) for arg in expression.args if not arg.is_Number]))

        if isinstance(expression, Expexted):
            inner_expr = expression.args[0]
            if isinstance(inner_expr, Mul):
                for i in range(inner_expr.args):
                    # TODO: This could be made more efficient by considering a powerset (and its inverse), instead of recursive calls
                    # TODO: More Cases are possible
                    hard_bounded_expr = inner_expr.args
                    other_expr = Mul(*[arg for j,arg in enumerate(inner_expr.args) if j!= i])

                    hb_upper_bound = self._get_upper_bound_for_expression(hard_bounded_expr)
                    if not hb_upper_bound.is_finite:
                        continue

                    oexpr_hard_lb = self._get_lower_bound_for_expression(other_expr)
                    if not oexpr_hard_lb.is_positive:
                        continue
                    oexpr_ub = self._get_upper_bound_for_expression(Expexted(other_expr))
                    if oexpr_ub.is_finite:
                        return Mul(hb_upper_bound, oexpr_ub)

        return oo
    
    def _get_lower_bound_for_expression(self, expression: Expr):
        if expression.is_Number:
            return expression
        if expression in self.lower_bounds:
            return self.lower_bounds[expression]
        if isinstance(expression, Add):
            return Add([self._get_lower_bound_for_expression(arg) for arg in expression.args])
        if isinstance(expression, Mul): # Case split based on signs of bounds
            # TODO: Currently only extract numbers from multiplication
            number_args = [arg for arg in expression.args if arg.is_Number]
            if len(number_args)==0:
                raise NotImplementedError("Can currently only split if one part of multiplication is number")
            # evaluate to check sign
            coeff:Expr = simplify(Mul(number_args))
            if coeff.is_positive:
                return coeff*self._get_lower_bound_for_expression(Mul(arg for arg in expression.args if not arg.is_Number))
            if coeff.is_negative:
                return coeff*self._get_upper_bound_for_expression(Mul((arg) for arg in expression.args if not arg.is_Number))

        if isinstance(expression, Expexted):
            # TODO: Consider this case
            pass

        return oo
