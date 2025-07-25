"""This algorithm continuously tries to obtain new bounds as long as possible.

Note that in the current implementation, there needs to be an iter-variable named "k" present in the loop to analyze.

TODO: check if positivity (of symbols in bounds) is a necessary requirement (i think so)
"""
from itertools import combinations
from typing import Dict, List

from sympy import Add, Expr, Interval, Mul, Symbol, oo, simplify, sympify, solve, Pow

from extension_ost.helpers import Expexted

# ITER_VAR = Symbol("k", integer=True, positive=True)

class BoundStore:
    def __init__(self):
        self.upper_bounds = {} # TODO: consider upgrading to multiple different bounds (i.e. list of bounds per expression)
        self.lower_bounds = {}
        self.initials = set()

    def add_upper_bound(self, expression, upper_bound):
        self.upper_bounds[expression] = upper_bound
        
    def add_lower_bound(self, expresssion, lower_bounds):
        self.lower_bounds[expresssion] = lower_bounds

    def add_initial(self, symbol):
        self.initials.add(symbol)

    def _is_initial(self, expression:Expr):
        return len(expression.free_symbols-self.initials)==0 and not expression.has(oo)
    
    def _is_finite(self, expression: Expr):
        return expression.is_finite or self._is_initial(expression)

    def _get_upper_bound_for_expression(self, expression:Expr):
        if expression.is_Number:
            return expression
        if self._is_initial(expression):
            return expression
        if expression in self.upper_bounds:
            return self.upper_bounds[expression]
        if isinstance(expression, Add):
            parts =[self._get_upper_bound_for_expression(arg) for arg in expression.args]
            return Add(*parts)
        if isinstance(expression, Mul): # Case split based on signs of bounds
            # TODO: Currently only extract numbers from multiplication
            number_args = [arg for arg in expression.args if arg.is_Number]
            if len(number_args)>0:
                # evaluate to check sign
                coeff:Expr = simplify(Mul(*number_args))
                if coeff.is_nonnegative:
                    return coeff*self._get_upper_bound_for_expression(Mul(*[arg for arg in expression.args if not arg.is_Number]))
                if coeff.is_nonpositive:
                    lb = self._get_lower_bound_for_expression(Mul(*[(arg) for arg in expression.args if not arg.is_Number]))
                    return coeff*lb
            else:
                # TODO: this is suboptimal, as below
                for i in range(len(expression.args)):
                    first_expr = expression.args[i]
                    second_expr = Mul(*[arg for j,arg in enumerate(expression.args) if j!=i])

                    first_lb:Expr = self._get_lower_bound_for_expression(first_expr)
                    second_lb:Expr = self._get_lower_bound_for_expression(second_expr)

                    first_ub:Expr = self._get_upper_bound_for_expression(first_expr)
                    second_ub:Expr = self._get_upper_bound_for_expression(second_expr)

                    if first_lb.is_nonnegative and second_lb.is_nonnegative and self._is_finite(first_ub) and self._is_finite(second_ub):
                        return first_ub*second_ub
                    if first_ub.is_nonpositive and second_ub.is_nonpositive and self._is_finite(first_lb) and self._is_finite(second_lb):
                        return first_lb*second_lb

        if isinstance(expression, Pow):
            base = expression.args[0]
            exponent = expression.args[1]
            
            base_lb:Expr = self._get_lower_bound_for_expression(base)
            base_ub:Expr = self._get_upper_bound_for_expression(base)

            if exponent.is_even:
                if base_ub.is_nonpositive and self._is_finite(base_lb):
                    return Pow(base_lb, exponent)
                if base_lb.is_nonnegative and self._is_finite(base_ub):
                    return Pow(base_ub, exponent)
            else:
                if base_ub.is_nonpositive:
                    if self._is_finite(base_ub):
                        return Pow(base_ub, exponent)
                    return 0
                if base_lb.is_nonnegative and self._is_finite(base_ub):
                    return Pow(base_ub, exponent)

        if isinstance(expression, Expexted):
            inner_expr = expression.args[0]
            sharp_bound = self._get_upper_bound_for_expression(inner_expr)
            if self._is_finite(sharp_bound):
                return sharp_bound
            if isinstance(inner_expr, Mul):
                for i in range(len(inner_expr.args)):
                    # TODO: This could be made more efficient by considering a powerset (and its complement), instead of recursive calls
                    # TODO: More Cases are possible
                    hard_bounded_expr = inner_expr.args[i]
                    other_expr = Mul(*[arg for j,arg in enumerate(inner_expr.args) if j!= i])

                    hb_upper_bound = self._get_upper_bound_for_expression(hard_bounded_expr)
                    if not self._is_finite(hb_upper_bound):
                        continue

                    oexpr_hard_lb = self._get_lower_bound_for_expression(other_expr)
                    if not oexpr_hard_lb.is_nonnegative:
                        continue
                    oexpr_ub = self._get_upper_bound_for_expression(Expexted(other_expr))
                    if self._is_finite(oexpr_ub):
                        return Mul(hb_upper_bound, oexpr_ub)

        elif expression.is_nonpositive:
            return 0
        return oo
    
    def __two_partitions(self, s):
        s = set(s)
        seen = set()
        return [
            (a := set(c), s - a)
            for r in range(1, len(s)//2 + 1)
            for c in combinations(s, r)
            if (key := frozenset([frozenset(c), frozenset(s - set(c))])) not in seen and not seen.add(key)
        ]   
    
    def _get_lower_bound_for_expression(self, expression: Expr):
        if expression.is_Number:
            return expression
        if self._is_initial(expression):
            return expression
        if expression in self.lower_bounds:
            return self.lower_bounds[expression]
        if isinstance(expression, Add):
            parts = [self._get_lower_bound_for_expression(arg) for arg in expression.args]
            return Add(*parts)
        if isinstance(expression, Mul): # Case split based on signs of bounds
            # TODO: Currently only extract numbers from multiplication
            number_args = [arg for arg in expression.args if arg.is_Number]
            if len(number_args)!=0:
                # evaluate to check sign
                coeff:Expr = simplify(Mul(*number_args))
                if coeff.is_nonnegative:
                    return coeff*self._get_lower_bound_for_expression(Mul(*[arg for arg in expression.args if not arg.is_Number]))
                if coeff.is_nonpositive:
                    return coeff*self._get_upper_bound_for_expression(Mul(*[(arg) for arg in expression.args if not arg.is_Number]))
            else:
                 for a_expr, b_expr in self.__two_partitions(expression.args):
                     a_lb = self._get_lower_bound_for_expression(Mul(*a_expr))
                     b_lb = self._get_lower_bound_for_expression(Mul(*b_expr))
                     if a_lb.is_nonnegative and self._is_finite(a_lb) and b_lb.is_nonnegative and self._is_finite(b_lb):
                         return a_lb*b_lb
        if isinstance(expression, Pow):
            base = expression.args[0]
            exponent = expression.args[1]
            
            base_lb:Expr = self._get_lower_bound_for_expression(base)
            base_ub:Expr = self._get_upper_bound_for_expression(base)

            if exponent.is_even:
                if base_ub.is_nonpositive and self._is_finite(base_ub):
                    return Pow(base_ub, exponent)
                if base_lb.is_nonnegative and self._is_finite(base_lb):
                    return Pow(base_lb, exponent)
                return 0
            else:
                if base_ub.is_nonpositive and self._is_finite(base_lb):
                    return Pow(base_lb, exponent)
                if base_lb.is_nonnegative and self._is_finite(base_lb):
                    return Pow(base_lb, exponent)
                return 0

        if isinstance(expression, Expexted):
            inner_expr = expression.args[0]
            sharp_bound = self._get_lower_bound_for_expression(inner_expr)
            if self._is_finite(sharp_bound):
                return sharp_bound
            
            if isinstance(inner_expr, Mul):
                for i in range(len(inner_expr.args)):
                    # TODO: This could be made more efficient by considering a powerset (and its complement), instead of recursive calls
                    # TODO: More Cases are possible - this is just to get the minimum example working
                    hard_bounded_expr = inner_expr.args[i]
                    other_expr = Mul(*[arg for j,arg in enumerate(inner_expr.args) if j!= i])

                    hb_lower_bound = self._get_lower_bound_for_expression(hard_bounded_expr)
                    if not self._is_finite(hb_lower_bound):
                        continue

                    oexpr_hard_lb = self._get_lower_bound_for_expression(other_expr)
                    if not oexpr_hard_lb.is_nonnegative or not self._is_finite(oexpr_hard_lb):
                        continue
                    
                    if hb_lower_bound.is_nonpositive:
                        oexpr_ub = self._get_upper_bound_for_expression(Expexted(other_expr))
                        if self._is_finite(oexpr_ub) and oexpr_ub.is_nonnegative:
                            return Mul(*[hb_lower_bound, oexpr_ub]) # redundant case - needs to be sharpened
            pass
        elif expression.is_nonnegative:
            return 0

        return oo
