from abc import ABC, abstractmethod
from typing import Union, Tuple, Set

from symengine.lib.symengine_wrapper import Expr, Symbol
from program.condition import Condition, TrueCond, And


class Assignment(ABC):
    variable: Symbol  # the variable to assign to
    condition: Condition  # a condition which has to hold in order for tha assignment to happen
    default: Symbol  # the value to assign if condition is false

    def __init__(self, variable, condition=TrueCond(), default=None):
        self.variable = Symbol(str(variable))
        self.condition = condition
        self.default = Symbol(str(default)) if default else self.variable

    def add_to_condition(self, cond: Condition):
        self.condition = And(self.condition, cond)

    def simplify_condition(self):
        self.condition = self.condition.simplify()

    @abstractmethod
    def subs(self, substitutions):
        pass

    @abstractmethod
    def get_free_symbols(self, with_condition=True) -> Set[Symbol]:
        pass

    @abstractmethod
    def get_support(self) -> Union[Set[Expr], Tuple[Expr, Expr]]:
        """
        Returns either a set of expressions if the support is finite.
        Otherwise it returns a tuple with a lower and upper bound for the support
        """
        pass

    @abstractmethod
    def get_moment(self, k: int, arithm_cond: Expr = 1, rest: Expr = 1):
        """
        returns E(X) for X := Assignment^k * rest
        relative to some given condition.
        """
        pass
