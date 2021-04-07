from diofant import Symbol, sympify
from .assignment import Assignment
from ..distribution import Distribution


class DistAssignment(Assignment):
    variable: Symbol
    distribution: Distribution

    def __init__(self, var, dist):
        self.variable = sympify(var)
        self.distribution = dist
