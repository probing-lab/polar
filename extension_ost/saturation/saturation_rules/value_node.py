from functools import cache
from typing import List, Set

from sympy import S, Add, Expr, Poly, PolynomialError, Pow, nan, oo

from extension_ost.saturation.saturation_rules.bound import Bound
from extension_ost.saturation.saturation_rules.initial_value_provider import InitialValueProvider
from program.distribution.distribution import DistributionFunction
class ValueNode:
    name: Expr
    lbs: Set[Bound]
    ubs: Set[Bound]

    initial_value_provider: InitialValueProvider

    def __init__(self,
                 initial_value_provider: InitialValueProvider,
                 name: Expr,
                 can_have_sqrt_in_bound=True,
                 use_minkowski=False):
        self.name = name
        self.initial_value_provider = initial_value_provider
        self.lbs=set()
        self.ubs=set()
        self.can_have_sqrt_in_bound=can_have_sqrt_in_bound
        use_minkowski=use_minkowski # if the minkowski rule is used, we need to perform different subsumption checks

        # dependency detection can be done using sets - little number of ground atoms
        self.descendants: Set[ValueNode] = set()
        self.ancestors: Set[ValueNode] = set()
        
    def _get_sqrts(self, expression):
        powers = expression.atoms(Pow)

        for p in powers:
            if p.exp == S.Half:
                yield p

    def _contains_sqrt(self, expression):
        try:
            next(self._get_sqrts(expression))
            return True
        except StopIteration:
            return False

    def add_ub(self, ub_bound: Bound) -> bool:
        """Try to add a new upper bound

        Args:
            ub (Expr): the new bound

        Returns:
            bool: whether the new upper bound was added (not subsumed by existing bound)
        """
        if not self.can_have_sqrt_in_bound and self._contains_sqrt(ub_bound.value):
            return False
        if self._has_nested_sqrt(ub_bound.value):
            return False
        
        new_bounds=set()
        for old_ub in self.ubs:
            sign =  self.initial_value_provider.asymptotic_sign(old_ub.value-ub_bound.value)
            if sign == 1: # new bound is better - drop the old one
                continue
            elif sign == -1: # old bound was better, do not add the current
                return False
            else: # indecisive which bound is better
                new_bounds.add(old_ub)
        new_bounds.add(ub_bound)

        self.ubs = new_bounds
        return True
    
    def _has_nested_sqrt(self, expr: Expr) -> bool:
        for sqrt in self._get_sqrts(expr):
            if self._contains_sqrt(sqrt.base):
                return True
        return False

    def add_lb(self, lb_bound: Bound) -> bool:
        """Try to add a new lower bound

        Args:
            lb (Expr): the new bound

        Returns:
            bool: whether the new lower bound was added (not subsumed by existing bound)
        """
        if not self.can_have_sqrt_in_bound and self._contains_sqrt(lb_bound.value):
            return False
        if self._has_nested_sqrt(lb_bound.value):
            return False
        
        new_bounds=set()
        for old_lb in self.lbs:
            sign =  self.initial_value_provider.asymptotic_sign(old_lb.value-lb_bound.value)
            if sign == -1: # new bound is better - drop the old one
                continue
            elif sign == 1: # old bound was better, do not add the current
                return False
            else: # indecisive which bound is better
                new_bounds.add(old_lb)
        new_bounds.add(lb_bound)
        
        self.lbs=new_bounds
        return True
    
    
    def _is_finite(self, expression: Expr):
        return expression.is_finite or (not expression.has(oo) and not expression.has(-oo))

    @cache
    def _is_smaller(self, smaller_expr: Expr, larger_expr: Expr):
        """returns True when smaller_expr < larger_expr, and false if the opposite is true, or if it is unknown

        Args:
            smaller_expr (Expr): smaller expression
            larger_expr (Expr): larger expression
        """
        diff_expr = Add(larger_expr,smaller_expr*(-1)).simplify()
        return self.initial_value_provider.is_nonnegative(diff_expr)

    def get_ubs_simplified(self):
        return {Bound(ub.value.expand().simplify(), ub.used_rules, ub.hash_salt) for ub in self.ubs}

    def get_lbs_simplified(self):
        return {Bound(lb.value.expand().simplify(), lb.used_rules, lb.hash_salt) for lb in self.lbs}