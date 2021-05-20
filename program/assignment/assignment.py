from abc import ABC, abstractmethod
from typing import Union, Tuple, Set, Dict

from symengine.lib.symengine_wrapper import Expr, Symbol

from .exceptions import EvaluationException
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

    def evaluate(self, state: Dict[Symbol, float]):
        if self.condition.evaluate(state):
            result = self.evaluate_right_side(state)
        else:
            if self.default not in state:
                raise EvaluationException(f"Tried to evaluate {self.default} which is not set in state {state}")
            result = state[self.default]

        state[self.variable] = float(result)
        return state

    @abstractmethod
    def subs(self, substitutions):
        pass

    @abstractmethod
    def evaluate_right_side(self, state: Dict[Symbol, float]):
        pass

    @abstractmethod
    def get_free_symbols(self, with_condition=True, with_default=True) -> Set[Symbol]:
        """
        Returns the free symbols in the assignments right side.
        with_condtiion == True <==> symbols of condition are included
        with_default == False <==> default symbol is not included if condition is syntactically TRUE
        """
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
