from abc import ABC
from sympy import Symbol


class Type(ABC):
    variable: Symbol
