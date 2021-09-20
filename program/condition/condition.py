from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
from symengine.lib.symengine_wrapper import Expr, Symbol


class Condition(ABC):

    is_loop_guard: bool = False

    @abstractmethod
    def is_implied_by_loop_guard(self):
        pass

    @abstractmethod
    def simplify(self) -> "Condition":
        pass

    @abstractmethod
    def reduce(self, store) -> List[Tuple[Symbol, Expr]]:
        pass

    @abstractmethod
    def get_normalized(self, program) -> Tuple["Condition", List]:
        pass

    @abstractmethod
    def get_free_symbols(self):
        pass

    @abstractmethod
    def get_conjuncts(self) -> List["Condition"]:
        pass

    @abstractmethod
    def subs(self, substitutions):
        pass

    @abstractmethod
    def evaluate(self, state: Dict[Symbol, float]):
        pass

    @abstractmethod
    def to_arithm(self, program) -> Expr:
        pass

    @abstractmethod
    def __simple_copy__(self) -> "Condition":
        pass

    def copy(self) -> "Condition":
        cond = self.__simple_copy__()
        cond.is_loop_guard = self.is_loop_guard
        return cond
