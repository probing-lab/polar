from typing import Union, Dict
from symengine.lib.symengine_wrapper import Expr, One, Zero, Symbol, sympy2symengine, sympify, Number, sin, cos, exp, oo
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

    def get_moment(self, k: int, arithm_cond: Expr = 1, rest: Expr = 1, previous_assigns: [Assignment] = None):
        if previous_assigns is None:
            raise FunctionalAssignmentException("The moment wrt. func assignments depends on previous assignments, But 'None' was given.")

        rest, count_removed_func_powers = self.remove_same_arg_funcs_from_monom(rest, previous_assigns)
        func_moment = None
        if self.func == "Cos" or self.func == "Sin":
            func_moment = self.get_trig_moment(int(k), count_removed_func_powers)
        if self.func == "Exp":
            func_moment = self.get_exp_moment(int(k), count_removed_func_powers)

        if_cond = arithm_cond * func_moment * rest
        if_not_cond = (1 - arithm_cond) * (self.default ** k) * rest
        return if_cond + if_not_cond

    def get_trig_moment(self, k: int, func_powers: Dict[str, int]):
        """
        For s = func_powers["Sin"] and c = func_powers["Cos"] the method computes
        E(self^k * sin^s(self.argument) * cos^c(self.argument))
        Trigonometric moments from https://arxiv.org/pdf/2101.12490.pdf
        """
        if "Exp" in func_powers:
            raise FunctionalAssignmentException("sin/cos and exp functional assignments must not be dependent")
        sin_power = func_powers["Sin"] if "Sin" in func_powers else 0
        sin_power += int(k) if self.func == "Sin" else 0
        cos_power = func_powers["Cos"] if "Cos" in func_powers else 0
        cos_power += int(k) if self.func == "Cos" else 0

        if self.argument.is_Number:
            return self.__convert_moment__((sin(self.argument)**sin_power) * (cos(self.argument)**cos_power))
        result = 0
        for k1 in range(cos_power+1):
            for k2 in range(sin_power+1):
                result += math.comb(cos_power, k1) * math.comb(sin_power, k2) * ((-1)**(sin_power - k2)) * self.argument_dist.cf(2*(k1 + k2) - cos_power - sin_power)
        result *= ((-I)**sin_power) / (2**(cos_power + sin_power))
        assert im(result).expand() == 0
        return self.__convert_moment__(re(result))

    def get_exp_moment(self, k: int, func_powers: Dict[str, int]):
        """
        For p = func_powers["Exp"] the method computes
        E(self^k * exp^p(self.argument))
        """
        if "Sin" in func_powers or "Cos" in func_powers:
            raise FunctionalAssignmentException("sin/cos and exp functional assignments must not be dependent")
        power = func_powers["Exp"] if "Exp" in func_powers else 0
        power += k
        if self.argument.is_Number:
            return self.__convert_moment__(exp(self.argument)**power)

        result = self.argument_dist.mgf(power)
        assert im(result).expand() == 0
        return self.__convert_moment__(re(result))

    def remove_same_arg_funcs_from_monom(self, monom: Expr, assigns: [Assignment]):
        """
        Given a monomial "monom" and assignments of the variables, the method removes from the monomial
        the variables that have a corresponding functional assignment with the same argument as 'self'.
        Moreover, it returns the number (or total power) of the different functions that were removed.
        Example:
            monom = x*y**2*z**3*t
            Assignments: a = Normal(0,1); b = Uniform(0,1); x = Sin(a); y = Cos(a); z = Exp(b) (t is independent of the rest)
            self.argument = a
            Then the function return:
                - z**3*t; because it removes x and y as they have the same argument to their functions ("a")
                - {"Sin": 1; "Cos": 2} because it removed "Sin(a)" with x (power 1) and "Cos(a)" with y (power 2)
        """
        same_arg_func_assigns = [a for a in assigns if isinstance(a, FunctionalAssignment) and a.variable in monom.free_symbols and a.argument == self.argument]
        if any([a.condition != TrueCond() for a in same_arg_func_assigns]):
            raise FunctionalAssignmentException("Not supported: Func assignment is dependent and conditioned")

        same_arg_func_vars = {}
        for a in same_arg_func_assigns:
            if a.func not in same_arg_func_vars:
                same_arg_func_vars[a.func] = [a.variable]
            else:
                same_arg_func_vars[a.func].append(a.variable)

        count_removed_func_powers = {}
        for func, vs in same_arg_func_vars.items():
            count_removed_func_powers[func] = int(sum(get_terms_with_vars(monom, vs)[0][0][0]))

        monom = monom.xreplace({a.variable: 1 for a in same_arg_func_assigns})
        return monom, count_removed_func_powers

    def __convert_moment__(self, m):
        if self.exact_moments or m.is_Rational:
            return m
        else:
            return sympy2symengine(Rational(N(m, 20)))
