from .finite import Finite
from .type import Type
from .finite_range import FiniteRange

__types__ = {
    "FiniteRange": FiniteRange,
    "Finite": Finite
}


def type_factory(type_name: str, parameters, variable: str) -> Type:
    if type_name in __types__:
        return __types__[type_name](parameters, variable)
    raise RuntimeError(f"Type {type_name} is not supported")
