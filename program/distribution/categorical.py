from functools import lru_cache
from typing import List
import random

from symengine.lib.symengine_wrapper import Expr, sympify
from .distribution import Distribution
from .exceptions import EvaluationException


class Categorical(Distribution):
    probabilities: List[Expr]

    def set_parameters(self, parameters):
        if len(parameters) == 0:
            raise RuntimeError("Categorical distribution requires >=1 parameters")
        s = sum(parameters)
        if s.is_Number and s != 1:
            raise RuntimeError(
                "Categorical distribution parameters need to sum up to 1"
            )
        self.probabilities = parameters

    @lru_cache()
    def get_moment(self, k: int):
        m = 0
        for i, p in enumerate(self.probabilities):
            m += (i**k) * p
        return m

    def is_discrete(self):
        return True

    def get_free_symbols(self):
        symbols = set()
        for p in self.probabilities:
            symbols = symbols.union(p.free_symbols)
        return symbols

    def get_support(self):
        return {sympify(v) for v in range(len(self.probabilities))}

    def sample(self, state):
        probabilities = []
        for prob in self.probabilities:
            p = prob.subs(state)
            if not p.is_Number:
                raise EvaluationException(
                    f"Probability {prob} is not a number in state {state}"
                )
            probabilities.append(float(p))

        return random.choices(range(len(probabilities)), weights=probabilities, k=1)[0]

    def subs(self, substitutions):
        self.probabilities = [p.subs(substitutions) for p in self.probabilities]

    def __str__(self):
        return f"Categorical({', '.join([str(p) for p in self.probabilities])})"
