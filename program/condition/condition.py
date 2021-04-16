from abc import ABC, abstractmethod
from diofant import Expr
from program import Program


class Condition(ABC):

    @abstractmethod
    def simplify(self):
        pass

    @abstractmethod
    def subs(self, substitutions):
        pass

    @abstractmethod
    def to_arithm(self, program: Program) -> Expr:
        pass
