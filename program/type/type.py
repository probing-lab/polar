from abc import ABC, abstractmethod
from typing import Iterable
from symengine.lib.symengine_wrapper import Symbol, Expr


class Type(ABC):
    variable: Symbol

    @abstractmethod
    def is_finite(self) -> bool:
        pass

    @abstractmethod
    def enumerate_values(self) -> Iterable[Expr]:
        pass
