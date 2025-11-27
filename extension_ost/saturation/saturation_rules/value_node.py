from typing import List, Set

from sympy import S, Add, Expr, Poly, nan, oo

from extension_ost.saturation.saturation_rules.initial_value_provider import InitialValueProvider
from program.distribution.distribution import DistributionFunction

class ValueNode:
    name: Expr
    lbs: Set[Expr]
    ubs: Set[Expr]

    initial_value_provider: InitialValueProvider

    def __init__(self,
                 initial_value_provider: InitialValueProvider,
                 name: Expr):
        self.name = name
        self.initial_value_provider = initial_value_provider
        self.lbs=set()
        self.ubs=set()
        

    def add_ub(self, ub: Expr) -> bool:
        """Try to add a new upper bound

        Args:
            ub (Expr): the new bound

        Returns:
            bool: whether the new upper bound was added (not subsumed by existing bound)
        """
        if not self._is_new_upper_bound(ub):
            return False
        self.ubs.add(ub)

    def add_lb(self, lb: Expr) -> bool:
        """Try to add a new lower bound

        Args:
            lb (Expr): the new bound

        Returns:
            bool: whether the new lower bound was added (not subsumed by existing bound)
        """
        if not self._is_new_lower_bound(lb):
            return False
        self.lbs.add(lb)

    def _is_new_upper_bound(self, upper_bound):
        if upper_bound == nan or not self._is_finite(upper_bound):
            return False
        # check if it is subsumed by any other lower bound
        for old_ub in self.ubs:
            if self._is_smaller(old_ub, upper_bound):
                return False

        return True

    def _is_new_lower_bound(self, lower_bound):
        if lower_bound == nan or not self._is_finite(lower_bound):
            return False
        # check if it is subsumed by any other lower bound
        for old_lb in self.lbs:
            if self._is_smaller(lower_bound, old_lb):
                return False

        return True
    
    
    def _is_finite(self, expression: Expr):
        return expression.is_finite or (not expression.has(oo) and not expression.has(-oo))


    def _is_smaller(self, smaller_expr: Expr, larger_expr: Expr):
        """returns True when smaller_expr < larger_expr, and false if the opposite is true, or if it is unknown

        Args:
            smaller_expr (Expr): smaller expression
            larger_expr (Expr): larger expression
        """
        diff_expr = Add(larger_expr,smaller_expr*(-1)).simplify()
        return self.initial_value_provider.is_nonnegative(diff_expr)
        
