from typing import Union, Dict, TYPE_CHECKING
from symengine.lib.symengine_wrapper import Expr, One, Zero, Symbol, sympy2symengine, sympify, Number, sin, cos, exp, oo
from sympy import I, N, re, im, Rational, diff, Symbol as SSymbol
import math
if TYPE_CHECKING:
    from recurrences import RecBuilderContext

from .assignment import Assignment
from program.condition import TrueCond
from program.distribution import Distribution
from .exceptions import FunctionalAssignmentException


class FunctionalAssignment(Assignment):
    func: str
    argument: Union[Symbol, Number]
    argument_dist: Distribution
    exact_func_moments: bool = False

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
        if self.func == "Cos":
            return math.cos(arg_value)
        if self.func == "Exp":
            return math.exp(arg_value)
        raise FunctionalAssignmentException(f"Function {self.func} not supported.")

    def get_support(self):
        if self.func == "Sin" or self.func == "Cos":
            return {(-One(), One())}
        if self.func == "Exp":
            return {(Zero(), oo)}
        raise FunctionalAssignmentException(f"Function {self.func} not supported.")

    def get_moment(self, k: int, rec_builder_context: "RecBuilderContext", arithm_cond: Expr = 1, rest: Expr = 1):
        if self.argument.is_Number:
            # if the argument is a number the moment can be immediately determined by just computing f(argument)
            func_moment = self.get_const_moment(k)
        else:
            # if the argument is a distribution, only the rec_builder_context is changed because the moment
            # will be determined together with the distribution variable.
            rec_builder_context.add_func_assignments(self)
            rec_builder_context.add_trigger(self.argument, self.variable)
            func_moment = self.variable ** k

        if_cond = arithm_cond * func_moment * rest
        if_not_cond = (1 - arithm_cond) * (self.default ** k) * rest
        return if_cond + if_not_cond

    def get_const_moment(self, k: int):
        if self.func == "Sin":
            return self.convert_func_moment(sin(self.argument) ** k)
        if self.func == "Cos":
            return self.convert_func_moment(cos(self.argument) ** k)
        if self.func == "Exp":
            return self.convert_func_moment(exp(self.argument) ** k)
        raise FunctionalAssignmentException(f"The function {self.func} is not supported.")

    @classmethod
    def get_func_moment(cls, dist: Distribution, func_powers: Dict[str, int]):
        """
        Computes E(dist^p1 * f1^p2(dist) * ... * fn^pn(dist)), where the functions and respective powers
        are given by the second argument. Currently the functions "Sin", "Cos", "Exp" and "Id" are supported.
        "Sin", "Cos" and "Id" can be mixed. "Exp" can be mixed with "Id".
        """
        is_trig_moment = "Sin" in func_powers or "Cos" in func_powers
        is_exp_moment = "Expt" in func_powers
        if is_trig_moment and is_exp_moment:
            raise FunctionalAssignmentException("Exponential and trigonometric moments cannot be mixed")

        if "Sin" in func_powers or "Cos" in func_powers:
            return cls.get_trig_moment(dist, func_powers)

        if "Exp" in func_powers:
            return cls.get_exp_moment(dist, func_powers)

        raise FunctionalAssignmentException("Unknown functions")

    @classmethod
    def get_trig_moment(cls, dist: Distribution, func_powers: Dict[str, int]):
        """
        Computes E(dist^p1 * sin^p2(dist) * cos^p3(dist)) where the powers are given by the second argument.
        Formula for mixed trigonometric moments from https://arxiv.org/pdf/2101.12490.pdf
        """
        id_power = func_powers["Id"] if "Id" in func_powers else 0
        sin_power = func_powers["Sin"] if "Sin" in func_powers else 0
        cos_power = func_powers["Cos"] if "Cos" in func_powers else 0
        t = SSymbol("t")

        result = 0
        for k1 in range(cos_power+1):
            for k2 in range(sin_power+1):
                if id_power == 0:
                    cf_term = dist.cf(2*(k1 + k2) - cos_power - sin_power)
                else:
                    cf_term = diff(dist.cf(t), t, id_power).xreplace({t: 2*(k1 + k2) - cos_power - sin_power})
                result += math.comb(cos_power, k1) * math.comb(sin_power, k2) * ((-1)**(sin_power - k2)) * cf_term
        result /= (I**(id_power + sin_power) * 2**(cos_power + sin_power))
        assert im(result).expand() == 0
        return cls.convert_func_moment(re(result))

    @classmethod
    def get_exp_moment(cls, dist: Distribution, func_powers: Dict[str, int]):
        """
        Computes E(exp(dist)**p) where p is given by the second argument.
        """
        exp_power = func_powers["Exp"] if "Exp" in func_powers else 0
        id_power = func_powers["Id"] if "Id" in func_powers else 0
        if not dist.mgf_exists_at(exp_power):
            raise FunctionalAssignmentException(f"The exponential moment of {dist} of order {exp_power} does not exist.")
        if id_power == 0:
            result = dist.mgf(exp_power)
        else:
            t = SSymbol("t")
            result = diff(dist.mgf(t), t, id_power).xreplace({t: exp_power})
        return cls.convert_func_moment(result)

    @classmethod
    def convert_func_moment(cls, m):
        if cls.exact_func_moments or m.is_Rational:
            return m
        else:
            return sympy2symengine(Rational(re(N(m, 20))))
