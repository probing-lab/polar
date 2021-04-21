from symengine.lib.symengine_wrapper import sympify
from program.condition import Condition
from .exceptions import ArithmConversionException
from program.type import Finite


class Atom(Condition):

    def __init__(self, poly1, cop, poly2):
        self.poly1 = sympify(poly1)
        self.cop = cop
        self.poly2 = sympify(poly2)

    def simplify(self):
        return self

    def subs(self, substitutions):
        self.poly1 = self.poly1.subs(substitutions)
        self.poly2 = self.poly2.subs(substitutions)

    def __str__(self):
        return f"{self.poly1} {self.cop} {self.poly2}"

    def is_canonical(self):
        return self.poly1.is_Symbol and self.poly2.is_Integer and self.cop == "=="

    def to_arithm(self, program):
        if not self.is_canonical():
            raise ArithmConversionException(f"Atom {self} is not canonical")
        var = self.poly1
        value = self.poly2
        var_type = program.get_type(var)
        if not isinstance(var_type, Finite):
            raise ArithmConversionException(f"Variable {var} in atom {self} is not of finite type.")

        if value not in var_type.values:
            return sympify(0)

        result = sympify(1)
        terms = [(var - v) / (value - v) for v in var_type.values if v != value]
        for t in terms:
            result *= t

        return result

    def get_free_symbols(self):
        return self.poly1.free_symbols | self.poly2.free_symbols
