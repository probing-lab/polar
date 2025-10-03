"""This algorithm continuously tries to obtain new bounds as long as possible.

Note that in the current implementation, there needs to be an iter-variable named "k" present in the loop to analyze.

TODO: check if positivity (of symbols in bounds) is a necessary requirement (i think so)
"""
from collections import defaultdict
from itertools import chain, combinations, product
from typing import Dict, List, Tuple

from sympy import S, Add, Expr, Interval, Mul, Poly, Symbol, nan, oo, simplify, sympify, solve, Pow

from extension_ost.helpers import Expexted
from program.distribution.distribution import DistributionFunction

# ITER_VAR = Symbol("k", integer=True, positive=True)

class BoundStore:
    def __init__(self):
        self.upper_bounds:Dict[Expr, List[Expr]] =  defaultdict(list)
        self.lower_bounds:Dict[Expr, List[Expr]] =  defaultdict(list)
        self.initials: Dict[Symbol, Tuple[Expr, Expr]] = {}

    def add_upper_bound(self, expression, upper_bound):
        # remove all the upper bounds which are subsumed by the new upper bound
        self.upper_bounds[expression] = [old_ub for old_ub in self.upper_bounds[expression] if not self._is_smaller(upper_bound, old_ub)]
        self.upper_bounds[expression].append(upper_bound)
        
    def add_lower_bound(self, expression, lower_bound):
        # remove all the lower bounds which are subsumed by the new lower bound
        self.lower_bounds[expression] = [old_lb for old_lb in self.lower_bounds[expression] if not self._is_smaller(old_lb, lower_bound)]
        self.lower_bounds[expression].append(lower_bound)

    def add_initial(self, symbol, lb=-oo, ub=oo):
        self.initials[symbol] = (lb, ub)

    def _is_initial(self, expression:Expr):
        return len(expression.free_symbols-self.initials.keys())==0 and not expression.has(oo) and not expression.has(-oo) and not expression.has(DistributionFunction)
    
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
            bounds = {tuple(x) for x in product(*bounds)}
            pass
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
                    bounds = list(self._get_lower_bounds_for_expression(Mul(*[(arg) for arg in expression.args if not arg.is_Number])))
                    for bound in bounds:
                        yield coeff*bound
            else:
                # exhaustively consider all combinations of expressions
                for i in range(len(expression.args)):
                    first_expr = expression.args[i]
                    second_expr = Mul(*[arg for j,arg in enumerate(expression.args) if j!=i])

                    first_lbs = list(self._get_lower_bounds_for_expression(first_expr))
                    if len(first_lbs) == 0:
                        first_lbs = [-oo]
                    second_lbs =list(self._get_lower_bounds_for_expression(second_expr))
                    if len(second_lbs) == 0:
                        second_lbs = [-oo]
                    first_ubs = list(self._get_upper_bounds_for_expression(first_expr))
                    if len(first_ubs) == 0:
                        first_ubs = [oo]
                    second_ubs =list(self._get_upper_bounds_for_expression(second_expr))
                    if len(second_ubs) == 0:
                        second_ubs = [oo]

                    for a, b, c, d in product(first_lbs, first_ubs, second_lbs, second_ubs):
                        # a<=X<=b, c<=Y<=d
                        if a.is_nonnegative and b. is_nonnegative and d.is_nonnegative:
                            bound = b*d
                            if self._is_finite(bound):
                                yield bound
                        if a.is_nonpositive and b. is_nonnegative and c.is_nonpositive and d.is_nonnegative:
                            # XY <= max(ac, bd)
                            if (a*c-b*d).is_nonnegative:
                                bound = a*c
                                if self._is_finite(bound):
                                    yield bound
                            elif (a*c-b*d).is_nonpositive:
                                bound = b*d
                                if self._is_finite(bound):
                                    yield bound
                        if a.is_nonnegative and d.is_nonpositive:
                            bound = a*d
                            if self._is_finite(bound):
                                yield bound
                        if a.is_nonpositive and c.is_nonpositive and d.is_nonpositive:
                            bound = a*c
                            if self._is_finite(bound):
                                yield bound

        if isinstance(expression, Pow):
            base = expression.args[0]
            exponent = expression.args[1]
            
            if exponent.is_even:
                yield sympify(0)
                for base_ub in self._get_upper_bounds_for_expression(base):
                    for base_lb in self._get_lower_bounds_for_expression(base):
                        if base_ub.is_nonpositive:
                            yield base_lb**exponent
                        elif base_lb.is_nonnegative:
                            yield base_ub**exponent
                        if base_lb.is_nonpositive and base_ub.is_nonnegative: # TODO: check if this could be even relaxed to an else case
                            # take the largest absolute value
                            diff_expr = base_ub+base_lb
                            if diff_expr.is_nonpositive: # the negative lower bound has greater absolute value
                                yield base_lb**exponent
                            elif diff_expr.is_nonnegative: # positive upper bound has greater absolute value
                                yield base_ub**exponent

            elif exponent.is_odd:
                for base_ub in self._get_upper_bounds_for_expression(base):
                    if base_ub.is_nonpositive:
                        yield sympify(0)
                    if self._is_finite(base_ub):
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

                    # hb_expr <= a   (a > 0)
                    # 0 <= other_expr               =>          E(hb_expr*other_expr) <= ab
                    # E(other_expr) < b
 
                    for hb_upper_bound in self._get_upper_bounds_for_expression(hard_bounded_expr):
                        if not self._is_finite(hb_upper_bound) and not hb_upper_bound.is_nonnegative:
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
            component_bounds = list(list(self._get_lower_bounds_for_expression(arg)) for arg in expression.args)
            bounds = [list(x) for x in product(*component_bounds)]
            for bound in bounds:
                yield Add(*bound)
        if isinstance(expression, Mul): # Case split based on signs of bounds
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
                # exhaustively consider all combinations of expressions
                for i in range(len(expression.args)):
                    first_expr = expression.args[i]
                    second_expr = Mul(*[arg for j,arg in enumerate(expression.args) if j!=i])

                    first_lbs = list(self._get_lower_bounds_for_expression(first_expr))
                    if len(first_lbs) == 0:
                        first_lbs = [-oo]
                    second_lbs =list(self._get_lower_bounds_for_expression(second_expr))
                    if len(second_lbs) == 0:
                        second_lbs = [-oo]
                    first_ubs = list(self._get_upper_bounds_for_expression(first_expr))
                    if len(first_ubs) == 0:
                        first_ubs = [oo]
                    second_ubs =list(self._get_upper_bounds_for_expression(second_expr))
                    if len(second_ubs) == 0:
                        second_ubs = [oo]

                    for a, b, c, d in product(first_lbs, first_ubs, second_lbs, second_ubs):
                        # a<=X<=b, c<=Y<=d
                        if b.is_nonpositive and d.is_nonpositive:
                            bound = b*d
                            if self._is_finite(bound):
                                yield bound
                        if b.is_nonnegative and c.is_nonpositive and (d.is_nonpositive or a.is_nonnegative):
                            # either, X is strictly positive, then c*b is the smallest term
                            #   or    Y is strictly negative, then c*b is also the smallest term
                            bound = b*c
                            if self._is_finite(bound):
                                yield bound
                        if a.is_nonpositive and b. is_nonnegative and c.is_nonpositive and d.is_nonnegative:
                            # min(ad, bc) <= XY
                            if (a*d-b*c).is_nonpositive:
                                bound = a*d
                                if self._is_finite(bound):
                                    yield bound
                            elif (a*d-b*c).is_nonnegative:
                                bound = b*c
                                if self._is_finite(bound):
                                    yield bound
                        if a.is_nonnegative and c.is_nonnegative:
                            bound = a*c
                            if self._is_finite(bound):
                                yield bound
        if isinstance(expression, Pow):
            base = expression.args[0]
            exponent = expression.args[1]
            
            if exponent.is_even:
                yield sympify(0)
                for base_ub in self._get_upper_bounds_for_expression(base):
                    for base_lb in self._get_lower_bounds_for_expression(base):
                        if base_ub.is_nonpositive:
                            yield base_ub**exponent
                        elif base_lb.is_nonnegative:
                            yield base_lb**exponent
                        if base_lb.is_nonpositive and base_ub.is_nonnegative: # TODO: check if this could be even relaxed to an else case
                            # take the smallest absolute value
                            diff_expr = base_ub+base_lb
                            if diff_expr.is_nonpositive: # the negative lower bound has greater absolute value
                                yield base_ub**exponent
                            elif diff_expr.is_nonnegative: # positive upper bound has greater absolute value
                                yield base_lb**exponent

            elif exponent.is_odd:
                for base_lb in self._get_lower_bounds_for_expression(base):
                    if base_lb.is_nonnegative:
                        yield sympify(0)
                    if self._is_finite(base_ub):
                        yield Pow(base_ub, exponent)

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
                            # a <= hb_expr [WHERE a <= 0] 
                            # 0 <= other_expr               =>          ab <= E(hb_expr*other_expr)
                            # E(other_expr) < b 
                            if hb_lower_bound.is_nonpositive:
                                for oexpr_ub in self._get_upper_bounds_for_expression(Expexted(other_expr)):
                                    if self._is_finite(oexpr_ub) and oexpr_ub.is_nonnegative:
                                        yield Mul(*[hb_lower_bound, oexpr_ub]) # redundant case - needs to be sharpened
                                        
                                                               


                    
        elif expression.is_nonnegative:
            yield sympify(0)

    def is_new_upper_bound(self, key, upper_bound):
        if upper_bound == nan or not self._is_finite(upper_bound):
            return False
        # check if it is subsumed by any other lower bound
        for old_ub in self.upper_bounds[key]:
            if self._is_smaller(old_ub, upper_bound):
                return False

        return True

    def is_new_lower_bound(self, key, lower_bound):
        if lower_bound == nan or not self._is_finite(lower_bound):
            return False
        # check if it is subsumed by any other lower bound
        for old_lb in self.lower_bounds[key]:
            if self._is_smaller(lower_bound, old_lb):
                return False

        return True

    def _pretty_print(self):
        print("================================================")
        for monom in {k for k in self.upper_bounds.keys() if len(self.upper_bounds[k])>0} |\
                        {k for k in self.lower_bounds.keys() if len(self.lower_bounds[k])>0}:
            if len(self.upper_bounds[monom])>0:
                print(f"{str(monom):<20} <= {self.upper_bounds[monom][0]}")
                for upper_bound in self.upper_bounds[monom][1:]:
                    print(" "*20 + " <= "+str(upper_bound))

            if len(self.lower_bounds[monom])>0:
                print(f"{str(monom):<20} >= {self.lower_bounds[monom][0]}")
                for lower_bound in self.lower_bounds[monom][1:]:
                    print(" "*20 + " >= "+str(lower_bound))
            print()

    def _get_ub_for_initial_monomial(self, monom: Expr):
        # TODO: support more complex monomials, like x0*y0
        if len(monom.free_symbols) == 0:
            return monom
        if len(monom.free_symbols)!=1:
            raise NotImplementedError("Currently only monomials that are of form x**k for some initial variable x are supported")
        if monom in self.initials:
            return self.initials[monom][1]

        if isinstance(monom, Pow):
            base = monom.args[0]
            exponent = monom.args[1]
            if base not in self.initials:
                raise KeyError(f"monom base {base} expected to be in initials")
            if exponent.is_odd:
                return self.initials[base][1]**exponent
            if exponent.is_even:
                # take the absolutely larger bound
                if self.initials[base][0].is_nonnegative:
                    return self.initials[base][1]**exponent
                if self.initials[base][1].is_nonpositive:
                    return self.initials[base][0]**exponent
                
                diff_expr = self.initials[base][1]+self.initials[base][0]
                if diff_expr.is_positive:
                    return self.initials[base][1]**exponent
                if diff_expr.is_negative:
                    return self.initials[base][0]**exponent
                # inconclusive :(

        raise NotImplementedError("monomial could not be bounded")
    
    def _get_lb_for_initial_monomial(self, monom: Expr):
        # TODO: support more complex monomials, like x0*y0
        if len(monom.free_symbols) == 0:
            return monom
        if len(monom.free_symbols)!=1:
            raise NotImplementedError("Currently only monomials that are of form x**k for some initial variable x are supported")
        if monom in self.initials:
            return self.initials[monom][0]

        if isinstance(monom, Pow):
            base = monom.args[0]
            exponent = monom.args[1]
            if base not in self.initials:
                raise KeyError(f"monom base {base} expected to be in initials")
            if exponent.is_odd:
                return self.initials[base][1]**exponent
            if exponent.is_even:
                # take the absolutely larger bound
                if self.initials[base][1].is_nonnegative:
                    return self.initials[base][1]**exponent
                else:
                    return S.Zero
                
                # inconclusive :(

        raise NotImplementedError("monomial could not be bounded")
    
    def _is_smaller(self, smaller_expr: Expr, larger_expr: Expr):
        """returns True when smaller_expr < larger_expr, and false if the opposite is true, or if it is unknown

        Args:
            smaller_expr (Expr): smaller expression
            larger_expr (Expr): larger expression
        """
        diff_expr = Add(larger_expr,smaller_expr*(-1)).simplify()

        # check if positivity can easily shown
        if diff_expr.is_nonnegative:
            return True
        
        # try to lower bound the expression, and check if positivity can then be shown
        initial_gens = list(self.initials.keys())
        diff_expr_poly = Poly(diff_expr, *initial_gens)

        coeff_monom_list = [(coeff,Mul(*[var**exp for var, exp in zip(initial_gens, poly_exps)])) for poly_exps, coeff in diff_expr_poly.terms()]

        term = S.Zero
        for coeff, monom in coeff_monom_list:
            if coeff.is_positive:
                monom_bound = self._get_lb_for_initial_monomial(monom)
                term *= monom_bound*coeff
            elif coeff.is_negative:
                monom_bound = self._get_ub_for_initial_monomial(monom)
                term *= monom_bound*coeff
            else:
                raise ValueError("Coefficient sign must be known")

        if term.simplify().is_nonnegative:
            return True

        return False
