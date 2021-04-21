from abc import ABC, abstractmethod
from symengine.lib.symengine_wrapper import Expr


class Condition(ABC):

    @abstractmethod
    def simplify(self):
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
