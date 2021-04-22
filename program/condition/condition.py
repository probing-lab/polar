from abc import ABC, abstractmethod
from typing import List, Tuple
from symengine.lib.symengine_wrapper import Expr, Symbol


class Condition(ABC):

    @abstractmethod
    def simplify(self) -> "Condition":
        pass

    @abstractmethod
    def reduce(self) -> List[Tuple[Symbol, Expr]]:
        pass

    @abstractmethod
    def get_free_symbols(self):
        pass

    @abstractmethod
    def subs(self, substitutions):
        pass

    @abstractmethod
    def to_arithm(self, program) -> Expr:
        pass
