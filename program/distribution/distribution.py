from abc import ABC, abstractmethod
from typing import Union, Tuple, Set, Dict
from symengine.lib.symengine_wrapper import Expr, Symbol, sympify
from utils import float_to_rational


class Distribution(ABC):

    def __init__(self, parameters):
        params = []
        for p in parameters:
            p = sympify(p)
            if p.is_Float:
                p = float_to_rational(p)
            params.append(p)
        self.set_parameters(params)
        super().__init__()

    @abstractmethod
    def set_parameters(self, parameters):
        pass

    @abstractmethod
    def get_moment(self, k: int):
        pass

    @abstractmethod
    def is_discrete(self) -> bool:
        pass

    @abstractmethod
    def sample(self, state: Dict[Symbol, float]):
        pass

    @abstractmethod
    def subs(self, substitutions):
        pass

    @abstractmethod
    def get_support(self) -> Union[Set[Expr], Tuple[Expr, Expr]]:
        """
        Returns either a set of expressions if the support is finite.
        Otherwise it returns a tuple with a lower and upper bound for the support
        """
        pass

    @abstractmethod
    def get_free_symbols(self) -> Set[Symbol]:
        pass
