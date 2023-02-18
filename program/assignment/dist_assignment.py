from symengine.lib.symengine_wrapper import Expr

from .assignment import Assignment
from program.distribution import Distribution
from program.condition import TrueCond


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

    def get_moment(self, k: int, arithm_cond: Expr = 1, rest: Expr = 1, previous_assigns=None):
        if_cond = arithm_cond * self.distribution.get_moment(k) * rest
        if_not_cond = (1 - arithm_cond) * (self.default ** k) * rest
        return if_cond + if_not_cond
