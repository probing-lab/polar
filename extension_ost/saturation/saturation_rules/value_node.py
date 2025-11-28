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
                 can_have_sqrt_in_bound=True):
        self.name = name
        self.initial_value_provider = initial_value_provider
        self.lbs=set()
        self.ubs=set()
        self.can_have_sqrt_in_bound=can_have_sqrt_in_bound

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

    def add_ub(self, ub: Expr) -> bool:
        """Try to add a new upper bound

        Args:
            ub (Expr): the new bound

        Returns:
            bool: whether the new upper bound was added (not subsumed by existing bound)
        """
        if not self.can_have_sqrt_in_bound and self._contains_sqrt(ub):
            return False
        if self._has_nested_sqrt(ub):
            return False
        # forwards subsumption
        if not self._is_new_upper_bound(ub):
            return False
            # backwards subsumption

        # skip if sqrt, since it breaks subsumption check
        self.ubs = {old_ub for old_ub in self.ubs if not self._is_smaller(ub, old_ub)}
        self.ubs.add(ub)
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
        if not self.can_have_sqrt_in_bound and self._contains_sqrt(lb.value):
            return False
        if self._has_nested_sqrt(lb.value):
            return False
        if not self._is_new_lower_bound(lb.value):
            return False
        # skip if sqrt, since it breaks subsumption check
        self.lbs = {old_lb for old_lb in self.lbs if not self._is_smaller(old_lb, lb)}
        self.lbs.add(lb)
        return True

    def _is_new_upper_bound(self, upper_bound):
        if upper_bound == nan or not self._is_finite(upper_bound):
            return False
        # check if it is subsumed by any other lower bound
        # skip if sqrt, since it breaks subsumption check
        for old_ub in self.ubs:
            if self._is_smaller(old_ub, upper_bound):
                return False
        
        # the following line does a more agressive subsumption check (good for termination, bad for completeness)
        for old_ub in self.ubs:
            if self._monoms_similar(old_ub, upper_bound):
                return False

        return True
    
    def _monoms_similar(self, old_ub: Expr, new_ub: Expr):
        # we must first extract the square-roots:
        sqrts1 = list(self._get_sqrts(old_ub))
        sqrts2 = list(self._get_sqrts(new_ub))
        root_objects = set(sqrts1+sqrts2)
        root_subs = {k: f"ROOT_SUBS{i}" for i,k in enumerate(root_objects)}
        old_ub = old_ub.subs(root_subs)
        new_ub = new_ub.subs(root_subs)

        # if they have the same monoms, and share the signs, then ignore the new
        gens = list(old_ub.free_symbols.union(new_ub.free_symbols))
        if not gens:
            return False
        try:
            p_old = Poly(old_ub, *gens).as_dict()
            p_new = Poly(new_ub, *gens).as_dict()
        except PolynomialError:
            return False
        if (p_old.keys() != p_new.keys()):
            return False

        for k in p_old:
            if p_old[k].is_positive and p_new[k].is_negative:
                return False
            if p_old[k].is_negative and p_new[k].is_positive:
                return False
        return True

    def _is_new_lower_bound(self, lower_bound):
        if lower_bound == nan or not self._is_finite(lower_bound):
            return False
        # check if it is subsumed by any other lower bound
        # skip if sqrt, since it breaks subsumption check
        for old_lb in self.lbs:
            if self._is_smaller(lower_bound, old_lb):
                return False
        # the following line does a more agressive subsumption check (good for termination, bad for completeness)
        for old_lb in self.lbs:
            if self._monoms_similar(old_lb, lower_bound):
                return False

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

