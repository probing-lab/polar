from abc import ABC, abstractmethod
from diofant import Expr


class Condition(ABC):

    @abstractmethod
    def simplify(self):
        pass

    @abstractmethod
    def subs(self, substitutions):
        pass

    @abstractmethod
    def to_arithm(self, program) -> Expr:
        pass
