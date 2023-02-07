from typing import Union
from symengine.lib.symengine_wrapper import Expr, One, Symbol, sympy2symengine, sympify, Number, sin, cos

from sympy import I, N, re, im
from .assignment import Assignment
from program.condition import TrueCond
import math
from program.distribution import Distribution
from .exceptions import TrigAssignmentException


class TrigAssignment(Assignment):
    trig_fun: str
    argument: Union[Symbol, Number]
    argument_dist: Distribution

    def __init__(self, var, trig_fun, argument):
        super().__init__(var)
        self.trig_fun = trig_fun
        self.argument = sympify(argument)
        if not self.argument.is_Symbol and not self.argument.is_Number:
            raise TrigAssignmentException(f"Argument to trig assignment must be number or symbol but is {self.argument}")

    def __str__(self):
        result = f"{self.variable} = {self.trig_fun}({self.argument})"
        if not isinstance(self.condition, TrueCond):
            result += "  |  " + str(self.condition) + "  :  " + str(self.default)
        return result

    def get_free_symbols(self, with_condition=True, with_default=True):
        symbols = self.argument.free_symbols
        if with_condition:
            symbols |= self.condition.get_free_symbols()
        if with_default or not self.condition.is_implied_by_loop_guard():
            symbols.add(self.default)
        return symbols

    def subs(self, substitutions):
        self.default = self.default.subs(substitutions)
        self.condition.subs(substitutions)
        self.argument.subs(substitutions)

    def evaluate_right_side(self, state):
        arg_value = state[self.argument]
        if self.trig_fun == "Sin":
            return math.sin(arg_value)
        else:
            return math.cos(arg_value)

    def get_support(self):
        return {(-One(), One())}

    def get_moment(self, k: int, arithm_cond: Expr = 1, rest: Expr = 1):
        trig_moment = self.get_sin_moment(k) if self.trig_fun == "Sin" else self.get_cos_moment(k)
        if_cond = arithm_cond * trig_moment * rest
        if_not_cond = (1 - arithm_cond) * (self.default ** k) * rest
        return if_cond + if_not_cond

    def get_sin_moment(self, k: int):
        """
        Trigonometric moments from https://arxiv.org/pdf/2101.12490.pdf
        Warning: The result is a float (numerical)
        """
        if self.argument.is_Number:
            return sympy2symengine(N(sin(self.argument)**k))
        k = int(k)
        result = 0
        for i in range(k+1):
            result += math.comb(k, i) * ((-1)**(k-i)) * self.argument_dist.cf(2*i - k)
        result = (((-I)**k)/(2**k)) * result
        assert im(result) == 0
        return sympy2symengine(N(re(result)))

    def get_cos_moment(self, k: int):
        """
        Trigonometric moments from https://arxiv.org/pdf/2101.12490.pdf
        Warning: The result is a float (numerical)
        """
        if self.argument.is_Number:
            return sympy2symengine(N(sin(self.argument)**k))
        k = int(k)
        result = 0
        for i in range(k+1):
            result += math.comb(k, i) * self.argument_dist.cf(2*i - k)
        result = result / (2**k)
        assert im(result) == 0
        return sympy2symengine(N(re(result)))
