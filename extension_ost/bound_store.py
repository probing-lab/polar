"""This algorithm continuously tries to obtain new bounds as long as possible.

Note that in the current implementation, there needs to be an iter-variable named "k" present in the loop to analyze.

TODO: check if positivity (of symbols in bounds) is a necessary requirement (i think so)
"""
from collections import defaultdict
from itertools import combinations, product
from typing import Dict, List

from sympy import Add, Expr, Interval, Mul, Symbol, oo, simplify, sympify, solve, Pow

from extension_ost.helpers import Expexted

# ITER_VAR = Symbol("k", integer=True, positive=True)

class BoundStore:
    def __init__(self):
        self.upper_bounds:Dict[Expr, List[Expr]] =  defaultdict(list)
        self.lower_bounds:Dict[Expr, List[Expr]] =  defaultdict(list)
        self.initials = set()

    def add_upper_bound(self, expression, upper_bound):
        self.upper_bounds[expression].append(upper_bound)
        
    def add_lower_bound(self, expresssion, lower_bounds):
        self.lower_bounds[expresssion].append(lower_bounds)

    def add_initial(self, symbol):
        self.initials.add(symbol)

    def _is_initial(self, expression:Expr):
        return len(expression.free_symbols-self.initials)==0 and not expression.has(oo) and not expression.has(-oo)
    
    def _is_finite(self, expression: Expr):
        return expression.is_finite or self._is_initial(expression)

    def _get_upper_bounds_for_expression(self, expression:Expr):
        if expression.is_Number:
            yield expression
        if self._is_initial(expression):
            yield expression
        for bound in self.upper_bounds[expression]:
            yield bound
        if isinstance(expression, Add):
            bounds = [list(self._get_upper_bounds_for_expression(arg)) for arg in expression.args]
            bounds = [list(x) for x in product(*bounds)]

            for bound in bounds:
                yield Add(*bound)
        if isinstance(expression, Mul): # Case split based on signs of bounds
            # TODO: Currently only extract numbers from multiplication
            number_args = [arg for arg in expression.args if arg.is_Number]
            if len(number_args)>0:
                # evaluate to check sign
                coeff:Expr = simplify(Mul(*number_args))
                if coeff.is_nonnegative:
                    for bound in self._get_upper_bounds_for_expression(Mul(*[arg for arg in expression.args if not arg.is_Number])):
                        yield coeff*bound
                if coeff.is_nonpositive:
                    for bound in self._get_lower_bounds_for_expression(Mul(*[(arg) for arg in expression.args if not arg.is_Number])):
                        yield coeff*bound
            else:
                # TODO: this is suboptimal, as below
                for i in range(len(expression.args)):
                    first_expr = expression.args[i]
                    second_expr = Mul(*[arg for j,arg in enumerate(expression.args) if j!=i])

                    for first_lb in self._get_lower_bounds_for_expression(first_expr):
                        for second_lb in self._get_lower_bounds_for_expression(second_expr):
                            for first_ub in self._get_upper_bounds_for_expression(first_expr):
                                for second_ub in self._get_upper_bounds_for_expression(second_expr):
                                    if first_lb.is_nonnegative and second_lb.is_nonnegative and self._is_finite(first_ub) and self._is_finite(second_ub):
                                        yield first_ub*second_ub
                                    if first_ub.is_nonpositive and second_ub.is_nonpositive and self._is_finite(first_lb) and self._is_finite(second_lb):
                                        yield first_lb*second_lb

        if isinstance(expression, Pow):
            base = expression.args[0]
            exponent = expression.args[1]
            
            for base_lb in self._get_lower_bounds_for_expression(base):
                for base_ub in self._get_upper_bounds_for_expression(base):

                    if exponent.is_even:
                        if base_ub.is_nonpositive and self._is_finite(base_lb):
                            yield Pow(base_lb, exponent)
                        if base_lb.is_nonnegative and self._is_finite(base_ub):
                            yield Pow(base_ub, exponent)
                    else:
                        if base_ub.is_nonpositive:
                            if self._is_finite(base_ub):
                                yield Pow(base_ub, exponent)
                            yield sympify(0)
                        if base_lb.is_nonnegative and self._is_finite(base_ub):
                            yield Pow(base_ub, exponent)

        if isinstance(expression, Expexted):
            inner_expr = expression.args[0]
            for sharp_bound in self._get_upper_bounds_for_expression(inner_expr):
                if self._is_finite(sharp_bound):
                    yield sharp_bound
                if isinstance(inner_expr, Mul):
                    for i in range(len(inner_expr.args)):
                        # TODO: This could be made more efficient by considering a powerset (and its complement), instead of recursive calls
                        # TODO: More Cases are possible
                        hard_bounded_expr = inner_expr.args[i]
                        other_expr = Mul(*[arg for j,arg in enumerate(inner_expr.args) if j!= i])

                        for hb_upper_bound in self._get_upper_bounds_for_expression(hard_bounded_expr):
                            if not self._is_finite(hb_upper_bound):
                                continue

                            for oexpr_hard_lb in self._get_lower_bounds_for_expression(other_expr):
                                if not oexpr_hard_lb.is_nonnegative:
                                    continue
                                for oexpr_ub in self._get_upper_bounds_for_expression(Expexted(other_expr)):
                                    if self._is_finite(oexpr_ub):
                                        yield Mul(hb_upper_bound, oexpr_ub)

        elif expression.is_nonpositive:
            yield sympify(0)
    
    def __two_partitions(self, s):
        s = set(s)
        seen = set()
        return [
            (a := set(c), s - a)
            for r in range(1, len(s)//2 + 1)
            for c in combinations(s, r)
            if (key := frozenset([frozenset(c), frozenset(s - set(c))])) not in seen and not seen.add(key)
        ]   
    
    def _get_lower_bounds_for_expression(self, expression: Expr):
        if expression.is_Number:
            yield expression
            return
        if self._is_initial(expression):
            yield expression
            return
        for bound in self.lower_bounds[expression]:
            yield bound
        if isinstance(expression, Add):
            bounds = [list(x) for x in product(*[self._get_lower_bounds_for_expression(arg) for arg in expression.args])]
            for bound in bounds:
                yield Add(*bound)
        if isinstance(expression, Mul): # Case split based on signs of bounds
            # TODO: Currently only extract numbers from multiplication
            number_args = [arg for arg in expression.args if arg.is_Number]
            if len(number_args)!=0:
                # evaluate to check sign
                coeff:Expr = simplify(Mul(*number_args))
                if coeff.is_nonnegative:
                    for bound in self._get_lower_bounds_for_expression(Mul(*[arg for arg in expression.args if not arg.is_Number])):
                        yield coeff*bound
                if coeff.is_nonpositive:
                    for bound in self._get_upper_bounds_for_expression(Mul(*[(arg) for arg in expression.args if not arg.is_Number])):
                        yield coeff*bound
            else:
                 for a_expr, b_expr in self.__two_partitions(expression.args):
                    for a_lb in self._get_lower_bounds_for_expression(Mul(*a_expr)):
                        for b_lb in self._get_lower_bounds_for_expression(Mul(*b_expr)):
                            if a_lb.is_nonnegative and self._is_finite(a_lb) and b_lb.is_nonnegative and self._is_finite(b_lb):
                                yield a_lb*b_lb
        if isinstance(expression, Pow):
            base = expression.args[0]
            exponent = expression.args[1]
            
            for base_lb in self._get_lower_bounds_for_expression(base):
                for base_ub in self._get_upper_bounds_for_expression(base):
                    if exponent.is_even:
                        if base_ub.is_nonpositive and self._is_finite(base_ub):
                            yield Pow(base_ub, exponent)
                        if base_lb.is_nonnegative and self._is_finite(base_lb):
                            yield Pow(base_lb, exponent)
                        yield sympify(0)
                    else:
                        if base_ub.is_nonpositive and self._is_finite(base_lb):
                            yield Pow(base_lb, exponent)
                        if base_lb.is_nonnegative and self._is_finite(base_lb):
                            yield Pow(base_lb, exponent)

        if isinstance(expression, Expexted):
            inner_expr = expression.args[0]
            for sharp_bound in self._get_lower_bounds_for_expression(inner_expr):
                if self._is_finite(sharp_bound):
                    yield sharp_bound
                
            if isinstance(inner_expr, Mul):
                for i in range(len(inner_expr.args)):
                    # TODO: This could be made more efficient by considering a powerset (and its complement), instead of recursive calls
                    # TODO: More Cases are possible - this is just to get the minimum example working
                    hard_bounded_expr = inner_expr.args[i]
                    other_expr = Mul(*[arg for j,arg in enumerate(inner_expr.args) if j!= i])

                    for hb_lower_bound in self._get_lower_bounds_for_expression(hard_bounded_expr):
                        if not self._is_finite(hb_lower_bound):
                            continue

                        for oexpr_hard_lb in self._get_lower_bounds_for_expression(other_expr):
                            if not oexpr_hard_lb.is_nonnegative or not self._is_finite(oexpr_hard_lb):
                                continue
                            
                            if hb_lower_bound.is_nonpositive:
                                for oexpr_ub in self._get_upper_bounds_for_expression(Expexted(other_expr)):
                                    if self._is_finite(oexpr_ub) and oexpr_ub.is_nonnegative:
                                        yield Mul(*[hb_lower_bound, oexpr_ub]) # redundant case - needs to be sharpened
        elif expression.is_nonnegative:
            yield sympify(0)
