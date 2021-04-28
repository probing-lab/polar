from abc import ABC
from symengine.lib.symengine_wrapper import Symbol


class Type(ABC):
    variable: Symbol
