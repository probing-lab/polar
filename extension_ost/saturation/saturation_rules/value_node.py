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

    def add_ub(self, ub_bound: Bound) -> bool:
        """Try to add a new upper bound

        Args:
            ub (Expr): the new bound

        Returns:
            bool: whether the new upper bound was added (not subsumed by existing bound)
        """
        # forwards subsumption
        if not self._is_new_upper_bound(ub_bound.value):
            return False
            # backwards subsumption

        # skip if sqrt, since it breaks subsumption check
        self.ubs = {old_ub for old_ub in self.ubs if not self._is_smaller(ub_bound.value, old_ub.value)}
        self.ubs.add(ub_bound)
        return True

    def add_lb(self, lb_bound: Bound) -> bool:
        """Try to add a new lower bound

        Args:
            lb (Expr): the new bound

        Returns:
            bool: whether the new lower bound was added (not subsumed by existing bound)
        """
        if not self._is_new_lower_bound(lb_bound.value):
            return False
        # skip if sqrt, since it breaks subsumption check
        self.lbs = {old_lb for old_lb in self.lbs if not self._is_smaller(old_lb.value, lb_bound.value)}
        self.lbs.add(lb_bound)
        return True

    def _is_new_upper_bound(self, upper_bound):
        if upper_bound == nan or not self._is_finite(upper_bound):
            return False
        # check if it is subsumed by any other lower bound
        # skip if sqrt, since it breaks subsumption check
        for old_ub in self.ubs:
            if self._is_smaller(old_ub.value, upper_bound):
                return False
        
        # the following line does a more agressive subsumption check (good for termination, bad for completeness)
        for old_ub in self.ubs:
            if self._monoms_similar(old_ub.value, upper_bound):
                return False
            if not self._new_upper_bound_better(old_ub.value, upper_bound):
                return False

        return True
    
    def _monoms_similar(self, old_ub: Expr, new_ub: Expr):
        # we must first extract the square-roots:

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
        return True
    
    def _new_upper_bound_better(self, old_ub: Expr, new_ub: Expr):
        vars = old_ub.free_symbols.union(new_ub.free_symbols)
        if len(new_ub.free_symbols)==0:
            return True


        new_ub_better = True
        for var in vars:
            old_ub_poly = Poly(old_ub, var)
            new_ub_poly = Poly(new_ub, var)
            lc_number,_ = old_ub_poly.LC().as_coeff_Mul()

            if lc_number.is_nonnegative:
                if new_ub_poly.degree() < old_ub_poly.degree():
                    return True
                elif new_ub_poly.LC().as_coeff_mul()[0].is_nonpositive:
                    return True

            if lc_number.is_nonpositive:
                if new_ub_poly.degree() > old_ub_poly.degree():
                    return True
        return False
    
    def _new_lower_bound_better(self, old_lb: Expr, new_lb: Expr):
        vars = old_lb.free_symbols.union(new_lb.free_symbols)
        if len(new_lb.free_symbols)==0:
            return True

        for var in vars:
            old_lb_poly = Poly(old_lb, var)
            new_lb_poly = Poly(new_lb, var)
            lc_number,_ = old_lb_poly.LC().as_coeff_Mul()

            if lc_number.is_nonnegative:
                if new_lb_poly.degree() > old_lb_poly.degree():
                    return True

            if lc_number.is_nonpositive:
                if new_lb_poly.degree() < old_lb_poly.degree():
                    return True
                if new_lb_poly.LC().as_coeff_mul()[0].is_nonnegative:
                    return True
        return False

    def _is_new_lower_bound(self, lower_bound):
        if lower_bound == nan or not self._is_finite(lower_bound):
            return False
        # check if it is subsumed by any other lower bound
        # skip if sqrt, since it breaks subsumption check
        for old_lb in self.lbs:
            if self._is_smaller(lower_bound, old_lb.value):
                return False
        # the following line does a more agressive subsumption check (good for termination, bad for completeness)
        for old_lb in self.lbs:
            if self._monoms_similar(old_lb.value, lower_bound):
                return False
            if not self._new_lower_bound_better(old_lb.value, lower_bound):
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

