from typing import Optional

from .assignment import Assignment
from program.distribution import Distribution, Type


class DistAssignment(Assignment):
    distribution: Distribution

    def __init__(self, var, dist):
        super().__init__(var)
        self.distribution = dist

    def __str__(self):
        return str(self.variable) + " = " + str(self.distribution) + "  |  " + str(self.condition) + "  :  " + str(self.default)

    def subs(self, substitutions):
        self.default = self.default.subs(substitutions)
        self.condition.subs(substitutions)
        self.distribution.subs(substitutions)

    def get_assign_type(self) -> Optional[Type]:
        if self.variable == self.default:
            return self.distribution.get_type()
        return None
