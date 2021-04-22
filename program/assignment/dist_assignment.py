from typing import Optional

from symengine.lib.symengine_wrapper import Expr

from .assignment import Assignment
from program.distribution import Distribution
from program.type import Type
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

    def get_free_symbols(self):
        return self.distribution.get_free_symbols() | self.condition.get_free_symbols()

    def subs(self, substitutions):
        self.default = self.default.subs(substitutions)
        self.condition.subs(substitutions)
        self.distribution.subs(substitutions)

    def get_assign_type(self) -> Optional[Type]:
        if self.variable == self.default:
            return self.distribution.get_type()
        return None

    def get_moment(self, k: int, arithm_cond: Expr = 1, rest: Expr = 1):
        if_cond = arithm_cond * self.distribution.get_moment(k) * rest
        if_not_cond = (1 - arithm_cond) * (self.default ** k) * rest
        return if_cond + if_not_cond
