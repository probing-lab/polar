from abc import ABC, abstractmethod
from program.condition import Condition, TrueCond, And


class Assignment(ABC):
    condition: Condition

    def __init__(self):
        self.condition = TrueCond()

    def add_to_condition(self, cond: Condition):
        self.condition = And(self.condition, cond)

    def simplify_condition(self):
        self.condition = self.condition.simplify()

    @abstractmethod
    def subs(self, substitutions):
        pass
