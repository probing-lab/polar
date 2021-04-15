from abc import ABC, abstractmethod
from diofant import Symbol

from program.condition import Condition, TrueCond, And, sympify


class Assignment(ABC):
    variable: Symbol      # the variable to assign to
    condition: Condition  # a condition which has to hold in order for tha assignment to happen
    default: Symbol       # the value to assign if condition is false

    def __init__(self, variable, condition=TrueCond(), default=None):
        self.variable = sympify(variable)
        self.condition = condition
        self.default = sympify(default) if default else self.variable

    def add_to_condition(self, cond: Condition):
        self.condition = And(self.condition, cond)

    def simplify_condition(self):
        self.condition = self.condition.simplify()

    @abstractmethod
    def subs(self, substitutions):
        pass
