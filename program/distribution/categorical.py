from diofant import sympify, Expr
from .distribution import Distribution
from program.type import FiniteRange


class Categorical(Distribution):
    probabilities: [Expr]

    def set_parameters(self, parameters):
        if len(parameters) == 0:
            raise RuntimeError("Categorical distribution requires >=1 parameters")
        self.probabilities = [sympify(p) for p in parameters]

    def get_moment(self, k: int):
        #TODO
        pass

    def get_type(self) -> FiniteRange:
        return FiniteRange([0, len(self.probabilities) - 1])

    def is_discrete(self):
        return True

    def get_free_symbols(self):
        symbols = set()
        for p in self.probabilities:
            symbols = symbols.union(p.free_symbols)
        return symbols

    def subs(self, substitutions):
        self.probabilities = [p.subs(substitutions) for p in self.probabilities]

    def __str__(self):
        return f"Categorical({', '.join([str(p) for p in self.probabilities])})"
