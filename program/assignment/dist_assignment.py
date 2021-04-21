from typing import Optional

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

    def get_moment_of_content(self, k: int):
        return self.distribution.get_moment(k)
