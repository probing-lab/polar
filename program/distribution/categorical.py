from diofant import sympify, Expr
from .distribution import Distribution


class Categorical(Distribution):
    probabilities: [Expr]

    def set_parameters(self, parameters):
        if len(parameters) == 0:
            raise RuntimeError("Categorical distribution requires >=1 parameters")
        self.probabilities = [sympify(p) for p in parameters]

    def get_moment(self, k: int):
        #TODO
        pass

    def is_discrete(self):
        return True

    def __str__(self):
        return f"Categorical({', '.join([str(p) for p in self.probabilities])})"
