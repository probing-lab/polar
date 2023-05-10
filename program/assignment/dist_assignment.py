from symengine.lib.symengine_wrapper import Expr, Symbol
from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from recurrences import RecBuilderContext
from .assignment import Assignment
from .functional_assignment import FunctionalAssignment
from program.distribution import Distribution
from program.condition import TrueCond
from utils import get_terms_with_vars


class DistAssignment(Assignment):
    distribution: Distribution

    def __init__(self, var, dist):
        super().__init__(var)
        self.distribution = dist

    def __str__(self):
        result = str(self.variable) + " = " + str(self.distribution)
        if not isinstance(self.condition, TrueCond):
            result += "  |  " + str(self.condition) + "  :  " + str(self.default)
        return result

    def get_free_symbols(self, with_condition=True, with_default=True):
        symbols = self.distribution.get_free_symbols()
        if with_condition:
            symbols |= self.condition.get_free_symbols()
        if with_default or not self.condition.is_implied_by_loop_guard():
            symbols.add(self.default)
        return symbols

    def subs(self, substitutions):
        self.default = self.default.subs(substitutions)
        self.condition.subs(substitutions)
        self.distribution.subs(substitutions)

    def evaluate_right_side(self, state):
        return self.distribution.sample(state)

    def get_support(self):
        result = self.distribution.get_support()
        if not self.condition.is_implied_by_loop_guard():
            result.add(self.default)
        return result

    def get_moment(
        self,
        k: int,
        rec_builder_context: "RecBuilderContext",
        arithm_cond: Expr = 1,
        rest: Expr = 1,
    ):
        # if rest contains variables that are functions of self.variable (like sin(var)/cos(var) etc.)
        # then we need to compute the moment of all those variables and self together.
        # In this case we hand the responsibility to FunctionalAssignment
        if self._contains_dependent_funcs(rec_builder_context, rest):
            func_vars = (
                rec_builder_context.dist_var_dependent_func_vars[self.variable]
                & rest.free_symbols
            )
            dist_moment = self._get_mixed_func_moment(
                k, rec_builder_context, func_vars, rest
            )
            rest = rest.xreplace({v: 1 for v in func_vars})
        # Otherwise, we can just compute the moment of the distribution and put it in the result
        # (the parameters of the distribution are always constant, hence self is independent of everything else)
        else:
            dist_moment = self.distribution.get_moment(k)
        if_cond = arithm_cond * dist_moment * rest
        if_not_cond = (1 - arithm_cond) * (self.default**k) * rest
        return if_cond + if_not_cond

    def _get_mixed_func_moment(
        self,
        k: int,
        rec_builder_context: "RecBuilderContext",
        func_vars: Set[Symbol],
        rest: Expr,
    ):
        k = int(k)
        func_vars = list(func_vars)
        func_powers = {"Id": k} if k > 0 else {}
        terms_with_vars, _ = get_terms_with_vars(rest, func_vars)
        # collect the powers of all variables that are functions of self.variable
        # rest is a monomial hence terms_with_vars only has a single entry
        powers = terms_with_vars[0][0]
        for var, power in zip(func_vars, powers):
            func_assign = rec_builder_context.func_assignments[var]
            if func_assign.func in func_powers:
                func_powers[func_assign.func] += int(power)
            else:
                func_powers[func_assign.func] = int(power)
        # pass the responsibility of computing the moment of E(dist^k * f1^p1(dist) ... * fl^pl(dist))
        # to FunctionalAssignment
        return FunctionalAssignment.get_func_moment(self.distribution, func_powers)

    def _contains_dependent_funcs(
        self, rec_builder_context: "RecBuilderContext", monom: Expr
    ):
        if self.variable not in rec_builder_context.dist_var_dependent_func_vars:
            return False
        return bool(
            monom.free_symbols
            & rec_builder_context.dist_var_dependent_func_vars[self.variable]
        )
