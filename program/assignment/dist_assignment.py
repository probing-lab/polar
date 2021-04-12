from diofant import Symbol, sympify
from .assignment import Assignment
from ..distribution import Distribution


class DistAssignment(Assignment):
    variable: Symbol
    distribution: Distribution

    def __init__(self, var, dist):
        super().__init__()
        self.variable = sympify(var)
        self.distribution = dist

    def __str__(self):
        return str(self.variable) + " = " + str(self.distribution) + "  |  " + str(self.condition)
