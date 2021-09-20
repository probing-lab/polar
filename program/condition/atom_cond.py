from typing import Dict

from symengine.lib.symengine_wrapper import sympify, Zero, Symbol

from .or_cond import Or
from .false_cond import FalseCond
from .condition import Condition
from .exceptions import ArithmConversionException, NormalizingException, EvaluationException
from utils import get_unique_var, get_valid_values, evaluate_cop
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

    def evaluate(self, state):
        poly1 = self.poly1.subs(state)
        poly2 = self.poly2.subs(state)
        if not poly1.is_Number or not poly2.is_Number:
            raise EvaluationException(f"Atom {self} cannot be fully evaluated with state {state}")
        result = evaluate_cop(float(poly1), self.cop, float(poly2))
        return result

    def is_reduced(self):
        return self.poly1.is_Symbol and self.poly2.is_Integer

    def reduce(self, store: Dict["Atom", Symbol]):
        if self.is_reduced():
            return []

        if self in store:
            self.poly1 = store[self].copy()
            self.poly2 = Zero()
            return []

        new_var = sympify(get_unique_var(name="r"))
        store[self.copy()] = new_var
        alias = self.poly1 - self.poly2
        self.poly1 = new_var
        self.poly2 = Zero()
        return [(new_var, alias)]

    def is_normalized(self):
        return self.poly1.is_Symbol and self.poly2.is_Integer and self.cop == "=="

    def get_normalized(self, program):
        if not self.is_reduced():
            raise NormalizingException(f"Atom {self} cannot be normalized because it's not reduced")

        var = self.poly1
        value = self.poly2
        var_type = program.get_type(var)
        if not isinstance(var_type, Finite):
            return self, [self]
        valid_values = get_valid_values(var_type.values, self.cop, value)

        if len(valid_values) == 0:
            return FalseCond(), []
        if len(valid_values) == 1:
            return Atom(self.poly1.copy(), "==", valid_values.pop()), []

        result = Atom(self.poly1.copy(), "==", valid_values.pop())
        for v in valid_values:
            result = Or(result, Atom(self.poly1.copy(), "==", v))

        return result, []

    def to_arithm(self, program):
        if not self.is_normalized():
            raise ArithmConversionException(f"Atom {self} is not normalized")
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

    def is_implied_by_loop_guard(self):
        return self.is_loop_guard

    def get_conjuncts(self):
        return [self]

    def get_free_symbols(self):
        return self.poly1.free_symbols | self.poly2.free_symbols

    def __str__(self):
        return f"{self.poly1} {self.cop} {self.poly2}"

    def __eq__(self, obj):
        return isinstance(obj, Atom) and (self.poly1, self.cop, self.poly2) == (obj.poly1, obj.cop, obj.poly2)

    def __hash__(self):
        return hash((self.poly1, self.cop, self.poly2))

    def __simple_copy__(self):
        return Atom(self.poly1.copy(), self.cop, self.poly2.copy())
