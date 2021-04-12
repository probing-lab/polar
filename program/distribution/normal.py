from diofant import sympify, Expr
from .distribution import Distribution


class Normal(Distribution):
    mu: Expr
    sigma2: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 2:
            raise RuntimeError("Normal distribution requires 2 parameters")
        self.mu = sympify(parameters[0])
        self.sigma2 = sympify(parameters[1])

    def get_moment(self, k: int):
        #TODO
        pass

    def is_discrete(self):
        return False

    def __str__(self):
        return f"Normal({self.mu}, {self.sigma2})"
