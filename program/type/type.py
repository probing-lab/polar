from abc import ABC
from diofant import Expr


class Type(ABC):
    expression: Expr

