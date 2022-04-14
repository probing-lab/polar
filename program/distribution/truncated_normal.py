from functools import lru_cache

from symengine.lib.symengine_wrapper import Expr, sqrt, sympy2symengine, one, zero
from program.distribution import Distribution
from program.distribution.exceptions import EvaluationException
from scipy.stats import truncnorm
from sympy import sympify, Rational
from sympy.stats import Normal, density, cdf
import math


class TruncNormal(Distribution):
    """
    Implements the truncated normal distribution.
    Disclaimer: When using this distribution in programs exact solutions are not guaranteed.
    The reason is that moments of the truncated normal depend on the erf function which is not elementary.
    """
    mu: Expr
    sigma2: Expr
    a: Expr
    b: Expr

    def set_parameters(self, parameters):
        if len(parameters) != 4:
            raise RuntimeError("TruncNormal distribution requires 4 parameters")
        self.mu = parameters[0]
        self.sigma2 = parameters[1]
        self.a = parameters[2]
        self.b = parameters[3]

    @lru_cache()
    def get_moment(self, k: int):
        """
        Implements the recursive definition of the central moments in:
        https://people.smp.uq.edu.au/YoniNazarathy/teaching_projects/studentWork/EricOrjebin_TruncatedNormalMoments.pdf
        """
        mu = self.mu
        a = self.a
        b = self.b
        sigma = sqrt(self.sigma2)
        if all([mu.is_Number, a.is_Number, b.is_Number, sigma.is_Number]):
            moment = truncnorm.moment(int(k), float(a), float(b), loc=float(mu), scale=float(sigma))
            return sympy2symengine(Rational(str(moment)))

        alpha = (a - mu) / sigma
        beta = (b - mu) / sigma
        z = Normal("z", 0, 1)
        z_pdf = lambda x: sympy2symengine(density(z)(sympify(x)))
        z_cdf = lambda x: sympy2symengine(cdf(z)(sympify(x)))
        m = {-1: zero, 0: one}
        for i in range(1, int(k)+1):
            m_i = (i-1) * self.sigma2 * m[i-2]
            m_i += mu * m[i-1]
            m_i -= sigma * ((beta**(i-1)) * z_pdf(beta) - (alpha**(i-1)) * z_pdf(alpha)) / (z_cdf(beta) - z_cdf(alpha))
            m[i] = m_i
        return m[k].simplify()

    def is_discrete(self):
        return False

    def subs(self, substitutions):
        self.mu = self.mu.subs(substitutions)
        self.sigma2 = self.sigma2.subs(substitutions)
        self.a = self.a.subs(substitutions)
        self.b = self.b.subs(substitutions)

    def sample(self, state):
        mu = self.mu.subs(state)
        sigma2 = self.sigma2.subs(state)
        a = self.a.subs(state)
        b = self.b.subs(state)
        if not mu.is_Number or not sigma2.is_Number or not a.is_Number or not b.is_Number:
            raise EvaluationException(
                f"Parameters {self.mu}, {self.sigma2}, {self.a}, {self.b} don't evaluate to numbers with state {state}")
        return truncnorm.rvs(float(a), float(b), loc=float(mu), scale=math.sqrt(float(sigma2)))

    def get_free_symbols(self):
        symbols = self.mu.free_symbols
        symbols = symbols.union(self.sigma2.free_symbols)
        symbols = symbols.union(self.a.free_symbols)
        symbols = symbols.union(self.b.free_symbols)
        return symbols

    def get_support(self):
        return self.a, self.b

    def __str__(self):
        return f"TruncNormal({self.mu}, {self.sigma2}, {self.a}, {self.b})"
