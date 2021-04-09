from .finite import *
from .type import *
from .finite_range import *

__types__ = {
    "FiniteRange": FiniteRange,
    "Finite": Finite
}


def type_factory(type_name: str, expression: str, parameters) -> Type:
    if type_name in __types__:
        return __types__[type_name](expression, parameters)
    raise RuntimeError(f"Type {type_name} is not supported")
