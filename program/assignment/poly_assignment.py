from typing import List
import random
from symengine.lib.symengine_wrapper import Expr, sympify

from utils import float_to_rational, get_monoms
from .assignment import Assignment
from program.condition import TrueCond
from .exceptions import EvaluationException


class PolyAssignment(Assignment):
    polynomials: List[Expr]
    probabilities: List[Expr]

    def __init__(self, variable, polynomials, probabilities):
        super().__init__(variable)
        # self.polynomials = [sympify(p) for p in polynomials]

        self.polynomials = []
        for poly in polynomials:
            expanded_poly = sympify(poly).expand()
            monoms = get_monoms(expanded_poly, with_constant=True)
            term = 0
            for coeff, monom in monoms:
                ncoeff = coeff
                if coeff.is_Float:
                    ncoeff = float_to_rational(coeff)
                term += sympify(ncoeff) * sympify(monom)
            self.polynomials.append(sympify(term))

        self.probabilities = []
        for p in probabilities:
            p = sympify(p)
            if p.is_Float:
                p = float_to_rational(p)
            self.probabilities.append(p)

    @classmethod
    def deterministic(cls, variable, polynomial):
        return cls(variable, [polynomial], [1])

    def is_constant(self):
        return len(self.polynomials) == 1 and self.polynomials[0].is_Number

    def is_reference(self):
        return len(self.polynomials) == 1 and self.polynomials[0].is_Symbol

    def __str__(self):
        result = str(self.variable) + " = " + str(self.polynomials[0])
        for i in range(1, len(self.polynomials)):
            result += " {" + str(self.probabilities[i-1]) + "} "
            result += str(self.polynomials[i])

        if not isinstance(self.condition, TrueCond):
            result += "  |  " + str(self.condition) + "  :  " + str(self.default)
        return result

    def subs(self, substitutions):
        self.default = self.default.subs(substitutions)
        self.condition.subs(substitutions)
        self.polynomials = [p.subs(substitutions) for p in self.polynomials]
        self.probabilities = [p.subs(substitutions) for p in self.probabilities]

    def get_free_symbols(self, with_condition=True, with_default=True):
        symbols = self.condition.get_free_symbols() if with_condition else set()
        for i in range(len(self.polynomials)):
            symbols |= self.polynomials[i].free_symbols | self.probabilities[i].free_symbols
        if with_default or not self.condition.is_implied_by_loop_guard():
            symbols.add(self.default)
        return symbols

    def get_support(self):
        result = set(self.polynomials)
        if not self.condition.is_implied_by_loop_guard():
            result.add(self.default)
        return result

    def evaluate_right_side(self, state):
        probabilities = []
        for prob in self.probabilities:
            p = prob.subs(state)
            if not p.is_Number:
                raise EvaluationException(f"Probability {prob} is not a number in state {state}")
            probabilities.append(float(p))

        polynomials = []
        for pol in self.polynomials:
            p = pol.subs(state)
            if not p.is_Number:
                raise EvaluationException(f"Polynomial {pol} is not a number in state {state}")
            polynomials.append(float(p))

        return random.choices(polynomials, weights=probabilities, k=1)[0]

    def get_moment(self, k: int, arithm_cond: Expr = 1, rest: Expr = 1, previous_assigns=None):
        if_cond = 0
        for i in range(len(self.polynomials)):
            if_cond += arithm_cond * self.probabilities[i] * (self.polynomials[i] ** k) * rest
        if_not_cond = (1 - arithm_cond) * (self.default ** k) * rest
        return if_cond + if_not_cond
