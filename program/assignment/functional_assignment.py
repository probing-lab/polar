from typing import Union
from symengine.lib.symengine_wrapper import Expr, One, Symbol, sympy2symengine, sympify, Number, sin, cos
from sympy import I, N, re, im, Rational
import math

from utils import get_terms_with_vars
from program.condition import TrueCond
from program.distribution import Distribution
from .assignment import Assignment
from .exceptions import FunctionalAssignmentException


class FunctionalAssignment(Assignment):
    func: str
    argument: Union[Symbol, Number]
    argument_dist: Distribution
    exact_moments: bool = False

    def __init__(self, var, func, argument):
        super().__init__(var)
        self.func = func
        self.argument = sympify(argument)
        if not self.argument.is_Symbol and not self.argument.is_Number:
            raise FunctionalAssignmentException(f"Argument to functional assignment must be number or symbol but is {self.argument}")

    def __str__(self):
        result = f"{self.variable} = {self.func}({self.argument})"
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
        arg_value = float(self.argument) if self.argument.is_Number else state[self.argument]
        if self.func == "Sin":
            return math.sin(arg_value)
        else:
            return math.cos(arg_value)

    def get_support(self):
        return {(-One(), One())}

    def get_moment(self, k: int, arithm_cond: Expr = 1, rest: Expr = 1, previous_assigns: [Assignment] = None):
        if previous_assigns is None:
            raise FunctionalAssignmentException("The moment wrt. func assignments depends on previous assignments, But 'None' was given.")

        rest, count_sin, count_cos = self.remove_same_arg_funcs_from_monom(rest, previous_assigns)
        if self.func == "Cos":
            count_cos += int(k)
        else:
            count_sin += int(k)
        func_moment = self.get_trig_moment(count_sin, count_cos)
        if_cond = arithm_cond * func_moment * rest
        if_not_cond = (1 - arithm_cond) * (self.default ** k) * rest
        return if_cond + if_not_cond

    def get_trig_moment(self, sin_power: int, cos_power: int):
        """
        Trigonometric moments from https://arxiv.org/pdf/2101.12490.pdf
        Warning: The result is a rational approximation of the (generally) transcendental answer
        """
        if self.argument.is_Number:
            return self.__convert_transcendental__((sin(self.argument)**sin_power) * (cos(self.argument)**cos_power))
        result = 0
        for k1 in range(cos_power+1):
            for k2 in range(sin_power+1):
                result += math.comb(cos_power, k1) * math.comb(sin_power, k2) * ((-1)**(sin_power - k2)) * self.argument_dist.cf(2*(k1 + k2) - cos_power - sin_power)
        result *= ((-I)**sin_power) / (2**(cos_power + sin_power))
        assert im(result).expand() == 0
        return self.__convert_transcendental__(re(result))

    def remove_same_arg_funcs_from_monom(self, monom: Expr, assigns: [Assignment]):
        """
        Given a monomial "monom" and assignments of the variables, the method removes from the monomial
        the variables that have a corresponding functional assignment with the same argument as 'self'.
        Moreover, it returns the number (or total power) of sin and cos appearences of such variables.
        """
        same_arg_func_assigns = [a for a in assigns if isinstance(a, FunctionalAssignment) and a.variable in monom.free_symbols and a.argument == self.argument]
        if any([a.condition != TrueCond() for a in same_arg_func_assigns]):
            raise FunctionalAssignmentException("Not supported: Func assignment is dependent and conditioned")
        same_arg_cos_vars = [a.variable for a in same_arg_func_assigns if a.func == "Cos"]
        same_arg_sin_vars = [a.variable for a in same_arg_func_assigns if a.func == "Sin"]

        count_cos = 0
        if len(same_arg_cos_vars) > 0:
            count_cos = int(sum(get_terms_with_vars(monom, same_arg_cos_vars)[0][0][0]))

        count_sin = 0
        if len(same_arg_sin_vars) > 0:
            count_sin = int(sum(get_terms_with_vars(monom, same_arg_sin_vars)[0][0][0]))
        monom = monom.xreplace({v: 1 for v in same_arg_cos_vars + same_arg_sin_vars})
        return monom, count_sin, count_cos

    def __convert_transcendental__(self, trans):
        if self.exact_moments:
            return trans
        else:
            return sympy2symengine(Rational(N(trans, 20)))
