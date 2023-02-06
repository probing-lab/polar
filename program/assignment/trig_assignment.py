from symengine.lib.symengine_wrapper import Expr, One, Symbol

from .assignment import Assignment
from program.condition import TrueCond
import math


class TrigAssignment(Assignment):
    trig_fun: str
    argument: Symbol

    def __init__(self, var, trig_fun, argument):
        super().__init__(var)
        self.trig_fun = trig_fun
        self.argument = Symbol(argument)

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
        pass
        # TODO
