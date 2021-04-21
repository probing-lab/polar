from abc import ABC
from symengine import Expr


class Type(ABC):
    expression: Expr
